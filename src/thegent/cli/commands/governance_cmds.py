#!/usr/bin/env python3
"""WL-124: governance_cmds stable import surface (extracted from cli.py monolith)."""

from __future__ import annotations

from typing import Any


def guardrails_check_cmd(*args: Any, **kwargs: Any) -> int:
    """Run guardrails check. Stub returning 0."""
    return 0


def guardrails_show_cmd(*args: Any, **kwargs: Any) -> int:
    """Show guardrails. Stub returning 0."""
    return 0


def policy_check_cmd(*args: Any, **kwargs: Any) -> int:
    """Run policy check. Stub returning 0."""
    return 0


__all__ = [
    "guardrails_check_cmd",
    "guardrails_show_cmd",
    "policy_check_cmd",
]
