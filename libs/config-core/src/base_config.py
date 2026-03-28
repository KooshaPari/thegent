"""
Environment-based Configuration Management.

Provides type-safe configuration loading from environment variables,
following ADR-001 patterns for the Phenotype ecosystem.
"""

import os
import re
from dataclasses import dataclass, field
from typing import Any, Optional, TypeVar, Callable
from pathlib import Path

T = TypeVar('T')


class ConfigError(Exception):
    """Base exception for configuration errors."""
    pass


class RequiredConfigMissingError(ConfigError):
    """Raised when a required configuration value is missing."""

    def __init__(self, key: str, env_key: str):
        self.key = key
        self.env_key = env_key
        super().__init__(
            f"Required configuration '{key}' is not set. "
            f"Set the environment variable {env_key}"
        )


class ConfigTypeError(ConfigError):
    """Raised when a configuration value has an invalid type."""

    def __init__(self, key: str, expected: type, actual: Any):
        self.key = key
        self.expected = expected
        self.actual = actual
        super().__init__(
            f"Configuration '{key}' has invalid type. "
            f"Expected {expected.__name__}, got {type(actual).__name__}"
        )


class Secret:
    """
    Wrapper for secret values that prevents accidental logging.

    The actual value is hidden when the object is printed or repr'd.
    """

    def __init__(self, value: str):
        self._value = value

    def __repr__(self) -> str:
        return "***"

    def __str__(self) -> str:
        return "***"

    def get(self) -> str:
        """Get the actual secret value."""
        return self._value


@dataclass
class BaseConfig:
    """
    Base configuration class with environment variable support.

    Subclass this to define your configuration with type-safe getters.

    Example:
        class AppConfig(BaseConfig):
            _env_prefix = "APP"

            def __init__(self):
                self.port = self.get_int("PORT", default=8080)
                self.debug = self.get_bool("DEBUG", default=False)
                self.secret = self.get_secret("API_SECRET")

        config = AppConfig.from_env()
    """

    _env_prefix: str = field(default="APP", repr=False)
    _required_keys: list[str] = field(default_factory=list, repr=False)

    def _env_key(self, key: str) -> str:
        """Build the environment variable name."""
        prefix = getattr(self, '_env_prefix', 'APP')
        return f"{prefix}_{key.upper()}"

    def get(self, key: str, default: Any = None) -> Any:
        """Get a raw configuration value from environment."""
        env_key = self._env_key(key)
        return os.environ.get(env_key, default)

    def get_str(self, key: str, default: Optional[str] = None) -> str:
        """Get a string configuration value."""
        value = self.get(key)
        if value is None:
            if default is not None:
                return str(default)
            raise RequiredConfigMissingError(key, self._env_key(key))
        return value

    def get_int(self, key: str, default: Optional[int] = None) -> int:
        """Get an integer configuration value."""
        value = self.get(key)
        if value is None:
            if default is not None:
                return int(default)
            raise RequiredConfigMissingError(key, self._env_key(key))

        try:
            return int(value)
        except ValueError:
            raise ConfigTypeError(key, int, value)

    def get_float(self, key: str, default: Optional[float] = None) -> float:
        """Get a float configuration value."""
        value = self.get(key)
        if value is None:
            if default is not None:
                return float(default)
            raise RequiredConfigMissingError(key, self._env_key(key))

        try:
            return float(value)
        except ValueError:
            raise ConfigTypeError(key, float, value)

    def get_bool(self, key: str, default: Optional[bool] = None) -> bool:
        """Get a boolean configuration value.

        True values: 'true', '1', 'yes', 'on', 'TRUE', 'YES', 'ON'
        False values: 'false', '0', 'no', 'off', 'FALSE', 'NO', 'OFF'
        """
        value = self.get(key)
        if value is None:
            if default is not None:
                return bool(default)
            raise RequiredConfigMissingError(key, self._env_key(key))

        value_lower = value.lower()
        if value_lower in ("true", "1", "yes", "on"):
            return True
        if value_lower in ("false", "0", "no", "off"):
            return False

        raise ConfigTypeError(key, bool, value)

    def get_list(
        self,
        key: str,
        separator: str = ",",
        default: Optional[list[str]] = None,
    ) -> list[str]:
        """Get a list configuration value (comma-separated)."""
        value = self.get(key)
        if value is None:
            if default is not None:
                return default
            raise RequiredConfigMissingError(key, self._env_key(key))

        return [item.strip() for item in value.split(separator) if item.strip()]

    def get_secret(self, key: str, default: Optional[str] = None) -> Secret:
        """Get a secret configuration value (value hidden in logs)."""
        value = self.get_str(key, default)
        return Secret(value)

    def get_required(self, *keys: str) -> None:
        """Declare required configuration keys for validation."""
        self._required_keys.extend(keys)

    def is_set(self, key: str) -> bool:
        """Check if a configuration key is set."""
        return self.get(key) is not None

    def validate(self) -> None:
        """Validate all required keys are present.

        Override this method to add custom validation logic.
        """
        for key in self._required_keys:
            if not self.is_set(key):
                raise RequiredConfigMissingError(key, self._env_key(key))

    @classmethod
    def from_env(cls) -> "BaseConfig":
        """Create a configuration instance from environment variables."""
        instance = cls()
        instance.validate()
        return instance

    def to_dict(self) -> dict[str, Any]:
        """Export all non-private configuration as a dictionary."""
        result = {}
        for key in dir(self):
            if key.startswith("_"):
                continue
            value = getattr(self, key)
            if callable(value):
                continue
            # Don't include Secret values by value
            if isinstance(value, Secret):
                result[key] = "[SECRET]"
            else:
                result[key] = value
        return result


@dataclass
class DatabaseConfig:
    """Common database configuration."""

    host: str = "localhost"
    port: int = 5432
    name: str = "phenotype"
    user: str = "postgres"
    password: Secret = field(default_factory=lambda: Secret(""))

    def connection_string(self) -> str:
        """Build a PostgreSQL connection string."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class RedisConfig:
    """Common Redis configuration."""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[Secret] = None
    ssl: bool = False

    def connection_string(self) -> str:
        """Build a Redis connection string."""
        auth = f":{self.password.get()}@" if self.password else ""
        ssl = "?ssl=true" if self.ssl else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}{ssl}"
