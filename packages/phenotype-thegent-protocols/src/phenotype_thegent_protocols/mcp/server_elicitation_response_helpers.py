"""Elicitation response interpretation helpers extracted from MCP server (WL-126)."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def resolve_cwd_elicitation(
    response: Any,
    *,
    accepted_elicitation_type: type,
    declined_elicitation_type: type,
    cancelled_elicitation_type: type,
) -> tuple[Path | None, str | None]:
    """Resolve cwd path and status from an elicitation response object."""
    if isinstance(response, accepted_elicitation_type):
        return Path(str(response.data)).expanduser().resolve(), None
    if isinstance(response, declined_elicitation_type):
        return None, "declined"
    if isinstance(response, cancelled_elicitation_type):
        return None, "cancelled"
    return None, "ambiguous"


def resolve_owner_elicitation(
    response: Any,
    *,
    default_owner_tag: str,
    accepted_elicitation_type: type,
    declined_elicitation_type: type,
    cancelled_elicitation_type: type,
) -> tuple[str | None, str | None]:
    """Resolve owner tag and status from an elicitation response object."""
    if isinstance(response, accepted_elicitation_type):
        return str(response.data), None
    if isinstance(response, declined_elicitation_type):
        return default_owner_tag, None
    if isinstance(response, cancelled_elicitation_type):
        return None, "cancelled"
    return default_owner_tag, None


__all__ = ["resolve_cwd_elicitation", "resolve_owner_elicitation"]
