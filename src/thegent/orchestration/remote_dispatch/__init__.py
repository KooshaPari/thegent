"""Stub module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RemoteDispatchConfig:
    """Configuration for remote dispatch."""

    endpoint: str = "http://localhost:8000"
    timeout: int = 30
    max_retries: int = 3


class RemoteDispatchBackend:
    """Backend for remote dispatch operations."""

    def __init__(self) -> None:
        self.tasks: dict[str, Any] = {}

    def dispatch(self, task: dict[str, Any]) -> str:
        """Dispatch a task to remote backend."""
        task_id = f"task_{len(self.tasks)}"
        self.tasks[task_id] = task
        return task_id

    def status(self, task_id: str) -> dict[str, Any]:
        """Get status of a dispatched task."""
        return self.tasks.get(task_id, {})


def adapt_request_to_agent_task(request: dict[str, Any]) -> dict[str, Any]:
    """Adapt an incoming request to an agent task format.

    Args:
        request: The incoming request dictionary.

    Returns:
        Adapted task dictionary.
    """
    return {
        "task_id": request.get("id", ""),
        "payload": request.get("payload", {}),
        "metadata": request.get("metadata", {}),
    }


def adapt_result_to_sub_agent_result(result: Any) -> dict[str, Any]:
    """Adapt a result to sub-agent result format.

    Args:
        result: The result from a sub-agent.

    Returns:
        Adapted result dictionary.
    """
    return {
        "status": "success",
        "data": result,
    }


__all__ = [
    "RemoteDispatchBackend",
    "RemoteDispatchConfig",
    "adapt_request_to_agent_task",
    "adapt_result_to_sub_agent_result",
]
