"""Phase 5C: Civilization-wide Dashboards for real-time status monitoring.

Generates three dashboard types:
1. Overview: Civilization-wide agent status and metrics
2. Project: Project-specific agent hierarchy and activity
3. Agent: Agent-specific details, metrics, and relationships
"""

import time
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any
from pathlib import Path
import json

# Conditional imports for agent identity and memory systems
try:
    from agent_identity_system import GlobalAgentRegistry

    AGENT_IDENTITY_AVAILABLE = True
except ImportError:
    try:
        from scripts.agent_identity_system import GlobalAgentRegistry

        AGENT_IDENTITY_AVAILABLE = True
    except ImportError:
        GlobalAgentRegistry = None
        AGENT_IDENTITY_AVAILABLE = False

try:
    from civilization_agent_memory import MemoryService

    MEMORY_AVAILABLE = True
except ImportError:
    try:
        from scripts.civilization_agent_memory import MemoryService

        MEMORY_AVAILABLE = True
    except ImportError:
        MemoryService = None
        MEMORY_AVAILABLE = False

try:
    from civilization_conflict_resolver import ConflictResolver

    CONFLICT_AVAILABLE = True
except ImportError:
    try:
        from scripts.civilization_conflict_resolver import ConflictResolver

        CONFLICT_AVAILABLE = True
    except ImportError:
        ConflictResolver = None
        CONFLICT_AVAILABLE = False

try:
    from civilization_memory_analytics import MemoryAnalytics

    _ANALYTICS_AVAILABLE = True
except ImportError:
    try:
        from scripts.civilization_memory_analytics import MemoryAnalytics

        _ANALYTICS_AVAILABLE = True
    except ImportError:
        MemoryAnalytics = None
        _ANALYTICS_AVAILABLE = False


@dataclass
class AgentStatus:
    """Status snapshot of an agent."""

    agent_id: str
    level: str
    project: str
    status: str  # "active", "stale", "unknown"
    last_heartbeat: Optional[float] = None
    created_at: Optional[float] = None
    parent_id: Optional[str] = None
    children_ids: list[str] = field(default_factory=list)


@dataclass
class MetricsSnapshot:
    """Aggregated metrics for an agent."""

    task_count: int = 0
    error_count: int = 0
    success_rate: float = 0.0
    learning_count: int = 0
    decision_count: int = 0
    average_importance: float = 0.0


@dataclass
class DashboardOverview:
    """Civilization-wide overview dashboard."""

    total_agents: int
    active_count: int
    stale_count: int
    by_level: dict[str, dict[str, int]]  # level -> {total, active, stale}
    by_project: dict[str, dict[str, int]]  # project -> {total, active, stale}
    timestamp: float


@dataclass
class DashboardProject:
    """Project-specific dashboard."""

    project: str
    agent_count: int
    hierarchy: dict[str, Any]  # Tree structure of agents
    recent_activity: list[dict[str, Any]]
    conflicts: list[dict[str, Any]]
    timestamp: float


@dataclass
class DashboardAgent:
    """Agent-specific detail dashboard."""

    agent_id: str
    status: str
    level: str
    last_heartbeat_seconds_ago: Optional[float]
    created_seconds_ago: Optional[float]
    metrics: MetricsSnapshot
    memory_summary: dict[str, Any]
    relationships: dict[str, Any]
    timestamp: float
    analytics: dict[str, Any] = field(default_factory=dict)


class DashboardService:
    """Generate real-time dashboards for civilization monitoring."""

    def __init__(
        self,
        registry: Optional[Any] = None,
        memory_service: Optional[Any] = None,
        conflict_resolver: Optional[Any] = None,
    ):
        """Initialize dashboard service with optional dependencies.

        Args:
            registry: GlobalAgentRegistry instance (auto-initialized if available)
            memory_service: MemoryService instance (auto-initialized if available)
            conflict_resolver: ConflictResolver instance (auto-initialized if available)
        """
        if registry is None and AGENT_IDENTITY_AVAILABLE:
            self.registry = GlobalAgentRegistry()
        else:
            self.registry = registry

        if memory_service is None and MEMORY_AVAILABLE:
            self.memory_service = MemoryService()
        else:
            self.memory_service = memory_service

        if conflict_resolver is None and CONFLICT_AVAILABLE:
            self.conflict_resolver = ConflictResolver()
        else:
            self.conflict_resolver = conflict_resolver

    def get_overview_dashboard(self) -> DashboardOverview:
        """Generate civilization-wide overview dashboard.

        Returns:
            DashboardOverview with agent counts, breakdown by level and project
        """
        if not self.registry:
            return self._empty_overview()

        agents = self.registry.agents.values()
        active_agents = [a for a in agents if self._is_agent_active(a)]
        stale_agents = [a for a in agents if self._is_agent_stale(a)]

        # Group by level
        by_level = {}
        for agent in agents:
            level = agent.level
            if level not in by_level:
                by_level[level] = {"total": 0, "active": 0, "stale": 0}
            by_level[level]["total"] += 1
            if agent in active_agents:
                by_level[level]["active"] += 1
            if agent in stale_agents:
                by_level[level]["stale"] += 1

        # Group by project
        by_project = {}
        for agent in agents:
            project = agent.project
            if project not in by_project:
                by_project[project] = {"total": 0, "active": 0, "stale": 0}
            by_project[project]["total"] += 1
            if agent in active_agents:
                by_project[project]["active"] += 1
            if agent in stale_agents:
                by_project[project]["stale"] += 1

        return DashboardOverview(
            total_agents=len(agents),
            active_count=len(active_agents),
            stale_count=len(stale_agents),
            by_level=by_level,
            by_project=by_project,
            timestamp=time.time(),
        )

    def get_project_dashboard(self, project: str) -> DashboardProject:
        """Generate project-specific dashboard.

        Args:
            project: Project identifier

        Returns:
            DashboardProject with hierarchy, activity, and conflicts
        """
        if not self.registry:
            return self._empty_project_dashboard(project)

        agents = [a for a in self.registry.agents.values() if a.project == project]

        # Build hierarchy
        hierarchy = self._build_project_hierarchy(project)

        # Get recent activity
        recent_activity = self._get_recent_activity(project)

        # Get conflicts for this project
        conflicts = self._get_project_conflicts(project)

        return DashboardProject(
            project=project,
            agent_count=len(agents),
            hierarchy=hierarchy,
            recent_activity=recent_activity,
            conflicts=conflicts,
            timestamp=time.time(),
        )

    def get_agent_dashboard(self, agent_id: str) -> Optional[DashboardAgent]:
        """Generate agent-specific detail dashboard.

        Args:
            agent_id: Agent identifier

        Returns:
            DashboardAgent with metrics, relationships, and memory summary, or None if not found
        """
        if not self.registry:
            return None

        agent = self.registry.get_agent(agent_id)
        if not agent:
            return None

        # Determine status
        status = "active" if self._is_agent_active(agent) else "stale"

        # Calculate time differences
        now = time.time()
        last_heartbeat_seconds_ago = None
        if agent.last_heartbeat:
            last_heartbeat_seconds_ago = now - agent.last_heartbeat

        created_seconds_ago = None
        if agent.created_at:
            created_seconds_ago = now - agent.created_at

        # Get metrics
        metrics = self._get_agent_metrics(agent_id)

        # Get memory summary
        memory_summary = self._get_memory_summary(agent_id)

        # Get relationships
        relationships = self._get_agent_relationships(agent_id, agent)

        # Get analytics summary (optional integration)
        analytics_summary = self._get_analytics_summary(agent_id)

        return DashboardAgent(
            agent_id=agent_id,
            status=status,
            level=agent.level,
            last_heartbeat_seconds_ago=last_heartbeat_seconds_ago,
            created_seconds_ago=created_seconds_ago,
            metrics=metrics,
            memory_summary=memory_summary,
            relationships=relationships,
            timestamp=time.time(),
            analytics=analytics_summary,
        )

    # ========== Private Helper Methods ==========

    def _is_agent_active(self, agent: Any) -> bool:
        """Check if agent is currently active.

        Args:
            agent: Agent from registry

        Returns:
            True if agent is active (recent heartbeat)
        """
        if not hasattr(agent, "last_heartbeat") or agent.last_heartbeat is None:
            return False

        # Agent is active if heartbeat within last 5 minutes
        time_since_heartbeat = time.time() - agent.last_heartbeat
        return time_since_heartbeat < 300

    def _is_agent_stale(self, agent: Any) -> bool:
        """Check if agent is stale.

        Args:
            agent: Agent from registry

        Returns:
            True if agent is stale (no heartbeat for >5 minutes)
        """
        if not hasattr(agent, "last_heartbeat") or agent.last_heartbeat is None:
            return True

        # Agent is stale if no heartbeat for >5 minutes
        time_since_heartbeat = time.time() - agent.last_heartbeat
        return time_since_heartbeat >= 300

    def _build_project_hierarchy(self, project: str) -> dict[str, Any]:
        """Build agent hierarchy tree for a project.

        Args:
            project: Project identifier

        Returns:
            Nested dict representing hierarchy with agents by level
        """
        if not self.registry:
            return {}

        hierarchy = {"L1": [], "L2": [], "L3": []}

        for agent in self.registry.agents.values():
            if agent.project == project:
                status = "active" if self._is_agent_active(agent) else "stale"
                children_count = 0
                if hasattr(agent, "children") and agent.children:
                    children_count = len(agent.children)
                agent_info = {
                    "id": agent.uuid,
                    "role": agent.role,
                    "status": status,
                    "children_count": children_count,
                }

                level_key = agent.level  # "L1", "L2", "L3"
                if level_key in hierarchy:
                    hierarchy[level_key].append(agent_info)

        return hierarchy

    def _get_recent_activity(self, project: str) -> list[dict[str, Any]]:
        """Get recent activity for a project.

        Args:
            project: Project identifier

        Returns:
            List of recent activity records
        """
        activity = []

        if not self.memory_service or not self.registry:
            return activity

        # Get agents in project
        agents = [a for a in self.registry.agents.values() if a.project == project]

        # Collect recent memories from all agents
        recent_memories = []
        for agent in agents:
            agent_id = agent.project_scoped_id
            memories = self.memory_service.query_memory(agent_id, limit=5)
            for memory in memories:
                recent_memories.append(
                    {
                        "agent_id": agent_id,
                        "timestamp": memory.timestamp,
                        "type": memory.memory_type.value,
                        "content": memory.content,
                    }
                )

        # Sort by timestamp (newest first) and limit to 10
        recent_memories.sort(key=lambda x: x["timestamp"], reverse=True)

        return recent_memories[:10]

    def _get_project_conflicts(self, project: str) -> list[dict[str, Any]]:
        """Get conflicts for a project.

        Args:
            project: Project identifier

        Returns:
            List of conflict records for the project
        """
        conflicts = []

        if not self.conflict_resolver:
            return conflicts

        # Get all conflicts and filter by project
        all_conflicts = self.conflict_resolver.get_unresolved_conflicts()

        for conflict in all_conflicts:
            # Check if conflict involves agents from this project
            if hasattr(conflict, "agents") and conflict.agents:
                conflict_agents = conflict.agents
                if any(agent.project == project for agent in conflict_agents):
                    conflicts.append(
                        {
                            "type": conflict.conflict_type.value
                            if hasattr(conflict.conflict_type, "value")
                            else str(conflict.conflict_type),
                            "agents": [str(a) for a in conflict_agents],
                            "detected_at": conflict.detected_at,
                            "status": conflict.status.value
                            if hasattr(conflict.status, "value")
                            else str(conflict.status),
                        }
                    )

        return conflicts

    def _get_agent_metrics(self, agent_id: str) -> MetricsSnapshot:
        """Get aggregated metrics for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            MetricsSnapshot with task/error/learning counts and rates
        """
        metrics = MetricsSnapshot()

        if not self.memory_service:
            return metrics

        try:
            stats = self.memory_service.get_agent_stats(agent_id)

            metrics.task_count = stats.get("total_memories", 0)
            metrics.error_count = stats.get("error_count", 0)
            metrics.success_rate = stats.get("success_rate", 0.0)
            metrics.learning_count = stats.get("learning_count", 0)
            metrics.decision_count = stats.get("decision_count", 0)
            metrics.average_importance = stats.get("average_importance", 0.0)
        except Exception:
            pass  # Return empty metrics if error

        return metrics

    def _get_memory_summary(self, agent_id: str) -> dict[str, Any]:
        """Get memory summary for an agent.

        Args:
            agent_id: Agent identifier

        Returns:
            Summary of agent's memories: learnings, errors, recent activities
        """
        summary = {
            "total_memories": 0,
            "recent_learnings": [],
            "recent_errors": [],
            "memory_types": {},
        }

        if not self.memory_service:
            return summary

        try:
            # Get stats
            stats = self.memory_service.get_agent_stats(agent_id)
            summary["total_memories"] = stats.get("total_memories", 0)
            summary["memory_types"] = stats.get("memory_types", {})

            # Get recent learnings
            learnings = self.memory_service.query_memory(agent_id, limit=3)
            summary["recent_learnings"] = [
                {
                    "timestamp": l.timestamp,
                    "content": l.content.get("learning", ""),
                }
                for l in learnings
                if hasattr(l, "memory_type") and l.memory_type.value == "learning"
            ]

            # Get recent errors (last 5)
            errors = self.memory_service.query_memory(agent_id, limit=5)
            summary["recent_errors"] = [
                {
                    "timestamp": e.timestamp,
                    "content": e.content.get("error", ""),
                }
                for e in errors
                if hasattr(e, "memory_type") and e.memory_type.value == "error"
            ]
        except Exception:
            pass  # Return partial summary if error

        return summary

    def _get_agent_relationships(self, agent_id: str, agent: Any) -> dict[str, Any]:
        """Get agent relationships (parent, siblings, children).

        Args:
            agent_id: Agent identifier
            agent: Agent object from registry

        Returns:
            Dictionary with parent, siblings, and children relationships
        """
        relationships = {
            "parent": None,
            "siblings": [],
            "children": [],
        }

        if not self.registry:
            return relationships

        # Get parent
        if hasattr(agent, "parent_id") and agent.parent_id:
            relationships["parent"] = agent.parent_id

        # Get children
        if hasattr(agent, "children") and agent.children:
            relationships["children"] = list(agent.children)

        # Get siblings (same parent, same level)
        if agent.parent_id:
            parent = self.registry.get_agent(agent.parent_id)
            if parent and hasattr(parent, "children") and parent.children:
                relationships["siblings"] = [c for c in parent.children if c != agent_id]

        return relationships

    def _get_analytics_summary(self, agent_id: str) -> dict[str, Any]:
        """Get analytics summary for an agent using MemoryAnalytics.

        Args:
            agent_id: Agent identifier

        Returns:
            Analytics summary dict, or empty dict if unavailable
        """
        if not _ANALYTICS_AVAILABLE or not self.memory_service:
            return {}

        try:
            memories = self.memory_service.query_memory(agent_id, limit=50)
            if not memories:
                return {}

            mem_dicts = []
            for m in memories:
                if hasattr(m, "__dict__"):
                    d = m.__dict__.copy()
                    if hasattr(m, "memory_type") and hasattr(m.memory_type, "value"):
                        d["memory_type"] = m.memory_type.value
                    mem_dicts.append(d)
                elif isinstance(m, dict):
                    mem_dicts.append(m)

            if not mem_dicts:
                return {}

            analytics = MemoryAnalytics()
            return analytics.get_agent_summary(mem_dicts)
        except Exception:
            return {}

    def _empty_overview(self) -> DashboardOverview:
        """Return empty overview dashboard."""
        return DashboardOverview(
            total_agents=0,
            active_count=0,
            stale_count=0,
            by_level={},
            by_project={},
            timestamp=time.time(),
        )

    def _empty_project_dashboard(self, project: str) -> DashboardProject:
        """Return empty project dashboard."""
        return DashboardProject(
            project=project,
            agent_count=0,
            hierarchy={},
            recent_activity=[],
            conflicts=[],
            timestamp=time.time(),
        )

    # ========== Serialization Helpers ==========

    def overview_to_dict(self, overview: DashboardOverview) -> dict[str, Any]:
        """Convert overview dashboard to dictionary for serialization.

        Args:
            overview: DashboardOverview

        Returns:
            Dictionary representation
        """
        return asdict(overview)

    def project_to_dict(self, project: DashboardProject) -> dict[str, Any]:
        """Convert project dashboard to dictionary for serialization.

        Args:
            project: DashboardProject

        Returns:
            Dictionary representation
        """
        return asdict(project)

    def agent_to_dict(self, agent: DashboardAgent) -> dict[str, Any]:
        """Convert agent dashboard to dictionary for serialization.

        Args:
            agent: DashboardAgent

        Returns:
            Dictionary representation
        """
        return asdict(agent)
