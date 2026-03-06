from datetime import datetime

import httpx

from utils.cache_decorator import cached
from typing import Optional, List, Dict
from utils.logger_setup import get_logger

logger = get_logger("SYSTEM")
from utils.adapter_currency import unify_currency
from .sender import _send_get_request
from utils.settings import REDIS_CLIENT

@unify_currency(mapper=dict(code='currency', name='currency', rate='saleRate'))
@cached(redis=REDIS_CLIENT, bank='privat')
def get_privat_exchange_rates(date: str, valcode: str = None) -> Optional[List[Dict]]:
    """
    Retrieves exchange rates from the PrivatBank API and returns them in a unified format, converting the input date and applying optional caching and currency filtering

    :param date: Date for which exchange rates are requested, in YYYYMMDD format
    :param valcode: Optional 3-letter currency code (e.g. "USD"); if None, all currencies are returned
    :return: A list of unified currency rate dictionaries, or None if the request fails
    """
    formated_date = datetime.strptime(date, '%Y%m%d').strftime('%d.%m.%Y')
    url = 'https://api.privatbank.ua/p24api/exchange_rates'
    params = {
        'date': formated_date,
    }
    res = _send_get_request(url=url, params=params).get("exchangeRate", [])
    logger.info(f"The exchange rate {valcode} was successfully obtained on {date}")
    return res

# from .sender import _send_get_request
# @unify_currency(mapper=dict(code='currency', name='currency', rate='saleRate'))
# async def get_privat_exchange_rates(date: str, valcode: str = None) -> Optional[List[Dict]]:
#     """
#     Retrieves exchange rates from the PrivatBank API and returns them in a unified format, converting the input date and applying currency filtering
#
#     :param date: Date for which exchange rates are requested, in YYYYMMDD format
#     :param valcode: Optional 3-letter currency code (e.g. "USD"); if None, all currencies are returned
#     :return: A list of unified currency rate dictionaries, or None if the request fails
#     """
#     formated_date = datetime.strptime(date, '%Y%m%d').strftime('%d.%m.%Y')
#     url = 'https://api.privatbank.ua/p24api/exchange_rates'
#     params = {
#         'date': formated_date,
#     }
#     response = await _send_get_request(url=url, params=params)
#     res = response.get("exchangeRate", []) if response else []
#
#     logger.info(f"The exchange rate {valcode} was successfully obtained on {date}")
#     return res
