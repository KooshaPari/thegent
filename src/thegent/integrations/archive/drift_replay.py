"""Drift Replay Tool for deterministic debugging.

WL-317: Drift Replay Tool
Replays drift scenarios from archived manifests for deterministic debugging.
"""

from __future__ import annotations

import orjson as json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class DriftManifest:
    """A manifest of drift events for replay."""

    manifest_id: str
    cycle_id: str
    drifts: list[dict]
    captured_at: datetime

    def to_dict(self) -> dict:
        """Convert manifest to dictionary for JSON serialization.

        Returns:
            Dictionary representation with ISO-formatted timestamp.
        """
        data = asdict(self)
        data["captured_at"] = self.captured_at.isoformat()
        return data

    @staticmethod
    def from_dict(data: dict) -> DriftManifest:
        """Create manifest from dictionary (e.g., from JSON).

        Args:
            data: Dictionary with manifest data.

        Returns:
            DriftManifest instance.
        """
        captured_at_str = data["captured_at"]
        if isinstance(captured_at_str, str):
            captured_at = datetime.fromisoformat(captured_at_str)
        else:
            captured_at = captured_at_str

        return DriftManifest(
            manifest_id=data["manifest_id"],
            cycle_id=data["cycle_id"],
            drifts=data["drifts"],
            captured_at=captured_at,
        )


class DriftReplayEngine:
    """Engine for archiving and replaying drift manifests."""

    @staticmethod
    def archive_manifest(manifest: DriftManifest, archive_dir: Path) -> Path:
        """Archive a drift manifest to disk.

        Args:
            manifest: DriftManifest to archive.
            archive_dir: Directory to store archived manifest.

        Returns:
            Path where manifest was written.

        Raises:
            ValueError: If archive_dir does not exist.
        """
        if not archive_dir.exists():
            raise ValueError(f"Archive directory does not exist: {archive_dir}")

        output_path = archive_dir / f"{manifest.manifest_id}.json"
        with open(output_path, "w") as f:
            json.dump(manifest.to_dict(), f, indent=2)

        return output_path

    @staticmethod
    def load_manifest(manifest_id: str, archive_dir: Path) -> DriftManifest:
        """Load a drift manifest from archive.

        Args:
            manifest_id: ID of manifest to load.
            archive_dir: Directory containing archived manifests.

        Returns:
            Loaded DriftManifest instance.

        Raises:
            FileNotFoundError: If manifest file not found.
        """
        manifest_path = archive_dir / f"{manifest_id}.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")

        with open(manifest_path) as f:
            data = json.load(f)

        return DriftManifest.from_dict(data)

    @staticmethod
    def list_manifests(archive_dir: Path) -> list[str]:
        """List all manifest IDs in archive directory.

        Args:
            archive_dir: Directory containing archived manifests.

        Returns:
            Sorted list of manifest IDs (without .json extension).
        """
        if not archive_dir.exists():
            return []

        manifest_files = archive_dir.glob("*.json")
        manifest_ids = [f.stem for f in manifest_files]
        return sorted(manifest_ids)

    @staticmethod
    def replay(manifest: DriftManifest) -> list[dict]:
        """Replay drifts from a manifest.

        Deterministically replays drift events from the manifest.

        Args:
            manifest: DriftManifest to replay.

        Returns:
            List of drift events from the manifest.
        """
        return manifest.drifts
