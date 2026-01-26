from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict

from utils.logger_setup import get_logger

logger = get_logger("SYSTEM")


@dataclass
class CurrencyRate:
    """
    Data container representing a single currency rate with its name, value, and date
    """
    name: str
    rate: float
    date: datetime

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the currency rate

        :return: Formatted string with currency name, rate, and date
        """
        return f'Назва: {self.name}\nКурс: {self.rate}\nДата {self.date.strftime('%Y-%m-%d')}'


def format_currency_data(data: Optional[List[dict]], date: datetime, bank: str, valcode: Optional[str]) -> List[CurrencyRate]:
    """
    Converts unified raw currency data into a list of CurrencyRate objects, applying optional currency code filtering

    :param data: Unified currency data received from a bank adapter
    :param date: Date associated with the exchange rates
    :param bank: Source bank identifier
    :param valcode: Optional currency code to filter results
    :return: List of formatted CurrencyRate objects
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

    :param data: List of unified currency dictionaries
    :param valcode: Optional currency code used for filtering
    :return: Filtered list of currency dictionaries
    """
    if not valcode:
        return data
    else:
        filtered_data = []
        for row in data:
            if row.get("code", "") == valcode:
                filtered_data.append(row)
        logger.info(f"Filtering of the result received from the API has been performed for the currency: {valcode}")
        return filtered_data
