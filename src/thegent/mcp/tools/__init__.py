"""MCP tools for agent modes, patterns, elicitation, and seeds."""
from thegent.mcp.tools.elicitation import register_elicitation_tools
from thegent.mcp.tools.modes import register_modes
from thegent.mcp.tools.patterns import register_tool_pattern_tools
from thegent.mcp.tools.seeds import register_seed_tools
from thegent.mcp.tools.sitback import register_sitback

__all__ = [
    "register_elicitation_tools",
    "register_modes",
    "register_tool_pattern_tools",
    "register_seed_tools",
    "register_sitback",
]
