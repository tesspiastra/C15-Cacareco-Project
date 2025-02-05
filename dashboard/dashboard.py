import altair as alt
import pandas as pd
import streamlit as st
from pymssql import connect, Connection
from os import environ as ENV
from dotenv import load_dotenv


def get_connection() -> Connection:
    """Makes a connection with the SQL Server database."""
    return connect(
        server=ENV["DB_HOST"],
        port=ENV["DB_PORT"],
        user=ENV["DB_USER"],
        password=ENV["DB_PASSWORD"],
        database=ENV["DB_NAME"]
    )

def setup_sidebar(plants: list[str]):
    """Sets up the filters in the side bar"""
    currently_viewing = st.sidebar.selectbox(
        "Currently Viewing", ["Today", "Historical"])
    
    plant_to_view = st.sidebar.selectbox("Plant to view", plants)


def display_temperature_and_moisture():
    pass


def display_average_temperature():
    pass

def last_watered():
    pass

def average_soil_moisture():
    pass


def homepage(conn: Connection):
    """The default homepage of the dashboard"""
    st.title("LMNH Botany Department Dashboard")
    st.sidebar.header("Filters")
    plants = ["cactus", "flowers", "bird of paradise"]
    setup_sidebar(plants)
    
    
    left_col, right_col = st.columns(2)
    with left_col:
        display_temperature_and_moisture()
        display_average_temperature()
    with right_col:
        last_watered()
        average_soil_moisture()

if __name__ == "__main__":
    load_dotenv()
    conn = get_connection()
    homepage(conn)
