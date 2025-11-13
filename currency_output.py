from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class CurrencyRate:
    name: str
    rate: float
    date: datetime

    def __str__(self) -> str:
        return f'Назва: {self.name}\nКурс: {self.rate}\nДата {self.date.strftime('%Y-%m-%d')}'


def format_currency_data(data: Optional[List[dict]], date: datetime) -> List[CurrencyRate]:
    """
    Format currency data into a list of currency rates

    :param data:
    :param date:
    :return:
    """
    currency_data = []
    if data:
        for i in data:
            name = i.get('txt')
            rate = i.get('rate')

            currency = CurrencyRate(name=name, rate=rate, date=date)
            currency_data.append(currency)
    return currency_data
