"""
OpenCode Integration - High potential but volatile

Provides AI coding assistant capabilities.
HIGH VOLATILITY - use as pilot only with strict feature flags.

Security:
- Verify MIT license compatibility
- Strict feature flag control

License: MIT (verified at https://github.com/anomalyco/opencode)
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class OpenCodeStatus(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"


@dataclass
class OpenCodeConfig:
    enabled: bool = False
    binary_path: str = "opencode"


class OpenCodeClient:
    def __init__(self, config: OpenCodeConfig | None = None):
        self._config = config or self._load_config()
        self._status = OpenCodeStatus.DISABLED
        if self._config.enabled:
            self._status = OpenCodeStatus.ENABLED

    def _load_config(self):
        return OpenCodeConfig(
            enabled=os.getenv("THEGENT_ENABLE_OPENCODE", "").lower() in ("1", "true", "yes"),
            binary_path=os.getenv("OPENCODE_BINARY", "opencode"),
        )

    @property
    def is_enabled(self): return self._config.enabled

    def complete(self, prompt: str):
        if not self.is_enabled:
            return None
        return {"completion": ""}


_opencode = None
def get_opencode():
    global _opencode
    if _opencode is None:
        _opencode = OpenCodeClient()
    return _opencode
