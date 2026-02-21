"""Port dex flash agents to other projects."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class DexFlashAgents:
    """Dex flash agents port."""

    def __init__(self) -> None:
        """Initialize dex flash agents."""
        self.agents: dict[str, Any] = {}

    def register_flash_agent(self, name: str, agent: Any) -> None:
        """Register a flash agent.

        Args:
            name: Agent name
            agent: Agent implementation
        """
        self.agents[name] = agent
        logger.info(f"Registered flash agent: {name}")

    def flash_execute(self, agent_name: str, command: str) -> dict[str, Any]:
        """Execute flash command.

        Args:
            agent_name: Agent name
            command: Command to execute

        Returns:
            Execution result
        """
        agent = self.agents.get(agent_name)
        if not agent:
            return {"error": f"Flash agent {agent_name} not found"}

        logger.info(f"Flash executing: {command}")
        return {"status": "success", "command": command}
