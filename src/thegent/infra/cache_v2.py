"""Back-compat shim — canonical home is ``thegent.infra.cache`` package.

The single-file ``cache_v2.py`` (419 LOC, 6 classes, 0 tests) was split
into a 5-submodule package during WL706 L1 Architecture hardening:

* :mod:`thegent.infra.cache.ttl` — :class:`CacheV2`
* :mod:`thegent.infra.cache.singleflight` — :class:`Singleflight`,
  :class:`CrossProcessSingleflight`
* :mod:`thegent.infra.cache.heat_lru` — :class:`HeatBasedLRU`
* :mod:`thegent.infra.cache.invalidator` — :class:`CacheInvalidator`,
  ``HAS_WATCHDOG``
* :mod:`thegent.infra.cache.multi_tier` — :class:`MultiTierCache`,
  :func:`get_cache`, ``PERSISTDICT_AVAILABLE``

Every legacy import (``from thegent.infra.cache_v2 import MultiTierCache``
/ ``get_cache`` / ``CacheInvalidator`` / ``CacheV2``) continues to
resolve against this shim.
"""

from __future__ import annotations

from .cache.heat_lru import HeatBasedLRU
from .cache.invalidator import HAS_WATCHDOG, CacheInvalidator
from .cache.multi_tier import MultiTierCache, get_cache
from .cache.singleflight import CrossProcessSingleflight, Singleflight
from .cache.ttl import CacheV2

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
