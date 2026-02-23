"""
Humanify Integration - Human-like interaction patterns.
"""
import logging
import os
import random
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class HumanifyStatus(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"

@dataclass
class HumanifyConfig:
    enabled: bool = False
    variability: float = 0.5

class HumanifyPatterns:
    def __init__(self, config: HumanifyConfig = None):
        self._config = config or self._load_config()
        self._status = HumanifyStatus.DISABLED
        if self._config.enabled:
            self._status = HumanifyStatus.ENABLED

    def _load_config(self):
        return HumanifyConfig(
            enabled=os.getenv("THEGENT_ENABLE_HUMANIFY", "").lower() in ("1", "true", "yes"),
            variability=float(os.getenv("HUMANIFY_VARIABILITY", "0.5")),
        )

    @property
    def is_enabled(self): return self._config.enabled

    def add_human_delay(self):
        if not self.is_enabled: return 0
        return random.uniform(100, 500) * self._config.variability / 1000

_humanify = None
def get_humanify():
    global _humanify
    if _humanify is None: _humanify = HumanifyPatterns()
    return _humanify
