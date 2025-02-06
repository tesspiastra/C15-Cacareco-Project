"""A script for checking plant metrics."""

import json
import logging
from os import environ as ENV
import pandas as pd
from pymssql import connect, Connection
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


def get_connection() -> Connection:
    """Makes a connection with the SQL Server database."""

    connection = connect(
        server=ENV["DB_HOST"],
        port=ENV["DB_PORT"],
        user=ENV["DB_USER"],
        password=ENV["DB_PASSWORD"],
        database=ENV["DB_NAME"]
    )
    logging.info("Established a secure connection to the database.")
    return connection


def get_plant_data(conn: Connection) -> list[dict]:
    """Loads relevant data from daily RDS."""

    query = """
        SELECT
            p.plant_name,
            ps.recording_taken,
            ps.soil_moisture,
            ps.temperature,
            ps.last_watered
        FROM plant p 
        JOIN plant_status ps ON (p.plant_id = ps.plant_id);
    """
    with conn.cursor(as_dict=True) as cur:
        cur.execute(query)
        result = cur.fetchall()
    logging.info("Successfully loaded plant data.")
    return result


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
                    'values': [round(value, 2) for value in last_three_soil_moisture]
                })
            if is_out_of_range(last_three_temperature, *temperature_safe):
                avg_temp = last_three_temperature.mean()
                alert_data.append({
                    'plant_name': plant_name,
                    'issue': 'temperature',
                    'average_value': round(float(avg_temp), 2),
                    'values': [round(value, 2) for value in last_three_temperature]
                })

    _ = [logging.warning(data) for data in alert_data]
    return alert_data


def format_alert_data(alert_data):
    """Format the alert data into HTML tables with improved styling."""
    # Initialize the HTML body with a header
    html_body = """
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 10px;
            text-align: center;
            border: 1px solid #ddd;
        }
        th {
            background-color: #4CAF50;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        tr:nth-child(odd) {
            background-color: #ffffff;
        }
        h2 {
            color: #333;
            font-family: Arial, sans-serif;
        }
        h3 {
            color: #4CAF50;
            font-family: Arial, sans-serif;
        }
    </style>
    <h2>Plant Health Alerts</h2>
    """

    # Table for 'needs_water' alerts
    needs_water_table = """
    <h3>Plants Needing Water</h3>
    <table>
        <thead>
            <tr>
                <th>Plant Name</th>
                <th>Issue</th>
                <th>Time Since Last Watering</th>
            </tr>
        </thead>
        <tbody>
    """

    # Table for 'soil_moisture' and 'temperature' alerts
    other_alerts_table = """
    <h3>Plants with Soil Moisture or Temperature Alerts</h3>
    <table>
        <thead>
            <tr>
                <th>Plant Name</th>
                <th>Issue</th>
                <th>Average Value</th>
                <th>Last 3 Values</th>
            </tr>
        </thead>
        <tbody>
    """

    # Process each alert data
    for alert in alert_data:
        plant_name = alert['plant_name']
        issue = alert['issue']

        if issue == 'needs_water':
            # Add 'needs_water' alert to its table
            time_delta = alert['time_delta']
            needs_water_table += f"""
            <tr>
                <td>{plant_name}</td>
                <td>{issue}</td>
                <td>{str(time_delta)}</td>
            </tr>
            """
        elif issue in ['soil_moisture', 'temperature']:
            # Add 'soil_moisture' or 'temperature' alert to its table
            average_value = alert['average_value']
            values = ', '.join([str(value) for value in alert['values']])
            other_alerts_table += f"""
            <tr>
                <td>{plant_name}</td>
                <td>{issue}</td>
                <td>{average_value}</td>
                <td>{values}</td>
            </tr>
            """

    # Close the tables
    needs_water_table += "</tbody></table>"
    other_alerts_table += "</tbody></table>"

    # Combine both tables
    html_body += needs_water_table + "<br>" + other_alerts_table

    return html_body


def send_email(body, to_address):
    """Sends the plant data by email using AWS SES."""

    ses_client = client('ses', region_name='eu-west-2')
    response = ses_client.send_email(
        Source='trainee.zander.rackevic@sigmalabs.co.uk',
        Destination={
            'ToAddresses':
                to_address,
        },
        Message={
            'Subject': {
                'Data': "Plant Health Alerts"
            },
            'Body': {
                'Text': {
                    'Data': json.dumps(body, indent=4)
                },
                'Html': {
                    'Data': f"<html><body>{body}</body></html>"
                }
            }
        }
    )
    return response


def handler(event=None, context=None):
    """AWS Lambda handler function."""

    setup_logging()

    conn = get_connection()
    plant_data = get_plant_data(conn)
    conn.close()

    df = pd.DataFrame(plant_data)
    df_sorted = df.sort_values(
        by=['plant_name', 'recording_taken'], ascending=[True, False])
    warning_data = get_alert_data(df_sorted)

    body = format_alert_data(warning_data)

    response = send_email(
        body, ['trainee.zander.rackevic@sigmalabs.co.uk',
               'trainee.benjamin.smith@sigmalabs.co.uk',
               'trainee.tess.piastra@sigmalabs.co.uk'])
    logging.info("SES response: %s", response)

    return {
        'status_code': 200,
        'data': json.dumps(warning_data)
    }


if __name__ == '__main__':
    print(handler())
