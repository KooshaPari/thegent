# tools_lsp API Reference

> **Source**: `src/thegent/mcp/server/tools_lsp.py`

WL-109: Typed MCP LSP tool implementations - server-layer thin wrapper.

Re-exports the typed dataclasses and async impl functions from thegent.mcp.lsp_tools
for server.py registration. This module is loaded by server.py via importlib.

The canonical implementations live in thegent.mcp.lsp_tools to allow direct
import in tests without requiring the server/ directory to be a Python package.

# @trace WL-109

---

