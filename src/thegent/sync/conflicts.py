"""Conflict surfacing helpers for sync operations.

# @trace WL-204
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SyncConflict:
    """A single unresolved sync conflict."""

    conflict_id: str
    wl_id: str
    field: str
    local_value: str
    remote_value: str
    connector: str
    resolved: bool = False


def recommend_action(conflict: SyncConflict) -> str:
    """Return a deterministic resolution recommendation."""
    if not conflict.local_value and conflict.remote_value:
        return "adopt_remote"
    if conflict.local_value and not conflict.remote_value:
        return "keep_local"
    return "manual_review"


def unresolved_conflicts(conflicts: list[SyncConflict]) -> list[SyncConflict]:
    return [conflict for conflict in conflicts if not conflict.resolved]


def render_conflict_surface(conflicts: list[SyncConflict]) -> list[str]:
    """Render stable one-line conflict summaries for CLI output."""
    lines: list[str] = []
    for conflict in unresolved_conflicts(conflicts):
        action = recommend_action(conflict)
        lines.append(
            f"{conflict.conflict_id} wl={conflict.wl_id} connector={conflict.connector} "
            f"field={conflict.field} action={action}"
        )
    return lines
