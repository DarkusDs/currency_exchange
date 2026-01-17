import os
from json import dumps

import redis
import json
from typing import Dict, Any, Optional

from utils.logger_setup import get_logger

logger = get_logger("REDIS")

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=os.getenv("REDIS_PORT", 6379),
    db=int(os.getenv("REDIS_DATABASES", 0)),
    decode_responses=True
)

def save_to_cache(key: str, value, ttl: int = 60):
    """
    Function saves value to cache

    :param key:
    :param value:
    :param ttl: time to live cached data in seconds
    :return:
    """
    try:
        redis_client.setex(key, ttl, json.dumps(value))
        logger.info("Дані збережено до кешу")
    except Exception as e:
        logger.error(f"Не вдалося зберегти дані до кешу: {e}")

def get_from_cache(key: str):
    """
    Function gets value from cache

    :param key:
    :return:
    """
    try:
        result = redis_client.get(key)
        logger.info("Дані отримано з кешу")
        return result
    except Exception as e:
        logger.error(f"Не вдалося отримати дані з кешу: {e}")

def delete_from_cache(key: str):
    """
    Function deletes value from cache

    :param key:
    :return:
    """
    try:
        redis_client.delete(key)
    except Exception as e:
        logger.error(f"Не вдалося видалити дані з кешу: {e}")


