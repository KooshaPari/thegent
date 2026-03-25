"""MCP module boundary for thegent."""


def get_mcp_app():
    """Return the FastMCP app from the canonical MCP package."""
    from thegent_mcp.server import app

    return app


__all__ = ["get_mcp_app"]
