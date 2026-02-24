"""Re-exports from thegent.mcp.storage for backwards compatibility."""

from thegent.mcp.storage import McpStorage, McpEventStore

__all__ = ["McpStorage", "McpEventStore"]
from thegent.mcp.storage import (
    McpStorage,
    McpEventStore,
    _reset_singletons_for_testing,
    get_mcp_storage,
    get_mcp_event_store,
)

__all__ = [
    "McpStorage",
    "McpEventStore",
    "_reset_singletons_for_testing",
    "get_mcp_storage",
    "get_mcp_event_store",
]
