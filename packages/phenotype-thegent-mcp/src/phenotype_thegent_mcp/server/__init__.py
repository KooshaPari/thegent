"""Compatibility exports for the historical ``thegent.mcp.server`` contract.

The server implementation was extracted into package modules under
``thegent.mcp.server`` while a legacy monolith still lives at
``thegent/mcp/server.py``. Tests and internal callers import symbols directly
from ``thegent.mcp.server``. Re-export those symbols from the legacy module so
collection/import contracts remain stable.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


_LEGACY_SERVER_PATH = Path(__file__).resolve().parents[1] / "server.py"
_spec = importlib.util.spec_from_file_location("thegent.mcp._legacy_server_module", _LEGACY_SERVER_PATH)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load legacy MCP server module from {_LEGACY_SERVER_PATH}")
_legacy_server_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_legacy_server_module)

for _name in dir(_legacy_server_module):
    if _name.startswith("__"):
        continue
    globals()[_name] = getattr(_legacy_server_module, _name)

__all__ = [name for name in dir(_legacy_server_module) if not name.startswith("_")]  # pyright: ignore[reportUnsupportedDunderAll]
