# Merged Fragmented Markdown

## Source: changes/two-surface-architecture/design.md

---
title: Two-Surface Architecture Design
date: 2026-02-21
status: accepted
owner: B90-W3-agent-a
tags: [wl-136, design, import-boundary, decomposition]
---

# Two-Surface Architecture Design

## Module Classification Table

| Module | Surface | Rationale |
|--------|---------|-----------|
| `src/thegent/agents/` | core | Production agent runners |
| `src/thegent/mcp/` | core | MCP server — always-on |
| `src/thegent/routing/` | core | Request routing — hot path |
| `src/thegent/governance/` | core | SLO emitter, policy engine |
| `src/thegent/infra/` | core | Infrastructure primitives |
| `src/thegent/config.py` | core | Config resolution at startup |
| `src/thegent/session/` | core | Session state management |
| `src/thegent/orchestration/` | core | DAG execution engine |
| `src/thegent/cli/commands/impl.py` | core | Execution dispatch |
| `src/thegent/cli/commands/run_cmds.py` | core | `thegent run` entrypoint |
| `src/thegent/cli/commands/cli_dag.py` | tooling | DAG management CLI (WL-120) |
| `src/thegent/cli/commands/cli_tooling.py` | tooling | Dev utilities (WL-136) |
| `src/thegent/cli/commands/impl_execution.py` | tooling | Execution boundary shim |
| `benchmarks/` | tooling | Performance benchmarks |
| `scripts/` | tooling | Dev/QA scripts |

## Import Boundary Rule

**Rule**: Tooling modules MAY import core modules. Core modules MUST NOT import tooling modules.

```
core  ← tooling   (allowed: tooling depends on core)
core  → tooling   (FORBIDDEN: core must not depend on tooling)
```

This is an acyclic dependency graph with core at the root.

### Enforcement

The import boundary is enforced by `scripts/check_thegent_core_boundary.py`:

```bash
# Advisory check (warns, non-blocking)
uv run python scripts/check_thegent_core_boundary.py

# Strict check (exits 1 on violation — used in CI)
uv run python scripts/check_thegent_core_boundary.py --strict
```

Via Taskfile:
```bash
task quality:core-boundary         # advisory
task quality:core-boundary:strict  # CI-blocking
```

Violations are any import edge where a core module imports from a tooling module.
The enforcement script reads `config/thegent_core_boundary.toml` for the boundary
definition.

## Tooling Module Details

### `cli_dag.py` (tooling surface)

Contains the 16 `dag_*_cmd` functions extracted from `cli.py` in WL-120 B90-W2-A1:

- `dag_validate_cmd`, `dag_list_cmd`, `dag_add_cmd`, `dag_remove_cmd`
- `dag_cancel_cmd`, `dag_status_cmd`, `dag_update_cmd`, `dag_ready_cmd`
- `dag_reconcile_cmd`, `dag_run_cmd`, `dag_sync_cmd`, `dag_checkpoint_cmd`
- `dag_rollback_cmd`, `dag_checkpoints_cmd`, `dag_recover_cmd`, `dag_probe_cmd`

These commands import from `cli.py` helpers (lazy imports via the `_lazy_import` pattern)
and from `thegent.execution` (core). They orchestrate DAG sessions and are user-facing
developer tools, not production runtime.

### `cli_tooling.py` (tooling surface)

Contains 5 commands extracted from `cli.py` in WL-136 B90-W2-D2:

- `audit_verify_cmd` — cross-check audit log against governance contracts
- `benchmark_cmd` — report orchestration performance metrics (WP-6001)
- `deep_research_cmd` — trigger deep research sub-agent workflow
- `drift_monitor_cmd` — continuous drift detection against governance baseline
- `roadmap_cmd` — generate roadmap view from workstream and plan data

### `impl_execution.py` (execution boundary shim)

A thin module (33 lines) that re-exports the four canonical execution boundary
functions from `impl.py`:

```python
from thegent.cli.commands.impl_execution import (
    run_impl, bg_impl, resume_impl, loop_impl
)
```

This shim is a transition artifact. Once all callers are migrated to import from
`impl_execution`, the function bodies will be moved here in a follow-on sprint (WL-120 Phase 3).

## Contract Metadata

The boundary is also machine-readable in `contracts/runtime/runtime-modularization-matrix.json`.
This file records the module classification, surface assignment, and migration status
for each module in the decomposition.

## Decision: Backmatter

**Decision delta**: cli_dag.py and cli_tooling.py are classified as tooling; impl.py
and run_cmds.py remain core.

**Validation commands**:
```bash
task quality:core-boundary:strict
uv run pytest tests/cli/test_wl120_extraction_hardening.py -v
uv run pytest tests/governance/test_wl136_two_surface_adr.py -v
```

**Residual risks**:
- `cli.py` still imports from `cli_tooling.py` via re-exports; these must be removed
  when cli.py is fully decomposed (Wave-5+).
- `cli_dag.py` imports from `cli.py` (lazy import pattern); this creates a transient
  coupling until Phase 3 migration.

**Follow-up review date**: 2026-03-21

---

## Source: changes/two-surface-architecture/proposal.md

---
title: Two-Surface Architecture Proposal
date: 2026-02-21
status: accepted
owner: B90-W3-agent-a
tags: [wl-136, architecture, cli, decomposition]
---

# Two-Surface Architecture Proposal

## Summary

thegent's Python codebase is split into two distinct surfaces: **core** and **tooling**.
This separation was initiated in Wave-1 (WL-120) and formalized in Wave-2 (WL-136,
B90-W2-D2). The two-surface split enforces a strict import boundary and allows the
tooling surface to be omitted from production deployments.

## The Core Surface

The **core** surface contains the production runtime path of thegent:

- **Orchestration**: `src/thegent/agents/`, `src/thegent/orchestration/`
- **MCP server**: `src/thegent/mcp/`
- **Routing**: `src/thegent/routing/`
- **Governance runtime**: `src/thegent/governance/` (SLO emitters, policy engine)
- **Infrastructure**: `src/thegent/infra/`
- **Configuration**: `src/thegent/config.py`, `src/thegent/config/`
- **Session management**: `src/thegent/session/`
- **Core CLI dispatch**: `src/thegent/cli/commands/impl.py`, `src/thegent/cli/commands/run_cmds.py`

Core modules are performance-critical and must start quickly. They must not import
tooling modules. Core is the surface deployed to production and embedded in agent
runtimes.

## The Tooling Surface

The **tooling** surface contains development utilities, research helpers, benchmarks,
audit commands, and QA workflows:

- **DAG CLI commands**: `src/thegent/cli/commands/cli_dag.py` — dag_* orchestration
  commands for managing DAG sessions. These are developer and orchestration tooling.
- **Tooling CLI commands**: `src/thegent/cli/commands/cli_tooling.py` — audit_verify,
  benchmark, deep_research, drift_monitor, roadmap commands.
- **Execution boundary shim**: `src/thegent/cli/commands/impl_execution.py` — thin
  shim re-exporting core execution functions; lives in the CLI surface.
- **Benchmarking**: `benchmarks/`
- **Scripts**: `scripts/` — collection, analysis, rendering

Tooling modules may import core modules. Core modules MUST NOT import tooling modules.

## Motivation

1. **Startup performance**: Core CLI (`thegent run`, `thegent bg`) must start in under
   250ms. Importing heavy tooling at startup violates the CLI SLO.
2. **Deployment footprint**: Production containers do not need research/benchmarking
   code; the two-surface split enables slimmer images.
3. **Separation of responsibilities**: Tooling evolves at a different cadence than core.
   Decoupling prevents tooling churn from breaking core contracts.
4. **Test isolation**: Core unit tests run without tooling deps; tooling tests may
   require heavier fixtures.

## Decision

Split all CLI commands into core (production path) and tooling (developer/QA path),
with a machine-enforced import boundary. Violations are detected by
`scripts/check_thegent_core_boundary.py` and blocked in CI.

## Alternatives Considered

- **Single surface**: Rejected. Monolithic CLI.py (6,994 LOC) is unmaintainable and
  violates startup SLOs.
- **Plugin architecture**: Considered for Wave-5+. The current split is a prerequisite.
- **Separate packages**: Deferred. Two-surface within the same package is sufficient for
  now and avoids packaging complexity.

---

## Source: changes/two-surface-architecture/tasks.md

---
title: Two-Surface Architecture — Remaining Tasks
date: 2026-02-21
status: in-progress
owner: B90-W3-agent-a
tags: [wl-136, tasks, wave-4, decomposition]
---

# Two-Surface Architecture — Remaining Tasks

## Completed (Wave-1 and Wave-2)

| Task | Status | Artifact |
|------|--------|----------|
| Extract dag_* commands from cli.py | DONE | `cli_dag.py` |
| Extract tooling commands from cli.py | DONE | `cli_tooling.py` |
| Create execution boundary shim | DONE | `impl_execution.py` |
| Classify modules (core vs tooling) | DONE | `design.md` |
| Machine-readable boundary matrix | DONE | `contracts/runtime/runtime-modularization-matrix.json` |
| Boundary enforcement script | DONE | `scripts/check_thegent_core_boundary.py` |

## Wave-4 Extractions (Remaining cli.py decomposition)

The following extractions are planned for Wave-4 to reduce `cli.py` from ~6,994 LOC
to under 2,000 LOC. Each module extracts a logical command group.

### cli_session.py

**Target**: Extract session management commands from `cli.py`.
**Commands**: `session_list_cmd`, `session_status_cmd`, `session_attach_cmd`,
`session_fork_cmd`, `session_rollback_cmd`, `session_export_cmd`.
**Surface**: tooling (session inspection is developer-facing).
**Dependencies**: `session_cmds.py`, `session_cmds_helpers.py` (already extracted).
**Predecessor**: Verify `session_cmds.py` is fully separated first.

### cli_infra.py

**Target**: Extract infrastructure commands from `cli.py`.
**Commands**: `infra_start_cmd`, `infra_stop_cmd`, `infra_status_cmd`,
`infra_logs_cmd`, `infra_reset_cmd`.
**Surface**: tooling (infra management is operator-facing).
**Dependencies**: `infra_cmds.py` and helpers (already extracted).
**Predecessor**: Verify `infra_cmds.py` is complete.

### cli_plan.py

**Target**: Extract planning commands from `cli.py`.
**Commands**: `plan_next_cmd`, `plan_loop_cmd`, `plan_incorporate_cmd`,
`plan_list_cmd`, `plan_archive_cmd`.
**Surface**: tooling (planning is orchestration tooling).
**Dependencies**: `plan_cmds.py` (already extracted).
**Predecessor**: Boundary test for plan_cmds.py.

### cli_models.py

**Target**: Extract model management commands from `cli.py`.
**Commands**: `models_list_cmd`, `models_inspect_cmd`, `models_set_cmd`,
`models_cost_cmd`.
**Surface**: tooling (model management is developer configuration).
**Dependencies**: `model_cmds.py` (already extracted).
**Predecessor**: Verify model_cmds.py import is clean.

### cli_governance.py

**Target**: Extract governance commands from `cli.py`.
**Commands**: `govern_conformance_cmd`, `govern_audit_cmd`, `govern_policy_cmd`,
`govern_slo_cmd`.
**Surface**: tooling (governance inspection is operator tooling).
**Dependencies**: `governance_cmds.py` (already extracted).
**Predecessor**: Boundary enforcement test for governance_cmds.py.

## Wave-4+ SLO Dashboard Wiring

Wire the SLO pass/fail gate to CI:

1. `scripts/check_slo_gate.py` — reads `.quality/slo-metrics.jsonl`, exits 1 on red
   (WL-135 B90-W3-A4).
2. Add `slo:check` task to `Taskfile.yml` (WL-135 B90-W3-A4).
3. Integrate `task slo:check` into `.github/workflows/ci.yml` quality gate step.
4. Wire SLO emission into `task metrics:loc` so each CI run emits a metric.

## Boundary Enforcement Test Reference

The canonical boundary enforcement test is:

```
uv run pytest tests/cli/test_wl120_extraction_hardening.py -v
uv run pytest tests/governance/test_wl136_two_surface_adr.py -v
```

These tests must pass before any Wave-4 extraction PR is merged.

---
