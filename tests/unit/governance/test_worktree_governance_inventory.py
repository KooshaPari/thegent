"""Tests for worktree inventory generation and conformance checks."""

from __future__ import annotations

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
        (str(tmp_path), "(detached)"),
        (str(tmp_path / "child"), "main"),
        (str(tmp_path / "detached"), "(detached)"),
    ]


def test_generate_inventory_marks_primary_and_warns_nonconformant_lane(tmp_path: Path, monkeypatch) -> None:
    marker = ".thegent-primary-main"
    (tmp_path / marker).write_text("ok", encoding="utf-8")

    def _fake_check_output(cmd: list[str], cwd: Path, text: bool):  # noqa: ARG001
        del cmd, text
        return _fake_git_output(
                f"worktree {tmp_path}",
                "HEAD abc",
                f"worktree {tmp_path / 'thegent-worktree-wave80-a'}",
                "branch refs/heads/codex/wave-a",
                f"worktree {tmp_path.parent / 'outside' / 'orphan'}",
                "branch refs/heads/main",
            )

    monkeypatch.setattr("subprocess.check_output", _fake_check_output)
    payload = generate_inventory(repo_root=tmp_path, marker=marker)

    assert payload["total"] == 3
    assert payload["warn"] == 1
    primary = next(item for item in payload["entries"] if item["path"] == str(tmp_path))
    assert primary["mode"] == "primary"
    assert primary["is_conformant"] is True
    lane = next(item for item in payload["entries"] if item["mode"] == "lane")
    assert lane["is_conformant"] is True
    outside = next(item for item in payload["entries"] if item["path"] == str(tmp_path.parent / "outside" / "orphan"))
    assert outside["is_conformant"] is False
    assert outside["issues"] == ["path outside repository root"]
