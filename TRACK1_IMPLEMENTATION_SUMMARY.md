# Track 1 TDD Implementation Plan — Delivery Summary

## What Was Delivered

A comprehensive, test-driven implementation plan for Track 1 of the thegent hexagonal split. This plan provides **bite-sized, executable tasks** with failing tests first, minimal implementations, and parity verification at each step.

**Scope:** Migrate ~30K LOC from thegent (Python) to CLIProxy (Go):
- Pareto frontier routing (~11.5K LOC)
- Provider adapters (~1.4K LOC)
- OAuth/auth integrations
- Quota/cost tracking

---

## Documentation Structure (4 Files, ~90K words)

### 1. **docs/changes/hexagonal-split-track-1/README.md** (13 KB)
**Purpose:** Entry point & navigation guide

**Contents:**
- High-level overview of Track 1
- Task grid by work stream (5 streams, 20 tasks)
- Execution timeline (Day 1–2, parallel strategy)
- Key files by work stream (where to add/edit)
- Quality gates & success criteria
- Getting started options (comprehensive vs. quick vs. strategic)
- Risk summary & next phases
- Full document map

**When to read:** First. Start here if new to Track 1.

---

### 2. **docs/changes/hexagonal-split-track-1/TRACK1_TDD_IMPLEMENTATION_PLAN.md** (52 KB)
**Purpose:** Complete technical specification for all 20 tasks

**Contents:**
- Executive summary (scope, timeline, TDD approach)
- 5 work streams with detailed task breakdown:
  - **Work Stream 1:** Pareto frontier routing (T1.1–T1.5)
    - Failing test, implementation, HTTP endpoint, parity verification
  - **Work Stream 2:** Provider adapters (T2.1–T2.3)
  - **Work Stream 3:** OAuth token management (T3.1–T3.3)
  - **Work Stream 4:** Quota enforcement (T4.1–T4.3)
  - **Work Stream 5:** Thegent integration & cleanup (T5.1–T5.5)
  - **Cross-track:** Endpoint smoke test (T0.0)

**Per-task structure:**
- Exact file paths (thegent & CLIProxy)
- Failing test code (TDD requirement)
- Minimal implementation (Go or Python)
- Acceptance criteria
- Verification commands (bash/pytest/go)
- Commit message template

**Appendices:**
- Summary table: all 20 tasks, dependencies, durations, files
- Parallel execution plan (Day 1–2 timeline)
- Risk mitigation strategies
- File structure reference (before/after Track 1)

**When to read:** Before starting implementation. Reference during coding.

---

### 3. **docs/changes/hexagonal-split-track-1/TRACK1_QUICK_REFERENCE.md** (11 KB)
**Purpose:** Operational handbook for hands-on developers

**Contents:**
- Task dependency DAG (visual graph)
- 1-page checklist (status tracking)
- File map (quick lookup)
- Copy-paste shell commands for each work stream
- Parallel execution strategies (sequential vs. subagents)
- Quality gates checklist
- Verification checklist (pre-merge)
- Gotchas & tips
- Example full session (20-minute demo)

**When to read:** While implementing. Keep this open in a terminal.

---

### 4. **docs/changes/hexagonal-split-track-1/TRACK1_ARCHITECTURE_DECISIONS.md** (14 KB)
**Purpose:** Strategic decisions, rationale, and open questions

**Contents:**
- **8 Architecture Decision Records (ADRs):**
  - ADR-001: Port Pareto to Go (not FFI)
  - ADR-002: HTTP endpoints (not lib imports)
  - ADR-003: OAuth in CLIProxy (centralized)
  - ADR-004: Translators in CLIProxy (not distributed)
  - ADR-005: Quota in CLIProxy (not thegent)
  - ADR-006: Task classifier separate from routing
  - ADR-007: Parity testing (dual-run before deletion)
  - ADR-008: CLIProxy as separate process (not embedded)

- **8 Open Questions (Deferred Decisions):**
  - Q1–Q8 covering quota scope, downtime handling, token persistence, etc.

- **Risk Register** (probability × impact × mitigation)
- **Success Criteria** (9-point checklist for "DONE")
- **Next Steps** (Tracks 2–4 preview)

**When to read:** Before starting, to understand the "why" behind design choices. Refer back when making architectural decisions.

---

## How to Use This Plan

### 🚀 **Start Immediately**
1. **Skim README.md** (10 min) — Understand scope & task grid
2. **Start T1.1** (from TRACK1_TDD_IMPLEMENTATION_PLAN.md)
   - Create failing test: `go test -run TestParetoRoutingSelectsOptimalModelGivenConstraints`
3. **Parallelize T2–T4** after T1.4 (routing endpoint available)
4. **Run T5.1–T5.5** sequentially after parity tests pass
5. **Check T0.0** for final verification

### 🔍 **Understand the "Why"**
1. Read TRACK1_ARCHITECTURE_DECISIONS.md (ADRs + rationale)
2. Review risk register
3. Clarify open questions (Q1–Q8) before starting conflicting tasks

### 📋 **Track Progress**
Use TRACK1_QUICK_REFERENCE.md checklist:
- [ ] T1.1–T1.5 (Work Stream 1)
- [ ] T2.1–T2.3 (Work Stream 2) — parallel
- [ ] T3.1–T3.3 (Work Stream 3) — parallel
- [ ] T4.1–T4.3 (Work Stream 4) — parallel
- [ ] T5.1–T5.5 (Work Stream 5) — sequential
- [ ] T0.0 (Smoke test) — final

---

## Key Features of This Plan

### 1. **Strict TDD (Test-Driven Development)**
- **Every task starts with a failing test** (code that shouldn't exist yet)
- Implementation is minimal (just enough to pass test)
- No fallbacks, legacy compatibility, or "optional" features
- Fail fast, fail loudly

Example (T1.1):
```go
// Test FIRST (fails because paretoRouter doesn't exist)
func TestParetoRoutingSelectsOptimalModelGivenConstraints(t *testing.T) {
    req := &RoutingRequest{...}
    selected, err := paretoRouter.SelectModel(ctx, req)  // ERROR: undefined
    assert.NoError(t, err)
    // ... assertions ...
}

// THEN implement minimal code to pass
func (p *ParetoRouter) SelectModel(ctx context.Context, req *RoutingRequest) (*RoutingCandidate, error) {
    // Minimal implementation
}
```

### 2. **Parity Verification at Each Stage**
- T1.5 verifies thegent.routing.ParetoRouter == CLIProxy /v1/routing/select
- T2.3 verifies thegent adapters == CLIProxy translators
- T3.3 verifies thegent OAuth == CLIProxy token manager
- T4.3 verifies thegent quota == CLIProxy enforcer
- T5.5 verifies legacy Python routing == new CLIProxy routing
- **Only deletes old code (T5.3) after parity is 100%**

### 3. **Bite-Sized Tasks**
- Each task is 30 min – 2 hours
- Each produces one passing test
- Each can be done independently (except dependencies)
- 20 tasks total, fits in 2 days with parallelism

### 4. **Executable Specifications**
- Every task includes:
  - Exact file paths (copy-paste ready)
  - Test code (copy-paste ready)
  - Implementation skeleton
  - Bash/pytest/go commands to run
  - Expected output/behavior
  - Commit message

### 5. **Parallel Work Streams**
- Work Stream 1 (routing) is foundational
- Work Streams 2–4 (adapters, auth, quota) run in parallel after WS1
- Work Stream 5 (integration) is sequential, last

Timeline:
```
T1.1–T1.5 (6.5h)
        ↓
T2.1–T2.3 (3h) ┐
T3.1–T3.3 (3h) ├─ parallel (3h wall clock)
T4.1–T4.3 (3h) ┘
        ↓
T5.1–T5.5 (8h) — sequential
        ↓
T0.0 (30m) — smoke test
```

**Total wall-clock duration:** ~12–14 hours with 4 parallel subagents.

### 6. **Risk Mitigation**
- Dual-implementation parity tests prevent silent failures
- Failing tests first catch bugs immediately
- Minimal changes reduce scope for defects
- Quality gates (tach, pytest, go vet) catch boundary violations
- Clear commit messages enable easy review

---

## Architecture Highlights

### Key Decisions
1. **Port Pareto to Go** (not expose via FFI) → simpler, faster
2. **HTTP endpoints** (not lib imports) → decoupled, scalable
3. **Centralized OAuth** in CLIProxy → single source of truth
4. **Translators in CLIProxy** → reusable across harnesses
5. **Quota in CLIProxy** → prevents cost overruns
6. **Separate task classifier** → modular, testable
7. **Parity testing** → verify before deletion
8. **CLIProxy as separate process** → scale independently

### Resulting Architecture
```
thegent (thin orchestration layer)
  ↓ HTTP
CLIProxy localhost:8317
  ├─ /v1/routing/select (Pareto frontier)
  ├─ /v1/auth/oauth/refresh (token mgmt)
  ├─ /v1/quota/check (quota enforcement)
  ├─ /v1/translate/acp (adapters)
  └─ /v1/models (metadata)
  ↓
Providers (OpenAI, Anthropic, Gemini, etc.)
```

---

## File Locations

All Track 1 documentation is in:
```
/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/docs/changes/hexagonal-split-track-1/
├─ README.md (start here)
├─ TRACK1_TDD_IMPLEMENTATION_PLAN.md (detailed specs)
├─ TRACK1_QUICK_REFERENCE.md (operational handbook)
└─ TRACK1_ARCHITECTURE_DECISIONS.md (strategic decisions)
```

---

## Next Steps (After Track 1)

### Track 2: Remaining Integrations
- Migrate cost tracking, credential lifecycle
- Add CLIProxy endpoints for credential refresh

### Track 3: Optimization
- Response caching in CLIProxy
- Batch multiple routing requests
- Latency metrics/SLOs

### Track 4: Production Rollout
- Canary to 10%, monitor for parity
- 100% rollout
- Decommission thegent.routing module

---

## Quality & Governance

**Pre-merge gates:**
- ✅ All 20 tests pass (Go + Python)
- ✅ Parity suite 100%
- ✅ `tach check` (boundaries)
- ✅ `go vet`, `ruff check` (linting)
- ✅ No LiteLLM in routing
- ✅ 20 commits with `@trace` tags

**Success criteria:**
- Identical behavior before/after (parity verified)
- All routing calls flow through CLIProxy
- Old code deleted, zero dangling imports
- Clean commit history

---

## Support & Questions

**Open questions deferred to later:**
- Q1: Quota per-agent vs. global?
- Q2: CLIProxy downtime fallback?
- Q3: Persist OAuth tokens?
- Q4: Model metadata sync?
- Q5: Provider-specific extensions?
- Q6: Quota reject vs. queue?
- Q7: API versioning?
- Q8: Mock CLIProxy in tests?

See **TRACK1_ARCHITECTURE_DECISIONS.md** for full context.

---

## Credits & References

**Source code analyzed:**
- thegent routing: `/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/src/thegent/routing/` (~11.5K LOC)
- thegent adapters: `/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/src/thegent/adapters/` (~1.4K LOC)
- CLIProxy registry: `/Users/kooshapari/temp-PRODVERCEL/485/kush/CLIProxyAPI-plusplus/pkg/llmproxy/registry/`
- CLIProxy auth: `/Users/kooshapari/temp-PRODVERCEL/485/kush/CLIProxyAPI-plusplus/pkg/llmproxy/auth/`
- CLIProxy translator: `/Users/kooshapari/temp-PRODVERCEL/485/kush/CLIProxyAPI-plusplus/pkg/llmproxy/translator/`

**Terminal Bench 2.0 reference:**
- Model routing metrics: `/Users/kooshapari/temp-PRODVERCEL/485/kush/thegent/docs/reference/MODEL_ROUTING_TERMINAL_BENCH_2_0_QUICK_REF.md`

---

## Status

**📋 Ready for Implementation**

All specifications written. No blocking unknowns. Ready to start T1.1 immediately.

**Estimated timeline:** 2 days wall clock with 4 parallel subagents.

---

Generated: 2026-02-22
Track 1 TDD Implementation Plan — Complete
