"""
SearXNG Search Integration - Privacy-respecting search.
"""
import logging
import os
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class SearXNGStatus(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"

@dataclass
class SearXNGConfig:
    enabled: bool = False
    server_url: str = "http://localhost:8888"

class SearXNGSearch:
    def __init__(self, config: SearXNGConfig | None = None):
        self._config = config or self._load_config()
        self._status = SearXNGStatus.DISABLED
        if self._config.enabled:
            self._status = SearXNGStatus.ENABLED

    def _load_config(self):
        return SearXNGConfig(
            enabled=os.getenv("THEGENT_ENABLE_SEARXNG", "").lower() in ("1", "true", "yes"),
            server_url=os.getenv("SEARXNG_URL", "http://localhost:8888"),
        )

    @property
    def is_enabled(self): return self._config.enabled
    async def search(self, query, categories=None): return [] if not self.is_enabled else []

_searxng = None
def get_searxng():
    global _searxng
    if _searxng is None:
        _searxng = SearXNGSearch()
    return _searxng
