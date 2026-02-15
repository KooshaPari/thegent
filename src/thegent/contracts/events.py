"""Canonical event schemas for orchestration audit trail (WP-0002).

Provides formal Pydantic models for chunk, evidence, and policy events
used in run registry, telemetry, and compliance evidence retention.
"""

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ChunkEvent(BaseModel):
    """Canonical schema for streaming output chunk events.

    Used when persisting or emitting partial parser/agent output.
    """

    run_id: str = ""
    task_id: str = ""
    chunk_id: str = ""
    sequence: int = 0
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp_utc: str = Field(default_factory=_utc_now)
    schema_version: str = "chunk-v1"


class EvidenceEvent(BaseModel):
    """Canonical schema for evidence artifact events.

    Links runs/tasks to evidence (session_id, hash, artifact type).
    """

    run_id: str = ""
    task_id: str = ""
    evidence_id: str = ""  # session_id or artifact id
    evidence_type: str = "session"  # session, artifact, hash
    hash_value: Optional[str] = None
    timestamp_utc: str = Field(default_factory=_utc_now)
    schema_version: str = "evidence-v1"


class PolicyEvent(BaseModel):
    """Canonical schema for policy decision events.

    Records allow/deny/warn with reason and policy gate id.
    """

    run_id: str = ""
    decision: str = "allow"  # allow, deny, warn
    reason: str = ""
    policy_id: Optional[str] = None
    override_applied: bool = False
    timestamp_utc: str = Field(default_factory=_utc_now)
    schema_version: str = "policy-v1"


__all__ = ["ChunkEvent", "EvidenceEvent", "PolicyEvent"]
