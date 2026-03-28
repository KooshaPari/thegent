"""
Hierarchical Configuration Resolution.

Implements environment-specific overrides following ADR-001 patterns.
Supports loading from multiple sources with proper precedence.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Union

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class ResolutionError(Exception):
    """Raised when configuration resolution fails."""
    pass


@dataclass
class ConfigSource:
    """Tracks the source of a configuration value."""

    name: str
    priority: int
    value: Any


class ConfigResolver:
    """Resolves configuration with hierarchical override precedence.

    Resolution order (later sources override earlier):
        1. Base defaults
        2. Repository defaults (defaults/)
        3. Environment-specific (environments/{env}.yaml)
        4. Local overrides (config.local.yaml)
        5. Environment variables (PREFIX_FIELD_SUBFORMAT)
        6. Runtime overrides (passed directly)

    Args:
        base_defaults: Base configuration dictionary
        env: Target environment name (e.g., 'development', 'production')
        prefix: Environment variable prefix
    """

    def __init__(
        self,
        base_defaults: Optional[dict[str, Any]] = None,
        env: str = "development",
        prefix: str = "APP",
    ):
        self.base_defaults = base_defaults or {}
        self.env = env
        self.prefix = prefix
        self._sources: dict[str, dict[str, Any]] = {
            "defaults": base_defaults.copy() if base_defaults else {}
        }
        self._source_order: list[str] = ["defaults"]
        self._overrides: dict[str, Any] = {}
        self._required_keys: set[str] = set()

    def load_defaults(self, defaults: dict[str, Any]) -> "ConfigResolver":
        """Load repository-level defaults.

        Args:
            defaults: Default configuration dictionary

        Returns:
            Self for chaining
        """
        self._sources["repository_defaults"] = defaults.copy()
        self._source_order.append("repository_defaults")
        return self

    def load_file(
        self,
        path: Union[str, Path],
        source_name: Optional[str] = None,
    ) -> "ConfigResolver":
        """Load configuration from a file.

        Supports JSON, YAML, and TOML formats.

        Args:
            path: Path to the configuration file
            source_name: Optional name for this source (defaults to filename)

        Returns:
            Self for method chaining
        """
        path = Path(path)
        if not path.exists():
            return self

        source_name = source_name or f"file:{path.name}"
        suffix = path.suffix.lower()

        data = {}
        try:
            with open(path, 'r') as f:
                if suffix in ('.json',):
                    data = json.load(f)
                elif suffix in ('.yaml', '.yml') and HAS_YAML:
                    data = yaml.safe_load(f) or {}
        except Exception as e:
            raise ResolutionError(f"Failed to load config from {path}: {e}")

        self._sources[source_name] = data
        self._source_order.append(source_name)
        return self

    def load_environment(self, env_config: dict[str, Any]) -> "ConfigResolver":
        """Load environment-specific configuration.

        Args:
            env_config: Environment configuration dictionary

        Returns:
            Self for chaining
        """
        self._sources[f"environment_{self.env}"] = env_config.copy()
        self._source_order.append(f"environment_{self.env}")
        return self

    def load_local(self, local_config: dict[str, Any]) -> "ConfigResolver":
        """Load local override configuration.

        Args:
            local_config: Local override dictionary

        Returns:
            Self for chaining
        """
        self._sources["local"] = local_config.copy()
        self._source_order.append("local")
        return self

    def override(self, key: str, value: Any) -> "ConfigResolver":
        """Add a runtime override.

        Args:
            key: Configuration key in SUBFORMAT (e.g., 'database.host')
            value: Override value

        Returns:
            Self for chaining
        """
        self._overrides[key] = value
        return self

    def override_from_env(self, env_vars: Optional[dict[str, str]] = None) -> "ConfigResolver":
        """Apply environment variable overrides.

        Environment variables use PREFIX_ prefix and SUBFORMAT naming:
            APP_DATABASE__HOST -> database.host
            APP_LOG_LEVEL -> log.level

        Args:
            env_vars: Dictionary of environment variables (defaults to os.environ)

        Returns:
            Self for chaining
        """
        env_vars = env_vars or dict(os.environ)
        prefix = f"{self.prefix}_"
        separator = "__"  # Double underscore for nested keys

        for env_key, env_value in env_vars.items():
            if not env_key.startswith(prefix):
                continue

            # Strip prefix and convert separators
            key = env_key[len(prefix):].lower()
            key = key.replace(separator, ".")

            # Type inference
            value = self._parse_env_value(env_value)
            self._overrides[key] = value

        return self

    def require(self, *keys: str) -> "ConfigResolver":
        """Mark keys as required.

        Args:
            keys: Configuration keys that must be present

        Returns:
            Self for chaining
        """
        self._required_keys.update(keys)
        return self

    def resolve(self) -> dict[str, Any]:
        """Resolve final configuration using override precedence.

        Returns:
            Fully resolved configuration dictionary

        Raises:
            ResolutionError: If a required key cannot be resolved
        """
        result: dict[str, Any] = {}

        # Merge in precedence order (later overwrites earlier)
        for source_name in self._source_order:
            if source_name in self._sources:
                self._deep_merge(result, self._sources[source_name])

        # Apply environment variables/overrides
        if self._overrides:
            self._deep_merge(result, self._overrides)

        # Check for unresolved required keys
        self._validate_required(result)

        return result

    def _deep_merge(self, target: dict[str, Any], source: dict[str, Any]) -> None:
        """Recursively merge source into target.

        Args:
            target: Target dictionary (modified in place)
            source: Source dictionary to merge
        """
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value

    def _validate_required(self, config: dict[str, Any]) -> None:
        """Validate that required keys are present.

        Args:
            config: Resolved configuration

        Raises:
            ResolutionError: If a required key is missing
        """
        for key in self._required_keys:
            if self._get_nested(config, key) is None:
                raise ResolutionError(f"Required configuration key '{key}' is missing")

    def _get_nested(self, data: dict[str, Any], key: str) -> Optional[Any]:
        """Get nested configuration value using dot notation.

        Args:
            data: Configuration dictionary
            key: Dot-separated key path (e.g., 'database.host')

        Returns:
            Value if found, None otherwise
        """
        keys = key.split(".")
        current = data

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None

        return current

    def _parse_env_value(self, value: str) -> Any:
        """Parse environment variable string to appropriate type."""
        # Boolean
        if value.lower() in ("true", "false"):
            return value.lower() == "true"

        # None
        if value.lower() in ("none", "null"):
            return None

        # Number
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        # Return as string
        return value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a resolved configuration value.

        Args:
            key: Dot-separated key path
            default: Default value if not found

        Returns:
            Resolved value or default
        """
        config = self.resolve()
        value = self._get_nested(config, key)
        return value if value is not None else default

    def sources(self) -> dict[str, ConfigSource]:
        """Get information about where each config value came from."""
        result = {}
        resolved = self.resolve()

        for key, value in self._flatten_dict(resolved).items():
            # Find the source
            for source_name in self._source_order:
                if source_name in self._sources:
                    source_value = self._get_nested(self._sources[source_name], key)
                    if source_value is not None:
                        result[key] = ConfigSource(
                            name=source_name,
                            priority=self._source_order.index(source_name),
                            value="[OVERRIDDEN]" if key in self._overrides else value
                        )
                        break

            # Check overrides
            if key in self._overrides:
                result[key] = ConfigSource(
                    name="environment/override",
                    priority=len(self._source_order),
                    value=value
                )

        return result

    def _flatten_dict(
        self,
        d: dict[str, Any],
        parent_key: str = "",
        sep: str = ".",
    ) -> dict[str, Any]:
        """Flatten a nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)


class EnvironmentConfigResolver(ConfigResolver):
    """
    ConfigResolver with automatic environment detection.

    Automatically determines environment from PREFIX_ENV or PREFIX_ENVIRONMENT.
    """

    def __init__(self, base_defaults: Optional[dict[str, Any]] = None, prefix: str = "APP"):
        env = os.environ.get(f"{prefix}_ENV") or os.environ.get(f"{prefix}_ENVIRONMENT", "development")
        super().__init__(base_defaults, env, prefix)

    def auto_load_config_files(self, base_path: Optional[Path] = None) -> "EnvironmentConfigResolver":
        """Automatically load config files based on environment.

        Loads:
        - config.json (base)
        - config.{env}.json (environment-specific)
        - config.local.json (local overrides)

        Args:
            base_path: Base directory for config files

        Returns:
            Self for method chaining
        """
        base_path = base_path or Path.cwd()

        # Load base config
        base_config = base_path / "config.json"
        if base_config.exists():
            self.load_file(base_config, "config")

        # Load environment-specific config
        env_config = base_path / f"config.{self.env}.json"
        if env_config.exists():
            self.load_file(env_config, f"config.{self.env}")

        # Load local overrides
        local_config = base_path / "config.local.json"
        if local_config.exists():
            self.load_file(local_config, "config.local")

        return self
