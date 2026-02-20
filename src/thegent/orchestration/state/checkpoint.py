"""Checkpoint/rollback service ops (WP-2001, FR-006)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from thegent.execution import CheckpointRegistry

if TYPE_CHECKING:
    from pathlib import Path


def create(session_dir: Path, reason: str, dag_content: str, owner: str) -> dict[str, object]:
    """Create a checkpoint."""
    ckpt = CheckpointRegistry(session_dir).create_checkpoint(reason=reason, dag_content=dag_content, owner=owner)
    return ckpt.model_dump()


def list_checkpoints(session_dir: Path, limit: int = 20) -> list[dict[str, object]]:
    """List recent checkpoints."""
    return CheckpointRegistry(session_dir).list_checkpoints(limit=limit)


def get(session_dir: Path, checkpoint_id: str) -> dict[str, object | None]:
    """Retrieve a checkpoint by ID."""
    return CheckpointRegistry(session_dir).get_checkpoint(checkpoint_id)
