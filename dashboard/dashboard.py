"""This module configures the streamlit dashboard"""
from os import environ as ENV

from boto3 import client
import altair as alt
import pandas as pd
import streamlit as st
from pymssql import connect, Connection
from dotenv import load_dotenv
from datetime import date

from dash_queries import get_connection_rds, fetch_data, latest_temp_and_moisture, average_temp_data, get_last_watered_data, get_avg_moisture_data


def get_connection_s3():
    return client('s3', aws_access_key_id=ENV["ACCESS_KEY"],
                  aws_secret_access_key=ENV["SECRET_KEY"])


def list_objects(s3_client, bucket_name: str, prefix: str) -> list[str]:
    objects = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    return [o["Key"] for o in objects.get('Contents', [])]


def read_s3_file(s3_client, bucket_name: str, file_key: str) -> pd.DataFrame:
    obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    return pd.read_csv(obj['Body'])


def get_s3_data(s3_client, date_to_view: str) -> pd.DataFrame:
    """Gets the data from the S3 bucket according to the date"""
    bucket_name = ENV["S3_BUCKET"]
    prefix = "historical/"
    files = list_objects(s3_client, bucket_name, prefix)

    file_name = f"{prefix}{date_to_view.day:02}_hist.csv"
    if file_name in files:
        df = read_s3_file(s3_client, bucket_name, file_name)
        return df
    else:
        st.write("No data available for the selected date")


def get_plants(conn: Connection) -> list[str]:
    """Fetches all plants from the database."""
    with conn.cursor() as cursor:
        cursor.execute("SELECT plant_name FROM plant")
        # return [plant[0] for plant in cursor.fetchall()]
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame(cursor.fetchall(), columns=columns)
    return df


def plant_filter(df: pd.DataFrame, selected):
    selected_plants = st.sidebar.multiselect(
        "Plants:", df["plant_name"].unique(), default=df["plant_name"].unique())

    df = df[df["plant_name"].isin(
        selected_plants).value_counts().reset_index()]
    return df


def setup_sidebar(plants: list[str]) -> tuple[list[str], str]:
    """Sets up the filters in the sidebar and updates the selected page"""
    page_options = ["Homepage", "Historical Data", "General Stats"]

    if "page" not in st.session_state:
        st.session_state.page = "Homepage"

    st.session_state.page = st.sidebar.radio("Currently Viewing", page_options)

    if st.session_state.page == "Homepage":

        plants_to_view = st.sidebar.multiselect(
            "Plants:", plants["plant_name"].unique(), default=plants["plant_name"].unique())

        return (plants_to_view, None)

    elif st.session_state.page == "Historical Data":

        plants_to_view = st.sidebar.multiselect(
            "Plants:", plants["plant_name"].unique(), default=plants["plant_name"].unique())
        date_to_view = st.sidebar.date_input("Select Date", date.today())

        return plants_to_view, date_to_view

    elif st.session_state.page == "General Stats":
        return None, None

# Homepage graphs


def temp_and_moist_chart(df):
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


def display_average_temperature(df):
    """Bar chart showing average temperature per plant"""
    chart = alt.Chart(df).mark_bar().encode(
        x="avg_temperature",
        y="plant_name"
    ).properties(
        width=600,
        height=400
    )
    st.altair_chart(chart)


def scatter_last_watered(df):
    """Displays chart for the most recent watered times, for each plant"""
    chart = alt.Chart(df).mark_point().encode(
        alt.X("last_watered:T", title="Time last watered"),
        alt.Y("plant_name:N", title="Plant Name"),
        tooltip=[alt.Tooltip(
            "last_watered", title="Time last watered", format="%b %d %Y %H:%M:%S")]
    ).properties(
        title="Times plants were last watered",
    )

    return st.altair_chart(chart)


# def last_watered(conn: Connection):
#     """Scatter plot showing last_watered time for each plant"""
#     df = fetch_data(conn, """SELECT p.plant_name, ps.last_watered
#                             FROM plant_status AS ps
#                             JOIN plant AS p ON ps.plant_id = p.plant_id""")
#     chart = alt.Chart(df).mark_circle().encode(
#         x="last_watered",
#         y="plant_name"
#     ).properties(
#         width=600,
#         height=400
#     )
#     st.altair_chart(chart)


def average_soil_moisture(df):
    """Bar chart showing average soil moisture per plant"""
    chart = alt.Chart(df).mark_bar().encode(
        x="avg_soil_moisture",
        y="plant_name"
    ).properties(
        width=600,
        height=400
    )
    st.altair_chart(chart)

# Historic page graphs


def temperature_over_time(s3_data_df: pd.DataFrame):
    """Line chart showing temperature over time"""
    pass


def soil_moisture_over_time(s3_data_df: pd.DataFrame):
    """Line chart showing soil moisture over time"""
    pass


def number_of_waterings(s3_data_df: pd.DataFrame):
    """Bar chart showing number of waterings per plant"""
    pass

# General stats page graphs


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

# Pages


def homepage(conn: Connection):
    """The default homepage of the dashboard"""
    st.title("LMNH Botany Department Dashboard")
    left_col, right_col = st.columns(2)

    with left_col:
        graph1_data = plant_filter(latest_temp_and_moisture(conn))
        temp_and_moist_chart(graph1_data)

        graph2_data = plant_filter(average_temp_data(conn))
        display_average_temperature(graph2_data)
    with right_col:
        graph3_data = plant_filter(get_last_watered_data(conn))
        # last_watered(conn)
        scatter_last_watered(graph3_data)

        graph4_data = plant_filter(get_avg_moisture_data(conn))
        average_soil_moisture(graph4_data)


def historical_data(conn: Connection, plants_to_view: list[str], date_to_view: str):
    """Dashboard page for historical data"""

    st.title("LMNH Botany Department Dashboard")
    st.subheader("Historical Data")
    s3_client = get_connection_s3()

    s3_data_df = get_s3_data(s3_client, date_to_view)

    st.write(s3_data_df)

    left_col, right_col = st.columns(2)
    with left_col:
        temperature_over_time(s3_data_df)
    with right_col:
        soil_moisture_over_time(s3_data_df)

    number_of_waterings(s3_data_df)


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

    plants = get_plants(conn)
    setup_sidebar(plants)

    if st.session_state.page == "Homepage":
        homepage(conn)
    elif st.session_state.page == "Historical Data":
        historical_data(conn, plants_to_view, date_to_view)
    elif st.session_state.page == "General Stats":
        general_stats(conn)

    conn.close()
