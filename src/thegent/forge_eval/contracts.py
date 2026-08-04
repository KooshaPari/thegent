"""Versioned, offline-safe contracts for ForgeEval runs.

These models describe inputs and observations.  They intentionally do not run
agents, call a judge, or persist credentials.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TaskFamily(StrEnum):
    """Supported task families in the reconstructed evaluation catalog."""

    TERMINAL_BENCH_2 = "terminal-bench-2"
    DEEP_SWE = "deep-swe"
    CUSTOM = "custom"


class ForgeEvalTask(BaseModel):
    """A versioned task specification with no embedded secret material."""

    model_config = ConfigDict(frozen=True)

    schema_version: str = "forgeeval.task.v1"
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{2,127}$")
    family: TaskFamily
    title: str = Field(min_length=1, max_length=200)
    instruction: str = Field(min_length=1)
    timeout_seconds: int = Field(default=240, ge=1, le=3600)
    tags: tuple[str, ...] = ()
    requires_network: bool = False


class JudgeSpec(BaseModel):
    """Declarative judge configuration; authentication stays in the environment."""

    model_config = ConfigDict(frozen=True)

    schema_version: str = "forgeeval.judge.v1"
    model: str = Field(min_length=1)
    transport: str = "openrouter"
    rubric_version: str = "forgeeval.rubric.v1"
    timeout_seconds: int = Field(default=60, ge=1, le=600)


class LatencyProfile(BaseModel):
    """Latency and throughput observations collected by a future runner."""

    model_config = ConfigDict(frozen=True)

    schema_version: str = "forgeeval.latency.v1"
    wall_time_seconds: float = Field(ge=0)
    time_to_first_token_seconds: float | None = Field(default=None, ge=0)
    inter_token_latency_seconds: float | None = Field(default=None, ge=0)
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    peak_concurrency: int = Field(default=1, ge=1)

    @property
    def tokens_per_second(self) -> float:
        """Return output throughput, avoiding a division-by-zero sentinel."""
        if self.wall_time_seconds == 0:
            return 0.0
        return self.output_tokens / self.wall_time_seconds


class ForgeEvalResult(BaseModel):
    """A single candidate-run observation, not a claimed benchmark conclusion."""

    model_config = ConfigDict(frozen=True)

    schema_version: str = "forgeeval.result.v1"
    task: ForgeEvalTask
    run_id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{2,127}$")
    harness: str = Field(min_length=1)
    candidate_model: str = Field(min_length=1)
    started_at: datetime
    completed_at: datetime
    succeeded: bool
    latency: LatencyProfile
    judge: JudgeSpec | None = None
    judge_score: float | None = Field(default=None, ge=0, le=1)
    failure_reason: str | None = None

    @model_validator(mode="after")
    def validate_temporal_and_judge_consistency(self) -> ForgeEvalResult:
        """Prevent impossible timestamps and unsupported scores."""
        if self.completed_at < self.started_at:
            raise ValueError("completed_at must not precede started_at")
        if self.judge_score is not None and self.judge is None:
            raise ValueError("judge_score requires a judge specification")
        return self
