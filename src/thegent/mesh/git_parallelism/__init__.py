"""Worktree parallelism submodule (WL709 L1 architecture split).

The public surface of the legacy ``thegent.mesh.git_parallelism`` module
is preserved at this package level.  The implementation is split into:

* :mod:`.helpers` — path hashing, atomic write, subprocess wrapper, git
  capability probes, path constants.
* :mod:`.pool_state` — :class:`_PoolStateLock` (flock-backed state file).
* :mod:`.worktree_context` — :class:`WorktreeContext` dataclass.
* :mod:`.pool` — :class:`WorktreePool` orchestrator.

Each submodule is independently importable; the legacy flat module
``thegent.mesh.git_parallelism`` is preserved as a thin re-export shim.

@trace FR-MESH-006, FR-MESH-007
"""

from __future__ import annotations

from thegent.mesh.git_parallelism.helpers import (
    _STATE_FILENAME,
    _WORKTREE_BASE,
    _atomic_write,
    _git_available,
    _project_hash,
    _run,
    _worktrees_supported,
    tempfile_mkstemp,
)
from thegent.mesh.git_parallelism.pool import WorktreePool
from thegent.mesh.git_parallelism.pool_state import _PoolStateLock
from thegent.mesh.git_parallelism.worktree_context import WorktreeContext

__all__ = [
    # Public classes
    "WorktreeContext",
    "WorktreePool",
    # Private helpers (re-exported because tests patch them at this path)
    "_PoolStateLock",
    "_project_hash",
    "_atomic_write",
    "tempfile_mkstemp",
    "_run",
    "_git_available",
    "_worktrees_supported",
    "_WORKTREE_BASE",
    "_STATE_FILENAME",
]
