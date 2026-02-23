"""Port thegent MCP tools to other projects."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class BorrowedMCPTools:
    """MCP tools borrowed from thegent for other projects."""

    def __init__(self) -> None:
        """Initialize borrowed MCP tools."""
        self.tools: dict[str, Any] = {}

    def register_tool(self, name: str, tool: Any) -> None:
        """Register a borrowed tool.

        Args:
            name: Tool name
            tool: Tool implementation
        """
        self.tools[name] = tool
        logger.info(f"Registered borrowed tool: {name}")

    def get_tool(self, name: str) -> Any:
        """Get a borrowed tool.

        Args:
            name: Tool name

        Returns:
            Tool implementation
        """
        return self.tools.get(name)

    def list_tools(self) -> list[str]:
        """List all borrowed tools.

        Returns:
            List of tool names
        """
        return list(self.tools.keys())
