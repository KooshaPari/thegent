"""
Nordlys Routing Adapter - Model routing/selection.
"""
import logging
import os
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class NordlysStatus(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"

@dataclass
class NordlysConfig:
    enabled: bool = False
    server_url: str = "http://localhost:8001"

class NordlysRouter:
    def __init__(self, config: NordlysConfig | None = None):
        self._config = config or self._load_config()
        self._status = NordlysStatus.DISABLED
        if self._config.enabled:
            self._status = NordlysStatus.ENABLED

    def _load_config(self):
        return NordlysConfig(
            enabled=os.getenv("THEGENT_ENABLE_NORDLYS", "").lower() in ("1", "true", "yes"),
            server_url=os.getenv("NORDLYS_SERVER_URL", "http://localhost:8001"),
        )

    @property
    def is_enabled(self): return self._config.enabled

    async def route(self, prompt, constraints=None):
        return {"provider": "openai", "model": "gpt-4", "reasoning": "fallback" if not self.is_enabled else "routed"}

_nordlys = None
def get_nordlys_router():
    global _nordlys
    if _nordlys is None:
        _nordlys = NordlysRouter()
    return _nordlys
