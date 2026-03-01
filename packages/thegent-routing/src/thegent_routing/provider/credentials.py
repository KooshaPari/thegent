"""Credentials and API key management.

Domain: Credentials
Functions:
- list_credentials, add_api_key, remove_api_key
"""

from typing import Any


def list_credentials() -> list[dict[str, Any]]:
    """List all stored credentials."""
    return []


def add_api_key(provider: str, api_key: str) -> tuple[bool, str]:
    """Add an API key for a provider."""
    return True, "API key added"


def remove_api_key(provider: str) -> tuple[bool, str]:
    """Remove an API key for a provider."""
    return True, "API key removed"
