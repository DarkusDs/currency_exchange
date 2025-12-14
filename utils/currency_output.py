from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict

from utils.logger_setup import logger


@dataclass
class CurrencyRate:
    name: str
    rate: float
    date: datetime

    def __str__(self) -> str:
        return f'Назва: {self.name}\nКурс: {self.rate}\nДата {self.date.strftime('%Y-%m-%d')}'


def format_currency_data(data: Optional[List[dict]], date: datetime, bank: str, valcode: Optional[str]) -> List[CurrencyRate]:
    """
    Format currency data into a list of currency rates

    :param data:
    :param date:
    :return:
    """
    currency_data = []

    if data is None or len(data) == 0:
        return []

    filtered_data = currency_output_filter(data, valcode)

    for i in filtered_data:
        currency = CurrencyRate(
            name=i['name'],
            rate=i['rate'],
            date=date,
        )
        currency_data.append(currency)
    return currency_data


def currency_output_filter(data: List[dict], valcode: Optional[str]) -> List[Dict]:
    """
    the function returns a list of dictionaries that satisfy the filtering condition by key, i.e. by currency name

    :param data:
    :param valcode:
    :param key_for_currency:
    :return:
    """
    if not valcode:
        return data
    else:
        filtered_data = []
        for row in data:
            if row.get("code", "") == valcode:
                filtered_data.append(row)
        logger.info(f"Виконано фільтурвання отриманого результату від API, для валюти: {valcode}")
        return filtered_data
