"""Stores the functions that query the database"""
from os import environ as ENV

from boto3 import client
import altair as alt
import pandas as pd
import streamlit as st
from pymssql import connect, Connection
from dotenv import load_dotenv
from datetime import date


@st.cache_data
def fetch_data(_conn: Connection, query: str) -> pd.DataFrame:
    """Fetches data from the database and returns it as a DataFrame"""
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute(query)
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


def latest_temp_and_moisture(conn):
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
            WHERE row_num = 1
            ORDER BY recording_taken DESC"""
    df = fetch_data(conn, q)
    return df


def average_temp_data(conn: Connection):
    df = fetch_data(conn, """SELECT p.plant_name, AVG(ps.temperature) AS avg_temperature
                            FROM plant_status AS ps
                            JOIN plant AS p ON ps.plant_id = p.plant_id
                            GROUP BY p.plant_name""")
    return df


def get_last_watered_data(conn):
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
            WHERE row_num = 1
            """
    df = fetch_data(conn, q)
    return df


def get_avg_moisture_data():
    df = fetch_data(conn, """SELECT p.plant_name, AVG(ps.soil_moisture) AS avg_soil_moisture
                            FROM plant_status AS ps
                            JOIN plant AS p ON ps.plant_id = p.plant_id
                            GROUP BY p.plant_name""")
    return df


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection_rds()
