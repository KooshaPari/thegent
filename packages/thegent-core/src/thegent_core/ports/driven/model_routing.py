"""ModelRoutingPort: Interface for model selection and routing."""

from __future__ import annotations

from typing import Any, Protocol


class ModelRoutingPort(Protocol):
    """Port interface for model discovery and routing operations."""

    def discover_models(
        self,
        provider: str | None = None,
        *,
        include_status: bool = False,
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """Discover available models from provider APIs.

        Args:
            provider: Optional provider name to filter models.
            include_status: If True, includes discovery status/error information.

        Returns:
            List of model dicts, or dict with models and status if include_status=True.
        """
        ...

    def validate_provider(self, name: str) -> tuple[bool, str, dict[str, Any]]:
        """Validate a provider by testing connectivity.

        Args:
            name: Provider name.

        Returns:
            Tuple of (is_valid: bool, message: str, details: dict).
        """
        ...

    def list_models(self, provider: str | None = None) -> list[dict[str, Any]]:
        """List all models, optionally filtered by provider.

        Args:
            provider: Optional provider name to filter by.

        Returns:
            List of model configurations.
        """
        ...

    def add_model_alias(self, provider: str, model: str, alias: str) -> tuple[bool, str]:
        """Add a model alias for a provider.

        Args:
            provider: Provider name.
            model: Base model name.
            alias: The alias to add.

        Returns:
            Tuple of (success: bool, message: str).
        """
        ...

    def remove_model_alias(self, provider: str, alias: str) -> tuple[bool, str]:
        """Remove a model alias from a provider.

        Args:
            provider: Provider name.
            alias: The alias to remove.

        Returns:
            Tuple of (success: bool, message: str).
        """
        ...

    def add_common_alias(self, alias: str) -> tuple[bool, str]:
        """Add a common model alias that works across providers.

        Args:
            alias: The alias to add.

        Returns:
            Tuple of (success: bool, message: str).
        """
        ...

    def remove_common_alias(self, alias: str) -> tuple[bool, str]:
        """Remove a common model alias.

        Args:
            alias: The alias to remove.

        Returns:
            Tuple of (success: bool, message: str).
        """
        ...


__all__ = [
    "ModelRoutingPort",
]
