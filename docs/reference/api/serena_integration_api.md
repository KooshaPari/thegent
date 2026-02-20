# serena_integration API Reference

> **Source**: `src/thegent/lsp/serena_integration.py`

Serena integration with JetBrains plugin support.

---

## detect_serena_backend

Detect available Serena backend (LSP or JetBrains plugin).

**Returns**: "jetbrains" if plugin MCP server is running, "lsp" otherwise

---

## get_serena_mcp_config

Get Serena MCP configuration based on detected backend.

**Returns**: Dict with command and args for Serena MCP server

---

