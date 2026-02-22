# Merged Fragmented Markdown

## Source: changes/mcp-server-extraction/design.md

---
title: MCP Server Tool Extraction — Design
date: 2026-02-21
status: implemented
owner: agent-f (B90-W2-F1)
tags: [wl-126, b90, monolith-split, mcp]
---

# Design: MCP Server Tool Extraction

## New Module Layout

```
src/thegent/mcp/
├── server.py              # Registrar + lifespan + middleware (3,939 lines)
│                          # Loads tool groups via _load_server_tools_*_module()
├── server_catalog_tools.py # Catalog tool group (direct import)
├── server_dispatch_helpers.py
├── server_elicitation_cache_helpers.py
├── server_elicitation_response_helpers.py
├── server_meta_helpers.py
├── server_module_loader.py
├── server_policy_quality_helpers.py
├── server_result_helpers.py
├── server_runtime_helpers.py
└── server/                # Tool group implementations (extracted)
    ├── auth.py
    ├── lifecycle.py
    ├── resources_catalog.py
    ├── resources_contracts.py
    ├── resources_sessions.py
    ├── resources_system.py
    ├── resources_workflow.py
    ├── resources_workstream.py
    ├── session_tools.py
    ├── tools_batch4.py
    ├── tools_catalog.py
    ├── tools_contract_observe.py
    ├── tools_coordination.py
    ├── tools_escalation.py
    ├── tools_governance.py
    ├── tools_handoff_queue.py
    ├── tools_locking_planning.py
    ├── tools_lsp.py
    ├── tools_planning.py
    ├── tools_prompt_and_handoff.py
    ├── tools_queue_mutations.py
    ├── tools_queue.py
    ├── tools_research.py
    ├── tools_runtime.py
    ├── tools_sessions.py
    ├── tools_skills.py
    ├── tools_terminal.py
    ├── tools_workstream_governance.py
    ├── tools_workstream_lsp.py
    └── workflow_prompts.py
```

## Tool Groups Extracted

| Module | Domain | Load pattern |
|--------|--------|--------------|
| `server/tools_sessions.py` | Session lifecycle tools | `_load_server_tools_sessions_module()` |
| `server/tools_queue.py` | Queue read tools | `_load_server_tools_queue_module()` |
| `server/tools_terminal.py` | Terminal/PTY tools | `_load_server_tools_terminal_module()` |
| `server/tools_escalation.py` | Escalation/alert tools | `_load_server_tools_escalation_module()` |
| `server/tools_governance.py` | Governance rule tools | `_load_server_tools_governance_module()` |
| `server/tools_research.py` | Research/search tools | `_load_server_tools_research_module()` |
| `server/tools_planning.py` | Planning/workstream tools | `_load_server_tools_planning_module()` |
| `server/tools_contract_observe.py` | Contract observation tools | `_load_server_tools_contract_observe_module()` |
| `server/tools_locking_planning.py` | Locking + planning combined | `_load_server_tools_locking_planning_module()` |
| `server/tools_skills.py` | Skill catalog tools | `_load_server_tools_skills_module()` |
| `server/tools_coordination.py` | Multi-agent coordination | `_load_server_tools_coordination_module()` |
| `server/tools_runtime.py` | Runtime diagnostics tools | `_load_server_tools_runtime_module()` |
| `server/tools_batch4.py` | Batch-4 additional tools | `_load_server_tools_batch4_module()` |
| `server_catalog_tools.py` | Model catalog tools | direct import (not lazy-loaded) |

## Loading Pattern

`server.py` uses a consistent lazy-loading pattern for each tool group:

```python
def _load_server_tools_<group>_module() -> Any:
    module_path = Path(__file__).with_suffix("") / "tools_<group>.py"
    spec = importlib.util.spec_from_file_location(
        "thegent.mcp._server_tools_<group>", module_path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load tools_<group>.py from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module

_server_tools_<group> = _load_server_tools_<group>_module()
```

This pattern:
- Fails loudly at startup if a tool group module is missing (no silent degradation).
- Allows each tool group to be modified independently without touching `server.py`.
- Preserves the FastMCP tool registration protocol in each extracted module.

## Re-Export Strategy

`server.py` does not re-export tool group symbols.  Tool groups are loaded as
opaque modules; their `register_tools(mcp)` or equivalent entry point is called
during lifespan initialization.

## What Remains in server.py

- FastMCP app instantiation and lifespan
- Middleware registration (logging, rate-limiting, error-handling, timing, caching)
- Auth and lifecycle module loading
- Resource group module loading
- Tool group lazy loading (the `_load_server_tools_*_module()` functions)
- Top-level route/prompt registration

---

## Source: changes/mcp-server-extraction/proposal.md

---
title: MCP Server Tool Extraction — Proposal
date: 2026-02-21
status: implemented
owner: agent-f (B90-W2-F1)
tags: [wl-126, b90, monolith-split, mcp]
---

# Proposal: Extract Tool Groups from mcp/server.py

## Problem Statement

`src/thegent/mcp/server.py` grew to 3,944 lines pre-wave-2 (3,939 post-wave-2), well
above the 500-line module ceiling.  The file contained registration logic for 13+
independent tool groups (sessions, queue, terminal, escalation, governance, research,
planning, contract_observe, locking_planning, skills, coordination, runtime, batch4)
each with its own `_load_server_tools_<group>_module()` factory and registration
handler.

These tool groups are independent domains — sessions tooling has no logical dependency
on escalation tooling, for example.  Keeping them in a single file causes:

1. **Review friction**: Any change to one tool group requires parsing 3.9k lines.
2. **Merge conflicts**: Parallel agents modifying different tool groups always conflict.
3. **Test isolation impossible**: Cannot import and test a single tool group without
   loading the entire server module.

## Why This Extraction

1. **Tool group isolation**: Each tool group is a coherent domain (sessions, queue,
   governance, research, planning, etc.).  Extracting them to `mcp/server/<group>.py`
   enables independent development and testing.

2. **LOC reduction**: The `server/` subdirectory pattern already exists — 24 tool
   group modules live there (`tools_sessions.py`, `tools_governance.py`, etc.).
   The `server.py` monolith only needed to be updated to delegate to these existing
   modules via its `_load_server_tools_<group>_module()` pattern.

3. **Zero business logic duplication**: The extracted modules own the tool definitions;
   `server.py` acts as the router/registrar only.

## Decision

Keep `server.py` as the registrar/lifespan/middleware entry point.  All tool group
implementations live in `src/thegent/mcp/server/<group>.py`.  The `server.py`
module loads each group at startup via the `_load_server_tools_<group>_module()`
pattern (already in place post-extraction).

## Acceptance Criteria

- `server.py` < 4,000 lines (ceiling; target < 2,000 in wave-5).
- All 13+ tool group modules exist under `src/thegent/mcp/server/`.
- `python -c "from thegent.mcp.server import app"` exits 0 in < 2s.
- MCP test suite passes without modification.

---

## Source: changes/mcp-server-extraction/tasks.md

---
title: MCP Server Tool Extraction — Remaining Tasks
date: 2026-02-21
status: in-progress
owner: agent-f (B90-W2-F1)
tags: [wl-126, b90, monolith-split, mcp]
---

# Remaining Tasks: MCP Server Split

## Completed

- [x] All 13+ tool group files exist under `src/thegent/mcp/server/`
- [x] `server.py` loads each group via `_load_server_tools_<group>_module()` pattern
- [x] Helper modules extracted: `server_dispatch_helpers.py`,
      `server_policy_quality_helpers.py`, `server_runtime_helpers.py`,
      `server_meta_helpers.py`, `server_result_helpers.py`,
      `server_elicitation_cache_helpers.py`, `server_elicitation_response_helpers.py`,
      `server_module_loader.py`
- [x] **W3-C3 (slice, 2026-02-21)** Collapsed remaining manual loader boilerplate in
      `server.py` to shared `server_load_module` wrappers while preserving
      `_load_server_tools_<group>_module()` call surface (`server.py` line-count
      baseline: `3867 -> 3845` in `docs/reports/artifacts/wl120-monolith-baseline-2026-02-21.json`)

## Remaining Extractions (Future Waves)

### Wave-3: server.py lifespan and registration further reduction

| ID | Target | Estimated LOC | Depends on | Status |
|----|--------|---------------|-----------|--------|
| W3-C1 | Extract auth/lifecycle loading into `server_bootstrap.py` | ~200 | pattern stable | DONE (28 LOC final) |
| W3-C2 | Extract resource group loading into `server_resources.py` | ~150 | pattern stable | DONE (78 LOC final) |
| W3-C3 | Extract tool group loading into `server_tool_loader.py` | ~300 | pattern stable | DONE (218 LOC final) |
| W3-C4 | Extract middleware setup into `server_middleware.py` | ~100 | pattern stable | DONE (57 LOC final) |
| W3-C5 | `server.py` reduced to lifespan + import delegation (~200 lines) | 952 final | W3-C1..C4 | DONE |

### Wave-4: Tool group unit tests

| ID | Target | Notes |
|----|--------|-------|
| W4-C1 | `tests/mcp/tools/test_tools_governance.py` | Currently no isolated tool tests |
| W4-C2 | `tests/mcp/tools/test_tools_planning.py` | |
| W4-C3 | `tests/mcp/tools/test_tools_sessions.py` | |
| W4-C4 | `tests/mcp/tools/test_tools_research.py` | |

## Cut-over Gate (per extraction)

Before removing a loader stub from `server.py`:

1. Tool group module imports cleanly: `python -c "import thegent.mcp.server.<group>"`
2. FastMCP tool registration call succeeds in isolated test
3. MCP integration tests still pass: `pytest tests/mcp/ -q`
4. `python -c "from thegent.mcp.server import app"` still exits 0 in < 2s
5. No new ruff errors in the extracted module

## Target Ceiling

- `server.py`: reduce from 3,939 to < 500 lines by end of Wave-5
- Each tool group module: < 500 lines (enforced by `contracts/max_lines.json`)

---
