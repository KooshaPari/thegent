"""Contract Migration Controller.

Manages the transition between contract versions, enforces deprecation policies,
and evaluates migration window compliance.
"""

from datetime import UTC, datetime
from typing import Any

from thegent.contracts.registry import get_registry


class MigrationController:
    """Controls and monitors contract version migrations."""

    def __init__(self, registry=None) -> None:
        self.registry = registry or get_registry()

    def evaluate_version(self, contract_id: str, version: str) -> dict[str, Any]:
        """Evaluate if a contract version is suitable for current use.

        Returns:
            Dictionary with keys: 'allowed', 'status', 'reason', 'migration_days_left'.
        """
        cv = self.registry.get(contract_id, version)
        if not cv:
            return {"allowed": False, "status": "unknown", "reason": f"Contract {contract_id}@{version} not found."}

        now = datetime.now(UTC)

        if cv.deprecated:
            if cv.migration_window_end:
                end_dt = datetime.fromisoformat(cv.migration_window_end)
                days_left = (end_dt - now).days
                if now > end_dt:
                    return {
                        "allowed": False,
                        "status": "expired",
                        "reason": f"Contract {contract_id}@{version} expired on {cv.migration_window_end}",
                        "migration_days_left": days_left,
                    }
                return {
                    "allowed": True,
                    "status": "deprecated",
                    "reason": f"Contract {contract_id}@{version} is deprecated. Migration window ends in {days_left} days.",
                    "migration_days_left": days_left,
                }
            return {
                "allowed": True,
                "status": "deprecated",
                "reason": f"Contract {contract_id}@{version} is deprecated.",
            }

        return {"allowed": True, "status": "active", "reason": "Contract version is active and supported."}

    def get_preferred_version(self, contract_id: str) -> str:
        """Return the latest non-deprecated version for a contract ID."""
        cv = self.registry.get(contract_id)
        return cv.version if cv else "unknown"
