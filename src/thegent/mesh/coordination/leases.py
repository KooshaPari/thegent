"""Lease-based file claims registry (SCLI-P6.3–P6.4).

Canonical home for ``FileClaimsRegistry``. Backed by
``src/thegent/mesh/coordination/leases.py``. The legacy flat path
``from thegent.mesh.coordination import FileClaimsRegistry`` is preserved
as a re-export in ``src/thegent/mesh/coordination/__init__.py``.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from .hlc import HLCTimestamp


class FileClaimsRegistry:
    """Lease-based file claims registry (SCLI-P6.3–P6.4).

    Each acquire writes a ``{agent_id, mode, expires_at, timestamp}`` JSON
    record under ``<claims_dir>/<sha256(file_path)>.lock``. The lease is
    renewed if the same agent re-acquires, and a background cleanup helper
    removes expired leases.
    """

    def __init__(self, mesh_root: Path) -> None:
        self.claims_dir = mesh_root / "claims"
        self.claims_dir.mkdir(parents=True, exist_ok=True, mode=0o1777)

    def acquire_lease(
        self,
        file_path: Path,
        agent_id: str,
        mode: str = "exclusive",
        ttl: int = 30,
    ) -> bool:
        """Acquire a lease on a file (SCLI-P6.3)."""
        file_id = hashlib.sha256(str(file_path).encode()).hexdigest()
        claim_file = self.claims_dir / f"{file_id}.lock"

        # Check if already held by someone else and not expired
        if claim_file.exists():
            with open(claim_file) as f:
                data = json.load(f)
            if time.time() < data["expires_at"]:
                if data["agent_id"] != agent_id:
                    return False

        # Write new/renew lease (SCLI-P6.4)
        lease_data = {
            "agent_id": agent_id,
            "mode": mode,
            "expires_at": time.time() + ttl,
            "timestamp": str(HLCTimestamp().update()),
        }

        with open(claim_file, "w") as f:
            json.dump(lease_data, f)
        return True

    def release_lease(self, file_path: Path, agent_id: str) -> bool:
        """Release a lease on a file."""
        file_id = hashlib.sha256(str(file_path).encode()).hexdigest()
        claim_file = self.claims_dir / f"{file_id}.lock"

        if claim_file.exists():
            with open(claim_file) as f:
                data = json.load(f)
            if data["agent_id"] == agent_id:
                claim_file.unlink()
                return True

        return False

    def _cleanup_expired_lock(self, lock_file: Path, now: float) -> int:
        """Clean up a single expired lock file. Returns 1 if deleted, 0 otherwise."""
        with open(lock_file) as f:
            data = json.load(f)
        if now > data["expires_at"]:
            lock_file.unlink()
            return 1
        return 0

    def cleanup_expired(self) -> int:
        """Background cleanup daemon (SCLI-P6.4)."""
        count = 0
        now = time.time()
        for lock_file in self.claims_dir.glob("*.lock"):
            count += self._cleanup_expired_lock(lock_file, now)
        return count


__all__ = ["FileClaimsRegistry"]
