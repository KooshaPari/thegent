"""Crew executor for agent execution."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class CrewExecutor:
    """Execute crew tasks."""

    def __init__(self, crew: Any) -> None:
        """Initialize crew executor.

        Args:
            crew: Crew instance
        """
        self.crew = crew

    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        """Execute a task.

        Args:
            task: Task dictionary

        Returns:
            Execution result
        """
        logger.info("Executing task via crew executor")
        return self.crew.execute(task)

    def execute_async(self, task: dict[str, Any]) -> Any:
        """Execute task asynchronously.

        Args:
            task: Task dictionary

        Returns:
            Async result
        """
        # Implementation would use async execution
        return self.execute(task)
