"""
Load Balancer

Distributes tasks across agents based on load and specialization.
"""

from dataclasses import dataclass
from typing import Optional
from collections import defaultdict


@dataclass
class AgentLoad:
    """Load information for an agent."""
    agent_id: str
    specialization: str
    current_tasks: int
    max_tasks: int
    avg_task_time: float  # seconds

    @property
    def utilization(self) -> float:
        """Get utilization ratio (0-1)."""
        if self.max_tasks == 0:
            return 1.0
        return self.current_tasks / self.max_tasks

    @property
    def available_capacity(self) -> int:
        """Get remaining task capacity."""
        return max(0, self.max_tasks - self.current_tasks)


class LoadBalancer:
    """Distributes tasks across agents."""

    def __init__(self):
        self._agents: dict[str, AgentLoad] = {}
        self._specialization_index: dict[str, list[str]] = defaultdict(list)
        self._task_history: dict[str, list[float]] = defaultdict(list)

    def register(
        self,
        agent_id: str,
        specialization: str,
        max_tasks: int = 5
    ) -> None:
        """Register an agent."""
        self._agents[agent_id] = AgentLoad(
            agent_id=agent_id,
            specialization=specialization,
            current_tasks=0,
            max_tasks=max_tasks,
            avg_task_time=1.0
        )
        self._specialization_index[specialization].append(agent_id)

    def select(self, task_type: str) -> Optional[str]:
        """Select best agent for task type."""
        # Find agents with matching specialization
        candidates = self._specialization_index.get(task_type, [])

        if not candidates:
            # Fall back to any available agent
            candidates = list(self._agents.keys())

        if not candidates:
            return None

        # Select least loaded
        best = min(
            candidates,
            key=lambda aid: self._agents[aid].utilization
        )

        return best

    def assign(self, agent_id: str) -> bool:
        """Assign a task to an agent."""
        agent = self._agents.get(agent_id)
        if not agent:
            return False

        if agent.current_tasks >= agent.max_tasks:
            return False

        agent.current_tasks += 1
        return True

    def complete(self, agent_id: str, duration: float) -> None:
        """Mark task as complete."""
        agent = self._agents.get(agent_id)
        if agent:
            agent.current_tasks = max(0, agent.current_tasks - 1)

            # Update average task time
            history = self._task_history[agent_id]
            history.append(duration)
            if len(history) > 100:
                history.pop(0)
            agent.avg_task_time = sum(history) / len(history)

    def stats(self) -> dict:
        """Get load balancer statistics."""
        return {
            "agents": {
                aid: {
                    "specialization": a.specialization,
                    "utilization": a.utilization,
                    "current_tasks": a.current_tasks,
                    "avg_task_time": a.avg_task_time
                }
                for aid, a in self._agents.items()
            }
        }
