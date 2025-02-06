"""This module configures the streamlit dashboard"""
from os import environ as ENV

from boto3 import client
from pymssql import connect
import altair as alt
import pandas as pd
import streamlit as st
from pymssql import connect, Connection
from dotenv import load_dotenv


def get_connection_rds() -> Connection:
    """Makes a connection with the SQL Server database."""
    return connect(
        server=ENV["DB_HOST"],
        port=ENV["DB_PORT"],
        user=ENV["DB_USER"],
        password=ENV["DB_PASSWORD"],
        database=ENV["DB_NAME"]
    )


def get_connection_s3():
    return client('s3', aws_access_key_id=ENV["ACCESS_KEY"],
                  aws_secret_access_key=ENV["SECRET_KEY"])


def list_objects(s3_client, bucket_name: str, prefix: str) -> list[str]:
    objects = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    return [o["Key"] for o in objects.get('Contents', [])]


def read_s3_file(s3_client, bucket_name: str, file_key: str) -> pd.DataFrame:
    obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    return pd.read_csv(obj['Body'])

def get_s3_data(conn: Connection, date_to_view: str) -> pd.DataFrame:
    """Gets the data from the S3 bucket according to the date"""
    bucket_name = ENV["S3_BUCKET"]
    prefix = "historical/"
    files = list_objects(s3_client, bucket_name, prefix)

    selected_date = st.sidebar.date_input("Select Date", date.today())
    
    file_name = f"{prefix}{selected_date.day:02}_hist.csv"
    if file_name in files:
        df = read_s3_file(s3_client, bucket_name, file_name)
        return df

def display_temp_and_moisture(conn):
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

    base = alt.Chart(df).encode(
        alt.X("plant_name", title="Plant Name")
    )
    scatter_1 = base.mark_point(color="blueviolet").encode(
        alt.Y("soil_moisture:Q", title="Soil Moisture"),
        tooltip=[alt.Tooltip("recording_taken:T", title="Timestamp", format="%H:%M:%S"),
                 alt.Tooltip("soil_moisture:Q", title="Soil Moisture")]
    )

    scatter_2 = base.mark_point(color="red").encode(
        alt.Y("temperature:Q", title="Temperature"),
        tooltip=[alt.Tooltip("recording_taken:T", title="Timestamp", format="%H:%M:%S"),
                 alt.Tooltip("temperature:Q", title="Temperature")]
    )

    chart = alt.layer(scatter_1, scatter_2).resolve_scale(
        y="independent"

    ).properties(
        title="Latest Temperature and Soil Moisture Readings per Plant",
    )

    return st.altair_chart(chart)


def get_plants(conn: Connection) -> list[str]:
    """Fetches all plants from the database."""
    with conn.cursor() as cursor:
        cursor.execute("SELECT plant_name FROM plant")
        return [plant[0] for plant in cursor.fetchall()]


def setup_sidebar(plants: list[str]) -> tuple[list[str], str]:
    """Sets up the filters in the sidebar and updates the selected page"""
    page_options = ["Homepage", "Historical Data", "General Stats"]

    if "page" not in st.session_state:
        st.session_state.page = "Homepage"

    st.session_state.page = st.sidebar.radio("Currently Viewing", page_options)

    if st.session_state.page == "Homepage":
        plants_to_view = st.sidebar.multiselect(
            "Plant to view", plants, default=plants)
        return (plants_to_view, None)

    elif st.session_state.page == "Historical Data":
        plants_to_view = st.sidebar.multiselect(
            "Plant to view", plants, default=plants)
        date_to_view = st.sidebar.date_input("Date to view")
        return plants_to_view, date_to_view

    elif st.session_state.page == "General Stats":
        return None, None


@st.cache_data
def fetch_data(_conn: Connection, query: str) -> pd.DataFrame:
    """Fetches data from the database and returns it as a DataFrame"""
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    return pd.DataFrame(rows)


def display_average_temperature(conn: Connection):
    """Bar chart showing average temperature per plant"""
    df = fetch_data(conn, """SELECT p.plant_name, AVG(ps.temperature) AS avg_temperature
                            FROM plant_status AS ps
                            JOIN plant AS p ON ps.plant_id = p.plant_id
                            GROUP BY p.plant_name""")
    chart = alt.Chart(df).mark_bar().encode(
        x="avg_temperature",
        y="plant_name"
    ).properties(
        width=600,
        height=400
    )
    st.altair_chart(chart)


def last_watered(conn: Connection):
    """Scatter plot showing last_watered time for each plant"""
    df = fetch_data(conn, """SELECT p.plant_name, ps.last_watered
                            FROM plant_status AS ps
                            JOIN plant AS p ON ps.plant_id = p.plant_id""")
    chart = alt.Chart(df).mark_circle().encode(
        x="last_watered",
        y="plant_name"
    ).properties(
        width=600,
        height=400
    )
    st.altair_chart(chart)


def average_soil_moisture(conn: Connection):
    """Bar chart showing average soil moisture per plant"""
    df = fetch_data(conn, """SELECT p.plant_name, AVG(ps.soil_moisture) AS avg_soil_moisture
                            FROM plant_status AS ps
                            JOIN plant AS p ON ps.plant_id = p.plant_id
                            GROUP BY p.plant_name""")
    chart = alt.Chart(df).mark_bar().encode(
        x="avg_soil_moisture",
        y="plant_name"
    ).properties(
        width=600,
        height=400
    )
    st.altair_chart(chart)


def temperature_over_time(conn: Connection):
    """Line chart showing temperature over time"""
    pass


def soil_moisture_over_time(conn: Connection):
    """Line chart showing soil moisture over time"""
    pass


def number_of_waterings(conn: Connection):
    """Bar chart showing number of waterings per plant"""
    pass


def unique_origins(conn: Connection):
    """Map showing unique origins of plants"""
    df = fetch_data(conn, """SELECT p.plant_name, o.latitude, o.longitude
                                FROM plant AS p
                                JOIN origin_location AS o ON p.origin_location_id = o.origin_location_id""")
    st.map(df)


def botanist_attending_plants(conn: Connection):
    """Bar chart showing number of plants each botanist is attending"""
    df = fetch_data(conn, """SELECT b.botanist_name, COUNT(ps.plant_id) AS num_plants
                                FROM botanist AS b
                                JOIN plant_status AS ps ON b.botanist_id = ps.botanist_id
                                GROUP BY b.botanist_name;
                                """)
    chart = alt.Chart(df).mark_bar().encode(
        x="num_plants",
        y="botanist_name"
    ).properties(
        width=600,
        height=400
    )
    st.altair_chart(chart)


def homepage(conn: Connection):
    """The default homepage of the dashboard"""
    st.title("LMNH Botany Department Dashboard")
    left_col, right_col = st.columns(2)
    with left_col:
        display_temp_and_moisture(conn)
        display_average_temperature(conn)
    with right_col:
        last_watered(conn)
        average_soil_moisture(conn)


def historical_data(conn: Connection, plants_to_view: list[str], date_to_view: str):
    """Dashboard page for historical data"""

    st.title("LMNH Botany Department Dashboard")
    st.subheader("Historical Data")
    s3_client = get_connection_s3()

    s3_data = get_s3_data(s3_client, date_to_view)
    

    left_col, right_col = st.columns(2)
    with left_col:
        temperature_over_time(conn, day_data_df)
    with right_col:
        soil_moisture_over_time(conn, day_data_df)

    number_of_waterings(conn)


def general_stats(conn: Connection):
    """Dashboard page for general stats"""
    st.title("LMNH Botany Department Dashboard")
    st.subheader("General Stats")

    left_col, right_col = st.columns(2)
    with left_col:
        unique_origins(conn)
    with right_col:
        botanist_attending_plants(conn)


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection_rds()

    # scatter_df = scatter_latest_readings(conn)

    plants = get_plants(conn)
    plants_to_view, date_to_view = setup_sidebar(plants)

    if st.session_state.page == "Homepage":
        homepage(conn, plants_to_view)
    elif st.session_state.page == "Historical Data":
        historical_data(conn, plants_to_view, date_to_view)
    elif st.session_state.page == "General Stats":
        general_stats(conn)

    conn.close()
