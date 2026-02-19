"""Unit tests for agent hierarchy system."""

import tempfile
from pathlib import Path

import pytest

from thegent.governance.agent_hierarchy import (
    AgentHierarchyManager,
    AgentRole,
    CoordinationMode,
    RelationshipType,
    TeamType,
)


@pytest.fixture
def temp_storage():
    """Create temporary storage directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def hierarchy_manager(temp_storage):
    """Create hierarchy manager instance."""
    return AgentHierarchyManager(temp_storage)


class TestAgentHierarchyManager:
    """Test AgentHierarchyManager."""

    def test_register_agent(self, hierarchy_manager):
        """Test agent registration."""
        node = hierarchy_manager.register_agent(
            agent_id="test-agent",
            run_id="run-001",
            role=AgentRole.SPECIALIST,
        )

        assert node.agent_id == "test-agent"
        assert node.run_id == "run-001"
        assert node.role == AgentRole.SPECIALIST
        assert node.status == "active"

        # Verify persistence
        retrieved = hierarchy_manager.get_agent("run-001")
        assert retrieved is not None
        assert retrieved.agent_id == "test-agent"

    def test_parent_child_relationship(self, hierarchy_manager):
        """Test parent-child relationship."""
        parent = hierarchy_manager.register_agent(
            agent_id="parent",
            run_id="parent-001",
            role=AgentRole.TEAM_LEAD,
        )

        child = hierarchy_manager.register_agent(
            agent_id="child",
            run_id="child-001",
            role=AgentRole.SPECIALIST,
            parent_id="parent-001",
        )

        assert child.parent_id == "parent-001"
        assert "child-001" in parent.children_ids

        children = hierarchy_manager.get_children("parent-001")
        assert len(children) == 1
        assert children[0].agent_id == "child"

    def test_create_team(self, hierarchy_manager):
        """Test team creation."""
        lead = hierarchy_manager.register_agent(
            agent_id="lead",
            run_id="lead-001",
            role=AgentRole.TEAM_LEAD,
        )

        team = hierarchy_manager.create_team(
            team_id="team-001",
            name="Test Team",
            description="Test team description",
            team_type=TeamType.FUNCTIONAL,
            coordination_mode=CoordinationMode.HIERARCHICAL,
            lead_id="lead-001",
        )

        assert team.team_id == "team-001"
        assert team.name == "Test Team"
        assert team.lead_id == "lead-001"

        retrieved = hierarchy_manager.get_team("team-001")
        assert retrieved is not None
        assert retrieved.name == "Test Team"

    def test_create_relationship(self, hierarchy_manager):
        """Test relationship creation."""
        parent = hierarchy_manager.register_agent(
            agent_id="parent",
            run_id="parent-001",
            role=AgentRole.TEAM_LEAD,
        )

        child = hierarchy_manager.register_agent(
            agent_id="child",
            run_id="child-001",
            role=AgentRole.SPECIALIST,
        )

        relationship = hierarchy_manager.create_relationship(
            parent_id="parent-001",
            child_id="child-001",
            relationship_type=RelationshipType.DIRECT_PARENT_CHILD,
            delegation_prompt="Test task",
        )

        assert relationship.parent_id == "parent-001"
        assert relationship.child_id == "child-001"
        assert relationship.relationship_type == RelationshipType.DIRECT_PARENT_CHILD
        assert relationship.delegation_prompt == "Test task"

    def test_get_ancestors(self, hierarchy_manager):
        """Test ancestor retrieval."""
        # Create hierarchy: executive -> lead -> specialist
        executive = hierarchy_manager.register_agent(
            agent_id="executive",
            run_id="exec-001",
            role=AgentRole.EXECUTIVE,
        )

        lead = hierarchy_manager.register_agent(
            agent_id="lead",
            run_id="lead-001",
            role=AgentRole.TEAM_LEAD,
            parent_id="exec-001",
        )

        specialist = hierarchy_manager.register_agent(
            agent_id="specialist",
            run_id="spec-001",
            role=AgentRole.SPECIALIST,
            parent_id="lead-001",
        )

        ancestors = hierarchy_manager.get_ancestors("spec-001")
        assert len(ancestors) == 2
        assert ancestors[0].agent_id == "lead"
        assert ancestors[1].agent_id == "executive"

    def test_get_descendants(self, hierarchy_manager):
        """Test descendant retrieval."""
        parent = hierarchy_manager.register_agent(
            agent_id="parent",
            run_id="parent-001",
            role=AgentRole.TEAM_LEAD,
        )

        child1 = hierarchy_manager.register_agent(
            agent_id="child1",
            run_id="child-001",
            role=AgentRole.SPECIALIST,
            parent_id="parent-001",
        )

        child2 = hierarchy_manager.register_agent(
            agent_id="child2",
            run_id="child-002",
            role=AgentRole.SPECIALIST,
            parent_id="parent-001",
        )

        descendants = hierarchy_manager.get_descendants("parent-001")
        assert len(descendants) == 2
        assert {d.agent_id for d in descendants} == {"child1", "child2"}

    def test_can_delegate_executive(self, hierarchy_manager):
        """Test delegation permission for executive."""
        executive = hierarchy_manager.register_agent(
            agent_id="executive",
            run_id="exec-001",
            role=AgentRole.EXECUTIVE,
        )

        target = hierarchy_manager.register_agent(
            agent_id="target",
            run_id="target-001",
            role=AgentRole.SPECIALIST,
        )

        assert hierarchy_manager.can_delegate("exec-001", "target-001") is True

    def test_can_delegate_team_lead(self, hierarchy_manager):
        """Test delegation permission for team lead."""
        lead = hierarchy_manager.register_agent(
            agent_id="lead",
            run_id="lead-001",
            role=AgentRole.TEAM_LEAD,
        )

        team_member = hierarchy_manager.register_agent(
            agent_id="member",
            run_id="member-001",
            role=AgentRole.SPECIALIST,
        )

        # Create team
        team = hierarchy_manager.create_team(
            team_id="team-001",
            name="Test Team",
            description="Test",
            team_type=TeamType.FUNCTIONAL,
            coordination_mode=CoordinationMode.HIERARCHICAL,
            lead_id="lead-001",
        )

        # Add member to team
        hierarchy_manager.add_team_member("team-001", "member-001")

        assert hierarchy_manager.can_delegate("lead-001", "member-001") is True

    def test_get_hierarchy_tree(self, hierarchy_manager):
        """Test hierarchy tree generation."""
        root = hierarchy_manager.register_agent(
            agent_id="root",
            run_id="root-001",
            role=AgentRole.EXECUTIVE,
        )

        child1 = hierarchy_manager.register_agent(
            agent_id="child1",
            run_id="child-001",
            role=AgentRole.TEAM_LEAD,
            parent_id="root-001",
        )

        child2 = hierarchy_manager.register_agent(
            agent_id="child2",
            run_id="child-002",
            role=AgentRole.SPECIALIST,
            parent_id="child-001",
        )

        tree = hierarchy_manager.get_hierarchy_tree(root_id="root-001")
        assert tree is not None
        assert tree["agent_id"] == "root"
        assert len(tree["children"]) == 1
        assert tree["children"][0]["agent_id"] == "child1"
        assert len(tree["children"][0]["children"]) == 1

    def test_team_members(self, hierarchy_manager):
        """Test team member management."""
        lead = hierarchy_manager.register_agent(
            agent_id="lead",
            run_id="lead-001",
            role=AgentRole.TEAM_LEAD,
        )

        member1 = hierarchy_manager.register_agent(
            agent_id="member1",
            run_id="member-001",
            role=AgentRole.SPECIALIST,
        )

        member2 = hierarchy_manager.register_agent(
            agent_id="member2",
            run_id="member-002",
            role=AgentRole.SPECIALIST,
        )

        team = hierarchy_manager.create_team(
            team_id="team-001",
            name="Test Team",
            description="Test",
            team_type=TeamType.FUNCTIONAL,
            coordination_mode=CoordinationMode.HIERARCHICAL,
            lead_id="lead-001",
        )

        hierarchy_manager.add_team_member("team-001", "member-001")
        hierarchy_manager.add_team_member("team-001", "member-002")

        members = hierarchy_manager.get_team_members("team-001")
        assert len(members) == 3  # Lead + 2 members

        hierarchy_manager.remove_team_member("team-001", "member-001")
        members = hierarchy_manager.get_team_members("team-001")
        assert len(members) == 2  # Lead + 1 member


class TestTeamCoordinator:
    """Test TeamCoordinator."""

    def test_delegate_within_team(self, hierarchy_manager):
        """Test within-team delegation."""
        from thegent.governance.team_coordinator import TeamCoordinator

        coordinator = TeamCoordinator(hierarchy_manager)

        # Create team
        lead = hierarchy_manager.register_agent(
            agent_id="lead",
            run_id="lead-001",
            role=AgentRole.TEAM_LEAD,
        )

        member = hierarchy_manager.register_agent(
            agent_id="member",
            run_id="member-001",
            role=AgentRole.SPECIALIST,
        )

        team = hierarchy_manager.create_team(
            team_id="team-001",
            name="Test Team",
            description="Test",
            team_type=TeamType.FUNCTIONAL,
            coordination_mode=CoordinationMode.HIERARCHICAL,
            lead_id="lead-001",
        )

        hierarchy_manager.add_team_member("team-001", "member-001")

        relationship = coordinator.delegate_within_team(
            from_agent_id="lead-001",
            to_agent_id="member-001",
            task="Test task",
        )

        assert relationship.relationship_type == RelationshipType.TEAM_MEMBERSHIP
        assert relationship.delegation_prompt == "Test task"

    def test_delegate_cross_team(self, hierarchy_manager):
        """Test cross-team delegation."""
        from thegent.governance.team_coordinator import TeamCoordinator

        coordinator = TeamCoordinator(hierarchy_manager)

        # Create orchestrator
        orchestrator = hierarchy_manager.register_agent(
            agent_id="orchestrator",
            run_id="orch-001",
            role=AgentRole.EXECUTIVE,
        )

        # Create two teams
        lead1 = hierarchy_manager.register_agent(
            agent_id="lead1",
            run_id="lead-001",
            role=AgentRole.TEAM_LEAD,
        )

        lead2 = hierarchy_manager.register_agent(
            agent_id="lead2",
            run_id="lead-002",
            role=AgentRole.TEAM_LEAD,
        )

        team1 = hierarchy_manager.create_team(
            team_id="team-001",
            name="Team 1",
            description="Test",
            team_type=TeamType.FUNCTIONAL,
            coordination_mode=CoordinationMode.HIERARCHICAL,
            lead_id="lead-001",
        )

        team2 = hierarchy_manager.create_team(
            team_id="team-002",
            name="Team 2",
            description="Test",
            team_type=TeamType.FUNCTIONAL,
            coordination_mode=CoordinationMode.HIERARCHICAL,
            lead_id="lead-002",
        )

        relationship = coordinator.delegate_cross_team(
            from_agent_id="lead-001",
            to_agent_id="lead-002",
            task="Cross-team task",
        )

        assert relationship.relationship_type == RelationshipType.CROSS_TEAM_COLLABORATION
        assert relationship.handoff_context is not None
        assert relationship.handoff_context["cross_team"] is True

    def test_coordinate_team_task_hierarchical(self, hierarchy_manager):
        """Test team task coordination in hierarchical mode."""
        from thegent.governance.team_coordinator import TeamCoordinator

        coordinator = TeamCoordinator(hierarchy_manager)

        lead = hierarchy_manager.register_agent(
            agent_id="lead",
            run_id="lead-001",
            role=AgentRole.TEAM_LEAD,
        )

        member1 = hierarchy_manager.register_agent(
            agent_id="member1",
            run_id="member-001",
            role=AgentRole.SPECIALIST,
        )

        member2 = hierarchy_manager.register_agent(
            agent_id="member2",
            run_id="member-002",
            role=AgentRole.SPECIALIST,
        )

        team = hierarchy_manager.create_team(
            team_id="team-001",
            name="Test Team",
            description="Test",
            team_type=TeamType.FUNCTIONAL,
            coordination_mode=CoordinationMode.HIERARCHICAL,
            lead_id="lead-001",
        )

        hierarchy_manager.add_team_member("team-001", "member-001")
        hierarchy_manager.add_team_member("team-001", "member-002")

        result = coordinator.coordinate_team_task(
            team_id="team-001",
            task="Test task",
        )

        assert result["status"] == "success"
        assert result["coordination_mode"] == "hierarchical"
        assert "assignments" in result
        assert result["assigned_by"] == "lead-001"
