"""In-memory JSON-RPC 2.0 agent server over stdio."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from typing import Any, TextIO


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
class JsonRpcError:
    code: int
    message: str
    data: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
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
    return isinstance(value, (str, int, float)) or value is None


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


def _dispatch_parsed_request(request: dict[str, Any]) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    if request.get("jsonrpc") != JSONRPC_VERSION:
        return _error_response(request.get("id"), JsonRpcError(-32600, "Invalid Request", {"reason": "jsonrpc"})), []
    if "id" in request and not _is_valid_request_id(request["id"]):
        return _error_response(None, JsonRpcError(-32600, "Invalid Request", {"reason": "id"})), []

    method = request.get("method")
    if not isinstance(method, str) or not method:
        return _error_response(request.get("id"), JsonRpcError(-32600, "Invalid Request", {"reason": "method"})), []

    if method not in SUPPORTED_METHODS:
        return _error_response(request.get("id"), _method_not_found(method)), []

    params, params_error = _extract_params(request)
    if params_error is not None:
        return _error_response(request.get("id"), params_error), []

    request_has_id = "id" in request
    request_id = request.get("id")
    notifications: list[dict[str, Any]] = []

    def maybe_response(result: dict[str, Any]) -> dict[str, Any] | None:
        if not request_has_id:
            return None
        return _result_response(request_id, result)

    if method == "health/check":
        return (
            maybe_response(
                {
                    "status": "ok",
                    "service": "thegent-agent-server",
                    "transport": "stdio",
                }
            ),
            notifications,
        )

    if method == "config/read":
        return (
            maybe_response(
                {
                    "server": "thegent-agent-server",
                    "transport": "stdio",
                    "supported_methods": sorted(SUPPORTED_METHODS),
                }
            ),
            notifications,
        )

    if method == "session/start":
        session_id = SERVER_STATE.next_session_id()
        session = {
            "id": session_id,
            "status": "active",
            "created_index": SERVER_STATE.session_counter,
            "turn_ids": [],
        }
        SERVER_STATE.sessions[session_id] = session
        return maybe_response({"session": _serialize_session(session)}), notifications

    if method == "session/resume":
        session_id = _normalized_non_empty_string(params.get("session_id"))
        if session_id is None:
            return _error_response(request_id, _invalid_params("session_id_required")), notifications
        session = SERVER_STATE.sessions.get(session_id)
        if session is None:
            return _error_response(request_id, JsonRpcError(-32001, "Session not found", {"session_id": session_id})), notifications
        session["status"] = "active"
        return maybe_response({"session": _serialize_session(session)}), notifications

    if method == "session/list":
        sessions = [
            _serialize_session(session)
            for session in sorted(SERVER_STATE.sessions.values(), key=lambda item: item["created_index"])
        ]
        return maybe_response({"sessions": sessions}), notifications

    if method == "session/read":
        session_id = _normalized_non_empty_string(params.get("session_id"))
        if session_id is None:
            return _error_response(request_id, _invalid_params("session_id_required")), notifications
        session = SERVER_STATE.sessions.get(session_id)
        if session is None:
            return _error_response(request_id, JsonRpcError(-32001, "Session not found", {"session_id": session_id})), notifications
        turns = [_serialize_turn(SERVER_STATE.turns[turn_id]) for turn_id in session["turn_ids"]]
        return maybe_response({"session": _serialize_session(session), "turns": turns}), notifications

    if method == "turn/submit":
        session_id = _normalized_non_empty_string(params.get("session_id"))
        if session_id is None:
            return _error_response(request_id, _invalid_params("session_id_required")), notifications
        session = SERVER_STATE.sessions.get(session_id)
        if session is None:
            return _error_response(request_id, JsonRpcError(-32001, "Session not found", {"session_id": session_id})), notifications

        user_input = params.get("input", "")
        if not isinstance(user_input, str):
            return _error_response(request_id, _invalid_params("input_must_be_string")), notifications

        if "requires_approval" in params and not isinstance(params["requires_approval"], bool):
            return _error_response(request_id, _invalid_params("requires_approval_must_be_boolean")), notifications

        requires_approval = params.get("requires_approval", False)
        if requires_approval:
            if "unified_diff" in params:
                raw_diff = params["unified_diff"]
            elif "diff" in params:
                raw_diff = params["diff"]
            else:
                return _error_response(request_id, _invalid_params("diff_required_when_requires_approval")), notifications
            if not isinstance(raw_diff, str):
                return _error_response(request_id, _invalid_params("diff_must_be_string")), notifications
            if not raw_diff.strip():
                return _error_response(request_id, _invalid_params("diff_must_be_non_empty_string")), notifications

        turn_id = SERVER_STATE.next_turn_id()
        turn = {
            "id": turn_id,
            "session_id": session_id,
            "input": user_input,
            "status": "in_progress",
            "approval_id": None,
            "tool_call_id": None,
        }
        SERVER_STATE.turns[turn_id] = turn
        session["turn_ids"].append(turn_id)

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

        if requires_approval:
            approval_id = SERVER_STATE.next_approval_id()
            approval_diff = params["unified_diff"] if "unified_diff" in params else params["diff"]
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
            return (
                maybe_response(
                    {
                        "turn": _serialize_turn(turn),
                        "approval": {
                            "id": approval_id,
                            "status": approval["status"],
                            "diff": approval_diff,
                        },
                    }
                ),
                notifications,
            )

        tool_call_id = SERVER_STATE.next_tool_call_id()
        turn["tool_call_id"] = tool_call_id
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
        turn["status"] = "completed"
        notifications.append(
            _notification(
                "turn/completed",
                {
                    "session_id": session_id,
                    "turn_id": turn_id,
                    "status": turn["status"],
                },
            )
        )
        return maybe_response({"turn": _serialize_turn(turn)}), notifications

    if method == "turn/cancel":
        turn_id = _normalized_non_empty_string(params.get("turn_id"))
        if turn_id is None:
            return _error_response(request_id, _invalid_params("turn_id_required")), notifications
        turn = SERVER_STATE.turns.get(turn_id)
        if turn is None:
            return _error_response(request_id, JsonRpcError(-32002, "Turn not found", {"turn_id": turn_id})), notifications
        if turn["status"] in TERMINAL_TURN_STATES:
            return _error_response(
                request_id,
                JsonRpcError(-32003, "Turn already terminal", {"turn_id": turn_id, "status": turn["status"]}),
            ), notifications

        turn["status"] = "cancelled"
        approval_id = turn.get("approval_id")
        if isinstance(approval_id, str) and approval_id in SERVER_STATE.approvals:
            approval = SERVER_STATE.approvals[approval_id]
            if approval["status"] == "requested":
                approval["status"] = "cancelled"
        return maybe_response({"turn": _serialize_turn(turn)}), notifications

    if method in {"approval/grant", "approval/reject"}:
        approval_id = _normalized_non_empty_string(params.get("approval_id"))
        if approval_id is None:
            return _error_response(request_id, _invalid_params("approval_id_required")), notifications

        approval = SERVER_STATE.approvals.get(approval_id)
        if approval is None:
            return _error_response(
                request_id,
                JsonRpcError(-32005, "Approval not found", {"approval_id": approval_id}),
            ), notifications

        if approval["status"] != "requested":
            return _error_response(
                request_id,
                JsonRpcError(
                    -32006,
                    "Approval already resolved",
                    {"approval_id": approval_id, "status": approval["status"]},
                ),
            ), notifications

        turn_id = approval["turn_id"]
        turn = SERVER_STATE.turns.get(turn_id)
        if turn is None:
            return _error_response(request_id, JsonRpcError(-32002, "Turn not found", {"turn_id": turn_id})), notifications
        if turn["status"] in TERMINAL_TURN_STATES:
            return _error_response(
                request_id,
                JsonRpcError(-32003, "Turn already terminal", {"turn_id": turn_id, "status": turn["status"]}),
            ), notifications

        if method == "approval/grant":
            approval["status"] = "granted"
            tool_call_id = SERVER_STATE.next_tool_call_id()
            turn["tool_call_id"] = tool_call_id
            notifications.append(
                _notification(
                    "item/toolCall/started",
                    {
                        "session_id": turn["session_id"],
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
                        "session_id": turn["session_id"],
                        "turn_id": turn_id,
                        "tool_call_id": tool_call_id,
                        "output": f"echo:{turn['input']}",
                    },
                )
            )
            turn["status"] = "completed"
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
        else:
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

        return (
            maybe_response(
                {
                    "approval": {"id": approval_id, "status": approval["status"]},
                    "turn": _serialize_turn(turn),
                }
            ),
            notifications,
        )

    return _error_response(request_id, _method_not_found(method)), notifications


def process_jsonrpc_line_full(raw_line: str) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    """Parse and fully process a single JSONL request, including notifications."""
    if not raw_line.strip():
        return None, []
    try:
        payload = json.loads(raw_line)
    except json.JSONDecodeError as exc:
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
            sink.write(json.dumps(response, separators=(",", ":")) + "\n")
        for notification in notifications:
            sink.write(json.dumps(notification, separators=(",", ":")) + "\n")

        if response is not None or notifications:
            sink.flush()


def main() -> int:
    return serve_stdio()


if __name__ == "__main__":
    raise SystemExit(main())
