from datetime import datetime
from typing import Optional, List, Dict
from urllib.error import HTTPError
import requests
from requests import URLRequired
from logger_setup import logger
from adapter_currency import unify_currency


@unify_currency('privat')
def get_privat_exchange_rates(date: str, valcode: str = None) -> Optional[List[Dict]]:
    res = []
    try:
        formated_date = datetime.strptime(date, '%Y%m%d').strftime('%d.%m.%Y')
        url = 'https://api.privatbank.ua/p24api/exchange_rates'
        params = {
            'date': formated_date,
        }
        res = requests.get(url, params=params)
        res = res.json().get("exchangeRate", [])
        logger.info(f"Успішно отримано курс валюти {valcode} на дату {date}")
    except HTTPError as e:
        logger.error("HTTP Error")
    except ConnectionError as e:
        logger.error("ConnectionError")
    except URLRequired as e:
        logger.error("URLRequired")
    except Exception as e:
        logger.error(e)
    finally:
        return res
