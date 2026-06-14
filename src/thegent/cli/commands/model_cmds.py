"""Model commands module."""

from __future__ import annotations

from typing import Any


def model_cmds_list() -> list[str]:
    """Return list of model commands."""
    return ["list", "info", "set"]


__all__ = ["model_cmds_list"]
