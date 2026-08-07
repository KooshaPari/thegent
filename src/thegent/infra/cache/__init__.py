"""TGNT-P9.x cache primitives — canonical home for thegent infra cache.

This package replaces the legacy single-file ``infra/cache_v2.py`` (419
LOC, 6 classes, 0 tests). The split is part of the WL706 L1 Architecture
hardening pass that brings every public class / function under test
coverage and reduces the CC of the two fan-out hot paths:

* ``CrossProcessSingleflight.do`` — three helpers (``_try_acquire_lock``,
  ``_wait_for_result``, ``_persist_result``) collapse a recursive
  retry + sleep-loop into ≤35 LOC of orchestration.
* ``MultiTierCache.get`` — three helpers (``_check_l1``,
  ``_check_l2_promote_to_l1``, ``_check_l3_promote_to_l2_and_l1``)
  collapse the three-tier promotion fan-out into ≤10 LOC.

Public surface (re-exported by ``infra.cache_v2`` back-compat shim):

* :class:`CacheV2` — async-friendly TTL cache (TGNT-P9.5).
* :class:`Singleflight` — in-process coalescing (TGNT-P9.1).
* :class:`CrossProcessSingleflight` — cross-process coalescing via
  file locks (TGNT-P9.1).
* :class:`HeatBasedLRU` — frequency + decay LRU eviction (TGNT-P9.3).
* :class:`CacheInvalidator` — watchdog / inotify invalidation
  (TGNT-P9.2).
* :class:`MultiTierCache` — three-tier L1 (TTLCache) + L2 (LRUCache) +
  L3 (PersistDict) cache (TGNT-P9.4).
* :func:`get_cache` — singleton accessor for ``MultiTierCache``.

A back-compat shim at ``infra/cache_v2.py`` (30 LOC) re-exports every
public symbol above so legacy imports (``from thegent.infra.cache_v2
import MultiTierCache, get_cache``) continue to resolve.
"""

from __future__ import annotations

from thegent.infra.cache.heat_lru import HeatBasedLRU
from thegent.infra.cache.invalidator import HAS_WATCHDOG, CacheInvalidator
from thegent.infra.cache.multi_tier import MultiTierCache, get_cache
from thegent.infra.cache.singleflight import CrossProcessSingleflight, Singleflight
from thegent.infra.cache.ttl import CacheV2

__all__ = [
    "CacheInvalidator",
    "CacheV2",
    "CrossProcessSingleflight",
    "HAS_WATCHDOG",
    "HeatBasedLRU",
    "MultiTierCache",
    "Singleflight",
    "get_cache",
]
