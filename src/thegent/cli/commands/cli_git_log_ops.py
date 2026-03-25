"""Backward compatibility wrapper for cli_git_log_ops.

Phase 9: GIT domain extraction. This module re-exports from the git subpackage
to maintain backward compatibility with existing imports.

New code should use: from thegent.cli.commands.git.cli_git_log_ops import ...
Legacy code can continue: from thegent.cli.commands.cli_git_log_ops import ...

Marked for deprecation in Phase 10.
"""

from .git.cli_git_log_ops import (
    diff,
    lock_cleanup_app,
    log,
    register_lock_cleanup_commands,
    register_worktree_commands,
    worktree_app,
)

__all__ = [
    "diff",
    "lock_cleanup_app",
    "log",
    "register_lock_cleanup_commands",
    "register_worktree_commands",
    "worktree_app",
]
