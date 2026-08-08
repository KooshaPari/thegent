"""WorktreeContext dataclass — handle to an acquired worktree.

A :class:`WorktreeContext` is the opaque token returned by
:meth:`WorktreePool.acquire_worktree`.  It captures the path, branch
and owning pool needed for the agent to work in isolation and to
release the worktree back to the pool when done.

Extracted from ``thegent.mesh.git_parallelism`` as part of the WL709 L1
architecture split so that the small ``commit_all`` / ``release`` helpers
are not interleaved with the much larger :class:`WorktreePool` class.

@trace FR-MESH-006
"""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, ForwardRef

from thegent.mesh.git_parallelism.helpers import _run

if TYPE_CHECKING:
    from thegent.mesh.git_parallelism.pool import WorktreePool

#: Re-exportable forward reference so callers can resolve ``WorktreePool``
#: without importing the heavier pool module at module-load time.
WorktreePoolRef = ForwardRef("WorktreePool")

_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class WorktreeContext:
    """Snapshot of an acquired worktree.

    Attributes:
        agent_id:    Stable identifier (``mesh-<uuid>`` or supplied label).
        path:        Filesystem path of the worktree checkout.
        branch:      Git branch checked out inside the worktree
                      (``agent/<agent_id>``).
        project_root: The main repository this worktree belongs to.
        _pool_ref:   Weak reference back to the pool that issued this
                      context.  Marked ``compare=False, repr=False`` so
                      the dataclass stays hashable + repr-clean.
    """

    agent_id: str
    path: Path
    branch: str
    project_root: Path
    _pool_ref: "WorktreePool | None" = field(compare=False, repr=False, default=None)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def commit_all(self, message: str) -> str | None:
        """Stage all changes in the worktree and create a commit.

        Returns the commit hash on success, ``None`` on failure.  Failures
        are logged at ``WARNING`` level so the caller can still continue
        with the agent's work even if the commit step failed.
        """
        try:
            _run(["git", "add", "-A"], self.path)
            proc = _run(
                ["git", "commit", "--allow-empty", "-m", message],
                self.path,
                check=False,
            )
            if proc.returncode not in (0, 1):
                _log.warning("commit failed in worktree %s: %s", self.path, proc.stderr)
                return None
            result = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=str(self.path),
                text=True,
            ).strip()
            return result
        except Exception as exc:
            _log.warning("commit_all failed for agent %s: %s", self.agent_id, exc)
            return None

    def release(self) -> bool:
        """Convenience: release this worktree back to the pool that issued it.

        Returns ``False`` if the context was created without a ``_pool_ref``
        (e.g. for tests that construct a context directly).
        """
        if self._pool_ref is not None:
            return self._pool_ref.release_worktree(self.agent_id)
        return False


__all__ = ["WorktreeContext"]
