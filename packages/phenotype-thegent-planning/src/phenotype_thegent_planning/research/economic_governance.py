"""Economic Governance (Cost-Aware Routing)."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class EconomicGovernance:
    """Economic governance for cost-aware routing."""

    def __init__(self) -> None:
        """Initialize economic governance."""
        self.policies: dict[str, Any] = {}
        self.budget_limits: dict[str, float] = {}

    def set_budget_limit(self, tenant_id: str, limit: float) -> None:
        """Set budget limit for a tenant.

        Args:
            tenant_id: Tenant identifier
            limit: Budget limit
        """
        self.budget_limits[tenant_id] = limit
        logger.info(f"Set budget limit for {tenant_id}: ${limit:.2f}")

    def check_budget(self, tenant_id: str, cost: float) -> bool:
        """Check if operation is within budget.

        Args:
            tenant_id: Tenant identifier
            cost: Operation cost

        Returns:
            True if within budget
        """
        limit = self.budget_limits.get(tenant_id, float("inf"))
        return cost <= limit

    def route_with_governance(self, tenant_id: str, options: list[dict[str, Any]]) -> dict[str, Any] | None:
        """Route with economic governance constraints.

        Args:
            tenant_id: Tenant identifier
            options: Routing options

        Returns:
            Selected route or None
        """
        budget_limit = self.budget_limits.get(tenant_id)
        if not budget_limit:
            return options[0] if options else None

        # Filter by budget
        affordable = [opt for opt in options if opt.get("cost", 0) <= budget_limit]
        if not affordable:
            logger.warning(f"No affordable routes for {tenant_id}")
            return None

        # Select best quality within budget
        best = max(affordable, key=lambda x: x.get("quality", 0))
        logger.info(f"Routed {tenant_id} to option with cost ${best.get('cost', 0):.4f}")
        return best
