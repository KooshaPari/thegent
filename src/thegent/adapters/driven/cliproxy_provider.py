"""CLIProxy compatibility layer adapter.

This module adapts provider operations to CLIProxy's openai-compatibility configuration format.
It delegates to provider_model_manager_cliproxy for core CLIProxy logic.
"""

from __future__ import annotations

import logging
from typing import Any

from thegent.provider_model_manager_cliproxy import (
    get_api_key_from_compat,
    remove_openai_compat_entry,
    upsert_openai_compat_entry,
)

_LOG = logging.getLogger(__name__)


class CliproxyCompatAdapter:
    """Adapter for CLIProxy openai-compatibility configuration."""

    @staticmethod
    def upsert_entry(
        compat: list[dict[str, Any]],
        *,
        name: str,
        base_url: str,
        model: str,
        api_key: str,
    ) -> None:
        """Add or update a CLIProxy openai-compatibility entry.

        Args:
            compat: The openai-compatibility list to modify in-place.
            name: Provider name.
            base_url: Provider base URL.
            model: Default model name.
            api_key: API key for authentication.
        """
        upsert_openai_compat_entry(
            compat,
            name=name,
            base_url=base_url,
            model=model,
            api_key=api_key,
        )

    @staticmethod
    def remove_entry(compat: list[dict[str, Any]], name: str) -> list[dict[str, Any]]:
        """Remove a CLIProxy openai-compatibility entry.

        Args:
            compat: The openai-compatibility list.
            name: Provider name to remove.

        Returns:
            Filtered list excluding the provider.
        """
        return remove_openai_compat_entry(compat, name)

    @staticmethod
    def get_api_key(compat: list[dict[str, Any]], name: str) -> str | None:
        """Get API key from a CLIProxy openai-compatibility entry.

        Args:
            compat: The openai-compatibility list.
            name: Provider name.

        Returns:
            API key string, or None if not found.
        """
        return get_api_key_from_compat(compat, name)


__all__ = [
    "CliproxyCompatAdapter",
]
