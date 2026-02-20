"""Budget-aware routing and economic governance for thegent.

Implements the Economic Governance Framework (WP-5003).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from thegent.routing.pareto_router import ParetoRouter, RouteCandidate

_log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


class BudgetType(Enum):
    """Supported budget scopes (SCLI-P9.1)."""

    SESSION = "session"
    DAILY = "daily"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    PER_MODEL = "per_model"
    EMERGENCY = "emergency"


@dataclass
class Budget:
    """A budget allocation for a project or session (FR-COST-001)."""

    id: str
    project_id: str
    budget_type: BudgetType
    amount: float
    spent: float = 0.0
    start_date: datetime = field(default_factory=lambda: datetime.now(UTC))
    end_date: datetime | None = None
    renews: bool = False

    @property
    def remaining(self) -> float:
        """Return remaining budget in USD."""
        return max(0.0, self.amount - self.spent)

    @property
    def utilization(self) -> float:
        """Return fraction of budget spent."""
        if self.amount <= 0:
            return 1.0
        return self.spent / self.amount


@dataclass
class BudgetStatus:
    """Status of a budget check."""

    can_proceed: bool
    remaining_budget: float
    utilization: float
    reason: str | None = None


class BudgetExceededError(Exception):
    """Raised when spend has exceeded a configured budget limit (FR-COST-002)."""

    def __init__(self, budget_type: str, limit: float, current: float) -> None:
        self.budget_type = budget_type
        self.limit = limit
        self.current = current
        super().__init__(f"{budget_type} budget exceeded: current=${current:.4f} > limit=${limit:.4f}")


# ---------------------------------------------------------------------------
# Managers and Meters
# ---------------------------------------------------------------------------


class CostMeter:
    """Real-time cost metering for projects and models (FR-COST-001)."""

    def __init__(self) -> None:
        self.current_costs: dict[str, float] = {}
        self.cost_history: list[dict[str, Any]] = []

    async def record_cost(
        self, project_id: str, model: str, input_tokens: int, output_tokens: int, cost: float
    ) -> None:
        """Record cost for a single request (FR-COST-001)."""
        key = f"{project_id}:{model}"
        self.current_costs[key] = self.current_costs.get(key, 0.0) + cost

        self.cost_history.append(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "project_id": project_id,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": cost,
            }
        )

    def get_project_cost(self, project_id: str) -> float:
        """Get total cost for a project across all models."""
        return sum(cost for key, cost in self.current_costs.items() if key.startswith(f"{project_id}:"))


class BudgetManager:
    """Manages budget allocations and enforcement (FR-COST-003)."""

    def __init__(self) -> None:
        self.budgets: dict[str, Budget] = {}

    def add_budget(self, budget: Budget) -> None:
        """Add a budget allocation."""
        self.budgets[budget.id] = budget

    def check_budget(self, project_id: str, requested_cost: float = 0.0) -> BudgetStatus:
        """Check if any budget for project_id is exceeded."""
        relevant_budgets = [b for b in self.budgets.values() if b.project_id == project_id]

        if not relevant_budgets:
            # If no budget is defined, we allow by default but warn
            return BudgetStatus(can_proceed=True, remaining_budget=float("inf"), utilization=0.0)

        for budget in relevant_budgets:
            if budget.spent + requested_cost > budget.amount:
                return BudgetStatus(
                    can_proceed=False,
                    remaining_budget=budget.remaining,
                    utilization=budget.utilization,
                    reason=f"Budget {budget.id} ({budget.budget_type.value}) exceeded",
                )

        # Return the most constrained budget's status
        most_constrained = min(relevant_budgets, key=lambda b: b.remaining)
        return BudgetStatus(
            can_proceed=True, remaining_budget=most_constrained.remaining, utilization=most_constrained.utilization
        )

    def record_spend(self, project_id: str, cost: float) -> None:
        """Update all relevant budgets for project_id with recorded cost."""
        for budget in self.budgets.values():
            if budget.project_id == project_id:
                budget.spent += cost


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------


class BudgetAwareRouter:
    """Routes to optimal candidates while respecting cost budgets (FR-COST-003, WP-1004)."""

    def __init__(
        self,
        budget_manager: BudgetManager,
        pareto_router: ParetoRouter | None = None,
        warn_at_pct: float = 0.8,
        degraded_at_pct: float = 0.9,
    ) -> None:
        self.budget_manager = budget_manager
        self.router = pareto_router or ParetoRouter()
        self.warn_at_pct = warn_at_pct
        self.degraded_at_pct = degraded_at_pct

    def route(self, project_id: str, candidates: list[RouteCandidate], strategy: str = "balanced") -> RouteCandidate:
        """Select the best candidate given current budget state and Pareto strategy."""
        if not candidates:
            raise ValueError("candidates list must not be empty")

        # 1. Hard Budget Check
        status = self.budget_manager.check_budget(project_id)

        if not status.can_proceed:
            # If strictly over budget, select the absolute cheapest candidate
            _log.warning("Budget exceeded for project %s. Routing to cheapest candidate.", project_id)
            return min(candidates, key=lambda c: c.cost_per_1k)

        # 2. Degraded Mode (90%+)
        if status.utilization >= self.degraded_at_pct:
            _log.info(
                "Degraded mode (utilization %.2f) for project %s. Forcing cost strategy.",
                status.utilization,
                project_id,
            )
            return self.router.select_by_strategy("cost", candidates)

        # 3. Warn Mode (80%+)
        if status.utilization >= self.warn_at_pct:
            # Filter to cheapest 50% before Pareto selection
            pool = self._cheapest_half(candidates)
            _log.info(
                "Warn mode (utilization %.2f) for project %s. Filtering to cheapest half.",
                status.utilization,
                project_id,
            )
            return self.router.select_by_strategy(strategy, pool)

        # 4. Normal Routing
        return self.router.select_by_strategy(strategy, candidates)

    def _cheapest_half(self, candidates: list[RouteCandidate]) -> list[RouteCandidate]:
        """Return the cheapest 50% (rounded up) of candidates by cost_per_1k."""
        sorted_by_cost = sorted(candidates, key=lambda c: c.cost_per_1k)
        cutoff = max(1, (len(sorted_by_cost) + 1) // 2)  # ceil(n/2), min 1
        return sorted_by_cost[:cutoff]
