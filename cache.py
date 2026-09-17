import json

from redis import Redis
from redis.exceptions import RedisError

from app.core.config import get_settings


redis_client = Redis.from_url(get_settings().redis_url, decode_responses=True)


def cache_get(key: str) -> dict | None:
    try:
        value = redis_client.get(key)
        return json.loads(value) if value else None
    except (RedisError, json.JSONDecodeError):
        return None


def cache_set(key: str, value: dict, ttl_seconds: int = 60) -> None:
    try:
        redis_client.setex(key, ttl_seconds, json.dumps(value))
    except (RedisError, TypeError):
        return


def cache_delete(pattern: str) -> None:
    try:
        for key in redis_client.scan_iter(pattern):
            redis_client.delete(key)
    except RedisError:
        return
