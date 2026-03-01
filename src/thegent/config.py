"""Pydantic settings for thegent.

DEPRECATED: This module is maintained for backward compatibility.
New code should import from thegent.config.settings instead.

The configuration has been split into logical modules for maintainability:
- thegent.config.model_config: Model selection and routing
- thegent.config.path_config: Filesystem paths and directories
- thegent.config.runtime_config: Sandbox, budgets, retention, execution
- thegent.config.settings: Composite ThegentSettings class
"""

import warnings

# Re-export the main settings class and helper function from the new location
from thegent.config.settings import ThegentSettings, get_settings

# Re-export the component configs for advanced users
from thegent.config.model_config import ModelConfig
from thegent.config.path_config import PathConfig
from thegent.config.runtime_config import RuntimeConfig

__all__ = [
    "ThegentSettings",
    "ModelConfig",
    "PathConfig",
    "RuntimeConfig",
    "get_settings",
]

# Issue deprecation warning on import
warnings.warn(
    "Importing from thegent.config is deprecated. "
    "Please import from thegent.config.settings instead, or from thegent.config.* for specific configs.",
    DeprecationWarning,
    stacklevel=2,
)
