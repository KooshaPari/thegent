"""thegent-config: Configuration schemas, validation, loading, and defaults for thegent.

This package contains all configuration logic extracted from the thegent monolith:
- ThegentSettings: Composite pydantic-settings class
- ModelConfig, PathConfig, RuntimeConfig: Domain-specific config classes
- ConfigManager: JSON file config management
- Defaults, parsers, validators: Shared utilities
"""

from thegent_config.settings import ThegentSettings, get_settings
from thegent_config.model_config import ModelConfig
from thegent_config.path_config import PathConfig
from thegent_config.runtime_config import RuntimeConfig
from thegent_config.manager import ConfigManager, ConfigLoadError

__all__ = [
    "ConfigLoadError",
    "ConfigManager",
    "ModelConfig",
    "PathConfig",
    "RuntimeConfig",
    "ThegentSettings",
    "get_settings",
]
