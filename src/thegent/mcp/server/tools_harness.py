"""Harness interaction tool handlers for MCP server."""

from __future__ import annotations

import json
from typing import Any

from thegent.agents.unified_session_index import HarnessActionError, HarnessTUIMapper, HarnessType


def register_harness_tools(
    mcp: Any,
    server_tools_harness: Any,
) -> tuple[Any, Any, Any, Any]:
    """Register harness interaction tools with the MCP server.

    Returns:
        Tuple of (thegent_harness_interact, thegent_harness_list_actions,
                  thegent_harness_get_command, thegent_harness_register_host)
    """

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    async def thegent_harness_interact(
        harness: str,
        action: str,
        host_id: str | None = None,
        prompt: str | None = None,
        session_id: str | None = None,
    ) -> str:
        """Execute a harness action via HarnessTUIMapper.

        Args:
            harness: Harness type (cursor, codex, claude, ante, droid)
            action: Abstract action (send_message, attach_terminal, view_history, etc.)
            host_id: Optional remote host identifier
            prompt: Prompt/message for send_message action
            session_id: Session ID for session-related actions

        Returns:
            JSON string with success status, output, and any errors
        """
        return server_tools_harness.harness_interact_impl(
            harness=harness,
            action=action,
            host_id=host_id,
            prompt=prompt,
            session_id=session_id,
        )

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    async def thegent_harness_list_actions() -> str:
        """List all available harness actions.

        Returns:
            JSON string with list of available actions
        """
        return server_tools_harness.harness_list_actions_impl()

    @mcp.tool(annotations={"readOnlyHint": True, "idempotentHint": True})
    async def thegent_harness_get_command(
        harness: str,
        action: str,
    ) -> str:
        """Get the command template for a harness-action pair.

        Args:
            harness: Harness type
            action: Abstract action

        Returns:
            JSON string with command template or error
        """
        return server_tools_harness.harness_get_command_impl(
            harness=harness,
            action=action,
        )

    @mcp.tool(annotations={"readOnlyHint": False, "idempotentHint": False})
    async def thegent_harness_register_host(
        host_id: str,
        harness: str,
        command_prefix: str = "",
        custom_actions: dict[str, str] | None = None,
    ) -> str:
        """Register a new host device with custom command mappings.

        Args:
            host_id: Unique identifier for the host
            harness: The harness type this host uses
            command_prefix: Prefix for all commands (e.g., "ssh user@host")
            custom_actions: Override commands for specific actions

        Returns:
            JSON string with registration status
        """
        return server_tools_harness.harness_register_host_impl(
            host_id=host_id,
            harness=harness,
            command_prefix=command_prefix,
            custom_actions=custom_actions,
        )

    return (
        thegent_harness_interact,
        thegent_harness_list_actions,
        thegent_harness_get_command,
        thegent_harness_register_host,
    )


def harness_interact_impl(
    *,
    harness: str,
    action: str,
    host_id: str | None = None,
    prompt: str | None = None,
    session_id: str | None = None,
) -> str:
    """Execute a harness action via HarnessTUIMapper.

    Args:
        harness: Harness type (cursor, codex, claude, ante, droid)
        action: Abstract action (send_message, attach_terminal, view_history, etc.)
        host_id: Optional remote host identifier
        prompt: Prompt/message for send_message action
        session_id: Session ID for session-related actions

    Returns:
        JSON string with success status, output, and any errors
    """
    try:
        harness_type = HarnessType(harness.lower())
    except ValueError:
        return json.dumps(
            {
                "success": False,
                "error": f"Unknown harness: {harness}. Valid: {[h.value for h in HarnessType]}",
                "harness": harness,
            }
        )

    try:
        mapper = HarnessTUIMapper()
        result = mapper.execute(
            harness=harness_type,
            action=action,
            host_id=host_id,
            prompt=prompt or "",
            session_id=session_id or "",
        )
        return json.dumps(result, indent=2)
    except HarnessActionError as e:
        return json.dumps(
            {
                "success": False,
                "error": str(e),
                "harness": harness,
                "action": action,
            }
        )


def harness_list_actions_impl() -> str:
    """List all available harness actions.

    Returns:
        JSON string with list of available actions
    """
    mapper = HarnessTUIMapper()
    actions = mapper.list_actions()
    return json.dumps(
        {
            "actions": actions,
            "count": len(actions),
        }
    )


def harness_get_command_impl(
    *,
    harness: str,
    action: str,
) -> str:
    """Get the command template for a harness-action pair.

    Args:
        harness: Harness type
        action: Abstract action

    Returns:
        JSON string with command template or error
    """
    try:
        harness_type = HarnessType(harness.lower())
    except ValueError:
        return json.dumps(
            {
                "error": f"Unknown harness: {harness}",
            }
        )

    mapper = HarnessTUIMapper()
    cmd = mapper.get_command(harness_type, action)
    if cmd is None:
        return json.dumps(
            {
                "error": f"No command for action={action} harness={harness}",
            }
        )
    return json.dumps(
        {
            "harness": harness,
            "action": action,
            "command": cmd,
        }
    )


def harness_register_host_impl(
    *,
    host_id: str,
    harness: str,
    command_prefix: str = "",
    custom_actions: dict[str, str] | None = None,
) -> str:
    """Register a new host device with custom command mappings.

    Args:
        host_id: Unique identifier for the host
        harness: The harness type this host uses
        command_prefix: Prefix for all commands (e.g., "ssh user@host")
        custom_actions: Override commands for specific actions

    Returns:
        JSON string with registration status
    """
    try:
        harness_type = HarnessType(harness.lower())
    except ValueError:
        return json.dumps(
            {
                "success": False,
                "error": f"Unknown harness: {harness}",
            }
        )

    mapper = HarnessTUIMapper()
    mapper.register_host(
        host_id=host_id,
        harness=harness_type,
        command_prefix=command_prefix,
        custom_actions=custom_actions,
    )
    return json.dumps(
        {
            "success": True,
            "host_id": host_id,
            "harness": harness,
            "command_prefix": command_prefix,
        }
    )


__all__ = [
    "harness_get_command_impl",
    "harness_interact_impl",
    "harness_list_actions_impl",
    "harness_register_host_impl",
]
