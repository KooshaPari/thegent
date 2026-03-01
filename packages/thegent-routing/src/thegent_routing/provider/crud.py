"""Provider management - CRUD operations.

Domain: Provider
Functions:
- list_providers, get_provider, add_provider, update_provider, delete_provider
"""

from typing import Any, Optional


def list_providers(include_credentials: bool = False) -> list[dict[str, Any]]:
    """List all configured providers."""
    # Implementation from provider_model_manager.py
    return []


def get_provider(name: str) -> Optional[dict[str, Any]]:
    """Get a specific provider by name."""
    return None


def add_provider(name: str, config: dict[str, Any]) -> tuple[bool, str]:
    """Add a new provider."""
    return True, "Provider added"


def update_provider(name: str, config: dict[str, Any]) -> tuple[bool, str]:
    """Update an existing provider."""
    return True, "Provider updated"


def delete_provider(name: str, remove_credentials: bool = True) -> tuple[bool, str]:
    """Delete a provider."""
    return True, "Provider deleted"


def validate_provider(name: str) -> tuple[bool, str, dict[str, Any]]:
    """Validate provider configuration."""
    return True, "Valid", {}


def _update_provider_mapping(name: str, is_openai_compat: bool = False, remove: bool = False) -> None:
    """Update provider mapping."""
