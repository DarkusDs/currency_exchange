from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from currency_output_filter import currency_output_filter


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

    if bank == 'nbu':
        key_for_currency = 'cc'
    elif bank == 'privat':
        key_for_currency = 'currency'

    filtered_data = currency_output_filter(data, valcode, key_for_currency)

    match bank:
        case "nbu":
            for i in filtered_data:
                name = i.get('txt')
                rate = i.get('rate')

                currency = CurrencyRate(name=name, rate=rate, date=date)
                currency_data.append(currency)
        case "privat":
            for i in filtered_data:
                name = i.get('currency')
                rate = i.get('saleRate')

                currency = CurrencyRate(name=name, rate=rate, date=date)
                currency_data.append(currency)

    return currency_data
