"""thegent adapter layer: HTTP-based clients for external agent protocols."""

from thegent.adapters.acp_client import ACPClient, ACPClientError, ACPResult, ACPServerUnreachableError
from thegent.adapters.acp_mcp_bridge import (
    ACPAgentCallError,
    AcpMcpBridge,
    ACPToolDescriptor,
    BridgeError,
    MCPToolNotFoundError,
)

__all__ = [
    "ACPAgentCallError",
    "ACPClient",
    "ACPClientError",
    "ACPResult",
    "ACPServerUnreachableError",
    "ACPToolDescriptor",
    "AcpMcpBridge",
    "BridgeError",
    "MCPToolNotFoundError",
]
