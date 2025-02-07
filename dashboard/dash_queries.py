"""Stores the functions that query the database"""
from os import environ as ENV

import pandas as pd
import streamlit as st
from pymssql import connect, Connection
from dotenv import load_dotenv


@st.cache_data
def fetch_data(_conn: Connection, query: str, params) -> pd.DataFrame:
    """Fetches data from the database and returns it as a DataFrame"""
    with _conn.cursor(as_dict=True) as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()
    return pd.DataFrame(rows)


def get_connection_rds() -> Connection:
    """Makes a connection with the SQL Server database."""
    return connect(
        server=ENV["DB_HOST"],
        port=ENV["DB_PORT"],
        user=ENV["DB_USER"],
        password=ENV["DB_PASSWORD"],
        database=ENV["DB_NAME"]
    )


# convert queries to use the VIEW names_and_data


def plant_names():
    """Defines a set of plant names"""
    plant_names = (
        "Epipremnum Aureum",
        "Venus flytrap",
        "Corpse flower",
        "Rafflesia arnoldii",
        "Black bat flower",
        "Pitcher plant",
        "Wollemi pine",
        "Bird of paradise",
        "Cactus",
        "Dragon tree,",
        "Asclepias Curassavica",
        "Brugmansia X Candida",
        "Canna ‘Striata’",
        "Colocasia Esculenta",
        "Cuphea ‘David Verity’",
        "Euphorbia Cotinifolia",
        "Ipomoea Batatas",
        "Manihot Esculenta ‘Variegata’",
        "Musa Basjoo",
        "Salvia Splendens",
        "Anthurium",
        "Bird of Paradise",
        "Cordyline Fruticosa",
        "Ficus",
        "Palm Trees",
        "Dieffenbachia Seguine",
        "Spathiphyllum",
        "Croton",
        "Aloe Vera",
        "Ficus Elastica",
        "Sansevieria Trifasciata",
        "Philodendron Hederaceum",
        "Schefflera Arboricola",
        "Aglaonema Commutatum",
        "Monstera Deliciosa",
        "Tacca Integrifolia",
        "Saintpaulia Ionantha",
        "Gaillardia",
        "Amaryllis",
        "Caladium Bicolor",
        "Chlorophytum Comosum",
        "Araucaria Heterophylla",
        "Begonia",
        "Medinilla Magnifica",
        "Calliandra Haematocephala",
        "Zamioculcas Zamiifolia",
        "Crassula Ovata",
        "Psychopsis Papilio"
    )

    return plant_names


def get_latest_temp_and_moisture(conn, params):
    """Queries the data for the most recent readings"""
    q = """with ranked_data as (SELECT plant_name,
                recording_taken,
                soil_moisture,
                temperature,
                ROW_NUMBER() OVER(
                    PARTITION BY plant_name
                    ORDER BY recording_taken DESC) as row_num
            FROM names_and_data)
            SELECT *
            FROM ranked_data
            WHERE row_num = 1 AND plant_name IN %s
            ORDER BY recording_taken DESC"""
    return fetch_data(conn, q, params)


def get_last_watered_data(conn, params):
    """Queries the data for the last time ech plant was watered"""
    q = """with lastwatered as (
            SELECT 
                last_watered, plant_name,recording_taken,
                ROW_NUMBER() OVER(
                    PARTITION BY plant_name 
                    ORDER BY recording_taken DESC) as row_num
            FROM names_and_data)
            SELECT * FROM lastwatered
            WHERE row_num = 1 AND plant_name IN %s
            """
    return fetch_data(conn, q, params)


def get_average_temp_data(conn: Connection, params):
    """Queries the data for the average temperatures of each plant"""
    q = """SELECT plant_name, 
                AVG(temperature) AS avg_temperature
            FROM names_and_data
            WHERE plant_name IN %s
            GROUP BY plant_name"""
    return fetch_data(conn, q, params)


def get_avg_moisture_data(conn, params):
    """Queries the data for the average soil moistures of each plant"""
    q = """SELECT plant_name, 
                AVG(soil_moisture) AS avg_soil_moisture
            FROM names_and_data
            WHERE plant_name IN %s
            GROUP BY plant_name
            """
    return fetch_data(conn, q, params)


def get_temp_over_time(conn, params):
    """Queries database for unique locations"""
    q = """SELECT recording_taken, 
                temperature,
                plant_name
            FROM names_and_data 
            WHERE recording_taken = %s"""
    return fetch_data(conn, q, params)


def get_unique_origins(conn, params):
    """Queries database for unique locations"""
    q = """SELECT p.plant_name, 
                o.latitude, 
                o.longitude
            FROM plant AS p
            JOIN origin_location AS o 
                ON p.origin_location_id = o.origin_location_id
            WHERE plant_name IN %s"""
    return fetch_data(conn, q, params)


def get_botanists(conn, params=None):
    """Retrieves all botanists"""
    q = """SELECT b.botanist_name, 
                COUNT(ps.plant_id) AS num_plants
            FROM botanist AS b
            JOIN plant_status AS ps 
                ON b.botanist_id = ps.botanist_id
            GROUP BY b.botanist_name
                                """
    return fetch_data(conn, q, params)


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection_rds()
    plants = plant_names()
