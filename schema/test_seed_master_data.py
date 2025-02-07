"""Test 'seed_master_data.py' using pytest"""
from unittest.mock import patch, MagicMock
import pytest
from seed_master_data import (
    get_plant_data, extract_country_data, extract_city_data,
    extract_origin_location_data, extract_plant_data, extract_botany_data,
    load_into_db, get_id_mapping
)


@pytest.fixture
def sample_api_data():
    """sample plant data expected from the API"""
    return {
        1: {
            "plant_id": "1",
            "name": "Venus flytrap",
            "scientific_name": "Dionaea muscipula",
            "origin_location": [
                "33.95015",
                "-118.03917",
                "South Whittier",
                "US",
                "America/Los_Angeles"
            ],
            "botanist": {
                "name": "Gertrude Jekyll",
                "email": "gertrude@botany.com",
                "phone": "123-456-7890"
            },
            "images": {"original_url": "http://example.com/image1.jpg"}
        },
        2: {
            "plant_id": "2",
            "name": "Sundew",
            "scientific_name": "Drosera capensis",
            "origin_location": [
                "-33.918861",
                "18.423300",
                "Cape Town",
                "ZA",
                "Africa/Johannesburg"],
            "botanist": {
                "name": "Carl Linnaeus",
                "email": "carl@botany.com",
                "phone": "987-654-3210"},
            "images": {"original_url": "http://example.com/image2.jpg"}
        }
    }


@patch("requests.get")
def test_get_plant_data(mock_get, sample_api_data):
    """test expected behavior for the 'get_plant_data' function"""
    url = "https://data-eng-plants-api.herokuapp.com/plants/"
    plant_id = 1

    mock_response = MagicMock()
    mock_response.json.return_value = sample_api_data[plant_id]
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    result = get_plant_data(url, plant_id)
    assert result == sample_api_data[plant_id]
    mock_get.assert_called_once_with(f"{url}{plant_id}", timeout=20)


def test_extract_country_data(sample_api_data):
    """tests expected behavior for the 'extract_country_data' function"""
    expected = [("US",), ("ZA",)]
    result = extract_country_data(sample_api_data)  # Pass dictionary directly
    assert result == expected


def test_extract_city_data(sample_api_data):
    """tests expected behavior for the 'extract_city_data' function"""
    country_map = {"US": 1, "ZA": 2}
    expected = [
        ("South Whittier", 1, "America/Los_Angeles"),
        ("Cape Town", 2, "Africa/Johannesburg")
    ]
    result = extract_city_data(sample_api_data, country_map)
    assert result == expected


def test_extract_origin_location_data(sample_api_data):
    """tests expected behavior for the 'extract_origin_location_data' function"""
    city_map = {"South Whittier": 1, "Cape Town": 2}
    expected = [('33.95015', '-118.03917', 1), ('-33.918861', '18.423300', 2)]
    result = extract_origin_location_data(sample_api_data, city_map)
    assert result == expected


def test_extract_plant_data(sample_api_data):
    """tests expected behavior for the 'extract_plant_data' function"""
    origin_location_map = {
        "33.95,-118.039": 1,
        "-33.919,18.423": 2
    }
    expected = [
        (1, "Venus flytrap", "Dionaea muscipula",
         1, "http://example.com/image1.jpg"),
        (2, "Sundew", "Drosera capensis", 2, "http://example.com/image2.jpg")
    ]
    result = extract_plant_data(sample_api_data, origin_location_map)
    assert result == expected


def test_extract_botany_data(sample_api_data):
    """tests expected behavior for the 'extract_botany_data' function"""
    expected = [
        ("Gertrude Jekyll", "gertrude@botany.com", "123-456-7890"),
        ("Carl Linnaeus", "carl@botany.com", "987-654-3210")
    ]
    result = extract_botany_data(sample_api_data)  # Pass dictionary directly
    assert result == expected


@patch("pymssql.connect")
def test_get_id_mapping(mock_connect):
    """tests expected behavior for the 'get_id_mapping' function"""
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [("US", 1), ("ZA", 2)]

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    query = "SELECT country_name, country_id FROM country"
    result = get_id_mapping(mock_conn, query)
    assert result == {"US": 1, "ZA": 2}
    mock_cursor.execute.assert_called_once_with(query)


@patch("pymssql.connect")
def test_load_into_db(mock_connect):
    """tests expected behavior for the 'load_into_db' function"""
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    data = [("US",), ("ZA",)]
    query = "INSERT INTO country (country_name) VALUES (%s)"

    load_into_db(mock_conn, data, query)
    mock_cursor.executemany.assert_called_once_with(query, data)
    mock_conn.commit.assert_called_once()
