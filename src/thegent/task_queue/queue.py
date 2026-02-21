"""Task queue system."""

import logging
from collections import deque
from typing import Any

logger = logging.getLogger(__name__)


class TaskQueue:
    """Task queue implementation."""

    def __init__(self) -> None:
        """Initialize task queue."""
        self.queue: deque = deque()
        self.processing: set[str] = set()

    def enqueue(self, task_id: str, task: dict[str, Any]) -> None:
        """Enqueue a task.

        Args:
            task_id: Task identifier
            task: Task dictionary
        """
        self.queue.append((task_id, task))
        logger.info(f"Enqueued task: {task_id}")

    def dequeue(self) -> tuple[str, dict[str, Any]] | None:
        """Dequeue a task.

        Returns:
            Task tuple or None
        """
        if not self.queue:
            return None

        task_id, task = self.queue.popleft()
        self.processing.add(task_id)
        return task_id, task

    def complete(self, task_id: str) -> None:
        """Mark task as complete.

        Args:
            task_id: Task identifier
        """
        self.processing.discard(task_id)
        logger.info(f"Completed task: {task_id}")
