"""Dead-letter queue service (WP-Y2, FR-034)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from thegent.execution import DLQManager

if TYPE_CHECKING:
    from pathlib import Path


def list_pending(session_dir: Path, limit: int = 50) -> list[dict[str, object]]:
    """List DLQ items pending review."""
    return DLQManager(session_dir).list_items(status="pending_review", run_id=None)[:limit]


def resolve(session_dir: Path, run_id: str, resolution: str) -> bool:
    """Mark DLQ item as resolved (replayed, fixed, discarded)."""
    return DLQManager(session_dir).resolve(run_id=run_id, resolution=resolution)


def is_poison_pill(session_dir: Path, run_id: str, threshold: int = 3) -> bool:
    """True if run has failed threshold+ times (poison pill)."""
    items = DLQManager(session_dir).list_items(run_id=run_id)
    if not items:
        return False
    return (items[0].get("poison_pill_count") or 0) >= threshold
