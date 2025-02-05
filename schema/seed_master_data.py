"""Performs extraction on the API as part of an ETL pipeline"""

# Imports

# Built-in
from os import environ as ENV
# Installed
import requests as req
from pymssql import connect
from dotenv import load_dotenv


def get_connection():
    """Makes a connection with the SQL Server database."""
    return connect(
        server=ENV["DB_HOST"],
        port=ENV["DB_PORT"],
        user=ENV["DB_USER"],
        password=ENV["DB_PASSWORD"],
        database=ENV["DB_NAME"]
    )


def get_plant_data(url, plant_id: int) -> dict:
    """Fetches plant data by plant_id."""
    response = req.get(f'{url}{plant_id}')
    if response.status_code == 200:
        return response.json()
    return {}


def extract_all_api_data() -> dict:
    """Fetches all plant data and stores it in a dictionary."""
    plant_data = {}
    url = 'https://data-eng-plants-api.herokuapp.com/plants/'

    for plant_id in range(50):
        plant_info = get_plant_data(url, plant_id)
        if plant_info:
            plant_data[plant_id] = plant_info

    return plant_data


def extract_country_data(api_data: dict) -> list:
    """Extracts Country Data from the api_data dictionary."""
    country_list = []
    seen_countries = set()

    for plant in api_data.values():
        country_code = plant.get(
            'origin_location', [None, None, None, None, None])[3]
        if country_code not in seen_countries:
            country_list.append((country_code,))
            seen_countries.add(country_code)
    return country_list


def extract_city_data(api_data: dict, country_map: dict) -> list:
    """Extracts City Data from the api_data dictionary."""
    city_list = []
    seen_cities = set()

    for plant in api_data.values():
        city_name = plant.get('origin_location', [
                              None, None, None, None, None])[2]
        country_code = plant.get(
            'origin_location', [None, None, None, None, None])[3]
        country_id = country_map.get(country_code)
        time_zone = plant.get('origin_location', [
            None, None, None, None, None])[4]

        if city_name not in seen_cities:
            city_list.append((city_name, country_id, time_zone))
            seen_cities.add((city_name))
    return city_list


def extract_origin_location_data(api_data: dict, city_map: dict) -> list:
    """Extracts origin location data from api_data dictionary"""
    origin_location = []
    seen_origin_location = set()

    for plant in api_data.values():
        origin_info = plant.get(
            "origin_location", [None, None, None, None, None])
        latitude = origin_info[0]
        longitude = origin_info[1]
        city_name = origin_info[2]
        city_id = city_map.get(city_name)

        if (latitude, longitude) not in seen_origin_location:
            origin_location.append((latitude, longitude, city_id))
            seen_origin_location.add((latitude, longitude))

    return origin_location


def extract_plant_data(api_data: dict, origin_location_map: dict) -> list:
    """Extracts all the plant data from the api_data dictionary"""
    plants = []

    for plant in api_data.values():
        plant_id = int(plant.get("plant_id"))
        name = plant.get("name")
        scientific_name = plant.get("scientific_name")
        origin_info = plant.get(
            "origin_location", [None, None, None, None, None])
        latitude = float(origin_info[0])
        longitude = float(origin_info[1])
        origin_location_id = origin_location_map.get(
            f'{('%.3f' % latitude).rstrip('0').rstrip('.')},{('%.3f' % longitude).rstrip('0').rstrip('.')}')

        images = plant.get("images") or {}
        image_link = images.get("original_url")

        plants.append(
            (plant_id, name, scientific_name, origin_location_id, image_link))

    return plants


def extract_botany_data(api_data: dict) -> list:
    """Extracts botanist data from the api_data dictionary."""
    botany_list = []
    seen_emails = set()

    for plant in api_data.values():
        botanist = plant.get('botanist', {})
        name = botanist.get('name')
        email = botanist.get('email')
        phone = botanist.get('phone')

        if email and email not in seen_emails:
            botany_list.append((name, email, phone))
            seen_emails.add(email)

    return botany_list


def load_into_db(conn, data: list, query: str) -> None:
    """Loads data into the database using executemany for bulk insertion."""
    cursor = conn.cursor()
    cursor.executemany(query, data)
    conn.commit()


def get_id_mapping(conn, query: str) -> dict:
    """Fetches mapping of names to their respective IDs from the database."""
    cursor = conn.cursor()
    cursor.execute(query)
    return {row[0]: row[1] for row in cursor.fetchall()}


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection()

    api_data = extract_all_api_data()
    countries = extract_country_data(api_data)
    load_into_db(conn, countries,
                 "INSERT INTO country (country_code) VALUES (%s)")

    country_map = get_id_mapping(
        conn, "SELECT country_code, country_id FROM country")

    cities = extract_city_data(api_data, country_map)

    load_into_db(
        conn, cities, "INSERT INTO city (city_name, country_id, time_zone) VALUES (%s, %s, %s)")

    city_map = get_id_mapping(conn, "SELECT city_name, city_id FROM city")

    origin_location = extract_origin_location_data(api_data, city_map)

    load_into_db(
        conn, origin_location, "INSERT INTO origin_location (latitude, longitude, city_id) VALUES (%s, %s, %s)")

    origin_location_map = get_id_mapping(conn,
                                         "SELECT CONCAT(ROUND(latitude, 3), ',', ROUND(longitude, 3)) AS lat_long, origin_location_id FROM origin_location")

    plants = extract_plant_data(api_data, origin_location_map)
    load_into_db(
        conn, plants, "INSERT INTO plant (plant_id, plant_name, plant_scientific_name, origin_location_id, image_link) VALUES (%s, %s, %s, %s, %s)")

    botanists = extract_botany_data(api_data)
    load_into_db(conn, botanists,
                 "INSERT INTO botanist (botanist_name, botanist_email, botanist_phone) VALUES (%s, %s, %s)")

    conn.close()
