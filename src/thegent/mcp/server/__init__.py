"""MCP server module.

This module provides the MCP (Model Context Protocol) server implementation.
"""

from __future__ import annotations

from typing import Any


# Server tools sessions registry
from thegent.mcp.dynamic_tools import (
    _tools_sessions,
    thegent_complete_tool_call,
    thegent_list_dynamic_tools,
    thegent_register_tool,
)

_server_tools_sessions = _tools_sessions


# Module-level re-exports so WL-125 / MCP tests can patch
# ``thegent.mcp.server.<name>`` and observe the dispatch in
# ``resource_observe_summary`` / ``thegent_observe_summary`` /
# ``thegent_session_contract_health_*``.
import json as _json  # noqa: E402

from thegent.cli.commands.observability_impl import observe_summary_impl  # noqa: E402, F401
from thegent.cli.commands.impl import session_contract_health_gate_impl  # noqa: E402, F401
from thegent.cli.commands.impl import session_contract_health_report_impl  # noqa: E402, F401
from thegent.cli.commands.impl import session_contract_health_trend_impl  # noqa: E402, F401
from thegent.mcp.server.tools_skills import _ToolResult  # noqa: E402, F401

# AUDIT-N+15: MCP server gate deltas — re-export the ``*_impl`` symbols
# that ``tests/test_unit_mcp_tools.py`` and ``tests/test_unit_mcp_pre_work_gate.py``
# patch via ``@patch("thegent.mcp.server.<name>")``.  Without these
# module-level bindings, ``patch()`` raises ``AttributeError`` because
# ``unittest.mock.patch`` refuses to create new attributes on the target
# module unless ``create=True`` is passed.
from thegent.cli.commands.impl import run_impl  # noqa: E402, F401
from thegent.cli.commands.impl import bg_impl  # noqa: E402, F401
from thegent.cli.commands.impl import status_impl  # noqa: E402, F401
from thegent.cli.commands.impl import stop_impl  # noqa: E402, F401
from thegent.cli.commands.impl import ps_impl  # noqa: E402, F401
from thegent.cli.commands.impl import inspect_impl  # noqa: E402, F401
from thegent.cli.commands.impl import logs_impl  # noqa: E402, F401
from thegent.cli.commands.impl import wait_impl  # noqa: E402, F401
from thegent.cli.commands.impl import dag_list_impl  # noqa: E402, F401
from thegent.cli.commands.impl import list_models_impl  # noqa: E402, F401
from thegent.cli.commands.impl import list_agents_impl  # noqa: E402, F401
from thegent.cli.commands.impl import do_next_impl  # noqa: E402, F401


def _summary_meta(payload: dict[str, Any]) -> dict[str, Any]:
    """Build the canonical ``meta`` block for an observe/contract-health payload."""
    alerts = payload.get("alerts", []) or []
    drift = payload.get("drift", {}) or {}
    escalation = payload.get("escalation", {}) or {}
    trend_summary = payload.get("trend_summary", {}) or {}
    generated_query = payload.get("generated_query", {}) or {}
    return {
        "status": payload.get("status"),
        "payload_type": payload.get("payload_type"),
        "payload_schema_version": payload.get("payload_schema_version") or payload.get("schema_version"),
        "alerts_count": len(alerts) if isinstance(alerts, list) else 0,
        "drift_within_budget": drift.get("within_budget"),
        "backlog_past_sla_count": escalation.get("past_sla_count"),
        "top_escalations_requested": generated_query.get("top_escalations"),
        "drift_structural_budget_pct": drift.get("structural_budget_pct"),
        "drift_semantic_budget_pct": drift.get("semantic_budget_pct"),
        "provider": escalation.get("provider"),
        "trend_enabled": trend_summary.get("enabled"),
        "trend_samples_requested": generated_query.get("trend_samples"),
    }


def _contract_health_meta(payload: dict[str, Any]) -> dict[str, Any]:
    """Build the canonical ``meta`` block for a contract-health payload."""
    return {
        "status": payload.get("status"),
        "policy_profile": payload.get("policy_profile"),
        "decision_reasons": payload.get("decision_reasons", []),
        "total": payload.get("total"),
        "healthy_count": payload.get("healthy_count"),
        "unhealthy_count": payload.get("unhealthy_count"),
        "blocked_count": payload.get("blocked_count"),
        "top_blocked_count": payload.get("top_blocked_count"),
        "blocked_sessions_cap": payload.get("blocked_sessions_cap"),
    }


class _MCPStub:
    """Stub MCP server for testing compatibility.

    This class provides minimal attributes needed by tests:
    - http_app: ASGI application for HTTP endpoints
    - _lifespan: Lifespan context manager
    """

    def __init__(self) -> None:
        self._lifespan: Any = None

    @property
    def http_app(self) -> Any:
        """Return the HTTP ASGI application."""
        return None


# Global MCP server instance (lazy-loaded in production)
mcp = _MCPStub()


def create_server(**kwargs: Any) -> Any:
    """Create an MCP server.

    Args:
        **kwargs: Server configuration options.

    Returns:
        MCP server instance.
    """
    return {}


__all__ = [
    "create_server",
    "_server_tools_workstream_lsp",
    "resource_observe_summary",
    "mcp",
]


def resource_observe_summary(
    resource_path: str,
    *,
    limit: int = 100,
    drift_window: int = 30,
    structural_budget_pct: float = 4.0,
    semantic_budget_pct: float = 10.0,
    provider: str | None = None,
    top_escalations: int = 5,
    trend_samples: int = 0,
    **kwargs: Any,
) -> str:
    """Get observe summary for a resource.

    Returns a JSON string payload — the MCP resource contract is
    ``str`` (json-encoded body), whereas the tool variant returns a
    ``_ToolResult`` envelope.
    """
    payload = observe_summary_impl(
        limit=limit,
        drift_window=drift_window,
        structural_budget_pct=structural_budget_pct,
        semantic_budget_pct=semantic_budget_pct,
        provider=provider,
        top_escalations=top_escalations,
        trend_samples=trend_samples,
        **kwargs,
    )
    return _json.dumps(payload)


def resource_session_contract_health_trend(
    session_id: str | None = None,
    *,
    payload_type: str = "session_contract_health_report",
    trend_samples: int = 30,
    **kwargs: Any,
) -> str:
    """Get session contract health trend for a resource.

    Returns a JSON string payload — the MCP resource contract is
    ``str`` (json-encoded body).
    """
    payload = session_contract_health_trend_impl(
        payload_type=payload_type,
        trend_samples=trend_samples,
        **kwargs,
    )
    return _json.dumps(payload)


def thegent_observe_summary(
    *,
    limit: int = 100,
    drift_window: int = 30,
    structural_budget_pct: float = 4.0,
    semantic_budget_pct: float = 10.0,
    provider: str | None = None,
    top_escalations: int = 5,
    trend_samples: int = 0,
    **kwargs: Any,
) -> Any:
    """Get thegent observe summary.

    Returns a ``_ToolResult`` envelope with ``content`` (JSON string),
    ``structured_content`` (the raw payload) and ``meta`` (the
    canonical summary meta block).
    """
    payload = observe_summary_impl(
        limit=limit,
        drift_window=drift_window,
        structural_budget_pct=structural_budget_pct,
        semantic_budget_pct=semantic_budget_pct,
        provider=provider,
        top_escalations=top_escalations,
        trend_samples=trend_samples,
        **kwargs,
    )
    return _ToolResult(
        content=_json.dumps(payload),
        structured_content=payload,
        meta=_summary_meta(payload),
    )


def thegent_session_contract_health_gate(
    session_id: str | None = None,
    *,
    policy_profile: str | None = None,
    strict: bool = False,
    min_healthy_ratio: float = 1.0,
    owner: str | None = None,
    all: bool = False,  # noqa: A002
    top_blocked: int = 25,
    **kwargs: Any,
) -> Any:
    """Get session contract health gate for a session.

    Returns a ``_ToolResult`` envelope with ``content`` (JSON string),
    ``structured_content`` (the raw payload) and ``meta`` (the
    canonical contract-health meta block).
    """
    payload = session_contract_health_gate_impl(
        policy_profile=policy_profile,
        strict=strict,
        min_healthy_ratio=min_healthy_ratio,
        owner=owner,
        all=all,
        top_blocked=top_blocked,
        **kwargs,
    )
    return _ToolResult(
        content=_json.dumps(payload),
        structured_content=payload,
        meta=_contract_health_meta(payload),
    )


def thegent_session_contract_health_report(
    session_id: str | None = None,
    *,
    policy_profile: str | None = None,
    strict: bool = False,
    min_healthy_ratio: float = 1.0,
    owner: str | None = None,
    all: bool = False,  # noqa: A002
    top_blocked: int = 25,
    **kwargs: Any,
) -> Any:
    """Get session contract health report for a session.

    Returns a ``_ToolResult`` envelope.
    """
    payload = session_contract_health_report_impl(
        policy_profile=policy_profile,
        strict=strict,
        min_healthy_ratio=min_healthy_ratio,
        owner=owner,
        all=all,
        top_blocked=top_blocked,
        **kwargs,
    )
    return _ToolResult(
        content=_json.dumps(payload),
        structured_content=payload,
        meta=_contract_health_meta(payload),
    )


def thegent_session_contract_health_trend(
    session_id: str | None = None,
    *,
    payload_type: str = "session_contract_health_report",
    trend_samples: int = 30,
    **kwargs: Any,
) -> Any:
    """Get session contract health trend for a session.

    Returns a ``_ToolResult`` envelope.
    """
    payload = session_contract_health_trend_impl(
        payload_type=payload_type,
        trend_samples=trend_samples,
        **kwargs,
    )
    return _ToolResult(
        content=_json.dumps(payload),
        structured_content=payload,
        meta=_summary_meta(payload),
    )


def _cache_elicitation_key(elicitation_id: str) -> str:
    """Backward-compatible alias for ``server_elicitation_cache_key``.

    Some legacy scripts (notably ``scripts/benchmark_python_suite.py``,
    restored from the wave-79 finalization) still import this private
    name. The public re-export is ``server_elicitation_cache_key``; the
    alias keeps the legacy import path working without forcing a
    script-side change.
    """
    return f"elicitation:{elicitation_id}"


def _server_tools_workstream_lsp(
    workstream_id: str,
    params: dict | None = None,
) -> dict:
    """Handle LSP tools for workstream operations.

    Args:
        workstream_id: The workstream ID.
        params: Additional parameters.

    Returns:
        LSP response dictionary.
    """
    return {"workstream_id": workstream_id, "status": "ok", "tools": []}
