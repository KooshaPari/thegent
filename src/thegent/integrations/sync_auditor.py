"""Sync policy auditor for runtime validation.

# @trace WL-261
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class SyncPolicyAudit:
    """Sync policy audit result."""

    enabled_connectors: list[str]
    quota_budgets: dict[str, int]
    policy_modes: dict[str, str]
    timestamp: str
    audit_status: str = "success"


class SyncAuditor:
    """Auditor for sync policies."""

    def __init__(self) -> None:
        """Initialize the sync auditor."""
        self._enabled_connectors: list[str] = []
        self._quota_budgets: dict[str, int] = {}
        self._policy_modes: dict[str, str] = {}

    def set_enabled_connectors(self, connectors: list[str]) -> None:
        """Set the list of enabled connectors.

        Args:
            connectors: List of enabled connector names.
        """
        self._enabled_connectors = list(connectors)

    def set_quota_budgets(self, budgets: dict[str, int]) -> None:
        """Set quota budgets for connectors.

        Args:
            budgets: Dictionary mapping connector names to daily quota limits.
        """
        self._quota_budgets = dict(budgets)

    def set_policy_modes(self, modes: dict[str, str]) -> None:
        """Set policy enforcement modes for connectors.

        Args:
            modes: Dictionary mapping connector names to policy modes
                  (e.g., 'enforce', 'warn', 'disabled').
        """
        self._policy_modes = dict(modes)

    def audit(self) -> SyncPolicyAudit:
        """Run the sync policy audit.

        Returns:
            SyncPolicyAudit with current policies.
        """
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc).isoformat()

        return SyncPolicyAudit(
            enabled_connectors=self._enabled_connectors,
            quota_budgets=self._quota_budgets,
            policy_modes=self._policy_modes,
            timestamp=now,
        )

    def audit_as_json(self) -> str:
        """Get audit result as JSON string.

        Returns:
            JSON representation of audit result.
        """
        audit = self.audit()
        return json.dumps(asdict(audit), indent=2)

    def audit_as_dict(self) -> dict[str, Any]:
        """Get audit result as dictionary.

        Returns:
            Dictionary representation of audit result.
        """
        audit = self.audit()
        return asdict(audit)

    def validate_policy(self) -> tuple[bool, list[str]]:
        """Validate sync policy configuration.

        Returns:
            Tuple of (is_valid, list_of_issues).
        """
        issues: list[str] = []

        if not self._enabled_connectors:
            issues.append("No connectors are enabled")

        # Check for quota budgets without corresponding enabled connectors
        for connector, budget in self._quota_budgets.items():
            if connector not in self._enabled_connectors:
                issues.append(f"Quota budget defined for disabled connector: {connector}")
            if budget <= 0:
                issues.append(f"Invalid quota budget for {connector}: {budget} (must be > 0)")

        # Check for policy modes without corresponding enabled connectors
        for connector in self._policy_modes:
            if connector not in self._enabled_connectors:
                issues.append(f"Policy mode defined for disabled connector: {connector}")

        # Check for missing policy modes
        for connector in self._enabled_connectors:
            if connector not in self._policy_modes:
                issues.append(f"Missing policy mode for enabled connector: {connector}")

        is_valid = len(issues) == 0
        return is_valid, issues
