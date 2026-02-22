# Protocols & Adapters Domain Technical Specification

## Overview

Multi-protocol support and adapter implementations.

## Protocols

| Protocol | Purpose | Files |
|----------|---------|-------|
| MCP | Tool exposure | `mcp/` |
| ACP | Agent communication | `adapters/acp_*.py` |
| A2A | Agent-to-agent | `protocols/a2a.py` |
| JSON-RPC | RPC | `protocols/jsonrpc_agent_server.py` |

### MCP Tools

| Category | Count | Files |
|----------|-------|-------|
| Session | 50+ | `tools_sessions.py` |
| Terminal | 20+ | `tools_terminal.py` |
| Governance | 15+ | `tools_governance.py` |

### Adapters

| Adapter | Protocol | Purpose |
|---------|----------|---------|
| ACP Server | ACP | Server |
| ACP Client | ACP | Client |
| MCP Bridge | MCP ↔ ACP | Bridge |

## Features

- Protocol negotiation
- Fallback chains
- Version negotiation
