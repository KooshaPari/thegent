"""Rolling checkpoint resume for long-running synchronization cycles.

Enables safe resumption of long sync cycles through persisted rolling checkpoints
that track progress through large workstream ranges.

FR traceability: WL-284 (Rolling Checkpoint Resume)
"""

from __future__ import annotations

import orjson as json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Checkpoint:
    """Represents a saved checkpoint in a synchronization cycle."""

    checkpoint_id: str
    cycle_id: str
    last_processed_idx: int
    total_items: int
    created_at: datetime


class CheckpointStore:
    """Manages persistence and retrieval of checkpoints."""

    @staticmethod
    def save(checkpoint: Checkpoint, store_dir: Path) -> Path:
        """Save a checkpoint to the store.

        Args:
            checkpoint: The checkpoint to save.
            store_dir: Directory to save the checkpoint file.

        Returns:
            Path to the saved checkpoint file.
        """
        store_dir.mkdir(parents=True, exist_ok=True)

        # Convert checkpoint to dict, handling datetime serialization
        checkpoint_dict = asdict(checkpoint)
        checkpoint_dict["created_at"] = checkpoint.created_at.isoformat()

        checkpoint_path = store_dir / f"{checkpoint.checkpoint_id}.json"
        with open(checkpoint_path, "w") as f:
            json.dump(checkpoint_dict, f, indent=2)

        logger.debug(f"Saved checkpoint {checkpoint.checkpoint_id} to {checkpoint_path}")

        return checkpoint_path

    @staticmethod
    def load(checkpoint_id: str, store_dir: Path) -> Checkpoint:
        """Load a checkpoint from the store.

        Args:
            checkpoint_id: ID of the checkpoint to load.
            store_dir: Directory containing the checkpoint file.

        Returns:
            The loaded checkpoint.

        Raises:
            FileNotFoundError: If checkpoint file does not exist.
        """
        checkpoint_path = store_dir / f"{checkpoint_id}.json"

        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint {checkpoint_id} not found at {checkpoint_path}")

        with open(checkpoint_path) as f:
            checkpoint_dict = json.load(f)

        # Parse datetime from ISO string
        checkpoint_dict["created_at"] = datetime.fromisoformat(checkpoint_dict["created_at"])

        checkpoint = Checkpoint(**checkpoint_dict)
        logger.debug(f"Loaded checkpoint {checkpoint_id}")

        return checkpoint

    @staticmethod
    def latest(cycle_id: str, store_dir: Path) -> Checkpoint | None:
        """Find the most recent checkpoint for a cycle.

        Args:
            cycle_id: ID of the cycle to search for.
            store_dir: Directory containing checkpoint files.

        Returns:
            The most recent checkpoint for the cycle, or None if none exist.
        """
        if not store_dir.exists():
            return None

        checkpoints: list[Checkpoint] = []

        for checkpoint_file in store_dir.glob("*.json"):
            try:
                checkpoint_dict = {}
                with open(checkpoint_file) as f:
                    checkpoint_dict = json.load(f)

                if checkpoint_dict.get("cycle_id") == cycle_id:
                    checkpoint_dict["created_at"] = datetime.fromisoformat(checkpoint_dict["created_at"])
                    checkpoints.append(Checkpoint(**checkpoint_dict))
            except (json.JSONDecodeError, ValueError, KeyError):
                logger.warning(f"Failed to load checkpoint from {checkpoint_file}")
                continue

        if not checkpoints:
            return None

        # Sort by created_at descending and return the most recent
        latest_checkpoint = max(checkpoints, key=lambda c: c.created_at)
        logger.debug(f"Found latest checkpoint {latest_checkpoint.checkpoint_id}")

        return latest_checkpoint

    @staticmethod
    def delete(checkpoint_id: str, store_dir: Path) -> None:
        """Delete a checkpoint from the store.

        Args:
            checkpoint_id: ID of the checkpoint to delete.
            store_dir: Directory containing the checkpoint file.
        """
        checkpoint_path = store_dir / f"{checkpoint_id}.json"

        if checkpoint_path.exists():
            checkpoint_path.unlink()
            logger.debug(f"Deleted checkpoint {checkpoint_id}")

    @staticmethod
    def list_checkpoints(cycle_id: str, store_dir: Path) -> list[str]:
        """List all checkpoint IDs for a cycle.

        Args:
            cycle_id: ID of the cycle to search for.
            store_dir: Directory containing checkpoint files.

        Returns:
            Sorted list of checkpoint IDs for the cycle.
        """
        if not store_dir.exists():
            return []

        checkpoint_ids: list[str] = []

        for checkpoint_file in store_dir.glob("*.json"):
            try:
                with open(checkpoint_file) as f:
                    checkpoint_dict = json.load(f)

                if checkpoint_dict.get("cycle_id") == cycle_id:
                    checkpoint_ids.append(checkpoint_dict["checkpoint_id"])
            except (json.JSONDecodeError, KeyError):
                logger.warning(f"Failed to load checkpoint from {checkpoint_file}")
                continue

        return sorted(checkpoint_ids)
