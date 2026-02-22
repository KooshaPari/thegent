"""Incident snapshot bundle for immutable postmortem workflows.

Captures and stores immutable snapshots of incidents at specific points in time,
enabling auditable postmortem analysis and incident trend analysis.

# @trace WL-268
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class IncidentSnapshot:
    """Immutable snapshot of an incident at a specific point in time.

    Attributes:
        incident_id: Unique identifier for the incident.
        timestamp: Exact time the snapshot was captured.
        data: Dictionary containing the incident state and metadata.
    """

    incident_id: str
    timestamp: datetime
    data: dict[str, Any]


class IncidentSnapshotBundle:
    """Manages capture, storage, and export of incident snapshots.

    Provides a registry for incident snapshots, enabling postmortem workflows
    to access immutable historical snapshots of incidents.
    """

    def __init__(self):
        """Initialize the snapshot bundle with an empty incident registry."""
        self._snapshots: dict[str, IncidentSnapshot] = {}

    def capture(self, incident_id: str, data: dict[str, Any]) -> IncidentSnapshot:
        """Capture a snapshot of the current incident state.

        Args:
            incident_id: Unique identifier for the incident.
            data: Dictionary containing incident state and metadata.

        Returns:
            The created IncidentSnapshot.
        """
        snapshot = IncidentSnapshot(
            incident_id=incident_id, timestamp=datetime.now(timezone.utc), data=data
        )
        self._snapshots[incident_id] = snapshot

        logger.debug(
            f"Captured incident snapshot for {incident_id} at {snapshot.timestamp.isoformat()}"
        )

        return snapshot

    def get(self, incident_id: str) -> IncidentSnapshot:
        """Retrieve a snapshot for a specific incident.

        Args:
            incident_id: Unique identifier for the incident.

        Returns:
            The IncidentSnapshot for the incident.

        Raises:
            KeyError: If the incident is not in the bundle.
        """
        if incident_id not in self._snapshots:
            raise KeyError(f"Incident snapshot for '{incident_id}' not found")
        return self._snapshots[incident_id]

    def list_incidents(self) -> list[str]:
        """List all incident IDs in the bundle.

        Returns:
            A list of all incident IDs for which snapshots are stored.
        """
        return list(self._snapshots.keys())

    def export(self) -> list[dict[str, Any]]:
        """Export all incident snapshots as a serializable list.

        Converts IncidentSnapshot objects to dictionaries with ISO-formatted
        timestamps, suitable for JSON serialization or storage.

        Returns:
            A list of dictionaries representing all incident snapshots.
        """
        exported = []
        for snapshot in self._snapshots.values():
            snapshot_dict = asdict(snapshot)
            # Convert datetime to ISO format string for JSON serialization
            snapshot_dict["timestamp"] = snapshot.timestamp.isoformat()
            exported.append(snapshot_dict)

        logger.debug(f"Exported {len(exported)} incident snapshots")
        return exported
