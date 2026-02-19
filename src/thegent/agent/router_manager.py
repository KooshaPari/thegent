"""Router manager for agent routing."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class RouterManager:
    """Manage routing of tasks to agents."""

    def __init__(self):
        """Initialize router manager."""
        self.routes: dict[str, Any] = {}

    def register_route(self, pattern: str, agent: Any) -> None:
        """Register a routing pattern.
        
        Args:
            pattern: Route pattern
            agent: Agent to route to
        """
        self.routes[pattern] = agent
        logger.info(f"Registered route: {pattern}")

    def route(self, task: dict[str, Any]) -> Any:
        """Route a task to an agent.
        
        Args:
            task: Task dictionary
            
        Returns:
            Routed agent
        """
        # Simple routing logic - would be more sophisticated in production
        task_type = task.get("type", "default")
        agent = self.routes.get(task_type)
        
        if not agent:
            agent = self.routes.get("default")
        
        logger.info(f"Routed task {task_type} to agent")
        return agent
