# Implementation Strategy

## Repo / Service Classification

### 1. `thegent-core`
- Keep in main repo initially.
- Owns: configuration, tenancy, orchestration contracts, shared domain models, dependency injection.
- Must become smaller, not broader.

### 2. `thegent-protocols`
- Type: `standalone_repo`
- Owns: `protocols`, `acp`, MCP transport contracts, JSON-RPC server/client, typed protocol schemas.
- Reason: high duplication, broad reuse, low dependency on UI/CLI concerns.

### 3. `thegent-sync`
- Type: `plugin_microservice`
- Owns: autosync, board sync, GitHub/Linear adapters, status reflection, idempotency cache contracts.
- Reason: external API coupling, retry/throttle behavior, and placeholder-heavy current implementation make it a natural adapter service.

### 4. `thegent-audit`
- Type: `standalone_repo`
- Owns: audit trail, shadow git audit, governance vetting, evidence and compliance collectors.
- Reason: strong bounded context, duplicated today, can run in-process or batch without needing full agent runtime.

### 5. `thegent-planning`
- Type: `standalone_repo`
- Owns: work-stream parsing, plan DAGs, dependency gating, planning persistence.
- Reason: business-domain package consumed by both CLI and services.

### 6. `thegent-agents`
- Type: `microservice`
- Owns: Codex/Claude/provider session orchestration, session index, sub-agent dispatch, cliproxy manager.
- Reason: long-lived runtime behavior, large state surface, natural service boundary.

### 7. `thegent-cli`
- Type: `standalone_repo`
- Owns: command UX only.
- Reason: should compose package APIs instead of owning mirrored business logic.

### 8. `thegent-hooks`
- Type: `standalone_repo`
- Owns: pre/post-edit hooks and artifact quality gates.
- Reason: separate release cadence, giant Rust binary, unrelated to application runtime.

### 9. `thegent-shm` and `thegent-shims`
- Type: `standalone_repo`
- Owns: shared memory, native bridge, FFI/runtime plumbing.
- Reason: low-level systems code should not churn with Python app releases.

## First Extraction Seams

### Seam A: Protocols
- Source of truth: `packages/thegent-protocols`
- Delete/replace mirrors under `src/thegent/protocols`, `src/thegent/acp`, and duplicate MCP transport helpers.
- Why first: highest reuse, lowest product ambiguity.
- Status update:
  - `src/thegent/acp/client.py` and `src/thegent/acp/server.py` are now reduced to explicit legacy shims importing from `thegent_protocols.acp`.
  - This keeps the public `thegent.acp` path stable while removing duplicate ACP implementation ownership from `src/thegent/acp`.
  - `src/thegent/protocols/a2a.py`, `src/thegent/protocols/jsonrpc_agent_server.py`, and `src/thegent/protocols/turn_submit_boundaries.py` are now legacy facades over `thegent_protocols.protocols.*`.
  - The JSON-RPC and turn-boundary facades intentionally re-export the full authority module surface because lane tests still depend on helper/private symbols from the legacy path.
  - Authority bugs found during the cut were fixed in `packages/thegent-protocols/src/thegent_protocols/protocols/jsonrpc_agent_server.py` rather than papered over in `src/thegent/protocols`.

### Seam B: Sync
- Source of truth: `packages/thegent-sync`
- Replace stub `src/thegent/integrations/workstream_autosync.py` with authoritative package wiring.
- Move `_perform_board_sync` and autosync cycle logic behind adapters.
- Why second: largest unfinished user-facing feature cluster.

### Seam C: Audit
- Source of truth: `packages/thegent-audit`
- Collapse mirrored `shadow_audit_git.py`, governance compliance collectors, and audit trail logic.
- Why third: concrete bounded context and heavy duplication.

## Non-Goals For First Wave
- Do not split UI/TUI packages first.
- Do not attempt one-shot extraction of all agent runtimes.
- Do not keep dual-write or dual-authority mirrors after a seam is selected.

## Cross-Project Reuse Opportunities
- `thegent-sync` adapters can become shared board/project sync libraries for other Phenotype repos.
- `thegent-protocols` can serve as the common MCP/JSON-RPC bridge layer across `cliproxyapi-plusplus`, `heliosCLI`, and future agent runtimes.
- `thegent-audit` collectors can become reusable governance enforcement tooling across Phenotype repos.

## Validation Notes
- The default repo runner is now workspace-aware via root pytest `pythonpath` entries for all extracted package `src/` trees.
- `src/thegent/__init__.py` now registers legacy subpackage aliases lazily instead of eagerly importing observability/platform packages at import time.
- Protocol and compatibility checks passed with default repo execution:
  - `TMPDIR=$PWD/.tmp uv run pytest tests/protocols/test_jsonrpc_agent_server_contract.py tests/protocols/test_a2a.py tests/protocols/test_acp_compatibility.py tests/protocols/test_wl9690_wl9699_lane_k.py tests/protocols/test_wl10570_wl10579_lane_a.py -q`
- ACP adapter and CLI wiring suites passed directly through the default workspace runner:
  - `TMPDIR=$PWD/.tmp uv run pytest tests/adapters/test_acp_server.py tests/adapters/test_acp_session_endpoints.py tests/test_wl104_agent_server_cli_wiring.py -q`
- The initial `uv run pytest` attempt failed before these fixes because `packages/thegent-agint` declared `readme = "README.md"` without shipping that file.
