"""Phase 8: File Coordination implementation.
Includes OCC, HLC, and Lease registry.
"""

import time
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
import hashlib
import os

logger = logging.getLogger(__name__)

class HybridLogicalClock:
    """Implementation of Hybrid Logical Clock (HLC)."""
    def __init__(self):
        self.logical = 0
        self.physical = 0

    def now(self) -> str:
        """Generate next HLC timestamp."""
        p_now = int(time.time() * 1000)
        if p_now > self.physical:
            self.physical = p_now
            self.logical = 0
        else:
            self.logical += 1
        return f"{self.physical}:{self.logical}"

class FileLeaseRegistry:
    """Registry for file leases using flock-like semantics."""
    def __init__(self, registry_dir: Path):
        self.registry_dir = registry_dir
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.hlc = HybridLogicalClock()

    def claim_lease(self, path: Path, agent_id: str, mode: str = "exclusive", ttl: int = 30) -> Optional[str]:
        """Claim a lease on a file."""
        lease_path = self._get_lease_path(path)
        if lease_path.exists():
            # Check if expired
            try:
                data = lease_path.read_text().split("|")
                expiry = float(data[2])
                if time.time() > expiry:
                    logger.info(f"Lease expired for {path}, reclaiming.")
                else:
                    logger.warning(f"File {path} is currently leased by {data[0]}")
                    return None
            except (IndexError, ValueError):
                pass

        # Create lease
        expiry = time.time() + ttl
        token = self.hlc.now()
        lease_path.write_text(f"{agent_id}|{mode}|{expiry}|{token}")
        return token

    def renew_lease(self, path: Path, agent_id: str, token: str, ttl: int = 30) -> bool:
        """Renew an existing lease."""
        lease_path = self._get_lease_path(path)
        if not lease_path.exists():
            return False
        
        data = lease_path.read_text().split("|")
        if data[0] == agent_id and data[3] == token:
            expiry = time.time() + ttl
            lease_path.write_text(f"{agent_id}|{data[1]}|{expiry}|{token}")
            return True
        return False

    def release_lease(self, path: Path, agent_id: str, token: str):
        """Release a file lease."""
        lease_path = self._get_lease_path(path)
        if lease_path.exists():
            data = lease_path.read_text().split("|")
            if data[0] == agent_id and data[3] == token:
                lease_path.unlink()

    def _get_lease_path(self, path: Path) -> Path:
        hashed = hashlib.sha256(str(path.resolve()).encode()).hexdigest()
        return self.registry_dir / f"{hashed}.lease"

class OCCManager:
    """Optimistic Concurrency Control manager."""
    def __init__(self, version_db: Path):
        self.version_db = version_db
        self.version_db.mkdir(parents=True, exist_ok=True)

    def get_version(self, path: Path) -> str:
        """Record current file version (SHA256 hash)."""
        if not path.exists():
            return "none"
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def verify_and_commit(self, path: Path, base_version: str, new_content: bytes) -> bool:
        """Verify version hasn't changed and commit new content."""
        current_version = self.get_version(path)
        if current_version != base_version:
            logger.error(f"OCC violation for {path}: expected {base_version}, got {current_version}")
            return False
        
        path.write_bytes(new_content)
        return True
