from typing import Optional, List, Dict
from utils.logger_setup import get_logger

logger = get_logger("SYSTEM")
from utils.adapter_currency import unify_currency
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

