"""CSM (Canonical Structured Message) contracts module."""

from __future__ import annotations
from typing import TYPE_CHECKING, Any
from enum import Enum


class CSMPhase(Enum):
    """CSM phase enumeration."""

    PARSE = "parse"
    COMMIT = "commit"
    SIDE_EFFECTS = "side_effects"
    RESPONSE = "response"


class CSMStatus(Enum):
    """CSM status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CanonicalStructuredMessage:
    """Canonical structured message for contracts."""

    def __init__(self, msg_type: str, payload: dict[str, Any]) -> None:
        self.msg_type = msg_type
        self.payload = payload
        self.status = CSMStatus.PENDING

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.msg_type, "payload": self.payload, "status": self.status.value}


__all__ = [
    "CSMPhase",
    "CSMStatus",
    "CanonicalStructuredMessage",
    "get_csm",
]


def get_csm(msg_type: str, payload: dict[str, Any]) -> CanonicalStructuredMessage:
    """Get a canonical structured message."""
    return CanonicalStructuredMessage(msg_type=msg_type, payload=payload)
