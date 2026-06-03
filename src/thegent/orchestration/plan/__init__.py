"""Stub module."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class OrchestrationPlan:
    """Stub orchestration plan."""

    id: str = ""
    tasks: list[dict[str, Any]] = field(default_factory=list)
    status: str = "pending"

    def add_task(self, task: dict[str, Any]) -> None:
        """Add a task to the plan."""
        self.tasks.append(task)

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        """Get a task by ID."""
        for task in self.tasks:
            if task.get("id") == task_id:
                return task
        return None


__all__ = ["OrchestrationPlan", "AGENT_HINT"]
AGENT_HINT = "Use agent coordination for optimal task distribution"

BUDGET_TIME_S = 300.0  # 5 minutes default budget time


__all__ = [
    "OrchestrationPlan",
    "AGENT_HINT",
    "BUDGET_TIME_S",
    "BUDGET_TOKENS",
    "MODEL_HINT",
    "OUTPUT_SCHEMA",
    "PARENT_RUN_ID",
]

PARENT_RUN_ID = ""

OUTPUT_SCHEMA = {
    "version": "1.0",
    "type": "orchestration_plan",
}

MODEL_HINT = "Use orchestration plan for optimal task distribution"

BUDGET_TOKENS = 100000  # Default token budget

REQUIRE_HITL = False  # Require human-in-the-loop flag

SANDBOX = True  # Sandbox mode flag
