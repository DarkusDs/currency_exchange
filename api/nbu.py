from typing import Optional, List, Dict

from utils.cache_decorator import cached
from utils.logger_setup import get_logger
from utils.redis_settings import RedisConfig

logger = get_logger("SYSTEM")
from utils.adapter_currency import unify_currency
from .sender import _send_get_request
from utils.settings import REDIS_CLIENT



@unify_currency(mapper=dict(code='cc', name='txt', rate='rate'))
@cached(redis=REDIS_CLIENT, bank='nbu')
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

