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
    """Fetches all plant names from the database."""
    with conn.cursor() as cursor:
        cursor.execute("SELECT plant_name FROM plant")
        return [plant[0] for plant in cursor.fetchall()]


def setup_sidebar(plants: list[str]) -> tuple[list[str], str]:
    """Sets up the sidebar filters and returns selected values."""
    page_options = ["Homepage", "Historical Data", "General Stats"]

    if "page" not in st.session_state:
        st.session_state.page = "Homepage"

    st.session_state.page = st.sidebar.radio("Currently Viewing", page_options)

    plants_to_view = st.sidebar.multiselect(
        "Plant to view", plants, default=plants)

    if st.session_state.page == "Historical Data":
        date_to_view = st.sidebar.date_input("Date to view")
        return plants_to_view, date_to_view

    return plants_to_view, None


@st.cache_data
def fetch_data(_conn: Connection, query: str, params: tuple = ()) -> pd.DataFrame:
    """Fetches data from the database and returns it as a DataFrame."""
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

    return pd.DataFrame(rows)


def display_temperature_and_moisture(conn: Connection, plants_to_view: list[str]):
    """Scatter graph showing the latest temperature and moisture readings for each selected plant."""
    if not plants_to_view:
        st.warning("No plants selected.")
        return

    placeholders = ",".join(["%s"] * len(plants_to_view))
    query = f"""
        SELECT p.plant_name, ps.temperature, ps.soil_moisture
        FROM plant_status AS ps
        JOIN plant AS p ON ps.plant_id = p.plant_id
        WHERE p.plant_name IN ({placeholders})
        AND ps.recording_taken = (SELECT MAX(recording_taken) FROM plant_status WHERE plant_id = ps.plant_id);
    """
    df = fetch_data(conn, query, tuple(plants_to_view))

    if df.empty:
        st.warning("No data available for the selected plants.")
        return

    chart = alt.Chart(df).mark_circle().encode(
        x="temperature",
        y="soil_moisture",
        color="plant_name"
    ).properties(width=600, height=400)
    st.altair_chart(chart)


def display_average_temperature(conn: Connection, plants_to_view: list[str]):
    """Bar chart showing average temperature per selected plant."""
    if not plants_to_view:
        st.warning("No plants selected.")
        return

    placeholders = ",".join(["%s"] * len(plants_to_view))
    query = f"""
        SELECT p.plant_name, AVG(ps.temperature) AS avg_temperature
        FROM plant_status AS ps
        JOIN plant AS p ON ps.plant_id = p.plant_id
        WHERE p.plant_name IN ({placeholders})
        GROUP BY p.plant_name;
    """
    df = fetch_data(conn, query, tuple(plants_to_view))

    if df.empty:
        st.warning("No data available for the selected plants.")
        return

    chart = alt.Chart(df).mark_bar().encode(
        x="avg_temperature",
        y="plant_name"
    ).properties(width=600, height=400)
    st.altair_chart(chart)


def last_watered(conn: Connection, plants_to_view: list[str]):
    """Scatter plot showing last watered time for each selected plant."""
    if not plants_to_view:
        st.warning("No plants selected.")
        return

    placeholders = ",".join(["%s"] * len(plants_to_view))
    query = f"""
        SELECT p.plant_name, ps.last_watered
        FROM plant_status AS ps
        JOIN plant AS p ON ps.plant_id = p.plant_id
        WHERE p.plant_name IN ({placeholders});
    """
    df = fetch_data(conn, query, tuple(plants_to_view))

    if df.empty:
        st.warning("No data available for the selected plants.")
        return

    chart = alt.Chart(df).mark_circle().encode(
        x="last_watered",
        y="plant_name"
    ).properties(width=600, height=400)
    st.altair_chart(chart)


def average_soil_moisture(conn: Connection, plants_to_view: list[str]):
    """Bar chart showing average soil moisture per selected plant."""
    if not plants_to_view:
        st.warning("No plants selected.")
        return

    placeholders = ",".join(["%s"] * len(plants_to_view))
    query = f"""
        SELECT p.plant_name, AVG(ps.soil_moisture) AS avg_soil_moisture
        FROM plant_status AS ps
        JOIN plant AS p ON ps.plant_id = p.plant_id
        WHERE p.plant_name IN ({placeholders})
        GROUP BY p.plant_name;
    """
    df = fetch_data(conn, query, tuple(plants_to_view))

    if df.empty:
        st.warning("No data available for the selected plants.")
        return

    chart = alt.Chart(df).mark_bar().encode(
        x="avg_soil_moisture",
        y="plant_name"
    ).properties(width=600, height=400)
    st.altair_chart(chart)


def homepage(conn: Connection, plants_to_view: list[str]):
    """The default homepage of the dashboard."""
    st.title("LMNH Botany Department Dashboard")
    left_col, right_col = st.columns(2)

    with left_col:
        display_temperature_and_moisture(conn, plants_to_view)
        display_average_temperature(conn, plants_to_view)

    with right_col:
        last_watered(conn, plants_to_view)
        average_soil_moisture(conn, plants_to_view)


def historical_data(conn: Connection, plants_to_view: list[str], date_to_view):
    """Dashboard page for historical data."""
    st.title("LMNH Botany Department Dashboard")
    st.subheader("Historical Data")

    # Placeholder
    st.warning("Historical data functionality not yet implemented.")


def general_stats(conn: Connection, plants_to_view: list[str]):
    """Dashboard page for general stats."""
    st.title("LMNH Botany Department Dashboard")
    st.subheader("General Stats")

    # Placeholder
    st.warning("General stats functionality not yet implemented.")


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection()

    plants = get_plants(conn)
    plants_to_view, date_to_view = setup_sidebar(plants)

    if st.session_state.page == "Homepage":
        homepage(conn, plants_to_view)
    elif st.session_state.page == "Historical Data":
        historical_data(conn, plants_to_view, date_to_view)
    elif st.session_state.page == "General Stats":
        general_stats(conn, plants_to_view)

    conn.close()
