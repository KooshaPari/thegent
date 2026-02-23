"""
Zed Editor Integration - IDE-like functionality.
"""
import logging
import os
import subprocess
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ZedStatus(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"

@dataclass
class ZedConfig:
    enabled: bool = False
    binary_path: str = ""

class ZedEditor:
    def __init__(self, config: ZedConfig = None):
        self._config = config or self._load_config()
        self._status = ZedStatus.DISABLED
        if self._config.enabled:
            self._status = ZedStatus.ENABLED

    def _load_config(self):
        return ZedConfig(
            enabled=os.getenv("THEGENT_ENABLE_ZED", "").lower() in ("1", "true", "yes"),
            binary_path=os.getenv("ZED_BINARY", ""),
        )

    @property
    def is_enabled(self): return self._config.enabled
    async def open_file(self, file_path, line=1): return self.is_enabled

_zed = None
def get_zed():
    global _zed
    if _zed is None: _zed = ZedEditor()
    return _zed
