#!/usr/bin/env python3
"""WL-124: project_commands stable import surface (extracted from cli.py monolith)."""

from __future__ import annotations

from typing import Any


def project_register_cmd(*args: Any, **kwargs: Any) -> int:
    """Register a project. Stub returning 0."""
    return 0


def project_list_cmd(*args: Any, **kwargs: Any) -> int:
    """List registered projects. Stub returning 0."""
    return 0


def project_get_cmd(*args: Any, **kwargs: Any) -> dict[str, Any]:
    """Get a project by name or ID. Stub returning empty dict."""
    return {}


__all__ = ["project_register_cmd", "project_list_cmd", "project_get_cmd"]
