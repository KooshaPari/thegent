"""Speed index for all model-provider pairs.

Uses CLIProxyAPIPlus GET /v1/metrics/providers (tps_1m, latency_p50_ms, latency_p95_ms, success_rate)
when available; falls back to Route.latency_ms from catalog.

Circular-dependency note
------------------------
This module previously imported fetch_provider_metrics directly from
phenotype_thegent_agents.agents.cliproxy_manager, creating a Core ↔ Agents cycle.
It now uses the ProxyMetricsPort from cost_values (same port instance), which is
injected at startup.  See phenotype_thegent_core.models.cost_values.set_proxy_metrics_port().
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from phenotype_thegent_core.cache.multi_level import MultiLevelCache

if TYPE_CHECKING:
    from phenotype_thegent_core.config import ThegentSettings

# Default formula parameters (overridable via config)
_TPS_MAX = 200.0
_LATENCY_MAX_MS = 10000.0
_WEIGHT_TPS = 0.4
_WEIGHT_LATENCY = 0.5
_WEIGHT_SUCCESS = 0.1


def _make_speed_cache() -> MultiLevelCache:
    """Create the speed-index cache (L1 in-process + L2 disk).

    L2 dir is resolved lazily from ThegentSettings so the import is safe even if
    config is not yet fully initialised (L2 is disabled in that case).
    """
    try:
        from phenotype_thegent_core.config import ThegentSettings

        settings = ThegentSettings()
        l2_dir = settings.cache_dir / "speed-index"
    except Exception:
        l2_dir = None
    return MultiLevelCache(l1_maxsize=4, l1_ttl=60, l2_dir=l2_dir, l2_ttl=600)


# Multi-level cache for speed indices (key "default" = full result)
# L1: fast in-process TTLCache (60s); L2: diskcache on disk (10 min, survives restarts).
_CACHE: MultiLevelCache = _make_speed_cache()


def _get_params(settings: ThegentSettings | None) -> tuple[float, float]:
    """Get tps_max and latency_max from settings or defaults."""
    try:
        from phenotype_thegent_core.config import ThegentSettings

        s = settings or ThegentSettings()
        return (
            getattr(s, "speed_index_tps_max", _TPS_MAX),
            getattr(s, "speed_index_latency_max_ms", _LATENCY_MAX_MS),
        )
    except Exception:
        return (_TPS_MAX, _LATENCY_MAX_MS)


def _speed_index_from_metrics(
    m: dict,
    tps_max: float = _TPS_MAX,
    latency_max_ms: float = _LATENCY_MAX_MS,
) -> float:
    """Compute speed index (0-1, higher = faster) from provider metrics dict."""
    tps = m.get("tps_1m")
    lat = m.get("latency_p50_ms")
    lat_p95 = m.get("latency_p95_ms")
    success = m.get("success_rate")

    norm_tps = min(1.0, float(tps) / tps_max) if tps is not None else 0.5
    norm_latency = max(0.0, 1.0 - float(lat) / latency_max_ms) if lat is not None else 0.5
    # Optional p95 penalty: if p95 >> p50, slightly reduce index
    if lat_p95 is not None and lat is not None and lat > 0:
        tail_ratio = float(lat_p95) / float(lat)
        if tail_ratio > 2.0:
            norm_latency *= 0.95  # 5% penalty for high tail latency
    norm_success = float(success) if success is not None else 1.0

    return _WEIGHT_TPS * norm_tps + _WEIGHT_LATENCY * norm_latency + _WEIGHT_SUCCESS * norm_success


def _speed_index_from_latency_ms(
    latency_ms: float,
    latency_max_ms: float = _LATENCY_MAX_MS,
) -> float:
    """Fallback: compute speed index from static Route.latency_ms."""
    return max(0.0, 1.0 - latency_ms / latency_max_ms)


def get_model_provider_speed_indices(
    settings: ThegentSettings | None = None,
    use_cache: bool = True,
) -> dict[str, dict[str, float]]:
    """
    Build speed indices for all model-provider pairs.

    Returns: {model_id: {provider: speed_index}}
    speed_index is 0-1, higher = faster.
    Uses proxy metrics when reachable; falls back to Route.latency_ms.
    """
    try:
        from phenotype_thegent_core.config import ThegentSettings

        s = settings or ThegentSettings()
    except Exception:
        s = None

    tps_max, latency_max = _get_params(s)
    cache_ttl = getattr(s, "speed_index_cache_ttl_sec", 60) if s else 60

    if use_cache and cache_ttl > 0:
        cached = _CACHE.get("default")
        if cached is not None:
            return cached

    from phenotype_thegent_core.models.cost_values import _get_proxy_metrics_port, _iter_catalog_routes

    metrics = _get_proxy_metrics_port().fetch_provider_metrics(s) if s else None

    result: dict[str, dict[str, float]] = {}
    for model_id, routes in _iter_catalog_routes():
        if model_id not in result:
            result[model_id] = {}
        for route in routes:
            prov = getattr(route, "provider", None)
            if not prov:
                continue
            if metrics and prov in metrics:
                result[model_id][prov] = _speed_index_from_metrics(metrics[prov], tps_max, latency_max)
            else:
                result[model_id][prov] = _speed_index_from_latency_ms(getattr(route, "latency_ms", 500.0), latency_max)

    if use_cache and cache_ttl > 0:
        _CACHE.set("default", result)

    return result


def invalidate_speed_index_cache() -> None:
    """Clear speed index cache (e.g. after proxy restart)."""
    _CACHE.clear()


def get_model_provider_speed_index(
    model_id: str,
    provider: str,
    settings: ThegentSettings | None = None,
) -> float:
    """
    Get speed index (0-1, higher = faster) for a model-provider pair.

    Returns 0.5 if unknown (neutral).
    """
    from phenotype_thegent_core.models.catalog import normalize_model_id

    indices = get_model_provider_speed_indices(settings)
    canonical = normalize_model_id(model_id)
    model_indices = indices.get(canonical, indices.get(model_id, {}))
    return model_indices.get(provider, 0.5)


def get_model_best_speed_index(
    model_id: str,
    settings: ThegentSettings | None = None,
) -> float:
    """
    Get best speed index (0-1) across all providers for a model.

    Used when provider is unknown (e.g. ObjectiveSelector).
    """
    from phenotype_thegent_core.models.catalog import normalize_model_id

    indices = get_model_provider_speed_indices(settings)
    canonical = normalize_model_id(model_id)
    model_indices = indices.get(canonical, indices.get(model_id, {}))
    return max(model_indices.values()) if model_indices else 0.5
