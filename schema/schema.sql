IF OBJECT_ID('plant_status', 'U') IS NOT NULL DROP TABLE plant_status;
IF OBJECT_ID('botanist', 'U') IS NOT NULL DROP TABLE botanist;
IF OBJECT_ID('plant', 'U') IS NOT NULL DROP TABLE plant;
IF OBJECT_ID('origin_location', 'U') IS NOT NULL DROP TABLE origin_location;
IF OBJECT_ID('city', 'U') IS NOT NULL DROP TABLE city;
IF OBJECT_ID('country', 'U') IS NOT NULL DROP TABLE country;

CREATE TABLE country (
    country_id SMALLINT IDENTITY(1,1) PRIMARY KEY,
    country_code VARCHAR(2) NOT NULL
);

CREATE TABLE city (
    city_id INT IDENTITY(1,1) PRIMARY KEY,
    city_name VARCHAR(30) NOT NULL,
    country_id SMALLINT NOT NULL,
    time_zone VARCHAR(30) NOT NULL,
    FOREIGN KEY (country_id) REFERENCES country(country_id)
);

CREATE TABLE origin_location (
    origin_location_id INT IDENTITY(1,1) PRIMARY KEY,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    city_id INT NOT NULL,
    FOREIGN KEY (city_id) REFERENCES city(city_id)
);

CREATE TABLE plant (
    plant_id INT PRIMARY KEY,
    plant_name VARCHAR(30) NOT NULL,
    plant_scientific_name VARCHAR(100),
    origin_location_id INT NOT NULL,
    image_link VARCHAR(250),
    FOREIGN KEY (origin_location_id) REFERENCES origin_location(origin_location_id)
);

CREATE TABLE botanist (
    botanist_id SMALLINT IDENTITY(1,1) PRIMARY KEY,
    botanist_name VARCHAR(30) NOT NULL,
    botanist_email VARCHAR(30) NOT NULL,
    botanist_phone VARCHAR(30)
);

CREATE TABLE plant_status (
    plant_status_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    botanist_id SMALLINT NOT NULL,
    plant_id INT NOT NULL,
    recording_taken DATETIME NOT NULL,
    soil_moisture FLOAT,
    temperature FLOAT,
    last_watered DATETIME,
    FOREIGN KEY (botanist_id) REFERENCES botanist(botanist_id),
    FOREIGN KEY (plant_id) REFERENCES plant(plant_id)
);
