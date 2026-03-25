"""
Task Delegation

Async delegation with status tracking, priority, and timeout handling.
"""

from .registry import TeammateRegistry
from .status import TaskStatus, TaskResult
from dataclasses import dataclass
from typing import Optional
import time
import xml.etree.ElementTree as ET


@dataclass
class DelegationRequest:
    """Request to delegate a task."""
    teammate_id: str
    task: str
    priority: str = "NORMAL"
    timeout: float = 300.0
    metadata: Optional[dict] = None


class Delegate:
    """Handles task delegation to teammates."""

    def __init__(self, registry: Optional[TeammateRegistry] = None):
        self.registry = registry or TeammateRegistry()
        self._tasks: dict[str, TaskResult] = {}
        self._counter = 0

    def _generate_id(self) -> str:
        """Generate unique task ID."""
        self._counter += 1
        return f"task-{int(time.time())}-{self._counter}"

    def delegate(self, request: DelegationRequest) -> TaskResult:
        """Delegate task to a teammate."""
        teammate = self.registry.get(request.teammate_id)
        if not teammate:
            # Auto-discover
            self.registry.discover()
            teammate = self.registry.get(request.teammate_id)
            if not teammate:
                raise ValueError(f"Teammate not found: {request.teammate_id}")

        task_id = self._generate_id()
        result = TaskResult(
            id=task_id,
            status=TaskStatus.PENDING,
            teammate_id=request.teammate_id,
            task=request.task
        )
        self._tasks[task_id] = result

        # Create handoff XML
        handoff = self._create_handoff_xml(request, task_id)

        # TODO: Execute async delegation
        result.status = TaskStatus.QUEUED
        result.metadata = {"handoff": handoff}

        return result

    def _create_handoff_xml(self, request: DelegationRequest, task_id: str) -> str:
        """Create XML-based handoff protocol."""
        root = ET.Element("handoff")
        root.set("version", "1.0")

        task_elem = ET.SubElement(root, "task")
        task_elem.set("id", task_id)
        task_elem.set("priority", request.priority)

        assignee = ET.SubElement(root, "assignee")
        assignee.set("teammate", request.teammate_id)

        content = ET.SubElement(root, "content")
        content.text = request.task

        if request.metadata:
            meta = ET.SubElement(root, "metadata")
            for k, v in request.metadata.items():
                meta.set(k, str(v))

        return ET.tostring(root, encoding="unicode")

    def status(self, task_id: str) -> Optional[TaskResult]:
        """Get status of delegated task."""
        return self._tasks.get(task_id)

    def cancel(self, task_id: str) -> bool:
        """Cancel a delegated task."""
        task = self._tasks.get(task_id)
        if task and task.status in (TaskStatus.PENDING, TaskStatus.QUEUED):
            task.status = TaskStatus.CANCELLED
            return True
        return False

    def list_active(self) -> list[TaskResult]:
        """List all active tasks."""
        return [
            t for t in self._tasks.values()
            if t.status in (TaskStatus.PENDING, TaskStatus.QUEUED, TaskStatus.RUNNING)
        ]
