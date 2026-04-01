"""Tests for governance/agent_hierarchy.py - WP-16001+ agent hierarchy management."""

import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import pytest

from thegent.governance.agent_hierarchy import (
    AgentHierarchyManager,
    AgentNode,
    AgentRelationship,
    AgentRole,
    AgentTeam,
    CoordinationMode,
    RelationshipType,
    TeamType,
)


class TestAgentRole:
    """Tests for AgentRole enum."""

    def test_all_roles_exist(self):
        assert AgentRole.EXECUTIVE.value == "executive"
        assert AgentRole.TEAM_LEAD.value == "team_lead"
        assert AgentRole.SPECIALIST.value == "specialist"

    def test_role_from_value(self):
        assert AgentRole("executive") == AgentRole.EXECUTIVE


class TestRelationshipType:
    """Tests for RelationshipType enum."""

    def test_all_types_exist(self):
        assert RelationshipType.DIRECT_PARENT_CHILD.value == "direct_parent_child"
        assert RelationshipType.TEAM_MEMBERSHIP.value == "team_membership"
        assert RelationshipType.CROSS_TEAM_COLLABORATION.value == "cross_team_collaboration"


class TestTeamType:
    """Tests for TeamType enum."""

    def test_all_types_exist(self):
        assert TeamType.FUNCTIONAL.value == "functional"
        assert TeamType.PROJECT.value == "project"
        assert TeamType.AD_HOC.value == "ad_hoc"


class TestCoordinationMode:
    """Tests for CoordinationMode enum."""

    def test_all_modes_exist(self):
        assert CoordinationMode.HIERARCHICAL.value == "hierarchical"
        assert CoordinationMode.COLLABORATIVE.value == "collaborative"
        assert CoordinationMode.SWARM.value == "swarm"
        assert CoordinationMode.ADAPTIVE.value == "adaptive"


class TestAgentNode:
    """Tests for AgentNode dataclass."""

    def test_create_node(self):
        node = AgentNode(
            agent_id="coder",
            run_id="run-123",
            role=AgentRole.SPECIALIST,
        )
        assert node.agent_id == "coder"
        assert node.run_id == "run-123"
        assert node.role == AgentRole.SPECIALIST
        assert node.team_id is None
        assert node.parent_id is None
        assert node.children_ids == []
        assert node.status == "active"

    def test_create_node_with_team(self):
        node = AgentNode(
            agent_id="coder",
            run_id="run-123",
            role=AgentRole.TEAM_LEAD,
            team_id="team-1",
            parent_id="parent-1",
        )
        assert node.team_id == "team-1"
        assert node.parent_id == "parent-1"

    def test_from_dict(self):
        data = {
            "agent_id": "test-agent",
            "run_id": "run-456",
            "role": "team_lead",
            "created_at": "2024-01-01T00:00:00+00:00",
        }
        node = AgentNode.from_dict(data)
        assert node.agent_id == "test-agent"
        assert node.role == AgentRole.TEAM_LEAD

    def test_to_dict(self):
        node = AgentNode(
            agent_id="test",
            run_id="run-1",
            role=AgentRole.EXECUTIVE,
        )
        d = node.to_dict()
        assert d["agent_id"] == "test"
        assert d["role"] == "executive"


class TestAgentRelationship:
    """Tests for AgentRelationship dataclass."""

    def test_create_relationship(self):
        rel = AgentRelationship(
            relationship_id="rel-1",
            parent_id="parent-1",
            child_id="child-1",
            relationship_type=RelationshipType.DIRECT_PARENT_CHILD,
        )
        assert rel.relationship_id == "rel-1"
        assert rel.parent_id == "parent-1"
        assert rel.child_id == "child-1"
        assert rel.status == "active"

    def test_to_dict(self):
        rel = AgentRelationship(
            relationship_id="rel-1",
            parent_id="parent-1",
            child_id="child-1",
            relationship_type=RelationshipType.DIRECT_PARENT_CHILD,
            task_id="task-1",
        )
        d = rel.to_dict()
        assert d["relationship_id"] == "rel-1"
        assert d["task_id"] == "task-1"

    def test_from_dict(self):
        data = {
            "relationship_id": "rel-2",
            "parent_id": "p-1",
            "child_id": "c-1",
            "relationship_type": "team_membership",
            "created_at": "2024-01-01T00:00:00+00:00",
        }
        rel = AgentRelationship.from_dict(data)
        assert rel.relationship_type == RelationshipType.TEAM_MEMBERSHIP


class TestAgentTeam:
    """Tests for AgentTeam dataclass."""

    def test_create_team(self):
        team = AgentTeam(
            team_id="team-1",
            name="Alpha Team",
            description="Primary development team",
            team_type=TeamType.PROJECT,
            coordination_mode=CoordinationMode.HIERARCHICAL,
            lead_id="lead-1",
        )
        assert team.team_id == "team-1"
        assert team.name == "Alpha Team"
        assert team.team_type == TeamType.PROJECT
        assert team.coordination_mode == CoordinationMode.HIERARCHICAL
        assert team.members == []
        assert team.status == "active"

    def test_create_team_with_members(self):
        team = AgentTeam(
            team_id="team-1",
            name="Alpha Team",
            description="Primary development team",
            team_type=TeamType.PROJECT,
            coordination_mode=CoordinationMode.COLLABORATIVE,
            lead_id="lead-1",
            members=["member-1", "member-2"],
            boundaries={"max_cost": 1000},
        )
        assert len(team.members) == 2
        assert team.boundaries == {"max_cost": 1000}

    def test_to_dict(self):
        team = AgentTeam(
            team_id="team-1",
            name="Test Team",
            description="D",
            team_type=TeamType.FUNCTIONAL,
            coordination_mode=CoordinationMode.ADAPTIVE,
            lead_id="lead-1",
        )
        d = team.to_dict()
        assert d["team_id"] == "team-1"
        assert d["team_type"] == "functional"

    def test_from_dict(self):
        data = {
            "team_id": "t-1",
            "name": "Test",
            "description": "D",
            "lead_id": "l-1",
            "team_type": "project",
            "coordination_mode": "swarm",
            "created_at": "2024-01-01T00:00:00+00:00",
        }
        team = AgentTeam.from_dict(data)
        assert team.team_type == TeamType.PROJECT
        assert team.coordination_mode == CoordinationMode.SWARM


class TestAgentHierarchyManager:
    """Tests for AgentHierarchyManager class."""

    @pytest.fixture
    def manager(self, tmp_path):
        return AgentHierarchyManager(tmp_path)

    @pytest.fixture
    def manager_with_team(self, tmp_path):
        mgr = AgentHierarchyManager(tmp_path)
        mgr.create_team(
            team_id="team-1",
            name="Alpha",
            description="Alpha team",
            team_type=TeamType.PROJECT,
            coordination_mode=CoordinationMode.HIERARCHICAL,
            lead_id="lead-1",
        )
        return mgr

    def test_init_creates_storage_dir(self, tmp_path):
        storage = tmp_path / "hierarchy"
        mgr = AgentHierarchyManager(storage)
        assert storage.exists()

    def test_init_loads_existing_data(self, tmp_path):
        storage = tmp_path / "hierarchy"
        # Create first manager and add agent
        mgr1 = AgentHierarchyManager(storage)
        mgr1.register_agent("agent-1", "run-1", AgentRole.EXECUTIVE, validate=False)

        # Create new manager pointing to same storage
        mgr2 = AgentHierarchyManager(storage)
        agent = mgr2.get_agent("run-1")
        assert agent is not None
        assert agent.agent_id == "agent-1"

    def test_register_agent_executive(self, manager):
        node = manager.register_agent(
            agent_id="exec-1",
            run_id="run-exec",
            role=AgentRole.EXECUTIVE,
            validate=False,
        )
        assert node.agent_id == "exec-1"
        assert node.role == AgentRole.EXECUTIVE

    def test_register_agent_with_parent(self, manager):
        parent = manager.register_agent("parent", "run-parent", AgentRole.EXECUTIVE, validate=False)
        child = manager.register_agent(
            "child",
            "run-child",
            AgentRole.SPECIALIST,
            parent_id="run-parent",
            validate=False,
        )
        assert child.parent_id == "run-parent"
        assert "run-child" in parent.children_ids

    def test_register_agent_with_team(self, manager_with_team):
        node = manager_with_team.register_agent(
            "member",
            "run-member",
            AgentRole.SPECIALIST,
            team_id="team-1",
            validate=False,
        )
        assert node.team_id == "team-1"

    def test_register_agent_validation_failure(self, manager):
        manager.register_agent("parent", "run-parent", AgentRole.EXECUTIVE, validate=False)
        with pytest.raises(ValueError, match="already exists"):
            manager.register_agent("different", "run-parent", AgentRole.SPECIALIST)

    def test_register_agent_with_invalid_parent(self, manager):
        with pytest.raises(ValueError, match="Invalid parent"):
            manager.register_agent("child", "run-child", AgentRole.SPECIALIST, parent_id="nonexistent")

    def test_create_relationship(self, manager):
        manager.register_agent("parent", "run-p", AgentRole.EXECUTIVE, validate=False)
        manager.register_agent("child", "run-c", AgentRole.SPECIALIST, validate=False)
        rel = manager.create_relationship(
            parent_id="run-p",
            child_id="run-c",
            relationship_type=RelationshipType.DIRECT_PARENT_CHILD,
        )
        assert rel.parent_id == "run-p"
        assert rel.child_id == "run-c"

    def test_create_relationship_with_delegation_context(self, manager):
        manager.register_agent("parent", "run-p", AgentRole.EXECUTIVE, validate=False)
        manager.register_agent("child", "run-c", AgentRole.SPECIALIST, validate=False)
        rel = manager.create_relationship(
            parent_id="run-p",
            child_id="run-c",
            relationship_type=RelationshipType.DIRECT_PARENT_CHILD,
            task_id="task-1",
            delegation_prompt="Do this task",
        )
        assert rel.task_id == "task-1"
        assert rel.delegation_prompt == "Do this task"

    def test_create_team(self, manager):
        team = manager.create_team(
            team_id="team-new",
            name="New Team",
            description="A new team",
            team_type=TeamType.PROJECT,
            coordination_mode=CoordinationMode.COLLABORATIVE,
            lead_id="lead-1",
        )
        assert team.team_id == "team-new"
        assert team.name == "New Team"

    def test_get_agent(self, manager):
        manager.register_agent("test", "run-test", AgentRole.EXECUTIVE, validate=False)
        node = manager.get_agent("run-test")
        assert node is not None
        assert node.agent_id == "test"

    def test_get_agent_not_found(self, manager):
        node = manager.get_agent("nonexistent")
        assert node is None

    def test_get_team(self, manager_with_team):
        team = manager_with_team.get_team("team-1")
        assert team is not None
        assert team.name == "Alpha"

    def test_get_team_members(self, manager_with_team):
        manager_with_team.register_agent("lead", "lead-1", AgentRole.TEAM_LEAD, validate=False)
        manager_with_team.register_agent("member", "member-1", AgentRole.SPECIALIST, team_id="team-1", validate=False)
        members = manager_with_team.get_team_members("team-1")
        assert len(members) == 2

    def test_get_children(self, manager):
        parent = manager.register_agent("parent", "run-p", AgentRole.EXECUTIVE, validate=False)
        manager.register_agent("child1", "run-c1", AgentRole.SPECIALIST, parent_id="run-p", validate=False)
        manager.register_agent("child2", "run-c2", AgentRole.SPECIALIST, parent_id="run-p", validate=False)
        children = manager.get_children("run-p")
        assert len(children) == 2

    def test_get_ancestors(self, manager):
        exec = manager.register_agent("exec", "run-exec", AgentRole.EXECUTIVE, validate=False)
        lead = manager.register_agent("lead", "run-lead", AgentRole.TEAM_LEAD, parent_id="run-exec", validate=False)
        specialist = manager.register_agent("spec", "run-spec", AgentRole.SPECIALIST, parent_id="run-lead", validate=False)
        ancestors = manager.get_ancestors("run-spec")
        assert len(ancestors) == 2

    def test_get_descendants(self, manager):
        exec = manager.register_agent("exec", "run-exec", AgentRole.EXECUTIVE, validate=False)
        manager.register_agent("child", "run-child", AgentRole.TEAM_LEAD, parent_id="run-exec", validate=False)
        manager.register_agent("grandchild", "run-gc", AgentRole.SPECIALIST, parent_id="run-child", validate=False)
        descendants = manager.get_descendants("run-exec")
        assert len(descendants) == 2

    def test_can_delegate_executive_to_anyone(self, manager):
        manager.register_agent("exec", "run-exec", AgentRole.EXECUTIVE, validate=False)
        manager.register_agent("any", "run-any", AgentRole.SPECIALIST, validate=False)
        assert manager.can_delegate("run-exec", "run-any") is True

    def test_can_delegate_team_lead_to_member(self, manager):
        manager.register_agent("lead", "run-lead", AgentRole.TEAM_LEAD, team_id="team-1", validate=False)
        manager.register_agent("member", "run-member", AgentRole.SPECIALIST, team_id="team-1", validate=False)
        assert manager.can_delegate("run-lead", "run-member") is True

    def test_can_delegate_team_lead_to_non_member(self, manager):
        manager.register_agent("lead", "run-lead", AgentRole.TEAM_LEAD, team_id="team-1", validate=False)
        manager.register_agent("other", "run-other", AgentRole.SPECIALIST, team_id="team-2", validate=False)
        assert manager.can_delegate("run-lead", "run-other") is False

    def test_can_delegate_cross_team_with_context(self, manager):
        manager.register_agent("lead", "run-lead", AgentRole.TEAM_LEAD, team_id="team-1", validate=False)
        manager.register_agent("other", "run-other", AgentRole.SPECIALIST, team_id="team-2", validate=False)
        assert manager.can_delegate("run-lead", "run-other", {"allow_cross_team": True}) is True

    def test_can_delegate_specialist_to_specialist(self, manager):
        manager.register_agent("spec1", "run-s1", AgentRole.SPECIALIST, team_id="team-1", validate=False)
        manager.register_agent("spec2", "run-s2", AgentRole.SPECIALIST, team_id="team-1", validate=False)
        assert manager.can_delegate("run-s1", "run-s2") is True

    def test_can_delegate_not_allowed(self, manager):
        manager.register_agent("exec", "run-exec", AgentRole.EXECUTIVE, validate=False)
        manager.register_agent("spec", "run-spec", AgentRole.SPECIALIST, validate=False)
        # Specialist cannot delegate to executive (no hierarchical relationship)
        assert manager.can_delegate("run-spec", "run-exec") is False

    def test_get_hierarchy_tree(self, manager):
        manager.register_agent("root", "run-root", AgentRole.EXECUTIVE, validate=False)
        manager.register_agent("child", "run-child", AgentRole.TEAM_LEAD, parent_id="run-root", validate=False)
        tree = manager.get_hierarchy_tree("run-root")
        assert tree["agent_id"] == "root"
        assert len(tree["children"]) == 1

    def test_get_hierarchy_tree_find_root(self, manager):
        manager.register_agent("root", "run-root", AgentRole.EXECUTIVE, validate=False)
        manager.register_agent("child", "run-child", AgentRole.TEAM_LEAD, parent_id="run-root", validate=False)
        tree = manager.get_hierarchy_tree()
        assert tree["agent_id"] == "root"

    def test_get_hierarchy_tree_nonexistent(self, manager):
        tree = manager.get_hierarchy_tree("nonexistent")
        assert tree == {}

    def test_list_all_agents(self, manager):
        manager.register_agent("a1", "run-1", AgentRole.EXECUTIVE, validate=False)
        manager.register_agent("a2", "run-2", AgentRole.SPECIALIST, validate=False)
        agents = manager.list_all_agents()
        assert len(agents) == 2

    def test_list_all_teams(self, manager_with_team):
        teams = manager_with_team.list_all_teams()
        assert len(teams) == 1

    def test_list_all_relationships(self, manager):
        manager.register_agent("p", "run-p", AgentRole.EXECUTIVE, validate=False)
        manager.register_agent("c", "run-c", AgentRole.SPECIALIST, validate=False)
        manager.create_relationship("run-p", "run-c", RelationshipType.DIRECT_PARENT_CHILD)
        rels = manager.list_all_relationships()
        assert len(rels) == 1

    def test_update_agent_status(self, manager):
        manager.register_agent("test", "run-test", AgentRole.EXECUTIVE, validate=False)
        result = manager.update_agent_status("run-test", "inactive")
        assert result is True
        assert manager.get_agent("run-test").status == "inactive"

    def test_update_agent_status_not_found(self, manager):
        result = manager.update_agent_status("nonexistent", "inactive")
        assert result is False

    def test_update_team_status(self, manager_with_team):
        result = manager_with_team.update_team_status("team-1", "inactive")
        assert result is True
        assert manager_with_team.get_team("team-1").status == "inactive"

    def test_add_team_member(self, manager_with_team):
        manager_with_team.register_agent("member", "run-member", AgentRole.SPECIALIST, validate=False)
        result = manager_with_team.add_team_member("team-1", "run-member")
        assert result is True

    def test_add_team_member_already_member(self, manager_with_team):
        manager_with_team.register_agent("member", "run-member", AgentRole.SPECIALIST, validate=False)
        manager_with_team.add_team_member("team-1", "run-member")
        result = manager_with_team.add_team_member("team-1", "run-member")
        assert result is False

    def test_remove_team_member(self, manager_with_team):
        manager_with_team.register_agent("member", "run-member", AgentRole.SPECIALIST, validate=False)
        manager_with_team.add_team_member("team-1", "run-member")
        result = manager_with_team.remove_team_member("team-1", "run-member")
        assert result is True

    def test_validate_agent_id_valid(self, manager):
        manager.register_agent("test", "run-test", AgentRole.EXECUTIVE, validate=False)
        is_valid, error = manager.validate_agent_id("run-test")
        assert is_valid is True
        assert error is None

    def test_validate_agent_id_empty(self, manager):
        is_valid, error = manager.validate_agent_id("")
        assert is_valid is False
        assert "non-empty string" in error

    def test_validate_agent_id_not_found(self, manager):
        is_valid, error = manager.validate_agent_id("nonexistent")
        assert is_valid is False
        assert "not found" in error

    def test_validate_agent_id_inactive(self, manager):
        manager.register_agent("test", "run-test", AgentRole.EXECUTIVE, validate=False)
        manager.update_agent_status("run-test", "inactive")
        is_valid, error = manager.validate_agent_id("run-test")
        assert is_valid is False
        assert "not active" in error

    def test_detect_circular_relationships_no_cycle(self, manager):
        manager.register_agent("exec", "run-exec", AgentRole.EXECUTIVE, validate=False)
        manager.register_agent("child", "run-child", AgentRole.SPECIALIST, parent_id="run-exec", validate=False)
        cycle = manager.detect_circular_relationships("run-exec")
        assert cycle == []

    def test_detect_circular_relationships_nonexistent_start(self, manager):
        cycle = manager.detect_circular_relationships("nonexistent")
        assert cycle == []

    def test_detect_orphaned_agents(self, manager):
        manager.register_agent("parent", "run-parent", AgentRole.EXECUTIVE, validate=False)
        manager.register_agent("child", "run-child", AgentRole.SPECIALIST, parent_id="run-parent", validate=False)
        orphaned = manager.detect_orphaned_agents()
        assert orphaned == []

    def test_detect_orphaned_agents_invalid_parent(self, manager):
        manager.register_agent("orphan", "run-orphan", AgentRole.SPECIALIST, parent_id="nonexistent", validate=False)
        orphaned = manager.detect_orphaned_agents()
        assert len(orphaned) == 1
        assert "nonexistent" in orphaned[0][1]

    def test_detect_orphaned_agents_invalid_team(self, manager):
        manager.register_agent("orphan", "run-orphan", AgentRole.SPECIALIST, team_id="nonexistent", validate=False)
        orphaned = manager.detect_orphaned_agents()
        assert len(orphaned) == 1

    def test_check_team_consistency_valid(self, manager_with_team):
        manager_with_team.register_agent("lead", "lead-1", AgentRole.TEAM_LEAD, team_id="team-1", validate=False)
        inconsistencies = manager_with_team.check_team_consistency()
        assert inconsistencies == []

    def test_check_team_consistency_lead_not_in_team(self, manager):
        manager.create_team(
            team_id="team-1",
            name="Test",
            description="T",
            team_type=TeamType.PROJECT,
            coordination_mode=CoordinationMode.HIERARCHICAL,
            lead_id="nonexistent",
        )
        manager.register_agent("member", "run-member", AgentRole.SPECIALIST, team_id="team-1", validate=False)
        inconsistencies = manager.check_team_consistency()
        assert len(inconsistencies) >= 1

    def test_validate_before_register_run_id_exists(self, manager):
        manager.register_agent("test", "run-test", AgentRole.EXECUTIVE, validate=False)
        is_valid, error = manager.validate_before_register("different", "run-test")
        assert is_valid is False
        assert "already exists" in error

    def test_validate_before_register_invalid_parent(self, manager):
        is_valid, error = manager.validate_before_register("test", "run-test", parent_id="nonexistent")
        assert is_valid is False
        assert "Invalid parent" in error

    def test_validate_before_register_circular(self, manager):
        manager.register_agent("parent", "run-parent", AgentRole.EXECUTIVE, validate=False)
        manager.register_agent("child", "run-child", AgentRole.SPECIALIST, parent_id="run-parent", validate=False)
        is_valid, error = manager.validate_before_register(
            "grandchild", "run-gc", parent_id="run-child"
        )
        # Making child the parent of grandchild is fine
        assert is_valid is True

    def test_validate_before_register_nonexistent_team(self, manager):
        is_valid, error = manager.validate_before_register("test", "run-test", team_id="nonexistent")
        assert is_valid is False
        assert "does not exist" in error


class TestAgentHierarchyEdgeCases:
    """Edge case tests for AgentHierarchyManager."""

    def test_register_with_circular_parent_reference_prevented(self, tmp_path):
        manager = AgentHierarchyManager(tmp_path)
        manager.register_agent("exec", "run-exec", AgentRole.EXECUTIVE, validate=False)
        manager.register_agent("child", "run-child", AgentRole.SPECIALIST, parent_id="run-exec", validate=False)
        is_valid, error = manager.validate_before_register(
            "exec2", "run-exec2", parent_id="run-child"
        )
        assert is_valid is True  # No cycle would be created

    def test_multiple_teams_with_members(self, tmp_path):
        manager = AgentHierarchyManager(tmp_path)
        manager.create_team(
            team_id="team-1", name="T1", description="D",
            team_type=TeamType.PROJECT, coordination_mode=CoordinationMode.HIERARCHICAL, lead_id="lead-1",
        )
        manager.create_team(
            team_id="team-2", name="T2", description="D",
            team_type=TeamType.FUNCTIONAL, coordination_mode=CoordinationMode.COLLABORATIVE, lead_id="lead-2",
        )
        manager.register_agent("lead1", "lead-1", AgentRole.TEAM_LEAD, team_id="team-1", validate=False)
        manager.register_agent("lead2", "lead-2", AgentRole.TEAM_LEAD, team_id="team-2", validate=False)
        manager.register_agent("member1", "m-1", AgentRole.SPECIALIST, team_id="team-1", validate=False)
        manager.register_agent("member2", "m-2", AgentRole.SPECIALIST, team_id="team-2", validate=False)
        teams = manager.list_all_teams()
        assert len(teams) == 2

    def test_hierarchy_with_multiple_levels(self, tmp_path):
        manager = AgentHierarchyManager(tmp_path)
        manager.register_agent("ceo", "run-ceo", AgentRole.EXECUTIVE, validate=False)
        manager.register_agent("vp1", "run-vp1", AgentRole.TEAM_LEAD, parent_id="run-ceo", validate=False)
        manager.register_agent("vp2", "run-vp2", AgentRole.TEAM_LEAD, parent_id="run-ceo", validate=False)
        manager.register_agent("mgr1", "run-mgr1", AgentRole.SPECIALIST, parent_id="run-vp1", validate=False)
        manager.register_agent("mgr2", "run-mgr2", AgentRole.SPECIALIST, parent_id="run-vp1", validate=False)
        manager.register_agent("dev1", "run-dev1", AgentRole.SPECIALIST, parent_id="run-mgr1", validate=False)

        descendants = manager.get_descendants("run-ceo")
        assert len(descendants) == 6

        ancestors = manager.get_ancestors("run-dev1")
        assert len(ancestors) == 3
        assert ancestors[0].agent_id == "vp1"
        assert ancestors[1].agent_id == "ceo"
