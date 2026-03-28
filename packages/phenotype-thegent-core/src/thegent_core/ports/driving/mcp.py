"""MCPPort: Interface for MCP adapter to invoke use cases."""

from __future__ import annotations

from typing import Any, Protocol


class MCPPort(Protocol):
    """Port interface that MCP adapters use to invoke provider/model use cases."""

    def get_providers(self, *, include_credentials: bool = False) -> dict[str, Any]:
        """Get all configured providers for MCP response.

        Args:
            include_credentials: If True, include sensitive credential info.

        Returns:
            Dict with provider data for MCP response.
        """
        ...

    def add_provider(
        self,
        name: str,
        base_url: str,
        model: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Add a provider and return result for MCP response.

        Args:
            name: Provider name.
            base_url: Provider base URL.
            model: Default model.
            **kwargs: Additional options.

        Returns:
            Dict with success/error info for MCP response.
        """
        ...

    def update_provider(self, name: str, **kwargs: Any) -> dict[str, Any]:
        """Update a provider and return result for MCP response.

        Args:
            name: Provider name.
            **kwargs: Fields to update.

        Returns:
            Dict with success/error info for MCP response.
        """
        ...

    def delete_provider(self, name: str, **kwargs: Any) -> dict[str, Any]:
        """Delete a provider and return result for MCP response.

        Args:
            name: Provider name.
            **kwargs: Additional options.

        Returns:
            Dict with success/error info for MCP response.
        """
        ...

    def get_models(self, *, provider: str | None = None) -> dict[str, Any]:
        """Get models for MCP response.

        Args:
            provider: Optional provider to filter by.

        Returns:
            Dict with model data for MCP response.
        """
        ...

    def discover_models(self, *, provider: str | None = None) -> dict[str, Any]:
        """Discover available models for MCP response.

        Args:
            provider: Optional provider to filter by.

        Returns:
            Dict with model discovery results for MCP response.
        """
        ...

    def validate_provider(self, name: str) -> dict[str, Any]:
        """Validate a provider and return result for MCP response.

        Args:
            name: Provider name.

        Returns:
            Dict with validation results for MCP response.
        """
        ...

    def get_provider_info(self, name: str) -> dict[str, Any]:
        """Get detailed provider information for MCP response.

        Args:
            name: Provider name.

        Returns:
            Dict with provider details for MCP response.
        """
        ...

    def add_model_alias(self, provider: str, model: str, alias: str) -> dict[str, Any]:
        """Add a model alias and return result for MCP response.

        Args:
            provider: Provider name.
            model: Model name.
            alias: Alias to add.

        Returns:
            Dict with success/error info for MCP response.
        """
        ...

    def remove_model_alias(self, provider: str, alias: str) -> dict[str, Any]:
        """Remove a model alias and return result for MCP response.

        Args:
            provider: Provider name.
            alias: Alias to remove.

        Returns:
            Dict with success/error info for MCP response.
        """
        ...


__all__ = [
    "MCPPort",
]
