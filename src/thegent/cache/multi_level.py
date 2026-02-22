"""Multi-level cache: L1 (in-process TTLCache) -> L2 (diskcache on disk).

Architecture:
  - L1: cachetools.TTLCache -- fastest, in-process, bounded by maxsize + TTL
  - L2: diskcache.Cache -- persistent, SQLite-backed, optional (graceful L1-only fallback)

Read path:  L1 hit -> return immediately
            L1 miss -> L2 hit -> promote to L1 -> return
            L2 miss -> return None (caller computes and calls set())

Write path: write-through to L1 and L2 simultaneously

Thread safety: cachetools.TTLCache is *not* thread-safe by default; we use threading.Lock
              for all L1 mutations. diskcache.Cache is process-safe and thread-safe natively.

Library-first compliance (LIBRARY_FIRST_POLICY.md):
  - L1: cachetools.TTLCache -- no custom TTL logic
  - L2: diskcache.Cache -- no custom disk serialisation/TTL logic
"""

from __future__ import annotations

import contextlib
import functools
import logging
import threading
from pathlib import Path
from typing import Any

from cachetools import TTLCache

try:
    import diskcache

    _DISKCACHE_AVAILABLE = True
except ImportError:
    _DISKCACHE_AVAILABLE = False

_LOG = logging.getLogger(__name__)


class MultiLevelCache:
    """Two-level cache: L1 in-memory TTLCache -> L2 diskcache on disk.

    Args:
        l1_maxsize: Maximum number of entries in L1 (in-process) cache.
        l1_ttl: Time-to-live in seconds for L1 entries (default: 60).
        l2_dir: Directory path for L2 disk cache. If None, L2 is disabled.
        l2_ttl: Time-to-live in seconds for L2 entries (default: 3600).
    """

    def __init__(
        self,
        l1_maxsize: int = 1000,
        l1_ttl: float = 60,
        l2_dir: str | Path | None = None,
        l2_ttl: float = 3600,
    ) -> None:
        self._l1: TTLCache = TTLCache(maxsize=l1_maxsize, ttl=l1_ttl)
        self._l1_lock = threading.Lock()
        self._l2_ttl = l2_ttl
        self._l2_init_status: dict[str, Any] = {
            "enabled": False,
            "reason": "disabled",
        }

        # L2: diskcache is optional; silently degrade to L1-only if unavailable or disabled
        self._l2: diskcache.Cache | None = None
        if l2_dir is None:
            self._l2_init_status = {"enabled": False, "reason": "not_configured"}
        elif not _DISKCACHE_AVAILABLE:
            self._l2_init_status = {"enabled": False, "reason": "diskcache_unavailable"}
        else:
            l2_path = Path(l2_dir)
            try:
                l2_path.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as exc:
                self._l2 = None
                self._l2_init_status = {
                    "enabled": False,
                    "reason": "directory_error",
                    "error_type": type(exc).__name__,
                    "detail": str(exc)[:200],
                }
                _LOG.warning("multilevel_cache_l2_disabled %s", self._l2_init_status)
            else:
                try:
                    self._l2 = diskcache.Cache(str(l2_path))
                    self._l2_init_status = {
                        "enabled": True,
                        "reason": "ok",
                        "path": str(l2_path),
                    }
                except (PermissionError, OSError, ValueError, RuntimeError) as exc:
                    self._l2 = None
                    self._l2_init_status = {
                        "enabled": False,
                        "reason": "open_failed",
                        "error_type": type(exc).__name__,
                        "detail": str(exc)[:200],
                    }
                    _LOG.warning("multilevel_cache_l2_disabled %s", self._l2_init_status)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, key: Any) -> Any | None:
        """Return cached value for *key*, or ``None`` on a full miss.

        Read-through order: L1 -> L2.
        On an L2 hit the value is promoted into L1.
        """
        # L1 lookup (lock guards TTLCache which mutates internal state on reads)
        with self._l1_lock:
            if key in self._l1:
                return self._l1[key]

        # L2 lookup (diskcache is thread/process-safe)
        if self._l2 is not None:
            with contextlib.suppress(Exception):
                value = self._l2.get(key)
                if value is not None:
                    # Promote to L1
                    with self._l1_lock:
                        with contextlib.suppress(Exception):
                            self._l1[key] = value
                    return value

        return None

    def set(self, key: Any, value: Any, ttl: float | None = None) -> None:
        """Store *value* for *key* in both L1 and L2 simultaneously (write-through).

        Args:
            key: Cache key (must be hashable for L1; must be picklable for L2).
            value: Value to store. Must be picklable if L2 is active.
            ttl: Per-entry TTL override in seconds. If ``None``:
                 - L1 uses its configured *l1_ttl*.
                 - L2 uses its configured *l2_ttl*.
        """
        with self._l1_lock:
            with contextlib.suppress(Exception):
                self._l1[key] = value

        if self._l2 is not None:
            l2_expire = ttl if ttl is not None else self._l2_ttl
            with contextlib.suppress(Exception):
                self._l2.set(key, value, expire=l2_expire)

    def delete(self, key: Any) -> None:
        """Remove *key* from both L1 and L2."""
        with self._l1_lock:
            self._l1.pop(key, None)
        if self._l2 is not None:
            with contextlib.suppress(Exception):
                self._l2.delete(key)

    def clear(self) -> None:
        """Clear all entries from both L1 and L2."""
        with self._l1_lock:
            self._l1.clear()
        if self._l2 is not None:
            with contextlib.suppress(Exception):
                self._l2.clear()

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    @property
    def l2_available(self) -> bool:
        """Return True if L2 (diskcache) is active."""
        return self._l2 is not None

    @property
    def l2_dir(self) -> Path | None:
        """Return the disk-cache directory path, or ``None`` if L2 is inactive."""
        if self._l2 is None:
            return None
        with contextlib.suppress(Exception):
            return Path(self._l2.directory)
        return None

    @property
    def l2_init_status(self) -> dict[str, Any]:
        """Return initialization metadata for L2 activation/degradation."""
        return dict(self._l2_init_status)

    def stats(self) -> dict[str, Any]:
        """Return a snapshot of current cache occupancy."""
        with self._l1_lock:
            l1_len = len(self._l1)
        result: dict[str, Any] = {"l1_size": l1_len, "l1_maxsize": self._l1.maxsize}
        if self._l2 is not None:
            with contextlib.suppress(Exception):
                result["l2_size"] = len(self._l2)  # type: ignore[arg-type]
                result["l2_volume_bytes"] = self._l2.volume()
        else:
            result["l2_size"] = 0
        return result

    def close(self) -> None:
        """Release resources held by L2 (diskcache file handles)."""
        if self._l2 is not None:
            with contextlib.suppress(Exception):
                self._l2.close()


# ---------------------------------------------------------------------------
# Decorator
# ---------------------------------------------------------------------------


def cached_multi(cache: MultiLevelCache):
    """Decorator that memoises a function's return value via *cache*.

    The cache key is built from the function's qualified name and its
    positional and keyword arguments.  Only hashable argument combinations
    are cached; unhashable arguments cause the function to run uncached.

    Example::

        cache = MultiLevelCache(l1_maxsize=500, l1_ttl=30)

        @cached_multi(cache)
        def expensive(x: int) -> str:
            ...
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            try:
                key = (func.__qualname__, args, tuple(sorted(kwargs.items())))
                # Verify hashability (tuple of kwargs items may contain unhashable values)
                hash(key)
            except TypeError:
                # Unhashable arguments -- skip cache and call through
                return func(*args, **kwargs)

            cached = cache.get(key)
            if cached is not None:
                return cached

            result = func(*args, **kwargs)
            if result is not None:
                cache.set(key, result)
            return result

        # Type annotation for introspection
        wrapper.cache = cache  # type: ignore[attr-defined]
        return wrapper

    return decorator
