"""Re-exports from thegent.mcp.tools.modes for backwards compatibility."""

import logging

from thegent.mcp.tools.modes import (
    _ctx_info,
    _get_project_root,
    register_modes,
)

# For tests that expect _ctx_warning, import from seeds module
from thegent.mcp.tools.seeds import _ctx_warning

# For test patching compatibility
_log = logging.getLogger(__name__)

__all__ = ["_ctx_info", "_ctx_warning", "_get_project_root", "register_modes", "_log"]
