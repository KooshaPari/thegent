"""Quality index for models.

Uses benchmarks.json (Terminal Bench 2.0, SWE-Bench, AIME) when available;
falls back to Route.accuracy_score from catalog.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from thegent.cache.multi_level import MultiLevelCache

if TYPE_CHECKING:
    from thegent.config import ThegentSettings

# Default weights (terminal-first)
_WEIGHT_TB2 = 0.7
_WEIGHT_SWE = 0.2
_WEIGHT_AIME = 0.1
_WEIGHT_PARSER = 0.0


def _make_quality_cache() -> MultiLevelCache:
    """Create the quality-index cache (L1 in-process + L2 disk).

    L2 dir is resolved lazily from ThegentSettings so the import is safe even if
    config is not yet fully initialised (L2 is disabled in that case).
    """
    try:
        from thegent.config import ThegentSettings

        settings = ThegentSettings()
        l2_dir = settings.cache_dir / "quality-index"
    except Exception:
        l2_dir = None
    return MultiLevelCache(l1_maxsize=4, l1_ttl=300, l2_dir=l2_dir, l2_ttl=3600)


# Multi-level cache for quality indices (key "default" = full result)
# L1: fast in-process TTLCache; L2: diskcache on disk (survives restarts).
_CACHE: MultiLevelCache = _make_quality_cache()


def _default_benchmarks_path() -> Path:
    """Path to bundled benchmarks.json."""
    return Path(__file__).resolve().parent / "benchmarks.json"


def _resolve_benchmarks_path(settings: ThegentSettings | None) -> Path:
    """Resolve benchmarks path from config or default."""
    if settings and getattr(settings, "quality_index_benchmarks_path", None):
        p = settings.quality_index_benchmarks_path
        if p and p.exists():
            return p
    return _default_benchmarks_path()


def _load_benchmarks(path: Path | None = None) -> dict:
    """Load benchmarks from JSON. Returns empty dict on error."""
    p = path or _default_benchmarks_path()
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text())
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _quality_index_from_benchmarks(
    model_id: str,
    benchmarks: dict,
    weight_tb2: float = _WEIGHT_TB2,
    weight_swe: float = _WEIGHT_SWE,
    weight_aime: float = _WEIGHT_AIME,
) -> float | None:
    """Compute quality index (0-1) from benchmarks. Returns None if insufficient data."""
    tb2 = benchmarks.get("terminal_bench_2_0", {})
    swe = benchmarks.get("swe_bench", {})
    aime = benchmarks.get("aime", {})

    v_tb2 = tb2.get(model_id)
    v_swe = swe.get(model_id)
    v_aime = aime.get(model_id)

    if v_tb2 is None and v_swe is None and v_aime is None:
        return None

    norm_tb2 = (float(v_tb2) / 100.0) if v_tb2 is not None else 0.5
    norm_swe = (float(v_swe) / 100.0) if v_swe is not None else 0.5
    norm_aime = (float(v_aime) / 100.0) if v_aime is not None else 0.5

    return weight_tb2 * norm_tb2 + weight_swe * norm_swe + weight_aime * norm_aime + _WEIGHT_PARSER * 1.0


def get_model_quality_index(
    model_id: str,
    settings: ThegentSettings | None = None,
    benchmarks_path: Path | str | None = None,
) -> float:
    """
    Get quality index (0-1) for a model.

    Uses benchmarks.json when available; falls back to Route.accuracy_score.
    """
    from thegent.models.catalog import ModelCatalog, normalize_model_id

    canonical = normalize_model_id(model_id)
    path = Path(benchmarks_path) if benchmarks_path else _resolve_benchmarks_path(settings)
    benchmarks = _load_benchmarks(path)
    w_tb2 = getattr(settings, "quality_index_weight_tb2", _WEIGHT_TB2) if settings else _WEIGHT_TB2
    w_swe = getattr(settings, "quality_index_weight_swe", _WEIGHT_SWE) if settings else _WEIGHT_SWE
    w_aime = getattr(settings, "quality_index_weight_aime", _WEIGHT_AIME) if settings else _WEIGHT_AIME
    idx = _quality_index_from_benchmarks(canonical, benchmarks, w_tb2, w_swe, w_aime)
    if idx is not None:
        return max(0.0, min(1.0, idx))

    routes = ModelCatalog.routes_for(canonical) or ModelCatalog.routes_for(model_id)
    if routes:
        return getattr(routes[0], "accuracy_score", 0.8)

    return 0.5


def get_model_provider_quality_indices(
    settings: ThegentSettings | None = None,
    benchmarks_path: Path | str | None = None,
    use_cache: bool = True,
) -> dict[str, dict[str, float]]:
    """
    Returns: {model_id: {provider: quality_index}}
    Same model has same quality across providers; structure matches cost/speed.
    """
    try:
        from thegent.config import ThegentSettings

        s = settings or ThegentSettings()
    except Exception:
        s = None

    path = Path(benchmarks_path) if benchmarks_path else _resolve_benchmarks_path(s)
    cache_ttl = getattr(s, "quality_index_cache_ttl_sec", 300) if s else 300

    if use_cache and cache_ttl > 0:
        cached = _CACHE.get("default")
        if cached is not None:
            return cached

    from thegent.models.cost_values import _iter_catalog_routes

    benchmarks = _load_benchmarks(path)
    w_tb2 = getattr(s, "quality_index_weight_tb2", _WEIGHT_TB2) if s else _WEIGHT_TB2
    w_swe = getattr(s, "quality_index_weight_swe", _WEIGHT_SWE) if s else _WEIGHT_SWE
    w_aime = getattr(s, "quality_index_weight_aime", _WEIGHT_AIME) if s else _WEIGHT_AIME

    result: dict[str, dict[str, float]] = {}
    for model_id, routes in _iter_catalog_routes():
        base_idx = _quality_index_from_benchmarks(model_id, benchmarks, w_tb2, w_swe, w_aime)
        if base_idx is not None:
            base_idx = max(0.0, min(1.0, base_idx))

        if model_id not in result:
            result[model_id] = {}
        for route in routes:
            prov = getattr(route, "provider", None)
            if not prov:
                continue
            if base_idx is not None:
                result[model_id][prov] = base_idx
            else:
                result[model_id][prov] = getattr(route, "accuracy_score", 0.8)

    if use_cache and cache_ttl > 0:
        _CACHE.set("default", result)

    return result


def get_model_provider_quality_index(
    model_id: str,
    provider: str,
    settings: ThegentSettings | None = None,
) -> float:
    """
    Get quality index (0-1) for a model-provider pair.

    Returns 0.5 if unknown.
    """
    from thegent.models.catalog import normalize_model_id

    indices = get_model_provider_quality_indices(settings)
    canonical = normalize_model_id(model_id)
    model_indices = indices.get(canonical, indices.get(model_id, {}))
    return model_indices.get(provider, 0.5)


# Map role benchmark_weights keys to our benchmark dimensions (Helios spec)
_ROLE_TO_BENCHMARK: dict[str, tuple[str, ...]] = {
    "terminal_bench_2_0": ("instruction_following", "coherence", "safety"),
    "swe_bench": ("coding", "tool_use"),
    "aime": ("reasoning", "long_context", "writing_eval"),
}


def _role_weights_to_benchmark_weights(
    role_weights: dict[str, float],
) -> tuple[float, float, float]:
    """Map role benchmark_weights to (tb2, swe, aime) weights. Returns normalized tuple."""
    w_tb2 = sum(role_weights.get(k, 0) for k in _ROLE_TO_BENCHMARK["terminal_bench_2_0"])
    w_swe = sum(role_weights.get(k, 0) for k in _ROLE_TO_BENCHMARK["swe_bench"])
    w_aime = sum(role_weights.get(k, 0) for k in _ROLE_TO_BENCHMARK["aime"])
    total = w_tb2 + w_swe + w_aime
    if total <= 0:
        return (_WEIGHT_TB2, _WEIGHT_SWE, _WEIGHT_AIME)
    return (w_tb2 / total, w_swe / total, w_aime / total)


def get_model_quality_for_role(
    model_id: str,
    role_benchmark_weights: dict[str, float] | None,
    settings: ThegentSettings | None = None,
    benchmarks_path: Path | str | None = None,
) -> float:
    """
    Get quality index (0-1) for a model with role-specific benchmark weights.
    When role_benchmark_weights is None or empty, falls back to default weights.
    """
    if not role_benchmark_weights:
        return get_model_quality_index(model_id, settings, benchmarks_path)
    w_tb2, w_swe, w_aime = _role_weights_to_benchmark_weights(role_benchmark_weights)
    path = Path(benchmarks_path) if benchmarks_path else _resolve_benchmarks_path(settings)
    benchmarks = _load_benchmarks(path)
    from thegent.models.catalog import normalize_model_id

    canonical = normalize_model_id(model_id)
    idx = _quality_index_from_benchmarks(canonical, benchmarks, w_tb2, w_swe, w_aime)
    if idx is not None:
        return max(0.0, min(1.0, idx))
    return get_model_quality_index(model_id, settings, benchmarks_path)


def invalidate_quality_index_cache() -> None:
    """Clear quality index cache (e.g. after benchmarks.json update)."""
    _CACHE.clear()


def get_all_model_quality_indices(
    settings: ThegentSettings | None = None,
    benchmarks_path: Path | str | None = None,
) -> dict[str, float]:
    """
    Returns: {model_id: quality_index}
    """
    from thegent.models.cost_values import _iter_catalog_routes

    try:
        from thegent.config import ThegentSettings

        s = settings or ThegentSettings()
    except Exception:
        s = None
    path = Path(benchmarks_path) if benchmarks_path else _resolve_benchmarks_path(settings)
    benchmarks = _load_benchmarks(path)
    w_tb2 = getattr(s, "quality_index_weight_tb2", _WEIGHT_TB2) if s else _WEIGHT_TB2
    w_swe = getattr(s, "quality_index_weight_swe", _WEIGHT_SWE) if s else _WEIGHT_SWE
    w_aime = getattr(s, "quality_index_weight_aime", _WEIGHT_AIME) if s else _WEIGHT_AIME

    result: dict[str, float] = {}
    for model_id, routes in _iter_catalog_routes():
        idx = _quality_index_from_benchmarks(model_id, benchmarks, w_tb2, w_swe, w_aime)
        if idx is not None:
            result[model_id] = max(0.0, min(1.0, idx))
        elif routes:
            result[model_id] = getattr(routes[0], "accuracy_score", 0.8)
        else:
            result[model_id] = 0.5

    return result
