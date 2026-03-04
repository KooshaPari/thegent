"""Pydantic settings for thegent.

DEPRECATED: This module is maintained for backward compatibility.
New code should import from thegent_config or thegent.config.settings instead.
"""

import warnings

from thegent_config import ThegentSettings, get_settings
from thegent_config.model_config import ModelConfig
from thegent_config.path_config import PathConfig
from thegent_config.runtime_config import RuntimeConfig

__all__ = [
    "ThegentSettings",
    "ModelConfig",
    "PathConfig",
    "RuntimeConfig",
    "get_settings",
]

warnings.warn(
    "Importing from thegent.config is deprecated. "
    "Please import from thegent_config instead, or from thegent.config.settings for specific configs.",
    DeprecationWarning,
    stacklevel=2,
)
