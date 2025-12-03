from typing import Optional, List, Dict
from urllib.error import HTTPError
import requests
from requests import URLRequired
from logger_setup import logger
from adapter_currency import unify_currency
from .sender import _send_get_request


@unify_currency(mapper=dict(code='cc', name='txt', rate='rate'))
def get_nbu_exchange_rates(date: str, valcode: str = None) -> Optional[List[Dict]]:

    url = 'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange'
    params = {
                 'date': date,
                 'type': 'json'
             }
    if valcode:
             params['valcode'] = valcode

    res = _send_get_request(url=url, params=params)
    logger.info(f"Успішно отримано курс валюти {valcode} на дату {date}")

    return res


# @unify_currency(mapper=dict(code='cc', name='txt', rate='rate'))
# def get_nbu_exchange_rates(date: str, valcode: str = None) -> Optional[List[Dict]]:
#     res = None
#     try:
#         url = 'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange'
#         params = {
#                      'date': date,
#                      'type': 'json'
#                  }
#         if valcode:
#                  params['valcode'] = valcode
#         res = requests.get(url, params=params)
#         res = res.json()
#         logger.info(f"Успішно отримано курс валюти {valcode} на дату {date}")
#     except HTTPError as e:
#         logger.error("HTTP Error")
#     except ConnectionError as e:
#         logger.error("ConnectionError")
#     except URLRequired as e:
#         logger.error("URLRequired")
#     except Exception as e:
#         logger.error(e)
#     finally:
#         return res
