"""thegent-protocols: DEPRECATED - merged into thegent-mcp.

All protocol, ACP, IPC, SDK, and MCP functionality is now in thegent-mcp.
This package exists only for backward compatibility.
"""

import warnings

warnings.warn(
    "thegent-protocols is deprecated. Import from thegent_mcp instead.",
    DeprecationWarning,
    stacklevel=2,
)
