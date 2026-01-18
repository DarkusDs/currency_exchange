from typing import Optional, List

from utils.redis_settings import Redis
from datetime import datetime
import json


def cached(redis: Redis, bank: str):
    bank = str(bank)
    def unificator(func):
        def wrapper(date: datetime, valcode: Optional[str]) -> List[dict]:

            r = redis.get_value(bank)
            data = None if r is None else json.loads(redis.get_value(bank))

            if data is None:
                data = func(date, valcode)
                if data is not None:
                    redis.set_value(bank, data)

            return data
        return wrapper
    return unificator
