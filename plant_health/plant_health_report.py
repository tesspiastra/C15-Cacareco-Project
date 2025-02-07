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

    water_threshold = pd.Timedelta(hours=24)
    soil_moisture_safe = (20.0, 98.0)
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


def format_alert_data_html(alert_data: list[dict]):
    """Format the alert data into HTML tables with improved styling."""

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

    for alert in alert_data:
        plant_name = alert['plant_name']
        issue = alert['issue']

        if issue == 'needs_water':
            time_delta = alert['time_delta']
            needs_water_table += f"""
            <tr>
                <td>{plant_name}</td>
                <td>{issue}</td>
                <td>{str(time_delta)}</td>
            </tr>
            """
        elif issue in ['soil_moisture', 'temperature']:
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

    needs_water_table += "</tbody></table>"
    other_alerts_table += "</tbody></table>"

    html_body += needs_water_table + "<br>" + other_alerts_table
    return html_body


def format_alert_data_sms(alert_data):
    """Format the alert data into a plain-text style message for SNS."""

    sns_message = "Plant Health Alerts:\n\n"
    sns_message += "====================\n"
    sns_message += "Plants Needing Water\n"
    sns_message += "====================\n"
    sns_message += f"{'Plant Name':<30}{'Issue':<15}{'Time Since Last Watering'}\n"
    sns_message += "-" * 70 + "\n"

    for alert in alert_data:
        if alert['issue'] == 'needs_water':
            plant_name = alert['plant_name']
            time_delta = alert['time_delta']
            sns_message += f"{plant_name:<30}{
                alert['issue']:<15}{str(time_delta)}\n"

    sns_message += "\n"
    sns_message += "====================================\n"
    sns_message += "Plants with Soil Moisture or Temperature Alerts\n"
    sns_message += "====================================\n"
    sns_message += f"{'Plant Name':<30}{'Issue':<15}{
        'Average Value':<15}{'Last 3 Values'}\n"
    sns_message += "-" * 80 + "\n"

    for alert in alert_data:
        if alert['issue'] in ['soil_moisture', 'temperature']:
            plant_name = alert['plant_name']
            issue = alert['issue']
            average_value = alert['average_value']
            values = ', '.join([str(value) for value in alert['values']])
            sns_message += f"{plant_name:<30}{issue:<15}{average_value:<15}{values}\n"

    sns_message += "\n"
    return sns_message


def send_email(body: str, to_address: list[str]):
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
    logging.info("Plant alerts email successfully sent to recipients.")


def send_sms(message):
    """Send an SNS message."""

    sns_client = client('sns')
    topic_arn = 'arn:aws:sns:eu-west-2:129033205317:c15-cacareco-plant-health-alerts'

    sns_client.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject="Plant Health Alerts"
    )
    logging.info("Plant alerts SMS successfully sent to topic subscribers.")


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

    email_body = format_alert_data_html(warning_data)
    sms_body = format_alert_data_sms(warning_data)

    send_email(
        email_body, ['trainee.zander.rackevic@sigmalabs.co.uk',
                     'trainee.benjamin.smith@sigmalabs.co.uk',
                     'trainee.tess.piastra@sigmalabs.co.uk',
                     'trainee.abdulrahman.dahir@sigmalabs.co.uk',
                     'ruy.zambrano@sigmalabs.co.uk',
                     'dan.keefe@sigmalabs.co.uk'])
    send_sms(sms_body)

    return {
        'status_code': 200,
        'data': json.dumps(warning_data)
    }
