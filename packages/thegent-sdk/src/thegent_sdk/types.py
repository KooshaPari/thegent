from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RunResult:
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool = False
    context_tokens_used: int | None = None
    context_window_max: int | None = None
    context_usage_ratio: float | None = None


@dataclass(frozen=True)
class SessionInfo:
    session_id: str
    status: str
    run_id: str | None = None
    correlation_id: str | None = None
    model: str | None = None
    owner: str | None = None
    started_at: str | None = None
    prompt_preview: str | None = None
    source: str | None = None
    interactivity: str | None = None
    attach_target: dict[str, Any] | None = None
    pid: int | None = None
    agent: str | None = None


@dataclass(frozen=True)
class StreamEvent:
    type: str
    payload: dict[str, Any]


def parse_run_result(payload: dict[str, Any]) -> RunResult:
    return RunResult(
        exit_code=int(payload.get("exit_code", 0)),
        stdout=str(payload.get("stdout", "")),
        stderr=str(payload.get("stderr", "")),
        timed_out=bool(payload.get("timed_out", False)),
        context_tokens_used=(
            int(payload["context_tokens_used"]) if payload.get("context_tokens_used") is not None else None
        ),
        context_window_max=int(payload["context_window_max"]) if payload.get("context_window_max") is not None else None,
        context_usage_ratio=(
            float(payload["context_usage_ratio"]) if payload.get("context_usage_ratio") is not None else None
        ),
    )


def parse_session_info(payload: dict[str, Any]) -> SessionInfo:
    session_id = str(
        payload.get("session_id") or payload.get("id") or payload.get("correlation_id") or payload.get("run_id") or ""
    )
    pid = payload.get("pid")
    return SessionInfo(
        session_id=session_id,
        status=str(payload.get("status", "")),
        run_id=(str(payload["run_id"]) if payload.get("run_id") is not None else None),
        correlation_id=(str(payload["correlation_id"]) if payload.get("correlation_id") is not None else None),
        model=(str(payload["model"]) if payload.get("model") is not None else None),
        owner=(str(payload["owner"]) if payload.get("owner") is not None else None),
        started_at=(
            str(payload["started_at"])
            if payload.get("started_at") is not None
            else (str(payload["started_at_utc"]) if payload.get("started_at_utc") is not None else None)
        ),
        prompt_preview=(str(payload["prompt_preview"]) if payload.get("prompt_preview") is not None else None),
        source=(str(payload["source"]) if payload.get("source") is not None else None),
        interactivity=(str(payload["interactivity"]) if payload.get("interactivity") is not None else None),
        attach_target=(payload.get("attach_target") if isinstance(payload.get("attach_target"), dict) else None),
        pid=(int(pid) if pid is not None else None),
        agent=(str(payload["agent"]) if payload.get("agent") is not None else None),
    )


def parse_stream_event(payload: dict[str, Any]) -> StreamEvent:
    event_type = str(payload.get("type", "")).strip() or "event"
    return StreamEvent(type=event_type, payload=payload)
