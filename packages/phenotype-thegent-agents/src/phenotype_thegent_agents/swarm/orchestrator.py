"""
Swarm Orchestrator

Coordinates multi-agent swarm execution.
"""

from dataclasses import dataclass
from typing import Optional, Any
from .communication import SwarmChannel, Message
from .balancer import LoadBalancer
import time
import uuid


@dataclass
class Task:
    """Task for swarm execution."""

    id: str
    task_type: str
    payload: Any
    priority: int = 0
    dependencies: list[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class TaskResult:
    """Result of swarm task."""

    task_id: str
    agent_id: str
    success: bool
    output: Any
    duration: float


class SwarmOrchestrator:
    """Orchestrates swarm of agents."""

    def __init__(self, channel: Optional[SwarmChannel] = None):
        self.channel = channel or SwarmChannel()
        self.balancer = LoadBalancer()
        self._pending: dict[str, Task] = {}
        self._running: dict[str, tuple[Task, str]] = {}  # task_id -> (task, agent_id)
        self._completed: dict[str, TaskResult] = {}

    def register_agent(self, agent_id: str, specialization: str, max_tasks: int = 5) -> None:
        """Register an agent with the swarm."""
        self.balancer.register(agent_id, specialization, max_tasks)

    def submit(self, task: Task) -> str:
        """Submit a task to the swarm."""
        if not task.id:
            task.id = str(uuid.uuid4())[:8]

        self._pending[task.id] = task
        return task.id

    def decompose(self, task: Task) -> list[Task]:
        """Decompose complex task into subtasks."""
        subtasks = []
        # Simple decomposition by task type
        if task.task_type == "refactor":
            subtasks = [
                Task(id=f"{task.id}_analyze", task_type="analyze", payload=task.payload),
                Task(id=f"{task.id}_code", task_type="code", payload=task.payload, dependencies=[f"{task.id}_analyze"]),
                Task(id=f"{task.id}_test", task_type="test", payload=task.payload, dependencies=[f"{task.id}_code"]),
            ]
        elif task.task_type == "implement":
            subtasks = [
                Task(id=f"{task.id}_design", task_type="design", payload=task.payload),
                Task(id=f"{task.id}_code", task_type="code", payload=task.payload, dependencies=[f"{task.id}_design"]),
                Task(id=f"{task.id}_test", task_type="test", payload=task.payload, dependencies=[f"{task.id}_code"]),
            ]
        else:
            subtasks = [task]

        return subtasks

    def tick(self) -> list[TaskResult]:
        """Process one orchestration cycle."""
        results = []

        # Check for completed tasks from agents
        for agent_id in self.balancer._agents:
            msg = self.channel.receive(agent_id, timeout=0.001)
            if msg and msg.message_type == "task_complete":
                result = self._handle_completion(msg)
                if result:
                    results.append(result)

        # Assign pending tasks
        ready = self._get_ready_tasks()
        for task in ready:
            agent_id = self.balancer.select(task.task_type)
            if agent_id and self.balancer.assign(agent_id):
                self._dispatch(task, agent_id)

        return results

    def _get_ready_tasks(self) -> list[Task]:
        """Get tasks ready for execution."""
        ready = []
        for task_id, task in list(self._pending.items()):
            if all(dep in self._completed for dep in task.dependencies):
                ready.append(task)
                del self._pending[task_id]
        return sorted(ready, key=lambda t: -t.priority)

    def _dispatch(self, task: Task, agent_id: str) -> None:
        """Dispatch task to agent."""
        self._running[task.id] = (task, agent_id)
        self.channel.send(
            Message(
                sender="orchestrator",
                receiver=agent_id,
                message_type="task_assign",
                payload=task,
                timestamp=time.time(),
            )
        )

    def _handle_completion(self, msg: Message) -> Optional[TaskResult]:
        """Handle task completion message."""
        payload = msg.payload
        task_id = payload.get("task_id")
        agent_id = msg.sender

        if task_id not in self._running:
            return None

        _, _ = self._running.pop(task_id)
        self.balancer.complete(agent_id, payload.get("duration", 0))

        result = TaskResult(
            task_id=task_id,
            agent_id=agent_id,
            success=payload.get("success", False),
            output=payload.get("output"),
            duration=payload.get("duration", 0),
        )
        self._completed[task_id] = result

        return result

    def status(self) -> dict:
        """Get swarm status."""
        return {
            "pending": len(self._pending),
            "running": len(self._running),
            "completed": len(self._completed),
            "channel": self.channel.stats(),
            "balancer": self.balancer.stats(),
        }
