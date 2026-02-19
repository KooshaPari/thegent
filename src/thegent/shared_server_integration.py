"""
Shared Server Integration - Session Management

Integrates shared LSP/MCP servers into thegent session lifecycle.
"""

from pathlib import Path

from thegent.shared_lsp_manager import (
    ensure_shared_lsp_server,
    get_lsp_server_scope,
)
from thegent.shared_mcp_manager import (
    check_mcp_health,
    ensure_shared_mcp_server,
    get_server_scope,
    get_shared_mcp_url,
)


def initialize_shared_servers_for_session(project_root: Path | None = None, languages: list[str] | None = None) -> dict:
    """
    Initialize shared servers for a new session.
    Called when a thegent session starts.

    Returns:
        {
            'mcp_url': str,
            'lsp_servers': {language: socket_path},
            'scope': 'system' | 'project'
        }
    """
    if languages is None:
        languages = ["python"]  # Default

    # Initialize MCP server (system-wide by default)
    is_new_mcp, mcp_url = ensure_shared_mcp_server(project_root)
    if not mcp_url or mcp_url.startswith("Failed"):
        raise RuntimeError(f"Failed to initialize MCP server: {mcp_url}")

    # Initialize LSP servers for each language
    lsp_servers = {}
    for language in languages:
        lsp_path = ensure_shared_lsp_server(project_root, language)
        if lsp_path:
            lsp_servers[language] = lsp_path

    # Determine scope
    scope_type, _ = get_server_scope(project_root)

    return {
        "mcp_url": mcp_url,
        "lsp_servers": lsp_servers,
        "scope": scope_type,
        "is_new_mcp": is_new_mcp,
    }


def cleanup_shared_servers_for_session(project_root: Path | None = None) -> None:
    """
    Cleanup shared servers when session ends.
    Note: Servers are shared, so we don't stop them here.
    Only cleanup session-specific resources.
    """
    # For now, no session-specific cleanup needed
    # Servers remain running for other sessions


def get_session_server_info(project_root: Path | None = None) -> dict:
    """
    Get current server information for a session.
    Useful for debugging and monitoring.
    """
    scope_type, mcp_lockfile = get_server_scope(project_root)
    lsp_scope, lsp_lockfile = get_lsp_server_scope(project_root)

    mcp_health = check_mcp_health(project_root)
    mcp_url = get_shared_mcp_url(project_root)

    return {
        "mcp": {
            "url": mcp_url,
            "scope": scope_type,
            "lockfile": str(mcp_lockfile),
            "health": mcp_health,
        },
        "lsp": {
            "scope": lsp_scope,
            "lockfile": str(lsp_lockfile),
        },
    }
