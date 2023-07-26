from redis import asyncio as aioredis
from redis.asyncio import Redis
from datetime import timedelta

from typing import Any

from .. config import settings


async def get_redis_client() -> Redis:
    """Create connection with redis make request there
    for Depend in endpoint"""
    redis = await aioredis.from_url(
        url=settings.REDIS_URL,
        encoding="utf8",
        decode_responses=True,
    )   
    return redis

async def add_value(
    redis_client: Redis,
    key: str,
    value: str,
    minuts_expire: int = 30) -> None:
    """Set new values in redis
    default key seting in redis by 30 minuts"""
    await redis_client.set(key, value, ex=timedelta(minutes=minuts_expire))
    
    
async def get_and_del_by_key(redis_client: Redis, key: str) -> Any:
    """Get value by key and delete it after this command"""
    return await redis_client.getdel(key)

async def get_by_key(redis_client: Redis, key: str) -> Any:
    """Get value from redis by key"""
    return await redis_client.get(key)

async def delete_by_key(redis_client: Redis, key: str) -> Any:
    """Delete value in redis by key"""
    return await redis_client.delete(key)