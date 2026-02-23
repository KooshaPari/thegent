"""Tests for WL-234: Incident Runbook.

Tests cover:
- RunbookStep dataclass creation
- IncidentRunbook step management
- Step retrieval and ordering
- Markdown rendering
"""

from __future__ import annotations

import pytest

from thegent.integrations.incident_runbook import IncidentRunbook, RunbookStep


@pytest.mark.requirement("WL-234")
class TestRunbookStep:
    """Tests for the RunbookStep dataclass."""

    def test_runbook_step_creation(self) -> None:
        """Test creating a RunbookStep."""
        step = RunbookStep(
            step_id="step-1",
            title="Check service status",
            instructions="Use kubectl to verify the pod is running",
        )
        assert step.step_id == "step-1"
        assert step.title == "Check service status"
        assert step.instructions == "Use kubectl to verify the pod is running"

    def test_runbook_step_attributes(self) -> None:
        """Test all RunbookStep attributes are accessible."""
        step = RunbookStep(
            step_id="rollback-db",
            title="Rollback database",
            instructions="Run migration backward",
        )
        assert hasattr(step, "step_id")
        assert hasattr(step, "title")
        assert hasattr(step, "instructions")


@pytest.mark.requirement("WL-234")
class TestIncidentRunbook:
    """Tests for the IncidentRunbook class."""

    def test_create_empty_runbook(self) -> None:
        """Test creating an empty runbook."""
        runbook = IncidentRunbook()
        assert runbook.steps() == []

    def test_add_single_step(self) -> None:
        """Test adding a single step to a runbook."""
        runbook = IncidentRunbook()
        step = runbook.add_step(
            "alert-received",
            "Alert Received",
            "Acknowledge the alert in PagerDuty",
        )
        assert step.step_id == "alert-received"
        assert len(runbook.steps()) == 1

    def test_add_multiple_steps_preserves_order(self) -> None:
        """Test that multiple steps are preserved in order."""
        runbook = IncidentRunbook()
        step1 = runbook.add_step("s1", "First", "Do first")
        step2 = runbook.add_step("s2", "Second", "Do second")
        step3 = runbook.add_step("s3", "Third", "Do third")

        steps = runbook.steps()
        assert len(steps) == 3
        assert steps[0].step_id == "s1"
        assert steps[1].step_id == "s2"
        assert steps[2].step_id == "s3"

    def test_get_step_returns_correct_step(self) -> None:
        """Test retrieving a step by ID."""
        runbook = IncidentRunbook()
        runbook.add_step("step-a", "Step A", "Instructions A")
        runbook.add_step("step-b", "Step B", "Instructions B")

        retrieved = runbook.get_step("step-a")
        assert retrieved.step_id == "step-a"
        assert retrieved.title == "Step A"
        assert retrieved.instructions == "Instructions A"

    def test_get_step_raises_keyerror_for_missing(self) -> None:
        """Test that get_step raises KeyError for missing step."""
        runbook = IncidentRunbook()
        with pytest.raises(KeyError):
            runbook.get_step("nonexistent")

    def test_duplicate_step_id_overwrites(self) -> None:
        """Test adding a step with duplicate ID overwrites the previous one."""
        runbook = IncidentRunbook()
        runbook.add_step("dup", "First Title", "First Instructions")
        runbook.add_step("dup", "Second Title", "Second Instructions")

        steps = runbook.steps()
        assert len(steps) == 1
        assert steps[0].title == "Second Title"

    def test_render_markdown_empty(self) -> None:
        """Test rendering empty runbook produces empty string."""
        runbook = IncidentRunbook()
        markdown = runbook.render_markdown()
        assert markdown == ""

    def test_render_markdown_single_step(self) -> None:
        """Test rendering runbook with single step."""
        runbook = IncidentRunbook()
        runbook.add_step("step-1", "Check Status", "Verify the service is responding")

        markdown = runbook.render_markdown()
        assert "1." in markdown
        assert "Check Status" in markdown
        assert "`step-1`" in markdown
        assert "Verify the service is responding" in markdown

    def test_render_markdown_multiple_steps(self) -> None:
        """Test rendering runbook with multiple steps."""
        runbook = IncidentRunbook()
        runbook.add_step("s1", "Alert", "Receive alert")
        runbook.add_step("s2", "Investigate", "Investigate root cause")
        runbook.add_step("s3", "Resolve", "Fix the issue")

        markdown = runbook.render_markdown()
        assert "1." in markdown
        assert "2." in markdown
        assert "3." in markdown
        assert "Alert" in markdown
        assert "Investigate" in markdown
        assert "Resolve" in markdown

    def test_render_markdown_formatting(self) -> None:
        """Test that markdown rendering includes proper formatting."""
        runbook = IncidentRunbook()
        runbook.add_step("test-id", "Test Title", "Test instructions")

        markdown = runbook.render_markdown()
        assert "**Test Title**" in markdown
        assert "(`test-id`)" in markdown
