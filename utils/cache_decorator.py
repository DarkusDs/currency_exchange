from typing import Optional, List

from utils.redis_settings import Redis
from datetime import datetime
import json


def cached(redis: Redis, bank: str):
    """
    Decorator factory that caches the result of a function call in Redis using the bank name as the cache key

    :param redis: Redis client instance used to store and retrieve cached values
    :param bank: Cache key identifier (usually the bank name)
    :return: Decorator that wraps a function and returns cached data if available
    """
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
