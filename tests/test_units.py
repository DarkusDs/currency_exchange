from unittest.mock import patch

from utils.date_logic import validate_date
from utils.adapter_currency import unify_currency
from api.nbu import get_nbu_exchange_rates
from api.privat import get_privat_exchange_rates
from utils.currency_output import currency_output_filter


def test_validate_date_valid():
    """
    Function to test if a date validation function is working

    :return:
    """
    assert validate_date("20251213") == True

def test_validate_date_invalid_format():
    """
    Function to test if a date validation function is able to detect invalid date inputs

    :return:
    """
    assert validate_date("2025-12-13") == False
    assert validate_date("20251313") == False
    assert validate_date("word") == False

def test_currency_output_filter_no_valcode():
    """
    Function checks what happens when no valcode is provided to currency_output_filter()

    :return:
    """
    data = [
        {"code": "USD", "name": "Долар", "rate": 41.0},
        {"code": "EUR", "name": "Євро", "rate": 45.0},
    ]
    result = currency_output_filter(data, None)
    assert result == data

def test_currency_output_filter_with_valcode():
    """
    Function checks what happens when valcode is provided to currency_output_filter()

    :return:
    """
    data = [
        {"code": "USD", "name": "Долар", "rate": 41.0},
        {"code": "EUR", "name": "Євро", "rate": 45.0},
    ]
    result = currency_output_filter(data, "EUR")
    assert len(result) == 1
    assert result[0]["code"] == "EUR"

@unify_currency(mapper=dict(code='cc', name='txt', rate='rate'))
def sample_function(date, valcode=None):
    """
    Creating fake function for imitation raw data returning from nbu

    :param date: Any date string used to match the decorator signature
    :param valcode: Optional currency code parameter (not used in this mock)
    :return: List of dictionaries imitating the raw NBU response structure
    """
    return [
        {"txt": "Долар США", "cc": "USD", "rate": 42.2721},
        {"txt": "Євро", "cc": "EUR", "rate": 49.5154},
    ]

def test_unify_currency_decorator():
    """
    Function checks if raw data from nbu is unificated correctly by @unify_currency

    :return:
    """
    result = sample_function("20251213")
    assert len(result) == 2
    assert result[0] == {"code": "USD", "name": "Долар США", "rate": 42.2721}
    assert result[1] == {"code": "EUR", "name": "Євро", "rate": 49.5154}

@patch('api.sender._send_get_request')
def test_get_nbu_exchange_rates(mock_request):
    """
    Function checks if get_nbu_exchange_rates() works in correct way after receiving nbu exchange rates

    :param mock_request: Mocked _send_get_request function returning a predefined payload
    :return:
    """
    mock_request.return_value = [
        {"txt": "Долар США", "r030": 840, "cc": "USD", "rate": 41.2},
        {"txt": "Євро", "r030": 978, "cc": "EUR", "rate": 45.5},
    ]

    result = get_nbu_exchange_rates(date="20251213")
    assert len(result) == 2
    assert result[0]["code"] == "USD"
    assert result[1]["name"] == "Євро"

@patch('api.sender._send_get_request')
def test_get_privat_exchange_rates(mock_request):
    """
    Function checks if get_privat_exchange_rates() works in correct way after receiving privat exchange rates

    :param mock_request: Mocked _send_get_request function returning a predefined payload
    :return:
    """
    mock_request.return_value = {
        "exchangeRate": [
            {"currency": "USD", "baseCurrency": "UAH", "saleRate": 41.5, "purchaseRate": 40.9},
            {"currency": "EUR", "baseCurrency": "UAH", "saleRate": 45.8, "purchaseRate": 45.0},
        ]
    }

    result = get_privat_exchange_rates(date="20251213")
    assert len(result) >= 1


