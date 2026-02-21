"""Factory helpers for execution registry event payloads."""

from datetime import UTC, datetime
from typing import Any


def build_schema_marker_event(schema_version: int) -> dict[str, Any]:
    """Create the schema marker event payload."""
    return {
        "event": "schema_version",
        "version": schema_version,
        "timestamp": datetime.now(UTC).isoformat(),
    }


def build_finish_event(
    run_id: str,
    exit_code: int,
    status: str,
    ended_at_utc: str,
    duration_s: float,
    error_class: str | None,
    prev_hash: str | None,
    cost_usd: float | None = None,
    event_details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a run-finish event payload."""
    event: dict[str, Any] = {
        "run_id": run_id,
        "event": "finish",
        "exit_code": exit_code,
        "status": status,
        "ended_at_utc": ended_at_utc,
        "duration_s": duration_s,
        "error_class": error_class,
        "timestamp": ended_at_utc,
        "prev_hash": prev_hash,
    }
    if cost_usd is not None:
        event["cost_usd"] = cost_usd
    if event_details:
        event.update(event_details)
    return event


def build_feedback_event(
    run_id: str,
    score: float,
    note: str | None,
    prev_hash: str | None,
) -> dict[str, Any]:
    """Create a run-feedback event payload."""
    timestamp = datetime.now(UTC).isoformat()
    return {
        "run_id": run_id,
        "event": "feedback",
        "feedback_score": score,
        "feedback_note": note,
        "timestamp": timestamp,
        "prev_hash": prev_hash,
    }


def build_pause_event(
    run_id: str,
    reason: str,
    continuity_snapshot: dict[str, Any] | None,
    prev_hash: str | None,
) -> dict[str, Any]:
    """Create a run-pause event payload."""
    timestamp = datetime.now(UTC).isoformat()
    return {
        "run_id": run_id,
        "event": "pause",
        "reason": reason,
        "continuity_snapshot": continuity_snapshot or {},
        "timestamp": timestamp,
        "prev_hash": prev_hash,
    }


def build_resume_event(run_id: str, prev_hash: str | None) -> dict[str, Any]:
    """Create a run-resume event payload."""
    timestamp = datetime.now(UTC).isoformat()
    return {
        "run_id": run_id,
        "event": "resume",
        "timestamp": timestamp,
        "prev_hash": prev_hash,
    }
