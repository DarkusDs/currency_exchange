import dataclasses
import redis
import json

from utils.logger_setup import get_logger

logger = get_logger("REDIS")

@dataclasses.dataclass
class RedisConfig:
    host: str = "redis"
    port: int = 6379
    db: int = 0
    decode_responses: bool = True


class Redis:
    _client = None
    def __init__(self, cfg: RedisConfig):
        self.cfg = cfg

    @property
    def client(self):
        host = self.cfg.host
        port = self.cfg.port
        db = self.cfg.db

        if self._client is None:
            self._client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True
            )

        return self._client


    def set_value(self, key: str, value, ttl: int = 60):
        """
        Function saves value to cache

        :param key:
        :param value:
        :param ttl: time to live cached data in seconds
        :return:
        """
        try:
            self.client.setex(key, ttl, json.dumps(value))
            logger.info("Дані збережено до кешу")
        except Exception as e:
            logger.error(f"Не вдалося зберегти дані до кешу: {e}")

    def get_value(self, key: str):
        """
        Function gets value from cache

        :param key:
        :return:
        """
        try:
            result = self.client.get(key)
            logger.info(f"result={str(result)}")
            logger.info("Дані отримано з кешу")
            return result
        except Exception as e:
            logger.error(f"Не вдалося отримати дані з кешу: {e}")
            return None

