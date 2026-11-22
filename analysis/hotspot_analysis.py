from config.database import get_db_connection


def get_hotspot_data():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            traffic_level,
            COUNT(*) AS total_records,
            SUM(vehicle_count) AS total_vehicles,
            AVG(average_speed) AS average_speed,
            AVG(traffic_density) AS average_density
        FROM traffic_data
        GROUP BY traffic_level
        ORDER BY total_records DESC
    """)

    data = cursor.fetchall()

    cursor.close()
    connection.close()

    return data


def get_high_traffic_data():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            location,
            COUNT(*) AS hotspot_count,
            AVG(vehicle_count) AS average_vehicles,
            AVG(traffic_density) AS average_density
        FROM traffic_data
        WHERE traffic_level = 'High'
        GROUP BY location
        ORDER BY hotspot_count DESC
    """)

    data = cursor.fetchall()

    cursor.close()
    connection.close()

    return data