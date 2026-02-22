"""BKM-06: Git operations using native Rust (thegent-git).

Provides HEAD, status, and diff-stat git metadata using the thegent-git
PyO3 extension. Requires thegent-git to be installed.

FR-GIT-001  @trace FR-GIT-001
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

_log = logging.getLogger(__name__)

# Native Rust extension (required)
try:
    import thegent_git
except ImportError:
    raise ImportError("thegent-git not available - install with: pip install thegent-git")


class GitNative:
    """Native git metadata provider using Rust."""

    def __init__(self, repo_path: str | Path = ".") -> None:
        self.repo_path = str(repo_path)

    def head(self) -> dict[str, Any]:
        """Return HEAD commit SHA and branch name.

        Returns:
            ``{"sha": "<40-char-hex>", "branch": "<name>"}``
        """
        sha = thegent_git.get_head_sha(self.repo_path)
        branch = thegent_git.get_branch_name(self.repo_path)
        return {"sha": sha or "", "branch": branch or "HEAD"}

    def status(self) -> dict[str, Any]:
        """Return working-tree status.

        Returns:
            ``{"modified": [...], "untracked": [...], "staged": [...]}``
        """
        return thegent_git.get_status(self.repo_path)

    def diff_stat(self) -> dict[str, Any]:
        """Return diff stats comparing HEAD to current worktree + index.

        Returns:
            ``{"files_changed": N, "insertions": N, "deletions": N}``
        """
        # TODO: Add diff_stat to thegent-git crate
        _log.warning("diff_stat not implemented in thegent-git yet")
        return {"files_changed": 0, "insertions": 0, "deletions": 0}
