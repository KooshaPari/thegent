"""Credential source precedence validation.

# @trace WL-263
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CredentialSources:
    """Available credential sources for a connector."""

    env_token: str | None = None
    config_token_path: str | None = None
    keychain_profile: str | None = None



def resolve_credential_source(sources: CredentialSources) -> str:
    """Resolve credential source with strict ambiguity rejection.

    Precedence: env > config path > keychain profile.
    """
    enabled = []
    if sources.env_token:
        enabled.append("env")
    if sources.config_token_path:
        enabled.append("config")
    if sources.keychain_profile:
        enabled.append("keychain")

    if not enabled:
        raise ValueError("no credential source configured")
    if len(enabled) > 1:
        raise ValueError(f"ambiguous credential sources configured: {', '.join(enabled)}")

    return enabled[0]
