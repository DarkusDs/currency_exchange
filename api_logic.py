from typing import Optional, List, Dict
from urllib.error import URLError, HTTPError
import requests, logging
from requests import URLRequired



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
        logging.info(f"Успішно отримано курс валюти {valcode} на дату {date}")
    except HTTPError as e:
        logging.error("HTTP Error")
    except ConnectionError as e:
        logging.error("ConnectionError")
    except URLRequired as e:
        logging.error("URLRequired")
    except Exception as e:
        logging.error(e)
    finally:
        return res
