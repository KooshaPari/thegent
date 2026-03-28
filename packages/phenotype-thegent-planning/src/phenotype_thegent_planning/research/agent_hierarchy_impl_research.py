"""Research: Implement AgentHierarchyManager (Phase 1)."""

from typing import Any

from phenotype_thegent_planning.research.agent_hierarchy import AgentHierarchyManager


class AgentHierarchyImplResearch:
    """Research for agent hierarchy implementation."""

    def __init__(self) -> None:
        """Initialize agent hierarchy research."""
        self.manager = AgentHierarchyManager()

    def test_hierarchy(self) -> dict[str, Any]:
        """Test hierarchy functionality.

        Returns:
            Test results
        """
        self.manager.register_agent("agent-1", None, {"type": "root"})
        self.manager.register_agent("agent-2", "agent-1", {"type": "child"})
        return {
            "agents": len(self.manager.agents),
            "hierarchy": self.manager.get_hierarchy_path("agent-2"),
        }
