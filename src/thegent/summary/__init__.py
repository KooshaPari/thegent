"""STUB MODULE - thegent.summary

WARNING: This is an auto-generated stub module.
The actual implementation was moved/deleted during repository restructuring.
This stub exists for backwards compatibility with existing tests.
"""

from __future__ import annotations


class GitCommit:
    """Git commit representation."""

    def __init__(self, sha: str, message: str) -> None:
        self.sha = sha
        self.message = message


def get_git_commits(path: str, limit: int = 100) -> list[GitCommit]:
    """Get git commits for a path."""
    return []


# Stub implementation - functionality not available
__all__ = ["GitCommit", "get_git_commits"]
