"""Performs extraction on the API as part of an ETL pipeline"""

# Imports

## Built in
from os import environ as ENV
## Installed
import requests as req
from pymssql import connect
from dotenv import load_dotenv

## Local Modules



def get_connection():
    """Makes a connection with the SQL Server database."""
    return connect(
        server=ENV["DB_HOST"],
        port=ENV["DB_PORT"],
        user=ENV["DB_USER"],
        password=ENV["DB_PASSWORD"],
        database=ENV["DB_NAME"],
        as_dict=True
    )


def get_plant_data(url, plant_id: int) -> dict:
    """Fetches plant data by plant_id."""
    response = req.get(f'{url}{plant_id}')
    if response.status_code == 200:
        return response.json()
    return {}  # Handle failures gracefully


def extract_all_plant_data() -> dict:
    """Fetches all plant data and stores it in a dictionary."""
    plant_data = {}
    url = 'https://data-eng-plants-api.herokuapp.com/plants/'

    for plant_id in range(50):
        plant_info = get_plant_data(url, plant_id)
        if plant_info:
            plant_data[plant_id] = plant_info

    return plant_data


def extract_botany_data(plants: dict) -> list:
    """Extracts botanist data from the plants dictionary."""
    botany_list = []
    seen_emails = set()

    for plant in plants.values():
        botanist = plant.get('botanist', {})
        name = botanist.get('name')
        email = botanist.get('email')
        phone = botanist.get('phone')

        if email and email not in seen_emails:
            botany_list.append({'name': name, 'email': email, 'phone': phone})
            seen_emails.add(email)

    return botany_list


def load_into_db(conn, botanists: list) -> None:
    """Loads botanist data into the DB."""
    cursor = conn.cursor()

    insert_query = '''INSERT INTO gamma.botanist (botanist_name, botanist_email, botanist_phone)
                      VALUES (%s, %s, %s)'''

    for botanist in botanists:
        cursor.execute(
            insert_query, (botanist['name'], botanist['email'], botanist['phone']))

    conn.commit()


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection()

    plants = extract_all_plant_data()
    botany = extract_botany_data(plants)

    if botany:
        load_into_db(conn, botany)

    conn.close()
