"""Model scoring, indices, and benchmarking functions.

This module provides functions for:
- Model indices (context limits, cost, speed, benchmarks)
- Composite score calculation
- Fuzzy search
- Modality management
"""

import logging
from typing import Any, cast

try:
    from rapidfuzz import fuzz, process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    fuzz = None
    process = None

from thegent_routing.provider_model_manager_io import (
    MODEL_INDICES_PATH as _MODEL_INDICES_PATH,
    load_json as _load_json,
    save_json as _save_json,
)

_LOG = logging.getLogger(__name__)


# ============ MODEL INDICES ============


def get_model_indices(provider: str | None = None, model: str | None = None) -> dict[str, Any]:
    """Get model indices (context limits, cost, speed, benchmarks)."""
    indices = _load_json(_MODEL_INDICES_PATH)

    result: dict[str, Any] = {}
    providers = indices.get("providers", {})

    for prov_name, prov_data in providers.items():
        if provider and prov_name.lower() != provider.lower():
            continue

        models = prov_data.get("models", {})
        for model_name, model_data in models.items():
            if model and model_name.lower() != model.lower():
                continue

            key = f"{prov_name}/{model_name}"
            result[key] = {
                "provider": prov_name,
                "model": model_name,
                **model_data,
            }

    return result


def list_model_indices(
    provider: str | None = None,
    sort_by: str = "context",
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """List all model indices with optional sorting.

    Args:
        provider: Optional provider filter
        sort_by: Sort by 'context', 'cost_input', 'cost_output', 'tps', 'score'
        limit: Optional limit on results

    Returns:
        List of model index entries sorted by specified field
    """
    indices = get_model_indices(provider=provider)

    results = []
    for key, data in indices.items():
        results.append(
            {
                "key": key,
                "provider": data.get("provider"),
                "model": data.get("model"),
                "context_window": data.get("context_window"),
                "max_output_tokens": data.get("max_output_tokens"),
                "cost_per_1m_input": data.get("cost_per_1m_input"),
                "cost_per_1m_output": data.get("cost_per_1m_output"),
                "tokens_per_second": data.get("tokens_per_second"),
                "benchmarks": data.get("benchmarks", {}),
                "modalities": data.get("modalities", {}),
            }
        )

    # Sort by specified field
    def sort_key(item: dict) -> Any:
        if sort_by == "context":
            return -(item.get("context_window") or 0)
        elif sort_by == "cost_input":
            return item.get("cost_per_1m_input") or float("inf")
        elif sort_by == "cost_output":
            return item.get("cost_per_1m_output") or float("inf")
        elif sort_by == "tps":
            return -(item.get("tokens_per_second") or 0)
        elif sort_by == "score":
            return -(calculate_composite_score(item.get("benchmarks", {})) or 0)
        return 0

    results.sort(key=sort_key)

    if limit:
        results = results[:limit]

    return results


def add_model_index(
    provider: str,
    model: str,
    context_window: int | None = None,
    max_output_tokens: int | None = None,
    cost_per_1m_input: float | None = None,
    cost_per_1m_output: float | None = None,
    tokens_per_second: int | None = None,
    benchmarks: dict[str, float] | None = None,
    modalities: dict[str, bool] | None = None,
) -> tuple[bool, str]:
    """Add or update model index entry.

    Args:
        provider: Provider name
        model: Model name
        context_window: Context window size
        max_output_tokens: Maximum output tokens
        cost_per_1m_input: Cost per million input tokens
        cost_per_1m_output: Cost per million output tokens
        tokens_per_second: Generation speed
        benchmarks: Dict of benchmark_name -> score (0-1)
        modalities: Dict of modality_name -> enabled

    Returns:
        Tuple of (success, message)
    """
    indices = _load_json(_MODEL_INDICES_PATH)

    if "providers" not in indices:
        indices["providers"] = {}

    if provider not in indices["providers"]:
        indices["providers"][provider] = {"models": {}}

    models = indices["providers"][provider]["models"]

    if model not in models:
        models[model] = {}

    # Update fields
    if context_window is not None:
        models[model]["context_window"] = context_window
    if max_output_tokens is not None:
        models[model]["max_output_tokens"] = max_output_tokens
    if cost_per_1m_input is not None:
        models[model]["cost_per_1m_input"] = cost_per_1m_input
    if cost_per_1m_output is not None:
        models[model]["cost_per_1m_output"] = cost_per_1m_output
    if tokens_per_second is not None:
        models[model]["tokens_per_second"] = tokens_per_second
    if benchmarks is not None:
        if "benchmarks" not in models[model]:
            models[model]["benchmarks"] = {}
        models[model]["benchmarks"].update(benchmarks)
    if modalities is not None:
        if "modalities" not in models[model]:
            models[model]["modalities"] = {}
        models[model]["modalities"].update(modalities)

    _save_json(_MODEL_INDICES_PATH, indices)
    return True, f"Updated index for {provider}/{model}"


def remove_model_index(provider: str, model: str) -> tuple[bool, str]:
    """Remove model index entry."""
    indices = _load_json(_MODEL_INDICES_PATH)

    providers = indices.get("providers", {})
    if provider not in providers:
        return False, f"Provider {provider} not found"

    models = providers[provider].get("models", {})
    if model not in models:
        return False, f"Model {model} not found in {provider}"

    del models[model]
    _save_json(_MODEL_INDICES_PATH, indices)
    return True, f"Removed index for {provider}/{model}"


# ============ SCORING ============


def calculate_composite_score(
    benchmarks: dict[str, float],
    weights: dict[str, float] | None = None,
) -> float | None:
    """Calculate composite performance score from benchmarks.

    Uses available benchmarks only - missing benchmarks don't penalize.
    Results are normalized to 0-100 scale.

    Args:
        benchmarks: Dict of benchmark_name -> score (0-1)
        weights: Optional custom weights for benchmarks

    Returns:
        Composite score 0-100, or None if no benchmarks available
    """
    if not benchmarks:
        return None

    # Default weights for standard benchmarks
    default_weights = {
        "swebench": 0.25,
        "termbench": 0.25,
        "humaneval": 0.20,
        "mmlu": 0.15,
        "reasoning": 0.15,
    }

    if weights is None:
        weights = default_weights

    total_weight = 0.0
    weighted_sum = 0.0

    for benchmark, score in benchmarks.items():
        if score is None:
            continue

        weight = weights.get(benchmark, 0.1)  # Default 0.1 for custom benchmarks
        weighted_sum += score * weight
        total_weight += weight

    if total_weight == 0:
        return None

    # Normalize to 0-100 scale
    return (weighted_sum / total_weight) * 100


def list_models_with_scores(
    provider: str | None = None,
    min_score: float | None = None,
    modality: str | None = None,
    sort_by: str = "composite_score",
) -> list[dict[str, Any]]:
    """List models with composite performance scores.

    Args:
        provider: Optional provider filter
        min_score: Minimum composite score filter
        modality: Only include models with this modality enabled
        sort_by: Sort by 'composite_score', 'cost', 'context', 'tps'

    Returns:
        List of models with computed composite scores
    """
    indices = _load_json(_MODEL_INDICES_PATH)
    weights = indices.get("benchmark_weights", {})

    result = []
    providers_map = indices.get("providers", {})

    for prov_name, prov_data in providers_map.items():
        if provider and prov_name.lower() != provider.lower():
            continue

        models = prov_data.get("models", {})
        for model_name, model_data in models.items():
            # Check modality filter
            if modality:
                modalities = model_data.get("modalities", {})
                if not modalities.get(modality, False):
                    continue

            # Get benchmarks
            benchmarks = model_data.get("benchmarks", {})
            composite_score = calculate_composite_score(benchmarks, weights)

            # Skip if below minimum score
            if min_score is not None and (composite_score is None or composite_score < min_score):
                continue

            # Get cost efficiency (score per dollar)
            cost_input = model_data.get("cost_per_1m_input", 0) or 0
            cost_output = model_data.get("cost_per_1m_output", 0) or 0
            total_cost = cost_input + cost_output

            result.append(
                {
                    "provider": prov_name,
                    "model": model_name,
                    "display_name": prov_data.get("display_name", prov_name),
                    "composite_score": composite_score,
                    "cost_per_1m_total": total_cost,
                    "context_window": model_data.get("context_window"),
                    "tokens_per_second": model_data.get("tokens_per_second"),
                    "benchmarks": benchmarks,
                    "modalities": model_data.get("modalities", {}),
                }
            )

    # Sort results
    def sort_key(item: dict) -> Any:
        if sort_by == "composite_score":
            return -(item.get("composite_score") or 0)
        elif sort_by == "cost":
            return item.get("cost_per_1m_total") or float("inf")
        elif sort_by == "context":
            return -(item.get("context_window") or 0)
        elif sort_by == "tps":
            return -(item.get("tokens_per_second") or 0)
        return 0

    result.sort(key=sort_key)
    return result


def add_custom_benchmark(
    provider: str,
    model: str,
    benchmark_name: str,
    score: float,
) -> tuple[bool, str]:
    """Add custom benchmark score to model.

    Args:
        provider: Provider name
        model: Model name
        benchmark_name: Name of benchmark
        score: Score (0-1)

    Returns:
        Tuple of (success, message)
    """
    if not 0 <= score <= 1:
        return False, "Score must be between 0 and 1"

    return add_model_index(
        provider=provider,
        model=model,
        benchmarks={benchmark_name: score},
    )


# ============ SEARCH ============


def fuzzy_search_models(
    query: str,
    provider: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Fuzzy search models by name.

    Args:
        query: Search query
        provider: Optional provider filter
        limit: Maximum results

    Returns:
        List of matching models with scores
    """
    indices = get_model_indices(provider=provider)

    # Build list of model names
    model_names = list(indices.keys())

    if RAPIDFUZZ_AVAILABLE:
        # Fuzzy match with rapidfuzz
        results = process.extract(
            query,
            model_names,
            scorer=fuzz.WRatio,
            limit=limit,
        )
        return [
            {
                "key": match,
                "score": score,
                **indices[match],
            }
            for match, score, _ in results
        ]
    else:
        # Fallback to simple substring matching
        query_lower = query.lower()
        matches = []
        for name in model_names:
            if query_lower in name.lower():
                matches.append({
                    "key": name,
                    "score": 100.0 if query_lower == name.lower() else 80.0,
                    **indices[name],
                })
        return matches[:limit]


def search_models_by_capability(
    capability: str,
    provider: str | None = None,
    min_value: float | None = None,
) -> list[dict[str, Any]]:
    """Search models by capability/benchmark score.

    Args:
        capability: Capability name (e.g., 'reasoning', 'coding', 'swebench')
        provider: Optional provider filter
        min_value: Minimum score threshold (0-1)

    Returns:
        List of models matching capability
    """
    indices = get_model_indices(provider=provider)

    results = []
    for key, data in indices.items():
        benchmarks = data.get("benchmarks", {})
        modalities = data.get("modalities", {})

        # Check benchmarks
        benchmark_score = benchmarks.get(capability)
        modality_enabled = modalities.get(capability, False)

        # Match if benchmark or modality matches
        if benchmark_score is not None:
            if min_value is not None and benchmark_score < min_value:
                continue
            results.append({**data, "key": key, "match_type": "benchmark", "score": benchmark_score})
        elif modality_enabled:
            results.append({**data, "key": key, "match_type": "modality", "enabled": True})

    # Sort by score descending
    results.sort(key=lambda x: x.get("score") or 0, reverse=True)
    return results


# ============ MODALITIES ============


def get_model_modalities(provider: str | None = None, model: str | None = None) -> dict[str, Any]:
    """Get model modalities (text, vision, audio, etc.).

    Args:
        provider: Optional provider filter
        model: Optional model filter

    Returns:
        Dict of model -> modalities
    """
    indices = get_model_indices(provider=provider, model=model)

    result = {}
    for key, data in indices.items():
        modalities = data.get("modalities", {})
        if modalities:
            result[key] = modalities

    return result


def add_model_modality(
    provider: str,
    model: str,
    modality: str,
    enabled: bool = True,
) -> tuple[bool, str]:
    """Add or update modality for model.

    Args:
        provider: Provider name
        model: Model name
        modality: Modality name (e.g., 'vision', 'audio', 'tools')
        enabled: Whether modality is enabled

    Returns:
        Tuple of (success, message)
    """
    return add_model_index(
        provider=provider,
        model=model,
        modalities={modality: enabled},
    )


def list_available_modalities() -> dict[str, Any]:
    """List all available modality types.

    Returns:
        Dict of modality -> description
    """
    return {
        "text": "Text generation",
        "vision": "Image understanding",
        "audio": "Audio input/output",
        "tools": "Function calling",
        "streaming": "Streaming output",
        "code": "Code generation",
        "embedding": "Text embeddings",
    }


def search_by_modalities(
    modalities: list[str],
    provider: str | None = None,
    match_all: bool = False,
) -> list[dict[str, Any]]:
    """Search models by enabled modalities.

    Args:
        modalities: List of required modalities
        provider: Optional provider filter
        match_all: If True, require all modalities; if False, require any

    Returns:
        List of models with specified modalities
    """
    indices = get_model_indices(provider=provider)

    results = []
    for key, data in indices.items():
        model_modalities = data.get("modalities", {})

        if match_all:
            # All modalities must be enabled
            if all(model_modalities.get(m, False) for m in modalities):
                results.append({**data, "key": key})
        else:
            # Any modality enabled
            if any(model_modalities.get(m, False) for m in modalities):
                results.append({**data, "key": key})

    return results


__all__ = [
    # Indices
    "get_model_indices",
    "list_model_indices",
    "add_model_index",
    "remove_model_index",
    # Scoring
    "calculate_composite_score",
    "list_models_with_scores",
    "add_custom_benchmark",
    # Search
    "fuzzy_search_models",
    "search_models_by_capability",
    # Modalities
    "get_model_modalities",
    "add_model_modality",
    "list_available_modalities",
    "search_by_modalities",
]
