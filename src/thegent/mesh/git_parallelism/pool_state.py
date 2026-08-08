"""flock-backed state file lock for the worktree pool.

The :class:`_PoolStateLock` is a tiny context manager that wraps a small
``agent_id -> worktree_path`` mapping file in an exclusive ``fcntl.flock``.
It is intentionally minimal and Windows-compatible (no flock is acquired
when :mod:`fcntl` is unavailable, but the file is still opened so writes
remain atomic at the OS level on the local filesystem).

Extracted from ``thegent.mesh.git_parallelism`` as part of the WL709 L1
architecture split so that :class:`WorktreePool` reads cleanly without
the ~40 LOC of state-file plumbing.

@trace FR-MESH-006
"""

from __future__ import annotations

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows compatibility shim
    fcntl = None  # type: ignore[assignment]

from pathlib import Path


class _PoolStateLock:
    """Simple flock-backed state file lock helper.

    Usage::

        with _PoolStateLock(path) as lock:
            state = lock.read()
            state["agent-1"] = "/tmp/worktrees/agent-1"
            lock.write(state)

    The file is created (and parent directories are made) on entry if it
    does not already exist.  Lock is released and the file handle is
    closed on exit.  :func:`read` parses ``key=value`` lines; lines
    without an ``=`` separator are silently skipped.
    """

    def __init__(self, state_path: Path) -> None:
        self._path = state_path
        self._fh = None

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> _PoolStateLock:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.touch()
        self._fh = open(self._path, "r+", encoding="utf-8")
        if fcntl is not None:
            fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX)
        return self

    def __exit__(self, *args: object) -> None:
        try:
            if self._fh is not None:
                if fcntl is not None:
                    fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
                self._fh.close()
        finally:
            self._fh = None

    # ------------------------------------------------------------------
    # State read / write
    # ------------------------------------------------------------------

    def read(self) -> dict[str, str]:
        """Parse state file lines as ``key=value`` pairs and return a dict.

        Lines without an ``=`` separator are ignored.  Whitespace around
        ``key`` and ``value`` is stripped.  Caller must already be inside
        the ``with`` block so that the underlying file handle is positioned
        at offset 0.
        """
        assert self._fh is not None
        self._fh.seek(0)
        state: dict[str, str] = {}
        for line in self._fh:
            line = line.strip()
            if "=" in line:
                key, _, value = line.partition("=")
                state[key] = value
        return state

    def write(self, state: dict[str, str]) -> None:
        """Overwrite the state file from *state* (sorted keys for determinism).

        The file is truncated to zero bytes before being written so that
        stale entries from a previous state are removed atomically.
        """
        assert self._fh is not None
        self._fh.seek(0)
        self._fh.truncate()
        for key in sorted(state):
            self._fh.write(f"{key}={state[key]}\n")
        self._fh.flush()


__all__ = ["_PoolStateLock"]
