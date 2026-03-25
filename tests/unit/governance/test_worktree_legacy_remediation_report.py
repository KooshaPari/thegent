"""Tests for legacy worktree remediation reporting."""

from __future__ import annotations

from pathlib import Path

from scripts.worktree_legacy_remediation_report import generate_report


def _fake_git_output(*entries: str) -> str:
    return "\n".join(entries) + "\n"


def test_generate_report_classifies_dirty_legacy_and_prunable_entries(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path
    (root / ".thegent-primary-main").write_text("ok\n", encoding="utf-8")

    def _fake_check_output(cmd: list[str], cwd: Path | None = None, text: bool = True):  # noqa: ARG001
        del cwd, text
        if cmd[:3] == ["git", "worktree", "list"]:
            return _fake_git_output(
                f"worktree {root}",
                "HEAD abc",
                f"worktree {root.parent / 'legacy-clean'}",
                "branch refs/heads/feat/clean-legacy",
                f"worktree {root.parent / 'legacy-dirty'}",
                "branch refs/heads/refactor/dirty-legacy",
                "prunable ",
                f"worktree {root.parent / 'detached'}",
                "HEAD def",
            )
        if cmd[:5] == ["git", "-C", str(root.parent / "legacy-clean"), "status", "--porcelain"]:
            return ""
        if cmd[:5] == ["git", "-C", str(root.parent / "legacy-dirty"), "status", "--porcelain"]:
            return "M file.txt\n"
        if cmd[:5] == ["git", "-C", str(root.parent / "detached"), "status", "--porcelain"]:
            return ""
        if cmd[:7] == [
            "git",
            "-C",
            str(root.parent / "legacy-clean"),
            "rev-list",
            "--count",
            "main..feat/clean-legacy",
        ]:
            return "2\n"
        if cmd[:7] == [
            "git",
            "-C",
            str(root.parent / "legacy-clean"),
            "rev-list",
            "--count",
            "feat/clean-legacy..main",
        ]:
            return "4\n"
        if cmd[:7] == [
            "git",
            "-C",
            str(root.parent / "legacy-dirty"),
            "rev-list",
            "--count",
            "main..refactor/dirty-legacy",
        ]:
            return "1\n"
        if cmd[:7] == [
            "git",
            "-C",
            str(root.parent / "legacy-dirty"),
            "rev-list",
            "--count",
            "refactor/dirty-legacy..main",
        ]:
            return "3\n"
        raise AssertionError(f"unexpected command: {cmd}")

    monkeypatch.setattr("subprocess.check_output", _fake_check_output)
    payload = generate_report(repo_root=root)

    assert payload["total"] == 3
    assert payload["dirty"] == 1
    assert payload["prunable"] == 1

    clean = next(item for item in payload["entries"] if item["path"] == str(root.parent / "legacy-clean"))
    assert clean["dirty_count"] == 0
    assert clean["ahead"] == 2
    assert clean["behind"] == 4
    assert clean["suggested_action"] == "migrate"

    dirty = next(item for item in payload["entries"] if item["path"] == str(root.parent / "legacy-dirty"))
    assert dirty["dirty_count"] == 1
    assert dirty["suggested_action"] == "migrate"

    detached = next(item for item in payload["entries"] if item["path"] == str(root.parent / "detached"))
    assert detached["suggested_action"] == "inspect"
    assert detached["ahead"] is None
    assert detached["behind"] is None
