"""Redis caching service."""

import json
from typing import Any, Optional
import redis.asyncio as redis

from api.config import settings


class CacheService:
    """Redis cache service for data caching."""

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Connect to Redis."""
        self._client = redis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._client:
            await self._client.close()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self._client:
            return None
        try:
            value = await self._client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: int = 3600,
    ) -> bool:
        """Set value in cache with optional expiration (seconds)."""
        if not self._client:
            return False
        try:
            await self._client.set(
                key,
                json.dumps(value, default=str),
                ex=expire,
            )
            return True
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self._client:
            return False
        try:
            await self._client.delete(key)
            return True
        except Exception:
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        if not self._client:
            return 0
        try:
            keys = []
            async for key in self._client.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                return await self._client.delete(*keys)
            return 0
        except Exception:
            return 0

    async def get_or_set(
        self,
        key: str,
        factory,
        expire: int = 3600,
    ) -> Any:
        """Get from cache or compute and cache value."""
        value = await self.get(key)
        if value is not None:
            return value

        # Compute value
        if callable(factory):
            value = await factory() if hasattr(factory, "__await__") else factory()
        else:
            value = factory

        await self.set(key, value, expire)
        return value

    # Session caching helpers
    async def cache_user_session(self, user_id: str, session_data: dict, expire: int = 86400) -> bool:
        """Cache user session data (24h default)."""
        return await self.set(f"session:{user_id}", session_data, expire)

    async def get_user_session(self, user_id: str) -> Optional[dict]:
        """Get cached user session."""
        return await self.get(f"session:{user_id}")

    async def invalidate_user_session(self, user_id: str) -> bool:
        """Invalidate user session cache."""
        return await self.delete(f"session:{user_id}")

    # Rate limiting helpers
    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
    ) -> tuple[bool, int]:
        """Check rate limit. Returns (allowed, remaining)."""
        if not self._client:
            return True, max_requests

        try:
            current = await self._client.get(key)
            if current is None:
                await self._client.set(key, 1, ex=window_seconds)
                return True, max_requests - 1

            count = int(current)
            if count >= max_requests:
                return False, 0

            await self._client.incr(key)
            return True, max_requests - count - 1
        except Exception:
            return True, max_requests


# Global cache instance
_cache: Optional[CacheService] = None


async def get_cache() -> CacheService:
    """Get cache service instance."""
    global _cache
    if _cache is None:
        _cache = CacheService(settings.REDIS_URL)
        await _cache.connect()
    return _cache


async def close_cache() -> None:
    """Close cache connection."""
    global _cache
    if _cache:
        await _cache.disconnect()
        _cache = None
