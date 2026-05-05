"""JSON-RPC agent server protocol."""
from __future__ import annotations
from typing import Any
import time as _time


SUPPORTED_METHODS = [
    "session/start",
    "session/list",
    "session/resume",
    "session/read",
    "turn/submit",
    "turn/cancel",
    "approval/grant",
    "approval/reject",
    "health/check",
    "config/read",
]


class JsonRpcError:
    """JSON-RPC error class."""
    def __init__(self, code: int, message: str, data: dict[str, Any] | None = None) -> None:
        self.code = code
        self.message = message
        self.data = data

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.data is not None:
            result["data"] = self.data
        return result


class _ServerState:
    """Server state for tracking sessions, turns, etc."""

    def __init__(self) -> None:
        self.session_counter = 0
        self.turn_counter = 0
        self.approval_counter = 0
        self.tool_call_counter = 0
        self.sessions: dict[str, Any] = {}
        self.turns: dict[str, Any] = {}
        self.approvals: dict[str, Any] = {}


class _WorkflowState:
    """Workflow state for tracking workflows."""

    def __init__(self) -> None:
        self.workflow_counter = 0
        self.workflows: dict[str, Any] = {}


class _SessionState:
    """Session state for tracking session details."""

    def __init__(self) -> None:
        self.turn_counter = 0
        self.turns: dict[str, Any] = {}


# Module-level state singletons
SERVER_STATE = _ServerState()
WORKFLOW_STATE = _WorkflowState()
SESSION_STATE = _SessionState()


def _reset_state() -> None:
    """Reset all server state."""
    SERVER_STATE.session_counter = 0
    SERVER_STATE.turn_counter = 0
    SERVER_STATE.approval_counter = 0
    SERVER_STATE.tool_call_counter = 0
    SERVER_STATE.sessions.clear()
    SERVER_STATE.turns.clear()
    SERVER_STATE.approvals.clear()
    WORKFLOW_STATE.workflow_counter = 0
    WORKFLOW_STATE.workflows.clear()
    SESSION_STATE.turn_counter = 0
    SESSION_STATE.turns.clear()


class InMemoryJsonRpcState:
    """In-memory state for JSON-RPC server."""

    def __init__(self) -> None:
        self.session_counter = 0
        self.turn_counter = 0
        self.approval_counter = 0
        self.tool_call_counter = 0
        self.sessions: dict[str, Any] = {}
        self.turns: dict[str, Any] = {}
        self.approvals: dict[str, Any] = {}


class NotificationContext:
    """Context for notification handling."""
    def __init__(self, method: str, params: dict[str, Any]) -> None:
        self.method = method
        self.params = params


async def serve_stdio() -> None:
    """Serve JSON-RPC over stdio."""
    import sys
    for line in sys.stdin:
        line = line.strip()
        if line:
            result = process_jsonrpc_line(line)
            if result:
                print(result)


def _error_response(request_id: str | int | None, error: JsonRpcError) -> dict[str, Any]:
    """Build an error response."""
    return {"jsonrpc": "2.0", "id": request_id, "error": error.to_dict()}


def _build_session_start_record() -> dict[str, Any]:
    """Build a new session start record."""
    SERVER_STATE.session_counter += 1
    session_id = f"session-{SERVER_STATE.session_counter}"
    record = {
        "id": session_id,
        "created_at": _time.time(),
        "turn_ids": [],
    }
    SERVER_STATE.sessions[session_id] = record
    return record


def _handle_session_start(request_id: str | int) -> dict[str, Any]:
    """Handle session/start request."""
    SERVER_STATE.session_counter += 1
    session_id = f"session-{SERVER_STATE.session_counter}"
    session = {
        "id": session_id,
        "status": "active",
        "created_index": SERVER_STATE.session_counter,
        "turn_ids": [],
    }
    SERVER_STATE.sessions[session_id] = session
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"session": session},
    }

def _handle_health_check(request_id: str | int) -> dict[str, Any]:
    """Handle health/check method."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"status": "ok", "timestamp": _time.time(), "service": "thegent-agent-server", "transport": "stdio"},
    }


def _handle_session_list(request_id: str | int) -> dict[str, Any]:
    """Handle session/list method."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"sessions": list(SERVER_STATE.sessions.values())},
    }


def _handle_session_resume(request_id: str | int, session_id: str) -> dict[str, Any]:
    """Handle session/resume method."""
    session = SERVER_STATE.sessions.get(session_id)
    if not session:
        return _error_response(request_id, JsonRpcError(-32001, "Session not found"))
    session["status"] = "active"
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"session": session},
    }


def _handle_session_read(request_id: str | int, params: dict[str, Any]) -> dict[str, Any]:
    """Handle session/read method."""
    session_id = params.get("session_id")
    if not session_id:
        return _error_response(request_id, JsonRpcError(-32602, "session_id required", {"reason": "session_id_required"}))
    if session_id not in SERVER_STATE.sessions:
        return _error_response(request_id, JsonRpcError(-32002, "session not found", {"reason": "session_not_found"}))

    session = SERVER_STATE.sessions[session_id]
    turns = [{"id": tid, "status": SERVER_STATE.turns.get(tid, {}).get("status", "unknown")}
             for tid in session.get("turn_ids", [])]

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "session": {"id": session_id, "status": session.get("status", "active")},
            "turns": turns,
        },
    }


def _handle_turn_submit_request(
    request_id: str | int,
    session_id: str,
    input_text: str,
    requires_approval: bool = False,
    unified_diff: str | None = None,
) -> dict[str, Any]:
    """Handle turn/submit request."""
    session = SERVER_STATE.sessions.get(session_id)
    if not session:
        return _error_response(request_id, JsonRpcError(-32002, "Session not found"))

    SERVER_STATE.turn_counter += 1
    turn_id = f"turn-{SERVER_STATE.turn_counter}"

    turn: dict[str, Any] = {
        "id": turn_id,
        "session_id": session_id,
        "status": "in_progress",
        "input": input_text,
        "created_index": SERVER_STATE.turn_counter,
        "approval_id": None,
        "tool_call_id": None,
    }

    if requires_approval:
        SERVER_STATE.approval_counter += 1
        approval_id = f"approval-{SERVER_STATE.approval_counter:04d}"
        approval: dict[str, Any] = {
            "id": approval_id,
            "turn_id": turn_id,
            "status": "pending",
            "unified_diff": unified_diff or "",
        }
        SERVER_STATE.approvals[approval_id] = approval
        turn["status"] = "awaiting_approval"
        turn["approval_id"] = approval_id
    else:
        SERVER_STATE.tool_call_counter += 1
        tool_call_id = f"tool-call-{SERVER_STATE.tool_call_counter:04d}"
        turn["status"] = "completed"
        turn["tool_call_id"] = tool_call_id

    SERVER_STATE.turns[turn_id] = turn
    session["turn_ids"].append(turn_id)

    result: dict[str, Any] = {"turn": turn}
    if requires_approval:
        result["approval_id"] = approval_id

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result,
    }


def _build_turn_submit_execution_plan(session_id: str, input_text: str) -> tuple[str, dict[str, Any]]:
    """Build turn submit execution plan."""
    session = SERVER_STATE.sessions.get(session_id)
    if not session:
        # Create session if it doesn't exist
        SERVER_STATE.session_counter += 1
        session_id = f"session-{SERVER_STATE.session_counter}"
        session = {"id": session_id, "status": "active", "turn_ids": []}
        SERVER_STATE.sessions[session_id] = session
    SERVER_STATE.turn_counter += 1
    turn_id = f"turn-{SERVER_STATE.turn_counter}"
    turn = {
        "id": turn_id,
        "session_id": session_id,
        "status": "in_progress",
        "input": input_text,
        "created_index": SERVER_STATE.turn_counter,
        "approval_id": None,
        "tool_call_id": None,
    }
    SERVER_STATE.turns[turn_id] = turn
    return turn_id, turn


def _commit_turn_submit_plan(turn_id: str, turn: dict[str, Any], session: dict[str, Any]) -> None:
    """Commit turn submit plan."""
    if session:
        session.setdefault("turn_ids", []).append(turn_id)


def _resolve_turn_submit_approval_payload(
    session_id: str,
    turn_id: str,
    turn: dict[str, Any],
    requires_approval: bool | None,
    unified_diff: str | None,
) -> dict[str, Any]:
    """Resolve turn submit approval payload."""
    # When unified_diff is provided (even as empty list), requires_approval must be explicitly True
    if unified_diff is not None and requires_approval is not True:
        raise ValueError("Turn submit approval diff unresolved")
    if requires_approval:
        if not unified_diff or unified_diff == [] or unified_diff == "":
            raise ValueError("Turn submit approval diff unresolved")
        SERVER_STATE.approval_counter += 1
        approval_id = f"approval-{SERVER_STATE.approval_counter:04d}"
        approval: dict[str, Any] = {
            "id": approval_id,
            "turn_id": turn_id,
            "status": "pending",
            "unified_diff": unified_diff,
        }
        SERVER_STATE.approvals[approval_id] = approval
        return {"approval": approval, "requires_approval": True, "unified_diff": unified_diff}
    return {"requires_approval": False, "unified_diff": None}


def _resolve_turn_submit_completion(
    session_id: str,
    turn_id: str,
    input_text: str,
    turn: dict[str, Any],
    notifications: list[dict[str, Any]],
) -> dict[str, Any]:
    """Resolve turn submit completion."""
    SERVER_STATE.tool_call_counter += 1
    tool_call_id = f"tool-call-{SERVER_STATE.tool_call_counter:04d}"
    turn["status"] = "completed"
    turn["tool_call_id"] = tool_call_id
    return {"tool_call_id": tool_call_id, "status": "completed"}


def _apply_turn_submit_side_effects(
    session_id: str,
    turn_id: str,
    turn: dict[str, Any],
    input_text: str,
    requires_approval: bool,
    unified_diff: str | None,
    notifications: list[dict[str, Any]],
) -> dict[str, Any]:
    """Apply turn submit side effects."""
    if requires_approval:
        SERVER_STATE.approval_counter += 1
        approval_id = f"approval-{SERVER_STATE.approval_counter:04d}"
        approval: dict[str, Any] = {
            "id": approval_id,
            "turn_id": turn_id,
            "status": "pending",
            "unified_diff": unified_diff or "",
        }
        SERVER_STATE.approvals[approval_id] = approval
        turn["status"] = "awaiting_approval"
        turn["approval_id"] = approval_id
        notifications.append({
            "method": "approval/requested",
            "params": {
                "approval_id": approval_id,
                "turn_id": turn_id,
                "unified_diff": unified_diff or "",
            },
        })
        return {"approval": approval, "status": "awaiting_approval"}
    else:
        SERVER_STATE.tool_call_counter += 1
        tool_call_id = f"tool-call-{SERVER_STATE.tool_call_counter:04d}"
        turn["status"] = "completed"
        turn["tool_call_id"] = tool_call_id
        notifications.append({
            "method": "turn/completed",
            "params": {
                "turn_id": turn_id,
                "tool_call_id": tool_call_id,
            },
        })
        return None


def _build_turn_submit_execution_phase(parse_phase: dict[str, Any]) -> tuple[str, dict[str, Any], str, bool, str | None, str | None, list[dict[str, Any]]]:
    """Build turn submit execution phase from parse phase."""
    # Return a 7-tuple matching what tests expect
    session_id = parse_phase.get("session_id", "")
    turn = parse_phase.get("turn", {})
    input_text = parse_phase.get("input", "")
    requires_approval = parse_phase.get("requires_approval", False)
    unified_diff = parse_phase.get("unified_diff")
    error = parse_phase.get("error")
    notifications = parse_phase.get("notifications", [])
    return (session_id, turn, input_text, requires_approval, unified_diff, error, notifications)


def _build_turn_submit_result_payload_flat(
    turn: dict[str, Any],
    approval: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build turn submit result payload (flat format)."""
    result: dict[str, Any] = {"turn": turn}
    if approval:
        result["approval"] = approval
    return result


def _build_turn_submit_result_payload_nested(
    turn: dict[str, Any],
    approval: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build turn submit result payload (nested format)."""
    result: dict[str, Any] = {"turn": turn}
    if approval:
        result["approval"] = approval
    return result


def _handle_turn_submit_parse_failure(error_payload: dict[str, Any]) -> dict[str, Any]:
    """Handle turn submit parse failure."""
    return error_payload


def _route_turn_cancel_method(
    plan: dict[str, Any],
) -> str:
    """Route turn cancel method."""
    return "turn_cancel_dispatch"


def _parse_turn_cancel_request(
    params: dict[str, Any],
) -> JsonRpcError | dict[str, str]:
    """Parse turn cancel request."""
    if not isinstance(params, dict):
        return JsonRpcError(-32602, "params must be object", {"reason": "params_must_be_object"})
    turn_id = params.get("turn_id")
    if not turn_id:
        return JsonRpcError(-32602, "turn_id is required", {"reason": "turn_id_required"})
    return {"turn_id": turn_id}


def _execute_turn_cancel_resolution(
    turn: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    """Execute turn cancel resolution."""
    return _execute_turn_cancel(turn, context)


def _project_turn_cancel_response(
    request_id: str | int | None,
    turn: dict[str, Any],
) -> dict[str, Any]:
    """Project turn cancel response."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"turn": turn},
    }


def _resolve_turn_cancel_turn(
    turn_id: str | None,
) -> JsonRpcError | dict[str, Any]:
    """Resolve turn cancel turn."""
    if not turn_id:
        return JsonRpcError(-32602, "turn_id is required", {"reason": "turn_id_required"})
    turn = SERVER_STATE.turns.get(turn_id)
    if not turn:
        return JsonRpcError(-32002, "Turn not found", {"reason": "turn_not_found"})
    return turn


def _resolve_turn_cancel_context(
    turn_id: str | None,
) -> JsonRpcError | dict[str, Any]:
    """Resolve turn cancel context."""
    if not turn_id:
        return JsonRpcError(-32602, "turn_id is required", {"reason": "turn_id_required"})
    turn = SERVER_STATE.turns.get(turn_id)
    if not turn:
        return JsonRpcError(-32002, "Turn not found", {"reason": "turn_not_found"})
    session_id = turn.get("session_id")
    if session_id:
        session = SERVER_STATE.sessions.get(session_id)
        if session:
            return session
    return {}


def _validate_turn_cancel_turn_state(turn: dict[str, Any]) -> JsonRpcError | None:
    """Validate turn cancel turn state."""
    if turn.get("status") in ("completed", "cancelled", "failed"):
        return JsonRpcError(-32003, "Turn already terminal", {"reason": "turn_terminal"})
    return None


def _cancel_turn_requested_approval(turn: dict[str, Any]) -> None:
    """Cancel turn's requested approval."""
    approval_id = turn.get("approval_id")
    if approval_id:
        approval = SERVER_STATE.approvals.get(approval_id)
        if approval and approval.get("status") in ("pending", "requested"):
            approval["status"] = "cancelled"


def _mark_turn_as_cancelled(turn: dict[str, Any]) -> None:
    """Mark turn as cancelled."""
    turn["status"] = "cancelled"


def _execute_turn_cancel(
    turn: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    """Execute turn cancel."""
    _cancel_turn_requested_approval(turn)
    _mark_turn_as_cancelled(turn)
    return turn


def _validate_turn_cancel_projection_turn_id(
    turn_id: str | None,
    projection: dict[str, Any],
) -> JsonRpcError | None:
    """Validate turn cancel projection turn id."""
    if projection.get("id") != turn_id:
        return JsonRpcError(-32001, "Projection turn_id mismatch", {"reason": "turn_id_mismatch"})
    return None


def _build_turn_cancel_projection_payload(turn: dict[str, Any]) -> dict[str, Any]:
    """Build turn cancel projection payload."""
    return {
        "id": turn.get("id"),
        "session_id": turn.get("session_id"),
        "status": "cancelled",
        "approval_id": turn.get("approval_id"),
    }


def _build_turn_cancel_phase_plan(
    turn_id: str | None = None,
    turn: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> JsonRpcError | dict[str, Any]:
    """Build turn cancel phase plan."""
    if turn_id is None:
        return JsonRpcError(-32602, "turn_id is required", {"reason": "turn_id_required"})

    result = _resolve_turn_cancel_turn(turn_id)
    if isinstance(result, JsonRpcError):
        return result

    result = _validate_turn_cancel_turn_state(result)
    if isinstance(result, JsonRpcError):
        return result

    context_result = _resolve_turn_cancel_context(turn_id)
    if isinstance(context_result, JsonRpcError):
        return context_result

    return {
        "turn_id": turn_id,
        "turn": result,
        "context": context_result,
    }


def _handle_turn_cancel_request(
    request_id: str | int | None,
    turn_id: str,
) -> dict[str, Any] | None:
    """Handle turn/cancel request."""
    turn = SERVER_STATE.turns.get(turn_id)
    if not turn:
        return _error_response(request_id, JsonRpcError(-32002, "Turn not found", {"reason": "turn_not_found"}))

    if turn.get("status") in ("completed", "cancelled", "failed"):
        return _error_response(request_id, JsonRpcError(-32003, "Turn already terminal", {"reason": "turn_terminal"}))

    # Cancel any pending approval
    approval_id = turn.get("approval_id")
    if approval_id and SERVER_STATE.approvals.get(approval_id, {}).get("status") in ("pending", "requested"):
        SERVER_STATE.approvals[approval_id]["status"] = "cancelled"

    turn["status"] = "cancelled"

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"turn": turn},
    }


def _handle_approval_grant(
    request_id: str | int | None,
    approval_id: str,
) -> dict[str, Any] | None:
    """Handle approval/grant request."""
    approval = SERVER_STATE.approvals.get(approval_id)
    if not approval:
        return _error_response(request_id, JsonRpcError(-32002, "Approval not found", {"reason": "approval_not_found"}))

    if approval.get("status") != "pending":
        return _error_response(request_id, JsonRpcError(-32003, "Approval not pending", {"reason": "approval_not_pending"}))

    approval["status"] = "granted"
    turn_id = approval.get("turn_id")
    if turn_id and turn_id in SERVER_STATE.turns:
        SERVER_STATE.turns[turn_id]["status"] = "approved"
        SERVER_STATE.tool_call_counter += 1
        SERVER_STATE.turns[turn_id]["tool_call_id"] = f"tool-call-{SERVER_STATE.tool_call_counter:04d}"

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"approval": approval},
    }


def _handle_approval_reject(
    request_id: str | int | None,
    approval_id: str,
) -> dict[str, Any] | None:
    """Handle approval/reject request."""
    approval = SERVER_STATE.approvals.get(approval_id)
    if not approval:
        return _error_response(request_id, JsonRpcError(-32002, "Approval not found", {"reason": "approval_not_found"}))

    if approval.get("status") != "pending":
        return _error_response(request_id, JsonRpcError(-32003, "Approval not pending", {"reason": "approval_not_pending"}))

    approval["status"] = "rejected"
    turn_id = approval.get("turn_id")
    if turn_id and turn_id in SERVER_STATE.turns:
        SERVER_STATE.turns[turn_id]["status"] = "rejected"

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"approval": approval},
    }


SUPPORTED_METHODS = [
    "session/start",
    "session/list",
    "session/resume",
    "session/read",
    "turn/submit",
    "turn/cancel",
    "approval/grant",
    "approval/reject",
    "health/check",
    "config/read",
]


def _handle_config_read(
    request_id: str | int | None,
    key: str | None = None,
) -> dict[str, Any]:
    """Handle config/read request."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"supported_methods": sorted(SUPPORTED_METHODS), "server": "thegent-agent-server", "transport": "stdio"},
    }


def process_jsonrpc_line(line: str) -> str | None:
    """Process a single JSON-RPC line and return response string."""
    try:
        import orjson
        request = orjson.loads(line)
    except Exception:
        return '{"jsonrpc": "2.0", "id": null, "error": {"code": -32700, "message": "Parse error"}}'

    method = request.get("method")
    request_id = request.get("id")
    params = request.get("params", {})

    if method == "session/start":
        response = _handle_session_start(request_id)
    elif method == "session/list":
        response = _handle_session_list(request_id)
    elif method == "session/resume":
        response = _handle_session_resume(request_id, params.get("session_id", ""))
    elif method == "session/read":
        response = _handle_session_read(request_id, params)
    elif method == "turn/submit":
        response = _handle_turn_submit_request(
            request_id,
            params.get("session_id", ""),
            params.get("input", ""),
            params.get("requires_approval", False),
            params.get("unified_diff"),
        )
    elif method == "turn/cancel":
        response = _handle_turn_cancel_request(request_id, params.get("turn_id", ""))
    elif method == "approval/grant":
        response = _handle_approval_grant(request_id, params.get("approval_id", ""))
    elif method == "approval/reject":
        response = _handle_approval_reject(request_id, params.get("approval_id", ""))
    elif method == "health/check":
        response = _handle_health_check(request_id)
    elif method == "config/read":
        response = _handle_config_read(request_id, params.get("key", ""))
    else:
        response = _error_response(request_id, JsonRpcError(-32601, f"Method not found: {method}"))

    return orjson.dumps(response).decode()


def process_jsonrpc_line_full(line: str) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    """Process a JSON-RPC line and return (response, notifications) tuple."""
    try:
        import orjson
        request = orjson.loads(line)
    except Exception:
        return ({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}, [])

    # Handle notifications (no id field)
    is_notification = request.get("id") is None
    method = request.get("method")
    request_id = request.get("id")
    params = request.get("params", {})

    notifications: list[dict[str, Any]] = []

    if method == "session/start":
        response = _handle_session_start(request_id)
        if is_notification:
            response = None
    elif method == "session/list":
        response = _handle_session_list(request_id)
    elif method == "session/resume":
        response = _handle_session_resume(request_id, params.get("session_id", ""))
    elif method == "session/read":
        response = _handle_session_read(request_id, params)
    elif method == "turn/submit":
        response = _handle_turn_submit_request(
            request_id,
            params.get("session_id", ""),
            params.get("input", ""),
            params.get("requires_approval", False),
            params.get("unified_diff"),
        )
        if response and "result" in response:
            notifications.append({
                "jsonrpc": "2.0",
                "method": "turn/started",
                "params": response["result"],
            })
        if is_notification:
            response = None
    elif method == "turn/cancel":
        response = _handle_turn_cancel_request(request_id, params.get("turn_id", ""))
        if is_notification and response and "result" in response:
            notifications.append({
                "jsonrpc": "2.0",
                "method": "turn/cancelled",
                "params": response["result"],
            })
            response = None
    elif method == "approval/grant":
        response = _handle_approval_grant(request_id, params.get("approval_id", ""))
        if is_notification:
            if response and "result" in response:
                notifications.append({
                    "jsonrpc": "2.0",
                    "method": "approval/granted",
                    "params": response["result"],
                })
            response = None
    elif method == "approval/reject":
        response = _handle_approval_reject(request_id, params.get("approval_id", ""))
        if is_notification:
            if response and "result" in response:
                notifications.append({
                    "jsonrpc": "2.0",
                    "method": "approval/rejected",
                    "params": response["result"],
                })
            response = None
    elif method == "health/check":
        response = _handle_health_check(request_id)
    elif method == "config/read":
        response = _handle_config_read(request_id, params.get("key", ""))
        if is_notification:
            response = None
    else:
        response = _error_response(request_id, JsonRpcError(-32601, f"Method not found: {method}"))

    return (response, notifications)


# === Turn Submit Phase Functions ===

def _build_turn_submit_parse_phase(
    plan: dict[str, Any],
    error: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build parse phase for turn submit."""
    return {
        "session_id": plan.get("session_id", ""),
        "lane": plan.get("lane", ""),
        "input": plan.get("input"),
        "parse_error": error,
    }
def _build_turn_submit_phase_plan(
    request_id: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    """Build turn submit phase plan."""
    input_text = params.get("input", "")
    if input_text and not isinstance(input_text, str):
        raise ValueError("input must be a string if provided")
    
    # Check if session exists
    session_id = params.get("session_id", "")
    if session_id and session_id not in SERVER_STATE.sessions:
        return {
            "request_id": request_id,
            "session_id": session_id,
            "input": input_text,
            "user_input": input_text,
            "error": {"code": -32001, "message": "Session not found"},
        }
    
    return {
        "request_id": request_id,
        "session_id": session_id,
        "input": input_text,
        "user_input": input_text,
        "requires_approval": params.get("requires_approval", False),
        "unified_diff": params.get("unified_diff"),
    }


def _build_turn_submit_parse_phase(
    plan: dict[str, Any],
    error: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build parse phase for turn submit."""
    # If plan has an error field, use it
    if error is None and "error" in plan:
        error = plan["error"]
    return {
        "session_id": plan.get("session_id", ""),
    Returns a tuple of (turn_id, turn, session).
    """
    turn = parse_phase.get("turn")
    session = parse_phase.get("session")
    if not isinstance(turn, dict):
        raise ValueError("commit_target: turn must be a dict")
    if not isinstance(session, dict):
        raise ValueError("commit_target: session must be a dict")
    turn_id = turn.get("id", "unknown")
    return (turn_id, turn, session)


def _build_turn_submit_commit_resolution_phase(
    route: str,
    request_id: str,
    commit_target: tuple[str, dict[str, Any], dict[str, Any]],
) -> dict[str, Any]:
    """Build commit resolution phase for turn submit.
    
    Returns a dict with route, request_id, turn, and session.
    """
    turn_id, turn, session = commit_target
    return {
        "route": route,
        "request_id": request_id,
        "turn": turn,
        "session": session,
    }


def _apply_turn_submit_commit(turn_id: str, turn: dict[str, Any], session: dict[str, Any]) -> dict[str, Any]:
    """Apply turn submit commit."""
    SERVER_STATE.turns[turn_id] = turn
    session_id = session.get("id")
    if session_id in SERVER_STATE.sessions:
        SERVER_STATE.sessions[session_id]["turn_ids"].append(turn_id)
    return turn


def _resolve_turn_submit_side_effects_target(resolved: dict[str, Any]) -> tuple[str, str, str]:
    """Resolve turn submit side effects target from resolved."""
    approval = resolved.get("approval")
    if approval is None:
        raise ValueError("side-effects target: approval is required")
    if not isinstance(approval, dict):
        raise ValueError("side-effects target: approval must be dict")
    approval_id = approval.get("id")
    approval_status = approval.get("status")
    approval_diff = approval.get("diff", "")
    if approval_id is None:
        raise ValueError("side-effects target: approval.id is required")
    if approval_status is None:
        raise ValueError("side-effects target: approval.status is required")
    return (approval_id, approval_status, approval_diff)


    return {
        "route": route,
        "request_id": request_id,
        "turn": turn,
        "approval": approval,
    }


def _build_turn_submit_side_effects_phase(
    session_id: str,
    turn_id: str,
    turn: dict[str, Any],
    lane: str,
    requires_approval: bool,
    diff: str | None,
) -> dict[str, Any]:
    """Build side effects phase for turn submit."""
    return {
        "session_id": session_id,
        "turn_id": turn_id,
        "turn": turn,
        "lane": lane,
        "requires_approval": requires_approval,
        "diff": diff,
    }

def _resolve_turn_submit_parse_error(
    parse_phase: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Resolve parse error from parse phase."""
    if parse_phase is not None and isinstance(parse_phase, dict):
        error = parse_phase.get("parse_error")
        if isinstance(error, dict):
            return error
    return None


def _resolve_turn_submit_execution_target(
    parse_phase: dict[str, Any],
) -> tuple[str, str, bool, str | None]:
    """Resolve execution target from parse phase."""
    if isinstance(parse_phase, dict):
        input_val = parse_phase.get("input", "")
        turn_id = parse_phase.get("turn_id", "")
        requires_approval = parse_phase.get("requires_approval", False)
        unified_diff = parse_phase.get("unified_diff")
        return turn_id, input_val, requires_approval, unified_diff
    return "", "", False, None


def _apply_turn_submit_execution(
    execution_phase: dict[str, Any],
) -> dict[str, Any]:
    """Apply turn submit execution - update turn status."""
    if isinstance(execution_phase, dict):
        turn = execution_phase.get("turn", {})
        session_id = execution_phase.get("session_id", "")
        requires_approval = execution_phase.get("requires_approval", False)
        if session_id:
            turn["session_id"] = session_id
        if requires_approval:
            turn["status"] = "awaiting_approval"
        else:
            turn["status"] = "completed"
        return turn
    return {}


def _apply_turn_submit_commit(
    commit_phase: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply turn submit commit - update session."""
    if isinstance(commit_phase, dict):
        turn = commit_phase.get("turn", {})
        session = commit_phase.get("session", {})
        if turn and session:
            turn_ids = session.get("turn_ids", [])
            if turn["id"] not in turn_ids:
                turn_ids.append(turn["id"])
                session["turn_ids"] = turn_ids
        return turn, session
    return {}, {}


def _apply_turn_submit_side_effects(
    side_effects_phase: dict[str, Any],
) -> dict[str, Any] | tuple[dict[str, Any], dict[str, Any] | None]:
    """Apply turn submit side effects.
    
    Returns (turn, approval) tuple for approval-required cases.
    """
    if isinstance(side_effects_phase, dict):
        turn = side_effects_phase.get("turn", {})
        requires_approval = side_effects_phase.get("requires_approval", False)
        if requires_approval:
            approval_id = f"approval-{SERVER_STATE.approval_counter}"
            SERVER_STATE.approval_counter += 1
            turn["approval_id"] = approval_id
            approval = {
                "id": approval_id,
                "turn_id": turn["id"],
                "status": "requested",
                "diff": side_effects_phase.get("diff"),
            }
            SERVER_STATE.approvals[approval_id] = approval
            return turn, approval
        return turn
    return {}


def _build_turn_submit_response_phase(
    requires_approval: bool,
    request_id: str | int | None,
    turn: dict[str, Any],
    approval: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build response phase for turn submit."""
    return {
        "requires_approval": requires_approval,
        "request_id": request_id,
        "turn": turn,
        "approval": approval,
    }


def _build_turn_submit_response_resolution_phase(
    response_phase: dict[str, Any],
) -> tuple[bool, str | int | None, dict[str, Any], dict[str, Any] | None]:
    """Build response resolution phase tuple from response phase dict."""
    requires_approval = response_phase.get("requires_approval", False)
    request_id = response_phase.get("request_id")
    turn = response_phase.get("turn", {})
    approval = response_phase.get("approval")
    return requires_approval, request_id, turn, approval


def _resolve_turn_submit_response_target(
    response_phase: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Resolve the response target from the response phase.

    WL-9827: Response target resolution.
    """
    if "turn" not in response_phase:
        raise ValueError("response_target requires 'turn'")
    turn = response_phase.get("turn", {})
    approval = response_phase.get("approval")
    return turn, approval


def _build_turn_submit_success_response(
    request_id: str | int,
    turn: dict[str, Any],
    approval_id: str | None = None,
    approval_status: str | None = None,
    approval_diff: str | None = None,
    approval: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build success response for turn submit."""
    result: dict[str, Any] = {"turn": turn}
    if approval_id is not None:
        result["approval_id"] = approval_id
    if approval_status is not None:
        result["approval_status"] = approval_status
    if approval_diff is not None:
        result["approval_diff"] = approval_diff
    if approval is not None:
        result["approval"] = approval
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result,
    }


def _build_turn_submit_result_payload(
    turn: dict[str, Any],
    approval_id: str | None = None,
    approval_status: str | None = None,
    approval_diff: str | None = None,
    approval: dict[str, Any] | None = None,
    flat: bool = False,
) -> dict[str, Any]:
    """Build result payload for turn submit."""
    if flat:
        result: dict[str, Any] = {"turn": turn}
        if approval_id is not None:
            result["approval_id"] = approval_id
        if approval_status is not None:
            result["approval_status"] = approval_status
        if approval_diff is not None:
            result["approval_diff"] = approval_diff
        return result
    else:
        payload: dict[str, Any] = {"turn": turn}
        if approval is not None:
            payload["approval"] = approval
        return payload


def _build_turn_submit_success_response_nested(
    request_id: str | int,
    turn: dict[str, Any],
    approval: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build success response with nested approval object."""
    result: dict[str, Any] = {"turn": turn}
    if approval is not None:
        result["approval"] = approval
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result,
    }


def _extract_turn_submit_response_request_id(
    response: dict[str, Any],
    is_required: bool | None = None,
    expected: bool | None = None,
    required: bool | None = None,
    request_has_id: bool | None = None,
) -> str | int | None:
    """Extract and validate request_id from response."""
    req = request_has_id if request_has_id is not None else (required if required is not None else (is_required if is_required is not None else expected))
    request_id = response.get("request_id")
    if req:
        if request_id is None:
            raise ValueError("Turn submit response target unresolved")
        if not isinstance(request_id, (str, int)):
            raise ValueError("Turn submit response target unresolved")
        return request_id
    if request_id is not None and not isinstance(request_id, (str, int)):
        raise ValueError("Turn submit response target unresolved")
    return None


def _extract_turn_submit_response_approval_id(response: dict[str, Any]) -> str | None:
    """Extract approval_id from response."""
    return response.get("approval_id")


def _extract_turn_submit_response_approval_status(response: dict[str, Any]) -> str | None:
    """Extract approval_status from response."""
    return response.get("approval_status")


def _extract_turn_submit_response_approval_diff(response: dict[str, Any]) -> str | None:
    """Extract approval_diff from response."""
    return response.get("approval_diff")


def _extract_turn_submit_response_approval_payload(response: dict[str, Any]) -> dict[str, Any] | None:
    """Extract approval payload from response."""
    return response.get("approval")


def _extract_turn_submit_approval_payload_id(approval: dict[str, Any] | None) -> str | None:
    """Extract id from approval payload."""
    if approval is None:
        return None
    return approval.get("id")


def _extract_turn_submit_approval_payload_status(approval: dict[str, Any] | None) -> str | None:
    """Extract status from approval payload."""
    if approval is None:
        return None
    return approval.get("status")


def _extract_turn_submit_approval_payload_diff(approval: dict[str, Any] | None) -> str | None:
    """Extract diff from approval payload."""
    if approval is None:
        return None
    return approval.get("diff")


def _resolve_turn_submit_response_approval_fields(
    response: dict[str, Any],
) -> tuple[str | None, str | None, str | None]:
    """Resolve approval fields from response."""
    approval_id = response.get("approval_id")
    approval_status = response.get("approval_status")
    approval_diff = response.get("approval_diff")
    return approval_id, approval_status, approval_diff


def _validate_turn_submit_approval_payload(approval: dict[str, Any] | None) -> dict[str, Any] | None:
    """Validate approval payload."""
    if approval is None:
        return None
    if not isinstance(approval, dict):
        raise ValueError("Invalid approval payload")
    return approval


def _extract_turn_submit_response_request_has_id(response: dict[str, Any]) -> bool:
    """Check if response has request_id."""
    return response.get("request_id") is not None


def _extract_turn_submit_response_turn(response: dict[str, Any]) -> dict[str, Any] | None:
    """Extract turn from response."""
    return response.get("turn")


# === Approval Resolution Functions ===

def _build_approval_resolution_phase_plan(
    approval_id: str,
    action: str,
) -> dict[str, Any]:
    """Build approval resolution phase plan."""
    return {
        "approval_id": approval_id,
        "action": action,
    }


def _resolve_approval_resolution_execution_target(
    phase_plan: dict[str, Any],
) -> tuple[str, str, str, dict[str, Any]]:
    """Resolve approval resolution execution target."""
    if not isinstance(phase_plan, dict):
        raise ValueError("Approval resolution execution target unresolved")
    approval_id = phase_plan.get("approval_id")
    action = phase_plan.get("action")
    if not approval_id or not action:
        raise ValueError("Approval resolution execution target unresolved")
    approval = SERVER_STATE.approvals.get(approval_id, {})
    return approval_id, action, approval.get("status", ""), approval


def _apply_approval_resolution_execution(
    approval_id: str,
    action: str,
    current_status: str,
) -> dict[str, Any]:
    """Apply approval resolution execution."""
    if current_status not in ("pending", "requested"):
        raise ValueError("Approval cannot be resolved")
    approval = SERVER_STATE.approvals.get(approval_id, {})
    if action == "grant":
        approval["status"] = "granted"
    else:
        approval["status"] = "rejected"
    SERVER_STATE.approvals[approval_id] = approval
    return approval


def _build_approval_resolution_success_response(
    request_id: str | int,
    approval: dict[str, Any],
    emit_policy: str = "always",
) -> dict[str, Any]:
    """Build approval resolution success response."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"approval": approval, "emit_policy": emit_policy},
    }


def _build_approval_resolution_failure_response(
    request_id: str | int,
    error: dict[str, Any],
    parse_error: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build approval resolution failure response."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": error,
    }


def _discover_approval_resolution_route(action: str) -> str:
    """Discover approval resolution route."""
    return f"approval/{action}"


def _resolve_approval_resolution_context(approval_id: str) -> dict[str, Any]:
    """Resolve approval resolution context."""
    approval = SERVER_STATE.approvals.get(approval_id, {})
    return {
        "approval_id": approval_id,
        "approval": approval,
        "status": approval.get("status", "unknown"),
    }


def _bind_approval_resolution_phases() -> list[Any]:
    """Bind approval resolution phase functions."""
    return [
        _resolve_approval_resolution_context,
        _apply_approval_resolution_execution,
    ]


# === Turn Cancel Functions ===

def _parse_turn_cancel_request(params: dict[str, Any] | None) -> str | None:
    """Parse turn cancel request parameters."""
    if not isinstance(params, dict):
        raise ValueError("params_must_be_object")
    turn_id = params.get("turn_id")
    if not turn_id:
        raise ValueError("turn_id_required")
    return turn_id


def _cancel_turn_requested_approval(approval_id: str | None) -> None:
    """Cancel the approval requested for a turn."""
    if approval_id:
        approval = SERVER_STATE.approvals.get(approval_id)
        if approval and approval.get("status") in ("pending", "requested"):
            approval["status"] = "cancelled"


def _mark_turn_as_cancelled(turn_id: str) -> None:
    """Mark a turn as cancelled."""
    turn = SERVER_STATE.turns.get(turn_id)
    if turn:
        turn["status"] = "cancelled"


def _build_turn_cancel_projection_payload(turn: dict[str, Any]) -> dict[str, Any]:
    """Build projection payload for turn cancel."""
    return {
        "id": turn.get("id"),
        "session_id": turn.get("session_id"),
        "status": turn.get("status"),
    }


def _validate_turn_cancel_turn_state(turn: dict[str, Any]) -> str:
    """Validate turn state for cancellation."""
    status = turn.get("status", "")
    if status in ("completed", "cancelled", "failed"):
        raise ValueError("Turn already terminal")
    return status


def _validate_turn_cancel_turn_state_with_approval(
    turn: dict[str, Any],
    approval_id: str | None,
) -> str:
    """Validate turn state with approval for cancellation."""
    status = turn.get("status", "")
    if status in ("completed", "cancelled", "failed"):
        raise ValueError("Turn already terminal")
    if approval_id:
        approval = SERVER_STATE.approvals.get(approval_id)
        if approval and approval.get("status") in ("granted", "rejected"):
            raise ValueError("Approval already resolved")
    return status


def _execute_turn_cancel_resolution(
    turn_id: str,
    turn: dict[str, Any],
) -> dict[str, Any]:
    """Execute turn cancel resolution."""
    return turn


def _project_turn_cancel_success(
    turn_id: str,
    turn: dict[str, Any],
) -> dict[str, Any]:
    """Project turn cancel success response."""
    return {
        "turn": turn,
    }


def _build_turn_cancel_phase_plan(turn_id: str) -> dict[str, Any]:
    """Build phase plan for turn cancel."""
    return {
        "turn_id": turn_id,
        "route": "turn/cancel",
    }


def _bind_turn_cancel_phases() -> list[Any]:
    """Bind turn cancel phase functions."""
    return [
        _parse_turn_cancel_request,
        _validate_turn_cancel_turn_state,
        _execute_turn_cancel_resolution,
        _project_turn_cancel_success,
    ]


# Alias for compatibility
_handle_turn_cancel_request = _handle_turn_cancel_request


def _resolve_turn_cancel_execution_target(
    turn_id: str,
    turn: dict[str, Any],
) -> tuple[str, dict[str, Any]]:
    """Resolve turn cancel execution target."""
    return turn_id, turn


def _apply_turn_cancel_execution(
    turn_id: str,
    turn: dict[str, Any],
) -> dict[str, Any]:
    """Apply turn cancel execution."""
    _cancel_turn_requested_approval(turn.get("approval_id"))
    _mark_turn_as_cancelled(turn_id)
    return turn


def _build_turn_cancel_success_response(
    request_id: str | int | None,
    turn: dict[str, Any],
) -> dict[str, Any]:
    """Build turn cancel success response."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"turn": turn},
    }


# === Additional Resolution Functions ===

def _resolve_turn_cancel_turn(turn_id: str) -> dict[str, Any]:
    """Resolve turn for cancel operation."""
    turn = SERVER_STATE.turns.get(turn_id)
    if not turn:
        raise ValueError("Turn not found")
    return turn


# === Approval Resolution Functions ===

def _resolve_approval_resolution_success_target(
    approval: dict[str, Any],
    emit_policy: str,
) -> tuple[dict[str, Any], str]:
    """Resolve approval resolution success target."""
    return approval, emit_policy


def _extract_approval_resolution_success_response(
    approval: dict[str, Any],
    emit_policy: str,
) -> dict[str, Any]:
    """Extract approval resolution success response."""
    return {
        "approval": approval,
        "emit_policy": emit_policy,
    }


def _resolve_turn_submit_parse_phase_input(parse_phase: dict[str, Any]) -> str | None:
    """Extract input from parse phase."""
    return parse_phase.get("input")


# === Helper Functions ===

def _apply_retry(turn_id: str) -> dict[str, Any]:
    """Apply retry to a turn."""
    turn = SERVER_STATE.turns.get(turn_id, {})
    turn["status"] = "in_progress"
    return turn


def _apply_conflict_resolution(
    turn_id: str,
    strategy: str,
) -> dict[str, Any]:
    """Apply conflict resolution to a turn."""
    turn = SERVER_STATE.turns.get(turn_id, {})
    turn["conflict_strategy"] = strategy
    return turn


def enforce_max_changes_per_cycle(
    changes: list[dict[str, Any]],
    max_changes: int = 100,
) -> list[dict[str, Any]]:
    """Enforce maximum changes per cycle."""
    return changes[:max_changes]


def _parse_turn_cancel_with_binding(
    turn_id: str,
    session_id: str | None = None,
) -> dict[str, Any]:
    """Parse turn cancel with binding."""
    return {
        "turn_id": turn_id,
        "session_id": session_id,
    }


def _dispatch_turn_cancel_success(
    request_id: str | int | None,
    turn: dict[str, Any],
) -> dict[str, Any]:
    """Dispatch turn cancel success."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"turn": turn},
    }


def _dispatch_turn_cancel_recovery(
    request_id: str | int | None,
    error: dict[str, Any],
) -> dict[str, Any]:
    """Dispatch turn cancel recovery."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": error,
    }


# === Additional Functions for Tests ===

def _extract_turn_submit_commit_session(commit_phase: dict[str, Any] | None) -> dict[str, Any]:
    """Extract session from commit phase."""
    if commit_phase is None:
        return {"id": f"session-{SERVER_STATE.session_counter}", "turn_ids": []}
    if not isinstance(commit_phase, dict):
        raise ValueError("Turn submit commit target unresolved")
    session = commit_phase.get("session")
    if not isinstance(session, dict):
        raise ValueError("Turn submit commit target unresolved")
    return session


def _extract_turn_submit_side_effects_turn_id(side_effects_phase: dict[str, Any]) -> str | None:
    """Extract turn_id from side effects phase."""
    if side_effects_phase is None:
        return None
    return side_effects_phase.get("turn_id")


def _resolve_turn_submit_commit_target(commit_phase: dict[str, Any]) -> tuple[str, dict[str, Any], dict[str, Any]]:
    """Resolve commit target from commit phase."""
    if not isinstance(commit_phase, dict):
        raise ValueError("commit_target: unresolved")
    turn = commit_phase.get("turn")
    session = commit_phase.get("session")
    if not isinstance(turn, dict):
        raise ValueError("commit_target: turn missing")
    if not isinstance(session, dict):
        raise ValueError("commit_target: session missing")
    return (turn["id"], turn, session)


def _resolve_turn_submit_side_effects_target(side_effects_phase: dict[str, Any]) -> tuple[str, str, str | None]:
    """Resolve side effects target from side effects phase."""
    if not isinstance(side_effects_phase, dict):
        raise ValueError("side-effects: unresolved")
    approval = side_effects_phase.get("approval")



def _build_turn_submit_commit_resolution_phase(route, request_id, turn, session):
    return {'route': route, 'request_id': request_id, 'turn': turn, 'session': session}

def _build_turn_submit_side_effects_resolution_phase(route, request_id, approval_id, approval_status, approval_diff):
    return {'route': route, 'request_id': request_id, 'approval_id': approval_id, 'approval_status': approval_status, 'approval_diff': approval_diff}

def _build_turn_submit_response_resolution_phase(route, request_id, turn, approval):
    return {'route': route, 'request_id': request_id, 'turn': turn, 'approval': approval}
