# Agent Executor
# Part of thegent-agents sub-project


class AgentExecutor:
    """Executes agent tasks."""

    def __init__(self, config=None):
        self.config = config

    async def execute(self, task_id: str, input_data: dict):
        """Execute a task."""
        return {"status": "completed", "task_id": task_id}

    async def cancel(self, task_id: str):
        """Cancel a running task."""
        return {"status": "cancelled", "task_id": task_id}
