"""
Doorstop Integration - Requirement traceability.

Implements doorstop-dev/doorstop for FR tracking.
"""

import logging
import os
import subprocess
from thegent.infra.shim_subprocess import run as shim_run
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class DoorstopStatus(Enum):
    UNAVAILABLE = "unavailable"
    AVAILABLE = "available"

@dataclass
class DoorstopConfig:
    enabled: bool = False
    project_path: str = "."

class DoorstopSync:
    """Doorstop requirement-trace sync."""

    def __init__(self, config: DoorstopConfig = None):
        self._config = config or self._load_config()
        self._status = DoorstopStatus.UNAVAILABLE
        if self._config.enabled:
            self._check_available()

    def _load_config(self):
        return DoorstopConfig(
            enabled=os.getenv("THEGENT_ENABLE_DOORSTOP", "").lower() in ("1", "true", "yes"),
            project_path=os.getenv("DOORSTOP_PROJECT", "."),
        )

    def _check_available(self):
        try:
            result = shim_run(
                ["doorstop", "--version"],
                capture_output=True, timeout=5
            )
            if result.returncode == 0:
                self._status = DoorstopStatus.AVAILABLE
        except Exception:  # noqa: BLE001 -- intentional: doorstop availability check must not raise
            pass

    @property
    def is_enabled(self) -> bool:
        return self._config.enabled and self._status == DoorstopStatus.AVAILABLE

    def sync_to_fr(self, output_path: str = "FUNCTIONAL_REQUIREMENTS.md"):
        if not self.is_enabled:
            return {"success": False, "error": "Not enabled"}
        try:
            # Generate requirements document
            result = shim_run(
                ["doorstop", "build", "-p", self._config.project_path, "-o", output_path],
                capture_output=True, timeout=60
            )
            return {"success": result.returncode == 0, "output": result.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}

_doorstop = None
def get_doorstop_sync():
    global _doorstop
    if _doorstop is None:
        _doorstop = DoorstopSync()
    return _doorstop
