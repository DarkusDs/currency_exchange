from datetime import datetime
from typing import List, Optional


def unify_currency(mapper: dict):
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
