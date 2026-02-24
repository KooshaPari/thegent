"""
Backward compatibility shim for mcp_tools_seeds.

Redirects imports to the new location at thegent.mcp.tools.seeds.
"""

from thegent.mcp.tools.seeds import (
    _ctx_info,
    _ctx_warning,
    register_seed_tools,
)

# Re-export for test patching compatibility
from thegent.memory.seed_detector import SeedDetector, SeedSource
from thegent.memory.seed_storage import SeedStorage

__all__ = [
    "_ctx_info",
    "_ctx_warning",
    "register_seed_tools",
    "SeedDetector",
    "SeedSource",
    "SeedStorage",
]
