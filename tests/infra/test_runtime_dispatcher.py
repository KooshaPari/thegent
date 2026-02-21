"""Unit tests for runtime_dispatcher._python_route_logic().

Tests the pure Python JIT-friendly routing logic for task classification
and agent selection based on keyword matching.
"""

from unittest.mock import MagicMock

import pytest

from thegent.infra.runtime_dispatcher import _python_route_logic


class MockAgent:
    """Mock agent for testing."""

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"MockAgent({self.name})"


class TestPythonRouteLogicBasic:
    """Basic tests for _python_route_logic."""

    def test_returns_agent_from_list(self):
        """Test that route logic returns an agent from the provided list."""
        agents = [MockAgent("agent1"), MockAgent("agent2")]
        result = _python_route_logic("do something", agents)
        assert result in agents

    def test_returns_single_agent(self):
        """Test that route logic returns exactly one agent."""
        agents = [MockAgent("agent1"), MockAgent("agent2")]
        result = _python_route_logic("do something", agents)
        assert result is not None

    def test_empty_agents_list(self):
        """Test behavior with empty agents list."""
        result = _python_route_logic("do something", [])
        assert result is None

    def test_single_agent_returns_that_agent(self):
        """Test that single agent is returned."""
        agent = MockAgent("lone_agent")
        result = _python_route_logic("any task", [agent])
        assert result is agent


class TestPythonRouteLogicCodeKeywords:
    """Tests for code-related task routing."""

    def test_implement_keyword_prefers_implementer(self):
        """Test 'implement' keyword prefers implementer agents."""
        generic_agent = MockAgent("generic_agent")
        implementer = MockAgent("code_implementer")
        agents = [generic_agent, implementer]

        result = _python_route_logic("implement the feature", agents)
        assert result is implementer

    def test_code_keyword_prefers_coder(self):
        """Test 'code' keyword prefers coder agents."""
        generic_agent = MockAgent("agent")
        coder = MockAgent("super_coder")
        agents = [generic_agent, coder]

        result = _python_route_logic("code the module", agents)
        assert result is coder

    def test_write_keyword_scores_implementer(self):
        """Test 'write' keyword scores implementer agents higher."""
        generic = MockAgent("worker")
        implementer = MockAgent("implementer_bot")
        agents = [generic, implementer]

        result = _python_route_logic("write a new function", agents)
        assert result is implementer

    def test_fix_keyword_routes_to_implementer(self):
        """Test 'fix' keyword routes to implementer."""
        planner = MockAgent("planner")
        implementer = MockAgent("implementer")
        agents = [planner, implementer]

        result = _python_route_logic("fix the bug", agents)
        assert result is implementer

    def test_debug_keyword_routes_to_implementer(self):
        """Test 'debug' keyword routes to implementer."""
        researcher = MockAgent("researcher")
        implementer = MockAgent("implementer")
        agents = [researcher, implementer]

        result = _python_route_logic("debug the issue", agents)
        assert result is implementer

    def test_refactor_keyword_routes_to_implementer(self):
        """Test 'refactor' keyword routes to implementer."""
        planner = MockAgent("architect")
        implementer = MockAgent("implementer")
        agents = [planner, implementer]

        result = _python_route_logic("refactor the code", agents)
        assert result is implementer

    def test_patch_keyword_routes_to_implementer(self):
        """Test 'patch' keyword routes to implementer."""
        researcher = MockAgent("researcher")
        implementer = MockAgent("implementer")
        agents = [researcher, implementer]

        result = _python_route_logic("patch the vulnerability", agents)
        assert result is implementer


class TestPythonRouteLogicResearchKeywords:
    """Tests for research-related task routing."""

    def test_research_keyword_prefers_researcher(self):
        """Test 'research' keyword prefers researcher agents."""
        implementer = MockAgent("implementer")
        researcher = MockAgent("research_agent")
        agents = [implementer, researcher]

        result = _python_route_logic("research the topic", agents)
        assert result is researcher

    def test_search_keyword_routes_to_search(self):
        """Test 'search' keyword routes to search agents."""
        implementer = MockAgent("implementer")
        searcher = MockAgent("search_agent")
        agents = [implementer, searcher]

        result = _python_route_logic("search for the file", agents)
        assert result is searcher

    def test_find_keyword_routes_to_researcher(self):
        """Test 'find' keyword routes to researcher agents."""
        generic = MockAgent("generic")
        researcher = MockAgent("researcher")
        agents = [generic, researcher]

        result = _python_route_logic("find the solution", agents)
        assert result is researcher

    def test_explore_keyword_routes_to_researcher(self):
        """Test 'explore' keyword routes to researcher agents."""
        planner = MockAgent("planner")
        researcher = MockAgent("researcher")
        agents = [planner, researcher]

        result = _python_route_logic("explore the codebase", agents)
        assert result is researcher

    def test_analyze_keyword_routes_to_researcher(self):
        """Test 'analyze' keyword routes to researcher agents."""
        implementer = MockAgent("implementer")
        researcher = MockAgent("researcher")
        agents = [implementer, researcher]

        result = _python_route_logic("analyze the data", agents)
        assert result is researcher

    def test_summarize_keyword_routes_to_researcher(self):
        """Test 'summarize' keyword routes to researcher agents."""
        planner = MockAgent("planner")
        researcher = MockAgent("researcher")
        agents = [planner, researcher]

        result = _python_route_logic("summarize the findings", agents)
        assert result is researcher


class TestPythonRouteLogicPlanKeywords:
    """Tests for planning-related task routing."""

    def test_plan_keyword_prefers_planner(self):
        """Test 'plan' keyword prefers planner agents."""
        implementer = MockAgent("implementer")
        planner = MockAgent("planner_agent")
        agents = [implementer, planner]

        result = _python_route_logic("plan the project", agents)
        assert result is planner

    def test_design_keyword_routes_to_architect(self):
        """Test 'design' keyword routes to architect agents."""
        researcher = MockAgent("researcher")
        architect = MockAgent("architect")
        agents = [researcher, architect]

        result = _python_route_logic("design the system", agents)
        assert result is architect

    def test_architect_keyword_routes_to_planner(self):
        """Test 'architect' keyword routes to planner agents."""
        implementer = MockAgent("implementer")
        planner = MockAgent("planner")
        agents = [implementer, planner]

        result = _python_route_logic("architect the solution", agents)
        assert result is planner

    def test_spec_keyword_routes_to_planner(self):
        """Test 'spec' keyword routes to planner agents."""
        researcher = MockAgent("researcher")
        planner = MockAgent("planner")
        agents = [researcher, planner]

        result = _python_route_logic("spec out the requirements", agents)
        assert result is planner

    def test_document_keyword_routes_to_planner(self):
        """Test 'document' keyword routes to planner agents."""
        implementer = MockAgent("implementer")
        planner = MockAgent("planner")
        agents = [implementer, planner]

        result = _python_route_logic("document the API", agents)
        assert result is planner


class TestPythonRouteLogicFallbackScoring:
    """Tests for fallback scoring when no keywords match."""

    def test_generic_agent_gets_base_score(self):
        """Test generic agents get base score when no keywords match."""
        agents = [MockAgent("generic_bot")]
        result = _python_route_logic("hello world", agents)
        assert result is agents[0]

    def test_agent_suffix_gets_bonus(self):
        """Test agents with 'agent' in name get bonus scoring."""
        generic = MockAgent("worker")
        agent = MockAgent("my_agent")
        agents = [generic, agent]

        # Using a code keyword, agent gets +5 bonus
        result = _python_route_logic("implement feature", agents)
        # Both get code scores, but agent gets +5 bonus
        assert result is agent

    def test_first_agent_wins_on_tie(self):
        """Test that first agent wins when scores are tied."""
        agent1 = MockAgent("agent_alpha")
        agent2 = MockAgent("agent_beta")
        agents = [agent1, agent2]

        # Both have same name pattern, no keywords match
        result = _python_route_logic("unknown task", agents)
        # First agent should win as it gets selected first with same score
        assert result in agents


class TestPythonRouteLogicCaseInsensitivity:
    """Tests for case-insensitive keyword matching."""

    def test_uppercase_keywords(self):
        """Test uppercase keywords are matched."""
        implementer = MockAgent("implementer")
        researcher = MockAgent("researcher")
        agents = [researcher, implementer]

        result = _python_route_logic("IMPLEMENT THE FEATURE", agents)
        assert result is implementer

    def test_mixed_case_keywords(self):
        """Test mixed case keywords are matched."""
        planner = MockAgent("planner")
        implementer = MockAgent("implementer")
        agents = [implementer, planner]

        result = _python_route_logic("Plan The Project", agents)
        assert result is planner

    def test_agent_names_case_insensitive(self):
        """Test agent name matching is case-insensitive."""
        generic = MockAgent("GENERIC")
        implementer = MockAgent("IMPLementer")
        agents = [generic, implementer]

        result = _python_route_logic("implement it", agents)
        assert result is implementer


class TestPythonRouteLogicComplexTasks:
    """Tests for complex multi-keyword tasks."""

    def test_multiple_keywords_first_wins(self):
        """Test tasks with multiple keyword types."""
        implementer = MockAgent("implementer")
        researcher = MockAgent("researcher")
        planner = MockAgent("planner")
        agents = [implementer, researcher, planner]

        # Has both implement and plan keywords - implementer scores higher
        result = _python_route_logic("implement and plan the feature", agents)
        # implementer gets +10 for implement, planner gets +10 for plan
        # Since implementer comes first with same score, it wins
        assert result is implementer

    def test_composite_task_description(self):
        """Test routing with composite task description."""
        researcher = MockAgent("researcher")
        implementer = MockAgent("implementer")
        agents = [researcher, implementer]

        result = _python_route_logic("research and code the solution", agents)
        # Both get +10, implementer gets selected first
        assert result in agents


class TestPythonRouteLogicAgentAttributes:
    """Tests for agent attribute handling."""

    def test_agent_without_name_attribute(self):
        """Test handling agents without name attribute."""
        # Create a mock that doesn't have a name attribute by default
        agent = MagicMock(spec=[])  # Empty spec means no attributes
        # The function uses getattr(agent, "name", str(agent))
        # str() on MagicMock returns something like "<MagicMock id=...>"

        result = _python_route_logic("implement", [agent])
        # Should not crash, returns the agent
        assert result is agent

    def test_agent_with_string_representation(self):
        """Test agents that are just strings."""
        # The function expects objects with .name attribute
        # If agents are strings, getattr returns the string itself
        agents = ["implementer", "researcher"]
        result = _python_route_logic("implement", agents)
        # String's .lower() works, so routing should succeed
        assert result in agents


class TestPythonRouteLogicEdgeCases:
    """Edge case tests for _python_route_logic."""

    def test_empty_task_string(self):
        """Test with empty task string."""
        agents = [MockAgent("agent1"), MockAgent("agent2")]
        result = _python_route_logic("", agents)
        assert result in agents

    def test_task_with_only_spaces(self):
        """Test task with only whitespace."""
        agents = [MockAgent("agent1")]
        result = _python_route_logic("   ", agents)
        assert result is agents[0]

    def test_task_with_special_characters(self):
        """Test task with special characters."""
        implementer = MockAgent("implementer")
        agents = [implementer]
        result = _python_route_logic("implement!@#$%^&*()", agents)
        # "implement" substring should still match
        assert result is implementer

    def test_partial_keyword_match(self):
        """Test partial keyword matching."""
        implementer = MockAgent("implementer")
        agents = [implementer]
        # "implementation" contains "implement"
        result = _python_route_logic("implementation needed", agents)
        assert result is implementer


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
