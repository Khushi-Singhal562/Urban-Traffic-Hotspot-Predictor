# 🚦 Urban Traffic Hotspot Predictor

## 📌 Project Overview

Urban Traffic Hotspot Predictor is a real-time traffic monitoring and prediction web application developed using Python and Flask.

The system uses the TomTom Traffic API to fetch live traffic information and helps users understand traffic conditions, congestion levels, and traffic hotspots.

## ✨ Features

- User Registration and Login
- Real-Time Traffic Monitoring
- TomTom API Integration
- Current Speed and Free Flow Speed
- Traffic Congestion Analysis
- Traffic Level Detection
- Traffic Hotspot Prediction
- Interactive Dashboard
- Traffic Analytics and Reports
- Live Traffic Map

## 🛠️ Technologies Used

**Frontend:**
- HTML
- CSS
- JavaScript

**Backend:**
- Python
- Flask

**Database:**
- MySQL

**API:**
- TomTom Traffic API

**Machine Learning:**
- Python
- Pandas
- Scikit-learn (if used in the prediction model)

## 📂 Project Structure

```text
Urban Traffic/
│
├── Templates/
│   ├── auth/
│   ├── dashboard/
│   ├── database/
│   ├── home.html
│   ├── predict.html
│   └── reports.html
│
├── analysis/
├── config/
├── models/
├── services/
├── static/
│   └── css/
├── utils/
│
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Khushi-Singhal562/Urban-Traffic-Hotspot-Predictor.git
```

### 2. Open Project Folder

```bash
cd Urban-Traffic-Hotspot-Predictor
```

### 3. Create Virtual Environment

```bash
python -m venv venv
```

### 4. Activate Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Environment Variables

Create a `.env` file in the main project folder and add your own credentials:

```env
TOMTOM_API_KEY=your_api_key
SECRET_KEY=your_secret_key
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=urban_traffic_db
```

### 7. Configure MySQL Database

Import the SQL file available in:

`Templates/database/database.sql`

Make sure MySQL is running and database credentials are configured correctly.

### 8. Run the Application

```bash
python app.py
```

Open your browser and visit:

`http://127.0.0.1:5000/`

## 🔐 Security

- API keys and database credentials are stored in environment variables.
- `.env` is excluded using `.gitignore`.
- Virtual environment files are not uploaded to GitHub.

## 🚀 Future Improvements

- Advanced traffic prediction
- More traffic hotspot analysis
- Improved real-time traffic visualization
- Advanced traffic analytics

## 👩‍💻 Developer

**Khushi Singhal**

MCA Student

GitHub: https://github.com/Khushi-Singhal562

---

⭐ If you find this project interesting, don't forget to star the repository!