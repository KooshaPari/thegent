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

import orjson as json
import logging
import os
import shlex
from thegent.infra.shim_subprocess import run as shim_run
import threading
import time
from dataclasses import dataclass
from collections.abc import Callable

_log = logging.getLogger(__name__)

TransportResult = tuple[int, str, str]


McpServerTransport = Callable[[list[str], str, dict[str, str], float], TransportResult]


@dataclass
class McpServerConfig:
    server_id: str
    command: str  # e.g. "npx -y @modelcontextprotocol/server-filesystem /tmp"
    env: dict[str, str]  # environment variables to pass
    timeout_sec: float = 30.0
    description: str = ""
    transport: McpServerTransport | None = None


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
        """Execute a tool call. Returns McpToolResult with error set on failure."""
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
        timeout_sec = min(call.timeout_sec, config.timeout_sec)
        request = {
            "jsonrpc": "2.0",
            "id": "thegent-gateway",
            "method": "tools/call",
            "params": {
                "name": call.tool,
                "arguments": call.arguments,
            },
        }
        command = shlex.split(config.command)
        env = os.environ.copy()
        env.update(config.env)
        payload = json.dumps(request).decode()
        try:
            if config.transport is None:
                returncode, stdout, stderr = self._run_subprocess_transport(
                    command=command,
                    request_payload=payload,
                    env=env,
                    timeout_sec=timeout_sec,
                )
            else:
                returncode, stdout, stderr = config.transport(command, payload, env, timeout_sec)
        except FileNotFoundError:
            duration_ms = (time.monotonic() - start) * 1000.0
            return McpToolResult(
                result=None,
                server_id=call.server_id,
                tool=call.tool,
                duration_ms=duration_ms,
                error=f"transport_error: command not found ({command[0]!r})",
            )
        except TimeoutError:
            duration_ms = (time.monotonic() - start) * 1000.0
            return McpToolResult(
                result=None,
                server_id=call.server_id,
                tool=call.tool,
                duration_ms=duration_ms,
                error=f"transport_error: timeout after {timeout_sec:.1f}s",
            )
        except Exception as exc:
            duration_ms = (time.monotonic() - start) * 1000.0
            return McpToolResult(
                result=None,
                server_id=call.server_id,
                tool=call.tool,
                duration_ms=duration_ms,
                error=f"transport_error: {type(exc).__name__}: {exc}",
            )

        duration_ms = (time.monotonic() - start) * 1000.0
        parsed, has_transport_payload = self._parse_mcp_response(stdout)
        if not has_transport_payload:
            return McpToolResult(
                result=None,
                server_id=call.server_id,
                tool=call.tool,
                duration_ms=duration_ms,
                error="transport_error: invalid or empty MCP response",
            )

        if parsed.get("error"):
            normalized_error = self._normalize_tool_error(
                server_id=call.server_id,
                tool=call.tool,
                error_payload=parsed["error"],
            )
            return McpToolResult(
                result=None,
                server_id=call.server_id,
                tool=call.tool,
                duration_ms=duration_ms,
                error=normalized_error,
            )

        if returncode != 0 and parsed.get("result") is None:
            stderr = (stderr or "").strip()
            return McpToolResult(
                result=None,
                server_id=call.server_id,
                tool=call.tool,
                duration_ms=duration_ms,
                error=f"transport_error: exit_code={returncode} {stderr}".strip(),
            )

        return McpToolResult(
            result=parsed.get("result"),
            server_id=call.server_id,
            tool=call.tool,
            duration_ms=duration_ms,
            error="",
        )

    def _parse_mcp_response(self, stdout: str) -> tuple[dict[str, object], bool]:
        payload: dict[str, object] = {"result": None, "error": None}
        has_payload = False
        for raw_line in stdout.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(data, dict):
                continue
            if "error" in data:
                payload["error"] = data.get("error")
                has_payload = True
            if "result" in data:
                payload["result"] = data.get("result")
                has_payload = True
        return payload, has_payload

    def _run_subprocess_transport(
        self,
        *,
        command: list[str],
        request_payload: str,
        env: dict[str, str],
        timeout_sec: float,
    ) -> TransportResult:
        completed = shim_run(
            command,
            input=request_payload,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
            env=env,
        )
        return completed.returncode, completed.stdout or "", completed.stderr or ""

    def _normalize_tool_error(self, server_id: str, tool: str, error_payload: object) -> str:
        if isinstance(error_payload, dict):
            code = error_payload.get("code")
            message = str(error_payload.get("message", "")).strip()
            lowered = message.lower()
            if code == -32601 or "method not found" in lowered or "unknown tool" in lowered:
                return f"Unknown tool '{tool}' on server '{server_id}'"
            return message or f"MCP tool error on '{server_id}:{tool}'"
        text = str(error_payload).strip()
        lowered = text.lower()
        if "method not found" in lowered or "unknown tool" in lowered:
            return f"Unknown tool '{tool}' on server '{server_id}'"
        return text or f"MCP tool error on '{server_id}:{tool}'"


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
