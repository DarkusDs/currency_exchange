from datetime import datetime
from typing import List, Optional


def unify_currency(mapper: dict):
    """
    Decorator factory that converts raw provider-specific currency data into a unified structure using a configurable field mapping

    :param mapper: Dictionary that maps unified field names to provider-specific keys (e.g. {"code": "cc", "name": "txt", "rate": "rate"})
    :return: Decorator that wraps a function and returns a list of unified currency dictionaries
    """
    def unificator(func):
        def wrapper(date: datetime, valcode: Optional[str]) -> List[dict]:
            data = func(date, valcode)
            unified = []

            for i in data:
                r = dict()
                for k, v in mapper.items():
                    r[k] = i.get(v)
                unified.append(r)

            return unified
        return wrapper
    return unificator
