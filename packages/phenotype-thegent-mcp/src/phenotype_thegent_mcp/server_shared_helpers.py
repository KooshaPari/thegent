"""Shared helpers and stable references for thegent MCP server."""

from phenotype_thegent_protocols.mcp import server_error_result as _shared_error_result
from phenotype_thegent_protocols.mcp import server_stable_json as _shared_stable_json

_stable_json = _shared_stable_json
_error_result = _shared_error_result
