"""Request metadata helpers extracted from MCP server (WL-126)."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def default_cwd_from_context(ctx: Any) -> Path | None:
    """Resolve cwd from request metadata when available."""
    request_context = getattr(ctx, "request_context", None)
    meta = getattr(request_context, "meta", None) if request_context else None
    cwd = getattr(meta, "cwd", None) if meta else None
    if not cwd:
        return None
    return Path(str(cwd)).expanduser().resolve()


def default_owner_from_context(ctx: Any) -> str | None:
    """Resolve owner from request metadata when available."""
    request_context = getattr(ctx, "request_context", None)
    meta = getattr(request_context, "meta", None) if request_context else None
    owner = getattr(meta, "owner", None) if meta else None
    return owner if isinstance(owner, str) and owner else None


__all__ = ["default_cwd_from_context", "default_owner_from_context"]
