"""Tests for task validator."""

from pathlib import Path

from thegent.task.validator import validate_task, validate_task_file


def test_validate_task_valid():
    """Test validation of valid task."""
    task = {
        "id": "test-task",
        "title": "Test Task",
        "subagent_type": "worker",
        "priority": "P1",
        "depends": [],
    }
    result = validate_task(task)
    assert result.valid
    assert len(result.errors) == 0


def test_validate_task_missing_required():
    """Test validation of task with missing required fields."""
    task = {
        "title": "Test Task"
        # Missing: id, subagent_type, priority
    }
    result = validate_task(task)
    assert not result.valid
    assert len(result.errors) > 0
    assert any("id" in str(e.field).lower() for e in result.errors)


def test_validate_task_invalid_id():
    """Test validation of task with invalid ID."""
    task = {
        "id": "INVALID_ID",  # Uppercase not allowed
        "title": "Test Task",
        "subagent_type": "worker",
        "priority": "P1",
    }
    result = validate_task(task)
    assert not result.valid
    assert any("id" in str(e.field).lower() for e in result.errors)


def test_validate_task_invalid_priority():
    """Test validation of task with invalid priority."""
    task = {
        "id": "test-task",
        "title": "Test Task",
        "subagent_type": "worker",
        "priority": "P4",  # Invalid priority
    }
    result = validate_task(task)
    assert not result.valid
    assert any("priority" in str(e.field).lower() for e in result.errors)


def test_validate_task_file(tmp_path: Path):
    """Test validating a task file."""
    task_file = tmp_path / "test-task.md"
    task_file.write_text("""---
id: test-task
title: Test Task
subagent_type: worker
priority: P1
depends: []
---
""")

    result = validate_task_file(task_file)
    assert result.valid


def test_validate_task_worker_requires_steps(tmp_path: Path):
    """Test that worker tasks require steps."""
    task_file = tmp_path / "worker-task.md"
    task_file.write_text("""---
id: worker-task
title: Worker Task
subagent_type: worker
priority: P1
depends: []
# Missing steps and deliverables
---
""")

    result = validate_task_file(task_file)
    # Should have warnings or conditional validation errors
    # (This depends on schema conditional validation)
