"""Session tool handlers for MCP server."""

from __future__ import annotations

import json as json
from typing import Any, Callable

from thegent_protocols.mcp.dynamic_tools import DynamicToolRegistry, DynamicToolSpec

_dynamic_registry = DynamicToolRegistry()


def reset_dynamic_registry_for_tests() -> None:
    """Reset session-scoped dynamic tool state for deterministic tests."""
    global _dynamic_registry
    _dynamic_registry = DynamicToolRegistry()


def _parse_dynamic_message(message: str) -> dict[str, Any]:
    try:
        payload = json.loads(message)
    except json.JSONDecodeError as exc:
        raise ValueError("dynamic tool message must be valid JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("dynamic tool message payload must be a JSON object")
    return payload


def session_list_impl(
    *,
    all: bool,
    owner: str | None,
    agent: str | None,
    status: str | None,
    limit: int,
    ps_impl: Callable[..., list[dict[str, Any]]],
) -> str:
    sessions = ps_impl(all=all, owner=owner, agent=agent, status=status, limit=limit)
    return json.dumps(sessions)


def _find_session(session_id: str, sessions: list[dict[str, Any]]) -> dict[str, Any] | None:
    return next((s for s in sessions if s.get("run_id") == session_id or s.get("correlation_id") == session_id), None)


def session_show_impl(
    *,
    session_id: str,
    ps_impl: Callable[..., list[dict[str, Any]]],
) -> str:
    session = _find_session(session_id, ps_impl(all=True))
    if not session:
        return json.dumps({"error": f"Session {session_id} not found"})
    return json.dumps(session)


def session_logs_impl(
    *,
    session_id: str,
    stderr: bool,
    tail: int,
    logs_impl: Callable[..., str | None],
) -> str:
    res = logs_impl(session_id=session_id, stderr=stderr, follow=False, tail=tail)
    return "" if res is None else res


def session_send_impl(
    *,
    session_id: str,
    message: str,
    msg_type: str,
    send_impl: Callable[..., tuple[bool, str]],
) -> str:
    if msg_type == "dynamic_tool_register":
        payload = _parse_dynamic_message(message)
        spec = DynamicToolSpec(
            name=str(payload.get("name", "")).strip(),
            description=str(payload.get("description", "")),
            input_schema=payload.get("input_schema", {}),
        )
        registered = _dynamic_registry.register_dynamic_tool(session_id, spec)
        return json.dumps(
            {
                "success": True,
                "registered": {
                    "name": registered.name,
                    "description": registered.description,
                    "input_schema": registered.input_schema,
                },
            },
            
        )

    if msg_type == "dynamic_tool_list":
        tools = _dynamic_registry.list_dynamic_tools(session_id)
        return json.dumps(
            {
                "success": True,
                "tools": [
                    {"name": tool.name, "description": tool.description, "input_schema": tool.input_schema}
                    for tool in tools
                ],
            },
            
        )

    if msg_type == "dynamic_tool_invoke":
        payload = _parse_dynamic_message(message)
        name = str(payload.get("name", "")).strip()
        arguments = payload.get("arguments", {})
        timeout_seconds = payload.get("timeout_seconds")
        if not isinstance(arguments, dict):
            raise ValueError("dynamic tool invoke arguments must be a JSON object")
        if timeout_seconds is not None:
            try:
                timeout_seconds = float(timeout_seconds)
            except (TypeError, ValueError) as exc:
                raise ValueError("dynamic tool invoke timeout_seconds must be numeric") from exc
        call = _dynamic_registry.create_tool_call(session_id, name, arguments, timeout_seconds=timeout_seconds)
        event = _dynamic_registry.tool_call_requested_event(call)
        return json.dumps({"success": True, "event": event})

    if msg_type == "dynamic_tool_complete":
        payload = _parse_dynamic_message(message)
        call_id = str(payload.get("callId", "")).strip()
        if not call_id:
            raise ValueError("dynamic tool completion requires non-empty callId")
        success = bool(payload.get("success", False))
        output = payload.get("output")
        error = payload.get("error")
        if not success and error is None and output is None:
            raise ValueError("failed dynamic tool completion requires error or output payload")
        try:
            result = _dynamic_registry.resolve_tool_call_for_session(
                session_id=session_id,
                call_id=call_id,
                output=output,
                success=success,
                error=error,
            )
        except TimeoutError as exc:
            raise ValueError(str(exc)) from exc
        event = _dynamic_registry.tool_call_completed_event(result)
        return json.dumps({"success": True, "event": event})

    ok, msg = send_impl(session_id, message, msg_type=msg_type)
    return json.dumps({"success": ok, "message": msg})


def session_attach_hint_impl(
    *,
    session_id: str,
    ps_impl: Callable[..., list[dict[str, Any]]],
) -> str:
    session = _find_session(session_id, ps_impl(all=True))
    if not session:
        return json.dumps({"error": f"Session {session_id} not found"})

    interactivity = session.get("interactivity")
    attach_target = session.get("attach_target") or {}

    if interactivity == "tmux" or attach_target.get("tmux_pane"):
        pane = attach_target.get("tmux_pane") or session_id
        return json.dumps(
            {
                "mode": "tmux",
                "command": f"thegent session attach {session_id}",
                "raw_command": f"tmux attach-session -t {pane}",
                "hint": "Attach via tmux",
            },
            
        )

    if interactivity == "headless-holdpty":
        return json.dumps(
            {
                "mode": "holdpty",
                "command": f"thegent session attach {session_id}",
                "hint": "Attach via holdpty wrapper",
            },
            
        )

    return json.dumps(
        {
            "mode": "none",
            "hint": "Session does not support interactive attachment. Use 'thegent session logs --follow' instead.",
        },
        
    )
