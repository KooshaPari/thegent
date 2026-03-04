"""CLI entry point for ACP server."""

import asyncio
import logging

from thegent_mcp.acp.server import main

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
