"""Capability mismatch detection for connectors.

Detects when a connector lacks required capabilities for sync operations
and generates alerts.

FR traceability: WL-305 (Capability Mismatch Alerts)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class CapabilityMismatchDetector:
    """Detects capability mismatches between connectors and sync requirements.

    Attributes:
        required_capabilities: List of capabilities required for sync.
    """

    def __init__(self, required_capabilities: list[str]) -> None:
        """Initialize the detector.

        Args:
            required_capabilities: Capabilities required by the sync.

        Raises:
            ValueError: If required_capabilities is empty or not a list.
        """
        if not isinstance(required_capabilities, list):
            raise ValueError("required_capabilities must be a list")
        if not required_capabilities:
            raise ValueError("required_capabilities cannot be empty")

        self.required_capabilities = required_capabilities

    def check_connector(
        self,
        connector_name: str,
        available_capabilities: list[str],
    ) -> list[str]:
        """Check a connector for missing capabilities.

        Args:
            connector_name: Name of the connector.
            available_capabilities: Capabilities the connector has.

        Returns:
            List of missing capability names (empty if all present).

        Raises:
            ValueError: If inputs are invalid.
        """
        if not isinstance(connector_name, str) or not connector_name:
            raise ValueError("connector_name must be a non-empty string")
        if not isinstance(available_capabilities, list):
            raise ValueError("available_capabilities must be a list")

        missing = []
        for cap in self.required_capabilities:
            if cap not in available_capabilities:
                missing.append(cap)

        return missing

    def is_compatible(
        self,
        connector_name: str,
        available_capabilities: list[str],
    ) -> bool:
        """Check if a connector has all required capabilities.

        Args:
            connector_name: Name of the connector.
            available_capabilities: Capabilities the connector has.

        Returns:
            True if all required capabilities are present.

        Raises:
            ValueError: If inputs are invalid.
        """
        missing = self.check_connector(connector_name, available_capabilities)
        return len(missing) == 0

    def generate_alert(
        self,
        connector_name: str,
        missing: list[str],
    ) -> dict:
        """Generate an alert for capability mismatch.

        Args:
            connector_name: Name of the connector.
            missing: List of missing capabilities.

        Returns:
            Alert dict with keys: connector, missing, severity, timestamp.

        Raises:
            ValueError: If inputs are invalid.
        """
        if not isinstance(connector_name, str) or not connector_name:
            raise ValueError("connector_name must be a non-empty string")
        if not isinstance(missing, list):
            raise ValueError("missing must be a list")

        severity = "critical" if missing else "ok"

        return {
            "connector": connector_name,
            "missing": missing,
            "severity": severity,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
