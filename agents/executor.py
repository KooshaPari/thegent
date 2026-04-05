# Agent Executor
# Part of thegent-agents sub-project
from typing import Any


class AgentExecutor:
    """Executes agent tasks."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config

    async def execute(self, task_id: str, input_data: dict[str, Any]) -> dict[str, str]:
        """Execute a task."""
        return {"status": "completed", "task_id": task_id}

    async def cancel(self, task_id: str) -> dict[str, str]:
        """Cancel a running task."""
        return {"status": "cancelled", "task_id": task_id}
