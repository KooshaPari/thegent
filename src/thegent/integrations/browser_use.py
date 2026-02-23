"""
Browser-use Integration - Browser automation.
"""
import logging, os
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class BrowserUseStatus(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"

@dataclass
class BrowserUseConfig:
    enabled: bool = False
    headless: bool = True

class BrowserUseAutomation:
    def __init__(self, config: BrowserUseConfig = None):
        self._config = config or self._load_config()
        self._status = BrowserUseStatus.DISABLED
        if self._config.enabled:
            self._status = BrowserUseStatus.ENABLED

    def _load_config(self):
        return BrowserUseConfig(
            enabled=os.getenv("THEGENT_ENABLE_BROWSER_USE", "").lower() in ("1", "true", "yes"),
            headless=os.getenv("BROWSER_USE_HEADLESS", "true").lower() == "true",
        )

    @property
    def is_enabled(self): return self._config.enabled
    async def navigate(self, url): return self.is_enabled

_browser_use = None
def get_browser_use():
    global _browser_use
    if _browser_use is None: _browser_use = BrowserUseAutomation()
    return _browser_use
