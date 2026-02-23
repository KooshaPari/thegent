# thegent-mcp

FastMCP 3.x protocol layer for thegent agent orchestration and MCP server integration.

## Overview

`thegent-mcp` is a sub-package that encapsulates the Model Context Protocol (MCP) server implementation for thegent. It handles:

- MCP server bootstrap and lifecycle management
- Tool registry and dynamic tool loading
- Protocol bridging between agents and external systems
- FastMCP 3.x integration

## Installation

```bash
pip install thegent-mcp
```

## Usage

```python
from thegent_mcp import server_load_module, BorrowedMCPTools

# Load MCP tools
tools = server_load_module("path.to.module")

# Use borrowed tools
borrowed = BorrowedMCPTools()
```

## Architecture

During the split transition (Track 4.2-4.3), this package is a thin wrapper over the monolith's `src/thegent/mcp` module. The wrapper will be replaced with independent implementation as the split completes.

**Phase 1 (Current)**: Wrapper delegates to monolith
**Phase 2 (T4.3)**: Independent implementation with full MCP server
**Phase 3 (T4.4)**: Full protocol layer replacement of zen-mcp-server

## Testing

```bash
pytest tests/
```

## Dependencies

- `fastmcp[tasks]>=3.0.0` - FastMCP protocol implementation
- `pydantic>=2.0.0` - Data validation
- `httpx>=0.28.1` - HTTP client
