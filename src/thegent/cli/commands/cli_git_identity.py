"""Backward compatibility wrapper for cli_git_identity.

Phase 9: GIT domain extraction. This module re-exports from the git subpackage
to maintain backward compatibility with existing imports.

New code should use: from thegent.cli.commands.git.cli_git_identity import ...
Legacy code can continue: from thegent.cli.commands.cli_git_identity import ...

Marked for deprecation in Phase 10.
"""

from .git.cli_git_identity import (
    _build_actor_email,
    _git_config_get,
    _parse_profile_map,
    infer_actor_profile,
    normalize_actor_profile,
    resolve_author_env,
)

__all__ = [
    "_parse_profile_map",
    "_build_actor_email",
    "_git_config_get",
    "infer_actor_profile",
    "normalize_actor_profile",
    "resolve_author_env",
]
