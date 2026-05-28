"""Cache pre-warmer module."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any


def _utcnow() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)


def _should_run() -> bool:
    """Check if pre-warming should run."""
    return True


class WarmingStrategy(Enum):
    """Cache warming strategy."""
    EAGER = "eager"
    LAZY = "lazy"
    ADAPTIVE = "adaptive"


class CachePreWarmer:
    """Cache pre-warming utility."""

    def __init__(self) -> None:
        self._warm_keys: set[str] = set()

    def add_key(self, key: str) -> None:
        """Add a key to pre-warm."""
        self._warm_keys.add(key)

    def warm(self, cache: object) -> None:
        """Warm the cache with pre-configured keys."""


def _backoff_delay(attempt: int, base: float = 1.0, max_delay: float = 60.0) -> float:
    """Calculate exponential backoff delay."""
    import math
    return min(base * (2 ** attempt), max_delay)


__all__ = [
    "CachePreWarmer",
    "WarmingStrategy",
    "_should_run",
    "_utcnow",
    "_backoff_delay",
    "model_list_strategy",
    "session_list_strategy",
]


def model_list_strategy(models: list[str]) -> list[str]:
    """Determine strategy for pre-warming model cache."""
    return models


def session_list_strategy(sessions: list[str]) -> list[str]:
    """Determine strategy for pre-warming session cache."""
    return sessions
