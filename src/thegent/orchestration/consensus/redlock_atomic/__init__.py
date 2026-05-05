"""Stub module."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RedlockAcquireResult:
    """Result of acquiring a redlock."""
    acquired: bool
    lock_key: str = ""
    ttl_ms: int = 0


class RedlockAtomic:
    """Atomic operations using Redis redlock."""

    def __init__(self) -> None:
        self.locks: dict[str, bool] = {}

    def acquire(self, key: str, ttl_ms: int = 30000) -> RedlockAcquireResult:
        """Acquire a lock."""
        self.locks[key] = True
        return RedlockAcquireResult(acquired=True, lock_key=key, ttl_ms=ttl_ms)

    def release(self, key: str) -> bool:
        """Release a lock."""
        if key in self.locks:
            del self.locks[key]
            return True
        return False


__all__ = ["RedlockAcquireResult", "RedlockAtomic", "RedlockController"]


class RedlockController:
    """Controller for Redlock distributed locking."""

    def __init__(self) -> None:
        self._locks: dict[str, str] = {}

    def lock(self, resource: str, owner: str, ttl_ms: int = 30000) -> bool:
        """Acquire a lock on a resource."""
        if resource not in self._locks:
            self._locks[resource] = owner
            return True
        return False

    def unlock(self, resource: str, owner: str) -> bool:
        """Release a lock on a resource."""
        if self._locks.get(resource) == owner:
            del self._locks[resource]
            return True
        return False


class _InMemoryLockState:
    """In-memory lock state for testing Redlock operations."""

    def __init__(self) -> None:
        self._locks: dict[str, dict] = {}

    def acquire(self, resource: str, owner: str, ttl_ms: int) -> bool:
        """Acquire a lock in memory."""
        if resource in self._locks:
            return False
        self._locks[resource] = {"owner": owner, "ttl_ms": ttl_ms}
        return True

    def release(self, resource: str, owner: str) -> bool:
        """Release a lock in memory."""
        if self._locks.get(resource, {}).get("owner") == owner:
            del self._locks[resource]
            return True
        return False

    def is_locked(self, resource: str) -> bool:
        """Check if a resource is locked."""
        return resource in self._locks


__all__ = ["RedlockAcquireResult", "RedlockAtomic", "RedlockController", "_InMemoryLockState", "_parse_node_urls_from_env", "_parse_redis_url", "make_redlock_controller"]


def make_redlock_controller(config: dict[str, Any] | None = None) -> RedlockController:
    """Create a redlock controller with the given config.

    Args:
        config: Optional configuration dictionary.

    Returns:
        RedlockController instance.
    """
    return RedlockController()


def _parse_redis_url(url: str) -> dict[str, Any]:
    """Parse a Redis URL into components.

    Args:
        url: Redis URL string.

    Returns:
        Dictionary with parsed components.
    """
    result = {"host": "localhost", "port": 6379, "db": 0, "password": None}
    if url.startswith("redis://"):
        url = url[8:]
        if "@" in url:
            auth, url = url.split("@", 1)
            if ":" in auth:
                result["password"] = auth.split(":")[1]
        if "/" in url:
            host_port, db = url.rsplit("/", 1)
            try:
                result["db"] = int(db)
            except ValueError:
                pass
            url = host_port
        if ":" in url:
            result["host"], port = url.split(":", 1)
            try:
                result["port"] = int(port)
            except ValueError:
                pass
        else:
            result["host"] = url
    return result


def _parse_node_urls_from_env() -> list[str]:
    """Parse Redis node URLs from environment variables.

    Returns:
        List of node URL strings.
    """
    import os
    env_val = os.environ.get("REDIS_NODE_URLS", "")
    if not env_val:
        return ["redis://localhost:6379"]
    return [url.strip() for url in env_val.split(",") if url.strip()]
