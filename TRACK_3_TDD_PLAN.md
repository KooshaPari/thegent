# Track 3: Zig Hook System + Quality Audit Fixes (TDD Implementation Plan)

## Overview

Track 3 replaces the hook execution infrastructure with a performant Zig-based system while addressing critical quality gaps identified in the orchestration layer. This plan follows strict Test-Driven Development (TDD) discipline: failing tests are written first, then implementation code follows. All phases use phased work breakdown structure (WBS) with explicit DAG dependencies.

**Primary Objectives:**
- **Part A**: Replace shell/C++ hook infrastructure with WASM-compilable Zig binaries
- **Part B**: Fix race conditions, raise test coverage to >80%, split monolithic files, resolve tach.toml boundaries
- **Coverage Targets**: routing=100%, cli≥80%, auth≥75%
- **Test-First Discipline**: Failing test MUST exist before implementation code

---

## Architecture Context

### Existing Infrastructure
- **hooks/governance-gates.sh**: 2,519 lines of shell validation logic
- **hooks/hook-dispatcher-bin**: 461KB C++ binary for hook invocation
- **Contract validation**: ~3,000 Python LOC scattered across `src/thegent/contracts/`
- **Hook events**: PreToolUse, PostToolUse, Stop, SessionStart, SessionEnd, UserPromptSubmit, PreCompact, Notification

### Target Architecture
- **Zig hooks**: WASM-compilable, deterministic, zero runtime overhead
- **Hook dispatcher**: Single-threaded, lock-free event queue
- **Contract engine**: Type-safe validation in Zig with Python shim interface
- **Integration**: `.mise.toml` Zig version pinning; shell-compatible output format

---

## Phase 1: Discovery (Agent-Driven, ~2-4 min wall clock)

### Tasks

| Phase | Task ID | Description | Depends On | Est. Effort |
|-------|---------|-------------|-----------|------------|
| Discovery | T3.D.1 | Analyze existing governance-gates.sh for business logic extraction | — | 1-2 calls |
| Discovery | T3.D.2 | Audit hook-config.yaml structure and event routing requirements | T3.D.1 | 2-3 calls |
| Discovery | T3.D.3 | Identify race conditions in src/thegent/orchestration/resource.py | T3.D.2 | 2-3 calls |
| Discovery | T3.D.4 | Identify race conditions in src/thegent/integrations/auth/*.py | T3.D.3 | 2-3 calls |
| Discovery | T3.D.5 | Profile hook-dispatcher-bin and measure latency/throughput SLOs | T3.D.4 | 2-3 calls |
| Discovery | T3.D.6 | Audit current test coverage: routing, cli, auth modules | T3.D.5 | 3-4 calls |
| Discovery | T3.D.7 | Inventory monolithic files >500 LOC in src/thegent/ | T3.D.6 | 1-2 calls |
| Discovery | T3.D.8 | Document tach.toml boundary violations blocking cutover | T3.D.7 | 2-3 calls |

**DAG Dependency Chain**: T3.D.1 → T3.D.2 → T3.D.3 → T3.D.4 → T3.D.5 → T3.D.6 → T3.D.7 → T3.D.8

**Execution Strategy**: Explore agent scans shell scripts, Python modules, and test directories. All discovery outputs feed into Design phase refinement.

---

## Phase 2: Design (Agent-Driven, ~3-6 min wall clock)

### Tasks

| Phase | Task ID | Description | Depends On | Est. Effort |
|-------|---------|-------------|-----------|------------|
| Design | T3.D2.1 | Design Zig hook system API (event types, contract language) | T3.D.8 | 2-3 calls |
| Design | T3.D2.2 | Design Zig dispatcher lifecycle (startup, teardown, thread safety) | T3.D2.1 | 2-3 calls |
| Design | T3.D2.3 | Design contract validation engine in Zig (language, primitives) | T3.D2.2 | 2-3 calls |
| Design | T3.D2.4 | Design race condition fix strategy for resource.py (locks, channels) | T3.D2.3 | 2-3 calls |
| Design | T3.D2.5 | Design race condition fix strategy for auth/*.py (async-safe patterns) | T3.D2.4 | 2-3 calls |
| Design | T3.D2.6 | Design test harness for routing property-based tests (Hypothesis) | T3.D2.5 | 2-3 calls |
| Design | T3.D2.7 | Design file splitting strategy for monolithic modules | T3.D2.6 | 1-2 calls |
| Design | T3.D2.8 | Design tach.toml boundary resolution strategy | T3.D2.7 | 1-2 calls |

**DAG Dependency Chain**: T3.D2.1 → T3.D2.2 → T3.D2.3 → T3.D2.4 → T3.D2.5 → T3.D2.6 → T3.D2.7 → T3.D2.8

**Execution Strategy**: Architect agent produces ADR-style design docs with pseudocode, API contracts, and validation rules. All designs require TDD failing tests (written in parallel or immediately after).

---

## Phase 3: Build (Agent-Driven, ~8-15 min wall clock, parallelizable)

### 3.1 Part A: Zig Hook System

#### Subphase 3A.1: Foundation (TDD-First)

| Phase | Task ID | Description | Depends On | Est. Effort |
|-------|---------|-------------|-----------|------------|
| Build | T3.B.A.1.1 | Write failing test for Zig event type validation | T3.D2.3 | 1 call |
| Build | T3.B.A.1.2 | Implement Zig event types and serialization | T3.B.A.1.1 | 2-3 calls |
| Build | T3.B.A.1.3 | Write failing test for contract DSL parser | T3.B.A.1.2 | 1 call |
| Build | T3.B.A.1.4 | Implement Zig contract DSL parser | T3.B.A.1.3 | 3-4 calls |
| Build | T3.B.A.1.5 | Write failing test for WASM compilation target | T3.B.A.1.4 | 1 call |
| Build | T3.B.A.1.6 | Configure .mise.toml Zig pinning (stable version) | T3.B.A.1.5 | 1 call |

#### Subphase 3A.2: Dispatcher (TDD-First)

| Phase | Task ID | Description | Depends On | Est. Effort |
|-------|---------|-------------|-----------|------------|
| Build | T3.B.A.2.1 | Write failing test for lock-free event queue | T3.B.A.1.6 | 2 calls |
| Build | T3.B.A.2.2 | Implement Zig dispatcher with lock-free queue | T3.B.A.2.1 | 3-4 calls |
| Build | T3.B.A.2.3 | Write failing test for hook lifecycle (startup/teardown) | T3.B.A.2.2 | 1 call |
| Build | T3.B.A.2.4 | Implement hook lifecycle handlers | T3.B.A.2.3 | 2-3 calls |
| Build | T3.B.A.2.5 | Write failing test for event ordering guarantees | T3.B.A.2.4 | 1 call |
| Build | T3.B.A.2.6 | Implement deterministic event ordering in dispatcher | T3.B.A.2.5 | 2-3 calls |

#### Subphase 3A.3: Contract Validation (TDD-First)

| Phase | Task ID | Description | Depends On | Est. Effort |
|-------|---------|-------------|-----------|------------|
| Build | T3.B.A.3.1 | Write failing test for contract evaluation (all rule types) | T3.B.A.2.6 | 2 calls |
| Build | T3.B.A.3.2 | Implement contract validation engine in Zig | T3.B.A.3.1 | 4-5 calls |
| Build | T3.B.A.3.3 | Write failing test for Python-to-Zig contract bridge | T3.B.A.3.2 | 1 call |
| Build | T3.B.A.3.4 | Implement Python FFI shim for contract engine | T3.B.A.3.3 | 2-3 calls |
| Build | T3.B.A.3.5 | Write failing test for shell output compatibility | T3.B.A.3.4 | 1 call |
| Build | T3.B.A.3.6 | Implement shell-compatible output formatter | T3.B.A.3.5 | 1-2 calls |

#### Subphase 3A.4: Integration & WASM (TDD-First)

| Phase | Task ID | Description | Depends On | Est. Effort |
|-------|---------|-------------|-----------|------------|
| Build | T3.B.A.4.1 | Write failing test for WASM compilation | T3.B.A.3.6 | 1 call |
| Build | T3.B.A.4.2 | Build WASM target for contract validation | T3.B.A.4.1 | 2-3 calls |
| Build | T3.B.A.4.3 | Write failing test for hook-config.yaml integration | T3.B.A.4.2 | 1 call |
| Build | T3.B.A.4.4 | Integrate Zig dispatcher with hook-config.yaml routing | T3.B.A.4.3 | 2-3 calls |
| Build | T3.B.A.4.5 | Write integration test for end-to-end hook invocation | T3.B.A.4.4 | 1 call |
| Build | T3.B.A.4.6 | Implement end-to-end hook invocation path | T3.B.A.4.5 | 2-3 calls |

**Part A DAG Note**: Subphases proceed in series (3A.1 → 3A.2 → 3A.3 → 3A.4). Within each subphase, TDD pattern is: failing test → implementation.

### 3.2 Part B: Critical Quality Fixes (Parallel to Part A from T3.B.A.2.1 onwards)

#### Subphase 3B.1: Race Condition Fixes

| Phase | Task ID | Description | Depends On | Est. Effort |
|-------|---------|-------------|-----------|------------|
| Build | T3.B.B.1.1 | Write failing test for resource.py race condition (threading scenario) | T3.D2.4 | 2 calls |
| Build | T3.B.B.1.2 | Fix race condition in src/thegent/orchestration/resource.py | T3.B.B.1.1 | 2-3 calls |
| Build | T3.B.B.1.3 | Verify fix: run test suite + ThreadSanitizer (tsan) | T3.B.B.1.2 | 2 calls |
| Build | T3.B.B.1.4 | Write failing test for auth/*.py race condition (async scenario) | T3.D2.5 | 2 calls |
| Build | T3.B.B.1.5 | Fix race condition in src/thegent/integrations/auth/*.py | T3.B.B.1.4 | 2-3 calls |
| Build | T3.B.B.1.6 | Verify fix: run test suite + asyncio deadlock detection | T3.B.B.1.5 | 2 calls |

#### Subphase 3B.2: Test Coverage Improvements

| Phase | Task ID | Description | Depends On | Est. Effort |
|-------|---------|-------------|-----------|------------|
| Build | T3.B.B.2.1 | Write property-based tests for routing (Hypothesis) | T3.D2.6 | 3-4 calls |
| Build | T3.B.B.2.2 | Run coverage: `pytest tests/routing/ --cov=src/thegent/routing` | T3.B.B.2.1 | 1 call |
| Build | T3.B.B.2.3 | Raise routing coverage to 100% (missing branches) | T3.B.B.2.2 | 2-3 calls |
| Build | T3.B.B.2.4 | Write property-based tests for CLI implementation | T3.B.B.2.1 | 2-3 calls |
| Build | T3.B.B.2.5 | Run coverage: `pytest tests/ -k cli --cov=src/thegent/cli` | T3.B.B.2.4 | 1 call |
| Build | T3.B.B.2.6 | Raise CLI coverage to ≥80% (missing branches) | T3.B.B.2.5 | 2-3 calls |
| Build | T3.B.B.2.7 | Run coverage: `pytest tests/integrations/auth --cov=src/thegent/integrations/auth` | T3.B.B.2.6 | 1 call |
| Build | T3.B.B.2.8 | Raise auth coverage to ≥75% (missing branches) | T3.B.B.2.7 | 2-3 calls |

#### Subphase 3B.3: File Splitting (Monolithic Module Refactor)

| Phase | Task ID | Description | Depends On | Est. Effort |
|-------|---------|-------------|-----------|------------|
| Build | T3.B.B.3.1 | Write failing test for split module A (new submodule) | T3.D2.7 | 1 call |
| Build | T3.B.B.3.2 | Refactor monolithic file A into submodules (parity tests) | T3.B.B.3.1 | 3-4 calls |
| Build | T3.B.B.3.3 | Verify: `pytest tests/ --cov` (no coverage drop) | T3.B.B.3.2 | 1 call |
| Build | T3.B.B.3.4 | Write failing test for split module B (new submodule) | T3.D2.7 | 1 call |
| Build | T3.B.B.3.5 | Refactor monolithic file B into submodules (parity tests) | T3.B.B.3.4 | 3-4 calls |
| Build | T3.B.B.3.6 | Verify: `pytest tests/ --cov` (no coverage drop) | T3.B.B.3.5 | 1 call |
| Build | T3.B.B.3.7 | Write failing test for split module C (new submodule) | T3.D2.7 | 1 call |
| Build | T3.B.B.3.8 | Refactor monolithic file C into submodules (parity tests) | T3.B.B.3.7 | 3-4 calls |
| Build | T3.B.B.3.9 | Verify: `pytest tests/ --cov` (no coverage drop) | T3.B.B.3.8 | 1 call |

#### Subphase 3B.4: tach.toml Boundary Resolution

| Phase | Task ID | Description | Depends On | Est. Effort |
|-------|---------|-------------|-----------|------------|
| Build | T3.B.B.4.1 | Audit tach.toml violations: `tach check --verbose` | T3.D2.8 | 1 call |
| Build | T3.B.B.4.2 | Implement boundary fix #1 (move/reorg modules) | T3.B.B.4.1 | 2-3 calls |
| Build | T3.B.B.4.3 | Run `tach check --verbose` (no new violations) | T3.B.B.4.2 | 1 call |
| Build | T3.B.B.4.4 | Implement boundary fix #2 (move/reorg modules) | T3.B.B.4.1 | 2-3 calls |
| Build | T3.B.B.4.5 | Run `tach check --verbose` (no new violations) | T3.B.B.4.4 | 1 call |
| Build | T3.B.B.4.6 | Implement boundary fix #3 (move/reorg modules) | T3.B.B.4.1 | 2-3 calls |
| Build | T3.B.B.4.7 | Run `tach check --verbose` → PASS (all boundaries clean) | T3.B.B.4.6 | 1 call |

**Part B DAG Notes**:
- Subphase 3B.1 (race conditions) can begin when T3.D2.4 and T3.D2.5 complete (parallel to Part A 3A.1)
- Subphase 3B.2 (test coverage) can begin when T3.D2.6 complete (parallel to Part A 3A.2)
- Subphase 3B.3 (file splitting) begins after 3B.2 completes (parity requires stable tests)
- Subphase 3B.4 (tach.toml) begins after 3B.3 completes (boundary violations emerge after refactoring)

---

## Phase 4: Test & Validate (Agent-Driven, ~4-8 min wall clock)

### 4.1 Unit Test Coverage Validation

| Phase | Task ID | Description | Depends On | Est. Effort |
|-------|---------|-------------|-----------|------------|
| Validate | T3.V.1 | Run full test suite: `pytest tests/ --cov=src/thegent` | T3.B.B.4.7 | 2 calls |
| Validate | T3.V.2 | Verify coverage report: routing ≥100%, cli ≥80%, auth ≥75% | T3.V.1 | 1 call |
| Validate | T3.V.3 | Run mutation testing (mutmut): `mutmut run --tests-dir tests/` | T3.V.2 | 3-4 calls |
| Validate | T3.V.4 | Verify mutation score ≥85% (critical paths) | T3.V.3 | 1 call |

### 4.2 Race Condition Validation

| Phase | Task ID | Description | Depends On | Est. Effort |
|-------|---------|-------------|-----------|------------|
| Validate | T3.V.5 | Run ThreadSanitizer: `TSAN_OPTIONS=... pytest tests/orchestration/` | T3.V.1 | 2 calls |
| Validate | T3.V.6 | Run asyncio deadlock detector: `pytest tests/integrations/auth/ --asyncio-mode=auto` | T3.V.5 | 2 calls |
| Validate | T3.V.7 | Stress test: 100x concurrent hook invocation (no crashes/deadlocks) | T3.V.6 | 2-3 calls |

### 4.3 Zig Hook System Validation

| Phase | Task ID | Description | Depends On | Est. Effort |
|-------|---------|-------------|-----------|------------|
| Validate | T3.V.8 | Verify Zig compilation: `zig build -Doptimize=ReleaseSmall` | T3.B.A.4.6 | 1 call |
| Validate | T3.V.9 | Verify WASM target: `zig build -Dtarget=wasm32-freestanding` | T3.V.8 | 1 call |
| Validate | T3.V.10 | Shell compatibility test: compare governance-gates.sh vs Zig output on 1000 inputs | T3.V.9 | 2-3 calls |
| Validate | T3.V.11 | Determinism test: run Zig dispatcher 10x on same input, verify identical output | T3.V.10 | 1 call |
| Validate | T3.V.12 | Performance benchmark: Zig dispatcher vs C++ dispatcher (latency, throughput) | T3.V.11 | 2-3 calls |

### 4.4 Architecture Validation

| Phase | Task ID | Description | Depends On | Est. Effort |
|-------|---------|-------------|-----------|------------|
| Validate | T3.V.13 | Run tach boundary check: `tach check` (all boundaries pass) | T3.B.B.4.7 | 1 call |
| Validate | T3.V.14 | Run linting: `ruff check src/thegent` (all pass, no new suppressions) | T3.V.13 | 1 call |
| Validate | T3.V.15 | Run type checker: `pyright src/thegent` (all pass, no errors) | T3.V.14 | 1 call |

---

## Phase 5: Deploy & Handoff (Agent-Driven, ~2-3 min wall clock)

| Phase | Task ID | Description | Depends On | Est. Effort |
|-------|---------|-------------|-----------|------------|
| Deploy | T3.D.1 | Update .mise.toml with Zig version pin and validation | T3.V.15 | 1 call |
| Deploy | T3.D.2 | Write migration guide: shell → Zig hook system | T3.D.1 | 2 calls |
| Deploy | T3.D.3 | Tag release: `v2.0.0-track3-zig-hooks` (git + changelog) | T3.D.2 | 1 call |
| Deploy | T3.D.4 | Publish CHANGELOG entry (Part A + Part B summary) | T3.D.3 | 1 call |
| Deploy | T3.D.5 | Write runbook: "How to disable Zig hooks and rollback to shell" | T3.D.4 | 1 call |
| Deploy | T3.D.6 | Archive governance-gates.sh to docs/archive/ (do not delete) | T3.D.5 | 1 call |

---

## Success Criteria & Acceptance

### Unit 1: Zig Hook System (Part A)
- ✅ `zig build -Doptimize=ReleaseSmall` succeeds
- ✅ `zig build -Dtarget=wasm32-freestanding` succeeds  
- ✅ All hook events routed through Zig dispatcher
- ✅ Contract validation engine supports all existing rule types
- ✅ Shell output format 100% compatible with governance-gates.sh on 1000+ inputs
- ✅ Test coverage: 100% (Zig + Python bridge)
- ✅ Determinism: 10 identical runs produce identical output
- ✅ Performance: Dispatcher latency ≤ original C++ binary

### Unit 2: Race Condition Fixes (Part B.1)
- ✅ No ThreadSanitizer errors in orchestration tests
- ✅ No asyncio deadlock errors in auth tests
- ✅ Stress test: 100x concurrent invocations, no crashes

### Unit 3: Test Coverage Improvements (Part B.2)
- ✅ routing coverage ≥100%
- ✅ cli coverage ≥80%
- ✅ auth coverage ≥75%
- ✅ Mutation score ≥85% on critical paths

### Unit 4: File Splitting (Part B.3)
- ✅ No monolithic files >500 LOC
- ✅ Parity tests verify zero behavior change
- ✅ Coverage: no regression

### Unit 5: Architecture (Part B.4)
- ✅ `tach check` passes with zero violations
- ✅ `ruff check` passes, zero new suppressions
- ✅ `pyright` passes, zero errors

---

## TDD Discipline & Execution Rules

### Test-First Pattern (Non-Negotiable)

1. **Write failing test FIRST**
   ```bash
   pytest tests/zig_hooks/test_event_validation.py -v  # FAILS
   ```

2. **Implement minimal code to pass test**
   ```bash
   pytest tests/zig_hooks/test_event_validation.py -v  # PASSES
   ```

3. **Refactor for clarity**
   ```bash
   pytest tests/zig_hooks/test_event_validation.py -v  # Still PASSES
   ```

### Coverage Checkpoints (Every Task)

```bash
pytest tests/ --cov=src/thegent --cov-report=term-missing
# Target: routing ≥100%, cli ≥80%, auth ≥75%
```

### Race Condition Detection (Every Task)

```bash
TSAN_OPTIONS=halt_on_error=1 pytest tests/orchestration/
pytest tests/integrations/auth/ --asyncio-mode=auto
```

### Boundary Enforcement (Every Phase)

```bash
tach check --verbose  # ZERO violations
```

### No Fallbacks / No Legacy Compatibility

- **FORBIDDEN**: Fallback to old shell/C++ on failure
- **FORBIDDEN**: Feature flags like `use_zig_hooks = False`
- **FORBIDDEN**: Compatibility shims
- **CORRECT**: Zig replaces shell/C++ completely; old code archived, not shipped

---

## Execution Strategy & Parallelization

### Critical Path
```
Discovery (8 min) → Design (8 min) → Build (15 min, parallel Parts A+B)
                                      → Validate (8 min) → Deploy (3 min)
```

**Total Wall Clock: ~42 minutes** (agent-driven, fully parallelized)

### Subagent Delegation
- **Architect**: Discovery + Design (8 calls each)
- **Builder-A**: Zig Hook System (~24 tasks, 6-8 parallel builders)
- **Builder-B**: Quality Fixes (~36 tasks, 4-6 parallel builders)
- **QA**: Validation (~15 tasks, 1-2 parallel checkers)
- **DevOps**: Deployment (~6 tasks, 1 builder)

---

## Conclusion

Track 3 delivers a complete Zig-based hook infrastructure with critical quality improvements, following strict TDD discipline. Phased WBS with explicit DAG dependencies ensures clear handoffs between discovery, design, build, validation, and deployment. No fallbacks, no legacy compatibility — only clean, tested, deterministic replacements.

**Estimated total wall-clock time: 42 minutes** (agent-driven, fully parallelized)
