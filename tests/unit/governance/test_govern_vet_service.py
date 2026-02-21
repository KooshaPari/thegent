from __future__ import annotations

import json
from pathlib import Path

import pytest

from thegent.cli.services import governance as governance_service


def _seed_run(session_dir: Path, run_id: str, *, stdout_text: str, stderr_text: str = "") -> None:
    stdout_path = session_dir / f"{run_id}.stdout.log"
    stderr_path = session_dir / f"{run_id}.stderr.log"
    stdout_path.write_text(stdout_text, encoding="utf-8")
    stderr_path.write_text(stderr_text, encoding="utf-8")

    registry_path = session_dir / "run_registry.jsonl"
    start = {
        "run_id": run_id,
        "event": "started",
        "status": "started",
        "correlation_id": "sess_test_01",
        "agent": "codex",
        "cwd": str(session_dir),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
    }
    registry_path.write_text(json.dumps(start) + "\n", encoding="utf-8")


def test_govern_vet_impl_rejects_on_safety_violation(tmp_path: Path) -> None:
    _seed_run(tmp_path, "run_bad", stdout_text="contact me at alice@example.com")

    result = governance_service.govern_vet_impl(run_id="run_bad", session=str(tmp_path))

    assert result["verdict"] == "rejected"
    assert any(check["check_name"] == "safety" and check["passed"] is False for check in result["checks"])
    events_path = tmp_path / "governance_events.jsonl"
    assert events_path.exists()


def test_govern_vet_impl_approves_clean_output(tmp_path: Path) -> None:
    _seed_run(tmp_path, "run_good", stdout_text="all clear output")

    result = governance_service.govern_vet_impl(run_id="run_good", session=str(tmp_path))

    assert result["verdict"] == "approved"
    assert all(check["passed"] is True for check in result["checks"])


def test_govern_vet_impl_dry_run_skips_execution(tmp_path: Path) -> None:
    _seed_run(tmp_path, "run_dry", stdout_text="safe output")

    result = governance_service.govern_vet_impl(run_id="run_dry", session=str(tmp_path), dry_run=True)

    assert result["verdict"] == "dry_run"
    assert all(check["passed"] is None for check in result["checks"])
    assert not (tmp_path / "governance_events.jsonl").exists()


def test_govern_vet_impl_raises_for_missing_run(tmp_path: Path) -> None:
    (tmp_path / "run_registry.jsonl").write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="Run not found"):
        governance_service.govern_vet_impl(run_id="run_missing", session=str(tmp_path))
