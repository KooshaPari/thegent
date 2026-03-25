"""Compatibility wrapper for git actor identity resolution."""

from __future__ import annotations

from pathlib import Path

import thegent_gitops.identity as _identity

_parse_profile_map = _identity._parse_profile_map
_build_actor_email = _identity._build_actor_email
_git_config_get = _identity._git_config_get
infer_actor_profile = _identity.infer_actor_profile
normalize_actor_profile = _identity.normalize_actor_profile


def resolve_author_env(
    *,
    project_root: Path,
    actor_profile: str | None,
    agent_id: str,
) -> dict[str, str]:
    """Resolve git identity env through the compatibility wrapper namespace."""
    _identity._git_config_get = _git_config_get
    return _identity.resolve_author_env(
        project_root=project_root,
        actor_profile=actor_profile,
        agent_id=agent_id,
    )


__all__ = [
    "_parse_profile_map",
    "_build_actor_email",
    "_git_config_get",
    "infer_actor_profile",
    "normalize_actor_profile",
    "resolve_author_env",
]
