from utils.redis_settings import Redis, RedisConfig

RABBITMQ_HOST = 'rabbitmq'
QUEUE_REQUEST_NAME = 'requests_queue'
QUEUE_REQUEST_ROUTING_KEY = 'requests'

QUEUE_DB_SAVE_NAME = 'db_save_queue'
QUEUE_DB_SAVE_ROUTING_KEY = 'db_save'



REDIS_CONFIG = RedisConfig()
REDIS_CLIENT = Redis(cfg=REDIS_CONFIG)






