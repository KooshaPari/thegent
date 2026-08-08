"""Optimistic Concurrency Control (OCC) version tracking (SCLI-P6.1).

Canonical home for ``OptimisticConcurrencyControl``. Backed by
``src/thegent/mesh/coordination/occ.py``. The legacy flat path
``from thegent.mesh.coordination import OptimisticConcurrencyControl`` is
preserved as a re-export in ``src/thegent/mesh/coordination/__init__.py``.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .hlc import HLCTimestamp


class OptimisticConcurrencyControl:
    """OCC version tracking (SCLI-P6.1).

    Tracks the sha256 version of each file at claim time so that a later
    ``verify_version`` can detect concurrent writes between the claim and
    the actual edit.
    """

    def __init__(self, mesh_root: Path) -> None:
        self.version_dir = mesh_root / "versions"
        self.version_dir.mkdir(parents=True, exist_ok=True, mode=0o1777)

    def get_version(self, file_path: Path) -> str:
        """Get current version hash of a file."""
        if not file_path.exists():
            return "empty"

        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def claim_version(self, file_path: Path, agent_id: str) -> str:
        """Record the version of a file at claim time (SCLI-P6.1)."""
        version = self.get_version(file_path)
        claim_data = {
            "agent_id": agent_id,
            "version": version,
            "timestamp": str(HLCTimestamp().update()),
        }

        file_id = hashlib.sha256(str(file_path).encode()).hexdigest()
        with open(self.version_dir / f"{file_id}-{agent_id}.json", "w") as f:
            json.dump(claim_data, f)

        return version

    def verify_version(self, file_path: Path, agent_id: str) -> bool:
        """Verify the file hasn't changed since it was claimed."""
        file_id = hashlib.sha256(str(file_path).encode()).hexdigest()
        claim_file = self.version_dir / f"{file_id}-{agent_id}.json"

        if not claim_file.exists():
            return True  # No claim found, proceed at own risk?

        with open(claim_file) as f:
            claim_data = json.load(f)

        current_version = self.get_version(file_path)
        return current_version == claim_data["version"]


__all__ = ["OptimisticConcurrencyControl"]
