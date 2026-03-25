"""Backward compatibility wrapper for cli_git_commit_ops.

Phase 9: GIT domain extraction. This module re-exports from the git subpackage
to maintain backward compatibility with existing imports.

New code should use: from thegent.cli.commands.git.cli_git_commit_ops import ...
Legacy code can continue: from thegent.cli.commands.cli_git_commit_ops import ...

Marked for deprecation in Phase 10.
"""

from .git.cli_git_commit_ops import (
    add,
    commit,
    lock_status,
    merge,
    run_system_git,
    status,
)

__all__ = [
    "add",
    "commit",
    "lock_status",
    "merge",
    "run_system_git",
    "status",
]
