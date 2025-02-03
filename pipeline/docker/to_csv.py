import pymssql
from dotenv import load_dotenv
from os import environ
from datetime import datetime


def query_db(query: str, params: list) -> tuple:
    load_dotenv()
    conn = pymssql.connect(
        environ["DB_HOST"], environ["DB_USER"], environ["DB_PASSWORD"], environ["DB_NAME"])
    cursor = conn.cursor()

    cursor.execute(query, params)
    output = cursor.fetchall()
    return output


def get_daily_data():
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


def tuples_to_csv(tuple_data):
    pass


def write_to_s3():
    pass


if __name__ == "__main__":
    data = get_daily_data()
    tuples_to_csv(data)
    write_to_s3()
