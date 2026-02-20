"""Cost-aware router: enforces per-session and per-day cost budgets.

Routes to cheaper models when approaching limits; raises BudgetExceededError
when limits are crossed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, date, datetime

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class RouteCandidate:
    """A routable candidate with quality and cost dimensions."""

    name: str
    cost_per_call: float  # Estimated USD cost per call
    quality: float  # 0–1 quality proxy (higher = better)


@dataclass
class CostBudget:
    """Budget thresholds for cost-aware routing."""

    daily_limit_usd: float
    session_limit_usd: float
    warn_at_pct: float = 0.8  # Fraction of either limit that triggers cheap mode


# ---------------------------------------------------------------------------
# Simple in-memory cost tracker (session + daily)
# ---------------------------------------------------------------------------


@dataclass
class _DailyBucket:
    day: date
    total: float = 0.0


class SimpleCostTracker:
    """Minimal in-memory cost tracker with session and daily totals.

    Traces to: FR-COST-001
    """

    def __init__(self) -> None:
        self._session_total: float = 0.0
        self._daily: _DailyBucket = _DailyBucket(day=date.today())

    def record(self, cost: float) -> None:
        """Record a cost entry (USD)."""
        if cost < 0:
            raise ValueError(f"cost must be non-negative, got {cost}")
        self._session_total += cost
        today = date.today()
        if self._daily.day != today:
            self._daily = _DailyBucket(day=today)
        self._daily.total += cost

    def session_total(self) -> float:
        """Return total spend for the current session."""
        return self._session_total

    def daily_total(self) -> float:
        """Return total spend for today (resets at midnight)."""
        today = date.today()
        if self._daily.day != today:
            self._daily = _DailyBucket(day=today)
        return self._daily.total

    def reset_session(self) -> None:
        """Reset session total (e.g. at session boundary)."""
        self._session_total = 0.0


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------


class BudgetExceededError(Exception):
    """Raised when spend has exceeded a configured budget limit.

    Traces to: FR-COST-002
    """

    def __init__(self, budget_type: str, limit: float, current: float) -> None:
        self.budget_type = budget_type
        self.limit = limit
        self.current = current
        super().__init__(
            f"{budget_type} budget exceeded: current=${current:.4f} > limit=${limit:.4f}"
        )


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------


class CostAwareRouter:
    """Routes to optimal candidates while respecting cost budgets.

    Selection logic:
    - If spend >= session_limit or daily_limit → raise BudgetExceededError
    - If spend >= warn_at_pct of either limit → select cheapest 50% of candidates
    - Otherwise → select highest-quality candidate

    Traces to: FR-COST-003
    """

    def __init__(self, budget: CostBudget, cost_tracker: SimpleCostTracker) -> None:
        self._budget = budget
        self._tracker = cost_tracker

    def select(self, candidates: list[RouteCandidate]) -> RouteCandidate:
        """Select the best candidate given current budget state.

        Args:
            candidates: Non-empty list of route candidates.

        Returns:
            Selected RouteCandidate.

        Raises:
            BudgetExceededError: When session or daily spend exceeds limits.
            ValueError: When candidates list is empty.
        """
        if not candidates:
            raise ValueError("candidates list must not be empty")

        session_spend = self._tracker.session_total()
        daily_spend = self._tracker.daily_total()

        # Hard limit checks
        if session_spend >= self._budget.session_limit_usd:
            raise BudgetExceededError("session", self._budget.session_limit_usd, session_spend)
        if daily_spend >= self._budget.daily_limit_usd:
            raise BudgetExceededError("daily", self._budget.daily_limit_usd, daily_spend)

        # Warn threshold: filter to cheapest 50%
        session_warn = self._budget.session_limit_usd * self._budget.warn_at_pct
        daily_warn = self._budget.daily_limit_usd * self._budget.warn_at_pct
        near_limit = session_spend >= session_warn or daily_spend >= daily_warn

        pool = _cheapest_half(candidates) if near_limit else candidates

        return max(pool, key=lambda c: c.quality)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _cheapest_half(candidates: list[RouteCandidate]) -> list[RouteCandidate]:
    """Return the cheapest 50% (rounded up) of candidates by cost_per_call."""
    sorted_by_cost = sorted(candidates, key=lambda c: c.cost_per_call)
    cutoff = max(1, (len(sorted_by_cost) + 1) // 2)  # ceil(n/2), min 1
    return sorted_by_cost[:cutoff]
