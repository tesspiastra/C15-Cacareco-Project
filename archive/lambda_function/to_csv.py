"""Handler for extracting most recent data from an RDS and uploading it to a CSV in an S3 bucket"""
from os import environ, path, makedirs
import csv
from datetime import datetime, date

from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
import pymssql


def query_db(query: str, params: list) -> tuple:
    """Query a MS SQL Server Database"""
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
            plant_name, botanist_name, region_name, city_name, country_name, recording_taken, soil_moisture, temperature, last_watered
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
    s3_filepath = f"{datetime.now().strftime("%Y/%m/%d")}_hist.csv"
    local_filepath = f"data/{s3_filepath}"
    if not path.exists(directories):
        makedirs(directories)
    with open(local_filepath, "w") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(("plant_name",
                             "botanist_name",
                             "region_name",
                             "city_name",
                             "country_name",
                             "recording_taken",
                             "soil_moisture",
                             "temperature",
                             "last_watered"))
        csv_writer.writerows(tuple_data)
    return s3_filepath


def write_to_s3(filepath: str) -> bool:
    """write a csv file to an S3 bucket"""
    s3 = boto3.client("s3", aws_access_key_id=environ["AWS_ACCESS_KEY"],
                      aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY"])
    local_path = "data/" + filepath
    try:
        response = s3.upload_file(local_path,
                                  "c15-cacareco-archive", filepath)
    except ClientError as e:
        print(e)
        return False
    return True


def handler(event, context):
    load_dotenv()
    data = get_daily_data()
    filepath = tuples_to_csv(data)
    write_to_s3(filepath)


if __name__ == "__main__":
    handler(None, None)
