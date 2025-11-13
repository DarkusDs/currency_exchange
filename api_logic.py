from typing import Optional, List, Dict
from urllib.error import URLError, HTTPError
import requests, logging
from requests import URLRequired

from logger_setup import logger


def get_currency_exchange_rates(date: str, valcode: str = None, type: str = "json") -> Optional[List[Dict]]:
    """
    Send request for api and parse result

    :param date:
    :param valcode:
    :param type:
    :return:
    """
    res = None

    try:
        url = 'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange'
        params = {
            'date': date,
            'type': type
        }
        if valcode:
            params['valcode'] = valcode

        res = requests.get(url, params=params)
        res = res.json()
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
