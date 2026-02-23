from typing import AsyncGenerator
import aioredis
from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import async_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_redis():
    if not settings.REDIS_URL:
        return None
    redis = aioredis.from_url(settings.REDIS_URL)
    try:
        yield redis
    finally:
        await redis.close()
