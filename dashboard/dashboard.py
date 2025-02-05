import altair as alt
import pandas as pd
import streamlit as st
from pymssql import connect
from os import environ as ENV
from dotenv import load_dotenv


def get_connection():
    """Makes a connection with the SQL Server database."""
    return connect(
        server=ENV["DB_HOST"],
        port=ENV["DB_PORT"],
        user=ENV["DB_USER"],
        password=ENV["DB_PASSWORD"],
        database=ENV["DB_NAME"]
    )

if __name__ == "__main__":
    load_dotenv()