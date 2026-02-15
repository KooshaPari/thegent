"""Canonical Structured Message (CSM) schema v1.

Unifies task-tool 18-tag and Zen rich protocol into a single typed schema
for orchestration events and agent outputs.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CSMStatus(str, Enum):
    """Canonical status values for agent/output lifecycle."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class CSMPhase(str, Enum):
    """Canonical phase for multi-agent workflows (Planner/Operator/Reviewer)."""

    PLANNER = "planner"
    OPERATOR = "operator"
    REVIEWER = "reviewer"
    UNKNOWN = "unknown"


@dataclass
class CanonicalStructuredMessage:
    """Canonical schema for agent output normalization.

    Maps task-tool 18-tag and Zen rich protocol into one typed structure.
    """

    # Core identifiers
    task_id: str = ""
    run_id: str = ""
    chunk_id: str = ""

    # Lifecycle
    status: CSMStatus = CSMStatus.PENDING
    phase: CSMPhase = CSMPhase.UNKNOWN
    progress: float = 0.0  # 0.0-1.0

    # Content
    objective: str = ""
    summary: str = ""
    actions_completed: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)

    # Evidence and governance
    evidence_set_hash: str = ""
    policy_gate_id: str = ""
    decision_reason_code: str = ""

    # Metadata
    schema_version: str = "csm-v1"
    source_contract: str = ""  # task-tool-18, zen-rich-v1, etc.
    raw_payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for JSON/transport."""
        return {
            "task_id": self.task_id,
            "run_id": self.run_id,
            "chunk_id": self.chunk_id,
            "status": self.status.value,
            "phase": self.phase.value,
            "progress": self.progress,
            "objective": self.objective,
            "summary": self.summary,
            "actions_completed": self.actions_completed,
            "issues": self.issues,
            "next_steps": self.next_steps,
            "evidence_set_hash": self.evidence_set_hash,
            "policy_gate_id": self.policy_gate_id,
            "decision_reason_code": self.decision_reason_code,
            "schema_version": self.schema_version,
            "source_contract": self.source_contract,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CanonicalStructuredMessage":
        """Deserialize from dict."""
        status = data.get("status", "pending")
        phase = data.get("phase", "unknown")
        return cls(
            task_id=data.get("task_id", ""),
            run_id=data.get("run_id", ""),
            chunk_id=data.get("chunk_id", ""),
            status=CSMStatus(status) if isinstance(status, str) else CSMStatus.PENDING,
            phase=CSMPhase(phase) if isinstance(phase, str) else CSMPhase.UNKNOWN,
            progress=float(data.get("progress", 0)),
            objective=data.get("objective", ""),
            summary=data.get("summary", ""),
            actions_completed=list(data.get("actions_completed", [])),
            issues=list(data.get("issues", [])),
            next_steps=list(data.get("next_steps", [])),
            evidence_set_hash=data.get("evidence_set_hash", ""),
            policy_gate_id=data.get("policy_gate_id", ""),
            decision_reason_code=data.get("decision_reason_code", ""),
            schema_version=data.get("schema_version", "csm-v1"),
            source_contract=data.get("source_contract", ""),
            raw_payload={
                k: v
                for k, v in data.items()
                if k
                not in {
                    "task_id",
                    "run_id",
                    "chunk_id",
                    "status",
                    "phase",
                    "progress",
                    "objective",
                    "summary",
                    "actions_completed",
                    "issues",
                    "next_steps",
                    "evidence_set_hash",
                    "policy_gate_id",
                    "decision_reason_code",
                    "schema_version",
                    "source_contract",
                }
            },
        )


__all__ = ["CSMPhase", "CSMStatus", "CanonicalStructuredMessage"]
