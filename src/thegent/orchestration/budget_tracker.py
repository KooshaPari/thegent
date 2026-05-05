"""Budget tracking for orchestration."""
from __future__ import annotations
from typing import Any


class BudgetTracker:
    """Tracks budget usage for tasks and agents."""

    def __init__(self, initial_budget: float = 0.0) -> None:
        self.initial_budget = initial_budget
        self.spent: float = 0.0
        self.allocation: dict[str, float] = {}

    def allocate(self, agent_id: str, amount: float) -> None:
        """Allocate budget to an agent."""
        self.allocation[agent_id] = amount

    def record_spend(self, agent_id: str, amount: float) -> None:
        """Record spending by an agent."""
        self.spent += amount

    def get_remaining(self, agent_id: str | None = None) -> float:
        """Get remaining budget."""
        if agent_id:
            return self.allocation.get(agent_id, 0.0)
        return self.initial_budget - self.spent

    def is_exhausted(self, agent_id: str | None = None) -> bool:
        """Check if budget is exhausted."""
        return self.get_remaining(agent_id) <= 0


class BudgetExceededError(Exception):
    """Raised when budget is exceeded."""

    def __init__(self, agent_id: str, budget: float, spent: float) -> None:
        self.agent_id = agent_id
        self.budget = budget
        self.spent = spent
        super().__init__(f"Budget exceeded for {agent_id}: {spent}/{budget}")


__all__ = ["BudgetTracker", "BudgetExceededError"]
