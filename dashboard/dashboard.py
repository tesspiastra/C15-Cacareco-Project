"""This module configures the streamlit dashboard"""
from os import environ as ENV

import altair as alt
import pandas as pd
import streamlit as st
from pymssql import connect
from dotenv import load_dotenv
from boto3 import client


def get_connection_rds():
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


def homepage(data):
    """Creates the project dashboard homepage"""
    st.title("LMNH Botanty Department Dashboard")

    left_col, right_col = st.columns(2)


def hist_page(data):
    """Page for the historical data"""


def scatter_latest_readings(conn):
    """Queries the data for the most recent readings"""
    with conn.cursor() as cur:
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

        cur.execute(q)
        columns = [desc[0] for desc in cur.description]
        df = pd.DataFrame(cur.fetchall(), columns=columns)

    return df


def display_temp_and_moisture():
    """Makes the graph to show the latest readings"""
    base = alt.Chart(scatter_df).encode(
        alt.X("plant_name", title="Plant Name")
    )
    scatter_1 = base.mark_point(color="blueviolet").encode(
        alt.Y("soil_moisture:Q", title="Soil Moisture"),
        alt.Tooltip("recording_taken:T", title="Timestamp", format="%H:%M:%S")
    )

    scatter_2 = base.mark_point(color="red").encode(
        alt.Y("temperature:Q", title="Temperature"),
        alt.Tooltip("recording_taken:T", title="Timestamp", format="%H:%M:%S")
    )

    chart = alt.layer(scatter_1, scatter_2).resolve_scale(
        y="independent"

    ).properties(
        title="Latest Temperature and Soil Moisture Readings per Plant",
    )

    return chart


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection_rds()
    scatter_df = scatter_latest_readings(conn)
