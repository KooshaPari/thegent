"""WP-10001: Operation envelope schema v2.

Provides a unified schema for all operations across CLI and MCP.
"""

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class OperationEnvelopeV2(BaseModel):
    """Unified operation envelope for Phase 10 convergence."""

    version: str = "2.0"
    operation_id: str = Field(..., description="Unique ID for this operation instance")
    parent_operation_id: str | None = None

    operation_type: str = Field(..., description="orchestrate, govern, recover, observe, plan")
    command: str = Field(..., description="The specific CLI command or tool name")

    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    auth_context: dict[str, Any] = Field(default_factory=dict)
    timestamp_utc: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    lane: Literal["standard", "critical", "recovery"] = "standard"
    status: Literal["created", "pending", "running", "completed", "failed"] = "created"


def validate_envelope_v2(envelope: dict[str, Any]) -> bool:
    """Validate a raw dict against the OperationEnvelopeV2 schema."""
    try:
        OperationEnvelopeV2(**envelope)
        return True
    except Exception:
        return False
