"""Tests for WP-Y5: Hierarchical prompt orchestration."""

from unittest.mock import MagicMock

import pytest
from thegent.orchestration.execution.prompts import PromptOrchestrator

from thegent.config import ThegentSettings


@pytest.fixture
def mock_settings():
    return MagicMock(spec=ThegentSettings)


def test_prompt_orchestrator_decomposes_complex_goal(mock_settings):
    orchestrator = PromptOrchestrator(mock_settings)

    goal = "Create a new database schema and implement the repository layer and add unit tests"
    sub_tasks = orchestrator.decompose(goal)

    assert len(sub_tasks) >= 2
    assert sub_tasks[0]["id"] == "task_1"
    assert "depends_on" in sub_tasks[1]


def test_prompt_orchestrator_routes_subtasks(mock_settings):
    orchestrator = PromptOrchestrator(mock_settings)

    tasks = [
        {"id": "t1", "prompt": "Implement the core logic"},
        {"id": "t2", "prompt": "Write unit tests for the logic"},
    ]

    routed = orchestrator.route_subtasks(tasks)

    assert routed[0]["agent"] == "atoms-developer"
    assert routed[1]["agent"] == "quality-agent"
