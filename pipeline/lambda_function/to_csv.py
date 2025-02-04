import pymssql
from dotenv import load_dotenv
from os import environ, path, makedirs
from datetime import datetime, date
import csv
import boto3


def query_db(query: str, params: list) -> tuple:
    """Query a MS SQL Server Database"""
    load_dotenv()
    conn = pymssql.connect(
        environ["DB_HOST"], environ["DB_USER"], environ["DB_PASSWORD"], environ["DB_NAME"])
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
            * 
        FROM 
            plant_status 
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
    directories = "data/" + datetime.now().strftime("%Y/%m")
    full_filename = datetime.now().strftime("%Y/%m/%d")
    filepath = f"data/{full_filename}_hist.csv"
    if not path.exists(directories):
        makedirs(directories)
    with open(filepath, "w") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(tuple_data)
    return full_filename


def write_to_s3(filepath):
    s3 = boto3.resource("s3")

    s3.Bucket("BUCKET_NAME").upload_file(filepath)


def handler(event, context):
    data = get_daily_data()
    filepath = tuples_to_csv(data)
    write_to_s3(filepath)


if __name__ == "__main__":
    handler(None, None)
