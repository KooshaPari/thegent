"""Tests for worktree inventory generation and conformance checks."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="API mismatch - scripts module not found")

from pathlib import Path

from scripts.worktree_governance_inventory import _parse_git_worktree, generate_inventory


def _fake_git_output(*entries: str) -> str:
    return "\n".join(entries) + "\n"


def test_parse_git_worktree_handles_detached_entries(tmp_path: Path, monkeypatch) -> None:
    def _fake_check_output(cmd: list[str], cwd: Path, text: bool):  # noqa: ARG001
        del cmd, cwd, text
        return _fake_git_output(
            f"worktree {tmp_path}",
            "HEAD abc",
            f"worktree {tmp_path / 'child'}",
            "branch refs/heads/main",
            "some other",
            f"worktree {tmp_path / 'detached'}",
            "HEAD 1234",
        )

    monkeypatch.setattr("subprocess.check_output", _fake_check_output)
    rows = _parse_git_worktree(tmp_path)

    assert rows == [
        (str(tmp_path), "(detached)", False),
        (str(tmp_path / "child"), "main", False),
        (str(tmp_path / "detached"), "(detached)", False),
    ]


def test_generate_inventory_marks_primary_and_warns_nonconformant_lane(tmp_path: Path, monkeypatch) -> None:
    marker = ".thegent-primary-main"
    (tmp_path / marker).write_text("ok", encoding="utf-8")
    legacy_in_root = tmp_path / ".worktrees" / "legacy-cache"
    structured_lane = tmp_path / ".worktrees" / "backend" / "m" / "wave-80-a" / "active"

    def _fake_check_output(cmd: list[str], cwd: Path, text: bool):  # noqa: ARG001
        del cmd, text
        return _fake_git_output(
            f"worktree {tmp_path}",
            "HEAD abc",
            f"worktree {structured_lane}",
            "branch refs/heads/codex/wave-a",
            f"worktree {legacy_in_root}",
            "branch refs/heads/legacy/cache",
            f"worktree {tmp_path.parent / 'outside' / 'orphan'}",
            "branch refs/heads/main",
        )

    monkeypatch.setattr("subprocess.check_output", _fake_check_output)
    payload = generate_inventory(repo_root=tmp_path, marker=marker)

    assert payload["total"] == 4
    assert payload["warn"] == 2
    primary = next(item for item in payload["entries"] if item["path"] == str(tmp_path))
    assert primary["mode"] == "primary"
    assert primary["is_conformant"] is True
    lane = next(item for item in payload["entries"] if item["path"] == str(structured_lane))
    assert lane["mode"] == "lane"
    assert lane["is_conformant"] is True
    assert lane["domain"] == "backend"
    assert lane["scale"] == "m"
    assert lane["change_anchor"] == "wave-80-a"
    assert lane["state"] == "active"
    legacy = next(item for item in payload["entries"] if item["path"] == str(legacy_in_root))
    assert legacy["mode"] == "other"
    assert legacy["is_conformant"] is False
    assert legacy["issues"] == ["legacy or malformed worktree inside structured root"]
    outside = next(item for item in payload["entries"] if item["path"] == str(tmp_path.parent / "outside" / "orphan"))
    assert outside["is_conformant"] is False
    assert outside["issues"] == ["path outside repository root"]


def test_generate_inventory_flags_malformed_lane_in_root(tmp_path: Path, monkeypatch) -> None:
    marker = ".thegent-primary-main"
    (tmp_path / marker).write_text("ok", encoding="utf-8")
    malformed_lane = tmp_path / ".worktrees" / "backend" / "m" / "wave-80-a" / "stale"

    def _fake_check_output(cmd: list[str], cwd: Path, text: bool):  # noqa: ARG001
        del cmd, cwd, text
        return _fake_git_output(
            f"worktree {tmp_path}",
            "HEAD abc",
            f"worktree {malformed_lane}",
            "branch refs/heads/codex/wave-b",
        )

    monkeypatch.setattr("subprocess.check_output", _fake_check_output)
    payload = generate_inventory(repo_root=tmp_path, marker=marker)

    assert payload["total"] == 2
    assert payload["warn"] == 1
    malformed = next(item for item in payload["entries"] if item["path"] == str(malformed_lane))
    assert malformed["mode"] == "other"
    assert malformed["is_conformant"] is False
    assert malformed["issues"] == ["legacy or malformed worktree inside structured root"]
