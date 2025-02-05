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

def setup_sidebar(page: str, plants: list[str]) -> tuple:
    """Sets up the filters in the side bar"""
    currently_viewing = st.sidebar.selectbox(
        "Currently Viewing", ["Today", "Historical"])
    
    plant_to_view = st.sidebar.selectbox("Plant to view", plants)

    general_stats = st.sidebar.button("general stats")


def display_temperature_and_moisture():
    """Scatter graph showing the latest temperature and moisture readings for each plant"""
    pass


def display_average_temperature():
    """Bar chart showing average temperature per plant"""
    pass

def last_watered():
    """Scatter plot showing last_watered time for each plant"""
    pass

def average_soil_moisture():
    """Bar chart showing average soil moisture per plant"""
    pass


def homepage(conn: Connection):
    """The default homepage of the dashboard"""
    st.title("LMNH Botany Department Dashboard")
    st.sidebar.header("Filters")
    plants = ["cactus", "flowers", "bird of paradise"] # example for now
    setup_sidebar(page= "homepage", plants)
    
    
    left_col, right_col = st.columns(2)
    with left_col:
        display_temperature_and_moisture()
        display_average_temperature()
    with right_col:
        last_watered()
        average_soil_moisture()

def general_stats(conn: Connection):
    """Dashboard page for general stats"""
    st.title("LMNH Botany Department Dashboard")
    st.subheader("General Stats")

    setup_sidebar(page= "general_stats")

if __name__ == "__main__":
    load_dotenv()
    conn = get_connection()
    homepage(conn)
