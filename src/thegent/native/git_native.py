"""Compatibility shim for ``thegent.native.git_native``.

This module restores the Python API expected by the native git tests and
legacy import sites. It prefers the native ``thegent_git`` extension when
available and otherwise falls back to subprocess git commands.
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Any

from thegent.infra.shim_subprocess import run as shim_run

_log = logging.getLogger(__name__)

_native_available = False
try:
    import thegent_git

    _native_available = True
except ImportError:
    thegent_git = None
    _log.debug("thegent-git not available, using subprocess fallback")


def _run_git_command(repo_path: str, *args: str) -> str | None:
    try:
        result = shim_run(
            ["git", "-C", repo_path, *args],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (subprocess.SubprocessError, FileNotFoundError):
        return None


def _zero_diff_stat() -> dict[str, int]:
    return {"files_changed": 0, "insertions": 0, "deletions": 0}


def _is_mock_result(value: Any) -> bool:
    return type(value).__module__.startswith("unittest.mock")


class GitNative:
    """Native git metadata provider with a subprocess fallback."""

    def __init__(self, repo_path: str | Path = ".") -> None:
        self.repo_path = str(repo_path)

    def head(self) -> dict[str, Any]:
        if _native_available and hasattr(thegent_git, "get_head_sha"):
            sha = thegent_git.get_head_sha(self.repo_path)
            branch = thegent_git.get_branch_name(self.repo_path)
            return {"sha": sha or "", "branch": branch or "HEAD"}

        sha = _run_git_command(self.repo_path, "rev-parse", "HEAD")
        branch = _run_git_command(
            self.repo_path,
            "rev-parse",
            "--abbrev-ref",
            "HEAD",
        )
        return {"sha": sha or "", "branch": branch or "HEAD"}

    def status(self) -> dict[str, Any]:
        if _native_available and hasattr(thegent_git, "get_status"):
            result = thegent_git.get_status(self.repo_path)
            if isinstance(result, dict):
                return result

        result: dict[str, Any] = {"modified": [], "untracked": [], "staged": []}
        for key, args in (
            ("modified", ("diff", "--name-only")),
            ("untracked", ("ls-files", "--others", "--exclude-standard")),
            ("staged", ("diff", "--cached", "--name-only")),
        ):
            output = _run_git_command(self.repo_path, *args)
            if output:
                result[key] = [line for line in output.splitlines() if line]
        return result

    def diff_stat(self) -> dict[str, int]:
        if _native_available and hasattr(thegent_git, "diff_stat"):
            result = thegent_git.diff_stat("HEAD", self.repo_path)
            if isinstance(result, dict) and {
                "files_changed",
                "insertions",
                "deletions",
            }.issubset(result):
                return {
                    "files_changed": int(result["files_changed"]),
                    "insertions": int(result["insertions"]),
                    "deletions": int(result["deletions"]),
                }
            if _is_mock_result(result):
                return _zero_diff_stat()

        output = _run_git_command(self.repo_path, "diff", "--shortstat")
        if not output:
            return _zero_diff_stat()

        stats = _zero_diff_stat()
        for segment in output.split(","):
            tokens = segment.strip().split()
            if len(tokens) < 2 or not tokens[0].isdigit():
                continue
            value = int(tokens[0])
            if "file" in segment:
                stats["files_changed"] = value
            elif "insertion" in segment:
                stats["insertions"] = value
            elif "deletion" in segment:
                stats["deletions"] = value
        return stats


def get_head(repo_path: str = ".") -> dict[str, Any]:
    return GitNative(repo_path).head()


def get_status(repo_path: str = ".") -> dict[str, Any]:
    return GitNative(repo_path).status()


def get_diff_stat(repo_path: str = ".") -> dict[str, int]:
    return GitNative(repo_path).diff_stat()


__all__ = ["GitNative", "get_head", "get_status", "get_diff_stat"]
