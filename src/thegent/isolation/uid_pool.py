"""UID pool management for tenant isolation."""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Set

logger = logging.getLogger(__name__)


class UidPool:
    """
    Manages a pool of UIDs for tenant isolation.

    Supports persistence to prevent UID reuse across restarts
    and ensures deterministic allocation for the same tenant.
    """

    def __init__(
        self,
        base_uid: int = 2000,
        size: int = 1000,
        state_file: Path | None = None,
    ) -> None:
        self.base_uid = base_uid
        self.size = size
        self.max_uid = base_uid + size - 1
        self.state_file = state_file

        # Mapping: tenant_id -> uid
        self._allocations: dict[str, int] = {}
        # Mapping: uid -> tenant_id (for reverse lookup)
        self._reverse_allocations: dict[int, str] = {}
        # Set of available UIDs
        self._available_uids: set[int] = set(range(base_uid, base_uid + size))

        if state_file:
            self._load_state()

    def _load_state(self) -> None:
        """Load allocation state from disk."""
        if not self.state_file or not self.state_file.exists():
            return

        try:
            with open(self.state_file) as f:
                data = json.load(f)
                self._allocations = data.get("allocations", {})
                for tenant_id, uid in self._allocations.items():
                    self._reverse_allocations[uid] = tenant_id
                    if uid in self._available_uids:
                        self._available_uids.remove(uid)
            logger.info(f"Loaded {len(self._allocations)} UID allocations from {self.state_file}")
        except Exception as e:
            logger.error(f"Failed to load UID pool state: {e}")

    def _save_state(self) -> None:
        """Save allocation state to disk."""
        if not self.state_file:
            return

        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, "w") as f:
                json.dump({"allocations": self._allocations}, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save UID pool state: {e}")

    def allocate(self, tenant_id: str) -> int:
        """
        Allocate a UID for a tenant.

        Returns existing UID if already allocated, otherwise picks next available.
        """
        if tenant_id in self._allocations:
            return self._allocations[tenant_id]

        if not self._available_uids:
            # If pool is full, we could either raise an error or try to reclaim
            raise RuntimeError(f"UID pool exhausted (size: {self.size})")

        # Pick the smallest available UID for predictability
        uid = min(self._available_uids)
        self._available_uids.remove(uid)

        self._allocations[tenant_id] = uid
        self._reverse_allocations[uid] = tenant_id

        self._save_state()
        logger.debug(f"Allocated UID {uid} to tenant {tenant_id}")
        return uid

    def release(self, tenant_id: str) -> None:
        """Release a UID back to the pool."""
        if tenant_id not in self._allocations:
            return

        uid = self._allocations.pop(tenant_id)
        self._reverse_allocations.pop(uid, None)
        self._available_uids.add(uid)

        self._save_state()
        logger.debug(f"Released UID {uid} from tenant {tenant_id}")

    def get_uid(self, tenant_id: str) -> int | None:
        """Get the UID for a tenant if it exists."""
        return self._allocations.get(tenant_id)

    def get_tenant_id(self, uid: int) -> str | None:
        """Get the tenant_id for a UID if it exists."""
        return self._reverse_allocations.get(uid)
