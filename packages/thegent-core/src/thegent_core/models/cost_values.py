"""Cost values for all model-provider pairs.

Uses CLIProxyAPIPlus GET /v1/metrics/providers when available; falls back to
static catalog cost_weight, planning/models_meta, and governance defaults.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from thegent_core.config import ThegentSettings

# Fallback $/1k (input, output) when proxy unreachable. From _GLM_OFFER_COST and catalog.
_PROVIDER_FALLBACK: dict[str, tuple[float, float]] = {
    "nim": (0.11, 0.22),
    "kilo": (0.14, 0.28),
    "minimax": (0.18, 0.36),
    "glm": (0.40, 0.80),
    "antigravity": (0.15, 0.30),
    "kiro": (0.15, 0.30),
    "cursor": (0.05, 0.15),
    "gemini": (0.00005, 0.0002),
    "claude": (0.0015, 0.0075),
    "codex": (0.0025, 0.0075),
    "copilot": (0.0002, 0.001),
    "openrouter": (0.002, 0.01),
    "qwen": (0.0, 0.0),  # QwenCode free tier
}


def _provider_cost_from_metrics(m: dict) -> tuple[float, float]:
    """Extract (input_per_1k, output_per_1k) from provider metrics dict."""
    inp = m.get("cost_per_1k_input")
    out = m.get("cost_per_1k_output")
    if inp is not None and out is not None:
        return (float(inp), float(out))
    single = m.get("cost_per_1k")
    if single is not None:
        v = float(single)
        return (v * 0.4, v)  # Assume output ~2.5x input
    return (0.0, 0.0)


def get_model_provider_costs(settings: ThegentSettings | None = None) -> dict[str, dict[str, tuple[float, float]]]:
    """
    Build cost values for all model-provider pairs.

    Returns: {model_id: {provider: (input_per_1k_usd, output_per_1k_usd)}}
    Uses proxy metrics when reachable; falls back to static values.
    """
    from thegent_agents.agents.cliproxy_manager import fetch_provider_metrics

    try:
        from thegent_core.config import ThegentSettings

        settings = settings or ThegentSettings()
    except Exception:
        settings = None

    metrics = fetch_provider_metrics(settings) if settings else None

    # Provider -> (in, out) from metrics or fallback
    provider_costs: dict[str, tuple[float, float]] = {}
    if metrics:
        for prov, m in metrics.items():
            in_out = _provider_cost_from_metrics(m)
            if in_out != (0.0, 0.0):
                provider_costs[prov] = in_out
    for prov, fallback in _PROVIDER_FALLBACK.items():
        if prov not in provider_costs:
            provider_costs[prov] = fallback

    # Build model -> provider -> (in, out) from catalog routes
    result: dict[str, dict[str, tuple[float, float]]] = {}
    for model_id, routes in _iter_catalog_routes():
        if model_id not in result:
            result[model_id] = {}
        for route in routes:
            prov = getattr(route, "provider", None)
            if prov:
                cost = provider_costs.get(prov, _PROVIDER_FALLBACK.get(prov, (0.001, 0.002)))
                result[model_id][prov] = cost

    return result


def _iter_catalog_routes() -> list[tuple[str, list]]:
    """Yield (model_id, routes) from catalog (static + scraped)."""
    from thegent_core.models.catalog import _get_catalog, _scraped_to_routes
    from thegent_core.models.scrapers import get_scraped_catalog

    catalog = _get_catalog()
    out: list[tuple[str, list]] = list(catalog.items())
    try:
        scraped = get_scraped_catalog()
        if scraped:
            scraped_map = _scraped_to_routes(scraped)
            for model_id, routes in scraped_map.items():
                if model_id not in catalog:
                    out.append((model_id, routes))
    except Exception:
        pass
    return out


def get_cost_for_model_provider(
    model_id: str,
    provider: str,
    settings: ThegentSettings | None = None,
) -> tuple[float, float]:
    """
    Get (input_per_1k_usd, output_per_1k_usd) for a model-provider pair.

    Returns (0.001, 0.002) if unknown.
    """
    from thegent_core.models.catalog import normalize_model_id

    costs = get_model_provider_costs(settings)
    canonical = normalize_model_id(model_id)
    model_costs = costs.get(canonical, costs.get(model_id, {}))
    return model_costs.get(provider, (0.001, 0.002))
