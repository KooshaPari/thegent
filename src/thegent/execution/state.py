"""Execution run metadata and registry for thegent orchestration."""

import contextlib
import orjson as json
import logging
import os
import socket
import uuid
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from thegent.execution_coercion_helpers import as_bool as _as_bool_impl
from thegent.execution_coercion_helpers import as_float as _as_float_impl
from thegent.execution_coercion_helpers import as_int as _as_int_impl

_log = logging.getLogger(__name__)
_EXECUTION_WARNING_LIMIT = 3
_execution_warning_count = 0
_admission_import_warning_once: set[str] = set()
_execution_diagnostics: dict[str, Any] = {
    "optional_gate_import_failures": 0,
    "optional_gate_last_error_type": None,
    "optional_gate_last_error_message": None,
    "deadline_unregister": {
        "import_failures": 0,
        "runtime_failures": 0,
        "last_error_type": None,
        "last_error_message": None,
    },
    "message_parse": {
        "invalid_rows": 0,
        "non_pending_rows": 0,
        "last_error_type": None,
        "last_error_message": None,
    },
}


def _warn_bounded(message: str, *args: object) -> None:
    global _execution_warning_count
    _execution_warning_count += 1
    if _execution_warning_count <= _EXECUTION_WARNING_LIMIT:
        _log.warning(message, *args)


def get_execution_diagnostics() -> dict[str, Any]:
    """Return diagnostics snapshot for execution-path degradation."""
    return {
        "optional_gate_import_failures": _execution_diagnostics["optional_gate_import_failures"],
        "optional_gate_last_error_type": _execution_diagnostics["optional_gate_last_error_type"],
        "optional_gate_last_error_message": _execution_diagnostics["optional_gate_last_error_message"],
        "deadline_unregister": dict(_execution_diagnostics["deadline_unregister"]),
        "message_parse": dict(_execution_diagnostics["message_parse"]),
    }


def reset_execution_diagnostics() -> None:
    """Reset execution diagnostics (test helper)."""
    global _execution_warning_count
    _execution_warning_count = 0
    _admission_import_warning_once.clear()
    _execution_diagnostics["optional_gate_import_failures"] = 0
    _execution_diagnostics["optional_gate_last_error_type"] = None
    _execution_diagnostics["optional_gate_last_error_message"] = None
    _execution_diagnostics["deadline_unregister"] = {
        "import_failures": 0,
        "runtime_failures": 0,
        "last_error_type": None,
        "last_error_message": None,
    }
    _execution_diagnostics["message_parse"] = {
        "invalid_rows": 0,
        "non_pending_rows": 0,
        "last_error_type": None,
        "last_error_message": None,
    }


def _as_float(value: Any, default: float) -> float:
    """Coerce arbitrary values to float with a safe default."""
    return _as_float_impl(value, default)


def _as_int(value: Any, default: int) -> int:
    """Coerce arbitrary values to int with a safe default."""
    return _as_int_impl(value, default)


def _as_bool(value: Any, default: bool) -> bool:
    """Coerce arbitrary values to bool with a safe default."""
    return _as_bool_impl(value, default)


class RunState(StrEnum):
    """Run lifecycle state for state-aware orchestration (G-KD-03)."""

    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class MAIFArtifact(BaseModel):
    """WP-3002: Model AI Information Format (MAIF) for signed artifacts."""

    version: str = "1.0"
    run_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    agent: str
    model: str | None = None
    prompt_hash: str
    output_hash: str | None = None
    signature: str
    policy_result: str | None = None


class ContinuityPacket(BaseModel):
    """Compressed essence of session progress for cross-session handoffs (L3/L4).

    # @trace FR-HAX-004
    """

    intent: str
    """High-level goal of the session."""

    decisions: list[str] = Field(default_factory=list)
    """Key decisions made during the session."""

    risks: list[str] = Field(default_factory=list)
    """Identified risks or blockers."""

    context_hashes: dict[str, str] = Field(default_factory=dict)
    """SHA-256 hashes of referenced context files keyed by path string."""

    token_count: int = 0
    """Approximate token count (rough estimate)."""

    session_id: str = Field(default_factory=lambda: "")
    """Session ID this packet belongs to."""

    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    """ISO-8601 timestamp when the packet was created."""


class AgentSource(StrEnum):
    """Source of the agent process for session registry (WP-9001)."""

    THEGENT_RUN = "thegent-run"
    THEGENT_DROID = "thegent-droid"
    THEGENT_SUBAGENT = "thegent-subagent"
    IDE_MANAGED = "ide-managed"
    USER_SPAWNED = "user-spawned"
    DISCOVERED = "discovered"
    MCP_PROXY = "mcp-proxy"


class InteractivityMode(StrEnum):
    """Interactivity mode of the session (WP-9002)."""

    PTY = "pty"
    TMUX = "tmux"
    HEADLESS_LOGS = "headless-logs"
    HEADLESS_HOLDPTY = "headless-holdpty"
    READ_ONLY = "read-only"


class RunMeta(BaseModel):
    """Metadata for a single agent/droid execution run."""

    run_id: str = Field(default_factory=lambda: f"run_{uuid.uuid4().hex[:8]}")
    correlation_id: str | None = None
    source: AgentSource = AgentSource.THEGENT_RUN
    interactivity: InteractivityMode = InteractivityMode.HEADLESS_LOGS

    # Attachment details
    attach_target: dict[str, Any] | None = None
    message_endpoint: str | None = None

    # Paths (managed sessions only)
    stdout_path: str | None = None
    stderr_path: str | None = None
    chat_path: str | None = None
    messages_path: str | None = None
    audit_path: str | None = None

    agent: str
    model: str | None = None
    mode: str = "write"
    prompt: str
    cwd: str
    owner: str
    started_at_utc: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    ended_at_utc: str | None = None
    duration_s: float | None = None
    exit_code: int | None = None
    status: str = "started"  # started, running, completed, failed, timed_out
    error_class: str | None = None  # usage_limit, timeout, logic_error, api_error
    signature: str | None = None
    policy_result: str | None = None  # allow, deny, warn
    policy_reason: str | None = None
    override_reason: str | None = None
    override_by: str | None = None
    rationale: str | None = None  # WP-4002/4007: Full explanation
    feedback_score: float | None = None  # WP-4008
    feedback_note: str | None = None
    host: str = Field(default_factory=socket.gethostname)
    pid: int = Field(default_factory=os.getpid)
    is_background: bool = False
    lane: str = "standard"  # standard, critical, recovery
    idempotency_token: str | None = None
    confidence: float | None = None
    arbitration: str | None = None  # leader, follower, consensus
    freshness_timestamp: str | None = Field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )  # ROB-011: Timestamp for stale-state detection

    # Audit trail chaining (WP-3004)
    prev_hash: str | None = None
    hash: str | None = None

    # Optional routing contract context
    route_contract: dict[str, Any] | None = None
    route_request: dict[str, Any] | None = None

    # Task routing metadata (Terminal Bench 2.0 Pareto frontier)
    task_category: str | None = None  # fast/normal/complex/high_complex
    task_complexity_score: int | None = None  # 0-100 complexity score
    estimated_cost_usd: float | None = None  # Estimated cost for this task
    estimated_duration_s: float | None = None  # Estimated duration
    constraint_violations: list[str] | None = None  # Hard constraint failures
    routing_reason: str | None = None  # Routing decision explanation

    # WP-3006: Compliance evidence retention — domain tagging for tiered retention
    domain_tag: str | None = None  # e.g. project-id, compliance-domain, lane

    # XA4: Contract version in task/run metadata for negotiation
    contract_version: str | None = None

    # WP-16002: Teammate delegation linkage
    task_id: str | None = None
    task_metadata: dict[str, Any] | None = None


class CheckpointMeta(BaseModel):
    """Metadata for a DAG/state checkpoint."""

    checkpoint_id: str = Field(default_factory=lambda: f"ckpt_{uuid.uuid4().hex[:8]}")
    created_at_utc: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    reason: str
    dag_content: str
    session_dir: str
    owner: str


class CalibrationRegistry:
    """WP-4008: Persists calibration factors and curves for agents (G-GP-09)."""

    def __init__(self, session_dir: Path) -> None:
        self.session_dir = session_dir
        self.path = session_dir / "calibration_registry.json"

    def get_factor(self, agent: str) -> float:
        """Return the persisted calibration factor for an agent."""
        if not self.path.exists():
            return 1.0
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data.get(agent, {}).get("factor", 1.0)
        except Exception:
            return 1.0

    def update_agent(self, agent: str, factor: float, sample_size: int) -> None:
        """Persist a new calibration factor for an agent."""
        data = {}
        if self.path.exists():
            with contextlib.suppress(Exception):
                data = json.loads(self.path.read_text(encoding="utf-8"))
        data[agent] = {
            "factor": factor,
            "sample_size": sample_size,
            "updated_at_utc": datetime.now(UTC).isoformat(),
        }
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")


