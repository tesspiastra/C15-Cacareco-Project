"""Handler for extracting most recent data from an RDS and uploading it to a CSV in an S3 bucket"""
from os import environ as ENV, path, makedirs
import csv
from datetime import datetime, date

from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
import pymssql


def query_db(query: str, params: list) -> tuple:
    """Query a MS SQL Server Database"""
    conn = pymssql.connect(ENV["DB_HOST"],
                           ENV["DB_USER"],
                           ENV["DB_PASSWORD"],
                           ENV["DB_NAME"])
    cursor = conn.cursor()

    q = f"""
        ALTER USER
            {ENV["DB_USER"]}
        WITH
            DEFAULT_SCHEMA = {ENV["SCHEMA_NAME"]}
        """
    cursor.execute(q)

    cursor.execute(query, params)
    output = cursor.fetchall()
    return output


def get_daily_data():
    """get today's data from the RDS"""
    q = """
        SELECT 
            p.plant_id, 
            p.plant_name, 
            b.botanist_name, 
            c.city_name, 
            c.time_zone, 
            co.country_code, 
            ps.recording_taken, 
            ps.soil_moisture, 
            ps.temperature, 
            ps.last_watered
        FROM 
            plant_status AS ps
        JOIN plant AS p 
            ON (ps.plant_id = p.plant_id)
        JOIN botanist AS b 
            ON (ps.botanist_id = b.botanist_id) 
        JOIN origin_location as ol
            ON (p.origin_location_id = ol.origin_location_id)
        JOIN city AS c 
            ON (c.city_id = ol.city_id)
        JOIN country AS co 
            ON (co.country_id = c.country_id)
        WHERE 
            DATENAME(year, ps.recording_taken) = DATENAME(year, CURRENT_TIMESTAMP)
            AND 
            DATENAME(month, ps.recording_taken) = DATENAME(month, CURRENT_TIMESTAMP)
            AND
            DATENAME(day, ps.recording_taken) = DATENAME(day, CURRENT_TIMESTAMP);
        """

    data_today = query_db(q, [])
    return data_today


def tuples_to_csv(tuple_data: list[tuple]) -> str:
    """write a list of tuples to a csv file and returns the target S3 filepath"""
    directories = "/tmp/" + datetime.now().strftime("%Y/%m")
    s3_filepath = f"{datetime.now().strftime("%Y/%m/%d")}_hist.csv"
    local_filepath = f"/tmp/{s3_filepath}"
    if not path.exists(directories):
        makedirs(directories)
    with open(local_filepath, "w") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(("plant_id",
                             "plant_name",
                             "botanist_name",
                             "city_name",
                             "time_zone",
                             "country_code",
                             "recording_taken",
                             "soil_moisture",
                             "temperature",
                             "last_watered"))
        csv_writer.writerows(tuple_data)
    return s3_filepath


def write_to_s3(filepath: str, s3) -> bool:
    """write a csv file to an S3 bucket"""
    local_path = "/tmp/" + filepath
    try:
        response = s3.upload_file(local_path,
                                  "c15-cacareco-archive", filepath)
    except ClientError as e:
        print(e)
        return False
    return True

def truncate_plant_status():
    """Truncate the plant_status table"""
    q = "TRUNCATE TABLE plant_status"
    query_db(q, [])


def handler(event, context):
    """lambda handler"""
    load_dotenv()
    s3 = boto3.client("s3", aws_access_key_id=ENV["AWS_ACCESS_ID"],
                      aws_secret_access_key=ENV["AWS_ACCESS_SECRET"])
    data = get_daily_data()
    filepath = tuples_to_csv(data)
    write_to_s3(filepath, s3)
    truncate_plant_status()


if __name__ == "__main__":
    handler(None, None)
