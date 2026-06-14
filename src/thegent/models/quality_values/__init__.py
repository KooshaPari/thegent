"""Model quality values and cache-backed quality indices."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from thegent.cache.multi_level import MultiLevelCache

_CACHE = MultiLevelCache(l1_maxsize=128, l1_ttl=3600, l2_dir=Path(tempfile.gettempdir()) / "thegent-quality-values")


class ModelQuality:
    """Model quality value."""

    def __init__(self, quality: float = 1.0) -> None:
        self.quality = quality


def get_model_quality_for_role(role: str) -> ModelQuality:
    """Get model quality for a given role."""
    return ModelQuality(quality=1.0)


def _load_benchmarks() -> dict[str, Any]:
    return {}


def invalidate_quality_index_cache() -> None:
    _CACHE.clear()


def get_model_provider_quality_indices(use_cache: bool = True) -> dict[str, dict[str, float]]:
    cached = _CACHE.get("default") if use_cache else None
    if cached is not None:
        return cached

    _load_benchmarks()
    from thegent.models.cost_values import _iter_catalog_routes

    indices: dict[str, dict[str, float]] = {}
    for route in _iter_catalog_routes():
        model = str(getattr(route, "model", getattr(route, "model_id", "")))
        provider = str(getattr(route, "provider", ""))
        if model and provider:
            indices.setdefault(model, {})[provider] = 1.0
    _CACHE.set("default", indices)
    return indices


__all__ = [
    "ModelQuality",
    "_CACHE",
    "get_model_provider_quality_indices",
    "get_model_quality_for_role",
    "get_model_quality_index",
    "invalidate_quality_index_cache",
]


def get_model_quality_index(model_id: str) -> float:
    """Get the quality index for a model."""
    return 1.0
