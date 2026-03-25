# Thegent MCP Boundary

## Module Contract

`thegent-mcp` owns MCP protocol-facing APIs, tool registration patterns, and MCP transport integrations.

### Owns

- MCP server tool declarations and invocation adapters.
- MCP-aware auth/session handling and context normalization.
- MCP transport-specific compatibility constraints.
- MCP-specific observability and contract validation.

### Must Not Own

- General app orchestration wiring (`thegent-app`).
- Generic branch/worktree orchestration (`thegent-control-plane`).
- Long-running execution adapters and background workers (`thegent-execution`).
- Repo governance automation (`thegent-governance`).

### Boundary Rule

Keep MCP protocol changes inside module surface contracts so app command wiring only consumes the stable interface.

### Split Execution Bootstrap

- Module manifests: `Phenotype/projects/modules/thegent-mcp/manifest.json`
- Typical workflow command:

```bash
./scripts/worktree_governance.sh new backend m split-thegent-mcp
```
