-- DROP DATABASE house_price_db;
CREATE DATABASE IF NOT EXISTS house_price_db;
USE house_price_db;

CREATE TABLE IF NOT EXISTS cities(
    city_id INT AUTO_INCREMENT PRIMARY KEY ,
    city_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS districts(
    district_id INT AUTO_INCREMENT PRIMARY KEY ,
    district_name VARCHAR(100) NOT NULL ,
    city_id INT NOT NULL ,
    FOREIGN KEY (city_id) REFERENCES cities(city_id) ON DELETE CASCADE, UNIQUE KEY unique_district (city_id, district_name)
);

CREATE TABLE IF NOT EXISTS neighborhoods(
    neighborhood_id INT AUTO_INCREMENT PRIMARY KEY ,
    neighborhood_name VARCHAR(100) NOT NULL ,
    district_id INT NOT NULL ,
    FOREIGN KEY (district_id) REFERENCES districts(district_id) ON DELETE CASCADE , UNIQUE KEY unique_neighborhood(district_id, neighborhood_name)
);

CREATE TABLE IF NOT EXISTS listings(
    id INT AUTO_INCREMENT PRIMARY KEY,
    listing_id VARCHAR(50) UNIQUE NOT NULL,
    neighborhood_id INT NOT NULL,
    title VARCHAR(255),
    price BIGINT NOT NULL,
    room_count VARCHAR(20),
    gross_sqm INT,
    net_sqm INT,
    building_age VARCHAR(50),
    floor_level VARCHAR(50),
    heating_type VARCHAR(100),
    is_furnished VARCHAR(50),
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (neighborhood_id) REFERENCES neighborhoods(neighborhood_id) ON DELETE RESTRICT
);