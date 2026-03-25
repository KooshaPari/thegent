# Thegent Execution Boundary

## Module Contract

`thegent-execution` owns execution adapters and runtime behavior used by commands across repos.

### Owns

- Local and distributed execution routing.
- Environment profile handling and task dispatch semantics.
- Runtime retries/backpressure/restart behavior for command execution.
- Execution telemetry at run-time boundary.

### Must Not Own

- App-level command UX and command graph registration (`thegent-app`).
- MCP transport definitions (`thegent-mcp`).
- Execution policy governance logic (`thegent-governance`).
- Control-plane routing abstractions (`thegent-control-plane`).

### Boundary Rule

Execution logic is module-owned and cannot own CLI surface decisions about which repos belong in scope.

### Split Execution Bootstrap

- Module manifests: `Phenotype/projects/modules/thegent-execution/manifest.json`
- Typical workflow command:

```bash
./scripts/worktree_governance.sh new backend m split-thegent-execution
```
