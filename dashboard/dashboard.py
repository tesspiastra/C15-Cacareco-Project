"""This module configures the streamlit dashboard"""
from os import environ as ENV

from boto3 import client
import pandas as pd
import streamlit as st
from pymssql import Connection
from dotenv import load_dotenv
from datetime import date

from dash_queries import get_connection_rds, get_latest_temp_and_moisture, get_average_temp_data, get_last_watered_data, get_avg_moisture_data, get_unique_origins, get_botanists
from dash_graphs import temp_and_moist_chart, display_average_temperature, scatter_last_watered, average_soil_moisture, temperature_over_time, soil_moisture_over_time, number_of_waterings, botanist_attending_plants
# s3 functions


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


def setup_sidebar(plants: list[dict],) -> tuple[list[str], str]:
    """Sets up the filters in the sidebar and updates the selected page"""
    page_options = ["Homepage", "Historical Data", "General Stats"]

    if "page" not in st.session_state:
        st.session_state.page = "Homepage"

    st.session_state.page = st.sidebar.radio("Currently Viewing", page_options)

    if st.session_state.page == "Homepage":

        plant_name_list = st.sidebar.multiselect(
            "Plants:", plants["plant_name"].unique(), default=plants["plant_name"].unique())
        return plant_name_list, None
    elif st.session_state.page == "Historical Data":

        plant_name_list = st.sidebar.multiselect(
            "Plants:", plants["plant_name"].unique(), default=plants["plant_name"].unique())
        time_list = st.sidebar.date_input("Select Date", date.today())
        return plant_name_list, time_list

# Pages


def homepage(conn: Connection, plant_name_list: list[str]):
    """The default homepage of the dashboard"""
    st.title("LMNH Botany Department Dashboard")
    left_col, right_col = st.columns(2)

    with left_col:
        graph1_data = get_latest_temp_and_moisture(conn)
        temp_and_moist_chart(graph1_data)

        graph2_data = get_average_temp_data(conn)
        display_average_temperature(graph2_data)
    with right_col:
        graph3_data = get_last_watered_data(conn)
        # last_watered(conn)
        scatter_last_watered(graph3_data)

        graph4_data = get_avg_moisture_data(conn)
        average_soil_moisture(graph4_data)


def historical_data(conn: Connection, plants_to_view: list[str], time_list: list[date]):
    """Dashboard page for historical data"""

    st.title("LMNH Botany Department Dashboard")
    st.subheader("Historical Data")
    s3_client = get_connection_s3()

    s3_data_df = get_s3_data(s3_client, time_list)

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
        st.map(get_unique_origins(conn))
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
        historical_data(conn)
    elif st.session_state.page == "General Stats":
        general_stats(conn)

    conn.close()
