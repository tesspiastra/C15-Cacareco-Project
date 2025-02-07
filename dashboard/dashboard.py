"""This module configures the streamlit dashboard"""
from os import environ as ENV

from boto3 import client
import pandas as pd
import streamlit as st
from pymssql import Connection
from dotenv import load_dotenv
from datetime import date, timedelta

from dash_queries import get_connection_rds, plant_names, get_latest_temp_and_moisture, get_average_temp_data, get_last_watered_data, get_avg_moisture_data, get_unique_origins, get_botanists
from dash_graphs import temp_and_moist_chart, display_average_temperature, scatter_last_watered, average_soil_moisture, temperature_over_time, soil_moisture_over_time, botanist_attending_plants
# s3 functions


def get_connection_s3():
    return client('s3', aws_access_key_id=ENV["ACCESS_KEY"],
                  aws_secret_access_key=ENV["SECRET_KEY"])


def list_objects(s3_client, bucket_name: str) -> list[str]:
    objects = s3_client.list_objects_v2(Bucket=bucket_name)
    return [o["Key"] for o in objects.get('Contents', [])]


def read_s3_file(s3_client, bucket_name: str, file_key: str) -> pd.DataFrame:
    obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    return pd.read_csv(obj['Body'])


def get_s3_data(s3_client, date_to_view: str) -> pd.DataFrame:
    """Gets the data from the S3 bucket according to the date"""
    bucket_name = ENV["S3_BUCKET"]
    files = list_objects(s3_client, bucket_name)
    file_name = f"""{
        date_to_view.year}/{date_to_view.month:02}/{date_to_view.day:02}_hist.csv"""
    st.write("Viewing File:", file_name.split('/')[-1])
    if file_name in files:
        df = read_s3_file(s3_client, bucket_name, file_name)
        return df
    else:
        return None


def setup_sidebar(plants: list[str]) -> tuple[list[str], str]:
    """Sets up the filters in the sidebar and updates the selected page"""
    page_options = ["Homepage", "Historical Data", "General Stats"]

    if "page" not in st.session_state:
        st.session_state.page = "Homepage"

    st.session_state.page = st.sidebar.radio("Currently Viewing", page_options)

    if st.session_state.page == "Homepage":

        plant_name_list = st.sidebar.multiselect(
            "Plants:", plants, default=plants)
        return plant_name_list, None
    elif st.session_state.page == "Historical Data":

        plant_name_list = st.sidebar.multiselect(
            "Plants:", plants, default=plants)

        time = st.sidebar.date_input(
            "Date to view:", value=date.today()-timedelta(days=1))
        return plant_name_list, time

# Pages


def homepage(conn: Connection, plant_name_list: list[str]):
    """The default homepage of the dashboard"""
    st.title("LMNH Botany Department Dashboard")
    left_col, right_col = st.columns(2)

    with left_col:
        graph1_data = get_latest_temp_and_moisture(conn, plant_name_list)
        temp_and_moist_chart(graph1_data)

        graph2_data = get_average_temp_data(conn, plant_name_list)
        display_average_temperature(graph2_data)
    with right_col:
        graph3_data = get_last_watered_data(conn, plant_name_list)
        # last_watered(conn)
        scatter_last_watered(graph3_data)

        graph4_data = get_avg_moisture_data(conn, plant_name_list)
        average_soil_moisture(graph4_data)


def historical_data(conn: Connection, plant_name_list: list[str], time: list):
    """Dashboard page for historical data"""

    st.title("LMNH Botany Department Dashboard")
    st.subheader("Historical Data")
    s3_client = get_connection_s3()

    s3_data_df = get_s3_data(s3_client, time)
    if s3_data_df is not None:
        st.write(s3_data_df)

        filtered_df = s3_data_df[s3_data_df['plant_name'].isin(
            plant_name_list)]
        filtered_df = filtered_df[[
            "recording_taken", "plant_name", "temperature"]].sort_values(by="recording_taken")
        temperature_over_time(filtered_df)

        filtered_df_2 = s3_data_df[s3_data_df['plant_name'].isin(
            plant_name_list)]
        filtered_df_2 = filtered_df_2[[
            "recording_taken", "plant_name", "soil_moisture"]].sort_values(by="recording_taken")
        soil_moisture_over_time(filtered_df)
    else:
        st.write("No data available for the selected date")


def general_stats(conn: Connection):
    """Dashboard page for general stats"""
    st.title("LMNH Botany Department Dashboard")
    st.subheader("General Stats")

    st.map(get_unique_origins(conn))
    get_botanists(conn)


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection_rds()

    plants = plant_names()
    plant_name_list, time = setup_sidebar(plants)

    if st.session_state.page == "Homepage":
        homepage(conn, plant_name_list)
    elif st.session_state.page == "Historical Data":
        historical_data(conn, plant_name_list, time)
    elif st.session_state.page == "General Stats":
        general_stats(conn)

    conn.close()
