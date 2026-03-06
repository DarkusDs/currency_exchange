from utils.redis_settings import Redis, RedisConfig

RABBITMQ_HOST = 'rabbitmq'
QUEUE_REQUEST_NAME = 'currency_requests'
QUEUE_REQUEST_ROUTING_KEY = 'requests'

QUEUE_DB_SAVE_NAME = 'currency_save_tasks'
QUEUE_DB_SAVE_ROUTING_KEY = 'db_save'

QUEUE_AUTO_REFRESH_NAME = 'currency_auto_refresh'


REDIS_CONFIG = RedisConfig()
REDIS_CLIENT = Redis(cfg=REDIS_CONFIG)






