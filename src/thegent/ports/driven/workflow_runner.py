"""Protocol for workflow/pipeline execution."""

from __future__ import annotations

from typing import Any, Protocol


class WorkflowRunner(Protocol):
    """Port interface for workflow and pipeline execution.

    Breaks cli ↔ workflow circular dependency by allowing CLI code
    to invoke workflows without importing workflow orchestration details.
    """

    async def run_workflow(self, workflow_id: str, params: dict[str, Any]) -> dict[str, Any]:
        """Execute a workflow asynchronously.

        Args:
            workflow_id: Identifier for the workflow to execute.
            params: Parameters to pass to the workflow.

        Returns:
            Workflow execution result (structure depends on specific workflow).
        """
        ...

    async def get_workflow_status(self, run_id: str) -> str:
        """Get the status of a running or completed workflow execution.

        Args:
            run_id: Identifier for a specific workflow run.

        Returns:
            Status string (e.g., 'pending', 'running', 'completed', 'failed').
        """
        ...


__all__ = [
    "WorkflowRunner",
]
