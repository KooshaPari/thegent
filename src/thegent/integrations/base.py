"""Base classes and utilities for integrations.

Provides standard patterns for:
- Configuration loading
- Status tracking
- Enable/disable toggles
- Feature flags
"""

from __future__ import annotations

import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, fields
from enum import StrEnum
from pathlib import Path
from typing import Any, TypeVar

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


# ---------------------------------------------------------------------------
# Feature Flag System
# ---------------------------------------------------------------------------

class FeatureFlag:
    """Simple feature flag with environment variable support.
    
    Usage:
        FLAG = FeatureFlag("MY_FEATURE", default=False)
        
        if FLAG.enabled:
            ...
    """
    
    def __init__(self, name: str, default: bool = False, env_prefix: str = "THEGENT_"):
        self.name = name
        self._default = default
        self._env_key = f"{env_prefix}ENABLE_{name}"
    
    @property
    def enabled(self) -> bool:
        """Check if feature is enabled via environment variable."""
        val = os.environ.get(self._env_key, "")
        if val:
            return val.lower() in ("1", "true", "yes", "on")
        return self._default
    
    def __bool__(self) -> bool:
        return self.enabled


class FeatureRegistry:
    """Registry for all feature flags."""
    
    _flags: dict[str, FeatureFlag] = {}
    
    @classmethod
    def register(cls, flag: FeatureFlag) -> None:
        cls._flags[flag.name] = flag
    
    @classmethod
    def get(cls, name: str) -> FeatureFlag | None:
        return cls._flags.get(name)
    
    @classmethod
    def all_enabled(cls) -> dict[str, bool]:
        return {name: flag.enabled for name, flag in cls._flags.items()}


def feature(name: str, default: bool = False) -> FeatureFlag:
    """Create and register a feature flag."""
    flag = FeatureFlag(name, default)
    FeatureRegistry.register(flag)
    return flag


# ---------------------------------------------------------------------------
# Serializable Mixin
# ---------------------------------------------------------------------------

class SerializableMixin:
    """Mixin providing to_dict/from_dict for dataclasses.
    
    Usage:
        @dataclass
        class MyModel(SerializableMixin):
            name: str
            value: int = 0
        
        m = MyModel(name="test", value=42)
        d = m.to_dict()  # {"name": "test", "value": 42}
        m2 = MyModel.from_dict(d)  # MyModel(name="test", value=42)
    """
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        if hasattr(self, '__dataclass_fields__'):
            return asdict(self)
        # Fallback for non-dataclass
        result = {}
        if hasattr(self.__class__, '__dataclass_fields__'):
            for f in fields(self.__class__):
                val = getattr(self, f.name, None)
                result[f.name] = val
        return result
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SerializableMixin":
        """Create instance from dictionary."""
        if hasattr(cls, '__dataclass_fields__'):
            field_names = {f.name for f in fields(cls)}
            filtered = {k: v for k, v in data.items() if k in field_names}
            return cls(**filtered)
        return cls(**data)


# ---------------------------------------------------------------------------
# Config Loading Utilities
# ---------------------------------------------------------------------------

def load_env_config(prefix: str, defaults: dict[str, Any] | None = None) -> dict[str, Any]:
    """Load configuration from environment variables with prefix.
    
    Args:
        prefix: Environment variable prefix (e.g., "MYAPP_")
        defaults: Default values for config keys
        
    Returns:
        Dict with config values from env (with type conversion)
    """
    config = dict(defaults) if defaults else {}
    
    for key, default_val in (defaults or {}).items():
        env_key = f"{prefix}{key.upper()}"
        env_val = os.environ.get(env_key)
        
        if env_val is not None:
            if isinstance(default_val, bool):
                config[key] = env_val.lower() in ("1", "true", "yes", "on")
            elif isinstance(default_val, int):
                config[key] = int(env_val)
            elif isinstance(default_val, float):
                config[key] = float(env_val)
            elif isinstance(default_val, list):
                config[key] = [s.strip() for s in env_val.split(",")]
            else:
                config[key] = env_val
    
    return config


def load_file_config(path: Path | str, defaults: dict[str, Any] | None = None) -> dict[str, Any]:
    """Load configuration from JSON or YAML file.
    
    Args:
        path: Path to config file (.json, .yaml, .yml)
        defaults: Default values
        
    Returns:
        Merged config dict
    """
    config = dict(defaults) if defaults else {}
    config_path = Path(path)
    
    if not config_path.exists():
        return config
    
    try:
        content = config_path.read_text()
        
        if config_path.suffix == ".json":
            data = json.loads(content)
        elif config_path.suffix in (".yaml", ".yml"):
            try:
                import yaml
                data = yaml.safe_load(content) or {}
            except ImportError:
                _log.warning("PyYAML not installed, skipping YAML config")
                return config
        else:
            return config
        
        if isinstance(data, dict):
            config.update(data)
            
    except (json.JSONDecodeError, OSError, ValueError) as e:
        _log.warning(f"Failed to load config from {path}: {e}")
    
    return config


# ---------------------------------------------------------------------------
# Dataclass Config Base
# ---------------------------------------------------------------------------

@dataclass
class DataclassConfig:
    """Base dataclass config with env loading support.

    Inherit from this for dataclass-based configs:
        @dataclass
        class MyConfig(DataclassConfig):
            base_url: str = "http://localhost"
            api_key: str = ""
    """

    enabled: bool = False

    @classmethod
    def from_env(cls, prefix: str = "") -> "DataclassConfig":
        """Load config from environment variables."""
        env_values: dict[str, Any] = {}

        for f in fields(cls):
            env_key = f"{prefix}{f.name.upper()}"
            env_val = os.environ.get(env_key)

            if env_val is not None and f.default is not None:
                field_type = type(f.default)
                if field_type == bool:
                    env_values[f.name] = env_val.lower() in ("1", "true", "yes")
                elif field_type == int:
                    env_values[f.name] = int(env_val)
                elif field_type == float:
                    env_values[f.name] = float(env_val)
                elif field_type == list:
                    env_values[f.name] = [s.strip() for s in env_val.split(",")]
                else:
                    env_values[f.name] = env_val

        return cls(**env_values)


# ---------------------------------------------------------------------------
# Base Integration Class
# ---------------------------------------------------------------------------

class BaseIntegration(ABC):
    """Base class for integrations with standard lifecycle."""

    def __init__(self, name: str, config: DataclassConfig | None = None) -> None:
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
    "DataclassConfig",
    "FeatureFlag",
    "FeatureRegistry",
    "IntegrationInfo",
    "IntegrationStatus",
    "SerializableMixin",
    "feature",
    "load_env_config",
    "load_file_config",
]
