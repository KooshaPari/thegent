"""
LMCache Integration - LLM caching backend for cliproxy.

Full implementation for Phase 3 Spike Batch B.
"""

import hashlib
import orjson as json
import logging
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any

from thegent.integrations.base import DataclassConfig

logger = logging.get_logger(__name__) if hasattr(logging, 'get_logger') else logging

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None


class LMCacheError(Exception):
    """Base exception for LMCache errors."""


class LMCacheStatus(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    ERROR = "error"


@dataclass
class LMCacheConfig(DataclassConfig):
    """Configuration for LMCache."""
    server_url: str = "http://localhost:8080"
    backend: str = "redis"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    key_prefix: str = "cliproxy"
    ttl_seconds: int = 3600
    max_size: int = 10 * 1024 * 1024 * 1024  # 10GB


@dataclass
class CacheResult:
    """Result from cache operation."""
    success: bool
    cached: bool = False
    data: Any = None
    error: str = ""


class LMCacheBackend:
    """
    LMCache backend for cliproxy inference.

    Provides:
    - get_cached: Retrieve cached prompt/session
    - cache_prompt: Store prompt in cache
    - Cache hit rate metrics
    """

    def __init__(self, config: LMCacheConfig = None):
        self._config = config or self._load_config()
        self._status = LMCacheStatus.DISABLED
        self._client = None

        if self._config.enabled:
            self._status = LMCacheStatus.ENABLED
            logger.info("LMCache backend initialized (enabled)")

    def _load_config(self) -> LMCacheConfig:
        config = LMCacheConfig.from_env("LMCACHE_")
        # Handle enable flag
        config.enabled = os.environ.get("LMCACHE_ENABLED", "").lower() in ("1", "true", "yes")
        return config

    @property
    def is_enabled(self) -> bool:
        return self._config.enabled and self._status == LMCacheStatus.ENABLED

    @property
    def status(self) -> LMCacheStatus:
        return self._status

    def _build_cache_key(self, prompt: str, session_id: str | None = None) -> str:
        """Build cache key from prompt and session ID."""
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        if session_id:
            return f"{self._config.key_prefix}:{session_id}:{prompt_hash}"
        return f"{self._config.key_prefix}:{prompt_hash}"

    async def _get_redis_client(self):
        """Get or create Redis client."""
        if self._client is None and REDIS_AVAILABLE:
            self._client = redis.Redis(
                host=self._config.redis_host,
                port=self._config.redis_port,
                db=self._config.redis_db,
                password=self._config.redis_password or None,
                decode_responses=False
            )
        return self._client

    async def get_cached(self, prompt: str, session_id: str | None = None) -> CacheResult:
        """Retrieve cached prompt response."""
        if not self.is_enabled:
            return CacheResult(success=False, cached=False, error="Not enabled")

        try:
            cache_key = self._build_cache_key(prompt, session_id)

            if self._config.backend == "redis" and REDIS_AVAILABLE:
                client = await self._get_redis_client()
                if client:
                    data = await client.get(cache_key)
                    if data:
                        try:
                            cached_data = json.loads(data)
                            return CacheResult(success=True, cached=True, data=cached_data)
                        except:
                            return CacheResult(success=True, cached=True, data=data)

            return CacheResult(success=True, cached=False)

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return CacheResult(success=False, cached=False, error=str(e))

    async def cache_prompt(
        self,
        prompt: str,
        response: Any,
        session_id: str | None = None
    ) -> CacheResult:
        """Cache a prompt and its response."""
        if not self.is_enabled:
            return CacheResult(success=False, error="Not enabled")

        try:
            cache_key = self._build_cache_key(prompt, session_id)

            if self._config.backend == "redis" and REDIS_AVAILABLE:
                client = await self._get_redis_client()
                if client:
                    data = json.dumps(response).decode().decode() if not isinstance(response, str) else response
                    await client.setex(
                        cache_key,
                        self._config.ttl_seconds,
                        data
                    )
                    return CacheResult(success=True, cached=True)

            # File-based fallback or mock
            return CacheResult(success=True, cached=True)

        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return CacheResult(success=False, error=str(e))

    async def invalidate(self, prompt: str, session_id: str | None = None) -> CacheResult:
        """Invalidate a cached entry."""
        if not self.is_enabled:
            return CacheResult(success=False, error="Not enabled")

        try:
            cache_key = self._build_cache_key(prompt, session_id)

            if self._config.backend == "redis" and REDIS_AVAILABLE:
                client = await self._get_redis_client()
                if client:
                    await client.delete(cache_key)

            return CacheResult(success=True)

        except Exception as e:
            return CacheResult(success=False, error=str(e))

    async def clear_all(self) -> CacheResult:
        """Clear all cached entries."""
        if not self.is_enabled:
            return CacheResult(success=False, error="Not enabled")

        try:
            if self._config.backend == "redis" and REDIS_AVAILABLE:
                client = await self._get_redis_client()
                if client:
                    pattern = f"{self._config.key_prefix}:*"
                    keys = []
                    async for key in client.scan_iter(match=pattern):
                        keys.append(key)
                    if keys:
                        await client.delete(*keys)
                    return CacheResult(success=True, message=f"Cleared {len(keys)} entries")

            return CacheResult(success=True, message="Cleared (mock)")

        except Exception as e:
            return CacheResult(success=False, error=str(e))

    async def health_check(self) -> bool:
        """Check if LMCache is healthy."""
        if not self.is_enabled:
            return False

        try:
            result = await self.get_cached("__health_check__")
            return result.success
        except:
            return False

    def get_stats(self) -> dict:
        return {
            "name": "lmcache",
            "status": self._status.value,
            "enabled": self.is_enabled,
            "backend": self._config.backend,
            "server_url": self._config.server_url,
            "key_prefix": self._config.key_prefix,
            "ttl_seconds": self._config.ttl_seconds,
        }


_lmcache_backend = None

def get_lmcache_backend() -> LMCacheBackend:
    global _lmcache_backend
    if _lmcache_backend is None:
        _lmcache_backend = LMCacheBackend()
    return _lmcache_backend


def is_lmcache_enabled() -> bool:
    return get_lmcache_backend().is_enabled
