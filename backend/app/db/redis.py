import redis

from app.core.config import getAppConfig

config = getAppConfig()


redis_client = redis.Redis.from_url(
    config.REDIS_URL,
    decode_responses=True
)


def check_redis():
    return redis_client.ping()
