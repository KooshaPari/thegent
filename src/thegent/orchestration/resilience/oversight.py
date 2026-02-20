"""Controlled oversight for repeated failures (WP-2008, FR-009)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def should_trigger_oversight(session_dir: Path, target: str, failure_count: int, threshold: int = 3) -> bool:
    """True if repeated failures exceed threshold and oversight should trigger."""
    return failure_count >= threshold


def get_oversight_action(failure_count: int) -> str:
    """Return recommended oversight action: Union[pause, escalate] | continue."""
    if failure_count >= 5:
        return "escalate"
    if failure_count >= 3:
        return "pause"
    return "continue"
