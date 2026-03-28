# server API Reference

> **Source**: `src/thegent/mcp/server/__init__.py`

Compatibility exports for the historical ``thegent.mcp.server`` contract.

The server implementation was extracted into package modules under
``thegent.mcp.server`` while a legacy monolith still lives at
``thegent/mcp/server.py``. Tests and internal callers import symbols directly
from ``thegent.mcp.server``. Re-export those symbols from the legacy module so
collection/import contracts remain stable.

---

