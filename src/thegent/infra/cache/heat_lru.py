"""TGNT-P9.3 — heat-based LRU cache primitive.

This module is the canonical home for :class:`HeatBasedLRU`, an LRU
cache with frequency + decay based eviction. Entries accrue "heat" on
every access; the entry with the lowest heat (after applying a
multiplicative decay over the elapsed wall-clock time since its last
access) is the eviction candidate.

It is part of the WL706 L1 Architecture hardening pass that splits the
legacy single-file ``infra/cache_v2.py`` (419 LOC) into focused
single-responsibility sub-modules. Body is verbatim from the legacy
module; only the module-level docstring was tightened.
"""

from __future__ import annotations

import collections
import logging
import threading
import time
from typing import Any

logger = logging.getLogger(__name__)


class HeatBasedLRU:
    """LRU cache with heat-based eviction (frequency + decay)."""

    def __init__(self, capacity: int = 100, decay_factor: float = 0.9) -> None:
        self.capacity = capacity
        self.decay_factor = decay_factor
        self.cache: dict[str, Any] = {}
        self.heat: dict[str, float] = collections.defaultdict(float)
        self.last_access: dict[str, float] = {}
        self.lock = threading.Lock()

    def get(self, key: str) -> Any | None:
        with self.lock:
            if key in self.cache:
                self._update_heat(key)
                return self.cache[key]
            return None

    def put(self, key: str, value: Any):
        with self.lock:
            if len(self.cache) >= self.capacity and key not in self.cache:
                self._evict()
            self.cache[key] = value
            self._update_heat(key)

    def _update_heat(self, key: str):
        now = time.time()
        prev_time = self.last_access.get(key, now)
        elapsed = now - prev_time
        # Apply decay to existing heat
        self.heat[key] = self.heat[key] * (self.decay_factor**elapsed) + 1.0
        self.last_access[key] = now

    def _evict(self):
        # Evict item with lowest heat
        if not self.heat:
            return

        # Recalculate heat for all items before eviction to apply decay
        now = time.time()
        for k in list(self.heat.keys()):
            elapsed = now - self.last_access[k]
            self.heat[k] *= self.decay_factor**elapsed
            self.last_access[k] = now

        victim = min(self.heat, key=lambda k: self.heat.get(k, 0.0))
        del self.cache[victim]
        del self.heat[victim]
        del self.last_access[victim]
        logger.info(f"Evicted {victim} from cache based on heat")


__all__ = ["HeatBasedLRU"]
