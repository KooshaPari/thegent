# Research Notes

## AgilePlus current surfaces

### CLI

- `agileplus` already exposes `specify`, `research`, `plan`, `implement`, `validate`, `ship`, `retrospective`, `triage`, `queue`, `module`, `cycle`, `dashboard`, and `platform`.
- `specify`/`research`/`plan`/`implement` are feature-scoped and single-item oriented.
- `module` and `cycle` have CRUD-ish commands in CLI, and the HTTP API now mirrors part of that write surface (`PATCH/DELETE` for modules and state transitions for cycles), but full create/list parity is still incomplete.
- `queue` is storage-backed already via backlog create/list/pop operations; the remaining gap is backlog import/bulk-mutation ergonomics rather than persistence.

### MCP

- The MCP server exists and registers `features`, `governance`, and `status` tool groups.
- The tool files currently expose thin wrappers plus multiple stubs/placeholders.
- The MCP layer does not yet give the same entity-management affordances as the CLI.

### HTTP API

- Features and work packages have mutation routes.
- Modules and cycles are read-only in the API.
- Audit and governance routes exist.
- This still leaves a visible asymmetry: CLI can mutate the full module/cycle surface, while the API only exposes a subset of those writes.

## Governance and release research

- The release-governance spec already uses the 5-tier model: `alpha -> canary -> beta -> rc -> prod`.
- The active governance docs use the 5-tier model; any remaining vocabulary drift is now limited to
  stale notes or generated scaffolding that still needs a final sweep.
- The spec documents channel-aware gates, promotion workflows, hooks, and org-wide rollout.
- The workflow files present in the repo are reusable building blocks, but they are not yet aligned to the full 5-tier model.

## Specs already covering parts of the ask

- `kitty-specs/001-spec-driven-development-engine` covers AgilePlus as a local git + SQLite spec-driven development engine.
- `kitty-specs/002-org-wide-release-governance-dx-automation` covers org-wide DX, hooks, registries, promotion, and channel governance.
- `kitty-specs/003-agileplus-platform-completion` covers Plane sync, event sourcing, dashboard, CLI integration, multi-device sync, and core entity modeling.
- `kitty-specs/004-modules-and-cycles` covers module hierarchy and cycle lifecycle, but is still largely unimplemented.

## Gaps that matter

- No first-class batch mutation pipeline for specs, work items, or entity collections.
- No canonical migration flow for importing, reconciling, validating, and applying project state.
- No API parity for module/cycle writes.
- No complete MCP parity for module/cycle/work-item operations.
- No canary/high-extreme branch/package strategy expressed as a continuously updated local developer flow.
- No single orchestrated operator path that makes “all projects are fully migrated to AgilePlus” feel intuitive.

## Evidence pointers

- CLI entrypoint: `crates/agileplus-cli/src/main.rs`
- Queue placeholder: `crates/agileplus-cli/src/commands/queue.rs`
- Module CLI: `crates/agileplus-cli/src/commands/module.rs`
- Cycle CLI: `crates/agileplus-cli/src/commands/cycle.rs`
- API routes: `crates/agileplus-api/src/router.rs`
- Module API: `crates/agileplus-api/src/routes/module.rs`
- Cycle API: `crates/agileplus-api/src/routes/cycle.rs`
- MCP server: `python/src/agileplus_mcp/server.py`
- MCP features tools: `python/src/agileplus_mcp/tools/features.py`
- MCP governance tools: `python/src/agileplus_mcp/tools/governance.py`
- MCP status tools: `python/src/agileplus_mcp/tools/status.py`
