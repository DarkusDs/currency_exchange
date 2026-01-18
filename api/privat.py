from datetime import datetime
from utils.cache_decorator import cached
from typing import Optional, List, Dict
from utils.logger_setup import get_logger
from utils.redis_settings import RedisConfig

logger = get_logger("SYSTEM")
from utils.adapter_currency import unify_currency
from .sender import _send_get_request
from utils.settings import REDIS_CLIENT

@unify_currency(mapper=dict(code='currency', name='currency', rate='saleRate'))
@cached(redis=REDIS_CLIENT, bank='privat')
def get_privat_exchange_rates(date: str, valcode: str = None) -> Optional[List[Dict]]:
    formated_date = datetime.strptime(date, '%Y%m%d').strftime('%d.%m.%Y')
    url = 'https://api.privatbank.ua/p24api/exchange_rates'
    params = {
        'date': formated_date,
    }
    res = _send_get_request(url=url, params=params).get("exchangeRate", [])
    logger.info(f"Успішно отримано курс валюти {valcode} на дату {date}")
    return res
