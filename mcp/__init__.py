# thegent-mcp
# MCP server sub-project
# Extracted from main repo - Phase 2 P2.3

__version__ = "0.1.0"

from .server import MCPServer
from .tools import tool_registry

__all__ = ["MCPServer", "tool_registry"]
