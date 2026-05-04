"""Compatibility wrapper for worktree parallelism domain module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class _PoolStateLock:
    """Lock for pool state."""

    def __init__(self) -> None:
        self._locked = False

    def acquire(self) -> bool:
        if self._locked:
            return False
        self._locked = True
        return True

    def release(self) -> None:
        self._locked = False

    def __enter__(self) -> "_PoolStateLock":
        self.acquire()
        return self

    def __exit__(self, *args: Any) -> None:
        self.release()


class WorktreeContext:
    """Context for worktree operations."""

    def __init__(self) -> None:
        self.worktree_id: str = ""


class WorktreePool:
    """Pool for managing worktrees."""

    def __init__(self) -> None:
        self.worktrees: list[WorktreeContext] = []

    def add(self, context: WorktreeContext) -> None:
        self.worktrees.append(context)


def _project_hash(path: str) -> str:
    """Generate a hash for a project path."""
    import hashlib
    return hashlib.sha256(path.encode()).hexdigest()[:8]


def _atomic_write(path: str, content: str) -> None:
    """Atomically write content to a file."""
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode="w", delete=False, dir=os.path.dirname(path)) as f:
        f.write(content)
        temp_path = f.name
    os.rename(temp_path, path)


def _git_available(path: str = ".") -> bool:
    """Check if git is available in the given path."""
    import shutil
    return shutil.which("git") is not None


def _worktrees_supported(path: str = ".") -> bool:
    """Check if git worktrees are supported in the given path."""
    return _git_available(path)


def _run(cmd: list[str]) -> str:
    """Run a subprocess command and return stdout."""
    import subprocess
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return e.stdout or ""


__all__ = [
    "WorktreeContext",
    "WorktreePool",
    "_project_hash",
    "_atomic_write",
    "_git_available",
    "_worktrees_supported",
    "_PoolStateLock",
    "_run",
]
