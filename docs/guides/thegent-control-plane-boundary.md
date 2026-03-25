# Thegent Control-Plane Boundary

## Module Contract

`thegent-control-plane` owns orchestration control logic that links policy, tenancy, and cross-repo execution direction.

### Owns

- Repo policy selection and cross-repo execution sequencing.
- Snapshot orchestration and control-plane command choreography.
- Global execution policy defaults for module orchestration.

### Must Not Own

- App command entrypoints and registration (`thegent-app`).
- MCP transport runtime (`thegent-mcp`).
- Background execution primitives (`thegent-execution`).
- Governance guardrail rule catalogs and policy exceptions (`thegent-governance`).

### Boundary Rule

Control-plane behavior must expose explicit interfaces and avoid hard dependency on CLI-level argument parsing details.

### Split Execution Bootstrap

- Module manifests: `Phenotype/projects/modules/thegent-control-plane/manifest.json`
- Typical workflow command:

```bash
./scripts/worktree_governance.sh new backend m split-thegent-control-plane
```
