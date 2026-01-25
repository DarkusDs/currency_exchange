from typing import Optional, List, Dict
from utils.logger_setup import get_logger

logger = get_logger("SYSTEM")

from api.nbu import get_nbu_exchange_rates
from api.privat import get_privat_exchange_rates


def get_currency_exchange_rates(bank: str, date: str, valcode: str = None) -> Optional[List[Dict]]:
    """
    Returns unified currency exchange rates by dynamically selecting the appropriate bank adapter based on the provided bank identifier

    :param bank: Bank identifier. In this version expected values are "nbu" or "privat"
    :param date: Date for which exchange rates are requested, in YYYYMMDD format
    :param valcode: Three letters currency code ("USD", "EUR" and so on). If None, all currencies are returned
    :return: A list of unified currency rate dictionaries, or None if the bank is unsupported or an error occurs
    """
    bank_option = {
        'nbu': get_nbu_exchange_rates,
        'privat': get_privat_exchange_rates,
    }
    if not bank_option.get(bank):
        logger.error(f"Unknown bank: {bank}")
        return None
    try:
        data = bank_option.get(bank)(date=date, valcode=(valcode or None))
        logger.info(f"Successfully received data from the bank: {bank}")
        return data
    except ValueError as e:
        logger.error(f"Error while executing function: get_currency_exchange_rates, {e}")
        return None
