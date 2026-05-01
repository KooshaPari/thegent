"""STUB MODULE - thegent.provider_model_manager

WARNING: This is an auto-generated stub module.
The actual implementation was moved/deleted during repository restructuring.
This stub exists for backwards compatibility with existing tests.
"""

from __future__ import annotations
from typing import Any


def discover_models(provider: str | None = None) -> list[dict[str, Any]]:
    """Discover available models."""
    return []


__all__ = ["discover_models", "validate_provider"]


def validate_provider(provider: str) -> bool:
    """Validate a provider name."""
    return True
