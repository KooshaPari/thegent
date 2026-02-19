"""Unit tests for Agent Hierarchy validation and error handling.

Tests for:
- Invalid agent ID validation
- Circular relationship detection
- Orphaned agent detection
- Team consistency checks
- Handoff integrity validation (WP-16005)
"""

from pathlib import Path

import pytest

from thegent.governance.agent_hierarchy import (
    AgentHierarchyManager,
    AgentRole,
    CoordinationMode,
    RelationshipType,
    TeamType,
)
from thegent.governance.handoff import HandoffIntegrity


class TestInvalidAgentIDValidation:
    """Test validation for invalid agent IDs."""

    @pytest.fixture
    def hierarchy(self, tmp_path):
        """Create a hierarchy manager."""
        return AgentHierarchyManager(tmp_path / "hierarchy")

    def test_validate_nonexistent_agent_id(self, hierarchy):
        """Test validation fails for nonexistent agent ID."""
        is_valid, error = hierarchy.validate_agent_id("NONEXISTENT")
        assert is_valid is False
        assert "not found" in error.lower()

    def test_validate_empty_agent_id(self, hierarchy):
        """Test validation fails for empty agent ID."""
        is_valid, error = hierarchy.validate_agent_id("")
        assert is_valid is False
        assert "non-empty string" in error.lower()

    def test_validate_inactive_agent_id(self, hierarchy):
        """Test validation fails for inactive agent."""
        hierarchy.register_agent("coder", "RUN-1", AgentRole.SPECIALIST, validate=False)
        hierarchy.update_agent_status("RUN-1", "inactive")

        is_valid, error = hierarchy.validate_agent_id("RUN-1")
        assert is_valid is False
        assert "not active" in error.lower()

    def test_validate_valid_agent_id(self, hierarchy):
        """Test validation succeeds for valid agent ID."""
        hierarchy.register_agent("coder", "RUN-1", AgentRole.SPECIALIST, validate=False)

        is_valid, error = hierarchy.validate_agent_id("RUN-1")
        assert is_valid is True
        assert error is None

    def test_register_agent_validates_by_default(self, hierarchy):
        """Test that register_agent validates by default."""
        hierarchy.register_agent("coder", "RUN-1", AgentRole.SPECIALIST, validate=False)

        # Should fail because parent doesn't exist
        with pytest.raises(ValueError, match="Invalid parent"):
            hierarchy.register_agent("coder", "RUN-2", AgentRole.SPECIALIST, parent_id="INVALID")


class TestCircularRelationshipDetection:
    """Test detection of circular relationships."""

    @pytest.fixture
    def hierarchy(self, tmp_path):
        """Create a hierarchy manager."""
        return AgentHierarchyManager(tmp_path / "hierarchy")

    def test_detect_no_circular_relationship(self, hierarchy):
        """Test no cycle detected in valid hierarchy."""
        hierarchy.register_agent("exec", "RUN-1", AgentRole.EXECUTIVE, validate=False)
        hierarchy.register_agent("lead", "RUN-2", AgentRole.TEAM_LEAD, parent_id="RUN-1", validate=False)
        hierarchy.register_agent("spec", "RUN-3", AgentRole.SPECIALIST, parent_id="RUN-2", validate=False)

        cycle = hierarchy.detect_circular_relationships("RUN-1")
        assert cycle == []

    def test_detect_direct_circular_relationship(self, hierarchy):
        """Test detection of direct circular relationship."""
        hierarchy.register_agent("agent1", "RUN-1", AgentRole.SPECIALIST, validate=False)
        hierarchy.register_agent("agent2", "RUN-2", AgentRole.SPECIALIST, parent_id="RUN-1", validate=False)

        # Manually create circular reference (shouldn't happen in normal flow)
        agent1 = hierarchy.get_agent("RUN-1")
        agent1.parent_id = "RUN-2"

        cycle = hierarchy.detect_circular_relationships("RUN-1")
        assert len(cycle) > 0
        assert "RUN-1" in cycle
        assert "RUN-2" in cycle

    def test_detect_indirect_circular_relationship(self, hierarchy):
        """Test detection of indirect circular relationship."""
        hierarchy.register_agent("agent1", "RUN-1", AgentRole.SPECIALIST, validate=False)
        hierarchy.register_agent("agent2", "RUN-2", AgentRole.SPECIALIST, parent_id="RUN-1", validate=False)
        hierarchy.register_agent("agent3", "RUN-3", AgentRole.SPECIALIST, parent_id="RUN-2", validate=False)

        # Create circular reference
        agent3 = hierarchy.get_agent("RUN-3")
        agent3.parent_id = "RUN-1"  # Creates cycle: RUN-1 -> RUN-2 -> RUN-3 -> RUN-1

        cycle = hierarchy.detect_circular_relationships("RUN-1")
        assert len(cycle) > 0

    def test_prevent_circular_on_register(self, hierarchy):
        """Test that register_agent prevents circular relationships."""
        hierarchy.register_agent("agent1", "RUN-1", AgentRole.SPECIALIST, validate=False)
        hierarchy.register_agent("agent2", "RUN-2", AgentRole.SPECIALIST, parent_id="RUN-1", validate=False)

        # Try to create circular relationship by making RUN-1's parent RUN-2
        # This should be detected when trying to register
        agent1 = hierarchy.get_agent("RUN-1")
        agent1.parent_id = "RUN-2"  # Creates cycle: RUN-1 -> RUN-2 -> RUN-1

        # Detection should find the cycle
        cycle = hierarchy.detect_circular_relationships("RUN-1")
        assert len(cycle) > 0


class TestOrphanedAgentDetection:
    """Test detection of orphaned agents."""

    @pytest.fixture
    def hierarchy(self, tmp_path):
        """Create a hierarchy manager."""
        return AgentHierarchyManager(tmp_path / "hierarchy")

    def test_detect_orphaned_agent_with_missing_parent(self, hierarchy):
        """Test detection of agent with missing parent."""
        # Create agent with invalid parent reference
        hierarchy.register_agent("coder", "RUN-1", AgentRole.SPECIALIST, parent_id="MISSING", validate=False)

        orphaned = hierarchy.detect_orphaned_agents()
        assert len(orphaned) > 0
        assert any("RUN-1" in str(item) for item in orphaned)
        assert any("does not exist" in str(item[1]).lower() for item in orphaned)

    def test_detect_orphaned_agent_with_inactive_parent(self, hierarchy):
        """Test detection of agent with inactive parent."""
        hierarchy.register_agent("parent", "RUN-PARENT", AgentRole.TEAM_LEAD, validate=False)
        hierarchy.register_agent("child", "RUN-CHILD", AgentRole.SPECIALIST, parent_id="RUN-PARENT", validate=False)
        hierarchy.update_agent_status("RUN-PARENT", "inactive")

        orphaned = hierarchy.detect_orphaned_agents()
        assert len(orphaned) > 0
        assert any("RUN-CHILD" in str(item) for item in orphaned)
        assert any("not active" in str(item[1]).lower() for item in orphaned)

    def test_detect_orphaned_agent_with_missing_team(self, hierarchy):
        """Test detection of agent with missing team."""
        hierarchy.register_agent("coder", "RUN-1", AgentRole.SPECIALIST, team_id="MISSING-TEAM", validate=False)

        orphaned = hierarchy.detect_orphaned_agents()
        assert len(orphaned) > 0
        assert any("RUN-1" in str(item) for item in orphaned)
        assert any("team" in str(item[1]).lower() for item in orphaned)

    def test_detect_orphaned_agent_not_in_team_members(self, hierarchy):
        """Test detection of agent not in team members list."""
        hierarchy.create_team(
            "TEAM-1", "Test Team", "Description", TeamType.FUNCTIONAL, CoordinationMode.HIERARCHICAL, "RUN-LEAD"
        )
        hierarchy.register_agent("coder", "RUN-1", AgentRole.SPECIALIST, team_id="TEAM-1", validate=False)

        orphaned = hierarchy.detect_orphaned_agents()
        # Agent should be orphaned because team doesn't have it in members
        assert any("RUN-1" in str(item) for item in orphaned)

    def test_no_orphaned_agents_in_valid_hierarchy(self, hierarchy):
        """Test no orphaned agents in valid hierarchy."""
        hierarchy.register_agent("exec", "RUN-1", AgentRole.EXECUTIVE, validate=False)
        hierarchy.register_agent("lead", "RUN-2", AgentRole.TEAM_LEAD, parent_id="RUN-1", validate=False)
        hierarchy.create_team(
            "TEAM-1", "Test Team", "Description", TeamType.FUNCTIONAL, CoordinationMode.HIERARCHICAL, "RUN-2"
        )
        hierarchy.register_agent("spec", "RUN-3", AgentRole.SPECIALIST, parent_id="RUN-2", team_id="TEAM-1", validate=False)
        hierarchy.add_team_member("TEAM-1", "RUN-3")

        orphaned = hierarchy.detect_orphaned_agents()
        # Should have no orphaned agents
        assert len(orphaned) == 0


class TestTeamConsistencyChecks:
    """Test team consistency validation."""

    @pytest.fixture
    def hierarchy(self, tmp_path):
        """Create a hierarchy manager."""
        return AgentHierarchyManager(tmp_path / "hierarchy")

    def test_check_team_with_missing_lead(self, hierarchy):
        """Test detection of team with missing lead."""
        hierarchy.create_team(
            "TEAM-1", "Test Team", "Description", TeamType.FUNCTIONAL, CoordinationMode.HIERARCHICAL, "MISSING-LEAD"
        )

        inconsistencies = hierarchy.check_team_consistency()
        assert len(inconsistencies) > 0
        assert any("TEAM-1" in str(item) for item in inconsistencies)
        assert any("lead" in str(item[1]).lower() for item in inconsistencies)

    def test_check_team_with_inactive_lead(self, hierarchy):
        """Test detection of team with inactive lead."""
        hierarchy.register_agent("lead", "RUN-LEAD", AgentRole.TEAM_LEAD, validate=False)
        hierarchy.create_team(
            "TEAM-1", "Test Team", "Description", TeamType.FUNCTIONAL, CoordinationMode.HIERARCHICAL, "RUN-LEAD"
        )
        hierarchy.update_agent_status("RUN-LEAD", "inactive")

        inconsistencies = hierarchy.check_team_consistency()
        assert len(inconsistencies) > 0
        assert any("not active" in str(item[1]).lower() for item in inconsistencies)

    def test_check_team_with_missing_member(self, hierarchy):
        """Test detection of team with missing member."""
        hierarchy.register_agent("lead", "RUN-LEAD", AgentRole.TEAM_LEAD, validate=False)
        hierarchy.create_team(
            "TEAM-1", "Test Team", "Description", TeamType.FUNCTIONAL, CoordinationMode.HIERARCHICAL, "RUN-LEAD"
        )
        team = hierarchy.get_team("TEAM-1")
        team.members.append("MISSING-MEMBER")
        hierarchy._save()

        inconsistencies = hierarchy.check_team_consistency()
        assert len(inconsistencies) > 0
        assert any("MISSING-MEMBER" in str(item) for item in inconsistencies)

    def test_check_team_with_duplicate_members(self, hierarchy):
        """Test detection of team with duplicate members."""
        hierarchy.register_agent("lead", "RUN-LEAD", AgentRole.TEAM_LEAD, validate=False)
        hierarchy.register_agent("member", "RUN-MEMBER", AgentRole.SPECIALIST, validate=False)
        hierarchy.create_team(
            "TEAM-1", "Test Team", "Description", TeamType.FUNCTIONAL, CoordinationMode.HIERARCHICAL, "RUN-LEAD"
        )
        team = hierarchy.get_team("TEAM-1")
        team.members.extend(["RUN-MEMBER", "RUN-MEMBER"])  # Duplicate
        hierarchy._save()

        inconsistencies = hierarchy.check_team_consistency()
        assert len(inconsistencies) > 0
        assert any("duplicate" in str(item[1]).lower() for item in inconsistencies)

    def test_check_consistent_team(self, hierarchy):
        """Test consistent team passes validation."""
        hierarchy.register_agent("lead", "RUN-LEAD", AgentRole.TEAM_LEAD, validate=False)
        hierarchy.register_agent("member", "RUN-MEMBER", AgentRole.SPECIALIST, validate=False)
        hierarchy.create_team(
            "TEAM-1", "Test Team", "Description", TeamType.FUNCTIONAL, CoordinationMode.HIERARCHICAL, "RUN-LEAD"
        )
        hierarchy.add_team_member("TEAM-1", "RUN-MEMBER")

        inconsistencies = hierarchy.check_team_consistency()
        assert len(inconsistencies) == 0


class TestHandoffIntegrityValidation:
    """Test handoff integrity validation (WP-16005)."""

    @pytest.fixture
    def handoff(self, tmp_path):
        """Create a HandoffIntegrity instance."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        (workspace / "src").mkdir()
        (workspace / "src" / "main.py").write_text("print('hello')")
        return HandoffIntegrity(workspace)

    def test_analyze_complete_prompt(self, handoff):
        """Test analysis of complete prompt."""
        prompt = "Create a new function in src/main.py that calculates the sum of two numbers."
        analysis = handoff.analyze_prompt(prompt)

        assert analysis["is_complete"] is True
        assert len(analysis["findings"]) == 0
        assert len(analysis["referenced_files"]) > 0
        assert analysis["has_action"] is True
        assert analysis["has_context"] is True

    def test_analyze_vague_prompt(self, handoff):
        """Test analysis of vague prompt."""
        prompt = "Implement this."
        analysis = handoff.analyze_prompt(prompt)

        assert analysis["is_complete"] is False
        assert len(analysis["findings"]) > 0
        assert any("vague" in f.lower() for f in analysis["findings"])

    def test_analyze_short_prompt(self, handoff):
        """Test analysis of very short prompt."""
        prompt = "Fix it"
        analysis = handoff.analyze_prompt(prompt)

        assert analysis["is_complete"] is False
        assert any("short" in f.lower() for f in analysis["findings"])

    def test_analyze_prompt_with_missing_files(self, handoff):
        """Test analysis of prompt referencing missing files."""
        prompt = "Update the code in src/nonexistent.py to add error handling."
        analysis = handoff.analyze_prompt(prompt)

        assert len(analysis["missing_files"]) > 0
        assert len(analysis["warnings"]) > 0

    def test_suggest_improvements(self, handoff):
        """Test suggestion generation for incomplete prompt."""
        prompt = "Fix the bug"
        improved = handoff.suggest_improvements(prompt)

        assert "Suggestions" in improved
        assert len(improved) > len(prompt)

    def test_validate_handoff_valid(self, handoff):
        """Test validation of valid handoff prompt."""
        prompt = "Create a new function in src/main.py that calculates the sum of two numbers because we need to add this feature."
        is_valid, error = handoff.validate_handoff(prompt)

        assert is_valid is True
        assert error == "Handoff prompt is valid"

    def test_validate_handoff_invalid(self, handoff):
        """Test validation of invalid handoff prompt."""
        prompt = "Fix it"
        is_valid, error = handoff.validate_handoff(prompt)

        assert is_valid is False
        assert len(error) > 0

    def test_completeness_score_calculation(self, handoff):
        """Test completeness score calculation."""
        # Low score prompt
        prompt1 = "Fix"
        analysis1 = handoff.analyze_prompt(prompt1)
        assert analysis1["completeness_score"] < 2

        # High score prompt
        prompt2 = "Create a new function in src/main.py that calculates the sum because we need this feature. Here's an example: ```python\ndef add(a, b):\n    return a + b\n```"
        analysis2 = handoff.analyze_prompt(prompt2)
        assert analysis2["completeness_score"] >= 2
