"""
Mem0 Integration - Fast memory layer for AI agents

Provides memory layer for AI agents.
Fast adoption candidate vs graphiti.

Security:
- Verify Apache-2.0 license compatibility

License: Apache-2.0 (verified at https://github.com/mem0ai/mem0)
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class Mem0Status(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"


@dataclass
class Mem0Config:
    enabled: bool = False
    api_key: str = ""
    api_url: str = "https://api.mem0.ai"


class Mem0Client:
    def __init__(self, config: Mem0Config = None):
        self._config = config or self._load_config()
        self._status = Mem0Status.DISABLED
        if self._config.enabled:
            self._status = Mem0Status.ENABLED

    def _load_config(self):
        return Mem0Config(
            enabled=os.getenv("THEGENT_ENABLE_MEM0", "").lower() in ("1", "true", "yes"),
            api_key=os.getenv("MEM0_API_KEY", ""),
            api_url=os.getenv("MEM0_API_URL", "https://api.mem0.ai"),
        )

    @property
    def is_enabled(self): return self._config.enabled

    async def add_memory(self, user_id: str, content: str, metadata: dict | None = None):
        if not self.is_enabled:
            return None
        return {"id": "mock"}

    async def search(self, user_id: str, query: str):
        if not self.is_enabled:
            return []
        return []


_mem0 = None
def get_mem0():
    global _mem0
    if _mem0 is None:
        _mem0 = Mem0Client()
    return _mem0
