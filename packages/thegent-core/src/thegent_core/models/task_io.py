"""Pydantic schemas for task input/output validation and documentation.

These models provide structured, type-safe representations of task I/O,
replacing the loosely-typed dicts used across the execution pipeline.

All models use ``extra="allow"`` for forward compatibility: unknown fields
are preserved rather than rejected, so callers on older versions can still
communicate with newer agents that emit additional fields.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TaskInput(BaseModel):
    """Structured input for a single agent task execution.

    Replaces ad-hoc ``dict[str, Any]`` payloads passed to run_impl and
    related call sites.  All fields beyond ``task`` are optional to ensure
    backward compatibility with existing callers.
    """

    model_config = ConfigDict(extra="allow")

    task: str = Field(
        ...,
        description="The task prompt or description to execute.",
        min_length=1,
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Arbitrary key/value context injected alongside the task prompt. "
            "Typical keys: 'cwd', 'session_id', 'prior_output'."
        ),
    )
    max_tokens: int | None = Field(
        default=None,
        description="Maximum tokens the model may generate. None = provider default.",
        ge=1,
    )
    temperature: float | None = Field(
        default=None,
        description="Sampling temperature (0.0–2.0). None = provider default.",
        ge=0.0,
        le=2.0,
    )
    tools: list[str] = Field(
        default_factory=list,
        description="List of tool names available to the agent during this task.",
    )


class TaskOutput(BaseModel):
    """Structured output from a completed agent task execution.

    Captures both the textual result and key execution telemetry in a
    single, validated envelope.
    """

    model_config = ConfigDict(extra="allow")

    result: str = Field(
        ...,
        description="The final textual output produced by the agent.",
    )
    tokens_used: int = Field(
        ...,
        description="Total tokens consumed (prompt + completion).",
        ge=0,
    )
    model: str = Field(
        ...,
        description="Exact model identifier used for this execution.",
    )
    provider: str = Field(
        ...,
        description="Provider name (e.g. 'claude', 'gemini', 'antigravity').",
    )
    elapsed_ms: float = Field(
        ...,
        description="Wall-clock execution time in milliseconds.",
        ge=0.0,
    )
    tool_calls: list[Any] = Field(
        default_factory=list,
        description=(
            "Ordered list of tool invocations made during execution. "
            "Each element may be a dict or a provider-specific object."
        ),
    )


class TaskError(BaseModel):
    """Structured error envelope for a failed task execution.

    Provides machine-readable classification so orchestrators can decide
    whether to retry, escalate, or abort.
    """

    model_config = ConfigDict(extra="allow")

    error_type: str = Field(
        ...,
        description=(
            "Short error class identifier, e.g. 'usage_limit', 'timeout', 'api_error', 'policy_deny', 'parse_error'."
        ),
    )
    message: str = Field(
        ...,
        description="Human-readable error description.",
    )
    retriable: bool = Field(
        ...,
        description=(
            "True if the caller may safely retry this task without side effects. "
            "Transient API errors are typically retriable; policy denials are not."
        ),
    )


class TaskSpec(BaseModel):
    """Full task specification combining structured input with execution metadata.

    Intended as the canonical envelope passed into the orchestration layer.
    The ``input`` field carries the validated TaskInput; remaining fields
    capture routing and governance metadata that travels alongside the task.
    """

    model_config = ConfigDict(extra="allow")

    task_id: str | None = Field(
        default=None,
        description=(
            "Optional stable identifier for this task (kebab-case). "
            "When present, used for idempotency and audit linkage."
        ),
    )
    input: TaskInput = Field(
        ...,
        description="Structured task input payload.",
    )
    agent: str | None = Field(
        default=None,
        description="Preferred agent persona (e.g. 'worker', 'flash', 'claude').",
    )
    model: str | None = Field(
        default=None,
        description="Preferred model alias (e.g. 'claude-sonnet-4-5').",
    )
    lane: str = Field(
        default="standard",
        description="Execution lane: 'standard', 'critical', or 'recovery'.",
    )
    priority: str | None = Field(
        default=None,
        description="Task priority: 'P1', 'P2', 'P3', 'P4'.",
    )
    owner: str | None = Field(
        default=None,
        description="Identity of the agent or user that created this task spec.",
    )
    correlation_id: str | None = Field(
        default=None,
        description="Correlation identifier for tracing across services.",
    )
    idempotency_token: str | None = Field(
        default=None,
        description="Token that prevents duplicate executions of the same logical task.",
    )
