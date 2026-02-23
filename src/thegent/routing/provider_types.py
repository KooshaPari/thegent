"""Execution path compatibility helpers."""

from __future__ import annotations

from enum import Enum


class ExecutionPath(str, Enum):
    DIRECT = "direct"
    CLIPROXY = "cliproxy"


def normalize_provider_name(value: str | None) -> str:
    """Return a normalized provider key used by routing/model catalog."""
    return (value or "").strip().lower().replace("_", "-")


def get_execution_path(value: str | None) -> ExecutionPath:
    normalized = normalize_provider_name(value)
    if normalized == ExecutionPath.CLIPROXY.value:
        return ExecutionPath.CLIPROXY
    return ExecutionPath.DIRECT
