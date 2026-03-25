"""Git domain subpackage for thegent CLI.

Phase 9: Extract GIT domain from god package.

This package contains all git, vcs, repository, and branch-related commands:
- cli_git: main git app and command registration
- cli_git_commit_ops: commit, add, merge, status operations
- cli_git_identity: git identity and author resolution
- cli_git_log_ops: log, diff, and worktree operations
- cli_git_worktree_governance: git worktree governance and lifecycle

Main entry point: git.app (Typer application)
Facade: git.facade (unified interface for all git commands)
"""

from .cli_git import (
    app,
    callback,
    console,
    # Re-export for backwards compatibility
    add,
    commit,
    diff,
    lock_cleanup_app,
    lock_status,
    log,
    merge,
    run_system_git,
    status,
    worktree_app,
)

__all__ = [
    "app",
    "console",
    "callback",
    # Exported commands
    "add",
    "commit",
    "diff",
    "lock_status",
    "lock_cleanup_app",
    "log",
    "merge",
    "run_system_git",
    "status",
    "worktree_app",
]
