"""Transformation part of the ETL pipeline, cleans, and reshapes the data for insertion of plant_status in DB"""

# Imports

## Built-in
from os import environ as ENV
from datetime import datetime
## Installed
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


def fetch_latest_plant_status(url: str, plant_id: int) -> dict:
    """Fetches the latest plant status from the API."""
    response = req.get(f"{url}{plant_id}")
    if response.status_code == 200:
        return response.json()
    return {}


def parse_datetime(date_str: str, format_str: str) -> datetime:
    """Parses a datetime string into a datetime object."""
    return datetime.strptime(date_str, format_str) if date_str else None


def validate_soil_moisture(soil_moisture: float) -> float:
    """Validates soil moisture values."""
    return soil_moisture if soil_moisture is not None and 0 <= soil_moisture <= 100 else None


def validate_temperature(temperature: float) -> float:
    """Validates temperature values."""
    return temperature if temperature is not None and -50 <= temperature <= 50 else None


def validate_and_transform(data: dict, botanist_map: dict) -> tuple:
    """Validates and transforms the API response into a format suitable for the database."""
    plant_id = data.get("plant_id")
    recording_taken = parse_datetime(
        data.get("recording_taken"), "%Y-%m-%d %H:%M:%S")
    soil_moisture = validate_soil_moisture(data.get("soil_moisture"))
    temperature = validate_temperature(data.get("temperature"))
    last_watered = parse_datetime(
        data.get("last_watered"), "%a, %d %b %Y %H:%M:%S %Z")

    botanist_email = data.get("botanist", {}).get("email")
    botanist_id = botanist_map.get(botanist_email)

    return (botanist_id, plant_id, recording_taken, soil_moisture, temperature, last_watered)
    
    



def get_id_mapping(conn, query: str) -> dict:
    """Fetches mapping of identifiers from the database."""
    cursor = conn.cursor()
    cursor.execute(query)
    return {row[0]: row[1] for row in cursor.fetchall()}



if __name__ == "__main__":
    load_dotenv()
    conn = get_connection()

    botanist_map = get_id_mapping(
        conn, "SELECT botanist_email, botanist_id FROM botanist")
    plants = {
        1: {
            "name": "Venus flytrap",
            "scientific_name": "Dionaea muscipula",
            "origin_location": ["33.95015", "-118.03917", "South Whittier", "US", "America/Los_Angeles"],
            "botanist": {"name": "Gertrude Jekyll", "email": "gertrude@botany.com", "phone": "123-456-7890"},
            "images": {"original_url": "http://example.com/image1.jpg"}
        },
        2: {
            "name": "Sundew",
            "scientific_name": "Drosera capensis",
            "origin_location": ["-33.918861", "18.423300", "Cape Town", "ZA", "Africa/Johannesburg"],
            "botanist": {"name": "Carl Linnaeus", "email": "carl@botany.com", "phone": "987-654-3210"},
            "images": {"original_url": "http://example.com/image2.jpg"}
        }
    }
    data = []
    for plant in plants: # This comes from load script
        data.append(validate_and_transform(plant, botanist_map))

    conn.close()
