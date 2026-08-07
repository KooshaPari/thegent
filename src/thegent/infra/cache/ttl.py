"""TGNT-P9.5 — async-friendly TTL cache primitive.

This module is the canonical home for :class:`CacheV2`, the in-process
TTL cache used by the newer infra modules (e.g.
``infra.mojo_bridge.MojoBridge``).

It is part of the WL706 L1 Architecture hardening pass that splits the
legacy single-file ``infra/cache_v2.py`` (419 LOC) into focused
single-responsibility sub-modules. Body is verbatim from the legacy
module; only the module-level docstring was tightened.
"""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any

logger = __import__("logging").getLogger(__name__)


class CacheV2:
    """Async-friendly TTL cache used by newer infra modules."""

    def __init__(self, root: Path, namespace: str = "default") -> None:
        self.root = root
        self.namespace = namespace
        self.root.mkdir(parents=True, exist_ok=True)
        self._store: dict[str, tuple[float | None, Any]] = {}
        self._lock = threading.Lock()

    async def get(self, key: str) -> Any | None:
        with self._lock:
            item = self._store.get(key)
            if item is None:
                return None
            expires_at, value = item
            if expires_at is not None and expires_at <= time.time():
                del self._store[key]
                return None
            return value

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        expires_at = None if ttl is None else time.time() + ttl
        with self._lock:
            self._store[key] = (expires_at, value)

    async def clear_expired(self) -> None:
        now = time.time()
        with self._lock:
            expired_keys = [k for k, (exp, _) in self._store.items() if exp is not None and exp <= now]
            for key in expired_keys:
                del self._store[key]

    async def clear(self) -> None:
        with self._lock:
            self._store.clear()


__all__ = ["CacheV2"]
