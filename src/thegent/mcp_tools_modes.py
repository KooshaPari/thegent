"""
Backward compatibility shim for mcp_tools_modes.

Redirects imports to the new location at thegent.mcp.tools.modes.
"""

from thegent.mcp.tools.modes import (
    _ctx_info,
    _get_project_root,
    _ensure_dir,
    _slugify,
    register_modes,
)

# For tests that expect _ctx_warning, import from seeds module
from thegent.mcp.tools.seeds import _ctx_warning

__all__ = [
    "_ctx_info",
    "_ctx_warning",
    "_get_project_root",
    "_ensure_dir",
    "_slugify",
    "register_modes",
]
"""Re-exports from thegent.mcp.tools.modes for backwards compatibility."""

import logging

from thegent.mcp.tools.modes import register_modes

# For test patching compatibility
_log = logging.getLogger(__name__)

__all__ = ["register_modes", "_log"]
