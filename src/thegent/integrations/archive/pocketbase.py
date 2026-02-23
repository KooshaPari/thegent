"""
PocketBase Storage Integration - Lightweight backend.
"""
import logging
import os
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class PocketBaseStatus(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"

@dataclass
class PocketBaseConfig:
    enabled: bool = False
    url: str = "http://localhost:8090"

class PocketBaseClient:
    def __init__(self, config: PocketBaseConfig | None = None):
        self._config = config or self._load_config()
        self._status = PocketBaseStatus.DISABLED
        if self._config.enabled:
            self._status = PocketBaseStatus.ENABLED

    def _load_config(self):
        return PocketBaseConfig(
            enabled=os.getenv("THEGENT_ENABLE_POCKETBASE", "").lower() in ("1", "true", "yes"),
            url=os.getenv("POCKETBASE_URL", "http://localhost:8090"),
        )

    @property
    def is_enabled(self): return self._config.enabled

    async def log_event(self, event_type, data):
        return self.is_enabled

_pocketbase = None
def get_pocketbase_client():
    global _pocketbase
    if _pocketbase is None:
        _pocketbase = PocketBaseClient()
    return _pocketbase
