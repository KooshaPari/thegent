"""Backward compatibility wrapper for cli_git_worktree_governance.

Phase 9: GIT domain extraction. This module re-exports from the git subpackage
to maintain backward compatibility with existing imports.

New code should use: from thegent.cli.commands.git.cli_git_worktree_governance import ...
Legacy code can continue: from thegent.cli.commands.cli_git_worktree_governance import ...

Marked for deprecation in Phase 10.
"""

from .git.cli_git_worktree_governance import (
    check_worktree_isolation,
    register_worktree_governance_commands,
    register_worktree_isolation_hook,
    validate_worktree_state,
)

__all__ = [
    "check_worktree_isolation",
    "register_worktree_governance_commands",
    "register_worktree_isolation_hook",
    "validate_worktree_state",
]
