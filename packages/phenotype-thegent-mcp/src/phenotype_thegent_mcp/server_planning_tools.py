"""Planning/escalation MCP tool registration helpers."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP
from fastmcp._vendor.docket_di import Depends
from fastmcp.server.dependencies import CurrentContext
from fastmcp.tools.tool import ToolResult


def register_planning_tools(
    *,
    mcp: FastMCP,
    server_tools_planning: Any,
    server_tools_locking_planning: Any,
    server_tools_contract_observe: Any,
    server_tools_escalation: Any,
    get_default_cwd: Any,
    resolve_cwd: Any,
    elicit_cwd_msg: str,
    elicit_timeout_s: int,
    accepted_elicitation_type: Any,
    declined_elicitation_type: Any,
    cancelled_elicitation_type: Any,
    dag_list_impl: Any,
    do_next_impl: Any,
    wait_next_impl: Any,
    history_impl: Any,
    plan_analyze_impl: Any,
    retry_impl: Any,
    incorporate_impl: Any,
    dag_status_impl: Any,
    escalate_list_impl: Any,
    escalate_add_impl: Any,
    escalate_approve_impl: Any,
    escalate_resolve_impl: Any,
    govern_list_pending_impl: Any,
    error_result: Any,
) -> tuple[object, ...]:
    """Register planning/escalation MCP tools and return stable handler bindings."""

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    async def phenotype_thegent_dag_list(
        cd: str | None = None,
        ctx: Any = CurrentContext(),
        default_cwd: Any = Depends(get_default_cwd),
    ) -> ToolResult:
        """List DAG tasks from .factory/dag-session.md."""
        return await server_tools_planning.phenotype_thegent_dag_list_impl(
            cd=cd,
            default_cwd=default_cwd,
            ctx=ctx,
            resolve_cwd=resolve_cwd,
            elicit_cwd_msg=elicit_cwd_msg,
            elicit_timeout_s=elicit_timeout_s,
            accepted_elicitation_type=accepted_elicitation_type,
            declined_elicitation_type=declined_elicitation_type,
            cancelled_elicitation_type=cancelled_elicitation_type,
            dag_list_impl=dag_list_impl,
            error_result_impl=error_result,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def phenotype_thegent_do_next(cd: str | None = None, limit: int = 5) -> ToolResult:
        """Find the next actionable work items from planning and escalation surfaces."""
        return server_tools_planning.phenotype_thegent_do_next_impl(
            cd=cd,
            limit=limit,
            do_next_impl=do_next_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def phenotype_thegent_lock_resource(resource: str, ttl: int = 60, cd: str | None = None) -> ToolResult:
        """Acquire an exclusive lock on a resource."""
        return server_tools_locking_planning.phenotype_thegent_lock_resource_impl(
            resource=resource,
            ttl=ttl,
            cd=cd,
            error_result_impl=error_result,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def phenotype_thegent_unlock_resource(resource: str, token: str, cd: str | None = None) -> ToolResult:
        """Release an exclusive lock on a resource."""
        return server_tools_locking_planning.phenotype_thegent_unlock_resource_impl(
            resource=resource,
            token=token,
            cd=cd,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def phenotype_thegent_verify_context(files: list[str], cd: str | None = None) -> ToolResult:
        """Verify if any given files have changed (OCC check)."""
        return server_tools_locking_planning.phenotype_thegent_verify_context_impl(
            files=files,
            cd=cd,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def phenotype_thegent_plan_get_next(cd: str | None = None) -> ToolResult:
        """Get first work item prompt for scripting."""
        return server_tools_planning.phenotype_thegent_plan_get_next_impl(
            cd=cd,
            do_next_impl=do_next_impl,
            error_result_impl=error_result,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": False})
    def phenotype_thegent_plan_wait_next(
        cd: str | None = None,
        poll: float = 2.0,
        timeout: float = 0.0,
        sources: str = "dag,do_next,escalation,inbox",
    ) -> ToolResult:
        """Block until next actionable work exists."""
        return server_tools_planning.phenotype_thegent_plan_wait_next_impl(
            cd=cd,
            poll=poll,
            timeout=timeout,
            sources=sources,
            wait_next_impl=wait_next_impl,
            error_result_impl=error_result,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def phenotype_thegent_history(limit: int = 50) -> ToolResult:
        """List execution history."""
        return server_tools_planning.phenotype_thegent_history_impl(
            limit=limit,
            history_impl=history_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def phenotype_thegent_plan_progress(limit: int = 10) -> ToolResult:
        """Show recent runs with smaller default limit."""
        return server_tools_planning.phenotype_thegent_plan_progress_impl(
            limit=limit,
            history_impl=history_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def phenotype_thegent_plan_analyze(
        cd: str | None = None,
        pert: bool = False,
        resources: bool = False,
        continuity: bool = False,
    ) -> ToolResult:
        """Run planning simulation overlays (XD1-XD3)."""
        return server_tools_planning.phenotype_thegent_plan_analyze_impl(
            cd=cd,
            pert=pert,
            resources=resources,
            continuity=continuity,
            plan_analyze_impl=plan_analyze_impl,
            error_result_impl=error_result,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def phenotype_thegent_retry(
        run_id: str,
        agent_override: str | None = None,
        failover: bool = False,
        cd: str | None = None,
        override_reason: str | None = None,
    ) -> ToolResult:
        """Retry a failed run by run_id."""
        return server_tools_locking_planning.phenotype_thegent_retry_impl(
            run_id=run_id,
            agent_override=agent_override,
            failover=failover,
            cd=cd,
            override_reason=override_reason,
            retry_impl=retry_impl,
            error_result_impl=error_result,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def phenotype_thegent_plan_incorporate(cd: str | None = None, dry_run: bool = False) -> ToolResult:
        """Merge planning fragments into backlog."""
        return server_tools_locking_planning.phenotype_thegent_plan_incorporate_impl(
            cd=cd,
            dry_run=dry_run,
            incorporate_impl=incorporate_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def phenotype_thegent_dag_status(cd: str | None = None) -> ToolResult:
        """Return DAG item statuses."""
        return server_tools_contract_observe.phenotype_thegent_dag_status_impl(
            cd=cd,
            dag_status_impl=dag_status_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def phenotype_thegent_escalate_list(past_sla_only: bool = False, limit: int = 50) -> ToolResult:
        """List escalation queue items."""
        return server_tools_escalation.phenotype_thegent_escalate_list_impl(
            past_sla_only=past_sla_only,
            limit=limit,
            escalate_list_impl=escalate_list_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def phenotype_thegent_escalate_add(
        run_id: str,
        reason: str,
        sla_minutes: int = 30,
        owner: str | None = None,
        agent: str | None = None,
        lane: str = "standard",
        priority: int = 0,
    ) -> ToolResult:
        """Add a blocked run to the escalation queue."""
        return server_tools_escalation.phenotype_thegent_escalate_add_impl(
            run_id=run_id,
            reason=reason,
            sla_minutes=sla_minutes,
            owner=owner,
            agent=agent,
            lane=lane,
            priority=priority,
            escalate_add_impl=escalate_add_impl,
            error_result_impl=error_result,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def phenotype_thegent_escalate_approve(run_id: str) -> ToolResult:
        """Approve an escalation (policy override)."""
        return server_tools_escalation.phenotype_thegent_escalate_approve_impl(
            run_id=run_id,
            escalate_approve_impl=escalate_approve_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def phenotype_thegent_escalate_resolve(run_id: str, resolution: str = "resolved") -> ToolResult:
        """Mark an escalation item as resolved."""
        return server_tools_escalation.phenotype_thegent_escalate_resolve_impl(
            run_id=run_id,
            resolution=resolution,
            escalate_resolve_impl=escalate_resolve_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def phenotype_thegent_govern_list_pending() -> ToolResult:
        """List all pending HITL approval requests."""
        return server_tools_escalation.phenotype_thegent_govern_list_pending_impl(
            govern_list_pending_impl=govern_list_pending_impl,
        )

    return (
        phenotype_thegent_dag_list,
        phenotype_thegent_do_next,
        phenotype_thegent_lock_resource,
        phenotype_thegent_unlock_resource,
        phenotype_thegent_verify_context,
        phenotype_thegent_plan_get_next,
        phenotype_thegent_plan_wait_next,
        phenotype_thegent_history,
        phenotype_thegent_plan_progress,
        phenotype_thegent_plan_analyze,
        phenotype_thegent_retry,
        phenotype_thegent_plan_incorporate,
        phenotype_thegent_dag_status,
        phenotype_thegent_escalate_list,
        phenotype_thegent_escalate_add,
        phenotype_thegent_escalate_approve,
        phenotype_thegent_escalate_resolve,
        phenotype_thegent_govern_list_pending,
    )
