"""This module configures the streamlit dashboard"""
from os import environ as ENV

import altair as alt
import pandas as pd
import streamlit as st
from pymssql import connect
from os import environ as ENV
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


if __name__ == "__main__":
    load_dotenv()
