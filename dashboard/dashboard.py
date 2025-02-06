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


def get_plants(conn: Connection) -> list[str]:
    """Fetches all plants from the database."""
    with conn.cursor() as cursor:
        cursor.execute("SELECT plant_name FROM plant")
        return [plant[0] for plant in cursor.fetchall()]


def setup_sidebar(plants: list[str]):
    """Sets up the filters in the sidebar and updates the selected page"""
    page_options = ["Homepage", "Historical Data", "General Stats"]

    if "page" not in st.session_state:
        st.session_state.page = "Homepage"

    st.session_state.page = st.sidebar.radio("Currently Viewing", page_options)

    if st.session_state.page == "Homepage":
        return st.sidebar.multiselect("Plant to view", plants, default=plants)

    elif st.session_state.page == "Historical Data":
        plant_to_view = st.sidebar.selectbox("Plant to view", plants)
        date_to_view = st.sidebar.date_input("Date to view")
        return plant_to_view, date_to_view

    elif st.session_state.page == "General Stats":
        return None


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


def temperature_over_time():
    """Line chart showing temperature over time"""
    pass


def soil_moisture_over_time():
    """Line chart showing soil moisture over time"""
    pass


def number_of_waterings():
    """Bar chart showing number of waterings per plant"""
    pass


def unique_origins():
    """Pie Chart showing unique origins of plants"""
    pass


def botanist_attending_plants():
    """Bar chart showing number of plants each botanist is attending"""
    pass


def homepage(conn: Connection):
    """The default homepage of the dashboard"""
    st.title("LMNH Botany Department Dashboard")
    left_col, right_col = st.columns(2)
    with left_col:
        display_temperature_and_moisture()
        display_average_temperature()
    with right_col:
        last_watered()
        average_soil_moisture()


def historical_data(conn: Connection):
    """Dashboard page for historical data"""
    st.title("LMNH Botany Department Dashboard")
    st.subheader("Historical Data")

    left_col, right_col = st.columns(2)
    with left_col:
        temperature_over_time()
    with right_col:
        soil_moisture_over_time()

    number_of_waterings()


def general_stats(conn: Connection):
    """Dashboard page for general stats"""
    st.title("LMNH Botany Department Dashboard")
    st.subheader("General Stats")

    left_col, right_col = st.columns(2)
    with left_col:
        unique_origins()
    with right_col:
        botanist_attending_plants()


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection()

    plants = get_plants(conn)
    setup_sidebar(plants)

    # Render the appropriate page based on selection
    if st.session_state.page == "Homepage":
        homepage(conn)
    elif st.session_state.page == "Historical Data":
        historical_data(conn)
    elif st.session_state.page == "General Stats":
        general_stats(conn)

    conn.close()
