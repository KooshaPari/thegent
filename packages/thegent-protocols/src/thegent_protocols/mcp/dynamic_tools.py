"""WL-105 dynamic per-session tool registry primitives."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from math import isfinite
import time
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class DynamicToolSpec:
    """Client-registered tool definition bound to a session."""

    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass(frozen=True)
class PendingDynamicToolCall:
    """In-flight dynamic tool call awaiting client response."""

    call_id: str
    session_id: str
    name: str
    arguments: dict[str, Any]
    timeout_seconds: float
    requested_at_utc: str
    expires_at_utc: str
    _expires_at_monotonic: float


@dataclass(frozen=True)
class DynamicToolCallResult:
    """Client-provided output for a prior dynamic tool call."""

    call_id: str
    output: Any
    success: bool
    error: Any = None


class DynamicToolRegistry:
    """Per-session dynamic tool registration and call lifecycle state."""

    def __init__(self, *, default_timeout_seconds: float = 30.0) -> None:
        if not isfinite(default_timeout_seconds) or default_timeout_seconds <= 0:
            raise ValueError("default_timeout_seconds must be > 0")
        self._tools_by_session: dict[str, dict[str, DynamicToolSpec]] = {}
        self._pending_calls: dict[str, PendingDynamicToolCall] = {}
        self._default_timeout_seconds = float(default_timeout_seconds)

    def _resolve_timeout_seconds(self, timeout_seconds: float | None) -> float:
        if timeout_seconds is None:
            return self._default_timeout_seconds
        if not isfinite(timeout_seconds) or timeout_seconds <= 0:
            raise ValueError("dynamic tool timeout_seconds must be > 0")
        return float(timeout_seconds)

    @staticmethod
    def _require_non_empty(value: Any, field_name: str) -> str:
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(f"{field_name} must be non-empty")
        return cleaned

    def _is_expired(self, call: PendingDynamicToolCall) -> bool:
        return time.monotonic() >= call._expires_at_monotonic

    def register_dynamic_tool(self, session_id: str, tool_spec: DynamicToolSpec) -> DynamicToolSpec:
        cleaned_session_id = self._require_non_empty(session_id, "session_id")
        cleaned_name = self._require_non_empty(tool_spec.name, "tool_spec.name")
        cleaned_description = self._require_non_empty(tool_spec.description, "tool_spec.description")
        if not isinstance(tool_spec.input_schema, dict):
            raise ValueError("tool_spec.input_schema must be a JSON schema object")

        normalized_spec = DynamicToolSpec(
            name=cleaned_name,
            description=cleaned_description,
            input_schema=tool_spec.input_schema,
        )
        session_tools = self._tools_by_session.setdefault(cleaned_session_id, {})
        if normalized_spec.name in session_tools:
            raise ValueError(f"dynamic tool already registered: {normalized_spec.name}")
        session_tools[normalized_spec.name] = normalized_spec
        return normalized_spec

    def list_dynamic_tools(self, session_id: str) -> list[DynamicToolSpec]:
        cleaned_session_id = self._require_non_empty(session_id, "session_id")
        return list(self._tools_by_session.get(cleaned_session_id, {}).values())

    def create_tool_call(
        self,
        session_id: str,
        name: str,
        arguments: dict[str, Any],
        timeout_seconds: float | None = None,
    ) -> PendingDynamicToolCall:
        cleaned_session_id = self._require_non_empty(session_id, "session_id")
        cleaned_name = self._require_non_empty(name, "name")
        if not isinstance(arguments, dict):
            raise ValueError("arguments must be a JSON object")
        session_tools = self._tools_by_session.get(cleaned_session_id, {})
        if cleaned_name not in session_tools:
            raise KeyError(f"dynamic tool not registered for session: {cleaned_name}")
        resolved_timeout = self._resolve_timeout_seconds(timeout_seconds)
        now_utc = datetime.now(UTC)
        now_monotonic = time.monotonic()
        call = PendingDynamicToolCall(
            call_id=f"dyn-call-{uuid4().hex}",
            session_id=cleaned_session_id,
            name=cleaned_name,
            arguments=arguments,
            timeout_seconds=resolved_timeout,
            requested_at_utc=now_utc.isoformat(),
            expires_at_utc=(now_utc + timedelta(seconds=resolved_timeout)).isoformat(),
            _expires_at_monotonic=now_monotonic + resolved_timeout,
        )
        self._pending_calls[call.call_id] = call
        return call

    def pending_calls_for_session(self, session_id: str) -> list[PendingDynamicToolCall]:
        cleaned_session_id = self._require_non_empty(session_id, "session_id")
        session_calls: list[PendingDynamicToolCall] = []
        for call_id, call in list(self._pending_calls.items()):
            if call.session_id != cleaned_session_id:
                continue
            if self._is_expired(call):
                self._pending_calls.pop(call_id, None)
                continue
            session_calls.append(call)
        return session_calls

    def get_pending_call(self, call_id: str) -> PendingDynamicToolCall:
        if call_id not in self._pending_calls:
            raise KeyError(f"unknown dynamic call id: {call_id}")
        call = self._pending_calls[call_id]
        if self._is_expired(call):
            self._pending_calls.pop(call_id, None)
            raise TimeoutError(f"dynamic tool call expired: {call_id}")
        return call

    def resolve_tool_call(self, call_id: str, output: Any, success: bool, error: Any = None) -> DynamicToolCallResult:
        if not isinstance(success, bool):
            raise ValueError("success must be a boolean")
        self.get_pending_call(call_id)
        self._pending_calls.pop(call_id, None)
        return DynamicToolCallResult(call_id=call_id, output=output, success=success, error=error)

    def resolve_tool_call_for_session(
        self,
        session_id: str,
        call_id: str,
        output: Any,
        success: bool,
        error: Any = None,
    ) -> DynamicToolCallResult:
        cleaned_session_id = self._require_non_empty(session_id, "session_id")
        call = self.get_pending_call(call_id)
        if call.session_id != cleaned_session_id:
            raise KeyError(f"dynamic call does not belong to session: {call_id}")
        return self.resolve_tool_call(call_id, output, success, error=error)

    def clear_session(self, session_id: str) -> None:
        cleaned_session_id = self._require_non_empty(session_id, "session_id")
        self._tools_by_session.pop(cleaned_session_id, None)
        for call_id, call in list(self._pending_calls.items()):
            if call.session_id == cleaned_session_id:
                self._pending_calls.pop(call_id, None)

    @staticmethod
    def tool_call_requested_event(call: PendingDynamicToolCall) -> dict[str, Any]:
        return {
            "event": "tool_call_requested",
            "callId": call.call_id,
            "sessionId": call.session_id,
            "name": call.name,
            "arguments": call.arguments,
            "timeoutSeconds": call.timeout_seconds,
            "requestedAt": call.requested_at_utc,
            "expiresAt": call.expires_at_utc,
        }

    @staticmethod
    def tool_call_completed_event(result: DynamicToolCallResult) -> dict[str, Any]:
        payload = {
            "event": "tool_call_completed",
            "callId": result.call_id,
            "output": result.output,
            "success": result.success,
        }
        if result.error is not None:
            payload["error"] = result.error
        return payload
