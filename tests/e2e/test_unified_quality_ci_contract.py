"""Contract checks for unified quality CI control-plane wiring."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TASKFILE = ROOT / "Taskfile.yml"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


def test_taskfile_declares_unified_quality_control_plane_tasks() -> None:
    text = TASKFILE.read_text(encoding="utf-8")
    for token in (
        "quality:ci:unified:",
        "quality:aggregate:artifacts:",
        "quality:gate-policy:validate:",
        "quality:gate:unified:",
    ):
        assert token in text


def test_ci_workflow_has_quality_unified_job_on_pr_and_schedule() -> None:
    text = CI_WORKFLOW.read_text(encoding="utf-8")
    assert "schedule:" in text
    assert "quality-unified:" in text
    assert "github.event_name == 'pull_request' || github.event_name == 'schedule'" in text


def test_ci_workflow_sets_mode_from_event_and_runs_unified_task() -> None:
    text = CI_WORKFLOW.read_text(encoding="utf-8")
    assert "export QUALITY_UNIFIED_MODE=nightly" in text
    assert "export QUALITY_UNIFIED_MODE=pr" in text
    assert "task quality:ci:unified" in text


def test_ci_workflow_uploads_unified_sarif_feeds() -> None:
    text = CI_WORKFLOW.read_text(encoding="utf-8")
    assert "github/codeql-action/upload-sarif@v3" in text
    assert "artifacts/hooks/hooks-results.sarif" in text
    assert "artifacts/quality/generated-python-antipatterns.sarif" in text
