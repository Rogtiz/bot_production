from functools import wraps
import json
import logging
from typing import Callable, Optional, Type
from fastapi import HTTPException
from redis import Redis
import redis.asyncio as redis
from pydantic import BaseModel

redis_client = redis.Redis(
    host="redis",  # или "redis", если внутри Docker-сети
    port=6379,
    decode_responses=True  # чтобы возвращать строки, а не байты
)


logger = logging.getLogger(__name__)

def redis_cache(
    schema: Type[BaseModel],
    key_func: Optional[Callable[..., str]] = None,
    expire: int = 3600,
    redis: Redis = redis_client,
    allow_null_cache: bool = False,
):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Генерация ключа
                if key_func:
                    key = key_func(*args, **kwargs)
                elif "key" in kwargs:
                    key = kwargs["key"]
                else:
                    raise ValueError(
                        "Cannot determine cache key. Provide `key_func` or ensure 'key' is in kwargs."
                    )

                # Проверка кэша
                cached = await redis.get(key)
                if cached:
                    logger.info(f"[CACHE HIT] key={key}")
                    data = json.loads(cached)
                    if data is None:
                        logger.info(f"[CACHE NULL] key={key} (cached None)")
                        raise HTTPException(status_code=404, detail="Not found (cached)")
                    return schema(**data)
                logger.info(f"[CACHE MISS] key={key}")
            except Exception as e:
                logger.warning(f"[CACHE ERROR] key=unknown: {e}")

            # Основная функция
            try:
                result = await func(*args, **kwargs)
                if result is not None:
                    value = schema.from_orm(result).model_dump_json()
                    await redis.set(key, value, ex=expire)
                    logger.info(f"[CACHE SET] key={key} (expires in {expire}s)")
                elif allow_null_cache:
                    await redis.set(key, json.dumps(None), ex=expire)
                    logger.info(f"[CACHE SET NULL] key={key} (expires in {expire}s)")
                return result
            except HTTPException as e:
                logger.warning(f"[RAISE HTTPException]: {e.detail}")
                raise e
            except Exception as e:
                logger.exception(f"[ERROR] while fetching and caching")
                raise e

        return wrapper
    return decorator