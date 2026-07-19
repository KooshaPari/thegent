#!/usr/bin/env python3
"""WL-124: queue_commands stable import surface (extracted from cli.py monolith)."""

from __future__ import annotations

from typing import Any


def queue_list_cmd(*args: Any, **kwargs: Any) -> int:
    """List queued items. Stub returning 0."""
    return 0


__all__ = ["queue_list_cmd"]
