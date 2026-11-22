
import os
from dotenv import load_dotenv

load_dotenv()
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from services.tomtom_service import get_live_traffic
from config.database import get_db_connection
from analysis.hotspot_analysis import get_hotspot_data, get_high_traffic_data
from utils.prediction import predict_traffic

app = Flask(__name__)

#app.secret_key = "urban_traffic_secret_key"
app.secret_key = os.getenv("SECRET_KEY")

# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM traffic_data
        ORDER BY date DESC, time DESC
    """)

    traffic_data = cursor.fetchall()

    cursor.close()
    connection.close()

    total_records = len(traffic_data)

    total_vehicles = sum(
        row["vehicle_count"] or 0
        for row in traffic_data
    )

    if total_records > 0:
        average_speed = round(
            sum(row["average_speed"] or 0 for row in traffic_data)
            / total_records,
            2
        )
    else:
        average_speed = 0

    high_hotspots = sum(
        1 for row in traffic_data
        if row["traffic_level"] == "High"
    )

    return render_template(
        "dashboard/dashboard.html",
        traffic_data=traffic_data,
        total_records=total_records,
        total_vehicles=total_vehicles,
        average_speed=average_speed,
        high_hotspots=high_hotspots
    )


# ---------------- TRAFFIC MAP API ----------------


@app.route("/api/traffic-data")
def traffic_map_api():

    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                location,
                AVG(vehicle_count) AS vehicle_count,
                AVG(average_speed) AS average_speed,
                AVG(traffic_density) AS traffic_density,
                MAX(traffic_level) AS traffic_level,
                latitude,
                longitude
            FROM traffic_data
            WHERE latitude IS NOT NULL
              AND longitude IS NOT NULL
            GROUP BY location, latitude, longitude
        """)

        data = cursor.fetchall()

        for row in data:
            row["latitude"] = float(row["latitude"])
            row["longitude"] = float(row["longitude"])

        return jsonify(data)

    except Exception:
        app.logger.exception("Traffic API Error")
        return jsonify({"error": "Database query failed"}), 500

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
    

    traffic_data = cursor.fetchall()

    cursor.close()
    connection.close()

    total_records = len(traffic_data)

    total_vehicles = sum(
        row["vehicle_count"] or 0
        for row in traffic_data
    )

    if total_records > 0:
        average_speed = round(
            sum(row["average_speed"] or 0 for row in traffic_data)
            / total_records,
            2
        )
    else:
        average_speed = 0

    high_hotspots = sum(
        1 for row in traffic_data
        if row["traffic_level"] == "High"
    )

    return render_template(
        "dashboard/dashboard.html",
        traffic_data=traffic_data,
        total_records=total_records,
        total_vehicles=total_vehicles,
        average_speed=average_speed,
        high_hotspots=high_hotspots
    )


# -------- TOMTOM LIVE TRAFFIC TEST --------


# ---------------- LIVE TRAFFIC + MYSQL SAVE ----------------

@app.route("/api/live-traffic")
def live_traffic_api():

    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    connection = None
    cursor = None

    try:
        # Step 1: Get live TomTom data
        latitude = 28.4744
        longitude = 77.5040
        location = "Greater Noida"

        traffic = get_live_traffic(latitude, longitude)

        # Step 2: Connect to MySQL
        connection = get_db_connection()
        cursor = connection.cursor()

        # Step 3: Insert live traffic record
        cursor.execute("""
            INSERT INTO traffic_data
            (
                location,
                date,
                time,
                vehicle_count,
                average_speed,
                traffic_density,
                weather,
                accident,
                traffic_level,
                latitude,
                longitude
            )
            VALUES (
                %s, CURDATE(), CURTIME(),
                NULL, %s, %s, NULL, 0, %s, %s, %s
            )
        """, (
            location,
            traffic["current_speed"],
            traffic["congestion"],
            traffic["traffic_level"],
            latitude,
            longitude
        ))

        connection.commit()

        # Step 4: Return successful response
        return jsonify({
            "success": True,
            "message": "Live traffic data saved successfully!",
            "location": location,
            "traffic": traffic
        })

    except Exception as error:

        if connection and connection.is_connected():
            connection.rollback()

        app.logger.exception("Live traffic database error")

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

# -------- GET LATEST LIVE TRAFFIC FOR DASHBOARD --------

@app.route("/api/latest-live-traffic")
def latest_live_traffic():

    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                location,
                date,
                time,
                average_speed,
                traffic_density,
                traffic_level,
                latitude,
                longitude
            FROM traffic_data
            ORDER BY id DESC
            LIMIT 1
        """)

        record = cursor.fetchone()

        if not record:
            return jsonify({
                "success": False,
                "message": "No traffic record found"
            }), 404

        # Convert date/time into JSON-friendly strings
        record["date"] = str(record["date"])
        record["time"] = str(record["time"])

        return jsonify({
            "success": True,
            "traffic": record
        })

    except Exception as error:

        app.logger.exception("Latest traffic fetch error")

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


    
# ---------------- TRAFFIC ANALYTICS API ----------------

@app.route("/api/traffic-analytics")
def traffic_analytics():

    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # 1. Traffic level distribution
        cursor.execute("""
            SELECT
                traffic_level,
                COUNT(*) AS total
            FROM traffic_data
            GROUP BY traffic_level
        """)

        level_data = cursor.fetchall()

        # 2. Average speed by traffic level
        cursor.execute("""
            SELECT
                traffic_level,
                ROUND(AVG(average_speed), 2) AS avg_speed
            FROM traffic_data
            GROUP BY traffic_level
        """)

        speed_data = cursor.fetchall()

        # 3. Daily traffic records (last 7 days)
        cursor.execute("""
            SELECT
                DATE(date) AS traffic_date,
                COUNT(*) AS total
            FROM traffic_data
            WHERE date >= CURDATE() - INTERVAL 6 DAY
            GROUP BY DATE(date)
            ORDER BY traffic_date ASC
        """)

        daily_data = cursor.fetchall()

        for row in daily_data:
            row["traffic_date"] = str(row["traffic_date"])

        return jsonify({
            "success": True,
            "levels": level_data,
            "speeds": speed_data,
            "daily": daily_data
        })

    except Exception as error:
        app.logger.exception("Traffic analytics error")
        return jsonify({
            "success": False,
            "error": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
        

# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("home.html")


# ---------------- ABOUT ----------------

@app.route("/about")
def about():
    return render_template("about.html")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        connection = get_db_connection()
        cursor = connection.cursor()

        # Check whether email already exists
        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            cursor.close()
            connection.close()

            return "Email already registered! Please login."


        # Insert new user
        cursor.execute(
            """
            INSERT INTO users (name, email, password)
            VALUES (%s, %s, %s)
            """,
            (name, email, password)
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("login"))

    return render_template("auth/register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email = %s AND password = %s
            """,
            (email, password)
        )

        user = cursor.fetchone()

        cursor.close()
        connection.close()


        if user:

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]

            return redirect(url_for("dashboard"))


        return "Invalid email or password!"


    return render_template("auth/login.html")


# ---------------- DASHBOARD ----------------


# ---------------- LOGOUT ----------------
@app.route("/hotspots")
def hotspots():

    if "user_id" not in session:
        return redirect(url_for("login"))

    hotspot_data = get_hotspot_data()
    high_traffic_data = get_high_traffic_data()

    return render_template(
        "dashboard/hotspots.html",
        hotspot_data=hotspot_data,
        high_traffic_data=high_traffic_data
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

@app.route("/predict", methods=["GET", "POST"])
def predict():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        try:
            vehicle_count = int(request.form["vehicle_count"])
            average_speed = float(request.form["average_speed"])
            traffic_density = float(request.form["traffic_density"])
            weather = request.form["weather"]
            accident = int(request.form["accident"])

            if vehicle_count < 0 or not 0 <= average_speed <= 200:
                raise ValueError("Please enter valid traffic values.")

            if not 0 <= traffic_density <= 100:
                raise ValueError("Traffic density must be between 0 and 100.")

            if weather not in ["Clear", "Rainy", "Foggy", "Cloudy"]:
                raise ValueError("Please select a valid weather option.")

            if accident not in [0, 1]:
                raise ValueError("Please select a valid accident option.")

            prediction = predict_traffic(
                vehicle_count,
                average_speed,
                traffic_density,
                weather,
                accident
            )

            return render_template(
                "predict.html",
                prediction=prediction
            )

        except (ValueError, TypeError) as e:
            return render_template(
                "predict.html",
                error=str(e) or "Please enter valid values."
            )

        except Exception:
            return render_template(
                "predict.html",
                error="Prediction failed. Please check the trained model and feature columns."
            )

    return render_template("predict.html")


@app.route("/reports")
def reports():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT location, date, time, vehicle_count,
               average_speed, traffic_density, traffic_level
        FROM traffic_data
        ORDER BY date DESC, time DESC
    """)

    traffic_records = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "reports.html",
        traffic_records=traffic_records
    )
# ---------------- RUN APP ----------------

if __name__ == "__main__":
    app.run(debug=True)

    
