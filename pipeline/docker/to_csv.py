import pymssql
from dotenv import load_dotenv
from os import environ
from datetime import datetime


def query_db(query: str, params: list) -> tuple:
    load_dotenv()
    conn = pymssql.connect(
        environ["DB_HOST"], environ["DB_USER"], environ["DB_PASSWORD"], environ["DB_NAME"])
    cursor = conn.cursor(as_dict=True)

    output = cursor.execute(query, params)
    return output


def get_daily_data():
    today = datetime.now().date()

    q = """
        SELECT
            * 
        FROM 
            plant_status
        WHERE
            DATE(recording_taken) = %s
        """

    data_today = query_db(q, today)


def tuples_to_csv():
    pass


def write_to_s3():
    pass


if __name__ == "__main__":
    data = get_daily_data()
    tuples_to_csv(data)
    write_to_s3()
