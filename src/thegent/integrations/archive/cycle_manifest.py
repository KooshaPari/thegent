"""Immutable cycle manifests for audit and reproducibility.

# @trace WL-242
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class CycleManifest:
    """Immutable manifest capturing cycle inputs and outputs."""

    cycle_id: str
    created_at: datetime
    items: tuple[str, ...]


class CycleManifestStore:
    """Store for managing cycle manifests."""

    def __init__(self) -> None:
        """Initialize the cycle manifest store."""
        self._manifests: dict[str, CycleManifest] = {}

    def create(self, cycle_id: str, items: list[str]) -> CycleManifest:
        """Create a new cycle manifest.

        Args:
            cycle_id: The unique cycle identifier.
            items: The list of items included in this cycle.

        Returns:
            The created CycleManifest.
        """
        manifest = CycleManifest(
            cycle_id=cycle_id,
            created_at=datetime.now(timezone.utc),
            items=tuple(items),
        )
        self._manifests[cycle_id] = manifest
        return manifest

    def get(self, cycle_id: str) -> CycleManifest:
        """Retrieve a cycle manifest.

        Args:
            cycle_id: The cycle ID to retrieve.

        Returns:
            The CycleManifest object.

        Raises:
            KeyError: If the cycle is not found.
        """
        if cycle_id not in self._manifests:
            raise KeyError(f"Cycle {cycle_id} not found")
        return self._manifests[cycle_id]

    def list_cycles(self) -> list[str]:
        """List all cycle IDs.

        Returns:
            A list of all registered cycle IDs.
        """
        return list(self._manifests.keys())
