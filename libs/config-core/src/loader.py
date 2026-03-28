"""Base configuration loader with environment variable support."""

import os
from typing import Any, Dict, Optional


class BaseConfigLoader:
    """Base configuration loader using environment variables.

    Provides type-safe getters for configuration values with
    support for defaults and required fields.
    """

    def __init__(self, prefix: str = ""):
        """Initialize loader with optional prefix for env vars.

        Args:
            prefix: Prefix for environment variables (e.g., 'APP' -> 'APP_PORT')
        """
        self.prefix = prefix.upper()
        self._required_fields: list[str] = []
        self._config: Dict[str, Any] = {}

    def _env_key(self, key: str) -> str:
        """Build full environment variable name."""
        if self.prefix:
            return f"{self.prefix}_{key.upper()}"
        return key.upper()

    def get_str(self, key: str, default: Optional[str] = None) -> str:
        """Get string configuration value."""
        value = os.environ.get(self._env_key(key), default)
        if value is None:
            raise ValueError(f"Required config '{key}' is missing")
        return value

    def get_int(self, key: str, default: Optional[int] = None) -> int:
        """Get integer configuration value."""
        raw = os.environ.get(self._env_key(key))
        if raw is None and default is not None:
            return default
        if raw is None:
            raise ValueError(f"Required config '{key}' is missing")
        try:
            return int(raw)
        except ValueError:
            raise ValueError(f"Config '{key}' must be an integer")

    def get_bool(self, key: str, default: Optional[bool] = None) -> bool:
        """Get boolean configuration value."""
        raw = os.environ.get(self._env_key(key))
        if raw is None and default is not None:
            return default
        if raw is None:
            raise ValueError(f"Required config '{key}' is missing")
        return raw.lower() in ("true", "1", "yes", "on")

    def get_required(self, *keys: str) -> None:
        """Declare required configuration keys."""
        self._required_fields.extend(keys)

    def validate(self) -> None:
        """Validate all required fields are present.

        Override in subclass to add custom validation logic.
        """
        for key in self._required_fields:
            if os.environ.get(self._env_key(key)) is None:
                raise ValueError(f"Required config '{key}' is missing")
