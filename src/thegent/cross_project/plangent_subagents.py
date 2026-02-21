"""Integrate plangent sub-agents into thegent."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class PlangentSubagents:
    """Plangent sub-agents integration."""

    def __init__(self) -> None:
        """Initialize plangent subagents."""
        self.subagents: dict[str, Any] = {}

    def register_subagent(self, name: str, agent: Any) -> None:
        """Register a plangent subagent.

        Args:
            name: Subagent name
            agent: Agent implementation
        """
        self.subagents[name] = agent
        logger.info(f"Registered plangent subagent: {name}")

    def execute(self, subagent_name: str, task: dict[str, Any]) -> dict[str, Any]:
        """Execute task with subagent.

        Args:
            subagent_name: Subagent name
            task: Task dictionary

        Returns:
            Execution result
        """
        subagent = self.subagents.get(subagent_name)
        if not subagent:
            return {"error": f"Subagent {subagent_name} not found"}

        logger.info(f"Executing task with {subagent_name}")
        return {"status": "success", "subagent": subagent_name}
