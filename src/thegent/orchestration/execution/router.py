"""WP-1001: Dependency-aware routing engine (FR-001)."""

import logging
from collections.abc import Iterable, Mapping
from graphlib import TopologicalSorter
from typing import Any

_log = logging.getLogger(__name__)


class DependencyRouter:
    """Dependency-aware routing engine for multi-task orchestration."""

    def __init__(self, dag: Mapping[str, Iterable[str]]) -> None:
        """
        Initialize with a DAG: task_id -> list of dependency task_ids.
        Example: {'B': ['A'], 'C': ['A'], 'D': ['B', 'C']}
        """
        self.dag = dag
        self.sorter = TopologicalSorter(dag)
        try:
            self.sorter.prepare()
        except Exception as e:
            _log.error("Invalid DAG provided to DependencyRouter: %s", e)
            raise
        self.completed_tasks: set[str] = set()
        self.running_tasks: set[str] = set()

    def get_ready_tasks(self) -> tuple[str, ...]:
        """Return task IDs that are ready to run (dependencies satisfied)."""
        return self.sorter.get_ready()

    def mark_started(self, task_id: str) -> None:
        """Mark a task as running."""
        self.running_tasks.add(task_id)

    def mark_completed(self, task_id: str) -> None:
        """Mark a task as completed and update the sorter."""
        if task_id in self.running_tasks:
            self.running_tasks.remove(task_id)
        self.completed_tasks.add(task_id)
        try:
            self.sorter.done(task_id)
        except ValueError:
            # Task might have already been marked done or wasn't ready
            _log.warning("Task %s was not in a state to be marked done", task_id)

    def is_finished(self) -> bool:
        """Return True if all tasks in the DAG are completed."""
        return not self.sorter.is_active()

    @classmethod
    def from_tasks(cls, tasks: list[dict[str, Any]]) -> "DependencyRouter":
        """Factory: Create router from a list of tasks with 'id' and 'depends_on'."""
        dag = {task["id"]: task.get("depends_on", []) for task in tasks}
        return cls(dag)
