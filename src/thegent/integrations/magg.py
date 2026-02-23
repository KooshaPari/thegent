"""
Magg Integration - MCP aggregator.

Implements sitbon/magg for MCP server aggregation.
"""

import logging
import os
import subprocess
from dataclasses import dataclass
from enum import Enum

logger = logging.get_logger(__name__) if hasattr(logging, 'get_logger') else logging

class MaggStatus(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    UNAVAILABLE = "unavailable"

@dataclass
class MaggConfig:
    enabled: bool = False
    http_port: int = 8080

class MaggAggregator:
    """MCP aggregator using magg."""

    def __init__(self, config: MaggConfig = None):
        self._config = config or self._load_config()
        self._status = MaggStatus.DISABLED
        self._process = None
        if self._config.enabled:
            self._status = MaggStatus.ENABLED

    def _load_config(self):
        return MaggConfig(
            enabled=os.getenv("THEGENT_ENABLE_MAGG", "").lower() in ("1", "true", "yes"),
            http_port=int(os.getenv("MAGG_HTTP_PORT", "8080")),
        )

    @property
    def is_enabled(self): return self._config.enabled

    def serve(self, background: bool = True):
        if not self.is_enabled:
            return None
        try:
            cmd = ["magg", "serve", "--http", str(self._config.http_port)]
            if background:
                self._process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return {"success": True, "pid": self._process.pid}
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            return {"success": result.returncode == 0}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_servers(self):
        if not self.is_enabled:
            return []
        try:
            result = subprocess.run(
                ["magg", "list"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return [line.strip() for line in result.stdout.split("\n") if line.strip()]
        except:
            pass
        return []

    def add_server(self, name: str, command: list):
        if not self.is_enabled:
            return {"success": False}
        try:
            result = subprocess.run(
                ["magg", "add", name] + command, capture_output=True, timeout=10
            )
            return {"success": result.returncode == 0}
        except Exception as e:
            return {"success": False, "error": str(e)}

_magg = None
def get_magg_aggregator():
    global _magg
    if _magg is None:
        _magg = MaggAggregator()
    return _magg
