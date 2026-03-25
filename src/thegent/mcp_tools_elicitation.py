"""Re-exports from thegent.mcp.tools.elicitation for backwards compatibility."""

from thegent.mcp.tools.elicitation import (
    elicit_choice,
    elicit_confirmation,
    elicit_structured,
    elicit_text,
    register_elicitation_tools,
)

__all__ = [
    "elicit_choice",
    "elicit_confirmation",
    "elicit_structured",
    "elicit_text",
    "register_elicitation_tools",
]
