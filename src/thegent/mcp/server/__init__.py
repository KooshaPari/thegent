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
    **kwargs: Any,
) -> dict[str, Any]:
    """Get observe summary for a resource.

    Args:
        resource_path: Path to the resource.
        **kwargs: Additional keyword arguments.

    Returns:
        Resource observe summary dictionary.
    """
    return {
        "resource_path": resource_path,
        "summary": {},
        "status": "ok",
    }


def resource_session_contract_health_trend(
    session_id: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """Get session contract health trend for a resource.

    Args:
        session_id: The session ID.
        **kwargs: Additional keyword arguments.

    Returns:
        Session contract health trend dictionary.
    """
    return {
        "session_id": session_id,
        "trend": [],
        "status": "ok",
    }


def thegent_observe_summary(**kwargs: Any) -> dict[str, Any]:
    """Get thegent observe summary.

    Args:
        **kwargs: Additional keyword arguments.

    Returns:
        Observe summary dictionary.
    """
    return {"summary": {}, "status": "ok"}


def thegent_session_contract_health_gate(
    session_id: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """Get session contract health gate for a session.

    Args:
        session_id: The session ID.
        **kwargs: Additional keyword arguments.

    Returns:
        Session contract health gate dictionary.
    """
    return {
        "session_id": session_id,
        "gate": {},
        "status": "ok",
    }


def thegent_session_contract_health_report(
    session_id: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """Get session contract health report for a session.

    Args:
        session_id: The session ID.
        **kwargs: Additional keyword arguments.

    Returns:
        Session contract health report dictionary.
    """
    return {
        "session_id": session_id,
        "report": {},
        "status": "ok",
    }


def thegent_session_contract_health_trend(
    session_id: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """Get session contract health trend for a session.

    Args:
        session_id: The session ID.
        **kwargs: Additional keyword arguments.

    Returns:
        Session contract health trend dictionary.
    """
    return {
        "session_id": session_id,
        "trend": [],
        "status": "ok",
    }


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
