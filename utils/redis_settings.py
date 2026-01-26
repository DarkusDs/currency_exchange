import dataclasses
import redis
import json

from utils.logger_setup import get_logger

logger = get_logger("REDIS")

@dataclasses.dataclass
class RedisConfig:
    """
    Configuration container for Redis connection parameters
    """
    host: str = "redis"
    port: int = 6379
    db: int = 0
    decode_responses: bool = True


class Redis:
    """
    Redis client wrapper that lazily initializes a single connection and provides basic cache operations.
    """
    _client = None
    def __init__(self, cfg: RedisConfig):
        """
        Initializes the Redis wrapper with the provided configuration

        :param cfg: RedisConfig instance with connection settings
        """
        self.cfg = cfg

    @property
    def client(self):
        """
        Returns a singleton Redis client instance, creating it on first access

        :return: Initialized redis.Redis client
        """
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
        Stores a JSON-serialized value in Redis with a specified time-to-live

        :param key: Cache key under which the value will be stored
        :param value: Python object to be serialized and cached
        :param ttl: Cache lifetime in seconds
        :return:
        """
        try:
            self.client.setex(key, ttl, json.dumps(value))
            logger.info("Data saved to cache")
        except Exception as e:
            logger.error(f"Failed to save data to cache: {e}")

    def get_value(self, key: str):
        """
        Retrieves a cached value from Redis by key

        :param key: Cache key to retrieve
        :return: Cached value as a string, or None if not found or on error
        """
        try:
            result = self.client.get(key)
            logger.info(f"result={str(result)}")
            logger.info("Data obtained from cache")
            return result
        except Exception as e:
            logger.error(f"Unable to retrieve data from cache: {e}")
            return None

