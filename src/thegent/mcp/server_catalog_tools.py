#!/usr/bin/env python3
"""WL-126: server_catalog_tools stable import surface.

Catalog helpers for listing MCP server operations. Stub module that
satisfies the WL-126 import-surface check; the real implementation is
expected to land in a follow-up slice alongside any future MCP server
catalog work.
"""

from __future__ import annotations

from typing import Any


def thegent_list_operations_impl(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Return catalog listing. Stub returning an empty envelope."""
    return {"operations": [], "count": 0}


__all__ = ["thegent_list_operations_impl"]
