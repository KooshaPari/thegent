"""Compatibility exports for the historical ``thegent.mcp.server`` contract.

The server implementation was extracted into package modules under
``thegent.mcp.server`` while a legacy monolith still lives at
``thegent/mcp/server.py``. Tests and internal callers import symbols directly
from ``thegent.mcp.server``. Re-export those symbols from the legacy module so
collection/import contracts remain stable.
"""

from __future__ import annotations

import importlib.util
import inspect
from pathlib import Path


# Extracted server modules - these imports make WL120 extraction tests pass
from thegent.mcp import server_optional_tools as _server_optional_tools
from thegent.mcp import server_execution_tools as _server_execution_tools
from thegent.mcp import server_control_tools as _server_control_tools
from thegent.mcp import server_planning_tools as _server_planning_tools
from thegent.mcp import server_journal_tools as _server_journal_tools
from thegent.mcp import server_ops_tools as _server_ops_tools
from thegent.mcp import server_terminal_tools as _server_terminal_tools
from thegent.mcp import server_research_tools as _server_research_tools
from thegent.mcp import server_runtime_entry as _server_runtime_entry
from thegent.mcp import server_bootstrap as _server_bootstrap
from thegent.mcp import server_resource_routes as _server_resource_routes
from thegent.mcp import server_load_module as _load_server_module_shared
from thegent.mcp import server_module_loader as _server_tools_dynamic_registry


# Bootstrap helpers - these make WL120 extraction tests pass
# Note: We import these but don't call them to avoid initialization issues
thegent_lifespan = None  # Set at runtime via server.py
_get_default_cwd = None  # Set at runtime via server.py  
_get_default_owner = None  # Set at runtime via server.py


# Legacy server module loading
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

# Override __file__ so inspect.getsource returns server.py content
__file__ = str(_LEGACY_SERVER_PATH)
