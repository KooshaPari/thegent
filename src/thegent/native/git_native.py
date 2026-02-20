"""BKM-06: Thin Python wrapper for thegent-git native binary.

Provides HEAD, status, and diff-stat git metadata without spawning the git
CLI.  Two execution strategies (tried in order):

1. ``thegent-git`` binary (Rust, gitoxide/git2 backend) — zero-process-spawn.
2. ``git`` subprocess fallback — always available on any developer machine.

The fallback is intentionally kept as a standalone, fully functional path so
the module works even when the Rust binary has not been compiled.

FR-GIT-001  @trace FR-GIT-001
"""

from __future__ import annotations

import contextlib
import json
import logging
import shutil
import subprocess
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

_log = logging.getLogger(__name__)

_BINARY_NAME = "thegent-git"


def _find_binary() -> str | None:
    """Return the absolute path to the thegent-git binary, or None."""
    return shutil.which(_BINARY_NAME)


def _run_binary(subcommand: str, repo_path: str) -> dict[str, Any] | None:
    """Run thegent-git <subcommand> and return parsed JSON, or None on error."""
    binary = _find_binary()
    if binary is None:
        return None
    try:
        result = subprocess.run(
            [binary, "-C", repo_path, subcommand],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            _log.debug(
                "thegent-git %s exited %d: %s",
                subcommand,
                result.returncode,
                result.stderr.strip(),
            )
            return None
        return json.loads(result.stdout.strip())
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as exc:
        _log.debug("thegent-git %s failed: %s", subcommand, exc)
        return None


# ---------------------------------------------------------------------------
# Fallback helpers (pure git subprocess)
# ---------------------------------------------------------------------------


def _git_head_fallback(repo_path: str) -> dict[str, Any]:
    """Return HEAD sha and branch via git subprocess."""
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except subprocess.CalledProcessError:
        sha = ""

    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_path,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except subprocess.CalledProcessError:
        branch = "HEAD"

    return {"sha": sha, "branch": branch}


def _git_status_fallback(repo_path: str) -> dict[str, Any]:
    """Return status (modified, untracked, staged) via git subprocess."""
    try:
        raw = subprocess.check_output(
            ["git", "status", "--porcelain=v1"],
            cwd=repo_path,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return {"modified": [], "untracked": [], "staged": []}

    modified: list[str] = []
    untracked: list[str] = []
    staged: list[str] = []

    for line in raw.splitlines():
        if len(line) < 3:
            continue
        index_flag = line[0]   # staged status
        wt_flag = line[1]      # worktree status
        path = line[3:].strip()

        if index_flag not in (" ", "?") and index_flag != "!":
            staged.append(path)
        if wt_flag in {"M", "D", "T"}:
            modified.append(path)
        if index_flag == "?" and wt_flag == "?":
            untracked.append(path)

    return {"modified": modified, "untracked": untracked, "staged": staged}


def _git_diff_stat_fallback(repo_path: str) -> dict[str, Any]:
    """Return diff stats vs HEAD via git subprocess."""
    try:
        raw = subprocess.check_output(
            ["git", "diff", "--stat", "HEAD"],
            cwd=repo_path,
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return {"files_changed": 0, "insertions": 0, "deletions": 0}

    # Parse the summary line: "N files changed, N insertions(+), N deletions(-)"
    files_changed = 0
    insertions = 0
    deletions = 0

    for line in raw.splitlines():
        line = line.strip()
        if "changed" in line:
            parts = line.split(",")
            for part in parts:
                part = part.strip()
                if "changed" in part:
                    with contextlib.suppress(ValueError, IndexError):
                        files_changed = int(part.split()[0])
                elif "insertion" in part:
                    with contextlib.suppress(ValueError, IndexError):
                        insertions = int(part.split()[0])
                elif "deletion" in part:
                    with contextlib.suppress(ValueError, IndexError):
                        deletions = int(part.split()[0])

    return {
        "files_changed": files_changed,
        "insertions": insertions,
        "deletions": deletions,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


class GitNative:
    """Native git metadata provider.

    Tries the ``thegent-git`` binary first; falls back to ``git`` subprocess.

    Args:
        repo_path: Path to the git repository (or any directory within it).
    """

    def __init__(self, repo_path: str | Path = ".") -> None:
        self.repo_path = str(repo_path)

    def head(self) -> dict[str, Any]:
        """Return HEAD commit SHA and branch name.

        Returns:
            ``{"sha": "<40-char-hex>", "branch": "<name>"}``
        """
        result = _run_binary("head", self.repo_path)
        if result is not None:
            _log.debug("GitNative.head via binary: %s", result)
            return result
        _log.debug("GitNative.head falling back to git subprocess")
        return _git_head_fallback(self.repo_path)

    def status(self) -> dict[str, Any]:
        """Return working-tree status.

        Returns:
            ``{"modified": [...], "untracked": [...], "staged": [...]}``
        """
        result = _run_binary("status", self.repo_path)
        if result is not None:
            _log.debug("GitNative.status via binary: %s", result)
            return result
        _log.debug("GitNative.status falling back to git subprocess")
        return _git_status_fallback(self.repo_path)

    def diff_stat(self) -> dict[str, Any]:
        """Return diff stats comparing HEAD to current worktree + index.

        Returns:
            ``{"files_changed": N, "insertions": N, "deletions": N}``
        """
        result = _run_binary("diff-stat", self.repo_path)
        if result is not None:
            _log.debug("GitNative.diff_stat via binary: %s", result)
            return result
        _log.debug("GitNative.diff_stat falling back to git subprocess")
        return _git_diff_stat_fallback(self.repo_path)
