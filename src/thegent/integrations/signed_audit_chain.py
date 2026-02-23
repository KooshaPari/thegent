"""Signed audit artifact chaining for compliance-grade provenance.

Maintains a verifiable chain of audit entries with cryptographic signatures
for compliance and provenance evidence.

FR traceability: WL-232 (Signed Audit Artifact Chain)
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AuditEntry:
    """Represents a single audit entry in the chain.

    # @trace WL-232
    """

    entry_id: str
    """Unique identifier for this audit entry."""

    data: dict[str, Any]
    """The audit data payload."""

    signature: str
    """SHA256 signature of this entry (computed from prev_signature + entry_id + data)."""

    prev_signature: str = ""
    """Signature of the previous entry in the chain (for chaining)."""


class SignedAuditArtifactChain:
    """Manages a verifiable chain of signed audit entries.

    # @trace WL-232
    """

    def __init__(self) -> None:
        """Initialize the chain with empty entries."""
        self._entries: list[AuditEntry] = []

    def append(self, entry_id: str, data: dict[str, Any]) -> AuditEntry:
        """Append a new audit entry to the chain.

        The entry's signature is computed as:
        SHA256(prev_signature + ":" + entry_id + ":" + json.dumps(data, sort_keys=True))

        Args:
            entry_id: Unique identifier for this entry.
            data: The audit data payload.

        Returns:
            The created AuditEntry with computed signature.
        """
        prev_signature = self._entries[-1].signature if self._entries else ""

        # Compute signature: SHA256 of prev_signature:entry_id:json_data
        data_json = json.dumps(data, sort_keys=True)
        signature_input = f"{prev_signature}:{entry_id}:{data_json}"
        signature = hashlib.sha256(signature_input.encode()).hexdigest()

        entry = AuditEntry(entry_id=entry_id, data=data, signature=signature, prev_signature=prev_signature)
        self._entries.append(entry)

        logger.debug(f"Appended audit entry {entry_id} (signature={signature[:8]}...)")
        return entry

    def verify_chain(self) -> bool:
        """Verify the integrity of the entire chain.

        Re-computes all signatures from scratch and verifies they match
        the stored signatures in each entry.

        Returns:
            True if the chain is valid, False if any entry's signature is invalid.
        """
        if not self._entries:
            return True

        prev_signature = ""
        for entry in self._entries:
            # Recompute signature for this entry
            data_json = json.dumps(entry.data, sort_keys=True)
            signature_input = f"{prev_signature}:{entry.entry_id}:{data_json}"
            expected_signature = hashlib.sha256(signature_input.encode()).hexdigest()

            # Verify it matches
            if expected_signature != entry.signature:
                logger.warning(
                    f"Signature mismatch for entry {entry.entry_id}: "
                    f"expected {expected_signature[:8]}..., got {entry.signature[:8]}..."
                )
                return False

            # Verify prev_signature matches
            if entry.prev_signature != prev_signature:
                logger.warning(
                    f"Chain link broken at {entry.entry_id}: "
                    f"expected prev_signature {prev_signature[:8]}..., "
                    f"got {entry.prev_signature[:8]}..."
                )
                return False

            prev_signature = entry.signature

        logger.debug(f"Chain verification passed for {len(self._entries)} entries")
        return True

    def entries(self) -> list[AuditEntry]:
        """Get all entries in the chain.

        Returns:
            A list of all AuditEntry objects in chain order.
        """
        return list(self._entries)
