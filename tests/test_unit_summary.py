"""Unit tests for summary git commit diagnostics."""

import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from thegent.summary import get_git_commits


def _window() -> tuple[datetime, datetime]:
    end = datetime.now(UTC)
    start = end - timedelta(days=1)
    return start, end


def test_get_git_commits_non_repo_returns_diagnostic_status(tmp_path: Path) -> None:
    start, end = _window()
    result = get_git_commits(tmp_path, start, end)
    assert result.commits == []
    assert result.status == "not_repo"
    assert result.error is not None
    assert result.error["type"] == "not_repo"


def test_get_git_commits_git_command_failure_logs_context(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    (tmp_path / ".git").mkdir()

    def _failed_run(*args, **kwargs):  # noqa: ANN002, ANN003
        return subprocess.CompletedProcess(
            args=["git", "log"],
            returncode=128,
            stdout="",
            stderr="fatal: bad revision",
        )

    monkeypatch.setattr("thegent.summary.subprocess.run", _failed_run)
    caplog.set_level("WARNING", logger="thegent.summary")

    start, end = _window()
    result = get_git_commits(tmp_path, start, end)

    assert result.commits == []
    assert result.status == "error"
    assert result.error is not None
    assert result.error["type"] == "git_log_failed"
    assert "Git commit collection failed:" in caplog.text
    assert str(tmp_path) in caplog.text
    assert "git log" in caplog.text
