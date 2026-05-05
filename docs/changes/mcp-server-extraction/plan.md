# Plan: mcp-server-extraction

## Objective

Extract Thegent's MCP server tool integrations into a dedicated, independently-versioned module with a clean interface contract for tool discovery, sandboxed execution, and composable MCP toolchain assembly.

## Approach

1. Survey the existing MCP server integration points in Thegent to identify the minimal contract surface
2. Define a tool descriptor schema covering name, capabilities, sandbox requirements, and timeout policies
3. Extract tool integration logic into a dedicated module with a plugin-style registration API
4. Implement sandboxing primitives (process isolation, resource limits) as first-class concerns
5. Validate by running existing MCP tool tests through the new module with parity checks
