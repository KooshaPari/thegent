# 02 — Unified Work Breakdown Structure

> Cross-ref: [00-MASTER-INDEX](./00-MASTER-INDEX.md) | [01-STATE](./01-PROJECT-STATE.md) | [03-DAG](./03-UNIFIED-DAG.md) | [04-REQ](./04-REQUIREMENTS.md) | [10-DISPATCH](./10-SUBAGENT-DISPATCH.md)

---

## Phase Summary

| Phase | Title | WPs | Depends On | Effort (tool calls) | Wall Clock |
|-------|-------|-----|------------|---------------------|------------|
| 0 | Foundation & Baseline | 7 | — | 35-55 | 10-16 min |
| X | Contract & Adapter Hardening | 8 | Phase 0 | 70-105 | 20-30 min |
| 1 | Core Routing & Deterministic Execution | 10 | Phase X | 65-100 | 20-28 min |
| 2 | Reliability & Recovery Hardening | 11 | Phase 1 | 70-105 | 20-30 min |
| 3 | Governance & Security Enforcement | 9 | Phase 1 | 55-80 | 15-22 min |
| 4 | Human-Centered UX & Explainability | 9 | Phase 2, 3 | 55-80 | 15-22 min |
| 5 | Adaptive Scale & Continuity | 10 | Phase 2, 3 | 60-90 | 18-25 min |
| 6 | Enterprise Readiness & Launch | 8 | Phase 4, 5 | 40-60 | 12-18 min |
| **Total** | | **75** | | **460-685** | **130-191 min** |

---

## Phase 0: Foundation & Baseline

**Gate A**: Schema and telemetry integrity pass

| WP | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-0001 | Baseline telemetry contracts and run IDs | DONE | P0 | — | NFR-013, NFR-014 | 5-8 | execution.py |
| WP-0002 | Canonical schemas for chunk/evidence/policy events | PARTIAL | P0 | WP-0001 | FR-026 | 8-12 | contracts/csm.py |
| WP-0003 | Planner dependency graph normalization | DONE | P0 | — | FR-001 | 5-8 | execution.py |
| WP-0004 | Risk and confidence scoring framework | DONE | P1 | WP-0001 | FR-023 | 6-10 | contracts/validation.py |
| WP-0005 | Program operating model and ownership map | NOT DONE | P2 | — | — | 3-5 | docs/ |
| WP-0006 | Run state tracking and pause/resume CLI | DONE | P0 | WP-0001 | FR-003 | 4-6 | execution.py, cli.py (RunState, pause_cmd, resume_cmd) |
| WP-Y6 | OTel GenAI instrumentation | NOT DONE | P0 | WP-0001 | NFR-013 | 8-12 | NEW: telemetry/ |

**Acceptance**: All event schemas validate; OTel traces visible; run IDs correlate across services; pause/resume events recorded.

---

## Phase X: Contract & Adapter Hardening

**Gate X**: Contract registry operational; adapters pass conformance; parser handles adversarial input

| WP | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-X1 | XML contract registry with versioning | DONE | P0 | WP-0002 | FR-025 | 8-12 | contracts/registry.py |
| WP-X2 | Canonical Structured Message (CSM) model | DONE | P0 | WP-X1 | FR-026 | 10-15 | contracts/csm.py |
| WP-X3 | Incremental XML parser engine | DONE | P1 | WP-X2 | FR-027 | 10-15 | contracts/parser.py |
| WP-X4 | Semantic validation layer | DONE | P1 | WP-X3 | FR-028 | 8-12 | contracts/validation.py |
| WP-X5 | Provider adapter conformance suite | DONE | P1 | WP-X2 | FR-029 | 12-18 | contracts/adapters.py, conformance.py |
| WP-X6 | Fallback reliability policy | DONE | P1 | WP-X5 | FR-030 | 8-12 | agents/state_machine.py, contracts/policy.py |
| WP-X7 | Contract telemetry and drift detection | DONE | P2 | WP-X5 | NFR-010 | 6-10 | contracts/telemetry.py |
| WP-X8 | Contract migration controller | DONE | P2 | WP-X7 | FR-031 | 8-12 | contracts/migration.py |

**Acceptance**: Golden corpus (18-tag + 26-tag) passes; adversarial XML handled; drift alarms fire within 60s.

---

## Phase 1: Core Routing & Deterministic Execution

**Gate B**: Deterministic replay and idempotency pass

| WP | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-1001 | Dependency-aware routing engine | PARTIAL | P0 | WP-X6 | FR-001 | 10-15 | NEW: orchestration/router.py |
| WP-1002 | Priority and urgency lane model | NOT DONE | P1 | WP-1001 | FR-019 | 6-10 | NEW: orchestration/lanes.py |
| WP-1003 | Idempotent execution envelope | DONE | P1 | WP-0001 | FR-002 | 8-12 | execution.py |
| WP-1004 | Deterministic phase transition contracts | NOT DONE | P1 | WP-1003 | FR-004 | 6-10 | NEW: orchestration/phases.py |
| WP-1005 | Evidence capture at every promotion gate | NOT DONE | P1 | WP-1004 | FR-004 | 8-12 | NEW: orchestration/evidence.py |
| WP-1006 | Conflict arbitration rules and quorum policy | NOT DONE | P2 | WP-1001 | FR-032 | 6-10 | orchestration_modes.py |
| WP-1007 | Child-task routing by capability and confidence | NOT DONE | P2 | WP-1001 | FR-038 | 8-12 | models/catalog.py |
| WP-1008 | Replay-safe run history and correlation IDs | DONE | P1 | WP-0001 | FR-022 | 6-10 | execution.py |
| WP-1009 | Pause/resume MCP tools and continuity snapshots | NOT DONE | P2 | WP-1008 | FR-003 | 6-10 | mcp_server.py (add pause/resume tools + continuity metadata) |
| WP-Y1 | Multi-agent mode runtime | PARTIAL | P2 | WP-1006 | FR-032 | 12-18 | orchestration_modes.py (3 modes defined: sequential, consensus, review) |

**Acceptance**: Replay test suite shows 100% deterministic transitions; idempotency tokens prevent duplicate work; pause/resume preserves state.

---

## Phase 2: Reliability & Recovery Hardening

**Gate C**: Rollback and recovery pass under chaos tests

| WP | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-2001 | Checkpoint/rollback service | PARTIAL | P1 | WP-1003 | FR-006 | 10-15 | execution.py (CheckpointRegistry exists), NEW: orchestration/checkpoint.py (service ops) |
| WP-2002 | Retry strategy with adaptive backoff | DONE | P1 | WP-1001 | FR-007 | 6-10 | agents/resilience.py |
| WP-2003 | Circuit breakers per subsystem | NOT DONE | P1 | WP-2002 | FR-007 | 8-12 | NEW: orchestration/circuit_breaker.py |
| WP-2004 | Recovery playbook automation | NOT DONE | P1 | WP-2001 | FR-008 | 10-15 | NEW: orchestration/playbooks.py |
| WP-2005 | MAST 14-mode failure taxonomy | NOT DONE | P1 | WP-2003 | FR-007 | 6-10 | NEW: orchestration/failure_modes.py |
| WP-2006 | Regression prevention probes | NOT DONE | P2 | WP-2004 | FR-005 | 6-10 | NEW: orchestration/probes.py |
| WP-2007 | Evidence completeness linting | NOT DONE | P2 | WP-1005 | FR-004 | 4-6 | contracts/validation.py |
| WP-2008 | Controlled oversight for repeated failures | NOT DONE | P2 | WP-2004 | FR-009 | 6-10 | NEW: orchestration/oversight.py |
| WP-Y2 | Dead-letter queue service | NOT DONE | P3 | WP-2005 | FR-034 | 6-10 | NEW: orchestration/dlq.py |
| WP-Y3 | Chaos engineering framework | NOT DONE | P3 | WP-2003 | FR-035 | 10-15 | NEW: tests/chaos/ |
| WP-Y8-rel | Provider scoring with learning | NOT DONE | P3 | WP-2003 | FR-021 | 10-15 | models/catalog.py |

**Acceptance**: Crash during execution resumes with no duplicate work; circuit breakers trip and recover; chaos tests pass.

---

## Phase 3: Governance & Security Enforcement

**Gate D**: Policy, security, and audit controls pass

| WP | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-3001 | Policy pre-check and gate evaluator | PARTIAL | P1 | WP-1004 | FR-003, FR-033 | 10-15 | NEW: governance/policy_engine.py |
| WP-3002 | Signed action artifacts | NOT DONE | P2 | WP-3001 | FR-010 | 6-10 | NEW: governance/signatures.py |
| WP-3003 | Override path with TTL and revalidation | NOT DONE | P2 | WP-3001 | FR-011 | 6-10 | NEW: governance/overrides.py |
| WP-3004 | Immutable audit trail and query interface | NOT DONE | P1 | WP-0001 | FR-012 | 10-15 | NEW: governance/audit.py |
| WP-3005 | Policy drift detection and sweep | NOT DONE | P2 | WP-3001 | FR-013 | 6-10 | NEW: governance/drift.py |
| WP-3006 | Compliance evidence retention | NOT DONE | P3 | WP-3004 | — | 6-10 | NEW: governance/retention.py |
| WP-3007 | Trust boundary checks | NOT DONE | P2 | WP-3001 | FR-014 | 6-10 | NEW: governance/trust.py |
| WP-3008 | Escalation SLA and governance queue | NOT DONE | P2 | WP-3001 | — | 6-10 | NEW: governance/escalation.py |
| WP-Y5 | Hierarchical prompt orchestration | NOT DONE | P3 | WP-3001 | FR-042 | 6-10 | NEW: orchestration/prompts.py |

**Acceptance**: Policy bypass attempts blocked with audit log; signed artifacts verify; drift alarms fire.

---

## Phase 4: Human-Centered UX & Explainability

**Gate E**: UX clarity and operator efficiency pass

| WP | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-4001 | Operator cockpit summary model | NOT DONE | P2 | WP-3004 | FR-015, FR-039 | 10-15 | NEW: ux/cockpit.py |
| WP-4002 | Concise and detailed explanation tiers | NOT DONE | P2 | WP-4001 | FR-015 | 6-10 | NEW: ux/explanations.py |
| WP-4003 | One-click safe fallback options | NOT DONE | P2 | WP-2001 | FR-016, FR-040 | 6-10 | NEW: ux/fallback_ui.py |
| WP-4004 | Interruption taxonomy and fatigue controls | NOT DONE | P2 | WP-4001 | — | 6-10 | NEW: ux/alerts.py |
| WP-4005 | State freshness checks and stale-state prevention | NOT DONE | P2 | WP-1003 | FR-017 | 6-10 | execution.py |
| WP-4006 | Continuity handoff summaries | NOT DONE | P2 | WP-2001 | FR-018 | 8-12 | execution.py |
| WP-4007 | Decision replay and rationale snapshots | NOT DONE | P2 | WP-3004 | FR-022 | 8-12 | NEW: ux/replay.py |
| WP-4008 | Feedback loops and confidence calibration | NOT DONE | P3 | WP-0004 | FR-023, FR-041 | 8-12 | NEW: ux/calibration.py |
| WP-Y7 | TRAFFIC KPI dashboard | NOT DONE | P2 | WP-0001 | — | 8-12 | NEW: ux/kpis.py |

**Acceptance**: Operators pass comprehension tests; safe fallback works; decision replay renders correctly.

---

## Phase 5: Adaptive Scale & Continuity Automation

**Gate F**: Burst load and continuity stress pass

| WP | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-5001 | Adaptive concurrency controller | NOT DONE | P2 | WP-2003 | FR-019, FR-037 | 10-15 | NEW: orchestration/concurrency.py |
| WP-5002 | Burst load classification and safe-mode | NOT DONE | P2 | WP-5001 | FR-019 | 6-10 | NEW: orchestration/burst.py |
| WP-5003 | Cost-aware routing and workload shaping | NOT DONE | P2 | WP-1001 | NFR-016 | 8-12 | models/catalog.py |
| WP-5004 | Non-critical deferral rules | NOT DONE | P2 | WP-5002 | FR-020 | 4-6 | NEW: orchestration/deferral.py |
| WP-5005 | Long-running continuity watchdog | NOT DONE | P2 | WP-4006 | FR-021 | 6-10 | execution.py |
| WP-5006 | Handoff integrity enforcement | NOT DONE | P2 | WP-4006 | FR-018 | 6-10 | execution.py |
| WP-5007 | Recovery under sustained load drills | NOT DONE | P3 | WP-2004, WP-5001 | — | 8-12 | tests/ |
| WP-5008 | Load-aware recommendation tuning | NOT DONE | P3 | WP-5003 | — | 6-10 | models/catalog.py |
| WP-Y4 | Cost tracking and optimization service | NOT DONE | P3 | WP-5003 | FR-036 | 8-12 | NEW: orchestration/cost.py |
| WP-Y8 | Provider scoring with learning | NOT DONE | P3 | WP-5003, WP-2003 | — | 10-15 | models/catalog.py |

**Acceptance**: Critical-path latency stable under burst; adaptive caps avoid oscillation; continuity snapshots at every boundary.

---

## Phase 6: Enterprise Readiness & Launch Closure

**Gate G**: Launch readiness and closure pass

| WP | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-6001 | End-to-end dress rehearsal | NOT DONE | P1 | All Phase 5 | — | 10-15 | tests/ |
| WP-6002 | Security and compliance signoff | PARTIAL | P1 | WP-3006 | — | 8-12 | docs/enterprise/ |
| WP-6003 | Reliability and SLO certification | NOT DONE | P1 | WP-5007 | NFR-001-008 | 8-12 | docs/ |
| WP-6004 | Runbook finalization and on-call readiness | PARTIAL | P2 | WP-2004 | — | 6-10 | docs/RUNBOOK.md |
| WP-6005 | KPI baselines and launch thresholds | NOT DONE | P2 | WP-Y7 | — | 4-6 | docs/ |
| WP-6006 | Decommission/sunset plan | NOT DONE | P2 | — | — | 4-6 | docs/enterprise/ |
| WP-6007 | Post-launch observation and rollback reserve | PARTIAL | P2 | WP-6001 | — | 6-10 | docs/ |
| WP-6008 | Formal closure and successor roadmap | NOT DONE | P3 | All | — | 4-6 | docs/ |

**Acceptance**: Dress rehearsal passes; compliance signoff received; two stable release cycles achieved.

---

## Dependency Graph (Critical Paths)

```
Path 1 (Contract → Routing → Enterprise):
  WP-0001 → WP-0002 → WP-X1 → WP-X2 → WP-1001 → WP-2001 → WP-6001

Path 2 (Schema → Audit → Compliance):
  WP-0002 → WP-X5 → WP-1005 → WP-3004 → WP-6002

Path 3 (Execution → Recovery → SLO):
  WP-1003 → WP-2004 → WP-5007 → WP-6003

Path 4 (Trust → Continuity → Runbook):
  WP-3007 → WP-4006 → WP-5006 → WP-6004

Path 5 (Telemetry → KPI → Launch):
  WP-Y6 → WP-Y7 → WP-6005
```

---

## Milestone Calendar

| Milestone | Description | Gate | Key WPs |
|-----------|-------------|------|---------|
| M0 | Foundation baseline | A | WP-0001..0006, WP-Y6 |
| MX | Contract hardening | X | WP-X1..X8 |
| M1 | Deterministic routing | B | WP-1001..1009, WP-Y1 |
| M2 | Recovery verified | C | WP-2001..2008, WP-Y2, Y3 |
| M3 | Governance enforced | D | WP-3001..3008, WP-Y5 |
| M4 | UX adopted | E | WP-4001..4008, WP-Y7 |
| M5 | Scale stable | F | WP-5001..5008, WP-Y4, Y8 |
| M6 | Enterprise launch | G | WP-6001..6008 |
