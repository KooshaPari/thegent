"""
OpenSpec Integration - Spec/change workflow integration.

Implements Fission-AI/OpenSpec for thegent.
"""

import logging
import os
import subprocess
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class OpenSpecStatus(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"

@dataclass
class OpenSpecConfig:
    enabled: bool = False
    binary_path: str = ""

class OpenSpecAdapter:
    """Adapter for openspec binary."""

    def __init__(self, config: OpenSpecConfig = None):
        self._config = config or self._load_config()
        self._status = OpenSpecStatus.DISABLED
        if self._config.enabled:
            self._status = OpenSpecStatus.ENABLED

    def _load_config(self):
        return OpenSpecConfig(
            enabled=os.getenv("THEGENT_ENABLE_OPENSPEC", "").lower() in ("1", "true", "yes"),
            binary_path=os.getenv("OPENSPEC_BINARY", "openspec"),
        )

    @property
    def is_enabled(self): return self._config.enabled

    def run(self, args):
        if not self.is_enabled:
            return None
        try:
            result = subprocess.run(
                [self._config.binary_path] + args,
                capture_output=True, text=True, timeout=30
            )
            return {"success": result.returncode == 0, "output": result.stdout, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}

_openspec = None
def get_openspec_adapter():
    global _openspec
    if _openspec is None:
        _openspec = OpenSpecAdapter()
    return _openspec
