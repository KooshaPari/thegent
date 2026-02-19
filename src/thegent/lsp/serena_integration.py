"""Serena integration with JetBrains plugin support."""

import logging
import socket
from typing import Literal

from thegent.config import ThegentSettings

logger = logging.getLogger(__name__)


def detect_serena_backend() -> Literal["lsp", "jetbrains"]:
    """Detect available Serena backend (LSP or JetBrains plugin).

    Returns:
        "jetbrains" if plugin MCP server is running, "lsp" otherwise
    """
    settings = ThegentSettings()

    # Explicit configuration
    if settings.serena_backend == "lsp":
        return "lsp"
    if settings.serena_backend == "jetbrains":
        return "jetbrains"

    # Auto-detect: Check if JetBrains plugin MCP server is running
    jetbrains_port = settings.serena_jetbrains_port

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("localhost", jetbrains_port))
        sock.close()

        if result == 0:
            logger.info(f"Detected Serena JetBrains plugin on port {jetbrains_port}")
            return "jetbrains"
    except Exception as e:
        logger.debug(f"Failed to check JetBrains plugin: {e}")

    # Fallback to LSP
    logger.info("Using Serena LSP backend")
    return "lsp"


def get_serena_mcp_config() -> dict:
    """Get Serena MCP configuration based on detected backend.

    Returns:
        Dict with command and args for Serena MCP server
    """
    backend = detect_serena_backend()
    settings = ThegentSettings()

    if backend == "jetbrains":
        # Connect to JetBrains plugin MCP server
        # Note: This assumes the plugin exposes an HTTP MCP server
        # Actual implementation may vary based on plugin API
        return {
            "command": "mcp-client",  # Placeholder - may need custom client
            "args": ["--url", f"http://localhost:{settings.serena_jetbrains_port}"],
        }
    # Use LSP backend (existing)
    return {
        "command": "uvx",
        "args": [
            "--from",
            "git+https://github.com/oraios/serena",
            "serena",
            "start-mcp-server",
            "--context",
            "ide",
        ],
    }
