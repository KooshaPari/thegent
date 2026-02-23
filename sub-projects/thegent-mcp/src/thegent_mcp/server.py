"""FastMCP server aggregating ecosystem tools."""

from __future__ import annotations

import importlib
import json
from typing import Any

from fastmcp import FastMCP

import structlog

logger = structlog.get_logger(__name__)

mcp = FastMCP("thegent-mcp")

# Tool modules to auto-register
TOOL_MODULES: list[str] = [
    "thegent_mcp.tools.github",
    "thegent_mcp.tools.slack",
]


def register_all_tools() -> None:
    """Register tools from all known modules."""
    for module_name in TOOL_MODULES:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, "register_tools"):
                module.register_tools(mcp)
                logger.info("registered_tools", module=module_name)
        except ImportError:
            logger.info("tool_module_not_available", module=module_name)


# Register on import
register_all_tools()
