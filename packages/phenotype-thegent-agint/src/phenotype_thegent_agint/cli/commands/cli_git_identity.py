"""Compatibility wrapper for git actor identity resolution."""

from phenotype_thegent_gitops.identity import (
    _parse_profile_map,
    _build_actor_email,
    _git_config_get,
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
