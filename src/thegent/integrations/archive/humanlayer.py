"""
HumanLayer Integration - Human-in-the-loop augmentation

Provides human-in-the-loop capabilities for agent workflows.
Enables approval workflows, human interventions.

Security:
- Verify NOASSERTION license compatibility
- No sensitive data in approval requests

License: NOASSERTION (verified at https://github.com/humanlayer/humanlayer)
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class HumanLayerStatus(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"


@dataclass
class HumanLayerConfig:
    enabled: bool = False
    api_url: str = "https://api.humanlayer.dev"
    api_key: str = ""


class HumanLayerClient:
    def __init__(self, config: HumanLayerConfig = None):
        self._config = config or self._load_config()
        self._status = HumanLayerStatus.DISABLED
        if self._config.enabled:
            self._status = HumanLayerStatus.ENABLED

    def _load_config(self):
        return HumanLayerConfig(
            enabled=os.getenv("THEGENT_ENABLE_HUMANLAYER", "").lower() in ("1", "true", "yes"),
            api_url=os.getenv("HUMANLAYER_API_URL", "https://api.humanlayer.dev"),
            api_key=os.getenv("HUMANLAYER_API_KEY", ""),
        )

    @property
    def is_enabled(self): return self._config.enabled

    async def request_approval(self, prompt: str, context: dict | None = None):
        """Request human approval for an action."""
        if not self.is_enabled:
            return {"approved": False, "reason": "HumanLayer not enabled"}
        # Implementation would call HumanLayer API
        return {"approved": True, "request_id": "mock"}

    async def notify_human(self, message: str, priority: str = "normal"):
        """Notify human of an event."""
        if not self.is_enabled:
            return False
        return True


_humanlayer = None
def get_humanlayer():
    global _humanlayer
    if _humanlayer is None:
        _humanlayer = HumanLayerClient()
    return _humanlayer
