import logging
from typing import Any

_log = logging.getLogger(__name__)


class DiscoverySystem:
    """Wrapper for thegent_discovery Rust extension."""

    _instance = None
    _interface = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        from thegent.config import ThegentSettings

        self.use_native = ThegentSettings().use_native_discovery
        self._interface = None

        if self.use_native:
            try:
                from thegent_discovery import DiscoveryInterface

                self._interface = DiscoveryInterface()
                _log.debug("Initialized native Discovery")
            except ImportError:
                _log.debug("thegent_discovery native extension not found. Falling back to legacy discovery.")
            except Exception as e:
                _log.error("Failed to initialize native Discovery: %s", e)

    def is_native_active(self) -> bool:
        return self._interface is not None

    def scan_agents(self) -> list[dict[str, Any]]:
        if self._interface:
            try:
                return self._interface.scan_agents()
            except Exception as e:
                _log.error("Native scan_agents failed: %s", e)

        # Fallback to legacy scan_agent_processes if needed
        # For now we'll just return empty list or let the caller handle it
        return []


def get_discovery_system() -> DiscoverySystem:
    return DiscoverySystem()
