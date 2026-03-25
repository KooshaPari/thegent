"""Tests for task/workstream sync behavior."""

from pathlib import Path

from thegent.task.sync import WorkStreamSync


def test_update_work_stream_from_tasks_fails_on_parse_error(tmp_path: Path) -> None:
    """Malformed task files should fail hard instead of being silently skipped."""
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir()

    valid_task = tasks_dir / "good.md"
    valid_task.write_text(
        "---\nid: WS-001\ntitle: Good task\ndepends: []\n---\n\n## Description\nTest\n",
        encoding="utf-8",
    )
    (tasks_dir / "bad.md").write_text("this is not a task file", encoding="utf-8")

    ws = tmp_path / "docs" / "reference" / "WORK_STREAM.md"
    ws.parent.mkdir(parents=True)
    ws.write_text(
        "# WORK_STREAM\n\n## BACKLOG\n\n| ID | Title | Source | Priority | Depends |\n|----|-------|--------|----------|---------|\n\n## CLAIMED\n",
        encoding="utf-8",
    )

    sync = WorkStreamSync(ws, tasks_dir)
    result = sync.update_work_stream_from_tasks()

    assert "error" in result
    assert result["tasks_synced"] == 0
    assert any("bad.md" in err for err in result["task_parse_errors"])


def test_get_task_status_reads_struck_backlog_id_as_completed(tmp_path: Path) -> None:
    """STATUS checks should read ID out of struck-through table cells."""
    ws = tmp_path / "docs" / "reference" / "WORK_STREAM.md"
    ws.parent.mkdir(parents=True)
    ws.write_text(
        "## COMPLETED\n| ID | Agent | Completed |\n|----|-------|-----------|\n| ~~WS-001~~ | Agent | 2026-02-20T11:00:00Z |\n",
        encoding="utf-8",
    )

    sync = WorkStreamSync(ws, tmp_path / "tasks")
    assert sync.get_task_status("WS-001") == "COMPLETED"


def test_claim_task_reports_dependency_errors_for_task_file(tmp_path: Path) -> None:
    """Claim should fail when dependencies are not satisfied."""
    ws = tmp_path / "docs" / "reference" / "WORK_STREAM.md"
    ws.parent.mkdir(parents=True)
    ws.write_text(
        "## BACKLOG\n| ID | Title | Source | Priority | Depends |\n|----|-------|--------|----------|---------|\n| WS-001 | Parent task | Task | P1 | - |\n\n## CLAIMED\n\n## COMPLETED\n",
        encoding="utf-8",
    )
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir()
    (tasks_dir / "WS-001.md").write_text(
        "---\nid: WS-001\ntitle: Parent task\ndepends:\n  - WS-099\n---\n",
        encoding="utf-8",
    )

    sync = WorkStreamSync(ws, tasks_dir)
    result = sync.claim_task("WS-001", "agent-1")

    assert "error" in result
    assert "unmet dependencies" in result["error"]
    assert result["unmet_dependencies"] == ["WS-099"]


def test_claim_task_returns_error_when_task_file_is_invalid(tmp_path: Path) -> None:
    """Invalid task files should produce an explicit dependency validation error."""
    ws = tmp_path / "docs" / "reference" / "WORK_STREAM.md"
    ws.parent.mkdir(parents=True)
    ws.write_text(
        "## BACKLOG\n| ID | Title | Source | Priority | Depends |\n|----|-------|--------|----------|---------|\n| WS-001 | Parent task | Task | P1 | - |\n\n## CLAIMED\n\n## COMPLETED\n",
        encoding="utf-8",
    )
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir()
    (tasks_dir / "WS-001.md").write_text("invalid", encoding="utf-8")

    sync = WorkStreamSync(ws, tasks_dir)
    result = sync.claim_task("WS-001", "agent-1")

    assert result["error"].startswith("Failed dependency validation for WS-001")


def test_update_work_stream_from_tasks_fails_on_duplicate_task_ids(tmp_path: Path) -> None:
    """Duplicate task IDs should fail immediately and avoid partial sync."""
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir()

    for idx in ("a", "b"):
        (tasks_dir / f"{idx}-{idx}.md").write_text(
            f"---\nid: WS-001\ntitle: Duplicate {idx}\ndepends: []\n---\n",
            encoding="utf-8",
        )

    ws = tmp_path / "docs" / "reference" / "WORK_STREAM.md"
    ws.parent.mkdir(parents=True)
    ws.write_text(
        "# WORK_STREAM\n\n## BACKLOG\n| ID | Title | Source | Priority | Depends |\n|----|-------|--------|----------|---------|\n## CLAIMED\n",
        encoding="utf-8",
    )

    sync = WorkStreamSync(ws, tasks_dir)
    result = sync.update_work_stream_from_tasks()

    assert "error" in result
    assert result["tasks_synced"] == 0
    assert any("duplicate task id WS-001" in err for err in result["task_parse_errors"])


def test_claim_task_fails_when_task_file_id_mismatch(tmp_path: Path) -> None:
    """Claiming should fail if the task file id does not match requested task id."""
    ws = tmp_path / "docs" / "reference" / "WORK_STREAM.md"
    ws.parent.mkdir(parents=True)
    ws.write_text(
        "## BACKLOG\n| ID | Title | Source | Priority | Depends |\n|----|-------|--------|----------|---------|\n| WS-001 | Parent task | Task | P1 | - |\n\n## CLAIMED\n\n## COMPLETED\n",
        encoding="utf-8",
    )
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir()
    (tasks_dir / "WS-001.md").write_text(
        "---\nid: WS-002\ntitle: Parent task\ndepends: []\n---\n",
        encoding="utf-8",
    )

    sync = WorkStreamSync(ws, tasks_dir)
    result = sync.claim_task("WS-001", "agent-1")

    assert "error" in result
    assert "Task file id mismatch for WS-001" in result["error"]
