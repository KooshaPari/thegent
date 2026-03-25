"""Tests for Phase 5C: Dashboard Service.

Comprehensive tests covering:
- Dashboard generation (overview, project, agent)
- Metrics aggregation
- Status calculation
- Relationship tracking
- Empty/error cases
"""

import unittest
import time
from dataclasses import dataclass
from typing import Optional, List

from civilization_dashboard_service import (
    DashboardService,
    DashboardOverview,
    DashboardProject,
    DashboardAgent,
    MetricsSnapshot,
    AgentStatus,
)


# Mock objects for testing
@dataclass
class MockAgent:
    """Mock agent for testing."""

    uuid: str
    project: str
    level: str
    role: str
    last_heartbeat: Optional[float]
    created_at: Optional[float]
    parent_id: Optional[str] = None
    children: Optional[list[str]] = None

    @property
    def project_scoped_id(self) -> str:
        return f"{self.project}:{self.uuid}:{self.level}:{self.role}"


@dataclass
class MockMemory:
    """Mock memory record."""

    timestamp: float
    memory_type: any
    content: dict


@dataclass
class MockMemoryType:
    """Mock memory type enum value."""

    value: str


@dataclass
class MockConflict:
    """Mock conflict record."""

    conflict_type: MockMemoryType
    agents: list[MockAgent]
    detected_at: float
    status: MockMemoryType


class MockMemoryService:
    """Mock memory service for testing."""

    def __init__(self):
        self.memories = {}

    def get_agent_stats(self, agent_id: str) -> dict:
        """Get mock stats for agent."""
        if agent_id not in self.memories:
            return {
                "total_memories": 0,
                "memory_types": {},
                "error_count": 0,
                "success_rate": 0.0,
                "learning_count": 0,
                "decision_count": 0,
                "average_importance": 0.0,
            }

        stats = self.memories[agent_id]
        return {
            "total_memories": len(stats),
            "memory_types": {"execution": 5, "learning": 2, "error": 1},
            "error_count": 1,
            "success_rate": 0.8,
            "learning_count": 2,
            "decision_count": 1,
            "average_importance": 0.7,
        }

    def query_memory(self, agent_id: str, limit: Optional[int] = None):
        """Get mock memories for agent."""
        if agent_id not in self.memories:
            return []

        memories = self.memories[agent_id]
        if limit:
            memories = memories[:limit]

        return memories


class MockRegistry:
    """Mock agent registry for testing."""

    def __init__(self):
        self.agents = {}

    def get_agent(self, agent_id: str) -> Optional[MockAgent]:
        """Get agent by ID."""
        return self.agents.get(agent_id)

    def add_agent(self, agent: MockAgent):
        """Add agent to registry."""
        self.agents[agent.uuid] = agent


class MockConflictResolver:
    """Mock conflict resolver for testing."""

    def __init__(self):
        self.conflicts = []

    def get_unresolved_conflicts(self) -> list[MockConflict]:
        """Get unresolved conflicts."""
        return self.conflicts


# ========== Test Classes ==========


class TestOverviewDashboard(unittest.TestCase):
    """Test overview dashboard generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.registry = MockRegistry()
        self.service = DashboardService(
            registry=self.registry,
            memory_service=None,
            conflict_resolver=None,
        )

    def test_overview_empty_civilization(self):
        """Test overview with no agents."""
        overview = self.service.get_overview_dashboard()

        assert overview.total_agents == 0
        assert overview.active_count == 0
        assert overview.stale_count == 0
        assert overview.by_level == {}
        assert overview.by_project == {}

    def test_overview_all_active_agents(self):
        """Test overview with all active agents."""
        now = time.time()

        # Create 10 active agents (heartbeat within last 5 minutes)
        for i in range(10):
            agent = MockAgent(
                uuid=f"agent-{i}",
                project="test-project",
                level="L1" if i < 3 else "L2" if i < 8 else "L3",
                role="researcher",
                last_heartbeat=now - 60,  # 1 minute ago
                created_at=now - 3600,
            )
            self.registry.add_agent(agent)

        overview = self.service.get_overview_dashboard()

        assert overview.total_agents == 10
        assert overview.active_count == 10
        assert overview.stale_count == 0
        assert "L1" in overview.by_level
        assert "L2" in overview.by_level
        assert "L3" in overview.by_level
        assert "test-project" in overview.by_project

    def test_overview_mixed_active_and_stale(self):
        """Test overview with mix of active and stale agents."""
        now = time.time()

        # 5 active agents
        for i in range(5):
            agent = MockAgent(
                uuid=f"active-{i}",
                project="project-a",
                level="L1",
                role="researcher",
                last_heartbeat=now - 60,
                created_at=now - 3600,
            )
            self.registry.add_agent(agent)

        # 3 stale agents (no heartbeat for >5 minutes)
        for i in range(3):
            agent = MockAgent(
                uuid=f"stale-{i}",
                project="project-a",
                level="L2",
                role="executor",
                last_heartbeat=now - 600,  # 10 minutes ago
                created_at=now - 3600,
            )
            self.registry.add_agent(agent)

        overview = self.service.get_overview_dashboard()

        assert overview.total_agents == 8
        assert overview.active_count == 5
        assert overview.stale_count == 3

    def test_overview_by_project_grouping(self):
        """Test overview correctly groups agents by project."""
        now = time.time()

        # Create agents in different projects
        for i in range(5):
            agent = MockAgent(
                uuid=f"proj-a-{i}",
                project="project-alpha",
                level="L1",
                role="researcher",
                last_heartbeat=now - 60,
                created_at=now - 3600,
            )
            self.registry.add_agent(agent)

        for i in range(3):
            agent = MockAgent(
                uuid=f"proj-b-{i}",
                project="project-beta",
                level="L2",
                role="executor",
                last_heartbeat=now - 60,
                created_at=now - 3600,
            )
            self.registry.add_agent(agent)

        overview = self.service.get_overview_dashboard()

        assert overview.total_agents == 8
        assert overview.by_project["project-alpha"]["total"] == 5
        assert overview.by_project["project-beta"]["total"] == 3


class TestProjectDashboard(unittest.TestCase):
    """Test project dashboard generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.registry = MockRegistry()
        self.memory_service = MockMemoryService()
        self.service = DashboardService(
            registry=self.registry,
            memory_service=self.memory_service,
            conflict_resolver=None,
        )

    def test_project_dashboard_empty(self):
        """Test project dashboard with no agents."""
        dashboard = self.service.get_project_dashboard("nonexistent-project")

        assert dashboard.project == "nonexistent-project"
        assert dashboard.agent_count == 0
        # Empty hierarchy still has L1, L2, L3 keys with empty lists
        assert "L1" in dashboard.hierarchy
        assert len(dashboard.hierarchy["L1"]) == 0

    def test_project_dashboard_hierarchy(self):
        """Test project dashboard builds correct hierarchy."""
        now = time.time()

        # Create L1 agent
        l1_agent = MockAgent(
            uuid="l1-coord",
            project="test-project",
            level="L1",
            role="coordinator",
            last_heartbeat=now - 60,
            created_at=now - 3600,
        )
        self.registry.add_agent(l1_agent)

        # Create L2 agents
        for i in range(2):
            l2_agent = MockAgent(
                uuid=f"l2-worker-{i}",
                project="test-project",
                level="L2",
                role="worker",
                last_heartbeat=now - 60,
                created_at=now - 3600,
                parent_id="l1-coord",
            )
            self.registry.add_agent(l2_agent)

        dashboard = self.service.get_project_dashboard("test-project")

        assert dashboard.agent_count == 3
        assert "L1" in dashboard.hierarchy
        assert "L2" in dashboard.hierarchy
        assert len(dashboard.hierarchy["L1"]) == 1
        assert len(dashboard.hierarchy["L2"]) == 2

    def test_project_dashboard_stale_agent_marking(self):
        """Test project dashboard marks stale agents."""
        now = time.time()

        # Active agent
        active = MockAgent(
            uuid="active",
            project="test-project",
            level="L1",
            role="coordinator",
            last_heartbeat=now - 60,
            created_at=now - 3600,
        )
        self.registry.add_agent(active)

        # Stale agent
        stale = MockAgent(
            uuid="stale",
            project="test-project",
            level="L2",
            role="worker",
            last_heartbeat=now - 600,  # 10 minutes ago
            created_at=now - 3600,
        )
        self.registry.add_agent(stale)

        dashboard = self.service.get_project_dashboard("test-project")

        # Check hierarchy contains status info
        statuses = [a["status"] for agents in dashboard.hierarchy.values() for a in agents]
        assert "active" in statuses
        assert "stale" in statuses


class TestAgentDashboard(unittest.TestCase):
    """Test agent dashboard generation."""

    def setUp(self):
        """Set up test fixtures."""
        self.registry = MockRegistry()
        self.memory_service = MockMemoryService()
        self.service = DashboardService(
            registry=self.registry,
            memory_service=self.memory_service,
            conflict_resolver=None,
        )
        self.now = time.time()

    def test_agent_dashboard_not_found(self):
        """Test agent dashboard when agent doesn't exist."""
        dashboard = self.service.get_agent_dashboard("nonexistent")
        assert dashboard is None

    def test_agent_dashboard_active(self):
        """Test agent dashboard for active agent."""
        agent = MockAgent(
            uuid="active-agent",
            project="test-project",
            level="L2",
            role="researcher",
            last_heartbeat=self.now - 60,
            created_at=self.now - 3600,
        )
        self.registry.add_agent(agent)

        # Add memory for the agent
        self.memory_service.memories["test-project:active-agent:L2:researcher"] = [
            MockMemory(
                timestamp=self.now - 100,
                memory_type=MockMemoryType("execution"),
                content={"task": "completed"},
            ),
        ]

        dashboard = self.service.get_agent_dashboard("active-agent")

        assert dashboard is not None
        assert dashboard.agent_id == "active-agent"
        assert dashboard.status == "active"
        assert dashboard.level == "L2"
        assert dashboard.last_heartbeat_seconds_ago is not None
        assert dashboard.last_heartbeat_seconds_ago < 70

    def test_agent_dashboard_stale(self):
        """Test agent dashboard for stale agent."""
        agent = MockAgent(
            uuid="stale-agent",
            project="test-project",
            level="L2",
            role="researcher",
            last_heartbeat=self.now - 600,  # 10 minutes ago
            created_at=self.now - 7200,
        )
        self.registry.add_agent(agent)

        dashboard = self.service.get_agent_dashboard("stale-agent")

        assert dashboard is not None
        assert dashboard.status == "stale"
        assert dashboard.last_heartbeat_seconds_ago > 300

    def test_agent_dashboard_metrics(self):
        """Test agent dashboard includes metrics."""
        agent = MockAgent(
            uuid="metrics-agent",
            project="test-project",
            level="L1",
            role="coordinator",
            last_heartbeat=self.now - 60,
            created_at=self.now - 3600,
        )
        self.registry.add_agent(agent)

        # Mock memory service with stats
        self.memory_service.memories["test-project:metrics-agent:L1:coordinator"] = [
            MockMemory(timestamp=self.now, memory_type=MockMemoryType("execution"), content={}),
        ]

        dashboard = self.service.get_agent_dashboard("metrics-agent")

        assert dashboard is not None
        assert dashboard.metrics is not None
        assert dashboard.metrics.success_rate >= 0.0
        assert dashboard.metrics.success_rate <= 1.0

    def test_agent_dashboard_relationships(self):
        """Test agent dashboard includes relationship information."""
        # Create parent
        parent = MockAgent(
            uuid="parent",
            project="test-project",
            level="L1",
            role="coordinator",
            last_heartbeat=self.now - 60,
            created_at=self.now - 7200,
        )
        self.registry.add_agent(parent)

        # Create agent with parent and children
        agent = MockAgent(
            uuid="child-worker",
            project="test-project",
            level="L2",
            role="worker",
            last_heartbeat=self.now - 60,
            created_at=self.now - 3600,
            parent_id="parent",
            children=["executor-1", "executor-2"],
        )
        self.registry.add_agent(agent)

        # Create sibling
        sibling = MockAgent(
            uuid="child-researcher",
            project="test-project",
            level="L2",
            role="researcher",
            last_heartbeat=self.now - 60,
            created_at=self.now - 3600,
            parent_id="parent",
        )
        self.registry.add_agent(sibling)

        dashboard = self.service.get_agent_dashboard("child-worker")

        assert dashboard is not None
        assert dashboard.relationships is not None
        assert dashboard.relationships["parent"] == "parent"
        assert len(dashboard.relationships["children"]) == 2


class TestMetricsAggregation(unittest.TestCase):
    """Test metrics aggregation."""

    def setUp(self):
        """Set up test fixtures."""
        self.registry = MockRegistry()
        self.memory_service = MockMemoryService()
        self.service = DashboardService(
            registry=self.registry,
            memory_service=self.memory_service,
            conflict_resolver=None,
        )

    def test_metrics_snapshot_no_memory_service(self):
        """Test metrics with no memory service."""
        service = DashboardService(registry=self.registry, memory_service=None)
        metrics = service._get_agent_metrics("some-agent")

        assert metrics.task_count == 0
        assert metrics.error_count == 0
        assert metrics.success_rate == 0.0

    def test_metrics_snapshot_with_memory_data(self):
        """Test metrics with memory service data."""
        agent_id = "test-agent"
        self.memory_service.memories[agent_id] = [
            MockMemory(timestamp=time.time(), memory_type=MockMemoryType("execution"), content={}),
        ]

        metrics = self.service._get_agent_metrics(agent_id)

        assert metrics.task_count > 0
        assert metrics.success_rate >= 0.0
        assert metrics.success_rate <= 1.0


class TestSerialization(unittest.TestCase):
    """Test dashboard serialization to dicts."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = DashboardService()

    def test_overview_to_dict(self):
        """Test converting overview to dict."""
        overview = DashboardOverview(
            total_agents=10,
            active_count=9,
            stale_count=1,
            by_level={"L1": {"total": 3, "active": 3, "stale": 0}},
            by_project={"project-a": {"total": 10, "active": 9, "stale": 1}},
            timestamp=time.time(),
        )

        result = self.service.overview_to_dict(overview)

        assert result["total_agents"] == 10
        assert result["active_count"] == 9
        assert "timestamp" in result

    def test_project_to_dict(self):
        """Test converting project dashboard to dict."""
        project_dash = DashboardProject(
            project="test-project",
            agent_count=5,
            hierarchy={},
            recent_activity=[],
            conflicts=[],
            timestamp=time.time(),
        )

        result = self.service.project_to_dict(project_dash)

        assert result["project"] == "test-project"
        assert result["agent_count"] == 5

    def test_agent_to_dict(self):
        """Test converting agent dashboard to dict."""
        agent_dash = DashboardAgent(
            agent_id="test-agent",
            status="active",
            level="L2",
            last_heartbeat_seconds_ago=60.0,
            created_seconds_ago=3600.0,
            metrics=MetricsSnapshot(task_count=5, error_count=1, success_rate=0.8),
            memory_summary={"total_memories": 5},
            relationships={"parent": "parent-id"},
            timestamp=time.time(),
        )

        result = self.service.agent_to_dict(agent_dash)

        assert result["agent_id"] == "test-agent"
        assert result["status"] == "active"
        assert result["level"] == "L2"


class TestErrorHandling(unittest.TestCase):
    """Test error handling in dashboard service."""

    def test_dashboard_with_none_registry(self):
        """Test dashboard service handles None registry gracefully."""
        # Force None registry by passing explicit None
        service = DashboardService.__new__(DashboardService)
        service.registry = None
        service.memory_service = None
        service.conflict_resolver = None

        overview = service.get_overview_dashboard()
        assert overview.total_agents == 0

        project = service.get_project_dashboard("test")
        assert project.agent_count == 0

    def test_agent_dashboard_with_none_registry(self):
        """Test agent dashboard with None registry returns None."""
        service = DashboardService(registry=None)

        dashboard = service.get_agent_dashboard("some-agent")
        assert dashboard is None

    def test_metrics_with_invalid_agent(self):
        """Test metrics with non-existent agent."""
        service = DashboardService(
            memory_service=MockMemoryService(),
        )

        metrics = service._get_agent_metrics("invalid-agent")

        # Should return empty metrics, not crash
        assert metrics.task_count == 0


class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility with Phase 1-5B systems."""

    def test_dashboard_service_with_phase1_registry(self):
        """Test dashboard service works with Phase 1 agent registry."""
        # This ensures no breaking changes to Phase 1
        registry = MockRegistry()
        now = time.time()

        # Create a phase 1 style agent
        agent = MockAgent(
            uuid="uuid-123",
            project="project",
            level="L1",
            role="researcher",
            last_heartbeat=now - 60,
            created_at=now - 3600,
        )
        registry.add_agent(agent)

        service = DashboardService(registry=registry)
        overview = service.get_overview_dashboard()

        # Should not crash and should show agent
        assert overview.total_agents == 1
        assert overview.active_count == 1

    def test_dashboard_service_with_phase5b_memory_service(self):
        """Test dashboard service works with Phase 5B memory service."""
        # This ensures no breaking changes to Phase 5B
        memory_service = MockMemoryService()

        service = DashboardService(memory_service=memory_service)
        metrics = service._get_agent_metrics("test-agent")

        # Should not crash and return metrics
        assert metrics is not None
        assert isinstance(metrics, MetricsSnapshot)


class TestDashboardAnalyticsIntegration(unittest.TestCase):
    """Test Phase 6 analytics integration into agent dashboard."""

    def setUp(self):
        """Set up test fixtures."""
        self.registry = MockRegistry()
        self.memory_service = MockMemoryService()
        self.service = DashboardService(
            registry=self.registry,
            memory_service=self.memory_service,
            conflict_resolver=None,
        )
        self.now = time.time()

    def test_agent_dashboard_has_analytics_field(self):
        """Agent dashboard dict includes 'analytics' key."""
        agent = MockAgent(
            uuid="analytics-agent",
            project="test-project",
            level="L2",
            role="researcher",
            last_heartbeat=self.now - 60,
            created_at=self.now - 3600,
        )
        self.registry.add_agent(agent)

        # Add memories so analytics has data to work with
        agent_scoped_id = agent.project_scoped_id
        self.memory_service.memories[agent_scoped_id] = [
            MockMemory(
                timestamp=self.now - 100,
                memory_type=MockMemoryType("execution"),
                content={"task": "completed"},
            ),
        ]

        dashboard = self.service.get_agent_dashboard("analytics-agent")

        assert dashboard is not None
        assert hasattr(dashboard, "analytics")
        assert isinstance(dashboard.analytics, dict)

        # Verify it serializes correctly
        result = self.service.agent_to_dict(dashboard)
        assert "analytics" in result
        assert isinstance(result["analytics"], dict)

    def test_agent_dashboard_analytics_empty_on_no_memories(self):
        """Analytics is {} when no memories exist for the agent."""
        agent = MockAgent(
            uuid="no-mem-agent",
            project="test-project",
            level="L1",
            role="coordinator",
            last_heartbeat=self.now - 60,
            created_at=self.now - 3600,
        )
        self.registry.add_agent(agent)

        # No memories added for this agent
        dashboard = self.service.get_agent_dashboard("no-mem-agent")

        assert dashboard is not None
        assert dashboard.analytics == {}

    def test_agent_dashboard_analytics_graceful_no_import(self):
        """Analytics works even if MemoryAnalytics is not importable."""
        import civilization_dashboard_service as cds

        # Temporarily disable analytics
        original = cds._ANALYTICS_AVAILABLE
        cds._ANALYTICS_AVAILABLE = False
        try:
            agent = MockAgent(
                uuid="no-import-agent",
                project="test-project",
                level="L2",
                role="worker",
                last_heartbeat=self.now - 60,
                created_at=self.now - 3600,
            )
            self.registry.add_agent(agent)

            # Even with memories, analytics should be empty
            agent_scoped_id = agent.project_scoped_id
            self.memory_service.memories[agent_scoped_id] = [
                MockMemory(
                    timestamp=self.now - 50,
                    memory_type=MockMemoryType("learning"),
                    content={"learning": "test"},
                ),
            ]

            dashboard = self.service.get_agent_dashboard("no-import-agent")

            assert dashboard is not None
            assert dashboard.analytics == {}
        finally:
            cds._ANALYTICS_AVAILABLE = original


if __name__ == "__main__":
    unittest.main()
