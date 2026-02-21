"""GW-64: MCP gateway — route LLM tool calls through MCP servers.

Provides a unified interface for executing MCP tools via:
  1. Direct MCP tool execution (when MCP server is available)
  2. REST passthrough (wrap tool call as REST request)

REST endpoint pattern: POST /v1/mcp/tool/execute
Request body:
  {
    "server_id": "filesystem",   # which MCP server
    "tool": "read_file",         # tool name
    "arguments": {"path": "/tmp/foo.txt"},
    "timeout_sec": 30.0
  }

Response:
  {
    "result": <tool_result>,
    "server_id": "filesystem",
    "tool": "read_file",
    "duration_ms": 142.5,
    "error": ""   # non-empty on failure
  }

# @trace FR-MCP-064
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass

_log = logging.getLogger(__name__)


@dataclass
class McpServerConfig:
    server_id: str
    command: str  # e.g. "npx -y @modelcontextprotocol/server-filesystem /tmp"
    env: dict[str, str]  # environment variables to pass
    timeout_sec: float = 30.0
    description: str = ""


@dataclass
class McpToolCall:
    server_id: str
    tool: str
    arguments: dict
    timeout_sec: float = 30.0


@dataclass
class McpToolResult:
    result: object  # tool's return value (can be any JSON-serializable type)
    server_id: str
    tool: str
    duration_ms: float
    error: str = ""  # non-empty on failure


class McpGateway:
    """Registry and dispatcher for MCP server tool calls."""

    def __init__(self) -> None:
        self._servers: dict[str, McpServerConfig] = {}
        self._lock: threading.Lock = threading.Lock()

    def register_server(self, config: McpServerConfig) -> None:
        """Register an MCP server configuration."""
        with self._lock:
            self._servers[config.server_id] = config
            _log.info("Registered MCP server: %s", config.server_id)

    def unregister_server(self, server_id: str) -> None:
        """Remove a server. Raises KeyError if not found."""
        with self._lock:
            if server_id not in self._servers:
                raise KeyError(server_id)
            del self._servers[server_id]
            _log.info("Unregistered MCP server: %s", server_id)

    def list_servers(self) -> list[McpServerConfig]:
        """Return all registered server configs."""
        with self._lock:
            return list(self._servers.values())

    def get_server(self, server_id: str) -> McpServerConfig | None:
        """Get server config by ID."""
        with self._lock:
            return self._servers.get(server_id)

    def execute(self, call: McpToolCall) -> McpToolResult:
        """Execute a tool call. Returns McpToolResult with error set on failure.

        For now: stub executor that records the call and returns a placeholder result.
        Actual subprocess/MCP invocation is deferred to a future integration.
        """
        start = time.monotonic()
        config = self.get_server(call.server_id)
        if config is None:
            duration_ms = (time.monotonic() - start) * 1000.0
            _log.warning("Unknown MCP server: %s", call.server_id)
            return McpToolResult(
                result=None,
                server_id=call.server_id,
                tool=call.tool,
                duration_ms=duration_ms,
                error=f"Unknown server_id: {call.server_id!r}",
            )
        duration_ms = (time.monotonic() - start) * 1000.0
        _log.debug(
            "Stub execute: server=%s tool=%s args=%s",
            call.server_id,
            call.tool,
            call.arguments,
        )
        return McpToolResult(
            result={"status": "ok", "tool": call.tool},
            server_id=call.server_id,
            tool=call.tool,
            duration_ms=duration_ms,
            error="",
        )


_gateway: McpGateway | None = None
_gateway_lock: threading.Lock = threading.Lock()


def get_mcp_gateway() -> McpGateway:
    """Return the singleton McpGateway instance, creating it if needed."""
    global _gateway
    with _gateway_lock:
        if _gateway is None:
            _gateway = McpGateway()
    return _gateway


def reset_mcp_gateway() -> None:
    """Replace the singleton with a fresh instance. Intended for testing only."""
    global _gateway
    with _gateway_lock:
        _gateway = McpGateway()
