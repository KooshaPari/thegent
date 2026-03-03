"""Compatibility wrapper for worktree parallelism domain module."""

from thegent_gitops.worktree import (
    WorktreeContext,
    WorktreePool,
    _atomic_write,
    _git_available,
    _PoolStateLock,
    _project_hash,
    _run,
    _worktrees_supported,
)

__all__ = [
    "WorktreeContext",
    "WorktreePool",
    "_PoolStateLock",
    "_atomic_write",
    "_git_available",
    "_project_hash",
    "_run",
    "_worktrees_supported",
]
