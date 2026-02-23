from app.core.config import settings

import time


class SimpleRateLimiter:
    """Stateless simple rate limiter using Redis-like interface.

    This is intentionally minimal: increments a key and sets expiry window.
    """

    def __init__(self, redis):
        self.redis = redis

    async def allow(self, key: str) -> bool:
        if not self.redis:
            return True
        now = int(time.time())
        count = await self.redis.incr(key)
        if count == 1:
            await self.redis.expire(key, settings.RATELIMIT_WINDOW_SECONDS)
        return count <= settings.RATELIMIT_REQUESTS
