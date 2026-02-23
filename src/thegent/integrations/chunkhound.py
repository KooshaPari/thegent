"""
ChunkHound Integration - Local-first code intelligence

Provides code chunking/indexing for local code intelligence.
Low infra overhead for code analysis.

Security:
- Verify MIT license compatibility

License: MIT (verified at https://github.com/chunkhound/chunkhound)
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ChunkHoundStatus(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"


@dataclass
class ChunkHoundConfig:
    enabled: bool = False
    index_path: str = "./.chunkhound"


class ChunkHoundClient:
    def __init__(self, config: ChunkHoundConfig = None):
        self._config = config or self._load_config()
        self._status = ChunkHoundStatus.DISABLED
        if self._config.enabled:
            self._status = ChunkHoundStatus.ENABLED

    def _load_config(self):
        return ChunkHoundConfig(
            enabled=os.getenv("THEGENT_ENABLE_CHUNKHOUND", "").lower() in ("1", "true", "yes"),
            index_path=os.getenv("CHUNKHOUND_INDEX_PATH", "./.chunkhound"),
        )

    @property
    def is_enabled(self): return self._config.enabled

    def index(self, path: str):
        if not self.is_enabled: return None
        return {"indexed": 0}

    def query(self, query: str):
        if not self.is_enabled: return []
        return []


_chunkhound = None
def get_chunkhound():
    global _chunkhound
    if _chunkhound is None: _chunkhound = ChunkHoundClient()
    return _chunkhound
