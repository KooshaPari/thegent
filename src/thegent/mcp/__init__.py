"""STUB MODULE - thegent.mcp

WARNING: This is an auto-generated stub module.
The actual implementation was moved/deleted during repository restructuring.
This stub exists for backwards compatibility with existing tests.
"""

from __future__ import annotations
from typing import Any


def server_cache_elicitation_response(data: dict[str, Any]) -> dict[str, Any]:
    """Server cache elicitation response stub."""
    return {"cached": True}


def server_create_elicitation_cache(cache_id: str) -> dict[str, Any]:
    """Create an elicitation cache."""
    return {"cache_id": cache_id, "created": True}


def server_default_cwd_from_context() -> str:
    """Get the default working directory from context."""
    return ""


def server_default_owner_from_context() -> str:
    """Get the default owner from context."""
    return ""


def server_elicitation_cache_key(elicitation_id: str) -> str:
    """Generate cache key for elicitation."""
    return f"elicitation:{elicitation_id}"


def server_get_cached_elicitation(elicitation_id: str) -> dict[str, Any] | None:
    """Get cached elicitation data by ID."""
    return None


def server_tools_workstream_lsp() -> dict[str, Any]:
    """Server tools workstream LSP."""
    return {}


def server_resolve_cwd_elicitation(cwd: str | None = None) -> str:
    """Resolve the working directory for elicitation."""
    return cwd or ""


def hotreload(enabled: bool = True) -> None:
    """Enable or disable hotreload."""
    pass


__all__ = [
    "server_cache_elicitation_response",
    "server_create_elicitation_cache",
    "server_default_cwd_from_context",
    "server_default_owner_from_context",
    "server_elicitation_cache_key",
    "_server_tools_workstream_lsp",
    "server_resolve_cwd_elicitation",
    "server_resolve_owner_elicitation",
    "hotreload",
]


def server_resolve_owner_elicitation(owner: str | None = None) -> str:
    """Resolve the owner for elicitation."""
    return owner or ""
