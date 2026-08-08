"""WorktreePool — pool for managing git worktrees in shared-directory parallelism.

The :class:`WorktreePool` is the orchestration entry point for
``thegent.mesh.git_parallelism``.  It owns:

* the per-project pool directory under ``_WORKTREE_BASE``;
* the flock-backed state file mapping ``agent_id -> worktree_path``;
* the acquire / release / cleanup state machine; and
* the optional AST-aware merge via :class:`thegent.mesh.smart_merger.SmartMerger`.

This is the only orchestration class in the package; helpers and data
types live in their own submodules (:mod:`.helpers`,
:mod:`.pool_state`, :mod:`.worktree_context`).  Internal-mode methods
(``_create_worktree``, ``_merge_and_remove``, ...) are kept private but
are ≤ 30 LOC each so the class reads top-to-bottom as a single narrative.

Extracted from ``thegent.mesh.git_parallelism`` as part of the WL709 L1
architecture split.

@trace FR-MESH-006, FR-MESH-007
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from contextlib import contextmanager, suppress
from pathlib import Path
from typing import TYPE_CHECKING

from thegent.mesh.git_parallelism.helpers import (
    _STATE_FILENAME,
    _WORKTREE_BASE,
    _atomic_write,
    _git_available,
    _project_hash,
    _run,
    _worktrees_supported,
)
from thegent.mesh.git_parallelism.pool_state import _PoolStateLock
from thegent.mesh.git_parallelism.worktree_context import WorktreeContext

if TYPE_CHECKING:
    from thegent.mesh.smart_merger import SmartMerger

_log = logging.getLogger(__name__)


class WorktreePool:
    """Pool for managing worktrees in shared-directory parallel execution mode.

    The pool has two operating modes:

    * **worktree mode** — when git is available and the repository supports
      worktrees, each agent gets a real ``git worktree`` on a per-agent
      branch ``agent/<agent_id>``.
    * **fallback mode** — when git is unavailable or worktrees are not
      supported, every agent shares the ``project_root`` and a small
      per-agent ``<agent_id>.fallback.lock`` file is used as a soft
      reservation marker.

    Each pool instance is scoped to a single ``project_root``; the pool
    directory is keyed by a stable 12-char hash of the resolved path so
    two pools for the same project share the same on-disk state.
    """

    def __init__(
        self,
        project_root: Path,
        target_branch: str = "HEAD",
        pool_root: Path | None = None,
        merger: "SmartMerger | None" = None,
    ) -> None:
        self.project_root = project_root.resolve()
        self.target_branch = target_branch
        self._pool_root = pool_root or _WORKTREE_BASE
        self._phash = _project_hash(self.project_root)
        self._pool_dir = self._pool_root / self._phash
        self._pool_dir.mkdir(parents=True, exist_ok=True)
        self._state_path = self._pool_dir / _STATE_FILENAME
        self._merger: "SmartMerger | None" = merger
        self._git_ok = _git_available(self.project_root)
        self._worktrees_ok = self._git_ok and _worktrees_supported(self.project_root)
        self.worktrees: list[WorktreeContext] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def acquire_worktree(self, agent_id: str) -> WorktreeContext:
        """Acquire (or reuse) a worktree context for *agent_id*."""
        with _PoolStateLock(self._state_path) as lock:
            state = lock.read()
            if agent_id in state:
                path = Path(state[agent_id])
                return WorktreeContext(
                    agent_id=agent_id,
                    path=path,
                    branch=f"agent/{agent_id}",
                    project_root=self.project_root,
                    _pool_ref=self,
                )

            ctx = self._create_worktree(agent_id) if self._worktrees_ok else self._acquire_shared_fallback(agent_id)
            state[agent_id] = str(ctx.path)
            lock.write(state)
            return ctx

    def release_worktree(self, agent_id: str) -> bool:
        """Release an acquired context and merge/remove it if necessary."""
        with _PoolStateLock(self._state_path) as lock:
            state = lock.read()
            if agent_id not in state:
                return False

            worktree_path = Path(state[agent_id])
            branch = f"agent/{agent_id}"

            if self._worktrees_ok and worktree_path != self.project_root:
                success = self._merge_and_remove(agent_id, worktree_path, branch)
            else:
                success = self._release_shared_fallback(agent_id, worktree_path)

            del state[agent_id]
            lock.write(state)
            return success

    @contextmanager
    def worktree(self, agent_id: str):
        """Context manager wrapping :meth:`acquire_worktree` + :meth:`release_worktree`."""
        ctx = self.acquire_worktree(agent_id)
        try:
            yield ctx
        finally:
            self.release_worktree(agent_id)

    def active_agents(self) -> list[str]:
        """Return the list of agent IDs currently held in the pool state."""
        with _PoolStateLock(self._state_path) as lock:
            return list(lock.read().keys())

    def cleanup_stale(self) -> int:
        """Remove stale entries whose worktree path no longer exists on disk.

        Returns the number of entries removed.  Also attempts a best-effort
        ``git worktree remove`` and ``git branch -D`` for the stale entries
        when operating in worktree mode so the repository stays tidy.
        """
        removed = 0
        with _PoolStateLock(self._state_path) as lock:
            state = lock.read()
            kept: dict[str, str] = {}
            for agent_id, path_str in state.items():
                if Path(path_str).exists():
                    kept[agent_id] = path_str
                    continue

                removed += 1
                if self._worktrees_ok:
                    self._git_worktree_remove(path_str)
                self._try_delete_branch(f"agent/{agent_id}")
            lock.write(kept)
            return removed

    # ------------------------------------------------------------------
    # Internal: worktree mode
    # ------------------------------------------------------------------

    def _create_worktree(self, agent_id: str) -> WorktreeContext:
        """Create (or recreate) a fresh ``git worktree`` for *agent_id*."""
        branch = f"agent/{agent_id}"
        worktree_path = self._pool_dir / agent_id

        if worktree_path.exists() and any(worktree_path.iterdir()):
            self._git_worktree_remove(str(worktree_path))
            shutil.rmtree(worktree_path, ignore_errors=True)

        worktree_path.mkdir(parents=True, exist_ok=True)

        if not self._branch_exists(branch):
            _run(["git", "branch", branch], self.project_root)

        _run(["git", "worktree", "add", str(worktree_path), branch], self.project_root)

        return WorktreeContext(
            agent_id=agent_id,
            path=worktree_path,
            branch=branch,
            project_root=self.project_root,
            _pool_ref=self,
        )

    def _merge_and_remove(self, agent_id: str, worktree_path: Path, branch: str) -> bool:
        """Merge *branch* into the resolved target and remove the worktree.

        Uses the configured :class:`SmartMerger` if one was supplied;
        otherwise falls back to a plain ``git merge --no-ff``.
        """
        target = self._resolve_target_branch()

        merged = False
        if self._merger is not None:
            merge_result = self._merger.merge_worktree_changes(worktree_path, target)
            merged = merge_result.success
        else:
            try:
                _run(
                    [
                        "git",
                        "merge",
                        "--no-ff",
                        "-m",
                        f"Merge agent/{agent_id} into {target}",
                        branch,
                    ],
                    self.project_root,
                )
                merged = True
            except subprocess.CalledProcessError:
                merged = False

        removed = self._git_worktree_remove(str(worktree_path))
        if worktree_path.exists():
            shutil.rmtree(worktree_path, ignore_errors=True)
        self._try_delete_branch(branch)

        return bool(merged and removed)

    def _git_worktree_remove(self, path_str: str) -> bool:
        """Best-effort ``git worktree remove --force`` for *path_str*."""
        try:
            _run(["git", "worktree", "remove", "--force", path_str], self.project_root)
            return True
        except subprocess.CalledProcessError:
            return False

    def _branch_exists(self, branch: str) -> bool:
        """Return True if the local branch *branch* exists in ``project_root``."""
        try:
            result = _run(["git", "branch", "--list", branch], self.project_root)
            return branch in result.stdout
        except subprocess.CalledProcessError:
            return False

    def _resolve_target_branch(self) -> str:
        """Resolve the configured ``target_branch`` to a concrete branch name.

        Returns the configured branch when it is not the sentinel ``"HEAD"``;
        otherwise falls back to the current branch via ``git rev-parse``,
        or ``"main"`` if git fails.
        """
        if self.target_branch != "HEAD":
            return self.target_branch
        try:
            result = _run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                self.project_root,
            )
            return result.stdout.strip() or "main"
        except subprocess.CalledProcessError:
            return "main"

    def _try_delete_branch(self, branch: str) -> None:
        """Best-effort ``git branch -D``; failures are silenced."""
        with suppress(subprocess.CalledProcessError):
            _run(["git", "branch", "-D", branch], self.project_root)

    # ------------------------------------------------------------------
    # Internal: fallback shared-tree mode
    # ------------------------------------------------------------------

    def _fallback_lock_path(self, agent_id: str) -> Path:
        """Return the per-agent fallback lock file path inside ``_pool_dir``."""
        return self._pool_dir / f"{agent_id}.fallback.lock"

    def _acquire_shared_fallback(self, agent_id: str) -> WorktreeContext:
        """Acquire a shared-tree fallback context (no real worktree)."""
        lock_path = self._fallback_lock_path(agent_id)
        _atomic_write(lock_path, f"agent={agent_id}\n")
        return WorktreeContext(
            agent_id=agent_id,
            path=self.project_root,
            branch=self._resolve_target_branch(),
            project_root=self.project_root,
            _pool_ref=self,
        )

    def _release_shared_fallback(self, agent_id: str, _worktree_path: Path) -> bool:
        """Remove the per-agent fallback lock file.  Returns True on success."""
        lock_path = self._fallback_lock_path(agent_id)
        with suppress(OSError):
            lock_path.unlink(missing_ok=True)
            return True
        return False


__all__ = ["WorktreePool"]
