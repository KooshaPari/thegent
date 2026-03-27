# Session Overview

## Goal
Evaluate `thegent` for stabilization-by-decomposition and define an execution-ready breakup plan into hexagonal polyrepos, plugin microservices, and a smaller control-plane core.

## Success Criteria
- Identify the highest-risk monolith seams using current code evidence, not aspirational architecture.
- Classify each seam as `standalone_repo`, `microservice`, `plugin_microservice`, or `keep_in_core`.
- Define a phased extraction order that avoids feature regression.
- Name the first low-risk extraction seams that can start immediately.

## Current Findings
- The repository currently contains mirrored code across `src/thegent/*` and `packages/thegent-*/*`, producing nearly 1,000 duplicate path pairs.
- Several domains exceed sane module size and are duplicated at the same time, which amplifies drift risk.
- The autosync / board-integration surface still contains placeholder and stub implementations while tests already expect a real domain model.
- Rust crates and Python command surfaces are mixed into one operational repo, but they have separable runtime responsibilities.

## Executed In This Session
- Started Seam A by collapsing `src/thegent/acp/{client,server}` to legacy import shims backed by `packages/thegent-protocols`.
- Finished the first `src/thegent/protocols/*` cut by collapsing the legacy `a2a`, `jsonrpc_agent_server`, and `turn_submit_boundaries` surfaces onto `packages/thegent-protocols`.
- Added compatibility coverage for the legacy `thegent.acp` import surface so authority stays in `thegent_protocols`.
- Fixed an extracted workspace packaging defect by adding the missing `packages/thegent-agint/README.md`, which allowed `uv` to resolve the package and refresh `uv.lock`.
- Restored missing `thegent_core.infra` compatibility exports for `fast_subprocess` and `fast_yaml_parser`, which were already consumed by extracted packages.
- Restored missing settings/runner compatibility needed by extracted packages and default test execution:
  - workspace-aware pytest `pythonpath`
  - lazy subpackage alias registration in `src/thegent/__init__.py`
  - `otel_console` setting in `thegent_core` config
- Fixed an unrelated broken protocol assertion in `tests/protocols/test_a2a.py` uncovered during seam validation.
- Fixed multiple authority-package defects in `thegent_protocols.protocols.jsonrpc_agent_server` that only surfaced once the legacy mirror stopped shadowing it.

## Recommended End State
- Keep a thin `thegent-core` control plane in-process.
- Move protocol, audit, sync, planning, and agent runtimes into explicit repos/packages with strict ports/adapters.
- Convert board sync / provider sync / MCP bridge surfaces into plugin microservices where they do not need the full CLI or orchestration runtime.
