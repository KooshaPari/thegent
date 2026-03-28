# Testing Strategy

## Principles

- Test the same object model through CLI, MCP, and API.
- Prefer contract tests for surface parity.
- Add batch-import tests before adding more import features.
- Keep release-governance tests channel-aware.
- Validate docs and generated artifacts as part of the workflow.

## Test layers

### Unit

- Parser tests for import bundle schemas.
- Validation tests for module/cycle mutation rules.
- Queue persistence logic tests.
- Channel normalization tests.

### Integration

- API module/cycle mutation tests.
- API batch import tests.
- MCP wrapper tests against the backend client.
- CLI command tests for batch and queue flows.

### Contract

- CLI vs API parity for shared operations.
- MCP tool contracts for command shape and error shape.
- Release channel contracts for promotion gates.

### End-to-end

- Spec import through applied state.
- Module/cycle creation through the API surface.
- Queue ingest through dequeue/triage.
- Canary branch promotion through the workflow path.

## Acceptance checks

- No workflow path should require seed SQL for ordinary operator tasks.
- A user should be able to import, validate, apply, and audit a bundle.
- A user should be able to mutate module and cycle state through API and MCP.
- A user should be able to promote on the full 5-tier channel ladder.

