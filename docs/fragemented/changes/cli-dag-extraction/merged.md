# Merged Fragmented Markdown

## Source: changes/cli-dag-extraction/design.md

---
title: CLI DAG Extraction — Design
date: 2026-02-21
status: implemented
owner: agent-f (B90-W2-F1)
tags: [wl-120, b90, monolith-split, cli]
---

# Design: CLI DAG Extraction

## New Module Layout

```
src/thegent/cli/commands/
├── cli.py              # Legacy monolith (6,870 lines post-wave-2)
│                       # Exports: all public CLI helpers, app object,
│                       #          re-exports from run_cmds, session_cmds,
│                       #          governance_cmds, plan_cmds, model_cmds,
│                       #          infra_cmds, team_cmds
├── cli_dag.py          # EXTRACTED — 622 lines (WL-120 B90-W2-A1)
│                       # Contains: dag_*_cmd handlers (16 functions)
│                       # Imports helpers from cli.py; no business logic
├── run_cmds.py         # Re-exported from cli.py (WL-124)
├── session_cmds.py     # Re-exported from cli.py (WL-124)
├── governance_cmds.py  # Re-exported from cli.py (WL-124)
├── plan_cmds.py        # Re-exported from cli.py (WL-124)
├── model_cmds.py       # Re-exported from cli.py (WL-124)
├── infra_cmds.py       # Re-exported from cli.py (WL-124)
├── team_cmds.py        # Re-exported from cli.py (WL-124)
├── queue_commands.py   # Re-exported via delegation from cli.py (WL-124)
└── observability_impl.py # Extracted from impl.py (WL-120 B90-W2-A2)
```

## What Was Moved

### cli_dag.py (622 lines)

All DAG command handler functions extracted from `cli.py`:

| Function | Responsibility |
|----------|---------------|
| `dag_validate_cmd` | Validate DAG session file; exit 2 on errors |
| `dag_list_cmd` | List DAG tasks (table or JSON format) |
| `dag_add_cmd` | Add a new task to the active DAG |
| `dag_remove_cmd` | Remove a task from the DAG |
| `dag_cancel_cmd` | Cancel a running task |
| `dag_status_cmd` | Show DAG status summary |
| `dag_update_cmd` | Update task metadata (status, owner, deps) |
| `dag_ready_cmd` | Show tasks ready to execute |
| `dag_reconcile_cmd` | Reconcile DAG with git session state |
| `dag_run_cmd` | Run a specific task by ID |
| `dag_sync_cmd` | Sync DAG to upstream and auto-run next |
| `dag_checkpoint_cmd` | Create a DAG checkpoint snapshot |
| `dag_rollback_cmd` | Roll back to a named checkpoint |
| `dag_checkpoints_cmd` | List all saved checkpoints |
| `dag_recover_cmd` | Recover from failure (retry-failed action) |
| `dag_probe_cmd` | Probe DAG against a baseline |

### observability_impl.py (WL-120 A2, extracted from impl.py)

37 functions for health reporting, observe-summary, compliance, and review.
Imported by `impl.py` via a re-export block at line 1091.

## Re-Export Strategy

`cli.py` currently does **not** re-export `cli_dag.py` via a wildcard import.
The DAG Typer sub-application wires `cli_dag.py` directly.  This avoids
namespace pollution and allows `cli_dag.py` to be tested without importing
the full `cli.py` monolith.

`impl.py` re-exports `observability_impl.py` via named import at line 1091.

## Import Graph (simplified)

```
cli_dag.py
  └─ imports helpers from cli.py
       (LazyConsole, ThegentSettings, _atomic_write, _check_dag_cycles,
        _dag_path, _dag_update_task, _default_owner_tag,
        _ensure_contract_version_header, _ensure_dag_file,
        _parse_dag_full, _parse_dag_session, _parse_depends_on,
        _resolve_checkpoint_id, _resolve_cwd, _serialize_dag,
        _session_status_for, _validate_agent, _validate_dag,
        _validate_task_id, console, dag_ready_impl, dag_recover_impl,
        dag_run_impl, dag_sync_impl)
```

## Parity Notes

- All 16 `dag_*_cmd` handlers are present in `cli_dag.py`; none were lost.
- `cli.py` still contains the original function stubs (kept for any direct callers
  until removal gate is green).
- Import chain: `cli_dag.py` → `cli.py` (helpers only, not circular).

---

## Source: changes/cli-dag-extraction/proposal.md

---
title: CLI DAG Extraction — Proposal
date: 2026-02-21
status: implemented
owner: agent-f (B90-W2-F1)
tags: [wl-120, b90, monolith-split, cli]
---

# Proposal: Extract DAG Command Handlers from cli.py

## Problem Statement

`src/thegent/cli/commands/cli.py` had grown to 6,927 lines (pre-wave-2), far exceeding
the 500-line target for a single module.  The DAG command group (`dag_validate_cmd`,
`dag_add_cmd`, `dag_update_cmd`, `dag_list_cmd`, `dag_run_cmd`, `dag_ready_cmd`,
`dag_sync_cmd`, `dag_recover_cmd`, and related helpers) represented a discrete,
testable responsibility that could be cleanly extracted without breaking the public
CLI surface.

## Why This Extraction

1. **Single-responsibility**: DAG lifecycle (add/validate/run/sync/recover) is a
   coherent domain unit. Combining it with session, model, plan, and infra commands
   in a single 6k-line file violates SRP and makes grep/navigation impractical.

2. **LOC reduction**: Extraction reduces the cli.py monolith by ~620 lines
   (the size of `cli_dag.py`), moving it from 6,927 to ~6,307 lines — a step
   toward the 500-line ceiling mandated by WL-120 / WL-124.

3. **Independent testability**: `cli_dag.py` can be unit-tested in isolation with
   stubbed helpers from `cli.py`, without importing the full 6k-line monolith.

4. **Parallel extraction enabled**: Once DAG handlers are isolated, other command
   groups (session, infra, plan, model, team, run) can be extracted in parallel by
   separate agents without merge conflicts.

## Decision

Extract DAG CLI command handlers to `src/thegent/cli/commands/cli_dag.py`.
Keep all helper functions and business logic in `cli.py` (or `impl.py`/`dag_impl.py`).
The new module imports the helpers it needs from `cli.py` and delegates to them.

`cli.py` does **not** re-export `cli_dag.py` — the DAG sub-app wires its own
commands by importing `cli_dag.py` directly.  This is forward-compatible with
full monolith removal when all groups are extracted.

## Acceptance Criteria

- `cli_dag.py` exists and contains all `dag_*_cmd` handlers.
- `cli.py` still exports existing public symbols for backwards compatibility.
- `python -c "from thegent.cli.commands.cli_dag import dag_validate_cmd"` exits 0.
- Existing DAG-related tests pass without modification.

---

## Source: changes/cli-dag-extraction/tasks.md

---
title: CLI DAG Extraction — Remaining Tasks
date: 2026-02-21
status: in-progress
owner: agent-f (B90-W2-F1)
tags: [wl-120, b90, monolith-split, cli]
---

# Remaining Tasks: CLI Monolith Split

## Completed

- [x] **B90-W2-A1** Extract `dag_*_cmd` handlers to `cli_dag.py` (622 lines)
- [x] **B90-W2-A2** Extract observability/health handlers to `observability_impl.py`
- [x] **WL-124** Re-export `run_cmds`, `session_cmds`, `governance_cmds`, `plan_cmds`,
      `model_cmds`, `infra_cmds`, `team_cmds` from `cli.py` via wildcard re-exports
- [x] **W3-B1 (slice, 2026-02-21)** Delegate DAG internals/public impls in `impl.py` to
      `dag_impl.py` and remove duplicated in-file DAG implementation
      (`impl.py` line-count baseline: `6541 -> 5932` in
      `docs/reports/artifacts/wl120-monolith-baseline-2026-02-21.json`)
- [x] **W3-B2 (2026-02-21)** Extract session backend logic from `impl.py` to `session_impl.py`
      (1716 LOC; 36 functions extracted; `impl.py` body reduced by ~1000 lines of session logic)
- [x] **W3-B3 (2026-02-21)** Extract infra/compute backend logic from `impl.py` to `infra_impl.py`
      (560 LOC; 10 functions extracted; `impl.py` 5932 → 3719 total after W3-B2+B3, -2213 lines)
      LOC recorded in `.quality/loc-metrics.jsonl`

## Remaining Extractions (Future Waves)

### Wave-3: cli.py monolith further reduction

| ID | Target module | Estimated LOC | Depends on | Status |
|----|--------------|---------------|-----------|--------|
| W3-A1 | `cli_session.py` — extract all `session_*_cmd` handlers | ~400 | A1 pattern stable | DONE (99 LOC final) |
| W3-A2 | `cli_infra.py` — extract all infra/compute/sandbox cmd handlers | ~350 | A1 pattern stable | DONE |
| W3-A3 | `cli_plan.py` — extract all plan/workstream cmd handlers | ~300 | A1 pattern stable | DONE |
| W3-A4 | `cli_models.py` — extract all model catalog cmd handlers | ~250 | A1 pattern stable | DONE |
| W3-A5 | `cli_governance.py` — extract governance/team/audit cmd handlers | ~200 | A1 pattern stable | DONE |

### Wave-3: impl.py monolith further reduction

| ID | Target module | Estimated LOC | Depends on | Status |
|----|--------------|---------------|------------|--------|
| W3-B1 | `dag_impl.py` — extract DAG backend logic | ~500 | A2 pattern stable | DONE |
| W3-B2 | `session_impl.py` — extract session backend | 1716 actual | A2 pattern stable | DONE |
| W3-B3 | `infra_impl.py` — extract infra/compute backend | 560 actual | A2 pattern stable | DONE |

## Cut-over Gate (per module)

Before removing the stub shim from `cli.py` / `impl.py` for any extracted module:

1. `python -c "from thegent.cli.commands.<module> import <cmd>"` exits 0
2. Focused unit tests for the extracted module pass (`pytest tests/commands/test_<module>.py`)
3. No p95 CLI latency regression vs baseline
4. Core-boundary strict check still green (`task quality:core-boundary:strict`)
5. LOC metric recorded for the extracted module in `.quality/loc-metrics.jsonl`

## Target Ceiling

- `cli.py`: reduce from 6,870 to < 2,000 lines by end of Wave-5
- `impl.py`: reduce from 6,541 to < 2,000 lines by end of Wave-5
- Each extracted module: < 500 lines (enforced by `contracts/max_lines.json`)

---
