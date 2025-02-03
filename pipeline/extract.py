"""performs extract """
import requests as req
    
    
def get_plant_data(plant_id: int) -> list[str]:
    """"""
    url = 'https://data-eng-plants-api.herokuapp.com/plants/'
    response = req.get(f'{url}{plant_id}')
    return response.json()

def extract_all_plant_data():
    """"""
    for i in range(50):
        plant_id = i
        plant = {plant_id: get_plant_data(plant_id)}
        print(plant[i].get('name'))

if __name__ == "__main__":
    extract_all_plant_data()
