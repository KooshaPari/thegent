"""Facade for git subpackage.

Provides unified interface to all git domain functionality:
- Command app registration
- Command re-exports
- Identity resolution
- Worktree management

Used by: thegent.cli.commands.__init__ for backward compatibility and delegation.
"""

from .cli_git import app as git_app
from .cli_git import (
    add,
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
from .cli_git_identity import resolve_git_identity
from .cli_git_worktree_governance import (
    check_worktree_isolation,
    register_worktree_isolation_hook,
    validate_worktree_state,
)

__all__ = [
    # App exports
    "git_app",
    "worktree_app",
    "lock_cleanup_app",
    # Command exports
    "add",
    "commit",
    "diff",
    "lock_status",
    "log",
    "merge",
    "run_system_git",
    "status",
    # Callback
    "callback",
    # Console
    "console",
    # Identity
    "resolve_git_identity",
    # Worktree governance
    "check_worktree_isolation",
    "register_worktree_isolation_hook",
    "validate_worktree_state",
]
