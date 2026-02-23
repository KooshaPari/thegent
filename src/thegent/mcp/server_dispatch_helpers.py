"""Helper utilities extracted from MCP server dispatch paths."""

from __future__ import annotations

import orjson as json
from pathlib import Path
from typing import Any


def write_session_control_file(session_root: Path, session_id: str, filename: str, content: str) -> None:
    """Create a session control file (e.g. takeover/STOP) under session dir."""
    session_dir = session_root / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / filename).write_text(content)


def normalize_bg_routing(
    routing: str | None,
    default_routing: str | None,
    failover: bool,
) -> tuple[str, str, str | None, bool]:
    """Normalize requested policy and derive lookup/child routing semantics."""
    from thegent.models import normalize_route_policy

    requested_policy = routing or default_routing or "prefer_direct"
    try:
        requested_policy = normalize_route_policy(requested_policy)
    except ValueError:
        requested_policy = "prefer_direct"

    route_lookup_policy = requested_policy
    if route_lookup_policy == "failover":
        failover = True
        route_lookup_policy = "prefer_direct"

    routing_for_child = requested_policy if routing is not None else None
    return requested_policy, route_lookup_policy, routing_for_child, failover


def build_route_request_payload(
    include_contract: bool,
    requested_model: str | None,
    requested_provider_hint: str | None,
    policy: str | None,
    resolved_model_alias: str | None,
    resolved_agent: str | None,
) -> dict[str, str] | None:
    """Build route request payload included in background dispatch output."""
    if not include_contract:
        return None
    return {
        "requested_model": requested_model or "",
        "requested_provider_hint": requested_provider_hint or "",
        "policy": policy or "",
        "resolved_model_alias": resolved_model_alias or "",
        "resolved_agent": resolved_agent or "",
    }


def parse_acp_payload(payload: str) -> tuple[dict[str, Any] | None, str | None]:
    """Parse ACP payload JSON into context dict."""
    try:
        parsed = json.loads(payload) if payload else {}
    except json.JSONDecodeError as exc:
        return None, f"Invalid payload JSON: {exc}"
    if isinstance(parsed, dict):
        return parsed, None
    return None, "Invalid payload JSON: expected object"


def format_acp_response(
    *,
    success: bool,
    agent_url: str,
    elapsed_ms: int,
    result: str = "",
    error: str | None = None,
) -> str:
    """Render normalized ACP invoke response payload."""
    payload: dict[str, Any] = {
        "success": success,
        "result": result,
        "agent_url": agent_url,
        "elapsed_ms": elapsed_ms,
    }
    if error:
        payload["error"] = error
    return json.dumps(payload).decode()
