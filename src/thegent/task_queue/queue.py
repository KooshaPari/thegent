"""Task queue system."""

import logging
from collections import deque
from typing import Any

logger = logging.getLogger(__name__)


class TaskQueue:
    """Task queue implementation."""

    TRANSIENT_FAILURE_CLASSES: frozenset[str] = frozenset({"timeout", "rate_limit", "network", "remote_5xx"})

    def __init__(self) -> None:
        """Initialize task queue."""
        self.queue: deque = deque()
        self.retry_queue: deque = deque()
        self.processing: set[str] = set()
        self.completed: set[str] = set()

    def enqueue(self, task_id: str, task: dict[str, Any]) -> None:
        """Enqueue a task.

        Args:
            task_id: Task identifier
            task: Task dictionary
        """
        self.queue.append((task_id, task))
        logger.info(f"Enqueued task: {task_id}")

    def enqueue_retry(self, task_id: str, task: dict[str, Any], *, failure_class: str) -> bool:
        """Enqueue transient failure for selective retry.

        Returns:
            True if enqueued, False if skipped.
        """
        if task_id in self.completed:
            return False
        normalized = failure_class.strip().lower()
        if normalized not in self.TRANSIENT_FAILURE_CLASSES:
            return False
        for retry_task_id, _retry_task, retry_class in self.retry_queue:
            if retry_task_id == task_id and retry_class == normalized:
                return False
        self.retry_queue.append((task_id, task, normalized))
        logger.info("Enqueued retry task: %s (%s)", task_id, normalized)
        return True

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

    def dequeue_retry(self) -> tuple[str, dict[str, Any]] | None:
        """Dequeue next retry task."""
        if not self.retry_queue:
            return None
        task_id, task, _failure_class = self.retry_queue.popleft()
        self.processing.add(task_id)
        return task_id, task

    def complete(self, task_id: str) -> None:
        """Mark task as complete.

        Args:
            task_id: Task identifier
        """
        self.processing.discard(task_id)
        self.completed.add(task_id)
        self.retry_queue = deque(
            (retry_task_id, retry_task, retry_class)
            for retry_task_id, retry_task, retry_class in self.retry_queue
            if retry_task_id != task_id
        )
        logger.info(f"Completed task: {task_id}")
