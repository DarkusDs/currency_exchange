from typing import Optional, List, Dict
from utils.logger_setup import logger

from api.nbu import get_nbu_exchange_rates
from api.privat import get_privat_exchange_rates


def get_currency_exchange_rates(bank: str, date: str, valcode: str = None) -> Optional[List[Dict]]:
    bank_option = {
        'nbu': get_nbu_exchange_rates,
        'privat': get_privat_exchange_rates,
    }
    if not bank_option.get(bank):
        logger.error(f"Невідомий банк: {bank}")
        return None
    try:
        data = bank_option.get(bank)(date=date, valcode=(valcode or None))
        logger.info(f"Успішно отримано дані від банку: {bank}")
        return data
    except ValueError as e:
        logger.error(f"Помилка при виконанні функції get_currency_exchange_rates, {e}")
        return None
