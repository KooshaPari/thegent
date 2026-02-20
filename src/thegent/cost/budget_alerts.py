"""Budget alerts and cost-overage gates."""

import logging
from datetime import UTC, datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


class BudgetAlerts:
    """Budget alerts and cost-overage gates."""

    def __init__(self, budget_limit: float = 1000.0) -> None:
        """Initialize budget alerts.

        Args:
            budget_limit: Budget limit in dollars
        """
        self.budget_limit = budget_limit
        self.current_spend = 0.0
        self.alerts: list[dict[str, Any]] = []

    def record_spend(self, amount: float, description: str = "") -> None:
        """Record spending.

        Args:
            amount: Amount spent
            description: Description of spending
        """
        self.current_spend += amount
        logger.info(f"Recorded spend: ${amount:.2f} (Total: ${self.current_spend:.2f})")

        # Check if over budget
        if self.current_spend >= self.budget_limit:
            self._trigger_alert(
                "budget_exceeded",
                {
                    "current": self.current_spend,
                    "limit": self.budget_limit,
                    "overage": self.current_spend - self.budget_limit,
                },
            )

    def _trigger_alert(self, alert_type: str, data: dict[str, Any]) -> None:
        """Trigger an alert.

        Args:
            alert_type: Type of alert
            data: Alert data
        """
        alert = {
            "type": alert_type,
            "timestamp": datetime.now(UTC).isoformat(),
            "data": data,
        }
        self.alerts.append(alert)
        logger.warning(f"Alert triggered: {alert_type} - {data}")

    def check_budget_gate(self) -> bool:
        """Check if budget gate allows operation.

        Returns:
            True if within budget
        """
        return self.current_spend < self.budget_limit

    def get_alerts(self) -> list[dict[str, Any]]:
        """Get all alerts.

        Returns:
            List of alerts
        """
        return self.alerts
