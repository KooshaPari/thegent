"""WL-120 B90-W2-D1: Dynamic client tool registration group.

Extracted from mcp/server.py — three @mcp.tool decorators that implement
WL-105 client-owned dynamic tool registration:

  - thegent_register_tool
  - thegent_complete_tool_call
  - thegent_list_dynamic_tools

These are passed back as named attributes by register_dynamic_registry_tools()
so that server.py can assign them to module-level names for backward compat.

# @trace WL-120 B90-W2-D1
"""

from __future__ import annotations

import orjson as json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastmcp import FastMCP


def register_dynamic_registry_tools(
    *,
    mcp: "FastMCP",
    server_tools_sessions: Any,
    error_result: Any,
) -> tuple[Any, Any, Any]:
    """Register the three dynamic-client-tool MCP tools and return them.

    Args:
        mcp: FastMCP instance to decorate tools onto.
        server_tools_sessions: Module providing _dynamic_registry attribute.
        error_result: Callable that formats structured error ToolResult.

    Returns:
        (thegent_register_tool, thegent_complete_tool_call, thegent_list_dynamic_tools)
    """

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    async def thegent_register_tool(
        session_id: str,
        name: str,
        description: str,
        input_schema: dict[str, Any],
    ) -> str:
        """Register a client-owned tool for a session (WL-105).

        The registered tool becomes available for the model to invoke during
        the session. When the model calls it, a tool_call_requested event is
        emitted to the client via thegent_session_send dynamic_tool_invoke flow.

        Args:
            session_id: The session this tool is scoped to.
            name: Unique tool name within the session.
            description: Human-readable description for the model.
            input_schema: JSON Schema object describing the tool's arguments.

        Returns: JSON with registered tool details.
        """
        from thegent.mcp.dynamic_tools import DynamicToolSpec

        spec = DynamicToolSpec(name=name, description=description, input_schema=input_schema)
        registered = server_tools_sessions._dynamic_registry.register_dynamic_tool(session_id, spec)
        return json.dumps(
            {
                "success": True,
                "registered": {
                    "name": registered.name,
                    "description": registered.description,
                    "input_schema": registered.input_schema,
                },
            },
            indent=2,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False})
    async def thegent_complete_tool_call(
        session_id: str,
        call_id: str,
        output: str,
        success: bool,
    ) -> str:
        """Deliver a client's response to a pending dynamic tool call (WL-105).

        The client calls this after receiving a tool_call_requested event. Raises
        KeyError if call_id is unknown (fail-loud: never silently drops unknown calls).

        Args:
            session_id: The session this call belongs to.
            call_id: The call_id from the tool_call_requested event.
            output: String output from the client-side tool execution.
            success: True if the tool succeeded.

        Returns: JSON with the tool_call_completed event payload.
        """
        result = server_tools_sessions._dynamic_registry.resolve_tool_call_for_session(
            session_id=session_id,
            call_id=call_id,
            output=output,
            success=success,
        )
        event = server_tools_sessions._dynamic_registry.tool_call_completed_event(result)
        return json.dumps({"success": True, "event": event}, indent=2)

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    async def thegent_list_dynamic_tools(
        session_id: str,
    ) -> str:
        """List all client-registered dynamic tools for a session (WL-105).

        Args:
            session_id: The session whose tool registry to query.

        Returns: JSON array of registered tool definitions.
        """
        tools = server_tools_sessions._dynamic_registry.list_dynamic_tools(session_id)
        return json.dumps(
            {
                "session_id": session_id,
                "tools": [
                    {"name": t.name, "description": t.description, "input_schema": t.input_schema} for t in tools
                ],
            },
            indent=2,
        ).decode()

    return thegent_register_tool, thegent_complete_tool_call, thegent_list_dynamic_tools
