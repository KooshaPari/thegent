"""Tests for task parser."""

from pathlib import Path

import pytest

from thegent.task.parser import parse_task_file, parse_yaml_frontmatter


def test_parse_yaml_frontmatter_valid():
    """Test parsing valid YAML frontmatter."""
    content = """---
id: test-task
title: Test Task
priority: P1
---
## Body
Test body content
"""
    frontmatter, body = parse_yaml_frontmatter(content)
    assert frontmatter["id"] == "test-task"
    assert frontmatter["title"] == "Test Task"
    assert frontmatter["priority"] == "P1"
    assert "Body" in body
    assert "Test body content" in body


def test_parse_yaml_frontmatter_invalid():
    """Test parsing invalid YAML frontmatter."""
    content = """---
id: test-task
invalid: yaml: syntax: error
---
"""
    with pytest.raises(ValueError):
        parse_yaml_frontmatter(content)


def test_parse_task_file_yaml(tmp_path: Path):
    """Test parsing a task file with YAML frontmatter."""
    task_file = tmp_path / "test-task.md"
    task_file.write_text("""---
id: test-task
title: Test Task
subagent_type: worker
priority: P1
depends: []
---
## Description
Test task description
""")

    task = parse_task_file(task_file)
    assert task["id"] == "test-task"
    assert task["title"] == "Test Task"
    assert task["subagent_type"] == "worker"
    assert task["priority"] == "P1"
    assert task["depends"] == []
