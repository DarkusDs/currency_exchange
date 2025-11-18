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

    filtered_data = currency_output_filter(data, valcode)

    for i in filtered_data:
        currency = CurrencyRate(
            name=i['name'],
            rate=i['rate'],
            date=date,
        )
        currency_data.append(currency)
    return currency_data
