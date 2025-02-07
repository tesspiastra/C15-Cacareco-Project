"""Contains the functions displaying the graphs"""
from os import environ as ENV

import altair as alt
import pandas as pd
import streamlit as st
from pymssql import Connection
from dotenv import load_dotenv

from dash_queries import fetch_data, get_connection_rds
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
    chart = alt.Chart(s3_data_df).mark_line().encode


def soil_moisture_over_time(s3_data_df: pd.DataFrame):
    """Line chart showing soil moisture over time"""
    pass


# General stats page graphs


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


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection_rds()
