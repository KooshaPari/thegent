"""Remote Payload Checksum Verification for data integrity.

WL-226: Remote Payload Checksums
Computes, stores, and verifies SHA256 checksums for payload integrity.

# @trace WL-226
"""

from __future__ import annotations

import hashlib
import orjson as json
from dataclasses import dataclass
from typing import Any


@dataclass
class ChecksumRecord:
    """Record of a payload and its computed checksum."""

    payload_id: str
    checksum: str


class RemotePayloadChecksumVerifier:
    """Manages payload checksums for integrity verification."""

    def __init__(self) -> None:
        """Initialize the checksum verifier with an empty storage."""
        self._checksums: dict[str, ChecksumRecord] = {}

    def compute(self, payload_id: str, data: dict[str, Any]) -> ChecksumRecord:
        """Compute SHA256 checksum for a payload.

        Args:
            payload_id: Unique identifier for the payload.
            data: The data dictionary to compute the checksum for.

        Returns:
            A ChecksumRecord with the payload_id and computed checksum.
        """
        json_str = json.dumps(data, sort_keys=True).decode().decode()
        checksum = hashlib.sha256(json_str.encode("utf-8")).hexdigest()
        return ChecksumRecord(payload_id=payload_id, checksum=checksum)

    def verify(self, payload_id: str, data: dict[str, Any]) -> bool:
        """Verify that data matches the stored checksum.

        Args:
            payload_id: The payload ID to verify.
            data: The data to verify against the stored checksum.

        Returns:
            True if the computed checksum matches the stored checksum,
                False if no stored checksum exists or checksums don't match.
        """
        if payload_id not in self._checksums:
            return False

        stored_record = self._checksums[payload_id]
        computed_record = self.compute(payload_id, data)
        return stored_record.checksum == computed_record.checksum

    def store(self, record: ChecksumRecord) -> None:
        """Store a checksum record.

        Args:
            record: The ChecksumRecord to store.
        """
        self._checksums[record.payload_id] = record

    def get(self, payload_id: str) -> ChecksumRecord:
        """Retrieve a stored checksum record.

        Args:
            payload_id: The payload ID to retrieve.

        Returns:
            The ChecksumRecord for the given payload_id.

        Raises:
            KeyError: If the payload_id is not found.
        """
        if payload_id not in self._checksums:
            raise KeyError(f"Checksum record for payload '{payload_id}' not found")
        return self._checksums[payload_id]
