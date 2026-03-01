"""Batch 4 MCP tool registrations extracted from server.py."""

from __future__ import annotations

from typing import Any, Callable, Literal

from fastmcp import FastMCP
from fastmcp.tools.tool import ToolResult


def register_batch4_tools(
    *,
    mcp: FastMCP,
    server_tools_catalog: Any,
    server_tools_skills: Any,
    server_tools_terminal: Any,
    skills_backend: Any,
    error_result: Callable[..., ToolResult],
    list_droids_impl: Callable[..., Any],
    get_default_cwd: Callable[..., Any],
    depends: Callable[..., Any],
) -> tuple[Any, Any, Any, Any, Any]:
    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_list_droids(
        cd: str | None = None,
        default_cwd: Any = depends(get_default_cwd),
    ) -> ToolResult:
        """
        List available droids.

        Args:
            cd: Optional working directory (or use meta.cwd in request)
            Returns: JSON string with list of droid names
        """
        return server_tools_catalog.thegent_list_droids_impl(
            cd=cd,
            default_cwd=default_cwd,
            list_droids_impl=list_droids_impl,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_list_skills() -> ToolResult:
        """List discoverable skills from the current discovery backend."""
        return server_tools_skills.thegent_list_skills_impl(
            backend=skills_backend,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    def thegent_activate_skill(skill_name: str) -> ToolResult:
        """Load and return a skill payload by name."""
        return server_tools_skills.thegent_activate_skill_impl(
            skill_name=skill_name,
            backend=skills_backend,
            error_result_impl=error_result,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_terminal_route(prompt: str, cd: str | None = None) -> ToolResult:
        """
        Route a prompt to an active terminal session if matching. Falls back to thegent_run if none found.
        Equivalent to: thegent route <prompt>
        """
        return server_tools_terminal.terminal_route_impl(
            prompt=prompt,
            cd=cd,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    def thegent_macos_run_script(
        script: str,
        language: Literal["applescript", "jxa"] = "applescript",
    ) -> str:
        """
        Run an AppleScript or JXA (JavaScript for Automation) script on macOS.

        Wraps *osascript* to give agents agent-driven desktop control on macOS.
        Returns a JSON object with ``{success, output, error}``.

        On non-macOS platforms the tool returns immediately with
        ``{success: false, error: "Not macOS"}``.

        Args:
            script:   Script source code to execute.
            language: Scripting language — ``"applescript"`` (default) or ``"jxa"``.
        """
        import json as _json

        from thegent_platform.automation.macos_desktop import MacOSDesktopAutomation

        automation = MacOSDesktopAutomation()

        result = automation.run_jxa(script) if language == "jxa" else automation.run_applescript(script)

        return _json.dumps(
            {
                "success": result.success,
                "output": result.output,
                "error": result.error,
            }
        )

    return (
        thegent_list_droids,
        thegent_list_skills,
        thegent_activate_skill,
        thegent_terminal_route,
        thegent_macos_run_script,
    )
