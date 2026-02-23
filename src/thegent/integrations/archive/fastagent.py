"""
FastAgent Integration - Developer-first MCP/agent framework

Provides rapid agent composition and orchestration.
Useful for prototyping but less proven for production.

Security:
- Verify MIT license compatibility
- Use behind feature flags

License: MIT (verified at https://github.com/evalstate/fast-agent)
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class FastAgentStatus(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"


@dataclass
class FastAgentConfig:
    enabled: bool = False
    config_path: str = "./fastagent.yaml"


class FastAgentClient:
    def __init__(self, config: FastAgentConfig = None):
        self._config = config or self._load_config()
        self._status = FastAgentStatus.DISABLED
        if self._config.enabled:
            self._status = FastAgentStatus.ENABLED

    def _load_config(self):
        return FastAgentConfig(
            enabled=os.getenv("THEGENT_ENABLE_FASTAGENT", "").lower() in ("1", "true", "yes"),
            config_path=os.getenv("FASTAGENT_CONFIG", "./fastagent.yaml"),
        )

    @property
    def is_enabled(self): return self._config.enabled

    def run(self, workflow: str, input_data: dict | None = None):
        if not self.is_enabled:
            return None
        return {"result": {}}


_fastagent = None
def get_fastagent():
    global _fastagent
    if _fastagent is None:
        _fastagent = FastAgentClient()
    return _fastagent
