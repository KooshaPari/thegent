"""
Shared Configuration Library
=============================

Centralized configuration management for Phenotype ecosystem.

## Features

- Environment-specific configuration loading
- Schema validation (Pydantic)
- Secrets management integration
- Multi-format support (YAML, TOML, ENV)

## Usage

```python
from libs.shared.config import Config, ConfigLoader

# Load from environment
config = ConfigLoader.load()

# Validate schema
validated = ConfigSchema(**config.data)
```

## Architecture

- ``base.py`` - Base configuration classes
- ``loader.py`` - Multi-format file loading
- ``schema.py`` - Pydantic validation schemas
- ``secrets.py`` - Secrets integration

## Design Principles

- **Single Responsibility**: Each module handles one config aspect
- **Dependency Inversion**: Config abstraction over concrete implementations
- **Open/Closed**: Extensible via plugins, not modification
"""

from typing import Any, Dict, Optional, Type, TypeVar
from dataclasses import dataclass, field
from pathlib import Path
import os
import yaml
import json
import tomli

T = TypeVar('T', bound='BaseConfig')


@dataclass
class BaseConfig:
    """Base configuration with environment override support."""

    env_prefix: str = "PHENOTYPE"
    _data: Dict[str, Any] = field(default_factory=dict, repr=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with dot-notation support."""
        keys = key.split('.')
        value = self._data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def set(self, key: str, value: Any) -> None:
        """Set configuration value with dot-notation support."""
        keys = key.split('.')
        data = self._data
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        data[keys[-1]] = value

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return self._data.copy()


class ConfigLoader:
    """Multi-format configuration loader with schema validation."""

    SUPPORTED_FORMATS = {'.yaml', '.yml', '.json', '.toml', '.env'}

    @classmethod
    def load(
        cls,
        path: Optional[Path] = None,
        env: Optional[str] = None,
        schema: Optional[Type[T]] = None,
    ) -> BaseConfig | T:
        """Load configuration from file and environment.

        Args:
            path: Configuration file path
            env: Environment name (development, staging, production)
            schema: Pydantic schema for validation

        Returns:
            Validated configuration object
        """
        config = BaseConfig()

        # Load from file if provided
        if path and path.exists():
            config._data = cls._load_file(path)

        # Override with environment variables
        config._data = cls._apply_env_overrides(config._data)

        # Apply environment-specific overrides
        if env:
            config._data = cls._apply_env_specific(config._data, env)

        # Validate against schema if provided
        if schema:
            return schema(**config._data)

        return config

    @classmethod
    def _load_file(cls, path: Path) -> Dict[str, Any]:
        """Load configuration from file."""
        suffix = path.suffix.lower()

        if suffix not in cls.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {suffix}")

        with open(path, 'r') as f:
            if suffix in {'.yaml', '.yml'}:
                return yaml.safe_load(f) or {}
            elif suffix == '.json':
                return json.load(f)
            elif suffix == '.toml':
                return tomli.load(f)
            else:
                return {}

    @classmethod
    def _apply_env_overrides(cls, data: Dict[str, Any], prefix: str = "PHENOTYPE") -> Dict[str, Any]:
        """Apply environment variable overrides."""
        result = data.copy()
        prefix_upper = prefix.upper()

        for key, value in os.environ.items():
            if key.startswith(f"{prefix_upper}_"):
                config_key = key[len(prefix_upper) + 1:].lower().replace('_', '.')
                keys = config_key.split('.')
                current = result
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                current[keys[-1]] = cls._parse_env_value(value)

        return result

    @classmethod
    def _apply_env_specific(cls, data: Dict[str, Any], env: str) -> Dict[str, Any]:
        """Apply environment-specific configuration overrides."""
        result = data.copy()

        if 'environments' in result and env in result['environments']:
            env_config = result['environments'][env]
            result.update(env_config)

        return result

    @classmethod
    def _parse_env_value(cls, value: str) -> Any:
        """Parse environment variable value to appropriate type."""
        # Boolean parsing
        if value.lower() in ('true', 'yes', '1'):
            return True
        if value.lower() in ('false', 'no', '0'):
            return False

        # None parsing
        if value.lower() == 'none':
            return None

        # Number parsing
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        return value


class SecretsManager:
    """Secrets management integration (Vault, AWS SM, etc.)."""

    def __init__(self, backend: str = "env"):
        self.backend = backend

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieve secret value."""
        env_key = f"SECRET_{key.upper().replace('.', '_')}"
        return os.environ.get(env_key, default)

    def set(self, key: str, value: str) -> None:
        """Set secret value."""
        env_key = f"SECRET_{key.upper().replace('.', '_')}"
        os.environ[env_key] = value
