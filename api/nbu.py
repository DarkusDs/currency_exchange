from typing import Optional, List, Dict

from utils.cache_decorator import cached
from utils.logger_setup import get_logger

logger = get_logger("SYSTEM")
from utils.adapter_currency import unify_currency
# from .sender import _send_get_request
from utils.settings import REDIS_CLIENT



# @unify_currency(mapper=dict(code='cc', name='txt', rate='rate'))
# @cached(redis=REDIS_CLIENT, bank='nbu')
# def get_nbu_exchange_rates(date: str, valcode: str = None) -> Optional[List[Dict]]:
#     """
#     Retrieves exchange rates from the National Bank of Ukraine API and returns them in a unified format, with optional caching and currency filtering
#
#     :param date: Date for which exchange rates are requested, in YYYYMMDD format
#     :param valcode: Optional 3-letter currency code (e.g. "USD"); if None, all currencies are returned
#     :return: A list of unified currency rate dictionaries, or None if the request fails
#     """
#     url = 'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange'
#     params = {
#                  'date': date,
#                  'type': 'json'
#              }
#     if valcode:
#              params['valcode'] = valcode
#
#     res = _send_get_request(url=url, params=params)
#     logger.info(f"The exchange rate {valcode} was successfully obtained on {date}")
#
#     return res


from .sender import _send_get_request
@unify_currency(mapper=dict(code='cc', name='txt', rate='rate'))
async def get_nbu_exchange_rates(date: str, valcode: str = None) -> Optional[List[Dict]]:
    """
    Retrieves exchange rates from the National Bank of Ukraine API and returns them in a unified format

    :param date: Date for which exchange rates are requested, in YYYYMMDD format
    :param valcode: Optional 3-letter currency code (e.g. "USD"); if None, all currencies are returned
    :return: A list of unified currency rate dictionaries, or None if the request fails
    """
    url = 'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange'
    params = {
        'date': date,
        'type': 'json'
    }
    if valcode:
        params['valcode'] = valcode

    response = await _send_get_request(url=url, params=params)
    res = response if response else []
    logger.info(f"The exchange rate {valcode} was successfully obtained on {date}")
    return res
