"""Execution state and metadata models.

Domain: State & Metadata
Classes:
- RunState: Execution state enum
- AgentSource: Agent type enum
- InteractivityMode: Interaction mode enum
- RunMeta: Run metadata
- CheckpointMeta: Checkpoint metadata
- MAIFArtifact: MAIF artifact model
- ContinuityPacket: Continuity packet
- CalibrationRegistry: Calibration registry
"""

from enum import Enum

# StrEnum only available in Python 3.11+
try:
    from enum import StrEnum
except ImportError:
    StrEnum = Enum

from typing import Any

from pydantic import BaseModel, Field


class RunState(StrEnum):
    """Execution run state."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentSource(StrEnum):
    """Agent source type."""
    CLAUDE = "claude"
    CODEX = "codex"
    GPT = "gpt"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    CUSTOM = "custom"


class InteractivityMode(StrEnum):
    """Interactivity mode."""
    INTERACTIVE = "interactive"
    AUTOMATED = "automated"
    SEMI_AUTOMATED = "semi_automated"


class RunMeta(BaseModel):
    """Run metadata."""
    run_id: str
    session_id: str
    state: RunState
    agent_source: AgentSource
    interactivity_mode: InteractivityMode
    started_at: str | None = None
    ended_at: str | None = None
    error: str | None = None
    metadata: dict = Field(default_factory=dict)


class CheckpointMeta(BaseModel):
    """Checkpoint metadata."""
    checkpoint_id: str
    run_id: str
    phase: str
    created_at: str
    data: dict = Field(default_factory=dict)


class MAIFArtifact(BaseModel):
    """MAIF artifact model."""
    artifact_id: str
    artifact_type: str
    content: str
    hash: str
    created_at: str
    metadata: dict = Field(default_factory=dict)


class ContinuityPacket(BaseModel):
    """Continuity packet for session handoff."""
    session_id: str
    run_id: str
    state: dict[str, Any]
    context: dict[str, Any]
    timestamp: str


class CalibrationRegistry:
    """Registry for execution calibration data."""

    def __init__(self) -> None:
        self._calibrations: dict[str, dict[str, Any]] = {}

    def register(self, run_id: str, calibration: dict[str, Any]) -> None:
        """Register calibration for a run."""
        self._calibrations[run_id] = calibration

    def get(self, run_id: str) -> dict[str, Any] | None:
        """Get calibration for a run."""
        return self._calibrations.get(run_id)

    def list_all(self) -> list[dict[str, Any]]:
        """List all calibrations."""
        return list(self._calibrations.values())


__all__ = [
    "AgentSource",
    "CalibrationRegistry",
    "CheckpointMeta",
    "ContinuityPacket",
    "InteractivityMode",
    "MAIFArtifact",
    "RunMeta",
    "RunState",
]
