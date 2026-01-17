from typing import Optional, List, Dict
from utils.logger_setup import get_logger
from utils.redis_settings import RedisConfig

logger = get_logger("SYSTEM")
from utils.adapter_currency import unify_currency
from .sender import _send_get_request
from utils.redis_settings import Redis
from datetime import datetime
from utils.settings import REDIS_CLIENT
import json


def cached(redis: Redis):
    def unificator(func):
        def wrapper(date: datetime, valcode: Optional[str]) -> List[dict]:

            r = redis.get_value("nbu")
            data = None if r is None else json.loads(redis.get_value("nbu"))

            if data is None:
                data = func(date, valcode)
                if data is not None:
                    redis.set_value("nbu", data)

            return data
        return wrapper
    return unificator



@unify_currency(mapper=dict(code='cc', name='txt', rate='rate'))
@cached(redis=REDIS_CLIENT)
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

