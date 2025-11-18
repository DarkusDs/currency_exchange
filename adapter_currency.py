from datetime import datetime
from typing import List, Optional
from logger_setup import logger


def unify_currency(bank: str):
    def unificator(func):
        def wrapper(date: datetime, valcode: Optional[str]) -> List[dict]:
            data = func(date, valcode)
            unified = []
            for i in data:
                if bank == "nbu":
                    code = i.get("cc")
                    name = i.get("txt") or code
                    rate = i.get("rate")
                elif bank == "privat":
                    code = i.get("currency")
                    name = i.get("currency") or code
                    rate = i.get("saleRate")
                else:
                    logger.warning(f"Невідомий банк: {bank}")
                    continue

                unified.append({"code": code, "name": name, "rate": rate})
            return unified
        return wrapper
    return unificator
