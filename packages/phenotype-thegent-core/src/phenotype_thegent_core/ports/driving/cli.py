"""CLIPort: Interface for CLI adapter to invoke use cases."""

from __future__ import annotations

from typing import Any, Protocol


class CLIPort(Protocol):
    """Port interface that CLI adapters use to invoke provider/model use cases."""

    def handle_list_providers(self, *, include_credentials: bool = False) -> None:
        """Handle CLI request to list providers.

        Args:
            include_credentials: If True, include sensitive credential info.
        """
        ...

    def handle_add_provider(
        self,
        name: str,
        base_url: str,
        model: str,
        **kwargs: Any,
    ) -> None:
        """Handle CLI request to add a provider.

        Args:
            name: Provider name.
            base_url: Provider base URL.
            model: Default model.
            **kwargs: Additional options (login_url, api_key, etc.).
        """
        ...

    def handle_update_provider(self, name: str, **kwargs: Any) -> None:
        """Handle CLI request to update a provider.

        Args:
            name: Provider name.
            **kwargs: Fields to update.
        """
        ...

    def handle_delete_provider(self, name: str, **kwargs: Any) -> None:
        """Handle CLI request to delete a provider.

        Args:
            name: Provider name.
            **kwargs: Additional options (remove_credentials, etc.).
        """
        ...

    def handle_list_models(self, *, provider: str | None = None) -> None:
        """Handle CLI request to list models.

        Args:
            provider: Optional provider to filter by.
        """
        ...

    def handle_discover_models(self, *, provider: str | None = None) -> None:
        """Handle CLI request to discover available models.

        Args:
            provider: Optional provider to filter by.
        """
        ...

    def handle_validate_provider(self, name: str) -> None:
        """Handle CLI request to validate a provider.

        Args:
            name: Provider name.
        """
        ...

    def handle_add_model_alias(self, provider: str, model: str, alias: str) -> None:
        """Handle CLI request to add a model alias.

        Args:
            provider: Provider name.
            model: Model name.
            alias: Alias to add.
        """
        ...

    def handle_remove_model_alias(self, provider: str, alias: str) -> None:
        """Handle CLI request to remove a model alias.

        Args:
            provider: Provider name.
            alias: Alias to remove.
        """
        ...

    def handle_add_api_key(self, provider: str, api_key: str) -> None:
        """Handle CLI request to add an API key.

        Args:
            provider: Provider name.
            api_key: API key to add.
        """
        ...

    def handle_remove_api_key(self, provider: str) -> None:
        """Handle CLI request to remove an API key.

        Args:
            provider: Provider name.
        """
        ...


__all__ = [
    "CLIPort",
]
