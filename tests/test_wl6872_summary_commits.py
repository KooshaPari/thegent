"""WL-6872: distinguish empty git windows from real git command failures."""

import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from thegent import summary


def _time_range() -> tuple[datetime, datetime]:
    end = datetime.now(UTC)
    start = end - timedelta(days=1)
    return start, end


def test_wl6872_get_git_commits_non_repo_path_reports_not_repo(tmp_path: Path) -> None:
    start, end = _time_range()

    result = summary.get_git_commits(tmp_path, start, end)

    assert result.status == "not_repo"
    assert result.commits == []
    assert result.error is not None
    assert result.error["type"] == "not_repo"


def test_wl6872_get_git_commits_git_command_failure_reports_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    (tmp_path / ".git").mkdir()
    start, end = _time_range()
    monkeypatch.setattr(
        summary.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            ["git", "log"], 128, stdout="", stderr="fatal: bad revision"
        ),
    )

    result = summary.get_git_commits(tmp_path, start, end)

    assert result.status == "error"
    assert result.commits == []
    assert result.error is not None
    assert result.error["type"] == "git_log_failed"
    assert result.error["returncode"] == 128


def test_wl6872_get_git_commits_no_commit_window_reports_empty(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    (tmp_path / ".git").mkdir()
    start, end = _time_range()
    monkeypatch.setattr(
        summary.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess(
            ["git", "log"],
            128,
            stdout="",
            stderr="fatal: your current branch 'main' does not have any commits yet",
        ),
    )

    result = summary.get_git_commits(tmp_path, start, end)

    assert result.status == "empty"
    assert result.commits == []
    assert result.error is None
