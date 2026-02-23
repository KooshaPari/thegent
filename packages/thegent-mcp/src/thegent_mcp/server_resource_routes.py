"""MCP resource route registrations extracted from server.py (WL-120)."""

from __future__ import annotations

from typing import Any, Callable

from fastmcp import FastMCP


def register_resource_routes(
    *,
    mcp: FastMCP,
    server_resource_sessions: Any,
    server_resource_catalog: Any,
    server_resource_workstream: Any,
    server_resource_contracts: Any,
    resource_session_contract_health_gate_helper: Callable[..., str],
    resource_session_contract_health_report_helper: Callable[..., str],
    resource_session_contract_health_trend_helper: Callable[..., str],
    ps_impl: Callable[..., Any],
    status_impl: Callable[..., Any],
    logs_impl: Callable[..., Any],
    dag_list_impl: Callable[..., Any],
    list_agents_impl: Callable[..., Any],
    list_models_impl: Callable[..., Any],
    session_contract_audit_impl: Callable[..., Any],
    session_contract_health_gate_impl: Callable[..., Any],
    session_contract_health_report_impl: Callable[..., Any],
    session_contract_health_trend_impl: Callable[..., Any],
    stable_json: Callable[[Any], str],
) -> tuple[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any, Any, Any, Any, Any]:
    @mcp.resource(
        "thegent://sessions{?include_contract}",
        mime_type="application/json",
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    def resource_sessions(include_contract: bool = False) -> str:
        """List all background sessions. Returns JSON array of session metadata."""
        return server_resource_sessions.resource_sessions_impl(
            include_contract=include_contract,
            ps_impl=ps_impl,
        )

    @mcp.resource(
        "thegent://session/{id}/meta{?include_contract}",
        mime_type="application/json",
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    def resource_session_meta(id: str, include_contract: bool = False) -> str:
        """Get session metadata (status, pid, owner) by ID."""
        return server_resource_sessions.resource_session_meta_impl(
            session_id=id,
            include_contract=include_contract,
            status_impl=status_impl,
        )

    @mcp.resource(
        "thegent://session/{id}/logs{?stderr,tail}",
        mime_type="text/plain",
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    def resource_session_logs(id: str, stderr: bool = False, tail: int | None = None) -> str:
        """Get logs from a background session. Use ?stderr=true for stderr, ?tail=N for last N lines."""
        return server_resource_sessions.resource_session_logs_impl(
            session_id=id,
            stderr=stderr,
            tail=tail,
            logs_impl=logs_impl,
        )

    @mcp.resource(
        "thegent://dag",
        mime_type="application/json",
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    def resource_dag() -> str:
        """Get DAG from .factory/dag-session.md as {frontmatter, tasks} JSON."""
        return server_resource_catalog.resource_dag_impl(dag_list_impl=dag_list_impl)

    @mcp.resource(
        "thegent://agents",
        mime_type="application/json",
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    def resource_agents() -> str:
        """List available agents. Returns JSON array of {name, backend}."""
        return server_resource_catalog.resource_agents_impl(list_agents_impl=list_agents_impl)

    @mcp.resource(
        "thegent://models{?provider,include_contract}",
        mime_type="application/json",
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    def resource_models(
        provider: str | None = None,
        include_contract: bool = False,
    ) -> str:
        """List models, optionally filtered by provider."""
        return server_resource_catalog.resource_models_impl(
            provider=provider,
            include_contract=include_contract,
            list_models_impl=list_models_impl,
        )

    @mcp.resource(
        "thegent://models/contract",
        mime_type="application/json",
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    def resource_models_contract() -> str:
        """Return model routing contract schema metadata."""
        return server_resource_catalog.resource_models_contract_impl()

    @mcp.resource(
        "thegent://workstream",
        mime_type="text/markdown",
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    def resource_workstream() -> str:
        """Get the canonical WORK_STREAM.md content."""
        return server_resource_workstream.resource_workstream_impl()

    @mcp.resource(
        "thegent://events/session-complete",
        mime_type="application/json",
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    def resource_events_session_complete() -> str:
        """Event stream for session completion events (for auto-launch system)."""
        return server_resource_workstream.resource_events_session_complete_impl()

    @mcp.resource(
        "thegent://workstream/db",
        mime_type="application/json",
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    def resource_workstream_db() -> str:
        """Workstream database metadata and schema info."""
        return server_resource_workstream.resource_workstream_db_impl()

    @mcp.resource(
        "thegent://sessions/contracts{?owner,all,missing_only,summary_only,strict}",
        mime_type="application/json",
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    def resource_session_contracts(
        owner: str | None = None,
        all: bool = False,
        missing_only: bool = False,
        summary_only: bool = False,
        strict: bool = False,
    ) -> str:
        """Contract audit for sessions including completeness summary."""
        return server_resource_contracts.resource_session_contracts_impl(
            owner=owner,
            all=all,
            missing_only=missing_only,
            summary_only=summary_only,
            strict=strict,
            session_contract_audit_impl=session_contract_audit_impl,
        )

    @mcp.resource(
        "thegent://sessions/contracts/health{?owner,all,strict,min_healthy_ratio,policy_profile,no_worse_than_baseline,regression_tolerance}",
        mime_type="application/json",
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    def resource_session_contract_health_gate(
        owner: str | None = None,
        all: bool = False,
        strict: bool = False,
        min_healthy_ratio: float = 1.0,
        policy_profile: str | None = None,
        no_worse_than_baseline: bool = False,
        regression_tolerance: float = 0.0,
    ) -> str:
        """
        Contract health gate for CI/automation and policy enforcement.
        Returns schema-aware payload with `schema_version` and `payload_type`.
        """
        return resource_session_contract_health_gate_helper(
            owner=owner,
            all=all,
            strict=strict,
            min_healthy_ratio=min_healthy_ratio,
            policy_profile=policy_profile,
            no_worse_than_baseline=no_worse_than_baseline,
            regression_tolerance=regression_tolerance,
            resource_impl=server_resource_contracts.resource_session_contract_health_gate_impl,
            session_contract_health_gate_impl=session_contract_health_gate_impl,
            stable_json=stable_json,
        )

    @mcp.resource(
        "thegent://sessions/contracts/report{?owner,all,strict,top_blocked,policy_profile,no_worse_than_baseline,regression_tolerance}",
        mime_type="application/json",
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    def resource_session_contract_health_report(
        owner: str | None = None,
        all: bool = False,
        strict: bool = False,
        top_blocked: int = 25,
        policy_profile: str | None = None,
        no_worse_than_baseline: bool = False,
        regression_tolerance: float = 0.0,
    ) -> str:
        """
        Contract health report for issue/owner triage and observability.
        Returns schema-aware payload with `schema_version` and `payload_type`.
        """
        return resource_session_contract_health_report_helper(
            owner=owner,
            all=all,
            strict=strict,
            top_blocked=top_blocked,
            policy_profile=policy_profile,
            no_worse_than_baseline=no_worse_than_baseline,
            regression_tolerance=regression_tolerance,
            resource_impl=server_resource_contracts.resource_session_contract_health_report_impl,
            session_contract_health_report_impl=session_contract_health_report_impl,
            stable_json=stable_json,
        )

    @mcp.resource(
        "thegent://sessions/contracts/trend{?payload_type,owner,all,strict,policy_profile,min_healthy_ratio,top_blocked,limit}",
        mime_type="application/json",
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    def resource_session_contract_health_trend(
        payload_type: str = "session_contract_health_report",
        owner: str | None = None,
        all: bool = False,
        strict: bool = False,
        policy_profile: str | None = None,
        min_healthy_ratio: float = 1.0,
        top_blocked: int = 25,
        limit: int = 20,
    ) -> str:
        """Contract health trend snapshots for a scoped report/gate policy context."""
        return resource_session_contract_health_trend_helper(
            payload_type=payload_type,
            owner=owner,
            all=all,
            strict=strict,
            policy_profile=policy_profile,
            min_healthy_ratio=min_healthy_ratio,
            top_blocked=top_blocked,
            limit=limit,
            resource_impl=server_resource_contracts.resource_session_contract_health_trend_impl,
            session_contract_health_trend_impl=session_contract_health_trend_impl,
            stable_json=stable_json,
        )

    return (
        resource_sessions,
        resource_session_meta,
        resource_session_logs,
        resource_dag,
        resource_agents,
        resource_models,
        resource_models_contract,
        resource_workstream,
        resource_events_session_complete,
        resource_workstream_db,
        resource_session_contracts,
        resource_session_contract_health_gate,
        resource_session_contract_health_report,
        resource_session_contract_health_trend,
    )
