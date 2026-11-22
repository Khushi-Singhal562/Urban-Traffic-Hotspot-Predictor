CREATE DATABASE urban_traffic_db;

USE urban_traffic_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE traffic_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    location VARCHAR(150) NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    vehicle_count INT,
    average_speed FLOAT,
    traffic_density FLOAT,
    weather VARCHAR(50),
    accident BOOLEAN DEFAULT FALSE,
    traffic_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);