"""Prompt and handoff/governance wrapper registrations for MCP server."""

from __future__ import annotations

from typing import Any, Callable

from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult


def register_prompt_and_handoff_wrappers(
    *,
    mcp: FastMCP,
    server_workflow_prompts: Any,
    server_tools_governance: Any,
    govern_vet_impl: Callable[..., dict[str, Any]],
    server_tools_terminal: Any,
    resolve_cwd: Callable[..., Any],
    error_result: Callable[..., ToolResult],
    settings_factory: Callable[[], Any],
    escalate_list_impl: Callable[..., list[dict[str, Any]]],
) -> tuple[Any, Any, Any, Any, Any]:
    @mcp.prompt
    def thegent_run_agent(agent: str, prompt: str, cd: str | None = None, mode: str = "write") -> str:
        """
        Generate a prompt to run an agent synchronously.
        Use thegent_run tool to execute.
        """
        return server_workflow_prompts.thegent_run_agent_prompt_impl(
            agent=agent,
            prompt=prompt,
            cd=cd,
            mode=mode,
        )

    @mcp.prompt
    def thegent_create_wbs(feature: str, scope: str | None = None) -> str:
        """
        Generate a prompt to create a Work Breakdown Structure (WBS) for a feature.
        Use thegent_run with a planning agent (e.g. cursor, claude) to execute.
        """
        return server_workflow_prompts.thegent_create_wbs_prompt_impl(
            feature=feature,
            scope=scope,
        )

    @mcp.prompt
    def thegent_bg_task(agent: str, prompt: str, owner: str | None = None) -> str:
        """
        Generate a prompt to start an agent task in the background.
        Use thegent_bg tool to execute.
        """
        return server_workflow_prompts.thegent_bg_task_prompt_impl(
            agent=agent,
            prompt=prompt,
            owner=owner,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_govern_vet(
        run_id: str,
        policy: str = "default",
        session: str | None = None,
        dry_run: bool = False,
        org: str | None = None,
        project: str | None = None,
        environment: str | None = None,
        policy_id: str | None = None,
    ) -> ToolResult:
        """
        Vet a recorded run using Vetter policy checks (WL-098).
        Equivalent to: thegent govern vet <run_id> [--policy <name>] [--session <path>] [--dry-run]
        """
        return server_tools_governance.thegent_govern_vet_impl(
            run_id=run_id,
            policy=policy,
            session=session,
            dry_run=dry_run,
            org=org,
            project=project,
            environment=environment,
            policy_id=policy_id,
            govern_vet_impl=govern_vet_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_handoff(owner: str, cd: str | None = None) -> ToolResult:
        """
        Create a handoff snapshot for shift handoff (WP-4006). Transfers active runs to snapshot.
        Equivalent to: thegent orchestrate handoff <owner>
        """
        return server_tools_terminal.handoff_impl(
            owner=owner,
            cd=cd,
            resolve_cwd=resolve_cwd,
            error_result=error_result,
            settings_factory=settings_factory,
            escalate_list_impl=escalate_list_impl,
        )

    return (
        thegent_run_agent,
        thegent_create_wbs,
        thegent_bg_task,
        thegent_govern_vet,
        thegent_handoff,
    )
