"""STUB MODULE - thegent.config_provider

WARNING: This is an auto-generated stub module.
The actual implementation was moved/deleted during repository restructuring.
This stub exists for backwards compatibility with existing tests.
"""

from __future__ import annotations

import os
from typing import Any


# Global provider instance
_provider_instance: "EnvConfigProvider | None" = None
_last_provider_metadata: dict[str, Any] = {}


class EnvConfigProvider:
    """Environment-based configuration provider."""

    def __init__(self) -> None:
        """Initialize the environment config provider."""
        self._base_config: dict[str, Any] = {
            "default_timeout": 300,
            "default_timeout_claude": 180,
            "session_dir": os.path.expanduser("~/.thegent/sessions"),
            "log_level": "INFO",
            "max_retries": 3,
        }

    def resolve(
        self,
        keys: list[str] | None = None,
        request_overrides: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Resolve configuration values.

        Args:
            keys: Optional list of specific keys to resolve.
            request_overrides: Optional overrides for the request.

        Returns:
            Dictionary of resolved configuration values.
        """
        config = self._base_config.copy()

        # Apply environment variable overrides
        for key, env_var in [
            ("default_timeout", "THGENT_TIMEOUT"),
            ("session_dir", "THGENT_SESSION_DIR"),
            ("log_level", "THGENT_LOG_LEVEL"),
        ]:
            if env_var in os.environ:
                config[key] = os.environ[env_var]

        # Apply request overrides
        if request_overrides:
            config.update(request_overrides)

        # Filter by keys if specified
        if keys:
            config = {k: v for k, v in config.items() if k in keys}

        return config

    def get_tenant_config(self, tenant_id: str) -> dict[str, Any] | None:
        """Get tenant-specific configuration.

        Args:
            tenant_id: The tenant identifier.

        Returns:
            Tenant configuration dict or None if not found.
        """
        return None


def get_config_provider() -> EnvConfigProvider:
    """Get the global configuration provider instance.

    Returns:
        The global EnvConfigProvider instance.
    """
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = EnvConfigProvider()
    return _provider_instance


def get_last_provider_metadata() -> dict[str, Any]:
    """Get metadata about the last provider operation.

    Returns:
        Dictionary containing metadata about the last operation.
    """
    return _last_provider_metadata.copy()


# Re-export the module for convenience
__all__ = ["EnvConfigProvider", "get_config_provider", "get_last_provider_metadata"]
