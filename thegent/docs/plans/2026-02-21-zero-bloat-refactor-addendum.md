# Zero-Bloat Refactor: Addendum & Corrections
> Extends: `2026-02-21-zero-bloat-refactor.md`
> Date: 2026-02-21 (Session 3 — 5-agent deep dive)
> Status: CORRECTIONS + EXTENSIONS to the base plan

---

## CORRECTIONS TO BASE PLAN

### CORRECTION 1: Hook Files Are NOT Missing

**Was:** Phase 0 Task 0.1 — "Create missing hook stubs: gardener-spawn-manager.sh, async-test-runner.sh, post-agent-run-vetter.sh"

**Reality (confirmed by agent):** All three exist and are active:
- `hooks/gardener-spawn-manager.sh` — 347 LOC, agent spawning with resource budgets
- `hooks/async-test-runner.sh` — 168 LOC, post-write test detection + async spawn
- `hooks/post-agent-run-vetter.sh` — 16 LOC, delegates to `thegent govern vet`

**Action:** Remove Task 0.1 from Phase 0. These hooks need no remediation. The prior analysis that called them "missing" was incorrect.

---

### CORRECTION 2: Do NOT Remove Zig — Expand It

**Was:** Phase 4 Task 4.2 — "Remove Zig POCs, replace with Python"

**Reality:** Zig is active production code across multiple components:
- `scripts/max_lines_gate.zig` — full production quality gate (per-commit, active)
- `crates/thegent-wasm-tools/src/metadata.zig` — WASM plugin exports
- `src/thegent/abi/zig_rust_poc/main.zig` — C ABI interop for ZMX (SY-008)
- `.github/workflows/ci.yml` has an active Zig CI job

**Action:** Replace Task 4.2 entirely. New task: **Expand Zig binary tools** (governance-gates.zig, session-cleanup.zig). See Phase 4 replacement below.

---

### CORRECTION 3: governance-gates.sh → Zig Binary, NOT Python

**Was:** Plan recommended converting governance-gates.sh to Python

**Reality:** Zig wins here for the same reasons max_lines_gate.zig wins:
- 50ms bash startup → 1ms Zig binary per hook invocation
- Compile-time pattern verification
- No subprocess spawning for JSON parsing
- max_lines_gate.zig (126 LOC) is the proven template

**Action:** governance-gates.sh → Zig binary is the P0 Zig conversion target.

---

### CORRECTION 4: Mojo Infrastructure Already Exists

**Was:** Plan treated Mojo as future/hypothetical

**Reality:** Active Mojo infrastructure:
- `src/thegent/infra/mojo_bridge.py` — subprocess-based bridge with JSON I/O
- `src/thegent/infra/mojo/math.mojo` — provider scoring kernel (POC)
- Pattern: subprocess JSON until Mojo C-ABI stabilizes

**Action:** Expand Mojo kernel set to Pareto routing, frecency decay, cost aggregation (Phase 4B — new). Do not call Mojo "missing" — it's a live POC.

---

## PHASE 0 REPLACEMENT (Critical Runtime Fixes)

Phase 0.1 (hooks) is removed. Remaining P0:

### Task 0.1-REVISED: Fix Hardcoded Path in specs.py

**File:** `src/thegent/specs.py:30`
**Issue:** Hardcoded path that breaks in CI/multi-user environments

Step 1: Write failing test
```python
# tests/unit/test_specs_path.py
def test_specs_path_not_hardcoded():
    """Specs must use dynamic path, not hardcoded user home."""
    import inspect, src.thegent.specs as m
    src_code = inspect.getsource(m)
    assert "/Users/" not in src_code, "Hardcoded user path found in specs.py"
```

Step 2: Fix the path (use `Path(__file__).parent` or env var)
Step 3: Run test → PASS
Step 4: Commit

---

## EXTENDED PHASE 1: Settings + Retry + Cache (Priority Order)

### Task 1.0: Confirm ConcurrencyController is the Rust Extraction Target

From execution.py analysis: 345-line ConcurrencyController class handles mutable shared state, hysteresis, and load-based slot allocation. This is the one execution class that benefits from Rust (thread-safety, float precision, contention).

**New file target:** `crates/thegent-concurrency/src/lib.rs` (PyO3 export)
**Interface:**
```
ConcurrencyController.acquire_slot(priority: &str) -> bool
ConcurrencyController.release_slot(priority: &str)
ConcurrencyController.get_load_metrics() -> LoadMetrics
ConcurrencyController.update_hysteresis(upper: f64, lower: f64, dwell: f64)
```
**Test:** Benchmark parallel slot acquisition; target 3-5x vs Python threading.Lock

---

### Task 1.A: ThegentSettings split (11 config groups)

**File:** `src/thegent/config.py` (1,360 LOC)

Split into 11 focused Pydantic models (all in `src/thegent/config/`):

| Module | LOC | Config Group |
|--------|-----|--------------|
| `model_defaults.py` | ~70 | Per-harness default model names |
| `timeout_config.py` | ~50 | default_timeout, max_idle_seconds, max_wall_time |
| `cache_config.py` | ~60 | cache_dir, session_dir, retention policies |
| `cost_governance.py` | ~90 | budget_*, cost_tracking_*, auto_router_* |
| `resilient_routing.py` | ~80 | routing_enabled, litellm_*, circuit_breaker_* |
| `concurrency_control.py` | ~75 | max_concurrency, critical_lane_slots, hysteresis_* |
| `backend_integration.py` | ~85 | cliproxy_*, cursor_api_*, mcp_*, opa_* |
| `security_sandbox.py` | ~65 | sandbox_*, input_guardrails_*, agent_allowlist |
| `platform_native.py` | ~70 | use_native_*, mac_keep_awake_*, tee_* |
| `distributed_services.py` | ~60 | redis_*, zmx_*, remote_nodes |
| `experimental.py` | ~75 | agileplus_*, shadow_workspaces_*, maif_enabled |

`config/__init__.py` re-exports `ThegentSettings` as a composed model using all 11 sub-configs.

**Tests:** ~100 tests across 11 test files in `tests/unit/test_config_*.py`

---

### Task 1.B: Retry consolidation → `src/thegent/resilience.py`

**41 manual retry loops → unified tenacity decorators**

Create `src/thegent/resilience.py` (~200 LOC) with:
- `transient_retry(max_attempts, min_wait, max_wait, exceptions)` — for HTTP/network
- `cas_retry(max_attempts, base_delay)` — for git CAS operations (with jitter)
- `user_input_retry(max_attempts)` — for MCP elicitation loops

Priority targets for migration:
1. `cliproxy_adapter.py:613` — while-True with attempts counter (24 LOC → 4 LOC)
2. `cliproxy_adapter.py:699` — recursive stream retry (30 LOC → 5 LOC)
3. `mesh/git.py:121` — CAS ref update retry (23 LOC → 4 LOC)
4. `mcp/tools/patterns.py:252` — choice elicitation retry (32 LOC → 4 LOC)
5. `infra/fast_http_client.py` — `_get_retry_decorator()` factory → delete, use resilience.py
6. `agents/resilience.py` — `with_retry()` decorator → delete, use resilience.py

Total savings: ~320 LOC across 41 loops → ~80 LOC in resilience.py.

**Tests:** `tests/unit/test_resilience_*.py` covering transient, CAS, user-input patterns

---

### Task 1.C: Cache consolidation → CacheStrategy protocol

**Files:** `cache/multi_level.py` (213), `cache/frecency.py` (393), `cache/pre_warmer.py` (460)
**60% overlap** in locking, persistence, stats, thread safety.

Create `cache/strategy.py` (~150 LOC) with abstract `CacheStrategy`:
```
get(key) → Any | None
set(key, value, ttl?) → None
delete(key) → None
clear() → None
stats() → dict
```

Refactor the 3 existing classes to inherit from `CacheStrategy`.
Add `CompositeCache` (~80 LOC) for L1→L2→null fallback chains.

**Remove:** `contextlib.suppress(Exception)` anti-patterns throughout — fail loudly.

**Tests:** `tests/unit/test_cache_*.py` (73 tests total)

---

## EXTENDED PHASE 2: Polyglot Boundary Completion

### Task 2.A: Complete thegent-parser PyO3 bindings

**Current state:** Rust implementations exist in `crates/thegent-parser/src/lib.rs` but Python may fall through to pure-Python:
- `parse_jsonl_file()` (Rust line 121)
- `parse_checkpoint_by_id()` (Rust line 142)
- `parse_dlq_item()` (Rust line 164)
- `strip_think_blocks()` (Rust line 59)
- `extract_xml_tags()` (Rust line 22)

Step 1: Run parity tests — `pytest tests/routing/test_wl131_parser_parity.py -v`
Step 2: If binding gaps found, fix PyO3 exports in lib.rs
Step 3: Enable Rust path as default (not fallback) in `execution_jsonl_parsers.py`
Step 4: Benchmark: target 7-10x speedup for JSONL parsing loops

---

### Task 2.B: New Rust extension — Cost Calculator

**File:** `crates/thegent-router/src/cost_calculator.rs` (NEW)

Hot path: `models/cost_values.py` — `get_model_provider_costs()` called thousands of times per session.

New PyO3 functions:
```
lookup_model_provider_cost(model, provider, fallback_cache) → (f64, f64)
estimate_request_cost(input_tokens, output_tokens, model, provider) → f64
```

**Tests:** Parity tests comparing Rust vs Python output; benchmark tests targeting 3-5x speedup.

---

### Task 2.C: New Rust extension — Execution Record Hashing

**File:** `crates/thegent-crypto/src/record.rs` (NEW)

Hot path: `execution_hash_helpers.py:8` — `calculate_stable_record_hash()` called per execution record.

New PyO3 function:
```
hash_execution_record(json_str: &str, exclude_keys: &[&str]) → String
```

Wire to Python: `execution_hash_helpers.py` imports `thegent_crypto.hash_execution_record`

**Tests:** SHA256 parity tests; benchmark: target 5-8x speedup.

---

### Task 2.D: Mojo kernel expansion

**Build on existing:** `mojo_bridge.py` + `mojo/math.mojo`

Add 3 new Mojo kernels:

1. `mojo/pareto.mojo` — Pareto front computation for routing (5-15x speedup)
   - Vectorized O(n²) → O(n) with SIMD comparison of cost/quality pairs
   - Called from `research/pareto_routing.py:20`

2. `mojo/frecency.mojo` — Batch frecency decay kernel (3-10x speedup)
   - Vectorized `score = count × e^(-λ × age)` for 100-1000 entries
   - Called from `cache/frecency.py:63`

3. `mojo/cost_agg.mojo` — Batch token-to-cost calculation (2-5x speedup)
   - Vectorized `(tokens / 1_000_000) × price_per_m` for 100-500 completions
   - Called from `cost/aggregator.py:44`

**Timing:** Implement after Mojo C-ABI stabilizes. For now, keep subprocess bridge. Batch calls to amortize startup cost.

---

## EXTENDED PHASE 4: Zig Binary Expansion

This replaces the deleted "remove Zig POCs" task.

### Task 4.A: governance-gates.zig (P0 — highest impact)

**Source:** `hooks/governance-gates.sh` (2,519 LOC)
**Target:** `scripts/governance-gates.zig` (est. ~400 LOC Zig)

Template: `scripts/max_lines_gate.zig` (126 LOC proven pattern)

Interface (matches existing hook interface):
```
stdin: JSON payload from hook-dispatcher
stdout: JSON gate results
exit 0: pass or advisory
exit 2: fail-closed gate failure
```

**Migration strategy (3 phases):**
1. Implement 3 gates first: `regression_spiral_guard`, `instruction_architecture`, `complexity_ratchet`
2. Parallel test (shell vs Zig outputs match)
3. Add remaining gates 5 at a time, parallel test each batch

**Estimated speedup:** 50ms bash → 1ms Zig per invocation (50x faster startup)

---

### Task 4.B: session-cleanup.zig (P1)

**Source:** `hooks/session-cleanup.sh` (123 LOC)
**Target:** `scripts/session-cleanup.zig` (est. ~80 LOC Zig)

What it does: prune stale cache dirs, disk usage abort guard, reset quality gate counters.

Simple file I/O and mtime checks — ideal Zig standalone binary.

---

### Task 4.C: Extend max_lines_gate.zig with complexity checks

**File:** `scripts/max_lines_gate.zig` (126 LOC, already production)

Add to existing binary:
- Cyclomatic complexity scan (parse functions, count branches)
- Function length enforcement (already done) → add class length check
- File-level LOC cap (already done)

**This extends the existing binary, not a new file.**

---

## EXTENDED PHASE 5: Execution Layer Decomposition

### Task 5.A: execution.py → execution/ package

**File:** `src/thegent/execution.py` (2,577 LOC, 25 classes)

Split into package `src/thegent/execution/`:

| Module | LOC | Contents |
|--------|-----|----------|
| `__init__.py` | ~30 | Public API re-exports |
| `state.py` | ~350 | RunState, RunMeta, RunRegistry, ChatHistory, CheckpointRegistry |
| `concurrency.py` | ~600 | ConcurrencyController, LoadClassifier, LaneController, CircuitBreakerRegistry |
| `quality.py` | ~550 | KPIManager, ProviderScorer, Auditor, EvidenceLinter, FreshnessValidator |
| `escalation.py` | ~400 | OverrideRegistry, EscalationQueue, IdempotencyManager, HandoffManager |
| `operations.py` | ~280 | ReplayManager, DeferralQueue, DLQManager, CalibrationRegistry |
| `parsers.py` | ~180 | All _parse_* JSONL functions (to be replaced by thegent-parser Rust extension) |

**Language note:** Keep Python for all except `concurrency.py` which may become a Rust PyO3 binding (see Task 1.0).

**Tests:** 105 new tests across `tests/unit/test_execution_*.py` and `tests/integration/test_execution_e2e.py`

---

### Task 5.B: mcp/server.py → layered builder

**File:** `src/thegent/mcp/server.py` (228 LOC facade hiding 40+ imported modules)

Refactor to clear layers:
```
mcp/server.py (50 LOC) → entry point only: mcp = build_app(); app = mcp
mcp/__init__.py (150 LOC) → build_app() factory, wires all submodules
mcp/auth.py (80 LOC) → auth registration
mcp/lifecycle.py (60 LOC) → lifespan hooks
mcp/resources.py (120 LOC) → resource routes
mcp/tools/batch1-4.py (4 × 150 LOC) → tool registrations
```

**Tests:** `tests/unit/test_mcp_builder.py`, `tests/integration/test_mcp_e2e.py`

---

### Task 5.C: cli/impl.py → 4 focused modules

**File:** `src/thegent/cli/commands/impl.py` (844 LOC, 37 functions)

Split:
```
impl_validation.py (180 LOC) → argument validation, image paths, health policy
impl_routing.py (220 LOC) → Pareto routing, model resolution, load classification
impl_response.py (140 LOC) → response building, health snapshot, audio metadata
impl_execution.py (300 LOC) → run/bg/resume/loop/work-stream entry points
impl.py (50 LOC) → public facade, re-exports all *_impl functions
```

---

## TEST IMPROVEMENT PHASE (New — Previously Missing)

### Task T.0: Fix test marker saturation (BLOCKING)

**Problem:** 88% of 12,625 tests (11,120 functions) lack `@pytest.mark.unit/integration/e2e` markers
**Impact:** CI fast-lane cannot filter tests; all 12,625 run every commit

**Action:** Scripted mass-tagging pass using AST analysis of each test function:
- Tests <100ms with no I/O → `@pytest.mark.unit`
- Tests >100ms OR call real services → `@pytest.mark.integration`
- Full CLI/API tests → `@pytest.mark.e2e`

**Effort:** ~40 subagent calls (grep-analyze-write batches of 50 files each)

---

### Task T.1: Fix tests/e2e/ collection (BLOCKING)

**Problem:** `tests/e2e/` has 67 files with 0 collected test functions (pytest.TestCase classes not collected)

**Action:** Convert pytest.TestCase subclasses to plain pytest functions for all 67 e2e files. Recovers ~500+ e2e tests.

---

### Task T.2: Write tests for 10 P0 untested modules

**Critical untested modules (by LOC):**

| Module | LOC | Test File to Create |
|--------|-----|---------------------|
| `mesh/git_parallelism.py` | 19,575 | `tests/unit/test_git_parallelism.py` |
| `mesh/git.py` | 10,395 | `tests/unit/test_mesh_git.py` |
| `research/cost_sensitivity_experiment.py` | 7,504 | `tests/unit/test_cost_sensitivity_experiment.py` |
| `mesh/task_queue.py` | 7,415 | `tests/unit/test_task_queue.py` |
| `mesh/merge.py` | 5,050 | `tests/unit/test_mesh_merge.py` |
| `config_provider.py` | 4,354 | `tests/unit/test_config_provider.py` |
| `mesh/mesh.py` | 4,309 | `tests/unit/test_mesh.py` |
| `research/cost_routing.py` | 3,851 | `tests/unit/test_cost_routing.py` |
| `mesh/injection.py` | 3,382 | `tests/unit/test_mesh_injection.py` |
| `research/cost_sensitivity.py` | 3,226 | `tests/unit/test_cost_sensitivity.py` |

**Priority:** mesh/git_parallelism.py is P0-CRITICAL (19K LOC with zero tests).

---

### Task T.3: Add property-based tests with hypothesis

**Current:** 0 property-based tests

**Add hypothesis tests to:**
- `tests/routing/` — 50 files, 455 tests — add parametric edge cases for routing logic
- `tests/cli/` — CLI arg combinations
- `tests/mcp/` — MCP message handling edge cases

Target: 50+ property-based tests

---

### Task T.4: Add FR traceability markers

**Current:** 5% of tests have `@pytest.mark.requirement("FR-XXX")`
**Target:** 25%+ (3,000+ tests)

**Action:** For each test module, add FR markers matching the module's functional requirements. Start with most-tested subsystems (routing: WL-103, FR-ROUTE-014).

---

### Task T.5: Add Rust integration tests for sparse crates

**Current:** Only 4 Rust crates have `tests/` directories

**Add integration tests (at minimum 1 per crate) to:**
- `crates/thegent-maif/` (3 inline tests, critical FFI boundary — expand to 15+)
- `crates/thegent-fs/` (3 inline tests)
- `crates/thegent-zmx-interop/` (4 tests only)
- `crates/thegent-zmx/` (29 inline, no integration tests)
- `crates/thegent-shm/` (26 inline, no integration tests)

---

## REVISED PHASE SEQUENCE (DAG)

```
Phase 0: [0.1-revised] hardcoded path fix
    ↓
Phase 1A: [ThegentSettings split] → independent
Phase 1B: [Retry consolidation] → independent
Phase 1C: [Cache consolidation] → independent
    ↓
Phase 2A: [thegent-parser PyO3 completion] → after 1B (uses resilience)
Phase 2B: [Cost calculator Rust] → after 1A (needs cost config group)
Phase 2C: [Record hashing Rust] → independent
Phase 2D: [Mojo kernels] → after 1C (Pareto uses frecency context)
    ↓
Phase T (parallel): All test tasks → can run parallel with Phase 1/2
    ↓
Phase 3: [Logging migration structlog] → after 2A (parsers resolved)
    ↓
Phase 4: [Zig expansions] → after Phase 3
  4A: governance-gates.zig
  4B: session-cleanup.zig
  4C: max_lines_gate.zig complexity extension
    ↓
Phase 5: [Execution decomposition] → after Phase 2
  5A: execution.py → package
  5B: mcp/server.py → builder
  5C: cli/impl.py → 4 modules
    ↓
Phase 6: [trace refactors] (unchanged from base plan)
Phase 7: [agent consolidation, template sync] (unchanged)
```

---

## REVISED SUMMARY TABLE

| Phase | Task | LOC Before | LOC After | Savings | Language | Priority |
|-------|------|-----------|-----------|---------|----------|----------|
| 1A | Settings split | 1,360 | 1,200 | 160 | Python | HIGH |
| 1B | Retry consolidation | ~400 scattered | ~80 | 320 | Python+tenacity | HIGH |
| 1C | Cache protocol | 1,100 | 900 | 200 | Python | MEDIUM |
| 2A | thegent-parser complete | Python fallbacks | Rust default | 7-10x faster | Rust→Python | HIGH |
| 2B | Cost calc Rust | Python 122 LOC | Rust 40 LOC | 3-5x faster | NEW Rust | MEDIUM |
| 2C | Record hashing Rust | Python 12 LOC | Rust 20 LOC | 5-8x faster | NEW Rust | MEDIUM |
| 2D | Mojo kernels ×3 | Python loops | Mojo SIMD | 3-15x faster | NEW Mojo | LOW-MED |
| 4A | governance-gates.zig | Bash 2,519 LOC | Zig ~400 LOC | 50x startup | Zig binary | HIGH |
| 4B | session-cleanup.zig | Bash 123 LOC | Zig ~80 LOC | 50x startup | Zig binary | MEDIUM |
| 5A | execution.py split | 2,577 LOC 1 file | 7 modules | maintainability | Python+Rust | HIGH |
| 5B | mcp/server builder | 228 LOC facade | 6 layered | discoverability | Python | LOW |
| 5C | cli/impl split | 844 LOC | 5 modules | maintainability | Python | MEDIUM |
| T.0 | Test markers | 0% marked | 100% | CI fast-lane | — | BLOCKING |
| T.1 | Fix e2e collection | 0 functions | ~500 | recover 500 tests | — | BLOCKING |
| T.2 | P0 untested modules | 0 tests | ~300 | coverage gap | — | HIGH |
| T.3 | Hypothesis tests | 0 property | 50+ | edge cases | — | MEDIUM |
| **TOTAL** | | **~10K LOC** | **~7.5K LOC** | **~25% reduction** | | |
