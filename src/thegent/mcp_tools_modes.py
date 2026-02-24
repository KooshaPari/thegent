"""Re-exports from thegent.mcp.tools.modes for backwards compatibility."""

import logging

from thegent.mcp.tools.modes import register_modes

# For test patching compatibility
_log = logging.getLogger(__name__)

__all__ = ["register_modes", "_log"]
