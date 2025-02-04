"""Loads all plant data for the current minute into the database"""
from os import environ as ENV

from dotenv import load_dotenv
import pymssql
from pymssql import Connection

load_dotenv()


def get_connection():
    """Makes a connection with the SQLServer database"""
    return pymssql.connect(
        server=ENV["DB_HOST"],
        port=ENV["DB_PORT"],
        user=ENV["DB_USER"],
        password=ENV["DB_PASSWORD"],
        database=ENV["DB_NAME"],
        as_dict=True)


def upload_data(conn: Connection, data):
    """Uploads data to database"""
    with conn.cursor as cursor:
        query = """INSERT INTO plant_status (
            botanist_id,plant_id,recording_taken,
            soil_moisture,temperature, last_watered)"""
        cursor.executemany(query, data)
    conn.commit()
    print("Uploaded to database")


if __name__ == "__main__":
    load_dotenv()
    conn = get_connection()
