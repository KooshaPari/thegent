"""Canonical Structured Message (CSM) schema v1.

Unifies task-tool 18-tag and Zen rich protocol into a single typed schema
for orchestration events and agent outputs.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class CSMStatus(StrEnum):
    """Canonical status values for agent/output lifecycle."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class CSMPhase(StrEnum):
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
    agent: str = ""
    model: str = ""

    # Lifecycle
    status: CSMStatus = CSMStatus.PENDING
    phase: CSMPhase = CSMPhase.UNKNOWN
    progress: float = 0.0  # 0.0-1.0

    # Content & Workload (Zen: ACTIONS_COMPLETED, ACTIONS_PENDING, FILES_CREATED, FILES_MODIFIED, DEPENDENCIES)
    objective: str = ""
    summary: str = ""
    actions_completed: list[str] = field(default_factory=list)
    actions_pending: list[str] = field(default_factory=list)
    files_created: list[str] = field(default_factory=list)
    files_modified: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)

    # Intelligence & Review (Zen: QUESTIONS, WARNINGS, SUGGESTIONS, PERFORMANCE_NOTES, TEST_RESULTS, CODE_QUALITY, DOCUMENTATION)
    issues: list[str] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    performance_notes: str = ""
    test_results: str = ""
    code_quality: str = ""
    documentation: str = ""

    # Architecture & Design (Zen: ARCHITECTURE_NOTES, SECURITY_CONSIDERATIONS, BLOCKERS)
    architecture_notes: str = ""
    security_considerations: str = ""
    blockers: list[str] = field(default_factory=list)

    # Risk & Governance (Zen: ASSUMPTIONS, RISKS, ALTERNATIVES_CONSIDERED, DECISION_RATIONALE, CONFIDENCE_LEVEL, ESTIMATED_EFFICIENCY, IMPACT_ASSESSMENT, ROLLBACK_PLAN)
    assumptions: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    alternatives_considered: list[str] = field(default_factory=list)
    decision_rationale: str = ""
    confidence_level: float = 1.0  # 0.0-1.0
    estimated_effort: str = ""
    impact_assessment: str = ""
    rollback_plan: str = ""
    next_steps: list[str] = field(default_factory=list)

    # Legacy/Compatibility
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
            "agent": self.agent,
            "model": self.model,
            "status": self.status.value,
            "phase": self.phase.value,
            "progress": self.progress,
            "objective": self.objective,
            "summary": self.summary,
            "actions_completed": self.actions_completed,
            "actions_pending": self.actions_pending,
            "files_created": self.files_created,
            "files_modified": self.files_modified,
            "dependencies": self.dependencies,
            "issues": self.issues,
            "questions": self.questions,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
            "performance_notes": self.performance_notes,
            "test_results": self.test_results,
            "code_quality": self.code_quality,
            "documentation": self.documentation,
            "architecture_notes": self.architecture_notes,
            "security_considerations": self.security_considerations,
            "blockers": self.blockers,
            "assumptions": self.assumptions,
            "risks": self.risks,
            "alternatives_considered": self.alternatives_considered,
            "decision_rationale": self.decision_rationale,
            "confidence_level": self.confidence_level,
            "estimated_effort": self.estimated_effort,
            "impact_assessment": self.impact_assessment,
            "rollback_plan": self.rollback_plan,
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
            agent=data.get("agent", ""),
            model=data.get("model", ""),
            status=CSMStatus(status) if isinstance(status, str) else CSMStatus.PENDING,
            phase=CSMPhase(phase) if isinstance(phase, str) else CSMPhase.UNKNOWN,
            progress=float(data.get("progress", 0)),
            objective=data.get("objective", ""),
            summary=data.get("summary", ""),
            actions_completed=list(data.get("actions_completed", [])),
            actions_pending=list(data.get("actions_pending", [])),
            files_created=list(data.get("files_created", [])),
            files_modified=list(data.get("files_modified", [])),
            dependencies=list(data.get("dependencies", [])),
            issues=list(data.get("issues", [])),
            questions=list(data.get("questions", [])),
            warnings=list(data.get("warnings", [])),
            suggestions=list(data.get("suggestions", [])),
            performance_notes=data.get("performance_notes", ""),
            test_results=data.get("test_results", ""),
            code_quality=data.get("code_quality", ""),
            documentation=data.get("documentation", ""),
            architecture_notes=data.get("architecture_notes", ""),
            security_considerations=data.get("security_considerations", ""),
            blockers=list(data.get("blockers", [])),
            assumptions=list(data.get("assumptions", [])),
            risks=list(data.get("risks", [])),
            alternatives_considered=list(data.get("alternatives_considered", [])),
            decision_rationale=data.get("decision_rationale", ""),
            confidence_level=float(data.get("confidence_level", 1.0)),
            estimated_effort=data.get("estimated_effort", ""),
            impact_assessment=data.get("impact_assessment", ""),
            rollback_plan=data.get("rollback_plan", ""),
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
                    "agent",
                    "model",
                    "status",
                    "phase",
                    "progress",
                    "objective",
                    "summary",
                    "actions_completed",
                    "actions_pending",
                    "files_created",
                    "files_modified",
                    "dependencies",
                    "issues",
                    "questions",
                    "warnings",
                    "suggestions",
                    "performance_notes",
                    "test_results",
                    "code_quality",
                    "documentation",
                    "architecture_notes",
                    "security_considerations",
                    "blockers",
                    "assumptions",
                    "risks",
                    "alternatives_considered",
                    "decision_rationale",
                    "confidence_level",
                    "estimated_effort",
                    "impact_assessment",
                    "rollback_plan",
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
