"""Base classes and utilities for integrations.

Provides standard patterns for:
- Configuration loading
- Status tracking
- Enable/disable toggles
"""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

_log = logging.getLogger(__name__)


class IntegrationStatus(StrEnum):
    """Standard integration status values."""

    UNKNOWN = "unknown"
    DISABLED = "disabled"
    ENABLED = "enabled"
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


@dataclass
class IntegrationInfo:
    """Basic integration metadata."""

    name: str
    description: str = ""
    version: str = "1.0.0"
    status: IntegrationStatus = IntegrationStatus.UNKNOWN
    enabled: bool = False
    error: str | None = None


T = TypeVar("T", bound=BaseModel)


class BaseIntegrationConfig(BaseModel, Generic[T]):
    """Base configuration for integrations using Pydantic.

    Usage:
        class MyConfig(BaseIntegrationConfig):
            base_url: str = "http://localhost"
            api_key: str = ""
            timeout: float = 30.0
    """

    enabled: bool = False

    @classmethod
    def from_env(cls, prefix: str = "") -> "T":
        """Load config from environment variables.

        Args:
            prefix: Env var prefix (e.g., "MYAPP_")

        Returns:
            Config instance with values from env
        """
        env_values: dict[str, Any] = {}

        for field_name, field_info in cls.model_fields.items():
            env_key = f"{prefix}{field_name.upper()}"
            env_val = os.environ.get(env_key)

            if env_val is not None:
                # Convert to appropriate type
                field_type = field_info.annotation
                if field_type == bool:
                    env_values[field_name] = env_val.lower() in ("1", "true", "yes")
                elif field_type == int:
                    env_values[field_name] = int(env_val)
                elif field_type == float:
                    env_values[field_name] = float(env_val)
                else:
                    env_values[field_name] = env_val

        return cls(**env_values)

    @classmethod
    def from_file(cls, path: Path | str) -> "T | None":
        """Load config from JSON file.

        Args:
            path: Path to config file

        Returns:
            Config instance or None if file doesn't exist
        """
        config_path = Path(path)
        if not config_path.exists():
            return None

        try:
            import json

            data = json.loads(config_path.read_text())
            return cls(**data)
        except (json.JSONDecodeError, OSError, ValueError) as e:
            _log.warning(f"Failed to load config from {path}: {e}")
            return None


class BaseIntegration(ABC):
    """Base class for integrations with standard lifecycle."""

    def __init__(self, name: str, config: BaseIntegrationConfig | None = None) -> None:
        self.name = name
        self._config = config
        self._status = IntegrationStatus.UNKNOWN
        self._error: str | None = None

    @property
    def status(self) -> IntegrationStatus:
        """Current integration status."""
        return self._status

    @property
    def enabled(self) -> bool:
        """Whether integration is enabled."""
        return self._config.enabled if self._config else False

    @property
    def error(self) -> str | None:
        """Last error message, if any."""
        return self._error

    @abstractmethod
    def check_available(self) -> bool:
        """Check if integration is available."""
        ...

    @abstractmethod
    def connect(self) -> bool:
        """Connect to integration."""
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from integration."""
        ...

    def enable(self) -> None:
        """Enable integration."""
        if self._config:
            self._config.enabled = True

    def disable(self) -> None:
        """Disable integration."""
        if self._config:
            self._config.enabled = False

    def get_info(self) -> IntegrationInfo:
        """Get integration metadata."""
        return IntegrationInfo(
            name=self.name,
            status=self._status,
            enabled=self.enabled,
            error=self._error,
        )


__all__ = [
    "BaseIntegration",
    "BaseIntegrationConfig",
    "IntegrationInfo",
    "IntegrationStatus",
]
