"""Low-level helpers for the worktree parallelism submodule.

Extracted from ``thegent.mesh.git_parallelism`` as part of the WL709 L1
architecture split.  Contains:

* Path / hashing helpers — :func:`_project_hash`
* Atomic file I/O — :func:`_atomic_write` and :func:`tempfile_mkstemp`
* Subprocess wrapper — :func:`_run`
* Git capability probes — :func:`_git_available`, :func:`_worktrees_supported`
* Path constants — :data:`_WORKTREE_BASE`, :data:`_STATE_FILENAME`

These are intentionally separate from the orchestration code so that
:class:`~thegent.mesh.worktree_pool.WorktreePool` and
:class:`~thegent.mesh.git_parallelism._PoolStateLock` can each be read
without scrolling through unrelated helpers.

@trace FR-MESH-006
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import tempfile
from contextlib import suppress
from pathlib import Path

from thegent.infra.shim_subprocess import run as shim_run

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

#: Default base directory under which per-project worktree pools are stored.
_WORKTREE_BASE: Path = Path.home() / ".thegent" / "worktrees"

#: Filename used for the per-pool ``state`` file mapping agent_id -> worktree path.
_STATE_FILENAME: str = "pool_state.txt"


# ---------------------------------------------------------------------------
# Path / hashing helpers
# ---------------------------------------------------------------------------


def _project_hash(project_root: Path) -> str:
    """Stable 12-character hex hash of the canonical absolute path of *project_root*.

    Two ``WorktreePool`` instances for the same project root will share the
    same pool directory because the hash is derived from the resolved
    :class:`pathlib.Path` (i.e. no symlink / relative-path ambiguity).
    """
    return hashlib.sha256(str(project_root.resolve()).encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Atomic file I/O
# ---------------------------------------------------------------------------


def tempfile_mkstemp(**kwargs: object) -> tuple[int, str]:
    """Thin wrapper around :func:`tempfile.mkstemp` exposed for test patching."""
    return tempfile.mkstemp(**kwargs)


def _atomic_write(path: Path, content: str) -> None:
    """Write *content* to *path* atomically via sibling temp + :func:`os.replace`.

    The parent directory is created if missing.  On any I/O failure after the
    temp file is created, the temp file is removed before the exception is
    re-raised so the caller does not observe a stale ``.tmp-*`` left behind.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile_mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(content)
        os.replace(tmp, path)
    except Exception:
        with suppress(OSError):
            os.unlink(tmp)
        raise


# ---------------------------------------------------------------------------
# Subprocess wrapper
# ---------------------------------------------------------------------------


def _run(cmd: list[str], cwd: Path | str, check: bool = True) -> subprocess.CompletedProcess:
    """Run *cmd* via the shim subprocess wrapper and return :class:`CompletedProcess`.

    The wrapper centralises the logic for capture-output / text mode and
    makes the call sites in :class:`WorktreePool` easier to mock in tests.
    """
    return shim_run([*cmd], cwd=str(cwd), check=check, capture_output=True, text=True)


# ---------------------------------------------------------------------------
# Git capability probes
# ---------------------------------------------------------------------------


def _git_available(path: Path | str = ".") -> bool:
    """Return True if ``git`` is on PATH and *path* is inside a git repository."""
    try:
        _run(["git", "rev-parse", "--git-dir"], path)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _worktrees_supported(path: Path | str = ".") -> bool:
    """Return True if ``git worktree`` succeeds at *path*.

    Worktrees may be unsupported in a bare repository or on filesystems
    without hard-link support; callers should fall back to the shared-tree
    mode when this returns False.
    """
    try:
        result = _run(["git", "worktree", "list"], path)
        return result.returncode == 0
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


__all__ = [
    "_WORKTREE_BASE",
    "_STATE_FILENAME",
    "_project_hash",
    "_atomic_write",
    "tempfile_mkstemp",
    "_run",
    "_git_available",
    "_worktrees_supported",
]
