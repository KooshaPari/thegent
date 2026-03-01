"""thegent-mcp: MCP server sub-package for thegent agent orchestration.

This package encapsulates the FastMCP 3.x protocol layer, delegating to the
monolith's src/thegent/mcp module. This is a thin wrapper during the split
transition phase.
"""

__version__ = "0.1.0"

# Public API: delegate to monolith MCP module
# During full split, these will be re-implemented here
from thegent_protocols.mcp import (
    BorrowedMCPTools,
    server_cache_elicitation_response,
    server_create_elicitation_cache,
    server_default_cwd_from_context,
    server_default_owner_from_context,
    server_elicitation_cache_key,
    server_error_result,
    server_get_cached_elicitation,
    server_load_module,
    server_resolve_cwd_elicitation,
    server_resolve_owner_elicitation,
    server_stable_json,
)

__all__ = [
    "BorrowedMCPTools",
    "server_cache_elicitation_response",
    "server_create_elicitation_cache",
    "server_default_cwd_from_context",
    "server_default_owner_from_context",
    "server_elicitation_cache_key",
    "server_error_result",
    "server_get_cached_elicitation",
    "server_load_module",
    "server_resolve_cwd_elicitation",
    "server_resolve_owner_elicitation",
    "server_stable_json",
]
