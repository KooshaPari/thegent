"""MCP configuration functions for thegent.

MCP server configuration and management.
Extracted from install.py for maintainability.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any


logger = logging.getLogger(__name__)


def _get_mcp_config(url: str, client: str = "generic") -> dict[str, Any]:
    """Get MCP server configuration for a client.
    
    Args:
        url: Server URL
        client: Client type (generic, claude, cursor, codex)
        
    Returns:
        MCP configuration dict
    """
    base_config = {
        "mcpServers": {
            "thegent": {
                "url": url,
                "transport": "stdio",
            }
        }
    }
    
    # Client-specific configurations
    if client in {"claude", "cursor", "codex"}:
        base_config["mcpServers"]["thegent"]["command"] = "thegent"
        base_config["mcpServers"]["thegent"]["args"] = ["mcp", "serve"]
    
    return base_config


def _update_compatible_mcp_servers(
    config_path: Path,
    server_config: dict[str, Any],
) -> bool:
    """Update MCP server configuration in a client config file.
    
    Args:
        config_path: Path to client config file
        server_config: Server configuration to add
        
    Returns:
        True if successful
    """
    import json
    
    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config = {}
    else:
        try:
            config = json.loads(config_path.read_text())
        except Exception:
            config = {}
    
    # Merge MCP servers
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    config["mcpServers"].update(server_config.get("mcpServers", {}))
    
    # Write back
    config_path.write_text(json.dumps(config, indent=2))
    
    return True


def configure_mcp_for_client(
    client: str,
    url: str = "http://127.0.0.1:3847",
    config_dir: Path | None = None,
) -> bool:
    """Configure MCP for a specific client.
    
    Args:
        client: Client name (claude, cursor, codex, windsurf)
        url: MCP server URL
        config_dir: Optional config directory override
        
    Returns:
        True if successful
    """
    # Determine config path
    if config_dir:
        config_path = config_dir
    else:
        home = Path.home()
        
        client_paths = {
            "claude": home / ".config" / "claude" / "settings.json",
            "cursor": home / ".cursor" / "mcp.json",
            "codex": home / ".codex" / "config.json",
            "windsurf": home / ".windsurf" / "mcp.json",
        }
        
        if client not in client_paths:
            logger.warning(f"Unknown client: {client}")
            return False
        
        config_path = client_paths[client]
    
    # Get config
    server_config = _get_mcp_config(url, client)
    
    # Update
    success = _update_compatible_mcp_servers(config_path, server_config)
    
    if success:
        logger.info(f"Configured MCP for {client} at {config_path}")
    
    return success


def list_mcp_clients() -> list[str]:
    """List supported MCP clients.
    
    Returns:
        List of client names
    """
    return ["claude", "cursor", "codex", "windsurf", "generic"]


__all__ = [
    "_get_mcp_config",
    "_update_compatible_mcp_servers",
    "configure_mcp_for_client",
    "list_mcp_clients",
]
