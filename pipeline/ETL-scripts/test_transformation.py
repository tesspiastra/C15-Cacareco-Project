import pytest
from datetime import datetime
from transform import parse_datetime, validate_soil_moisture, validate_temperature


@pytest.mark.parametrize("temp, expected", [
    (20.5, 20.5),
    (-50, -50),
    (50, 50),
    (-51, None),
    (51, None),
    (None, None),
])
def test_validate_temperature(temp, expected):
    """Tests the temperature validation function with multiple inputs."""
    assert validate_temperature(temp) == expected


@pytest.mark.parametrize("soil_moisture, expected", [
    (20.5, 20.5),
    (-50, None),
    (50, 50),
    (-51, None),
    (51, 51),
    (None, None),
    (120, None)
])
def test_validate_soil_moisture(soil_moisture, expected):
    """Tests the temperature validation function with multiple inputs."""
    assert validate_soil_moisture(soil_moisture) == expected


def test_parse_datetime():
    """Tests the parse_datetime function actually returns a datetime object"""
    date_str = "2025-02-04 14:20:40"
    assert isinstance(parse_datetime(date_str, "%Y-%m-%d %H:%M:%S"), datetime)




