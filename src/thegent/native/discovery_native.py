"""BKM-08: Discovery operations using native Rust (thegent-discovery).

Provides discovery of running agents using the thegent-discovery PyO3 extension.

Requires thegent-discovery to be installed.

FR-trace: BKM-08
"""

from __future__ import annotations

import logging
from typing import Any

import thegent_discovery

_log = logging.getLogger(__name__)


class DiscoveryClient:
    """Native discovery client using Rust."""

    def __init__(self) -> None:
        self._manager = thegent_discovery.DiscoveryManager.new()

    def scan_agents(self) -> list[dict[str, Any]]:
        """Scan for running AI agents (claude, codex, cursor, etc.)."""
        return self._manager.scan_agents()

    def get_system_info(self) -> dict[str, float]:
        """Get system info (CPU, memory, etc.)."""
        return self._manager.get_system_info()
