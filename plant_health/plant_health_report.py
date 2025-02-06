"""A script for checking plant metrics."""

import json
import logging
from datetime import date
from os import environ as ENV
import pandas as pd
from dotenv import load_dotenv
from boto3 import client


def setup_logging(level=20):
    """Setup the basicConfig."""
    log_format = "{asctime} - {levelname} - {message}"
    log_datefmt = "%Y-%m-%d %H:%M"
    logging.basicConfig(
        level=level,
        format=log_format,
        style="{",
        datefmt=log_datefmt
    )
    logging.info("Logging to console.")


def connect_to_s3():
    """Connects to plant archive S3."""

    s3 = client("s3", aws_access_key_id=ENV["AWS_ACCESS_KEY"],
                aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])
    logging.info("Successfully connected to S3.")
    return s3


def list_objects(s3_client, bucket_name: str, prefix: str) -> list[str]:
    """Returns a list of object names in a specific bucket."""

    objects = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    return [o["Key"] for o in objects['Contents']]


def download_objects(s3_client, bucket_name: str, prefix: str, objects: list[str]) -> str:
    """Downloads objects from a bucket."""

    plants_file = f"{date.today().day:02}_hist.csv"
    plants_today = f"{prefix}{plants_file}"
    if plants_today in objects:
        s3_client.download_file(
            bucket_name, plants_today, f"data/{plants_file}")
        logging.info("Downloaded file from s3 bucket: %s", plants_today)
        return plants_file
    else:
        logging.error("No file found.")


def is_out_of_range(values, range_min, range_max) -> bool:
    """Calculate if the values provided are out of range."""

    return all(v < range_min or v > range_max for v in values)


def get_alert_data(df: pd.DataFrame):
    """Retrieves plant information marked as warning."""

    water_threshold = pd.Timedelta(hours=36)
    soil_moisture_safe = (20.0, 80.0)
    temperature_safe = (9.0, 30.0)
    alert_data = []

    for plant_name, group in df.groupby('plant_name'):
        most_recent = group.head(1)
        time_delta = most_recent['recording_taken'].values[0] - \
            most_recent['last_watered'].values[0]
        if time_delta > water_threshold:
            alert_data.append({
                'plant_name': plant_name,
                'issue': 'needs_water',
                'time_delta': time_delta
            })

        if len(group) >= 3:
            recent_group = group.head(3)
            last_three_soil_moisture = recent_group['soil_moisture'].values
            last_three_temperature = recent_group['temperature'].values

            if is_out_of_range(last_three_soil_moisture, *soil_moisture_safe):
                avg_soil_moisture = last_three_soil_moisture.mean()
                alert_data.append({
                    'plant_name': plant_name,
                    'issue': 'soil_moisture',
                    'average_value': round(float(avg_soil_moisture), 2),
                    'values': last_three_soil_moisture
                })
            if is_out_of_range(last_three_temperature, *temperature_safe):
                avg_temp = last_three_temperature.mean()
                alert_data.append({
                    'plant_name': plant_name,
                    'issue': 'temperature',
                    'average_value': round(float(avg_temp), 2),
                    'values': last_three_temperature
                })

    _ = [logging.warning(data) for data in alert_data]
    return alert_data


def handler(event=None, context=None):
    """AWS Lambda handler function."""
    setup_logging()
    load_dotenv()

    bucket = "c15-cacareco-archive"
    prefix = f"{date.today().year}/{date.today().month:02}/"

    s3 = connect_to_s3()
    content = list_objects(s3, bucket, prefix)
    plants = download_objects(s3, bucket, prefix, content)
    df = pd.read_csv(f"data/{plants}")
    df['recording_taken'] = pd.to_datetime(df['recording_taken'])
    df['last_watered'] = pd.to_datetime(df['last_watered'])

    df_sorted = df.sort_values(
        by=['plant_name', 'recording_taken'], ascending=[True, False])
    warning_data = get_alert_data(df_sorted)

    return {
        'status_code': 200,
        'data': json.dumps(warning_data)
    }


if __name__ == '__main__':
    handler()
