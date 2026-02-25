"""Model search and scoring functions.

Extracted from provider_model_manager.py for maintainability.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast


logger = logging.getLogger(__name__)

_MODEL_INDICES_PATH = Path.home() / ".config" / "thegent" / "model_indices.json"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        import orjson as json
        return json.loads(path.read_text())
    except Exception:
        return {}


def list_model_indices(sort_by: str = "name", provider: str | None = None, reverse: bool = False) -> list[dict[str, Any]]:
    """List all model indices with optional sorting."""
    indices = _load_json(_MODEL_INDICES_PATH)
    result = []
    providers = indices.get("providers", {})

    for prov_name, prov_data in providers.items():
        if provider and prov_name.lower() != provider.lower():
            continue
        models = prov_data.get("models", {})
        for model_name, model_data in models.items():
            entry = {"provider": prov_name, "model": model_name, **model_data}
            result.append(entry)

    if sort_by == "name":
        result.sort(key=lambda x: x.get("model", ""), reverse=reverse)
    elif sort_by == "cost":
        result.sort(key=lambda x: x.get("total_cost_per_1m", float("inf")), reverse=reverse)

    return result


def search_models_by_capability(capability: str, min_context: int | None = None, max_cost_per_1m: float | None = None) -> list[dict[str, Any]]:
    """Search models by capability."""
    all_models = list_model_indices(sort_by="cost")
    result = []
    for m in all_models:
        if capability == "reasoning" and not m.get("reasoning"):
            continue
        if capability == "vision" and not m.get("vision"):
            continue
        if min_context and (m.get("context_limit") or 0) < min_context:
            continue
        if max_cost_per_1m and (m.get("total_cost_per_1m") or float("inf")) > max_cost_per_1m:
            continue
        result.append(m)
    return result


def calculate_composite_score(benchmarks: dict[str, float], weights: dict[str, float] | None = None) -> float | None:
    """Calculate composite performance score from benchmarks."""
    if not benchmarks:
        return None
    default_weights = {"swebench": 0.3, "termbench": 0.2, "reasoning": 0.2, "coding": 0.2, "quality": 0.1}
    w = weights or default_weights
    total_weight = 0.0
    weighted_sum = 0.0
    for bench_name, score in benchmarks.items():
        weight = w.get(bench_name, 0.1)
        weighted_sum += score * weight
        total_weight += weight
    return weighted_sum / total_weight if total_weight > 0 else None


def fuzzy_search_models(query: str, min_score: float = 0.3) -> list[dict[str, Any]]:
    """Fuzzy search models by name."""
    query_lower = query.lower()
    all_models = list_model_indices()
    result = []
    for m in all_models:
        model_name = m.get("model", "").lower()
        provider = m.get("provider", "").lower()
        score = 0.0
        if query_lower == model_name:
            score = 1.0
        elif query_lower in model_name:
            score = 0.8
        elif query_lower in provider:
            score = 0.5
        if score >= min_score:
            m["_match_score"] = score
            result.append(m)
    result.sort(key=lambda x: x.get("_match_score", 0), reverse=True)
    return result


__all__ = ["search_models_by_capability", "list_model_indices", "calculate_composite_score", "fuzzy_search_models"]
