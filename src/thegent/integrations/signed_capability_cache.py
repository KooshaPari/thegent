"""Signed Capability Cache for connector capabilities.

Signs connector capability cache entries and enforces TTL renewal
to prevent use of stale or tampered capability data.

# @trace WL-293
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class SignedCapability:
    """A signed capability entry with TTL tracking.

    Attributes:
        capability_id: Unique identifier for the capability.
        connector: The connector this capability belongs to.
        capability_type: Type of capability (e.g., 'read', 'write', 'sync').
        enabled: Whether this capability is currently enabled.
        signature: Cryptographic signature validating this entry.
        created_at: Timestamp when capability was created.
        expires_at: Timestamp when the capability signature expires.
        last_renewed_at: Timestamp of last renewal.
    """

    capability_id: str
    connector: str
    capability_type: str
    enabled: bool
    signature: str
    created_at: datetime
    expires_at: datetime
    last_renewed_at: datetime


class SignedCapabilityCache:
    """Cache for signed connector capabilities with TTL enforcement.

    Maintains signed capability entries and enforces renewal of expired
    capabilities to prevent use of stale data.
    """

    def __init__(self, ttl_seconds: int = 3600) -> None:
        """Initialize the signed capability cache.

        Args:
            ttl_seconds: Time-to-live for capabilities in seconds (default: 3600).

        Raises:
            ValueError: If ttl_seconds is not positive.
        """
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")

        self._ttl_seconds = ttl_seconds
        self._capabilities: dict[str, SignedCapability] = {}

    def store(
        self,
        capability_id: str,
        connector: str,
        capability_type: str,
        enabled: bool,
        signature: str,
    ) -> SignedCapability:
        """Store a signed capability in the cache.

        Args:
            capability_id: Unique identifier for the capability.
            connector: The connector name.
            capability_type: Type of capability.
            enabled: Whether capability is enabled.
            signature: Cryptographic signature for validation.

        Returns:
            The stored SignedCapability object.

        Raises:
            ValueError: If any required parameter is empty.
        """
        if not capability_id:
            raise ValueError("capability_id cannot be empty")
        if not connector:
            raise ValueError("connector cannot be empty")
        if not capability_type:
            raise ValueError("capability_type cannot be empty")
        if not signature:
            raise ValueError("signature cannot be empty")

        now = datetime.now(timezone.utc)
        expires_at = datetime.fromtimestamp(
            now.timestamp() + self._ttl_seconds, tz=timezone.utc
        )

        capability = SignedCapability(
            capability_id=capability_id,
            connector=connector,
            capability_type=capability_type,
            enabled=enabled,
            signature=signature,
            created_at=now,
            expires_at=expires_at,
            last_renewed_at=now,
        )

        self._capabilities[capability_id] = capability
        return capability

    def get(self, capability_id: str) -> SignedCapability | None:
        """Get a capability from the cache.

        Returns None if capability doesn't exist or is expired.

        Args:
            capability_id: The capability identifier.

        Returns:
            The SignedCapability if found and not expired, None otherwise.
        """
        if capability_id not in self._capabilities:
            return None

        capability = self._capabilities[capability_id]

        if self.is_expired(capability_id):
            return None

        return capability

    def is_expired(self, capability_id: str) -> bool:
        """Check if a capability has expired.

        Args:
            capability_id: The capability identifier.

        Returns:
            True if expired or not found, False otherwise.
        """
        if capability_id not in self._capabilities:
            return True

        capability = self._capabilities[capability_id]
        now = datetime.now(timezone.utc)
        return now >= capability.expires_at

    def renew(self, capability_id: str, signature: str) -> SignedCapability | None:
        """Renew a capability's signature and TTL.

        Args:
            capability_id: The capability identifier.
            signature: New cryptographic signature.

        Returns:
            Updated SignedCapability if found and renewed, None otherwise.

        Raises:
            ValueError: If signature is empty.
        """
        if not signature:
            raise ValueError("signature cannot be empty")

        if capability_id not in self._capabilities:
            return None

        capability = self._capabilities[capability_id]
        now = datetime.now(timezone.utc)
        expires_at = datetime.fromtimestamp(
            now.timestamp() + self._ttl_seconds, tz=timezone.utc
        )

        # Update in place
        capability.signature = signature
        capability.expires_at = expires_at
        capability.last_renewed_at = now

        return capability

    def list_connector_capabilities(self, connector: str) -> list[SignedCapability]:
        """List all non-expired capabilities for a connector.

        Args:
            connector: The connector name.

        Returns:
            List of non-expired SignedCapability objects for the connector.
        """
        result = []

        for cap_id, capability in self._capabilities.items():
            if capability.connector == connector and not self.is_expired(cap_id):
                result.append(capability)

        return result

    def invalidate(self, capability_id: str) -> bool:
        """Invalidate (remove) a capability from the cache.

        Args:
            capability_id: The capability identifier.

        Returns:
            True if capability was removed, False if not found.
        """
        if capability_id in self._capabilities:
            del self._capabilities[capability_id]
            return True

        return False

    def cleanup_expired(self) -> int:
        """Remove all expired capabilities from the cache.

        Returns:
            Number of capabilities removed.
        """
        expired_ids = [
            cap_id
            for cap_id in self._capabilities
            if self.is_expired(cap_id)
        ]

        for cap_id in expired_ids:
            del self._capabilities[cap_id]

        return len(expired_ids)

    def get_all(self) -> list[SignedCapability]:
        """Get all capabilities (expired and non-expired).

        Returns:
            List of all SignedCapability objects.
        """
        return list(self._capabilities.values())
