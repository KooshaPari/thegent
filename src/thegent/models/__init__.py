"""STUB MODULE - thegent.models

WARNING: This is an auto-generated stub module.
The actual implementation was moved/deleted during repository restructuring.
This stub exists for backwards compatibility with existing tests.
"""

from __future__ import annotations
from typing import Any


class ModelCatalog:
    """Catalog of available models."""

    def __init__(self) -> None:
        self._models: dict[str, Any] = {}

    def register(self, model_id: str, model_info: dict[str, Any]) -> None:
        """Register a model."""
        self._models[model_id] = model_info

    def get(self, model_id: str) -> dict[str, Any] | None:
        """Get model information."""
        return self._models.get(model_id)


__all__ = ["ModelCatalog", "filter_models_for_provider", "normalize_model_id"]


def filter_models_for_provider(provider: str) -> list[str]:
    """Filter models by provider."""
    return []


def normalize_model_id(model_id: str) -> str:
    """Normalize a model ID to canonical form."""
    return model_id.strip().lower()
