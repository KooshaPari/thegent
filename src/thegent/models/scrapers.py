"""Model scraper cache helpers."""

from __future__ import annotations

import tempfile
import time
from pathlib import Path

from thegent.cache.multi_level import MultiLevelCache

_CACHE_PATH = Path(tempfile.gettempdir()) / "thegent-models"
_MODELS_CACHE = MultiLevelCache(l1_maxsize=64, l1_ttl=3600, l2_dir=_CACHE_PATH)


def _save_cache(by_provider: dict[str, list[str]], ttl_sec: int = 3600) -> None:
    _MODELS_CACHE.set("by_provider", by_provider, ttl=ttl_sec)
    _MODELS_CACHE.set("mtime", time.time(), ttl=ttl_sec)


def _load_cached() -> tuple[dict[str, list[str]], float] | None:
    by_provider = _MODELS_CACHE.get("by_provider")
    mtime = _MODELS_CACHE.get("mtime")
    if by_provider is None or mtime is None:
        return None
    return by_provider, float(mtime)


def invalidate_models_cache() -> bool:
    had_entries = _MODELS_CACHE.get("by_provider") is not None or _MODELS_CACHE.get("mtime") is not None
    _MODELS_CACHE.clear()
    return had_entries


def get_models_cache_path() -> Path:
    return _CACHE_PATH


__all__ = [
    "_MODELS_CACHE",
    "_load_cached",
    "_save_cache",
    "get_models_cache_path",
    "invalidate_models_cache",
]
