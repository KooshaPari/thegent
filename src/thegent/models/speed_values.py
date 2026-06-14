"""Model speed values and cache-backed speed indices."""

from __future__ import annotations

import tempfile
from pathlib import Path

from thegent.cache.multi_level import MultiLevelCache

_CACHE = MultiLevelCache(l1_maxsize=128, l1_ttl=3600, l2_dir=Path(tempfile.gettempdir()) / "thegent-speed-values")


def invalidate_speed_index_cache() -> None:
    _CACHE.clear()


def get_model_provider_speed_indices(use_cache: bool = True) -> dict[str, dict[str, float]]:
    cached = _CACHE.get("default") if use_cache else None
    if cached is not None:
        return cached

    from thegent.agents.cliproxy_manager import fetch_provider_metrics
    from thegent.models.cost_values import _iter_catalog_routes

    fetch_provider_metrics()
    indices: dict[str, dict[str, float]] = {}
    for route in _iter_catalog_routes():
        model = str(getattr(route, "model", getattr(route, "model_id", "")))
        provider = str(getattr(route, "provider", ""))
        if model and provider:
            indices.setdefault(model, {})[provider] = 1.0
    _CACHE.set("default", indices)
    return indices


__all__ = ["_CACHE", "get_model_provider_speed_indices", "invalidate_speed_index_cache"]
