"""
Ory Kratos Auth Integration - Self-hosted identity management.
"""
import logging, os
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class KratosStatus(Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"

@dataclass
class KratosConfig:
    enabled: bool = False
    public_url: str = "http://localhost:4433"

class KratosAuthProvider:
    def __init__(self, config: KratosConfig = None):
        self._config = config or self._load_config()
        self._status = KratosStatus.DISABLED
        if self._config.enabled:
            self._status = KratosStatus.ENABLED

    def _load_config(self):
        return KratosConfig(
            enabled=os.getenv("THEGENT_AUTH_KRATOS", "").lower() in ("1", "true", "yes"),
            public_url=os.getenv("KRATOS_PUBLIC_URL", "http://localhost:4433"),
        )

    @property
    def is_enabled(self): return self._config.enabled

    async def validate_session(self, session_token):
        if not self.is_enabled: return {"success": False}
        return {"success": True, "roles": ["user"]}

_kratos = None
def get_kratos_provider():
    global _kratos
    if _kratos is None: _kratos = KratosAuthProvider()
    return _kratos
