#!/usr/bin/env python3
"""WL-124: recovery_commands stable import surface (extracted from cli.py monolith)."""

from __future__ import annotations

from typing import Any


def recover_status_cmd(*args: Any, **kwargs: Any) -> int:
    """Return recovery status. Stub returning 0."""
    return 0


def forensics_snapshot_cmd(*args: Any, **kwargs: Any) -> int:
    """Snapshot forensics data. Stub returning 0."""
    return 0


__all__ = ["recover_status_cmd", "forensics_snapshot_cmd"]
