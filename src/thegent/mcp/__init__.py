"""MCP (Model Context Protocol) server for thegent.

This module implements the MCP server adapter for thegent, exposing
task execution and agent management via the MCP protocol.

Dependencies:
- thegent.core (ports + domain types)
- thegent.execution (executor)
- thegent.agents (agent registry)
- thegent.models (model definitions)

NO imports from thegent.cli to maintain clean separation.
"""

from __future__ import annotations

from thegent.mcp.server import MCPServer

__all__ = ["MCPServer"]
