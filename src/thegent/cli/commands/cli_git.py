"""Backward compatibility wrapper for git subpackage.

Phase 9: GIT domain extraction. This module re-exports the git subpackage
to maintain backward compatibility with existing imports.

New code should use: from thegent.cli.commands.git import ...
Legacy code can continue: from thegent.cli.commands.cli_git import ...

Marked for deprecation in Phase 10.
"""

# Re-export everything from the git subpackage
from .git import (
    add,
    app,
    callback,
    commit,
    console,
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
