from unittest.mock import patch, MagicMock
import pytest
from extract import get_plant_data


@pytest.fixture
def plant_data():
    return {
        "botanist": {
            "email": "gertrude.jekyll@lnhm.co.uk",
            "name": "Gertrude Jekyll",
            "phone": "001-481-273-3691x127"
        },
        "last_watered": "Mon, 03 Feb 2025 13:54:32 GMT",
        "name": "Venus flytrap",
        "origin_location": [
            "33.95015",
            "-118.03917",
            "South Whittier",
            "US",
            "America/Los_Angeles"
        ],
        "plant_id": 1,
        "recording_taken": "2025-02-03 16:28:40",
        "soil_moisture": 90.8972845511811,
        "temperature": 12.0375669599007
    }


@patch("requests.get")  # Mock the `requests.get` call
def test_get_plant_data(mock_get, plant_data):
    url = "https://data-eng-plants-api.herokuapp.com/plants/"

    mock_response = MagicMock()
    mock_response.json.return_value = plant_data
    mock_get.return_value = mock_response

    result = get_plant_data(url, 1)

    assert result == plant_data

    mock_get.assert_called_once_with(f"{url}1")
