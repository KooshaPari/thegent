"""JetBrains MCP tool wrappers.

These tools provide a clean interface to JetBrains IDE features via MCP protocol.
They communicate with the JetBrains MCP server running in the IDE.
"""

import json
import logging

import httpx

from thegent.config import ThegentSettings

_log = logging.getLogger(__name__)


def _get_jetbrains_mcp_url() -> str:
    """Get the JetBrains MCP server URL."""
    settings = ThegentSettings()
    return f"http://localhost:{settings.serena_jetbrains_port}"


async def jetbrains_read_file(path: str, offset: int = 0, limit: int = -1) -> str:
    """Read a file via JetBrains IDE.

    Args:
        path: Absolute path to the file to read
        offset: Line offset to start reading from (0-based)
        limit: Number of lines to read (-1 for entire file)

    Returns:
        File content as string
    """
    url = _get_jetbrains_mcp_url()
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "read_file",
            "arguments": {"path": path, "offset": offset, "limit": limit},
        },
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("result", {}).get("content", "")
        except Exception as e:
            _log.error(f"JetBrains read_file failed: {e}")
            return f"Error reading file: {e}"


async def jetbrains_apply_patch(patch: str, force: bool = False) -> str:
    """Apply a patch to the project via JetBrains IDE.

    Args:
        patch: Unified diff patch content
        force: Whether to force apply even with conflicts

    Returns:
        Result message
    """
    url = _get_jetbrains_mcp_url()
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "apply_patch",
            "arguments": {"patch": patch, "force": force},
        },
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("result", {}).get("message", "Patch applied successfully")
        except Exception as e:
            _log.error(f"JetBrains apply_patch failed: {e}")
            return f"Error applying patch: {e}"


async def jetbrains_run_command(cmd: str, cwd: str | None = None, timeout: int = 300) -> str:
    """Run a shell command in the project context via JetBrains IDE.

    Args:
        cmd: Command to run
        cwd: Working directory (defaults to project root)
        timeout: Command timeout in seconds

    Returns:
        Command output
    """
    url = _get_jetbrains_mcp_url()
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "run_command",
            "arguments": {"command": cmd, "cwd": cwd, "timeout": timeout},
        },
    }

    async with httpx.AsyncClient(timeout=float(timeout + 10)) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("result", {}).get("output", "")
        except Exception as e:
            _log.error(f"JetBrains run_command failed: {e}")
            return f"Error running command: {e}"


async def jetbrains_find_usages(symbol: str, file_path: str | None = None) -> str:
    """Find usages of a symbol via JetBrains IDE.

    Args:
        symbol: Symbol name to find usages for
        file_path: Optional file path where the symbol is defined

    Returns:
        JSON string of usage locations
    """
    url = _get_jetbrains_mcp_url()
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "find_usages",
            "arguments": {"symbol": symbol, "file": file_path},
        },
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            return json.dumps(result.get("result", {}), indent=2)
        except Exception as e:
            _log.error(f"JetBrains find_usages failed: {e}")
            return json.dumps({"error": str(e)})


async def jetbrains_go_to_definition(symbol: str, file_path: str | None = None) -> str:
    """Navigate to definition of a symbol via JetBrains IDE.

    Args:
        symbol: Symbol name to find definition for
        file_path: Optional file path where the symbol is defined

    Returns:
        JSON string with definition location
    """
    url = _get_jetbrains_mcp_url()
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "go_to_definition",
            "arguments": {"symbol": symbol, "file": file_path},
        },
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            return json.dumps(result.get("result", {}), indent=2)
        except Exception as e:
            _log.error(f"JetBrains go_to_definition failed: {e}")
            return json.dumps({"error": str(e)})


async def jetbrains_list_tools() -> str:
    """List available JetBrains MCP tools.

    Returns:
        JSON string of available tools
    """
    tools = [
        {
            "name": "jetbrains_read_file",
            "description": "Read a file from the JetBrains IDE project",
            "parameters": ["path", "offset", "limit"],
        },
        {
            "name": "jetbrains_apply_patch",
            "description": "Apply a unified diff patch to the project",
            "parameters": ["patch", "force"],
        },
        {
            "name": "jetbrains_run_command",
            "description": "Run a shell command in the project context",
            "parameters": ["cmd", "cwd", "timeout"],
        },
        {
            "name": "jetbrains_find_usages",
            "description": "Find all usages of a symbol",
            "parameters": ["symbol", "file_path"],
        },
        {
            "name": "jetbrains_go_to_definition",
            "description": "Navigate to symbol definition",
            "parameters": ["symbol", "file_path"],
        },
    ]
    return json.dumps({"tools": tools, "count": len(tools)}, indent=2)


def check_jetbrains_mcp_available() -> bool:
    """Check if JetBrains MCP server is available.

    Returns:
        True if the JetBrains MCP server is running and accessible
    """
    import socket

    settings = ThegentSettings()
    port = settings.serena_jetbrains_port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(("localhost", port))
    sock.close()
    return result == 0
