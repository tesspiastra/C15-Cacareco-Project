# Built-in
from os import environ as ENV
from datetime import datetime
# Installed
import requests as req
from pymssql import connect, Connection
from dotenv import load_dotenv


def get_plant_data(url, plant_id: int) -> dict:
    """Fetches plant data by plant_id."""
    response = req.get(f'{url}{plant_id}')

    return response.json()


def extract_all_plant_data() -> dict:
    """Fetches all plant data and stores it in a dictionary."""
    
    url = 'https://data-eng-plants-api.herokuapp.com/plants/'
    plant_data = []
    for plant_id in range(50):
        plant_data.append(get_plant_data(url, plant_id))

    return plant_data


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


def validate_and_transform(data: dict, conn) -> tuple:
    """Validates and transforms the API response into a format suitable for the database."""
    plant_id = data.get("plant_id")
    recording_taken = parse_datetime(
        data.get("recording_taken"), "%Y-%m-%d %H:%M:%S")
    soil_moisture = validate_soil_moisture(data.get("soil_moisture"))
    temperature = validate_temperature(data.get("temperature"))
    last_watered = parse_datetime(
        data.get("last_watered"), "%a, %d %b %Y %H:%M:%S %Z")

    botanist_email = data.get("botanist", {}).get("email")

    cursor = conn.cursor()
    cursor.execute("SELECT botanist_email, botanist_id FROM botanist")
    botanist_map = {row[0]: row[1] for row in cursor.fetchall()}
    cursor.close()

    botanist_id = botanist_map.get(botanist_email)

    if not all([soil_moisture, temperature, last_watered]) or None in (botanist_id, plant_id, recording_taken):
        return None

    return (botanist_id, plant_id, recording_taken, soil_moisture, temperature, last_watered)


def upload_data(conn: Connection, data: list[tuple]):
    """Uploads data to database"""
    with conn.cursor() as cursor:
        query = """INSERT INTO plant_status (botanist_id, plant_id, recording_taken, soil_moisture, temperature, last_watered)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
        cursor.executemany(query, data)
    conn.commit()
    print("Uploaded to database")

def handler():
    plants = extract_all_plant_data()
    data = []
    conn = get_connection()
    print(plants)
    for plant in plants:
        transformed_entry = validate_and_transform(plant, conn)
        if transformed_entry is not None:
            data.append(transformed_entry)

    upload_data(conn, data)
    conn.close()
    
