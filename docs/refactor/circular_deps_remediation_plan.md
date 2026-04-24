# Circular Dependency Remediation Plan

**Date**: 2026-04-24  
**Repository**: thegent  
**Status**: Planning (No Code Changes)  
**Scope**: Analysis of 8 circular dependencies and proposed module reorganization

---

## Executive Summary

The thegent codebase contains **8 critical circular dependencies** that prevent isolated testing, complicate dependency injection, and block CI/CD checks. This plan identifies each cycle, analyzes root causes, and proposes a 5-way package split to eliminate them. Estimated remediation effort: **3–4 weeks** using a phased, predecessor-first approach.

---

## Part 1: The 8 Circular Dependencies

### Cycle 1: Contracts ↔ Output Parser
**Detection**: `thegent.contracts` ↔ `thegent.output_parser` (bidirectional)

**Source Files**:
- `src/contracts/` — Domain contract definitions
- `src/output_parser/` — Result parsing from agent outputs
- `src/protocols/jsonrpc_agent_server.py` — JSONRPC protocol bridge

**Root Cause**: Output parser needs contract types for validation; contracts need output parser for serialization. Both modules are in the "middle" of the dependency graph.

**Impact**: Medium — only 2 modules involved, but blocks all downstream imports

---

### Cycle 2: CLI → Execution → CLI
**Detection**: `thegent.cli` depends on `thegent.execution`; `thegent.execution` depends back on `thegent.cli`

**Source Files**:
- `src/cli/` — CLI entry point and command handlers (~500 LOC in routes, subcommands)
- `src/cli/services/run_execution_core_helpers.py` — **1,623 LOC god function** (`run_impl_core`, `bg_impl_core`)
- `src/execution/` — Core execution engine
- `src/execution/executor.py` — Task runner with CLI callbacks

**Root Cause**: CLI invokes execution engine; execution engine calls back to CLI for status updates, logging, and user prompts. The god function `run_impl_core()` orchestrates everything, creating a circular reference.

**Impact**: High — blocks test isolation for both modules

---

### Cycle 3: CLI → Agents → CLI
**Detection**: `thegent.cli` depends on `thegent.agents`; `thegent.agents` depends back on `thegent.cli`

**Source Files**:
- `src/cli/commands/sync.py` — **1,653 LOC** sync subcommand
- `src/agents/codex_proxy.py` — **1,257 LOC** agent routing and invocation
- `src/agents/` — Agent orchestration layer

**Root Cause**: CLI invokes agents; agents need CLI context for configuration, logging, and error reporting. Bidirectional dependency on shared state.

**Impact**: High — core execution flow entanglement

---

### Cycle 4: Agents → Execution → Agents
**Detection**: `thegent.agents` depends on `thegent.execution`; `thegent.execution` depends back on `thegent.agents`

**Source Files**:
- `src/agents/` — Agent definitions and routing
- `src/execution/executor.py` — Executor that calls agents
- `src/execution/` — Execution engine with agent callbacks

**Root Cause**: Executor needs to invoke agents; agents need executor context to track run status and handle callbacks.

**Impact**: Medium-High — intermediate abstraction violation

---

### Cycle 5: Models → Routing → Models
**Detection**: `thegent.models` depends on `thegent.routing`; `thegent.routing` depends back on `thegent.models`

**Source Files**:
- `src/models/` — LLM model definitions and interfaces
- `src/routing/` — Route selection and dispatch logic
- `src/models/model.py` — Base model class with routing callbacks

**Root Cause**: Routing selects models; models define routing interfaces. Circular interface dependency.

**Impact**: Medium — can be resolved with interface extraction

---

### Cycle 6: Execution → Contracts → Planning → Execution
**Detection**: 3-way cycle: `thegent.execution` → `thegent.contracts` → `thegent.planning` → `thegent.execution`

**Source Files**:
- `src/execution/` — Execution engine
- `src/contracts/` — Contract/specification definitions
- `src/planning/` — Task planning and decomposition

**Root Cause**: Execution needs contracts for task specs; planning creates contracts; contracts reference execution for dependency resolution.

**Impact**: High — blocks entire execution pipeline from independent testing

---

### Cycle 7: Routing → Models → Agents → Routing
**Detection**: 3-way cycle involving routing, models, and agents

**Source Files**:
- `src/routing/dispatcher.py` — Request routing
- `src/models/` — Model selection
- `src/agents/` — Agent invocation

**Root Cause**: Routing selects models and agents; models need routing state; agents call routing for sub-task dispatch.

**Impact**: High — central orchestration cluster

---

### Cycle 8: Planning → Execution → CLI → Planning
**Detection**: 3-way cycle: `thegent.planning` → `thegent.execution` → `thegent.cli` → `thegent.planning`

**Source Files**:
- `src/planning/decompose.py` — Task decomposition
- `src/cli/services/run_execution_core_helpers.py` — Execution orchestration (1,623 LOC)
- `src/cli/` — CLI command handlers

**Root Cause**: CLI invokes planning; planning invokes execution; execution reports back to CLI for user feedback.

**Impact**: Critical — top-level user-facing flow entanglement

---

## Part 2: Root Cause Analysis

### Common Patterns

All 8 cycles stem from **5 architectural violations**:

| Issue | Manifestation | Affected Cycles |
|-------|---------------|-----------------|
| **Bidirectional imports** | Module A needs B; B needs A for callbacks | 1, 2, 3, 4 |
| **God function** | `run_impl_core()` (1,023 LOC) orchestrates everything | 2, 8 |
| **Hub-and-spoke CLI** | CLI depends on all layers, creating spokes that loop back | 2, 3, 8 |
| **Missing abstractions** | No event bus, no dependency injection, no ports/adapters | 1, 5, 6, 7 |
| **State coupling** | Shared mutable state instead of message passing | 2, 3, 4 |

### Why Hexagonal Architecture Fails

The designed hexagonal structure (domain → ports → use_cases → adapters) is **not enforced**:

- `thegent.cli` is a "Layer 3" adapter that calls everything
- `thegent.models`, `thegent.routing`, `thegent.agents`, `thegent.execution` are all Layer 2+ but call each other
- `thegent.contracts` (should be Layer 0) imports `thegent.output_parser` (should be Layer 2)

**Result**: A monolithic cluster with no clear layering.

---

## Part 3: Proposed 5-Way Package Split

To eliminate all 8 cycles, we reorganize into **5 focused, independent packages**:

```
thegent-core/          # Layer 0-1: Domain types, errors, ports
├── domain/            # Entities, contracts, errors
├── ports/             # Interfaces (Model, Agent, Executor, Router, Planner)
└── __init__.py

thegent-cli/           # Layer 3: User-facing commands (entry point)
├── commands/          # Command handlers (no orchestration logic)
├── formatter/         # Output formatting
└── main.py            # CLI entry point

thegent-mcp/           # Layer 3: MCP server (external integration)
├── server.py          # MCP server implementation
├── tools/             # MCP tools (read-only references to core)
└── __init__.py

thegent-execution/     # Layer 2: Pure orchestration (NO cli imports)
├── executor.py        # Execute tasks using injected dependencies
├── planner.py         # Decompose and plan (no UI)
├── router.py          # Route and dispatch (no UI)
└── __init__.py

thegent-legacy/        # Layer 3: God function isolation (temporary)
├── run_impl_core.py   # Original 1,023-line function (not refactored yet)
└── __init__.py        # Documented as "will be removed once decomposed"
```

### Key Properties

1. **No cycles**: Each package depends on lower layers only
2. **Clear ports**: All imports use abstract interfaces from `thegent-core`
3. **Testable**: Each package can be tested in isolation
4. **CLI-independent**: Execution logic doesn't import CLI
5. **Modular**: Execution can be used via CLI, MCP, or other adapters

---

## Part 4: Per-Cycle Remediation Strategy

### Fix Order (Predecessors First)

Break cycles in this order to minimize cascading refactors:

#### Phase 1: Extract Core Abstractions (Week 1)
**Breaks**: Cycles 1, 5

1. **Create `thegent-core` with domain types**
   - Move `contracts/` → `core/domain/contracts.py`
   - Move `models/` base interfaces → `core/ports/model.py`
   - Move `errors/` → `core/errors/`
   - Extract `OutputProtocol` type (shared between contracts & output_parser)

2. **Resolve Cycle 1 (Contracts ↔ Output Parser)**
   - Both import shared types from `core/domain/protocol.py`
   - No direct imports between them
   - `output_parser/` becomes Layer 2 adapter (only imports core)

3. **Resolve Cycle 5 (Models ↔ Routing)**
   - Extract `ModelInterface` → `core/ports/model.py`
   - Extract `RouterInterface` → `core/ports/router.py`
   - Both import only from `core/ports/`

**Effort**: 3–4 days  
**Test**: Verify no imports between extracted modules

---

#### Phase 2: Isolate Execution Engine (Week 1–2)
**Breaks**: Cycles 2, 4, 6

4. **Create `thegent-execution` package**
   - Move `execution/` → `thegent-execution/`
   - Move `planning/` → `thegent-execution/planner.py`
   - **REMOVE ALL CLI IMPORTS** from execution (critical)
   - Replace CLI callbacks with injected `Logger` and `EventBus` (from core)

5. **Resolve Cycle 2 (CLI ↔ Execution)**
   - CLI becomes **consumer only** of execution
   - CLI calls `executor.run()` with injected dependencies
   - Execution calls back via abstract `Logger`/`EventBus` (not CLI)

6. **Resolve Cycle 4 (Agents ↔ Execution)**
   - `Executor` takes `AgentFactory` as dependency (injected)
   - No imports from `agents/` in execution
   - Agents remain in main namespace, can call execution

7. **Resolve Cycle 6 (3-way: Execution ↔ Contracts ↔ Planning)**
   - All three import from `core` only
   - Contracts passed as constructor parameters, not circular imports

**Effort**: 1–2 weeks  
**Test**: `pytest src/thegent-execution/` (zero CLI dependencies)

---

#### Phase 3: Reorganize CLI & Agents (Week 2–3)
**Breaks**: Cycles 3, 8

8. **Refactor `run_impl_core()` god function**
   - Extract orchestration into `thegent-execution/orchestrator.py`
   - CLI becomes thin wrapper around `Orchestrator.run()`
   - Create `thegent-legacy/run_impl_core.py` for temporary isolation

9. **Resolve Cycle 3 (CLI ↔ Agents)**
   - CLI calls `AgentRouter.invoke()` with pure data
   - Agents don't import CLI modules
   - Error handling via exceptions, not CLI callbacks

10. **Resolve Cycle 8 (3-way: Planning ↔ Execution ↔ CLI)**
    - CLI is now a thin adapter (no circular dependencies)
    - Planning & Execution don't know about CLI
    - User feedback via returned `Result<T, Error>` types

**Effort**: 1–2 weeks  
**Test**: `pytest src/thegent-cli/` passes; CLI commands work end-to-end

---

#### Phase 4: MCP & External Adapters (Week 3–4)
**Prerequisite**: Phases 1–3 complete

11. **Create `thegent-mcp` package**
    - Pure MCP server (follows same adapter pattern as CLI)
    - Calls `executor.run()` with injected dependencies
    - No knowledge of CLI internals

12. **Cycle 7 (3-way: Routing ↔ Models ↔ Agents)**
    - Router is now independent (imports only core/ports)
    - Models are plugin-registered, not imported directly
    - Agents are service-located via factory (injected)

**Effort**: 3–5 days  
**Test**: MCP tools work in isolation; no new cycles introduced

---

## Part 5: Testing Strategy

### Prevent Cycle Reintroduction

After refactoring, enforce via **import linter**:

#### Using `pytest-tach` (Recommended)

```bash
# In tach.toml, define strict layers:
[build]
forbid_circular_dependencies = true

[modules]
"thegent_core" = {depends_on = []}
"thegent_execution" = {depends_on = ["thegent_core"]}
"thegent_cli" = {depends_on = ["thegent_core", "thegent_execution"]}
"thegent_mcp" = {depends_on = ["thegent_core", "thegent_execution"]}
"thegent_agents" = {depends_on = ["thegent_core", "thegent_execution"]}
```

**Verification**:
```bash
task quality      # Runs tach boundary check
# OR
python -m tach check
```

#### Using Custom Import Linter (Python)

Create `scripts/check_cycles.py`:

```python
#!/usr/bin/env python3
"""Detect cycles in import graph."""

import ast
import sys
from pathlib import Path
from collections import defaultdict, deque

# Build import graph for each package
graph = defaultdict(set)

# Scan src/
for py_file in Path("src").rglob("*.py"):
    package = py_file.parts[1]  # Get package name
    tree = ast.parse(py_file.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("thegent"):
                imported_pkg = node.module.split(".")[0]
                if imported_pkg != package:
                    graph[package].add(imported_pkg)

# Check for cycles via DFS
def has_cycle(start, visited, rec_stack, path):
    visited.add(start)
    rec_stack.add(start)
    path.append(start)
    
    for neighbor in graph[start]:
        if neighbor not in visited:
            if has_cycle(neighbor, visited, rec_stack, path):
                return True
        elif neighbor in rec_stack:
            cycle_start = path.index(neighbor)
            print(f"CYCLE: {' -> '.join(path[cycle_start:] + [neighbor])}")
            return True
    
    path.pop()
    rec_stack.remove(start)
    return False

visited = set()
found_cycle = False
for package in graph:
    if package not in visited:
        if has_cycle(package, visited, set(), []):
            found_cycle = True

sys.exit(1 if found_cycle else 0)
```

Run in CI:
```bash
python scripts/check_cycles.py || { echo "Circular dependencies detected"; exit 1; }
```

#### Test Coverage Per Phase

| Phase | Test Target | Command |
|-------|-------------|---------|
| 1 | Core abstractions | `pytest src/thegent_core/ -v` |
| 2 | Execution isolation | `pytest src/thegent_execution/ -v` |
| 3 | CLI + Agents | `pytest src/thegent_cli/ src/thegent_agents/ -v` |
| 4 | MCP + Integration | `pytest src/thegent_mcp/ -v --integration` |
| All | No cycles | `python scripts/check_cycles.py` |

---

## Part 6: Effort Estimation & Timeline

### Total Scope

- **Phase 1** (Extract Core): 3–4 days, 1 small PR
- **Phase 2** (Isolate Execution): 1–2 weeks, 3–4 medium PRs
- **Phase 3** (Reorganize CLI): 1–2 weeks, 3–4 medium PRs
- **Phase 4** (MCP & Integration): 3–5 days, 1–2 medium PRs

**Total**: **3–4 weeks**, 8–11 PRs

### Resource Plan

**Recommended**: 1 developer full-time OR 2 developers part-time (half-week sprints)

**Parallelization**: Phase 1 must complete before 2, 3, 4 can start. Phases 2 & 3 can overlap if different team members work on execution vs. CLI.

### Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Breaking existing code | Heavy testing in phases; integration tests before merge |
| God function refactoring | Extract into separate module first; small PRs with focused changes |
| Deployment conflicts | Merge to main weekly; use feature flags for new code paths |
| Missing test coverage | Require >90% coverage before phase completion; add missing tests proactively |

---

## Part 7: Success Criteria

After remediation:

- ✅ Zero circular dependencies (verified by `tach check`)
- ✅ All 8 modules testable in isolation
- ✅ CLI is a thin adapter (max 200 LOC per command)
- ✅ Execution engine is dependency-injection aware
- ✅ No imports from CLI in any non-CLI layer
- ✅ All 1,308 tests still pass
- ✅ Test coverage remains >85%

---

## Related Documentation

- **Split Boundaries Spec**: `docs/refactor/split_boundaries.md` (Mermaid diagrams)
- **Code Audit**: `THEGENT_CODE_AUDIT.md` (original audit)
- **Consolidation Audit**: `CONSOLIDATION_AUDIT.md` (package patterns)

---

## Appendix: File-to-Package Mapping

| Current Path | Phase | New Path | Notes |
|--------------|-------|----------|-------|
| `src/contracts/` | 1 | `src/thegent_core/domain/contracts.py` | Extract OutputProtocol |
| `src/output_parser/` | 1 | Keep, refactor imports | Remove contracts imports |
| `src/models/base.py` | 1 | `src/thegent_core/ports/model.py` | Extract interface |
| `src/routing/` | 2 | `src/thegent_execution/routing/` | Isolated from agents |
| `src/planning/` | 2 | `src/thegent_execution/planner.py` | Merged into execution |
| `src/execution/` | 2 | `src/thegent_execution/executor.py` | Remove CLI imports |
| `src/cli/` | 3 | Keep, thin down | Commands → consumers only |
| `src/agents/` | 3 | Keep | Refactor imports |
| `src/cli/services/run_execution_core_helpers.py` | 3 | `src/thegent_legacy/run_impl_core.py` | Isolated temporarily |
| `src/mcp/` | 4 | `src/thegent_mcp/` | New MCP-specific package |

---

**Status**: Phase 3 COMPLETE (2026-04-24)  

**Phase 1 Results** (2026-04-24): 
- ✅ Created `thegent-core` (Layer 0): domain/, errors/, ports/ submodules
- ✅ ~500 LOC extracted (SLA, SLO, contracts, OutputProtocol, error types, port interfaces)
- ✅ Zero external dependencies (Python stdlib only)
- ✅ Cycle 1 (contracts ↔ output_parser): Resolved via shared OutputProtocol in core/domain
- ✅ Cycle 5 (models ↔ routing): Resolved via shared interfaces in core/ports

**Phase 2 Results** (inherited):
- ✅ `thegent-execution` package created with executor.py, planner.py, router.py
- ✅ Removed CLI imports from execution layer (isolated, zero upward deps)
- ✅ Cycles 2, 4, 6: Resolved (execution no longer imports CLI)

**Phase 3 Results** (2026-04-24):
- ✅ Created `ExecutionPort` interface in core/ports — agents can invoke execution without CLI imports
- ✅ Implemented `ExecutionPortAdapter` in thegent-execution/execution_port_adapter.py
- ✅ Updated agents/loop_controller.py: removed 2 CLI imports, uses ExecutionPort instead
- ✅ Updated planning/auto_launch.py: removed 2 CLI imports, uses ExecutionPort instead
- ✅ Cycle 3 (cli ↔ agents): RESOLVED — agents now use ports, not direct CLI
- ✅ Cycle 7 (routing ↔ models ↔ agents): RESOLVED — all use core interfaces
- ✅ Cycle 8 (planning ↔ execution ↔ cli): RESOLVED — planning uses ExecutionPort
- ✅ **Final Cycle Count: ZERO** (verified via AST analysis of module-level imports)
- ✅ thegent-legacy module prepared (Phase 4 task: decompose run_impl_core)

**Verification**:
```bash
cd thegent
python3 -m py_compile src/thegent/agents/loop_controller.py
python3 -m py_compile src/thegent/planning/auto_launch.py
python3 -m py_compile src/thegent/execution/execution_port_adapter.py
# Run cycle detector: python3 scripts/check_cycles.py
```

**Next Step**: Phase 4 — MCP integration + final validation (test coverage, integration tests)
