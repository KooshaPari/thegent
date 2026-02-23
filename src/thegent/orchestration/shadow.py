"""Shadow workspace management via git worktree isolation (MTSP-12).

Provides isolated workspaces for agent runs using git worktrees.
When enabled, agents operate in a separate worktree to avoid conflicts
with the main working directory.

IMPORTANT: Uses git worktrees, NOT file copying.
- Worktrees share the same .git objects (no disk duplication)
- Each shadow is just a pointer + working files
- ~100x more efficient than copying entire repo
"""

from __future__ import annotations

import atexit
import logging
import shutil
import subprocess
from thegent.infra.shim_subprocess import run as shim_run
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)

# Track all created shadows for cleanup on exit
_active_shadows: set[str] = set()


def _cleanup_orphaned_shadows(repo_root: Path) -> int:
    """Clean up orphaned shadow directories that aren't active worktrees.

    Returns number of directories cleaned.
    """
    cleaned = 0

    # Get list of active worktrees
    result = shim_run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=10,
    )

    active_paths = set()
    for line in result.stdout.split("\n"):
        if line.startswith("worktree "):
            active_paths.add(Path(line[9:]))

    # Find orphaned .shadow-* directories
    for item in repo_root.iterdir():
        if item.is_dir() and item.name.startswith(".shadow-"):
            if item not in active_paths:
                # Orphaned - remove it
                try:
                    shutil.rmtree(item, ignore_errors=True)
                    _log.info("Cleaned orphaned shadow: %s", item.name)
                    cleaned += 1
                except OSError as e:
                    _log.warning("Failed to clean %s: %s", item, e)

    return cleaned


def register_shadow_cleanup() -> None:
    """Register atexit handler for shadow cleanup."""
    atexit.register(_cleanup_all_shadows)


def _cleanup_all_shadows() -> None:
    """Cleanup all shadows tracked by this process."""
    for _ in list(_active_shadows):
        # Individual shadows handle their own cleanup via context manager.
        pass


# Register cleanup on module import
register_shadow_cleanup()


class ShadowWorkspace:
    """Manages a git worktree-based shadow workspace for isolated agent execution."""

    def __init__(self, original_cwd: Path | str, run_id: str) -> None:
        """Initialize shadow workspace manager.

        Args:
            original_cwd: The original working directory
            run_id: Unique identifier for this run (used for worktree name)
        """
        self.original_cwd = Path(original_cwd).resolve()
        self.run_id = run_id
        self.shadow_root: Path | None = None
        self._worktree_name = f".shadow-{run_id[:8]}"
        self._created = False

    def create(self) -> bool:
        """Create the shadow workspace as a git worktree.

        Returns:
            True if workspace was created successfully, False otherwise
        """
        try:
            # Check if we're in a git repo
            result = shim_run(  # noqa: PLW1510 -- returncode checked manually
                ["git", "rev-parse", "--git-dir"],
                cwd=self.original_cwd,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                _log.debug("Not in a git repo; shadow workspace disabled")
                return False

            # Create shadow directory
            shadow_dir = self.original_cwd / self._worktree_name

            # Create worktree
            result = shim_run(  # noqa: PLW1510 -- returncode checked manually
                ["git", "worktree", "add", "--detach", str(shadow_dir), "HEAD"],
                cwd=self.original_cwd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                self.shadow_root = shadow_dir
                self._created = True
                _active_shadows.add(self.run_id)
                _log.info("Created shadow workspace at %s", shadow_dir)
                return True

            _log.warning("Failed to create worktree: %s", result.stderr)
            return False

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            _log.warning("Shadow workspace creation failed: %s", e)
            return False

    def get_env(self) -> dict[str, str]:
        """Get environment variables for the shadow workspace.

        Returns:
            Dict with SHADOW_WORKSPACE and other relevant env vars
        """
        if not self.shadow_root:
            return {}

        return {
            "SHADOW_WORKSPACE": str(self.shadow_root),
            "SHADOW_RUN_ID": self.run_id,
            "GIT_WORK_TREE": str(self.shadow_root),
        }

    def merge_back(self) -> bool:
        """Merge changes from shadow workspace back to main.

        Returns:
            True if merge was successful, False otherwise
        """
        if not self._created or not self.shadow_root:
            return False

        try:
            # Stage all changes in shadow
            shim_run(  # noqa: PLW1510 -- returncode checked manually
                ["git", "add", "-A"],
                cwd=self.shadow_root,
                capture_output=True,
                timeout=30,
            )

            # Commit if there are changes
            result = shim_run(  # noqa: PLW1510 -- returncode checked manually
                ["git", "diff", "--cached", "--quiet"],
                cwd=self.shadow_root,
                capture_output=True,
                timeout=10,
            )

            if result.returncode != 0:
                # There are staged changes, commit them
                shim_run(  # noqa: PLW1510 -- returncode checked manually
                    ["git", "commit", "-m", f"Shadow workspace changes for {self.run_id}"],
                    cwd=self.shadow_root,
                    capture_output=True,
                    timeout=30,
                )

            _log.info("Merged shadow workspace changes")
            return True

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            _log.warning("Shadow merge failed: %s", e)
            return False

    def destroy(self) -> None:
        """Remove the shadow workspace and clean up."""
        if not self._created:
            return

        try:
            if self.shadow_root and self.shadow_root.exists():
                # Remove worktree
                shim_run(  # noqa: PLW1510 -- returncode checked manually
                    ["git", "worktree", "remove", "--force", str(self.shadow_root)],
                    cwd=self.original_cwd,
                    capture_output=True,
                    timeout=30,
                )

                # Fallback: manual cleanup if worktree command fails
                if self.shadow_root.exists():
                    shutil.rmtree(self.shadow_root, ignore_errors=True)

            self._created = False
            self.shadow_root = None
            _active_shadows.discard(self.run_id)
            _log.debug("Destroyed shadow workspace")

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            _log.warning("Shadow cleanup failed: %s", e)

    def __enter__(self) -> ShadowWorkspace:
        """Context manager entry."""
        self.create()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - cleanup workspace."""
        self.destroy()


def get_shadow_stats(repo_root: Path) -> dict[str, Any]:
    """Get statistics about shadow workspaces.

    Returns dict with:
        - active_worktrees: number of active git worktrees
        - orphaned_dirs: number of .shadow-* dirs not tracked by git
        - disk_usage_bytes: total disk usage of shadow dirs
        - worktrees: list of active worktree paths
    """
    repo_root = Path(repo_root).resolve()

    stats = {
        "active_worktrees": 0,
        "orphaned_dirs": 0,
        "disk_usage_bytes": 0,
        "worktrees": [],
        "orphaned_paths": [],
    }

    # Get active worktrees
    result = shim_run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=10,
    )

    active_paths = set()
    for line in result.stdout.split("\n"):
        if line.startswith("worktree "):
            path = Path(line[9:])
            active_paths.add(path)
            stats["worktrees"].append(str(path))

    stats["active_worktrees"] = len(active_paths)

    # Find orphaned shadow directories
    for item in repo_root.iterdir():
        if item.is_dir() and item.name.startswith(".shadow-"):
            # Calculate disk usage
            try:
                total_size = sum(f.stat().st_size for f in item.rglob("*") if f.is_file())
                stats["disk_usage_bytes"] += total_size
            except OSError:
                pass

            if item not in active_paths:
                stats["orphaned_dirs"] += 1
                stats["orphaned_paths"].append(str(item))

    return stats


def cleanup_shadows(repo_root: Path) -> dict[str, Any]:
    """Clean up orphaned shadow directories.

    Returns dict with cleanup results.
    """
    repo_root = Path(repo_root).resolve()
    cleaned = _cleanup_orphaned_shadows(repo_root)

    return {
        "cleaned_count": cleaned,
        "message": f"Cleaned {cleaned} orphaned shadow directories",
    }


__all__ = [
    "ShadowWorkspace",
    "_cleanup_orphaned_shadows",
    "cleanup_shadows",
    "get_shadow_stats",
]
