"""GW-66: REST-to-MCP adapter — wrap REST endpoints as MCP tools.

Allows any REST API to be exposed as an MCP tool, enabling LLMs to call
arbitrary HTTP endpoints through the MCP tool calling interface.

# @trace FR-MCP-066
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

import httpx

_log = logging.getLogger(__name__)

# Regex to find {param_name} placeholders in URL templates.
_PLACEHOLDER_RE = re.compile(r"\{(\w+)\}")


@dataclass
class RestToolDef:
    """Definition of a REST endpoint exposed as an MCP tool."""

    name: str  # MCP tool name e.g. "search_products"
    description: str  # shown to LLM
    url: str  # REST endpoint URL template, e.g. "https://api.example.com/search?q={query}"
    method: str = "GET"  # HTTP method
    headers: dict[str, str] = field(default_factory=dict)  # static headers to include
    param_schema: dict = field(default_factory=dict)  # JSON schema for tool parameters
    timeout_sec: float = 10.0


@dataclass
class RestToolResult:
    status_code: int
    body: object  # parsed JSON or raw string
    error: str = ""


class RestToMcpAdapter:
    """Registry of REST endpoints exposed as MCP tools."""

    def __init__(self) -> None:
        self._tools: dict[str, RestToolDef] = {}

    def register(self, tool: RestToolDef) -> None:
        """Register a REST endpoint as an MCP tool."""
        self._tools[tool.name] = tool
        _log.info("Registered REST tool: %s -> %s %s", tool.name, tool.method, tool.url)

    def unregister(self, name: str) -> None:
        """Remove a tool. Raises KeyError if not found."""
        if name not in self._tools:
            raise KeyError(name)
        del self._tools[name]
        _log.info("Unregistered REST tool: %s", name)

    def list_tools(self) -> list[RestToolDef]:
        """Return all registered tool definitions."""
        return list(self._tools.values())

    def get_tool(self, name: str) -> RestToolDef | None:
        """Return the RestToolDef for the given name, or None if not registered."""
        return self._tools.get(name)

    def to_openai_tools(self) -> list[dict]:
        """Convert registered tools to OpenAI tools format for LLM consumption."""
        return [build_openai_tool_def(tool) for tool in self._tools.values()]

    def call(self, name: str, arguments: dict) -> RestToolResult:
        """Execute the named REST tool with the given arguments.

        Substitutes {param} placeholders in URL, sends HTTP request.
        Uses httpx for HTTP. Returns RestToolResult with error set on failure.
        """
        tool = self._tools.get(name)
        if tool is None:
            _log.warning("Unknown REST tool: %s", name)
            return RestToolResult(
                status_code=0,
                body=None,
                error=f"Unknown tool: {name!r}",
            )

        # Substitute URL placeholders and collect remaining arguments.
        placeholders = _PLACEHOLDER_RE.findall(tool.url)
        url = tool.url
        remaining: dict = {}
        for key, value in arguments.items():
            if key in placeholders:
                url = url.replace(f"{{{key}}}", str(value))
            else:
                remaining[key] = value

        _log.debug("REST call: %s %s args=%s", tool.method, url, remaining)

        try:
            with httpx.Client(timeout=tool.timeout_sec) as client:
                method = tool.method.upper()
                if method in ("POST", "PUT", "PATCH"):
                    response = client.request(
                        method,
                        url,
                        json=remaining if remaining else None,
                        headers=tool.headers,
                    )
                else:
                    response = client.request(
                        method,
                        url,
                        headers=tool.headers,
                    )
        except Exception as exc:  # noqa: BLE001 — must not raise; return error instead
            _log.warning("HTTP error calling %s: %s", name, exc)
            return RestToolResult(
                status_code=0,
                body=None,
                error=str(exc),
            )

        try:
            body = response.json()
        except Exception:
            body = response.text

        return RestToolResult(
            status_code=response.status_code,
            body=body,
            error="",
        )


def build_openai_tool_def(tool: RestToolDef) -> dict:
    """Convert a RestToolDef to OpenAI function calling format."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.param_schema,
        },
    }


# Register with unified adapter registry
from phenotype_thegent_core.adapters.ports import AdapterRegistry


class McpAdapter:
    """MCP adapter wrapper for registry"""

    def __init__(self):
        self._adapter = RestToMcpAdapter()

    def call(self, **kwargs) -> dict:
        return {"status": "mcp_adapter_ready"}


AdapterRegistry.register("mcp", McpAdapter())
