"""Shared helpers and stable references for thegent MCP server."""

from thegent_mcp.mcp import server_error_result as _shared_error_result
from thegent_mcp.mcp import server_stable_json as _shared_stable_json

_stable_json = _shared_stable_json
_error_result = _shared_error_result
