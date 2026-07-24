"""Stub module."""

from dataclasses import dataclass


@dataclass
class EditLeaseManager:
    """Manager for edit leases."""

    lease_id: str
    resource: str
    holder: str
    expires_at: float

    def is_valid(self) -> bool:
        """Check if lease is still valid."""
        import time

        return time.time() < self.expires_at


__all__ = ["EditLeaseManager"]
