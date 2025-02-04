"""Handler for extracting most recent data from an RDS and uploading it to a CSV in an S3 bucket"""
from os import environ, path, makedirs
import csv
from datetime import datetime, date

from dotenv import load_dotenv
import boto3
import pymssql


def query_db(query: str, params: list) -> tuple:
    """Query a MS SQL Server Database"""
    load_dotenv()
    conn = pymssql.connect(environ["DB_HOST"],
                           environ["DB_USER"],
                           environ["DB_PASSWORD"],
                           environ["DB_NAME"])
    cursor = conn.cursor()

    q = "ALTER USER gamma  WITH DEFAULT_SCHEMA = gamma"
    cursor.execute(q)

    cursor.execute(query, params)
    output = cursor.fetchall()
    return output


def get_daily_data():
    """get today's data from the RDS"""
    q = """
        SELECT 
            plant_name, botanist_name, region_name, city_name, country_name
        FROM 
            plant_status 
        JOIN plant ON (plant_status.plant_id = plant.plant_id)
        JOIN botanist ON (plant_status.botanist_id = botanist.botanist_id) 
        JOIN origin_location ON (origin_location.origin_location_id = plant.origin_location_id)
        JOIN city ON (city.city_id = origin_location.city_id)
        JOIN country ON (country.country_id = city.country_id)
        WHERE 
            DATENAME(year, recording_taken) = DATENAME(year, CURRENT_TIMESTAMP)
            AND 
            DATENAME(month, recording_taken) = DATENAME(month, CURRENT_TIMESTAMP)
            AND
            DATENAME(day, recording_taken) = DATENAME(day, CURRENT_TIMESTAMP);
        """

    data_today = query_db(q, [])
    return data_today


def tuples_to_csv(tuple_data: list[tuple]) -> str:
    """write a list of tuples to a csv file"""
    directories = "data/" + datetime.now().strftime("%Y/%m")
    full_filename = datetime.now().strftime("%Y/%m/%d")
    filepath = f"data/{full_filename}_hist.csv"
    if not path.exists(directories):
        makedirs(directories)
    with open(filepath, "w") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(tuple_data)
    return full_filename


def write_to_s3(filepath: str):
    """write a csv file to an S3 bucket"""
    s3 = boto3.resource("s3")

    s3.Bucket("BUCKET_NAME").upload_file(filepath)


def handler(event, context):
    data = get_daily_data()
    filepath = tuples_to_csv(data)
    # write_to_s3(filepath)


if __name__ == "__main__":
    handler(None, None)
