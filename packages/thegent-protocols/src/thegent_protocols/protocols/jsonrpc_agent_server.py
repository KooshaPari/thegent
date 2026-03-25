"""In-memory JSON-RPC 2.0 agent server over stdio."""

# pyright: reportUnusedFunction = false

from __future__ import annotations

from json import JSONDecodeError as StdJSONDecodeError
import orjson as json
import sys
from dataclasses import dataclass, field
from typing import Any, TextIO

from thegent_core.utils.json_utils import json_loads
from thegent_sync.integrations.base import SerializableMixin


JSONRPC_VERSION = "2.0"

SUPPORTED_METHODS = {
    "approval/grant",
    "approval/reject",
    "config/read",
    "health/check",
    "session/list",
    "session/read",
    "session/resume",
    "session/start",
    "turn/cancel",
    "turn/submit",
}

TERMINAL_TURN_STATES = {"completed", "cancelled", "rejected"}


@dataclass(frozen=True)
class JsonRpcError(SerializableMixin):
    code: int
    message: str
    data: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Override to conditionally include data field."""
        payload: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.data is not None:
            payload["data"] = self.data
        return payload


@dataclass
class InMemoryJsonRpcState:
    session_counter: int = 0
    turn_counter: int = 0
    approval_counter: int = 0
    tool_call_counter: int = 0
    sessions: dict[str, dict[str, Any]] = field(default_factory=dict)
    turns: dict[str, dict[str, Any]] = field(default_factory=dict)
    approvals: dict[str, dict[str, Any]] = field(default_factory=dict)

    def next_session_id(self) -> str:
        self.session_counter += 1
        return f"session-{self.session_counter:04d}"

    def next_turn_id(self) -> str:
        self.turn_counter += 1
        return f"turn-{self.turn_counter:04d}"

    def next_approval_id(self) -> str:
        self.approval_counter += 1
        return f"approval-{self.approval_counter:04d}"

    def next_tool_call_id(self) -> str:
        self.tool_call_counter += 1
        return f"toolcall-{self.tool_call_counter:04d}"


SERVER_STATE = InMemoryJsonRpcState()


def _error_response(request_id: Any, error: JsonRpcError) -> dict[str, Any]:
    return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "error": error.to_dict()}


def _result_response(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": JSONRPC_VERSION, "id": request_id, "result": result}


def _notification(method: str, params: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": JSONRPC_VERSION, "method": method, "params": params}


def _method_not_found(method: Any) -> JsonRpcError:
    return JsonRpcError(-32601, f"Method not found: {method}", {"supported_methods": sorted(SUPPORTED_METHODS)})


def _invalid_params(reason: str) -> JsonRpcError:
    return JsonRpcError(-32602, "Invalid params", {"reason": reason})


def _is_valid_request_id(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, bool):
        return False
    return isinstance(value, (str, int, float))


def _normalized_non_empty_string(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    return cleaned


def _extract_params(request: dict[str, Any]) -> tuple[dict[str, Any], JsonRpcError | None]:
    params = request.get("params")
    if params is None:
        return {}, None
    if not isinstance(params, dict):
        return {}, _invalid_params("params_must_be_object")
    return params, None


def _serialize_session(session: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": session["id"],
        "status": session["status"],
        "created_index": session["created_index"],
        "turn_ids": list(session["turn_ids"]),
    }


def _serialize_turn(turn: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": turn["id"],
        "session_id": turn["session_id"],
        "status": turn["status"],
        "input": turn["input"],
        "approval_id": turn.get("approval_id"),
        "tool_call_id": turn.get("tool_call_id"),
    }


def _validate_request_envelope(request: dict[str, Any]) -> JsonRpcError | None:
    if request.get("jsonrpc") != JSONRPC_VERSION:
        return JsonRpcError(-32600, "Invalid Request", {"reason": "jsonrpc"})
    if "id" in request and not _is_valid_request_id(request["id"]):
        return JsonRpcError(-32600, "Invalid Request", {"reason": "id"})
    method = request.get("method")
    if not isinstance(method, str) or not method:
        return JsonRpcError(-32600, "Invalid Request", {"reason": "method"})
    if method not in SUPPORTED_METHODS:
        return _method_not_found(method)
    return None


def _require_session(
    request_id: Any, params: dict[str, Any]
) -> tuple[str | None, dict[str, Any] | None, dict[str, Any] | None]:
    session_id = _normalized_non_empty_string(params.get("session_id"))
    if session_id is None:
        return None, None, _error_response(request_id, _invalid_params("session_id_required"))
    session = SERVER_STATE.sessions.get(session_id)
    if session is None:
        return (
            session_id,
            None,
            _error_response(request_id, JsonRpcError(-32001, "Session not found", {"session_id": session_id})),
        )
    return session_id, session, None


def _require_turn(
    request_id: Any, params: dict[str, Any]
) -> tuple[str | None, dict[str, Any] | None, dict[str, Any] | None]:
    turn_id = _normalized_non_empty_string(params.get("turn_id"))
    if turn_id is None:
        return None, None, _error_response(request_id, _invalid_params("turn_id_required"))
    turn = SERVER_STATE.turns.get(turn_id)
    if turn is None:
        return turn_id, None, _error_response(request_id, JsonRpcError(-32002, "Turn not found", {"turn_id": turn_id}))
    return turn_id, turn, None


def _extract_required_approval_diff(
    request_id: Any, params: dict[str, Any]
) -> tuple[str | None, dict[str, Any] | None]:
    if "unified_diff" in params:
        raw_diff = params["unified_diff"]
    elif "diff" in params:
        raw_diff = params["diff"]
    else:
        return None, _error_response(request_id, _invalid_params("diff_required_when_requires_approval"))
    if not isinstance(raw_diff, str):
        return None, _error_response(request_id, _invalid_params("diff_must_be_string"))
    if not raw_diff.strip():
        return None, _error_response(request_id, _invalid_params("diff_must_be_non_empty_string"))
    return raw_diff, None


def _append_execution_notifications(
    notifications: list[dict[str, Any]], session_id: str, turn_id: str, user_input: str, tool_call_id: str
) -> None:
    notifications.append(
        _notification(
            "item/toolCall/started",
            {
                "session_id": session_id,
                "turn_id": turn_id,
                "tool_call_id": tool_call_id,
                "tool_name": "in_memory.echo",
            },
        )
    )
    notifications.append(
        _notification(
            "item/toolCall/completed",
            {
                "session_id": session_id,
                "turn_id": turn_id,
                "tool_call_id": tool_call_id,
                "output": f"echo:{user_input}",
            },
        )
    )
    notifications.append(
        _notification("turn/completed", {"session_id": session_id, "turn_id": turn_id, "status": "completed"})
    )


def _route_turn_cancel_method(method: str) -> str:
    if method != "turn/cancel":
        raise ValueError(f"Unsupported turn cancel method: {method}")
    return "cancel"


def _discover_turn_cancel_route(method: str) -> str:
    return _route_turn_cancel_method(method)


def _bind_turn_cancel_phases(route: str) -> dict[str, Any]:
    if route != "cancel":
        raise ValueError(f"Unsupported turn cancel route: {route}")
    return {
        "parse": _resolve_turn_cancel_context,
        "execute": _execute_turn_cancel,
        "project": _build_turn_cancel_projection_payload,
    }


def _parse_turn_cancel_with_binding(
    request_id: Any, params: dict[str, Any], binding: dict[str, Any]
) -> tuple[str | None, dict[str, Any] | None, dict[str, Any] | None]:
    parse_fn = binding["parse"]
    return parse_fn(request_id, params)


def _dispatch_turn_cancel_success(
    request_has_id: bool,
    request_id: Any,
    turn_id: str,
    turn: dict[str, Any],
    binding: dict[str, Any],
) -> dict[str, Any] | None:
    execute_fn = binding["execute"]
    project_fn = binding["project"]
    execute_fn(turn)
    if not request_has_id:
        return None
    payload = project_fn(turn)
    _validate_turn_cancel_projection_turn_id(turn_id, payload)
    return _result_response(request_id, payload)


def _dispatch_turn_cancel_recovery(request_has_id: bool, parse_error: dict[str, Any]) -> dict[str, Any] | None:
    if _should_suppress_turn_cancel_recovery_response(request_has_id, parse_error):
        return None
    return parse_error


def _extract_turn_cancel_recovery_error_code(parse_error: dict[str, Any]) -> int | None:
    code = parse_error.get("error", {}).get("code")
    if not isinstance(code, int):
        return None
    return code


def _should_suppress_turn_cancel_recovery_response(request_has_id: bool, parse_error: dict[str, Any]) -> bool:
    return not request_has_id and _extract_turn_cancel_recovery_error_code(parse_error) == -32003


def _build_turn_cancel_phase_plan(method: str, request_id: Any, params: dict[str, Any]) -> dict[str, Any]:
    route = _discover_turn_cancel_route(method)
    binding = _bind_turn_cancel_phases(route)
    turn_id, turn, parse_error = _parse_turn_cancel_with_binding(request_id, params, binding)
    return {
        "route": route,
        "binding": binding,
        "turn_id": turn_id,
        "turn": turn,
        "parse_error": parse_error,
    }


def _turn_cancel_should_emit_response(request_has_id: bool) -> bool:
    return request_has_id


def _resolve_turn_cancel_execution_target(plan: dict[str, Any]) -> tuple[str, dict[str, Any], dict[str, Any]]:
    turn_id = plan["turn_id"]
    turn = plan["turn"]
    binding = plan["binding"]
    if not isinstance(turn_id, str) or not isinstance(turn, dict):
        raise ValueError("Turn cancel execution target unresolved")
    return turn_id, turn, binding


def _apply_turn_cancel_execution(turn: dict[str, Any], binding: dict[str, Any]) -> None:
    execute_fn = binding["execute"]
    execute_fn(turn)


def _build_turn_cancel_success_response(
    request_has_id: bool,
    request_id: Any,
    turn_id: str,
    turn: dict[str, Any],
    binding: dict[str, Any],
) -> dict[str, Any] | None:
    if not _turn_cancel_should_emit_response(request_has_id):
        return None
    project_fn = binding["project"]
    payload = project_fn(turn)
    _validate_turn_cancel_projection_turn_id(turn_id, payload)
    return _result_response(request_id, payload)


def _build_turn_cancel_failure_response(request_has_id: bool, parse_error: dict[str, Any]) -> dict[str, Any] | None:
    return _dispatch_turn_cancel_recovery(request_has_id, parse_error)


def _resolve_turn_cancel_turn(
    request_id: Any, params: dict[str, Any]
) -> tuple[str | None, dict[str, Any] | None, dict[str, Any] | None]:
    turn_id, turn, turn_error = _require_turn(request_id, params)
    if turn_error is not None:
        return None, None, turn_error
    return turn_id, turn, None


def _validate_turn_cancel_turn_state(
    request_id: Any,
    turn_id: Any,
    turn: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    if turn is None and isinstance(turn_id, dict):
        turn = turn_id
        turn_id = request_id
        request_id = "compat"
    if turn is None or not isinstance(turn, dict):
        raise TypeError("Turn payload required")
    if turn.get("status") in TERMINAL_TURN_STATES:
        return _error_response(
            request_id,
            JsonRpcError(-32003, "Turn already terminal", {"turn_id": turn_id, "status": turn["status"]}),
        )
    return None


def _resolve_turn_cancel_context(
    request_id: Any, params: dict[str, Any]
) -> tuple[str | None, dict[str, Any] | None, dict[str, Any] | None]:
    turn_id, turn, turn_error = _resolve_turn_cancel_turn(request_id, params)
    if turn_error is not None:
        return None, None, turn_error
    assert turn_id is not None
    assert turn is not None
    terminal_error = _validate_turn_cancel_turn_state(request_id, turn_id, turn)
    if terminal_error is not None:
        return None, None, terminal_error
    return turn_id, turn, None


def _parse_turn_cancel_request(
    method: str, request_id: Any, params: dict[str, Any]
) -> tuple[str | None, dict[str, Any] | None, dict[str, Any] | None]:
    _route_turn_cancel_method(method)
    return _resolve_turn_cancel_context(request_id, params)


def _mark_turn_as_cancelled(turn: dict[str, Any]) -> None:
    turn["status"] = "cancelled"


def _resolve_turn_approval_id(turn: dict[str, Any]) -> str | None:
    approval_id = turn.get("approval_id")
    if not isinstance(approval_id, str):
        return None
    return approval_id


def _resolve_requested_approval(approval_id: str) -> dict[str, Any] | None:
    approval = SERVER_STATE.approvals.get(approval_id)
    if not isinstance(approval, dict):
        return None
    return approval


def _is_requested_approval_status(approval: dict[str, Any]) -> bool:
    return approval.get("status") == "requested"


def _mark_approval_as_cancelled(approval: dict[str, Any]) -> None:
    approval["status"] = "cancelled"


def _cancel_turn_requested_approval(turn: dict[str, Any]) -> None:
    approval_id = _resolve_turn_approval_id(turn)
    if approval_id is None:
        return
    approval = _resolve_requested_approval(approval_id)
    if approval is None:
        return
    if _is_requested_approval_status(approval):
        _mark_approval_as_cancelled(approval)


def _execute_turn_cancel(turn: dict[str, Any]) -> None:
    _mark_turn_as_cancelled(turn)
    _cancel_turn_requested_approval(turn)


def _execute_turn_cancel_resolution(method: str, turn: dict[str, Any]) -> None:
    _route_turn_cancel_method(method)
    _execute_turn_cancel(turn)


def _build_turn_cancel_projection_payload(turn: dict[str, Any]) -> dict[str, Any]:
    return {"turn": _build_turn_cancel_result(turn)}


def _build_turn_cancel_result(turn: dict[str, Any]) -> dict[str, Any]:
    return _serialize_turn(turn)


def _validate_turn_cancel_projection_turn_id(expected_turn_id: str, payload: dict[str, Any]) -> None:
    actual_turn_id = str(payload.get("turn", {}).get("id"))
    if actual_turn_id != expected_turn_id:
        raise ValueError(f"Turn id mismatch: expected={expected_turn_id} actual={actual_turn_id}")


def _project_turn_cancel_response(method: str, turn_id: str, turn: dict[str, Any]) -> dict[str, Any]:
    _route_turn_cancel_method(method)
    payload = _build_turn_cancel_projection_payload(turn)
    _validate_turn_cancel_projection_turn_id(turn_id, payload)
    return payload


def _handle_turn_cancel_request(
    method: str, request_has_id: bool, request_id: Any, params: dict[str, Any]
) -> dict[str, Any] | None:
    plan = _build_turn_cancel_phase_plan(method, request_id, params)
    parse_error = plan["parse_error"]
    if parse_error is not None:
        return _build_turn_cancel_failure_response(request_has_id, parse_error)
    turn_id, turn, binding = _resolve_turn_cancel_execution_target(plan)
    _apply_turn_cancel_execution(turn, binding)
    return _build_turn_cancel_success_response(request_has_id, request_id, turn_id, turn, binding)


def _handle_turn_cancel(
    request_has_id: bool, request_id: Any, params: dict[str, Any]
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    return _handle_turn_cancel_request("turn/cancel", request_has_id, request_id, params), []


def _parse_turn_cancel_turn_id(params: dict[str, Any]) -> tuple[str | None, JsonRpcError | None]:
    turn_id = _normalized_non_empty_string(params.get("turn_id"))
    if turn_id is None:
        return None, _invalid_params("turn_id_required")
    return turn_id, None


def _lookup_turn_for_cancel(turn_id: str) -> dict[str, Any] | None:
    return SERVER_STATE.turns.get(turn_id)


def _resolve_turn_cancel_target(
    session_id: Any, params: dict[str, Any]
) -> tuple[str | None, dict[str, Any] | None, dict[str, Any] | None]:
    # session_id retained for compatibility with earlier call signatures.
    turn_id = _normalized_non_empty_string(params.get("turn_id"))
    if turn_id is None:
        return None, None, _error_response(session_id, _invalid_params("turn_id_required"))
    turn = SERVER_STATE.turns.get(turn_id)
    if turn is None:
        return turn_id, None, _error_response(session_id, JsonRpcError(-32002, "Turn not found", {"turn_id": turn_id}))
    error = _validate_turn_cancel_turn_state(session_id, turn_id, turn)
    if error is not None:
        return None, None, error
    return turn_id, turn, None


def _mark_turn_cancelled(turn: dict[str, Any]) -> None:
    _mark_turn_as_cancelled(turn)


def _cancel_requested_approval_for_turn(turn: dict[str, Any]) -> None:
    _cancel_turn_requested_approval(turn)


def _build_turn_cancel_response(request_has_id: bool, request_id: Any, turn: dict[str, Any]) -> dict[str, Any] | None:
    if not request_has_id:
        return None
    return _result_response(request_id, _build_turn_cancel_projection_payload(turn))


def _discover_approval_resolution_route(method: str) -> str:
    if method == "approval/grant":
        return "grant"
    if method == "approval/reject":
        return "reject"
    raise ValueError(f"Unsupported approval resolution method: {method}")


def _bind_approval_resolution_phases(route: str) -> dict[str, Any]:
    if route not in {"grant", "reject"}:
        raise ValueError(f"Unsupported approval resolution route: {route}")
    return {
        "parse": _resolve_approval_resolution_context,
        "execute": _execute_approval_resolution,
        "project": _project_approval_resolution_result,
    }


def _resolve_approval_resolution_context(
    request_id: Any, params: dict[str, Any]
) -> tuple[str | None, dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None]:
    approval_id = _normalized_non_empty_string(params.get("approval_id"))
    if approval_id is None:
        return None, None, None, _error_response(request_id, _invalid_params("approval_id_required"))

    approval = SERVER_STATE.approvals.get(approval_id)
    if approval is None:
        return (
            approval_id,
            None,
            None,
            _error_response(
                request_id,
                JsonRpcError(-32005, "Approval not found", {"approval_id": approval_id}),
            ),
        )

    if approval["status"] != "requested":
        return (
            approval_id,
            approval,
            None,
            _error_response(
                request_id,
                JsonRpcError(
                    -32006,
                    "Approval already resolved",
                    {"approval_id": approval_id, "status": approval["status"]},
                ),
            ),
        )

    turn_id = approval["turn_id"]
    turn = SERVER_STATE.turns.get(turn_id)
    if turn is None:
        return (
            approval_id,
            approval,
            None,
            _error_response(request_id, JsonRpcError(-32002, "Turn not found", {"turn_id": turn_id})),
        )
    if turn["status"] in TERMINAL_TURN_STATES:
        return (
            approval_id,
            approval,
            turn,
            _error_response(
                request_id,
                JsonRpcError(-32003, "Turn already terminal", {"turn_id": turn_id, "status": turn["status"]}),
            ),
        )
    return approval_id, approval, turn, None


def _parse_approval_resolution_with_binding(
    request_id: Any, params: dict[str, Any], binding: dict[str, Any]
) -> tuple[str | None, dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None]:
    parse_fn = binding["parse"]
    return parse_fn(request_id, params)


def _execute_approval_resolution(
    route: str, approval: dict[str, Any], turn: dict[str, Any], notifications: list[dict[str, Any]]
) -> None:
    turn_id = approval["turn_id"]
    if route == "grant":
        approval["status"] = "granted"
        tool_call_id = SERVER_STATE.next_tool_call_id()
        turn["tool_call_id"] = tool_call_id
        _append_execution_notifications(notifications, turn["session_id"], turn_id, turn["input"], tool_call_id)
        turn["status"] = "completed"
        return
    if route == "reject":
        approval["status"] = "rejected"
        turn["status"] = "rejected"
        notifications.append(
            _notification(
                "turn/completed",
                {
                    "session_id": turn["session_id"],
                    "turn_id": turn_id,
                    "status": turn["status"],
                },
            )
        )
        return
    raise ValueError(f"Unsupported approval resolution route: {route}")


def _project_approval_resolution_result(
    approval_id: str, approval: dict[str, Any], turn: dict[str, Any]
) -> dict[str, Any]:
    if approval.get("id") != approval_id:
        raise ValueError(f"Approval id mismatch: expected={approval_id} actual={approval.get('id')}")
    return {
        "approval": {"id": approval_id, "status": approval["status"]},
        "turn": _serialize_turn(turn),
    }


def _dispatch_approval_resolution_success(
    request_has_id: bool,
    request_id: Any,
    approval_id: str,
    approval: dict[str, Any],
    turn: dict[str, Any],
    route: str,
    binding: dict[str, Any],
    notifications: list[dict[str, Any]],
) -> dict[str, Any] | None:
    execute_fn = binding["execute"]
    project_fn = binding["project"]
    execute_fn(route, approval, turn, notifications)
    if not request_has_id:
        return None
    payload = project_fn(approval_id, approval, turn)
    return _result_response(request_id, payload)


def _dispatch_approval_resolution_recovery(parse_error: dict[str, Any]) -> dict[str, Any]:
    return parse_error


def _build_approval_resolution_phase_plan(method: str, request_id: Any, params: dict[str, Any]) -> dict[str, Any]:
    route = _discover_approval_resolution_route(method)
    binding = _bind_approval_resolution_phases(route)
    approval_id, approval, turn, parse_error = _parse_approval_resolution_with_binding(request_id, params, binding)
    return {
        "route": route,
        "binding": binding,
        "approval_id": approval_id,
        "approval": approval,
        "turn": turn,
        "parse_error": parse_error,
    }


def _resolve_approval_resolution_parse_error(plan: dict[str, Any]) -> dict[str, Any] | None:
    parse_error = plan["parse_error"]
    if not isinstance(parse_error, dict):
        return None
    return parse_error


def _build_approval_resolution_parse_phase(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "parse_error": _resolve_approval_resolution_parse_error(plan),
        "approval_id": plan["approval_id"],
        "approval": plan["approval"],
        "turn": plan["turn"],
        "route": plan["route"],
        "binding": plan["binding"],
    }


def _build_approval_resolution_execution_phase(
    parse_phase: dict[str, Any],
) -> tuple[str, dict[str, Any], dict[str, Any], str, dict[str, Any]]:
    return _resolve_approval_resolution_execution_target(parse_phase)


def _approval_resolution_should_emit_response(request_has_id: bool) -> bool:
    return request_has_id


def _resolve_approval_resolution_execution_target(
    plan: dict[str, Any],
) -> tuple[str, dict[str, Any], dict[str, Any], str, dict[str, Any]]:
    approval_id = plan["approval_id"]
    approval = plan["approval"]
    turn = plan["turn"]
    route = plan["route"]
    binding = plan["binding"]
    if (
        not isinstance(approval_id, str)
        or not isinstance(approval, dict)
        or not isinstance(turn, dict)
        or not isinstance(route, str)
        or not isinstance(binding, dict)
    ):
        raise ValueError("Approval resolution execution target unresolved")
    return approval_id, approval, turn, route, binding


def _apply_approval_resolution_execution(
    route: str,
    approval: dict[str, Any],
    turn: dict[str, Any],
    binding: dict[str, Any],
    notifications: list[dict[str, Any]],
) -> None:
    execute_fn = binding["execute"]
    execute_fn(route, approval, turn, notifications)


def _apply_approval_resolution_projection(
    approval_id: str, approval: dict[str, Any], turn: dict[str, Any], binding: dict[str, Any]
) -> dict[str, Any]:
    project_fn = binding["project"]
    return project_fn(approval_id, approval, turn)


def _build_approval_resolution_success_response(
    request_has_id: bool,
    request_id: Any,
    approval_id: str,
    approval: dict[str, Any],
    turn: dict[str, Any],
    binding: dict[str, Any],
) -> dict[str, Any] | None:
    if not _approval_resolution_should_emit_response(request_has_id):
        return None
    payload = _apply_approval_resolution_projection(approval_id, approval, turn, binding)
    return _result_response(request_id, payload)


def _build_approval_resolution_failure_response(parse_error: dict[str, Any]) -> dict[str, Any]:
    return _dispatch_approval_resolution_recovery(parse_error)


def _handle_approval_resolution_request(
    method: str, request_has_id: bool, request_id: Any, params: dict[str, Any], notifications: list[dict[str, Any]]
) -> dict[str, Any] | None:
    plan = _build_approval_resolution_phase_plan(method, request_id, params)
    parse_phase = _build_approval_resolution_parse_phase(plan)
    parse_error = parse_phase["parse_error"]
    if parse_error is not None:
        return _build_approval_resolution_failure_response(parse_error)
    approval_id, approval, turn, route, binding = _build_approval_resolution_execution_phase(parse_phase)
    _apply_approval_resolution_execution(
        route,
        approval,
        turn,
        binding,
        notifications,
    )
    return _build_approval_resolution_success_response(request_has_id, request_id, approval_id, approval, turn, binding)


def _build_turn_submit_phase_plan(request_id: Any, params: dict[str, Any]) -> dict[str, Any]:
    session_id, session, session_error = _require_session(request_id, params)
    if session_error is not None:
        return {"parse_error": session_error}

    assert session_id is not None
    assert session is not None

    user_input = params.get("input", "")
    if not isinstance(user_input, str):
        return {"parse_error": _error_response(request_id, _invalid_params("input_must_be_string"))}

    if "requires_approval" in params and not isinstance(params["requires_approval"], bool):
        return {"parse_error": _error_response(request_id, _invalid_params("requires_approval_must_be_boolean"))}

    requires_approval = params.get("requires_approval", False)
    approval_diff: str | None = None
    if requires_approval:
        approval_diff, approval_diff_error = _extract_required_approval_diff(request_id, params)
        if approval_diff_error is not None:
            return {"parse_error": approval_diff_error}

    return {
        "parse_error": None,
        "session_id": session_id,
        "session": session,
        "user_input": user_input,
        "requires_approval": requires_approval,
        "approval_diff": approval_diff,
    }


def _resolve_turn_submit_parse_error(plan: dict[str, Any]) -> dict[str, Any] | None:
    parse_error = plan.get("parse_error")
    if not isinstance(parse_error, dict):
        return None
    return parse_error


def _build_turn_submit_parse_phase(plan: dict[str, Any]) -> dict[str, Any]:
    return {
        "parse_error": _resolve_turn_submit_parse_error(plan),
        "session_id": plan.get("session_id"),
        "session": plan.get("session"),
        "user_input": plan.get("user_input"),
        "requires_approval": plan.get("requires_approval"),
        "approval_diff": plan.get("approval_diff"),
    }


def _turn_submit_should_emit_response(request_has_id: bool) -> bool:
    return request_has_id


def _resolve_turn_submit_execution_target(
    plan: dict[str, Any],
) -> tuple[str, dict[str, Any], str, bool, str | None]:
    session_id = plan.get("session_id")
    session = plan.get("session")
    user_input = plan.get("user_input")
    requires_approval = plan.get("requires_approval")
    approval_diff = plan.get("approval_diff")
    if (
        not isinstance(session_id, str)
        or not isinstance(session, dict)
        or not isinstance(user_input, str)
        or not isinstance(requires_approval, bool)
        or (approval_diff is not None and not isinstance(approval_diff, str))
    ):
        raise ValueError("Turn submit execution target unresolved")
    return session_id, session, user_input, requires_approval, approval_diff


def _build_turn_submit_execution_phase(
    parse_phase: dict[str, Any],
) -> tuple[str, dict[str, Any], str, bool, str | None]:
    return _resolve_turn_submit_execution_target(parse_phase)


def _build_turn_submit_commit_phase(session_id: str, session: dict[str, Any], user_input: str) -> dict[str, Any]:
    turn_id, turn = _build_turn_submit_execution_plan(session_id, user_input)
    return {"turn_id": turn_id, "turn": turn, "session": session}


def _resolve_turn_submit_commit_target(
    commit_phase: dict[str, Any],
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    turn_id = commit_phase.get("turn_id")
    turn = commit_phase.get("turn")
    session = commit_phase.get("session")
    if not isinstance(turn_id, str) or not isinstance(turn, dict) or not isinstance(session, dict):
        raise ValueError("Turn submit commit target unresolved")
    return turn_id, turn, session


def _build_turn_submit_commit_resolution_phase(
    commit_phase: dict[str, Any],
) -> tuple[str, dict[str, Any], dict[str, Any]]:
    return _resolve_turn_submit_commit_target(commit_phase)


def _apply_turn_submit_started_notifications(
    notifications: list[dict[str, Any]], session_id: str, turn_id: str, user_input: str
) -> None:
    notifications.append(_notification("turn/started", {"session_id": session_id, "turn_id": turn_id}))
    notifications.append(
        _notification(
            "item/agentMessage/delta",
            {
                "session_id": session_id,
                "turn_id": turn_id,
                "delta": f"ack:{user_input}",
            },
        )
    )


def _execute_turn_submit_with_approval(
    session_id: str,
    turn_id: str,
    turn: dict[str, Any],
    approval_diff: str,
    notifications: list[dict[str, Any]],
) -> dict[str, Any]:
    approval_id = SERVER_STATE.next_approval_id()
    turn["status"] = "awaiting_approval"
    turn["approval_id"] = approval_id
    approval = {
        "id": approval_id,
        "turn_id": turn_id,
        "session_id": session_id,
        "status": "requested",
        "diff": approval_diff,
    }
    SERVER_STATE.approvals[approval_id] = approval
    notifications.append(
        _notification(
            "approval/requested",
            {
                "approval_id": approval_id,
                "session_id": session_id,
                "turn_id": turn_id,
                "diff": approval_diff,
            },
        )
    )
    return {"id": approval_id, "status": approval["status"], "diff": approval_diff}


def _execute_turn_submit_without_approval(
    session_id: str, turn_id: str, user_input: str, turn: dict[str, Any], notifications: list[dict[str, Any]]
) -> None:
    tool_call_id = SERVER_STATE.next_tool_call_id()
    turn["tool_call_id"] = tool_call_id
    _append_execution_notifications(notifications, session_id, turn_id, user_input, tool_call_id)
    turn["status"] = "completed"


def _build_turn_submit_execution_plan(session_id: str, user_input: str) -> tuple[str, dict[str, Any]]:
    turn_id = SERVER_STATE.next_turn_id()
    turn = {
        "id": turn_id,
        "session_id": session_id,
        "input": user_input,
        "status": "in_progress",
        "approval_id": None,
        "tool_call_id": None,
    }
    return turn_id, turn


def _commit_turn_submit_plan(turn_id: str, turn: dict[str, Any], session: dict[str, Any]) -> None:
    SERVER_STATE.turns[turn_id] = turn
    session["turn_ids"].append(turn_id)


def _resolve_turn_submit_approval_payload(
    session_id: str,
    turn_id: str,
    turn: dict[str, Any],
    approval_diff: str | None,
    notifications: list[dict[str, Any]],
) -> dict[str, Any]:
    if not isinstance(approval_diff, str):
        raise ValueError("Turn submit approval diff unresolved")
    return _execute_turn_submit_with_approval(session_id, turn_id, turn, approval_diff, notifications)


def _build_turn_submit_side_effects_phase(
    session_id: str,
    turn_id: str,
    turn: dict[str, Any],
    user_input: str,
    requires_approval: bool,
    approval_diff: str | None,
) -> dict[str, Any]:
    return {
        "session_id": session_id,
        "turn_id": turn_id,
        "turn": turn,
        "user_input": user_input,
        "requires_approval": requires_approval,
        "approval_diff": approval_diff,
    }


def _resolve_turn_submit_side_effects_target(
    side_effects_phase: dict[str, Any],
) -> tuple[str, str, dict[str, Any], str, bool, str | None]:
    session_id = side_effects_phase.get("session_id")
    turn_id = side_effects_phase.get("turn_id")
    turn = side_effects_phase.get("turn")
    user_input = side_effects_phase.get("user_input")
    requires_approval = side_effects_phase.get("requires_approval")
    approval_diff = side_effects_phase.get("approval_diff")
    if (
        not isinstance(session_id, str)
        or not isinstance(turn_id, str)
        or not isinstance(turn, dict)
        or not isinstance(user_input, str)
        or not isinstance(requires_approval, bool)
        or (approval_diff is not None and not isinstance(approval_diff, str))
    ):
        raise ValueError("Turn submit side-effects target unresolved")
    return session_id, turn_id, turn, user_input, requires_approval, approval_diff


def _build_turn_submit_side_effects_resolution_phase(
    side_effects_phase: dict[str, Any],
) -> tuple[str, str, dict[str, Any], str, bool, str | None]:
    return _resolve_turn_submit_side_effects_target(side_effects_phase)


def _resolve_turn_submit_completion(
    session_id: str, turn_id: str, user_input: str, turn: dict[str, Any], notifications: list[dict[str, Any]]
) -> None:
    _execute_turn_submit_without_approval(session_id, turn_id, user_input, turn, notifications)


def _apply_turn_submit_side_effects(
    session_id: str,
    turn_id: str,
    turn: dict[str, Any],
    user_input: str,
    requires_approval: bool,
    approval_diff: str | None,
    notifications: list[dict[str, Any]],
) -> dict[str, Any] | None:
    _apply_turn_submit_started_notifications(notifications, session_id, turn_id, user_input)
    if requires_approval:
        return _resolve_turn_submit_approval_payload(session_id, turn_id, turn, approval_diff, notifications)
    _resolve_turn_submit_completion(session_id, turn_id, user_input, turn, notifications)
    return None


def _build_turn_submit_result_payload(turn: dict[str, Any], approval_payload: dict[str, Any] | None) -> dict[str, Any]:
    result: dict[str, Any] = {"turn": _serialize_turn(turn)}
    if approval_payload is not None:
        result["approval"] = approval_payload
    return result


def _build_turn_submit_success_response(
    request_has_id: bool, request_id: Any, turn: dict[str, Any], approval_payload: dict[str, Any] | None
) -> dict[str, Any] | None:
    if not _turn_submit_should_emit_response(request_has_id):
        return None
    result = _build_turn_submit_result_payload(turn, approval_payload)
    return _result_response(request_id, result)


def _handle_turn_submit_parse_failure(parse_error: dict[str, Any]) -> dict[str, Any]:
    return parse_error


def _build_turn_submit_response_phase(
    request_has_id: bool, request_id: Any, turn: dict[str, Any], approval_payload: dict[str, Any] | None
) -> dict[str, Any]:
    return {
        "request_has_id": request_has_id,
        "request_id": request_id,
        "turn": turn,
        "approval_payload": approval_payload,
    }


def _extract_turn_submit_response_request_has_id(response_phase: dict[str, Any]) -> bool:
    request_has_id = response_phase.get("request_has_id")
    if not isinstance(request_has_id, bool):
        raise ValueError("Turn submit response target unresolved")
    return request_has_id


def _extract_turn_submit_response_request_id(response_phase: dict[str, Any], request_has_id: bool) -> Any:
    request_id = response_phase.get("request_id")
    if request_has_id and (request_id is None or not _is_valid_request_id(request_id)):
        raise ValueError("Turn submit response target unresolved")
    return request_id


def _extract_turn_submit_response_turn(response_phase: dict[str, Any]) -> dict[str, Any]:
    turn = response_phase.get("turn")
    if not isinstance(turn, dict):
        raise ValueError("Turn submit response target unresolved")
    return turn


def _extract_turn_submit_response_approval_payload(
    response_phase: dict[str, Any],
) -> dict[str, Any] | None:
    approval_payload = response_phase.get("approval_payload")
    if approval_payload is not None and not isinstance(approval_payload, dict):
        raise ValueError("Turn submit response target unresolved")
    return approval_payload


def _extract_turn_submit_response_approval_id(approval_payload: dict[str, Any] | None) -> str | None:
    if approval_payload is None:
        return None
    return _extract_turn_submit_approval_payload_id(approval_payload)


def _extract_turn_submit_response_approval_status(approval_payload: dict[str, Any] | None) -> str | None:
    if approval_payload is None:
        return None
    return _extract_turn_submit_approval_payload_status(approval_payload)


def _extract_turn_submit_response_approval_diff(approval_payload: dict[str, Any] | None) -> str | None:
    if approval_payload is None:
        return None
    return _extract_turn_submit_approval_payload_diff(approval_payload)


def _resolve_turn_submit_response_approval_fields(
    approval_payload: dict[str, Any] | None,
) -> tuple[str | None, str | None, str | None]:
    approval_id = _extract_turn_submit_response_approval_id(approval_payload)
    approval_status = _extract_turn_submit_response_approval_status(approval_payload)
    approval_diff = _extract_turn_submit_response_approval_diff(approval_payload)
    return approval_id, approval_status, approval_diff


def _extract_turn_submit_approval_payload_id(approval_payload: dict[str, Any]) -> str:
    approval_id = approval_payload.get("id")
    if not isinstance(approval_id, str) or not approval_id:
        raise ValueError("Turn submit response target unresolved")
    return approval_id


def _extract_turn_submit_approval_payload_status(approval_payload: dict[str, Any]) -> str:
    approval_status = approval_payload.get("status")
    if not isinstance(approval_status, str) or not approval_status:
        raise ValueError("Turn submit response target unresolved")
    return approval_status


def _extract_turn_submit_approval_payload_diff(approval_payload: dict[str, Any]) -> str | None:
    approval_diff = approval_payload.get("diff")
    if approval_diff is not None and not isinstance(approval_diff, str):
        raise ValueError("Turn submit response target unresolved")
    return approval_diff


def _validate_turn_submit_approval_payload(approval_payload: dict[str, Any]) -> None:
    _extract_turn_submit_approval_payload_id(approval_payload)
    _extract_turn_submit_approval_payload_status(approval_payload)
    _extract_turn_submit_approval_payload_diff(approval_payload)


def _resolve_turn_submit_response_target(
    response_phase: dict[str, Any],
) -> tuple[bool, Any, dict[str, Any], dict[str, Any] | None]:
    request_has_id = _extract_turn_submit_response_request_has_id(response_phase)
    request_id = _extract_turn_submit_response_request_id(response_phase, request_has_id)
    turn = _extract_turn_submit_response_turn(response_phase)
    approval_payload = _extract_turn_submit_response_approval_payload(response_phase)
    if isinstance(approval_payload, dict):
        _resolve_turn_submit_response_approval_fields(approval_payload)
    return request_has_id, request_id, turn, approval_payload


def _build_turn_submit_response_resolution_phase(
    response_phase: dict[str, Any],
) -> tuple[bool, Any, dict[str, Any], dict[str, Any] | None]:
    return _resolve_turn_submit_response_target(response_phase)


def _handle_turn_submit_request(
    request_has_id: bool, request_id: Any, params: dict[str, Any], notifications: list[dict[str, Any]]
) -> dict[str, Any] | None:
    plan = _build_turn_submit_phase_plan(request_id, params)
    parse_phase = _build_turn_submit_parse_phase(plan)
    parse_error = parse_phase["parse_error"]
    if parse_error is not None:
        return _handle_turn_submit_parse_failure(parse_error)
    session_id, session, user_input, requires_approval, approval_diff = _build_turn_submit_execution_phase(parse_phase)
    commit_phase = _build_turn_submit_commit_phase(session_id, session, user_input)
    turn_id, turn, _planned_session = _build_turn_submit_commit_resolution_phase(commit_phase)
    side_effects_phase = _build_turn_submit_side_effects_phase(
        session_id, turn_id, turn, user_input, requires_approval, approval_diff
    )
    (
        side_effects_session_id,
        side_effects_turn_id,
        side_effects_turn,
        side_effects_user_input,
        side_effects_requires_approval,
        side_effects_approval_diff,
    ) = _build_turn_submit_side_effects_resolution_phase(side_effects_phase)
    _commit_turn_submit_plan(turn_id, turn, session)
    approval_payload = _apply_turn_submit_side_effects(
        side_effects_session_id,
        side_effects_turn_id,
        side_effects_turn,
        side_effects_user_input,
        side_effects_requires_approval,
        side_effects_approval_diff,
        notifications,
    )
    response_phase = _build_turn_submit_response_phase(request_has_id, request_id, side_effects_turn, approval_payload)
    response_request_has_id, response_request_id, response_turn, response_approval_payload = (
        _build_turn_submit_response_resolution_phase(response_phase)
    )
    return _build_turn_submit_success_response(
        response_request_has_id, response_request_id, response_turn, response_approval_payload
    )


def _build_health_check_result() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "thegent-agent-server",
        "transport": "stdio",
    }


def _build_config_read_result() -> dict[str, Any]:
    return {
        "server": "thegent-agent-server",
        "transport": "stdio",
        "supported_methods": sorted(SUPPORTED_METHODS),
    }


def _maybe_result_response(request_has_id: bool, request_id: Any, result: dict[str, Any]) -> dict[str, Any] | None:
    if not request_has_id:
        return None
    return _result_response(request_id, result)


def _dispatch_static_method_response(
    method: str, request_has_id: bool, request_id: Any
) -> tuple[bool, dict[str, Any] | None]:
    if method == "health/check":
        return True, _maybe_result_response(request_has_id, request_id, _build_health_check_result())
    if method == "config/read":
        return True, _maybe_result_response(request_has_id, request_id, _build_config_read_result())
    return False, None


def _build_session_start_record() -> dict[str, Any]:
    session_id = SERVER_STATE.next_session_id()
    session = {
        "id": session_id,
        "status": "active",
        "created_index": SERVER_STATE.session_counter,
        "turn_ids": [],
    }
    SERVER_STATE.sessions[session_id] = session
    return session


def _resume_existing_session(session: dict[str, Any]) -> None:
    session["status"] = "active"


def _list_sessions_sorted() -> list[dict[str, Any]]:
    return [
        _serialize_session(session)
        for session in sorted(SERVER_STATE.sessions.values(), key=lambda item: item["created_index"])
    ]


def _read_session_turns(session: dict[str, Any]) -> list[dict[str, Any]]:
    return [_serialize_turn(SERVER_STATE.turns[turn_id]) for turn_id in session["turn_ids"]]


def _dispatch_session_method_response(
    method: str,
    request_has_id: bool,
    request_id: Any,
    params: dict[str, Any],
) -> tuple[bool, dict[str, Any] | None]:
    if method == "session/start":
        session = _build_session_start_record()
        return True, _maybe_result_response(request_has_id, request_id, {"session": _serialize_session(session)})

    if method == "session/resume":
        _session_id, session, session_error = _require_session(request_id, params)
        if session_error is not None:
            return True, session_error
        assert session is not None
        _resume_existing_session(session)
        return True, _maybe_result_response(request_has_id, request_id, {"session": _serialize_session(session)})

    if method == "session/list":
        return True, _maybe_result_response(request_has_id, request_id, {"sessions": _list_sessions_sorted()})

    if method == "session/read":
        _session_id, session, session_error = _require_session(request_id, params)
        if session_error is not None:
            return True, session_error
        assert session is not None
        turns = _read_session_turns(session)
        return True, _maybe_result_response(
            request_has_id, request_id, {"session": _serialize_session(session), "turns": turns}
        )

    return False, None


def _dispatch_turn_or_approval_method(
    method: str,
    request_has_id: bool,
    request_id: Any,
    params: dict[str, Any],
    notifications: list[dict[str, Any]],
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]] | None:
    if method == "turn/submit":
        return _handle_turn_submit_request(request_has_id, request_id, params, notifications), notifications
    if method == "turn/cancel":
        return _handle_turn_cancel(request_has_id, request_id, params)
    if method in {"approval/grant", "approval/reject"}:
        return (
            _handle_approval_resolution_request(method, request_has_id, request_id, params, notifications),
            notifications,
        )
    return None


def _dispatch_parsed_request(request: dict[str, Any]) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    envelope_error = _validate_request_envelope(request)
    if envelope_error is not None:
        request_id = request.get("id")
        if envelope_error.data and envelope_error.data.get("reason") == "id":
            request_id = None
        return _error_response(request_id, envelope_error), []

    method = str(request.get("method"))

    params, params_error = _extract_params(request)
    if params_error is not None:
        return _error_response(request.get("id"), params_error), []

    request_has_id = "id" in request
    request_id = request.get("id")
    notifications: list[dict[str, Any]] = []

    static_handled, static_response = _dispatch_static_method_response(method, request_has_id, request_id)
    if static_handled:
        return static_response, notifications

    session_handled, session_response = _dispatch_session_method_response(method, request_has_id, request_id, params)
    if session_handled:
        return session_response, notifications

    turn_or_approval_response = _dispatch_turn_or_approval_method(
        method, request_has_id, request_id, params, notifications
    )
    if turn_or_approval_response is not None:
        return turn_or_approval_response

    return _error_response(request_id, _method_not_found(method)), notifications


def process_jsonrpc_line_full(raw_line: str) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    """Parse and fully process a single JSONL request, including notifications."""
    if not raw_line.strip():
        return None, []
    try:
        payload = json_loads(raw_line)
    except (json.JSONDecodeError, StdJSONDecodeError) as exc:
        return _error_response(None, JsonRpcError(-32700, "Parse error", {"detail": str(exc)})), []

    if not isinstance(payload, dict):
        return _error_response(None, JsonRpcError(-32600, "Invalid Request", {"reason": "not_object"})), []

    return _dispatch_parsed_request(payload)


def process_jsonrpc_line(raw_line: str) -> dict[str, Any] | None:
    """Parse a single JSONL request and return response payload."""
    response, _notifications = process_jsonrpc_line_full(raw_line)
    return response


def serve_stdio(in_stream: TextIO | None = None, out_stream: TextIO | None = None) -> int:
    """Run the daemon in newline-delimited JSON-RPC mode over stdio."""
    src = in_stream or sys.stdin
    sink = out_stream or sys.stdout

    while True:
        raw = src.readline()
        if raw == "":
            return 0

        response, notifications = process_jsonrpc_line_full(raw)
        if response is not None:
            sink.write(json.dumps(response).decode() + "\n")
        for notification in notifications:
            sink.write(json.dumps(notification).decode() + "\n")

        if response is not None or notifications:
            sink.flush()


def main() -> int:
    return serve_stdio()


if __name__ == "__main__":
    raise SystemExit(main())
