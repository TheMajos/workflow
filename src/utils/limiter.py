import redis.asyncio as redis
from config import REDIS_DB_ZERO, REDIS_DB_ONE


class CacheManager:
    _instance = None
    _cache = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if CacheManager._cache is None:
            CacheManager._cache = REDIS_DB_ZERO

        self.client = CacheManager._cache

    async def incr(self, email, method: str, increment_value: int = 1, ttl: int = 30):
        key = f"{method}:{email}"
        v = await self.client.incrby(key, increment_value)

        # Ensures doesn't reset TTL.
        if v == increment_value:
            await self.client.expire(key, ttl)
        return v

    async def grab_value(self, email, method: str):
        key = f"{method}:{email}"
        value = await self.client.get(key)
        if value:
            return int(value)
        return 0


class Blocker:
    _blocked = None
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if Blocker._blocked is None:
            Blocker._blocked = REDIS_DB_ONE

        self.blocked = Blocker._blocked

    async def block(self, method: str, email: str, ttl: int = 300):
        await self.blocked.setex(f"{method}:{email}", ttl, "blocked")

    async def is_blocked(self, method: str, email: str):
        return await self.blocked.exists(f"{method}:{email}")


class Ratelimit:
    def __init__(self, cache: CacheManager, blocker: Blocker, limit: int):
        self.cache_manager = cache
        self.blocker = blocker
        self.limit = limit

    async def ratelimit(self, method, email):

        if await self.blocker.is_blocked(method, email):
            return True

        await self.cache_manager.incr(email, method)
        current_value = await self.cache_manager.grab_value(email, method)

        if current_value >= self.limit:
            await self.blocker.block(method, email)
            return True
        return False


async def is_rate_limited(method: str, email: str):
    cache_manager = CacheManager()
    blocker = Blocker()
    limiter = Ratelimit(cache=cache_manager, blocker=blocker, limit=5)

    return await limiter.ratelimit(method, email)
