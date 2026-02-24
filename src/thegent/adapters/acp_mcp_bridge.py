"""ACP <-> MCP Bridge Adapter.

Bridges MCP tools to ACP task endpoints and vice versa:

- ``mcp_tool_to_acp_task``: Wrap an MCP tool call as an ACP task sent to a
  remote ACP server.
- ``acp_agent_to_mcp_tool``: Call a remote ACP agent and return its output in
  MCP tool response format (plain string).
- ``get_mcp_tool_manifest``: Introspect all registered FastMCP tools and return
  them as ACP-compatible task descriptors.

The bridge is deliberately stateless.  Callers are responsible for providing an
:class:`~thegent.adapters.acp_client.ACPClient` instance and for managing the
FastMCP application reference when manifest introspection is needed.

# @trace FR-ACP-002
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, cast, get_type_hints

from thegent.adapters.acp_client import ACPClient, ACPClientError, ACPResult
from thegent.integrations.base import SerializableMixin

if TYPE_CHECKING:
    from fastmcp import FastMCP

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: ACP task type used when invoking an MCP tool via ACP protocol.
ACP_TASK_TYPE = "mcp_tool_call"

#: Version string embedded in ACP task descriptors.
ACP_DESCRIPTOR_VERSION = "1.0"


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class BridgeError(Exception):
    """Base class for bridge-specific errors."""


class MCPToolNotFoundError(BridgeError):
    """Raised when a requested MCP tool is not registered."""

    def __init__(self, tool_name: str) -> None:
        super().__init__(f"MCP tool '{tool_name}' is not registered on this server.")
        self.tool_name = tool_name


class ACPAgentCallError(BridgeError):
    """Raised when calling an ACP agent fails non-transiently."""

    def __init__(self, agent_url: str, detail: str) -> None:
        super().__init__(f"ACP agent at '{agent_url}' returned an error: {detail}")
        self.agent_url = agent_url


# ---------------------------------------------------------------------------
# Tool descriptor (ACP-compatible)
# ---------------------------------------------------------------------------


@dataclass
class ACPToolDescriptor(SerializableMixin):
    """ACP-compatible descriptor for a single MCP tool.

    Attributes:
        name:        MCP tool name.
        description: Human-readable description extracted from the tool's
                     docstring.
        parameters:  JSON-Schema-style parameter map ``{name: {"type": ...,
                     "description": ...}}``.
        version:     Descriptor schema version.
    """

    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)
    version: str = ACP_DESCRIPTOR_VERSION


# ---------------------------------------------------------------------------
# Bridge
# ---------------------------------------------------------------------------


class AcpMcpBridge:
    """Bridges MCP tools to ACP task endpoints and vice versa.

    Args:
        acp_client:     Pre-configured :class:`~thegent.adapters.acp_client.ACPClient`
                        instance used to reach remote ACP servers.
        mcp_app:        Optional reference to the running :class:`fastmcp.FastMCP`
                        application.  Required only for
                        :meth:`get_mcp_tool_manifest`; all other methods work
                        without it.
        mcp_server_url: Optional URL for a remote MCP server (informational;
                        currently unused by bridge logic but retained for future
                        tool-proxying support).
    """

    def __init__(
        self,
        acp_client: ACPClient,
        mcp_app: FastMCP | None = None,
        mcp_server_url: str | None = None,
    ) -> None:
        self._acp_client = acp_client
        self._mcp_app = mcp_app
        self._mcp_server_url = mcp_server_url

        logger.debug(
            "AcpMcpBridge initialised (mcp_server_url=%s, has_mcp_app=%s)",
            self._mcp_server_url,
            self._mcp_app is not None,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def mcp_tool_to_acp_task(
        self,
        tool_name: str,
        args: dict[str, Any],
        timeout: float = 30.0,
    ) -> ACPResult:
        """Call an MCP tool via the ACP task protocol.

        Encodes the tool name and arguments into an ACP task payload and
        delivers it to the remote ACP server via ``POST /tasks``.  The remote
        server is expected to understand the ``type: mcp_tool_call`` envelope.

        Args:
            tool_name: Name of the MCP tool to invoke (e.g. ``"thegent_ps"``).
            args:      Keyword arguments forwarded to the tool.
            timeout:   Per-attempt HTTP timeout in seconds.

        Returns:
            :class:`~thegent.adapters.acp_client.ACPResult` with the remote
            agent's response.

        Raises:
            ACPServerUnreachableError: When the remote server cannot be reached.
            ACPClientError:            On non-retryable server-side errors.
        """
        if not tool_name:
            raise ValueError("tool_name must not be empty")

        task_description = f"Invoke MCP tool: {tool_name}"
        context: dict[str, Any] = {
            "type": ACP_TASK_TYPE,
            "tool_name": tool_name,
            "args": args,
        }

        logger.debug("mcp_tool_to_acp_task: tool=%s args_keys=%s", tool_name, sorted(args))

        start = time.monotonic()
        result = await self._acp_client.send_task(
            task=task_description,
            context=context,
            timeout=timeout,
        )
        elapsed_ms = (time.monotonic() - start) * 1000

        logger.debug(
            "mcp_tool_to_acp_task completed: tool=%s success=%s elapsed_ms=%.1f",
            tool_name,
            result.success,
            elapsed_ms,
        )
        return result

    async def acp_agent_to_mcp_tool(
        self,
        agent_url: str,
        task: str,
        payload: dict[str, Any],
        timeout: float = 30.0,
    ) -> str:
        """Call a remote ACP agent and return its result as an MCP tool response.

        Creates a short-lived :class:`~thegent.adapters.acp_client.ACPClient`
        targeting *agent_url* for this single call.  The ``payload`` dict is
        passed as ACP task context.

        Args:
            agent_url: Base URL of the target ACP agent (no trailing slash).
            task:      Human-readable task description / prompt.
            payload:   Arbitrary context dict forwarded as ACP context.
            timeout:   Per-attempt HTTP timeout in seconds.

        Returns:
            The plain-text result string from the remote agent, ready to be
            returned directly from an MCP tool handler.

        Raises:
            ACPAgentCallError:        On non-retryable server errors.
            ACPServerUnreachableError: When the agent is unreachable.
        """
        if not agent_url:
            raise ValueError("agent_url must not be empty")
        if not task:
            raise ValueError("task must not be empty")

        # Build a one-shot client targeting the specific agent URL.
        client = ACPClient(base_url=agent_url)

        logger.debug("acp_agent_to_mcp_tool: agent_url=%s task=%r", agent_url, task[:80])

        try:
            result = await client.send_task(task=task, context=payload or {}, timeout=timeout)
        except ACPClientError as exc:
            raise ACPAgentCallError(agent_url, str(exc)) from exc

        logger.debug(
            "acp_agent_to_mcp_tool completed: agent_url=%s agent_id=%s elapsed_ms=%.1f",
            agent_url,
            result.agent_id,
            result.elapsed_ms,
        )
        return result.result

    def get_mcp_tool_manifest(self) -> list[dict[str, Any]]:
        """Return all registered MCP tools as ACP-compatible task descriptors.

        Introspects the FastMCP application (if provided at construction time)
        and converts each registered tool into an :class:`ACPToolDescriptor`,
        serialised as a plain dict.

        When no FastMCP application is available the method returns an empty
        list rather than raising, so callers can safely call it unconditionally.

        Returns:
            List of dicts, each with keys ``name``, ``description``,
            ``parameters``, and ``version``.
        """
        if self._mcp_app is None:
            logger.debug("get_mcp_tool_manifest: no mcp_app configured; returning empty manifest")
            return []

        descriptors: list[dict[str, Any]] = []
        try:
            # FastMCP's list_tools() is async; cast to Any for sync introspection
            # (callers may provide a duck-typed or mocked mcp_app).
            tools = cast("Any", self._mcp_app).list_tools()
        except Exception as exc:
            logger.warning("get_mcp_tool_manifest: failed to introspect tools: %s", exc)
            return []

        for tool_obj in tools:
            descriptor = self._build_descriptor(getattr(tool_obj, "name", str(tool_obj)), tool_obj)
            descriptors.append(descriptor.to_dict())

        logger.debug("get_mcp_tool_manifest: returning %d descriptors", len(descriptors))
        return descriptors

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_descriptor(self, tool_name: str, tool_obj: Any) -> ACPToolDescriptor:
        """Convert a FastMCP tool object into an :class:`ACPToolDescriptor`.

        Args:
            tool_name: Registered tool name.
            tool_obj:  FastMCP tool object (duck-typed; attributes accessed
                       defensively).

        Returns:
            Populated :class:`ACPToolDescriptor`.
        """
        description = self._extract_description(tool_obj)
        parameters = self._extract_parameters(tool_obj)
        return ACPToolDescriptor(
            name=tool_name,
            description=description,
            parameters=parameters,
        )

    @staticmethod
    def _extract_description(tool_obj: Any) -> str:
        """Extract a human-readable description from a FastMCP tool object.

        Tries common attribute names in order: ``description``, ``__doc__``.

        Args:
            tool_obj: FastMCP tool object.

        Returns:
            Description string, or an empty string if none found.
        """
        for attr in ("description", "__doc__"):
            value = getattr(tool_obj, attr, None)
            if value and isinstance(value, str):
                # Trim leading/trailing whitespace and collapse internal newlines.
                return " ".join(value.split())
        return ""

    @staticmethod
    def _extract_parameters(tool_obj: Any) -> dict[str, Any]:
        """Extract parameter schema from a FastMCP tool object.

        Tries ``parameters``, ``inputSchema``, and ``typing.get_type_hints(fn)`` in
        order, returning whichever yields a usable dict first.

        Args:
            tool_obj: FastMCP tool object.

        Returns:
            Parameter dict or empty dict if extraction fails.
        """
        # 1. Direct parameters attribute (FastMCP ≥ 2.x)
        params = getattr(tool_obj, "parameters", None)
        if isinstance(params, dict) and params:
            return params

        # 2. inputSchema (JSON-Schema style)
        schema = getattr(tool_obj, "inputSchema", None)
        if isinstance(schema, dict) and schema:
            return schema

        # 3. Annotations from the underlying function
        fn = getattr(tool_obj, "fn", None)
        if fn is not None:
            try:
                annotations = get_type_hints(fn)
            except Exception:
                annotations = {}
            if annotations:
                return {k: {"type": str(v)} for k, v in annotations.items() if k != "return"}

        return {}
