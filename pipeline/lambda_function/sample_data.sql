INSERT INTO country (country_name) VALUES 
    ('TEST_COUNTRY');

INSERT INTO city (city_name, country_id) VALUES 
    ('TEST_CITY', 1);

INSERT INTO origin_location 
    (latitude, longitude, region_name, city_id) 
VALUES 
    (1.1, 1.1, 'TEST_REGION', 1);

INSERT INTO plant 
    (plant_name, origin_location_id) 
VALUES 
    ('TEST_PLANT', 1);

INSERT INTO botanist 
    (botanist_name, botanist_email) 
VALUES 
    ('TEST_BOTANIST_NAME', 'TEST_BOTANIST_EMAIL');

INSERT INTO plant_status 
    (botanist_id, plant_id, recording_taken) 
VALUES 
    (1, 1, CURRENT_TIMESTAMP);