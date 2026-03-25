#!/usr/bin/env python3
"""Agent Identity & Discovery System for Multi-Tenant Civilization.

Provides:
- Unique agent ID generation and persistence
- Global registry for agent discovery across projects
- Service discovery mechanism (file-based with MCP fallback)
- Agent relationship tracking (L1/L2/L3 hierarchy)
- Cross-project communication support
"""

import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import time


class AgentLevel(Enum):
    """Agent level in hierarchy."""

    L1_STRATEGIC = "L1"  # Strategic lead, orchestrator
    L2_WORKER = "L2"  # Named teammate, component owner
    L3_EXECUTOR = "L3"  # Free tier executor, sub-task worker


class AgentRole(Enum):
    """Agent role type."""

    RESEARCHER = "researcher"
    BUILDER = "builder"
    INTEGRATOR = "integrator"
    COORDINATOR = "coordinator"
    MONITOR = "monitor"
    GENERIC = "generic"


@dataclass
class AgentIdentity:
    """Unique agent identity and metadata."""

    # Core identity
    project: str  # Project name or path
    uuid: str  # Unique identifier
    level: AgentLevel  # L1, L2, or L3
    role: AgentRole  # Role type

    # Timestamps
    created_at: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)

    # Capabilities and scope
    capabilities: list[str] = field(default_factory=list)  # What this agent can do
    scope_tags: dict[str, str] = field(default_factory=dict)  # Key metadata tags

    # Relationships
    parent_agent_id: Optional[str] = None  # L2 reports to L1, L3 reports to L2
    child_agent_ids: list[str] = field(default_factory=list)  # L1 manages L2s, L2 manages L3s
    peer_agent_ids: list[str] = field(default_factory=list)  # Same level coordination

    # Status
    is_active: bool = True
    status_message: str = "healthy"

    # Communication
    session_id: Optional[str] = None  # Current session or MCP connection
    mcp_endpoint: Optional[str] = None  # MCP server endpoint if available

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "project": self.project,
            "uuid": self.uuid,
            "level": self.level.value,
            "role": self.role.value,
            "created_at": self.created_at,
            "last_heartbeat": self.last_heartbeat,
            "capabilities": self.capabilities,
            "scope_tags": self.scope_tags,
            "parent_agent_id": self.parent_agent_id,
            "child_agent_ids": self.child_agent_ids,
            "peer_agent_ids": self.peer_agent_ids,
            "is_active": self.is_active,
            "status_message": self.status_message,
            "session_id": self.session_id,
            "mcp_endpoint": self.mcp_endpoint,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentIdentity":
        """Create from dictionary."""
        data = data.copy()
        if "level" in data and isinstance(data["level"], str):
            data["level"] = AgentLevel(data["level"])
        if "role" in data and isinstance(data["role"], str):
            data["role"] = AgentRole(data["role"])
        return cls(**data)

    @property
    def agent_id(self) -> str:
        """Get unique agent ID string: {project}:{uuid}:L{1-3}:{role}"""
        return f"{self.project}:{self.uuid}:{self.level.value}:{self.role.value}"

    @property
    def is_stale(self, ttl_seconds: int = 300) -> bool:  # noqa: PLR0206
        """Check if agent heartbeat is stale (default 5 minutes)."""
        return (time.time() - self.last_heartbeat) > ttl_seconds


class GlobalAgentRegistry:
    """Central registry for all agents across projects.

    Location: ~/.claude/civilization/registry.json
    Provides service discovery and agent relationship tracking.
    """

    def __init__(self, registry_path: Optional[str] = None):
        """Initialize registry.

        Args:
            registry_path: Path to registry file. Defaults to ~/.claude/civilization/registry.json
        """
        if registry_path is None:
            registry_path = Path("~/.claude/civilization/registry.json").expanduser()

        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

        # In-memory cache (synced to disk on changes)
        self.agents: dict[str, AgentIdentity] = {}
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        """Load registry from disk."""
        if self.registry_path.exists():
            try:
                with open(self.registry_path) as f:
                    data = json.load(f)
                    self.agents = {
                        agent_id: AgentIdentity.from_dict(agent_data) for agent_id, agent_data in data.items()
                    }
                self.logger.info(f"Loaded {len(self.agents)} agents from registry")
            except Exception as e:
                self.logger.error(f"Failed to load registry: {e}")
                self.agents = {}

    def _save_to_disk(self) -> None:
        """Save registry to disk."""
        try:
            data = {agent_id: agent.to_dict() for agent_id, agent in self.agents.items()}
            with open(self.registry_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save registry: {e}")

    def register_agent(self, identity: AgentIdentity) -> str:
        """Register a new agent or update existing.

        Args:
            identity: Agent identity

        Returns:
            Agent ID string
        """
        agent_id = identity.agent_id
        identity.last_heartbeat = time.time()
        self.agents[agent_id] = identity
        self._save_to_disk()
        self.logger.info(f"Registered agent: {agent_id}")
        return agent_id

    def unregister_agent(self, agent_id: str) -> bool:
        """Remove agent from registry.

        Args:
            agent_id: Agent ID to remove

        Returns:
            True if found and removed, False if not found
        """
        if agent_id in self.agents:
            self.agents.pop(agent_id)
            # Clean up relationships
            for other in self.agents.values():
                if agent_id in other.child_agent_ids:
                    other.child_agent_ids.remove(agent_id)
                if agent_id in other.peer_agent_ids:
                    other.peer_agent_ids.remove(agent_id)
            self._save_to_disk()
            self.logger.info(f"Unregistered agent: {agent_id}")
            return True
        return False

    def get_agent(self, agent_id: str) -> Optional[AgentIdentity]:
        """Get agent by ID."""
        return self.agents.get(agent_id)

    def get_agents_by_project(self, project: str) -> list[AgentIdentity]:
        """Get all agents for a project."""
        return [a for a in self.agents.values() if a.project == project]

    def get_agents_by_level(self, level: AgentLevel) -> list[AgentIdentity]:
        """Get all agents at a specific level."""
        return [a for a in self.agents.values() if a.level == level]

    def get_agents_by_role(self, role: AgentRole) -> list[AgentIdentity]:
        """Get all agents with a specific role."""
        return [a for a in self.agents.values() if a.role == role]

    def get_active_agents(self) -> list[AgentIdentity]:
        """Get all active agents."""
        return [a for a in self.agents.values() if a.is_active]

    def get_stale_agents(self, ttl_seconds: int = 300) -> list[AgentIdentity]:
        """Get agents with stale heartbeats."""
        cutoff_time = time.time() - ttl_seconds
        return [a for a in self.agents.values() if a.last_heartbeat < cutoff_time]

    def update_heartbeat(self, agent_id: str) -> bool:
        """Update agent heartbeat.

        Args:
            agent_id: Agent ID

        Returns:
            True if updated, False if agent not found
        """
        if agent_id in self.agents:
            self.agents[agent_id].last_heartbeat = time.time()
            self._save_to_disk()
            return True
        return False

    def set_relationship(self, parent_id: str, child_id: str) -> bool:
        """Set parent-child relationship.

        Args:
            parent_id: Parent agent ID (L1 or L2)
            child_id: Child agent ID (L2 or L3)

        Returns:
            True if set successfully, False if agents not found
        """
        parent = self.agents.get(parent_id)
        child = self.agents.get(child_id)

        if not parent or not child:
            return False

        if child_id not in parent.child_agent_ids:
            parent.child_agent_ids.append(child_id)
        child.parent_agent_id = parent_id

        self._save_to_disk()
        self.logger.info(f"Set relationship: {parent_id} -> {child_id}")
        return True

    def get_hierarchy(self, agent_id: str, levels: int = 3) -> dict[str, Any]:
        """Get agent hierarchy (self + children + grandchildren).

        Args:
            agent_id: Root agent ID
            levels: How many levels down to fetch

        Returns:
            Dictionary with agent hierarchy
        """
        agent = self.get_agent(agent_id)
        if not agent:
            return {}

        hierarchy = {
            "agent_id": agent_id,
            "identity": agent.to_dict(),
            "children": [],
        }

        if levels > 1:
            for child_id in agent.child_agent_ids:
                child_hierarchy = self.get_hierarchy(child_id, levels - 1)
                if child_hierarchy:
                    hierarchy["children"].append(child_hierarchy)

        return hierarchy

    def list_all_agents(self) -> list[str]:
        """Get list of all agent IDs."""
        return list(self.agents.keys())

    def get_stats(self) -> dict[str, Any]:
        """Get registry statistics."""
        agents_by_level = {}
        agents_by_role = {}
        agents_by_project = {}

        for agent in self.agents.values():
            level_key = agent.level.value
            role_key = agent.role.value
            project_key = agent.project

            agents_by_level[level_key] = agents_by_level.get(level_key, 0) + 1
            agents_by_role[role_key] = agents_by_role.get(role_key, 0) + 1
            agents_by_project[project_key] = agents_by_project.get(project_key, 0) + 1

        return {
            "total_agents": len(self.agents),
            "active_agents": len(self.get_active_agents()),
            "stale_agents": len(self.get_stale_agents()),
            "by_level": agents_by_level,
            "by_role": agents_by_role,
            "by_project": agents_by_project,
        }


class AgentIdentityFactory:
    """Factory for creating new agents with proper identity."""

    def __init__(self, registry: GlobalAgentRegistry):
        """Initialize factory.

        Args:
            registry: Global agent registry
        """
        self.registry = registry

    def create_l1_agent(
        self,
        project: str,
        role: AgentRole = AgentRole.COORDINATOR,
        capabilities: Optional[list[str]] = None,
        scope_tags: Optional[dict[str, str]] = None,
    ) -> AgentIdentity:
        """Create L1 strategic agent.

        Args:
            project: Project name
            role: Agent role
            capabilities: List of capabilities
            scope_tags: Metadata tags

        Returns:
            New L1 agent identity
        """
        identity = AgentIdentity(
            project=project,
            uuid=str(uuid.uuid4())[:8],
            level=AgentLevel.L1_STRATEGIC,
            role=role,
            capabilities=capabilities or ["orchestration", "monitoring", "escalation"],
            scope_tags=scope_tags or {"tier": "strategic"},
        )
        self.registry.register_agent(identity)
        return identity

    def create_l2_agent(
        self,
        project: str,
        role: AgentRole,
        parent_l1_id: str,
        capabilities: Optional[list[str]] = None,
        scope_tags: Optional[dict[str, str]] = None,
    ) -> AgentIdentity:
        """Create L2 worker agent.

        Args:
            project: Project name
            role: Agent role
            parent_l1_id: Parent L1 agent ID
            capabilities: List of capabilities
            scope_tags: Metadata tags

        Returns:
            New L2 agent identity
        """
        identity = AgentIdentity(
            project=project,
            uuid=str(uuid.uuid4())[:8],
            level=AgentLevel.L2_WORKER,
            role=role,
            parent_agent_id=parent_l1_id,
            capabilities=capabilities or ["component_execution", "sub_delegation"],
            scope_tags=scope_tags or {"tier": "worker"},
        )
        self.registry.register_agent(identity)
        self.registry.set_relationship(parent_l1_id, identity.agent_id)
        return identity

    def create_l3_agent(
        self,
        project: str,
        parent_l2_id: str,
        capabilities: Optional[list[str]] = None,
        scope_tags: Optional[dict[str, str]] = None,
    ) -> AgentIdentity:
        """Create L3 executor agent.

        Args:
            project: Project name
            parent_l2_id: Parent L2 agent ID
            capabilities: List of capabilities
            scope_tags: Metadata tags

        Returns:
            New L3 agent identity
        """
        identity = AgentIdentity(
            project=project,
            uuid=str(uuid.uuid4())[:8],
            level=AgentLevel.L3_EXECUTOR,
            role=AgentRole.GENERIC,  # L3s are generic executors
            parent_agent_id=parent_l2_id,
            capabilities=capabilities or ["task_execution", "reporting"],
            scope_tags=scope_tags or {"tier": "executor", "free_tier": "true"},
        )
        self.registry.register_agent(identity)
        self.registry.set_relationship(parent_l2_id, identity.agent_id)
        return identity


def main():
    """Example usage."""
    logging.basicConfig(level=logging.INFO)

    # Initialize registry
    registry = GlobalAgentRegistry()
    factory = AgentIdentityFactory(registry)

    # Create L1 agent
    l1_agent = factory.create_l1_agent("thegent", AgentRole.COORDINATOR)
    print(f"Created L1 agent: {l1_agent.agent_id}")

    # Create L2 agents
    l2_researcher = factory.create_l2_agent(
        "thegent",
        AgentRole.RESEARCHER,
        l1_agent.agent_id,
        capabilities=["research", "analysis"],
    )
    print(f"Created L2 agent: {l2_researcher.agent_id}")

    l2_builder = factory.create_l2_agent(
        "thegent",
        AgentRole.BUILDER,
        l1_agent.agent_id,
        capabilities=["implementation", "testing"],
    )
    print(f"Created L2 agent: {l2_builder.agent_id}")

    # Create L3 agents
    l3_executor1 = factory.create_l3_agent("thegent", l2_researcher.agent_id)
    print(f"Created L3 agent: {l3_executor1.agent_id}")

    l3_executor2 = factory.create_l3_agent("thegent", l2_builder.agent_id)
    print(f"Created L3 agent: {l3_executor2.agent_id}")

    # Show hierarchy
    print("\nHierarchy:")
    hierarchy = registry.get_hierarchy(l1_agent.agent_id)
    print(json.dumps(hierarchy, indent=2))

    # Show stats
    print("\nRegistry stats:")
    print(json.dumps(registry.get_stats(), indent=2))


if __name__ == "__main__":
    main()
