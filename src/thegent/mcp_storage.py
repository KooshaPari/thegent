"""Re-exports from thegent.mcp.storage for backwards compatibility."""

from thegent.mcp.storage import (
    McpStorage,
    McpEventStore,
    get_mcp_storage,
    get_mcp_event_store,
)

__all__ = [
    "McpStorage",
    "McpEventStore",
    "get_mcp_storage",
    "get_mcp_event_store",
]
