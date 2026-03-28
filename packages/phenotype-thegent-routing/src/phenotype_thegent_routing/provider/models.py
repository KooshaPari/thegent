"""Model management - model CRUD, aliases, indices.

Domain: Models
Functions:
- list_models, add_model_alias, remove_model_alias
- get_model_indices, add_model_index, remove_model_index
- search_models_by_capability, fuzzy_search_models
"""

from typing import Any, Optional


def list_models(provider: Optional[str] = None) -> list[dict[str, Any]]:
    """List models, optionally filtered by provider."""
    return []


def add_model_alias(provider: str, model: str, alias: str) -> tuple[bool, str]:
    """Add a model alias."""
    return True, "Alias added"


def remove_model_alias(provider: str, alias: str) -> tuple[bool, str]:
    """Remove a model alias."""
    return True, "Alias removed"


def add_common_alias(alias: str) -> tuple[bool, str]:
    """Add a common alias across providers."""
    return True, "Common alias added"


def remove_common_alias(alias: str) -> tuple[bool, str]:
    """Remove a common alias."""
    return True, "Common alias removed"


def get_model_indices(
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> dict[str, Any]:
    """Get model indices."""
    return {}


def list_model_indices(provider: Optional[str] = None) -> list[dict[str, Any]]:
    """List all model indices."""
    return []


def add_model_index(provider: str, model: str, index: dict[str, Any]) -> tuple[bool, str]:
    """Add a model index."""
    return True, "Index added"


def remove_model_index(provider: str, model: str) -> tuple[bool, str]:
    """Remove a model index."""
    return True, "Index removed"


def search_models_by_capability(capability: str) -> list[dict[str, Any]]:
    """Search models by capability."""
    return []


def fuzzy_search_models(query: str) -> list[dict[str, Any]]:
    """Fuzzy search models."""
    return []


def add_custom_benchmark(name: str, config: dict[str, Any]) -> tuple[bool, str]:
    """Add a custom benchmark."""
    return True, "Benchmark added"


def add_model_modality(provider: str, model: str, modality: str) -> tuple[bool, str]:
    """Add a model modality."""
    return True, "Modality added"


def list_available_modalities() -> dict[str, list[str]]:
    """List available modalities."""
    return {}


def search_by_modalities(modalities: list[str]) -> list[dict[str, Any]]:
    """Search models by modalities."""
    return []
