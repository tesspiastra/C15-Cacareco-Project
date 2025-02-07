"""performs extraction on the api as part of a ETL pipeline"""
import requests as req


def get_plant_data(url, plant_id: int) -> dict:
    """Fetches plant data by plant_id."""
    response = req.get(f'{url}{plant_id}')

    return response.json()


def extract_all_plant_data() -> dict:
    """Fetches all plant data and stores it in a dictionary."""
    plant_data = {}
    url = 'https://data-eng-plants-api.herokuapp.com/plants/'

    for plant_id in range(50):
        print("done")
        plant_data[plant_id] = get_plant_data(url, plant_id)

    return plant_data


if __name__ == "__main__":
    plants = extract_all_plant_data()
    print(plants[0].get('name'))
