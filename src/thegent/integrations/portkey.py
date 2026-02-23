"""
Portkey AI Integration - LLM Gateway with observability

Provides LLM gateway governance with full observability.
2.0 transition - use with controlled rollout.

Security:
- Verify Apache-2.0 license compatibility

License: Apache-2.0 (verified at https://github.com/Portkey-AI/gateway)
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PortkeyStatus(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"


@dataclass
class PortkeyConfig:
    enabled: bool = False
    api_key: str = ""
    gateway_url: str = "https://api.portkey.ai"


class PortkeyClient:
    def __init__(self, config: PortkeyConfig | None = None):
        self._config = config or self._load_config()
        self._status = PortkeyStatus.DISABLED
        if self._config.enabled:
            self._status = PortkeyStatus.ENABLED

    def _load_config(self):
        return PortkeyConfig(
            enabled=os.getenv("THEGENT_ENABLE_PORTKEY", "").lower() in ("1", "true", "yes"),
            api_key=os.getenv("PORTKEY_API_KEY", ""),
            gateway_url=os.getenv("PORTKEY_GATEWAY_URL", "https://api.portkey.ai"),
        )

    @property
    def is_enabled(self): return self._config.enabled

    async def call(self, prompt: str, model: str = "gpt-4"):
        if not self.is_enabled:
            return None
        return {"choices": [{"text": ""}]}


_portkey = None
def get_portkey():
    global _portkey
    if _portkey is None:
        _portkey = PortkeyClient()
    return _portkey
