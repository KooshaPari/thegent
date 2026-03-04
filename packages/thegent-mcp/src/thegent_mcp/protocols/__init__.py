"""Protocol implementations for agent communication.

Submodules:
- a2a: Agent-to-Agent protocol
- jsonrpc_agent_server: JSON-RPC agent server (requires thegent-sync)
- turn_submit_boundaries: Turn submission boundary handling
"""

from thegent_mcp.protocols.a2a import A2AProtocol

__all__ = [
    "A2AProtocol",
]


def __getattr__(name: str):
    if name == "serve_stdio":
        from thegent_mcp.protocols.jsonrpc_agent_server import serve_stdio

        return serve_stdio
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
