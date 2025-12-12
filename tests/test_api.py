import pytest
import requests

BASE_URL = "http://localhost:8080"


def test_get_rates_nbu():
    response = requests.get(f"{BASE_URL}/rates?bank=nbu")
    data = response.json()

    assert response.status_code == 200
    assert "rates" in data
    assert len(data["rates"]) > 0
    assert "request_id" in data


def test_get_specific_currency():
    response = requests.get(f"{BASE_URL}/rates?bank=nbu&vcc=USD")
    data = response.json()
    assert response.status_code == 200
    assert len(data["rates"]) == 1
    assert data["requested_currency"] == "USD"


def test_get_from_db():
    response = requests.get(f"{BASE_URL}/rates/db?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5


def test_invalid_bank():
    response = requests.get(f"{BASE_URL}/rates?bank=undefined_bank")
    assert response.status_code == 400



