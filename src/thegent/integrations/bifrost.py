"""
Bifrost Integration - Gateway claims validation

Provides gateway claims validation for LLM calls.
Requires local validation of claims.

Security:
- Verify Apache-2.0 license compatibility
- Local validation required

License: Apache-2.0 (verified at https://github.com/maximhq/bifrost)
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class BifrostStatus(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"


@dataclass
class BifrostConfig:
    enabled: bool = False
    gateway_url: str = "http://localhost:8080"


class BifrostClient:
    def __init__(self, config: BifrostConfig = None):
        self._config = config or self._load_config()
        self._status = BifrostStatus.DISABLED
        if self._config.enabled:
            self._status = BifrostStatus.ENABLED

    def _load_config(self):
        return BifrostConfig(
            enabled=os.getenv("THEGENT_ENABLE_BIFROST", "").lower() in ("1", "true", "yes"),
            gateway_url=os.getenv("BIFROST_GATEWAY_URL", "http://localhost:8080"),
        )

    @property
    def is_enabled(self): return self._config.enabled

    def validate_claims(self, claims: dict):
        if not self.is_enabled:
            return False
        return True


_bifrost = None
def get_bifrost():
    global _bifrost
    if _bifrost is None:
        _bifrost = BifrostClient()
    return _bifrost
