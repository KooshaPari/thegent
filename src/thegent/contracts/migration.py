"""Contract Migration Controller.

Manages the transition between contract versions, enforces deprecation policies,
and evaluates migration window compliance.
"""

from datetime import UTC, datetime
from typing import Any

from thegent.contracts.registry import get_registry


class MigrationController:
    """Controls and monitors contract version migrations (WP-7008)."""

    def __init__(self, registry=None) -> None:
        self.registry = registry or get_registry()
        self._canary_percentage: float = 0.0  # 0.0 to 1.0
        self._dual_write_enabled: bool = False

    def set_canary(self, percentage: float) -> None:
        """Set canary rollout percentage (WP-7008)."""
        self._canary_percentage = max(0.0, min(1.0, percentage))

    def set_dual_write(self, enabled: bool) -> None:
        """Enable or disable dual-write mode (WP-7008)."""
        self._dual_write_enabled = enabled

    def should_use_new_version(self, run_id: str) -> bool:
        """Determine if a run should use the target migration version based on canary."""
        if self._canary_percentage >= 1.0:
            return True
        if self._canary_percentage <= 0.0:
            return False

        # Deterministic hash-based canary
        import hashlib

        h = int(hashlib.md5(run_id.encode()).hexdigest(), 16)
        return (h % 100) < (self._canary_percentage * 100)

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
