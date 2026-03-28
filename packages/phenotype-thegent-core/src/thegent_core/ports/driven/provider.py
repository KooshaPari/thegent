"""ProviderPort: Interface for provider CRUD operations."""

from __future__ import annotations

from typing import Any, Protocol


class ProviderPort(Protocol):
    """Port interface for provider management operations."""

    def list_providers(self, include_credentials: bool = False) -> list[dict[str, Any]]:
        """List all configured providers.

        Args:
            include_credentials: If False, strips sensitive API keys.

        Returns:
            List of provider configurations.
        """
        ...

    def get_provider(self, name: str) -> dict[str, Any] | None:
        """Get a specific provider by name.

        Args:
            name: Provider name (case-insensitive).

        Returns:
            Provider configuration dict, or None if not found.
        """
        ...

    def add_provider(
        self,
        name: str,
        base_url: str,
        model: str,
        login_url: str | None = None,
        login_instructions: list[str] | None = None,
        display_name: str | None = None,
        extra_aliases: list[str] | None = None,
        api_key: str | None = None,
        base_url_env: str | None = None,
    ) -> tuple[bool, str]:
        """Add a new provider.

        Args:
            name: Provider name.
            base_url: Base URL for the provider API.
            model: Default model name.
            login_url: Optional login/authentication URL.
            login_instructions: Optional list of login instruction steps.
            display_name: Display name for login UI.
            extra_aliases: Additional model aliases.
            api_key: API key to store in config.
            base_url_env: Environment variable name for base_url.

        Returns:
            Tuple of (success: bool, message: str).
        """
        ...

    def update_provider(
        self,
        name: str,
        base_url: str | None = None,
        model: str | None = None,
        login_url: str | None = None,
        login_instructions: list[str] | None = None,
        display_name: str | None = None,
        extra_aliases: list[str] | None = None,
        api_key: str | None = None,
        base_url_env: str | None = None,
    ) -> tuple[bool, str]:
        """Update an existing provider.

        Args:
            name: Provider name.
            base_url: New base URL (optional).
            model: New default model (optional).
            login_url: New login URL (optional).
            login_instructions: New login instructions (optional).
            display_name: New display name (optional).
            extra_aliases: New aliases (optional).
            api_key: New API key (optional).
            base_url_env: New env var name (optional).

        Returns:
            Tuple of (success: bool, message: str).
        """
        ...

    def delete_provider(self, name: str, remove_credentials: bool = True) -> tuple[bool, str]:
        """Delete a provider.

        Args:
            name: Provider name.
            remove_credentials: If True, also removes credentials.

        Returns:
            Tuple of (success: bool, message: str).
        """
        ...


__all__ = [
    "ProviderPort",
]
