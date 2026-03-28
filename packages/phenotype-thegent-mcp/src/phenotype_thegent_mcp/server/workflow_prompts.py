"""Workflow resource/prompt registrations for MCP server."""

from typing import Any

from fastmcp import FastMCP


def register_workflow_prompts(
    *,
    mcp: FastMCP,
    server_resource_workflow: Any,
) -> tuple[Any, Any, Any, Any, Any]:
    @mcp.resource(
        "thegent://workflow/triggers",
        mime_type="text/markdown",
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    def resource_workflow_triggers() -> str:
        """Workflow instructions: idea→research→spec, quality green, next item. Injected on UserPromptSubmit."""
        return server_resource_workflow.resource_workflow_triggers_impl()

    @mcp.prompt
    def phenotype_thegent_workflow_idea(idea: str) -> str:
        """
        Instructions for idea/task prompts: dump research, create specs, add work items.
        Use when user gives research/explore/build/implement/design/create/feature prompts.
        """
        return server_resource_workflow.phenotype_thegent_workflow_idea_impl(idea)

    @mcp.prompt
    def phenotype_thegent_workflow_quality_green() -> str:
        """
        Instructions to run full quality pipeline until green.
        Use when user says "get task quality green", "quality green", "make quality pass".
        """
        return server_resource_workflow.phenotype_thegent_workflow_quality_green_impl()

    @mcp.prompt
    def phenotype_thegent_workflow_next_item() -> str:
        """
        Instructions to find and execute the next work item from the unified stream.
        Use when user says "find the next thing to do", "what next", "pick next".
        """
        return server_resource_workflow.phenotype_thegent_workflow_next_item_impl()

    @mcp.prompt
    def phenotype_thegent_workflow_gardening() -> str:
        """
        Instructions for gardening: check gov traceability, tests, plan items; dispatch; converge to empty backlog and complete green.
        Use when user says "garden", "converge", "empty backlog", "complete green".
        """
        return server_resource_workflow.phenotype_thegent_workflow_gardening_impl()

    return (
        resource_workflow_triggers,
        phenotype_thegent_workflow_idea,
        phenotype_thegent_workflow_quality_green,
        phenotype_thegent_workflow_next_item,
        phenotype_thegent_workflow_gardening,
    )


def phenotype_thegent_run_agent_prompt_impl(*, agent: str, prompt: str, cd: str | None, mode: str) -> str:
    cd_hint = f" in directory {cd}" if cd else ""
    return f"Run agent '{agent}'{cd_hint} with mode '{mode}'. Task: {prompt}"


def phenotype_thegent_create_wbs_prompt_impl(*, feature: str, scope: str | None) -> str:
    scope_hint = f" Scope: {scope}." if scope else ""
    return (
        f"Create a phased WBS (Work Breakdown Structure) for: {feature}.{scope_hint} "
        "Use phases (Discovery, Design, Build, Test, Deploy) and DAG-style dependencies."
    )


def phenotype_thegent_bg_task_prompt_impl(*, agent: str, prompt: str, owner: str | None) -> str:
    owner_hint = f" (owner: {owner})" if owner else ""
    return f"Start background task: agent '{agent}'{owner_hint}. Task: {prompt}"


def register_workflow_gardening_resource(
    *,
    mcp: FastMCP,
    server_resource_workflow: Any,
) -> Any:
    @mcp.resource(
        "thegent://workflow/gardening",
        mime_type="text/markdown",
        annotations={"readOnlyHint": True, "idempotentHint": True},
    )
    def resource_workflow_gardening() -> str:
        """Gardening workflow: converge to empty backlog and complete green."""
        return server_resource_workflow.resource_workflow_gardening_impl()

    return resource_workflow_gardening
