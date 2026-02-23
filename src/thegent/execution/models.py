"""Execution core models and enums."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class RunState(StrEnum):
    """Execution run states."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class MAIFArtifact(BaseModel):
    """Multi-Agent Interaction Framework artifact."""
    run_id: str
    artifact_id: str
    artifact_type: str
    content: dict[str, Any] = {}
    timestamp: datetime | None = None


class AgentSource(StrEnum):
    """Agent source types."""
    CODEX = "codex"
    CLAUDE = "claude"
    GPT = "gpt"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    OTHER = "other"


class InteractivityMode(StrEnum):
    """Interactivity modes."""
    AUTO = "auto"
    HITL = "hitl"
    FULL_AUTO = "full_auto"


class RunMeta(BaseModel):
    """Run metadata."""
    run_id: str
    session_id: str | None = None
    state: RunState = RunState.PENDING
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CheckpointMeta(BaseModel):
    """Checkpoint metadata."""
    checkpoint_id: str
    run_id: str
    step: int = 0
    timestamp: datetime | None = None


class CalibrationRegistry(BaseModel):
    """Calibration settings registry."""
    calibrations: dict[str, Any] = Field(default_factory=dict)


# Re-export for backward compatibility
__all__ = [
    "AgentSource",
    "CalibrationRegistry",
    "CheckpointMeta",
    "InteractivityMode",
    "MAIFArtifact",
    "RunMeta",
    "RunState",
]
