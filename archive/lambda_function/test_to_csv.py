"""Tests to_csv.py"""
from unittest.mock import patch, MagicMock
from datetime import datetime

import pytest

from to_csv import tuples_to_csv


@pytest.fixture
def sample_tuple_data():
    """returns example tuple data fetched from an RDS"""
    return [("plant_name_1",
             "botanist_name_1",
             "region_name_1",
             "city_name_1",
             "country_name_1",
             "recording_taken_1",
             "soil_moisture_1",
             "temperature_1",
             "last_watered_1"),
            ("plant_name_2",
             "botanist_name_2",
             "region_name_2",
             "city_name_2",
             "country_name_2",
             "recording_taken_2",
             "soil_moisture_2",
             "temperature_2",
             "last_watered_2")]


@patch("builtins.open")
def test_tuples_to_csv(mock_open, sample_tuple_data):
    """tests correct function input and output"""
    filepath = f"{datetime.now().strftime("%Y/%m/%d")}_hist.csv"
    assert tuples_to_csv(sample_tuple_data) == filepath
