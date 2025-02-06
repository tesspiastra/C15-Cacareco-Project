"""Stores the functions that query the database"""
from os import environ as ENV

import pandas as pd
import streamlit as st
from pymssql import connect, Connection
from dotenv import load_dotenv


@st.cache_data
def fetch_data(_conn: Connection, query: str, params: list[int]) -> pd.DataFrame:
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


def get_filters(conn, params):
    """Queries the data for the attributes to filter"""
    q = """SELECT p.plant_name,ps.recording_taken 
                        FROM plant_status AS ps
                        JOIN plant AS p 
                            ON ps.plant_id = p.plant_id"""
    return fetch_data(conn, q, params)


def get_latest_temp_and_moisture(conn, params):
    """Queries the data for the most recent readings"""
    q = """with ranked_data as (SELECT p.plant_name, 
                ps.recording_taken,
                ps.soil_moisture,
                ps.temperature,
                ROW_NUMBER() OVER(
                    PARTITION BY p.plant_name 
                    ORDER BY ps.recording_taken DESC) as row_num
            FROM plant as p
            JOIN plant_status as ps
                ON p.plant_id = ps.plant_id)
            SELECT * 
            FROM ranked_data
            WHERE row_num = 1 AND plant_name = %s
            ORDER BY recording_taken DESC"""
    return fetch_data(conn, q, params)


def get_last_watered_data(conn, params):
    """Queries the data for the last time ech plant was watered"""
    q = """with lastwatered as (
            SELECT 
                ps.last_watered, p.plant_name,ps.recording_taken,
                ROW_NUMBER() OVER(
                    PARTITION BY p.plant_name 
                    ORDER BY recording_taken DESC) as row_num
            FROM plant_status AS ps 
            JOIN plant AS p 
                ON p.plant_id = ps.plant_id)
            SELECT * FROM lastwatered
            WHERE row_num = 1 AND plant_name = %s
            """
    return fetch_data(conn, q, params)


def get_average_temp_data(conn: Connection, params):
    """Queries the data for the average temperatures of each plant"""
    q = """SELECT p.plant_name, AVG(ps.temperature) AS avg_temperature
                            FROM plant_status AS ps
                            JOIN plant AS p ON ps.plant_id = p.plant_id
                            GROUP BY p.plant_name
                            WHERE plant_name = %s"""
    return fetch_data(conn, q, params)


def get_avg_moisture_data(conn, params):
    """Queries the data for the average soil moistures of each plant"""
    q = """SELECT p.plant_name, AVG(ps.soil_moisture) AS avg_soil_moisture
                            FROM plant_status AS ps
                            JOIN plant AS p ON ps.plant_id = p.plant_id
                            GROUP BY p.plant_name
                            WHERE plant_name = %s"""
    return fetch_data(conn, q, params)


def get_unique_origins(conn, params):
    """Queries database for unique locations"""
    q = """SELECT p.plant_name, o.latitude, o.longitude
                                FROM plant AS p
                                JOIN origin_location AS o ON p.origin_location_id = o.origin_location_id
                            WHERE plant_name = %s"""
    return fetch_data(conn, q, params)


def get_botanists(conn, params):
    """Retrieves all botanists"""
    q = """SELECT b.botanist_name, COUNT(ps.plant_id) AS num_plants
                            FROM botanist AS b
                            JOIN plant_status AS ps ON b.botanist_id = ps.botanist_id
                            GROUP BY b.botanist_name
                            WHERE plant_name = %s
                                """
    return fetch_data(conn, q, params)


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection_rds()
    get_filters(conn, [])
