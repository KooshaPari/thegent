"""Agent hierarchy manager implementation."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class AgentHierarchyManager:
    """Manager for agent hierarchy."""

    def __init__(self) -> None:
        """Initialize agent hierarchy manager."""
        self.hierarchy: dict[str, Any] = {}
        self.agents: dict[str, Any] = {}

    def register_agent(
        self, agent_id: str, parent_id: str | None = None, metadata: dict[str, Any] | None = None
    ) -> None:
        """Register an agent in the hierarchy.

        Args:
            agent_id: Agent identifier
            parent_id: Parent agent ID (None for root)
            metadata: Agent metadata
        """
        self.agents[agent_id] = {
            "id": agent_id,
            "parent": parent_id,
            "metadata": metadata or {},
        }
        logger.info(f"Registered agent: {agent_id}")

    def get_children(self, agent_id: str) -> list[str]:
        """Get child agents.

        Args:
            agent_id: Parent agent ID

        Returns:
            List of child agent IDs
        """
        return [aid for aid, agent in self.agents.items() if agent.get("parent") == agent_id]

    def get_hierarchy_path(self, agent_id: str) -> list[str]:
        """Get hierarchy path from root to agent.

        Args:
            agent_id: Agent ID

        Returns:
            List of agent IDs from root to agent
        """
        path = [agent_id]
        current = self.agents.get(agent_id)
        while current and current.get("parent"):
            path.insert(0, current["parent"])
            current = self.agents.get(current["parent"])
        return path
