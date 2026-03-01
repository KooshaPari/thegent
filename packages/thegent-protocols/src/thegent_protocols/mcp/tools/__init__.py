"""MCP tools for agent modes, patterns, elicitation, and seeds."""
from thegent_protocols.mcp.tools.elicitation import register_elicitation_tools
from thegent_protocols.mcp.tools.modes import register_modes
from thegent_protocols.mcp.tools.patterns import register_tool_pattern_tools
from thegent_protocols.mcp.tools.seeds import register_seed_tools
from thegent_protocols.mcp.tools.sitback import register_sitback

__all__ = [
    "register_elicitation_tools",
    "register_modes",
    "register_seed_tools",
    "register_sitback",
    "register_tool_pattern_tools",
]
