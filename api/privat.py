from datetime import datetime
from typing import Optional, List, Dict
from urllib.error import HTTPError
import requests
from requests import URLRequired
from logger_setup import logger
from adapter_currency import unify_currency
from .sender import _send_get_request


@unify_currency('privat')
def get_privat_exchange_rates(date: str, valcode: str = None) -> Optional[List[Dict]]:
    formated_date = datetime.strptime(date, '%Y%m%d').strftime('%d.%m.%Y')
    url = 'https://api.privatbank.ua/p24api/exchange_rates'
    params = {
        'date': formated_date,
    }
    res = _send_get_request(url=url, params=params).get("exchangeRate", [])
    logger.info(f"Успішно отримано курс валюти {valcode} на дату {date}")
    return res
