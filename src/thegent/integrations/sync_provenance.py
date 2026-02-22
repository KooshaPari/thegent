"""Provenance metadata for sync operations.

Adds per-item provenance stamps to tracked sync records with sync ID,
timestamp, source, operator, and cycle number.

FR traceability: WL-201 (Sync Provenance Stamps)
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)

# Provenance metadata key in records
_PROVENANCE_KEY = "__provenance__"


@dataclass
class SyncProvenanceStamp:
    """Provenance metadata for a sync operation.

    Attributes:
        sync_id: Unique identifier for the sync operation.
        timestamp: ISO 8601 timestamp of when the sync occurred.
        source: Source system (e.g., "github", "linear", "board").
        operator: The operator or service that performed the sync.
        cycle_number: Monotonic cycle counter for repeated syncs.
    """

    sync_id: str
    timestamp: str
    source: str
    operator: str
    cycle_number: int

    def to_dict(self) -> dict[str, Any]:
        """Convert stamp to a dictionary.

        Returns:
            Dictionary representation of the stamp.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SyncProvenanceStamp:
        """Create a stamp from a dictionary.

        Args:
            data: Dictionary with required keys.

        Returns:
            A new SyncProvenanceStamp instance.

        Raises:
            KeyError: If required fields are missing.
        """
        return cls(
            sync_id=data["sync_id"],
            timestamp=data["timestamp"],
            source=data["source"],
            operator=data["operator"],
            cycle_number=data["cycle_number"],
        )


def stamp_sync_record(
    record: dict[str, Any],
    stamp: SyncProvenanceStamp,
) -> dict[str, Any]:
    """Attach a provenance stamp to a record.

    Creates a shallow copy of the record with the stamp attached.

    Args:
        record: The record to stamp (dict).
        stamp: The provenance stamp to attach.

    Returns:
        A new dict with the stamp attached under the provenance key.

    Raises:
        ValueError: If record is not a dictionary.
    """
    if not isinstance(record, dict):
        raise ValueError("record must be a dictionary")

    result = record.copy()
    result[_PROVENANCE_KEY] = stamp.to_dict()
    return result


def extract_provenance(record: dict[str, Any]) -> SyncProvenanceStamp | None:
    """Extract the provenance stamp from a record.

    Args:
        record: The record to extract from.

    Returns:
        The SyncProvenanceStamp if present, None otherwise.

    Raises:
        ValueError: If the provenance data is malformed.
    """
    if not isinstance(record, dict):
        raise ValueError("record must be a dictionary")

    if _PROVENANCE_KEY not in record:
        return None

    prov_data = record[_PROVENANCE_KEY]
    if not isinstance(prov_data, dict):
        raise ValueError("Provenance data must be a dictionary")

    try:
        return SyncProvenanceStamp.from_dict(prov_data)
    except KeyError as e:
        raise ValueError(f"Malformed provenance data: missing key {e}") from e


def has_provenance(record: dict[str, Any]) -> bool:
    """Check if a record has provenance metadata.

    Args:
        record: The record to check.

    Returns:
        True if the record has provenance metadata.
    """
    return isinstance(record, dict) and _PROVENANCE_KEY in record


def remove_provenance(record: dict[str, Any]) -> dict[str, Any]:
    """Remove provenance metadata from a record.

    Creates a shallow copy without the provenance key.

    Args:
        record: The record to clean.

    Returns:
        A new dict without provenance metadata.
    """
    if not isinstance(record, dict):
        raise ValueError("record must be a dictionary")

    result = record.copy()
    result.pop(_PROVENANCE_KEY, None)
    return result


def get_current_timestamp() -> str:
    """Get the current timestamp in ISO 8601 format.

    Returns:
        ISO 8601 formatted timestamp.
    """
    return datetime.utcnow().isoformat() + "Z"
