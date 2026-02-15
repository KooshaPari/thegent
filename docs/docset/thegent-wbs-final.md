# Thegent Final WBS (Comprehensive)

Status: Finalized with Phase X Contract Hardening & WP-Y Cross-Cutting Enhancements
Date: 2026-02-15
Version: 2.0 (Updated with synthesis findings)

## Scope

This WBS defines the execution structure for thegent orchestration optimization program across reliability, governance, UX, scale, and continuity. It integrates:
- 7 original phases (0, 1, 2, 3, 4, 5, 6) with 8 WPs each (56 base WPs)
- 1 new Phase X: Contract and Adapter Hardening (8 WPs)
- 8 cross-cutting WP-Y enhancements distributed across phases
- 3 post-closure phases (Phase 10, 11, 12) with 30 WPs
- Complete dependency chains, pattern references, and acceptance criteria per WP

Total: 102 work packages across 11 named phases + cross-cutting work.

## Planning Assumptions

- Program executes with staged rollout and strict gate-based promotion.
- High-risk changes require evidence-linked approval.
- All critical actions are rollback-capable and auditable.
- Ownership exists for every work package.
- Contract normalization (Phase X) gates all Phase 1+ work.
- Cross-cutting enhancements (WP-Y) integrate into their target phases.

## Phase Structure

- **Phase 0:** Foundation and Baseline (WP-0001..0005, WP-Y6)
- **Phase X:** Contract and Adapter Hardening (WP-X1..X8) [NEW, inserts after Phase 0]
- **Phase 1:** Core Routing and Deterministic Execution (WP-1001..1008, WP-Y1)
- **Phase 2:** Reliability and Recovery Hardening (WP-2001..2008, WP-Y2, WP-Y3)
- **Phase 3:** Governance and Security Enforcement (WP-3001..3008, WP-Y5)
- **Phase 4:** Human-Centered UX and Explainability (WP-4001..4008, WP-Y7)
- **Phase 5:** Adaptive Scale and Continuity Automation (WP-5001..5008, WP-Y4, WP-Y8)
- **Phase 6:** Enterprise Readiness and Launch Closure (WP-6001..6008)
- **Phase 10:** Adaptive Interface and Ecosystem Convergence (WP-10001..10010)
- **Phase 11:** Autonomous Reliability Optimization and Predictive Resilience (WP-11001..11010)
- **Phase 12:** Enterprise-Grade Intuition, Explainability, and Hardening (WP-12001..12010)

---

## Work Packages (Detailed)

### Phase 0: Foundation and Baseline

| WP | Description | Status | Acceptance Criteria | FR Map | Pattern Map |
|----|-------------|--------|-------------------|--------|------------|
| **WP-0001** | Baseline telemetry contracts and run IDs | Done | Chunk 219 complete; run_id schemas standardized across providers | FR-001 | P-001, P-022 |
| **WP-0002** | Canonical schemas for chunk/evidence/policy events | Partial | Core events schema defined; Zen 26-tag extension blocks complete | FR-002 | P-001, P-002, P-003 |
| **WP-0003** | Planner dependency graph normalization | Done | DAG normalization rules published; crun adapter integrated | FR-003 | P-045 |
| **WP-0004** | Initial risk and confidence scoring framework | Done | Risk classes 1-4 defined; confidence decay function implemented | FR-004 | P-046 |
| **WP-0005** | Program operating model and ownership map | Unclear | RACI matrix complete; escalation paths defined | FR-005 | P-047 |
| **WP-Y6** | OTel GenAI Instrumentation (cross-cutting) | Partial | OTel spans with gen_ai.* attributes on all tool calls; parent-child hierarchy complete | FR-043 | P-074 |

**Dependencies for Phase 0:**
- WP-0001 (baseline telemetry) must complete before WP-0002 (schemas depend on telemetry contract).
- WP-Y6 (OTel) parallel with WP-0001, gates Phase X.

---

### Phase X: Contract and Adapter Hardening (NEW)

This phase gates all Phase 1+ work. Contract normalization must complete before deterministic routing can be proven stable.

| WP | Description | Status | Acceptance Criteria | FR Map | Pattern Map | Depends On |
|----|-------------|--------|-------------------|--------|-----------|------------|
| **WP-X1** | XML Contract Registry with versioning, capability negotiation, namespace-based evolution | Not Started | Registry published with 4+ provider contracts versioned; capability ads working | FR-025 | P-004, P-005, P-006 | WP-0002, WP-Y6 |
| **WP-X2** | Canonical Structured Message (CSM) model: normalize task-tool 18-tag + Zen 26-tag into unified typed schema | Not Started | CSM schema v1 published; adapters for all 4 providers produce conforming CSM; doc-vs-code mismatch resolved | FR-026 | P-001, P-002, P-007 | WP-X1 |
| **WP-X3** | Incremental XML Parser Engine: XMLPullParser with sloppy-xml-py fallback, partial-state buffering, stream-safe commit | Not Started | Parser handles streaming chunks; partial-state recovery tested; < 50ms parse latency p95 | FR-027 | P-008, P-009, P-010 | WP-X2 |
| **WP-X4** | Semantic Validation Layer: cross-tag invariants, status-progress coherence, action/result consistency, phase-aware rules | Not Started | Invariant rule engine deployed; semantic-drift events emitted on violation; silent validation disabled | FR-028 | P-011, P-012, P-013 | WP-X3 |
| **WP-X5** | Provider Adapter Conformance Suite: per-provider adapters (gemini/copilot/codex/claude) with strict test vectors and drift alarms | Not Started | Conformance suite for 4 providers with 50+ test vectors each; drift alarms working; --check-drift flag functional | FR-029 | P-014, P-015, P-016 | WP-X2 |
| **WP-X6** | Fallback Reliability Policy: MCP->XML->raw fallback state machine with SLO budgets, quality thresholds, degrade/restore controls | Not Started | FallbackPolicy state machine live; SLO budgets enforced per lane; fallback-rate < 5% | FR-030 | P-017, P-018, P-019 | WP-X3, WP-X5 |
| **WP-X7** | Contract Telemetry and Drift Detection: schema-drift and semantics-drift events with alert budgets, OPAL-style change propagation | Not Started | Drift detection within 60s; telemetry events emitted per tag mutation; OPAL-sync active | FR-043 (partial) | P-020, P-021, P-074 | WP-X4, WP-0001 |
| **WP-X8** | Contract Migration Controller: dual-read/dual-write windows, canary rollout, rollback, deprecation of legacy parsing | Not Started | Dual-read/write windows operational; canary rollout from v1->v2 tested; rollback procedure validated | FR-031 | P-022, P-023, P-024 | WP-X6, WP-X7 |

**Interdependencies within Phase X:**
- WP-X1 -> WP-X2 (CSM depends on registry).
- WP-X2 -> WP-X3 (Parser depends on CSM target schema).
- WP-X3 -> WP-X4 (Semantic validation uses parsed CSM).
- WP-X2 also -> WP-X5 (Adapters produce CSM).
- WP-X3, WP-X5 -> WP-X6 (Fallback logic uses parser + adapter quality signals).
- WP-X4, WP-0001 -> WP-X7 (Telemetry tracks validation drift).
- WP-X6, WP-X7 -> WP-X8 (Migration controller orchestrates fallback + telemetry policies).

**Critical Gate:** Phase X completion gates entry to Phase 1. All contract normalization must be production-ready before deterministic routing claims are tested.

---

### Phase 1: Core Routing and Deterministic Execution

| WP | Description | Status | Acceptance Criteria | FR Map | Pattern Map | Depends On |
|----|-------------|--------|-------------------|--------|-----------|------------|
| **WP-1001** | Dependency-aware routing engine with LiteLLM fallback chains | Not Started | Routing table stores provider chains per task; fallback_with_function chains work; p95 routing latency < 50ms | FR-006, FR-037 | P-025, P-026, P-027 | WP-X8, WP-0001 |
| **WP-1002** | Priority and urgency lane model with starvation prevention | Not Started | Lane model enforces reserved capacity for critical; urgent tasks dequeued ahead of normal; p99 wait time < 30s | FR-007 | P-028, P-029 | WP-1001 |
| **WP-1003** | Idempotent execution envelope with idempotency key generation (run_id, step_index, action_type, content_hash) | Not Started | IdempotencyKey(4-tuple) stored per action; replay returns cached result; no duplicated side effects | FR-008, FR-029 | P-030, P-031, P-032 | WP-1001 |
| **WP-1004** | Deterministic phase transition contracts with explicit guards | Not Started | Phase state machine defined; transition guards enforced; evidence required before promotion | FR-009 | P-033, P-034 | WP-1001, WP-X2 |
| **WP-1005** | Evidence capture at every promotion gate with policy-linked artifact checksums | Not Started | Evidence struct stored per gate; SHA-256 checksums immutable; policy version linked to decision | FR-010 | P-035, P-036 | WP-1004, WP-0001 |
| **WP-1006** | Conflict arbitration rules and quorum policy for multi-agent consensus | Not Started | Quorum rule engine deployed; majority vote + confidence weighting; tie escalates to human; RACI enforced | FR-011 | P-037, P-038, P-039 | WP-Y1 |
| **WP-1007** | Child-task routing policy by capability and confidence, with prompt-characteristic classification | Not Started | Child-task router matches provider capability to task type; prompt-characteristic classifier (complexity/domain/length) active | FR-012, FR-038 | P-040, P-041, P-042 | WP-1001 |
| **WP-1008** | Replay-safe run history and correlation IDs with session continuity | Not Started | Run history immutable; correlation IDs propagate across all logs; session resume tested under chaos | FR-013 | P-043, P-044 | WP-X7 |
| **WP-Y1** | Multi-Agent Mode Runtime: sequential delegation, parallel consensus, hierarchical planning | Not Started | 3 modes selectable via policy; mode-selection decision logged; conflict resolution per Kagentop pattern | FR-032 | P-053, P-054, P-055 | WP-1001, WP-X2 |

**Interdependencies within Phase 1:**
- WP-X8 -> WP-1001 (routing depends on contract normalization).
- WP-1001 -> WP-1002, WP-1003, WP-1007 (lane, idempotency, child-routing build on router).
- WP-1001, WP-X2 -> WP-1004 (deterministic transitions depend on routing + contract stability).
- WP-1004 -> WP-1005 (gates require evidence).
- WP-1001 -> WP-Y1 (multi-agent modes need router).

**Critical Gate M1:** Deterministic routing + multi-agent modes in canary. All WP-1xxx + WP-Y1 must pass canary acceptance before Phase 2 starts.

---

### Phase 2: Reliability and Recovery Hardening

| WP | Description | Status | Acceptance Criteria | FR Map | Pattern Map | Depends On |
|----|-------------|--------|-------------------|--------|-----------|------------|
| **WP-2001** | Checkpoint/rollback service with LangGraph-style PostgresSaver and thread-based snapshots | Not Started | Checkpoints stored per run_id + step_id; point-in-time recovery working; rollback SLA < 10s | FR-014 | P-056, P-057, P-058 | WP-1003 |
| **WP-2002** | Retry strategy with adaptive exponential backoff, jitter, and guardrails | Not Started | Backoff with jitter; stop-after-N; retry-on-specific exception; no thundering herd; max retry latency < 5 min | FR-015 | P-059, P-060 | WP-1001 |
| **WP-2003** | Circuit breakers for tool/model/storage classes with per-provider thresholds and half-open probes | Not Started | CLOSED/OPEN/HALF-OPEN state machine; threshold 5 failures; reset timeout 30s; health probes in HALF-OPEN | FR-016 | P-061, P-062, P-063 | WP-1001 |
| **WP-2004** | Recovery playbook automation with IdempotencyKey tokens and compensation handlers | Not Started | PlaybookRegistry stores (FailureKind, attempt_count) -> RemediationAction; compensation handlers undo side effects | FR-017 | P-064, P-065, P-066 | WP-2001, WP-1003 |
| **WP-2005** | Failure taxonomy expansion to MAST 14-mode (F-01..F-14) covering infrastructure/model/tool/logic/security | Not Started | All 14 failure modes classified; recovery strategy per mode defined; telemetry tags every failure with mode | FR-018 | P-067, P-068 | WP-1001 |
| **WP-2006** | Regression prevention probes at pre-promote stage with chaos test harness | Not Started | Probes run on every canary candidate; chaos scenarios: partition, timeout, malformed response, state corruption | FR-019 | P-069, P-070 | WP-2003, WP-Y3 |
| **WP-2007** | Evidence completeness linting with policy-linked artifact validation | Not Started | Linter checks evidence struct completeness; rejects promotion if evidence incomplete; drift detector active | FR-020 | P-071, P-072 | WP-1005 |
| **WP-2008** | Controlled oversight path for repeated failures with escalation SLA | Not Started | DLQ integration; manual review queue functional; SLA for escalation < 30 min; replay from DLQ | FR-021 | P-073 | WP-Y2 |
| **WP-Y2** | Dead-Letter Queue Service: DLQ for permanently failing items with poison pill detection, manual review interface, replay capability | Not Started | DLQ stores permanently-failed runs; poison-pill detection active (same failure 3x); manual review UI; replay < 2s latency | FR-034 | P-076, P-077, P-078 | WP-2004 |
| **WP-Y3** | Chaos Engineering Framework: fault injection (network partition, provider timeout, malformed response, state corruption) with automated test scenarios | Not Started | Fault injection library deployed; 20+ test scenarios; automated execution on PRs; rollback drills green | FR-035 | P-079, P-080, P-081 | WP-2003 |

**Interdependencies within Phase 2:**
- WP-1003 -> WP-2001 (idempotency keys enable checkpoint/rollback).
- WP-1001 -> WP-2002, WP-2003 (routing foundation for retry + circuit breaker).
- WP-2001, WP-1003 -> WP-2004 (playbook automation uses checkpoint + idempotency).
- WP-1001 -> WP-2005 (failure classification tags on routing decisions).
- WP-2003, WP-Y3 -> WP-2006 (regression probes use circuit breaker + chaos framework).
- WP-1005 -> WP-2007 (evidence linting gates promotion).
- WP-Y2 -> WP-2008 (controlled oversight via DLQ).

**Critical Gate M2:** Recovery hardening verified under chaos drills. All WP-2xxx + WP-Y2 + WP-Y3 must pass chaos test suite before Phase 3.

---

### Phase 3: Governance and Security Enforcement

| WP | Description | Status | Acceptance Criteria | FR Map | Pattern Map | Depends On |
|----|-------------|--------|-------------------|--------|-----------|------------|
| **WP-3001** | Policy pre-check and gate evaluator with OPA/Rego engine and ABAC expressions | Not Started | OPA/Rego policies deployed; ABAC eval (risk_score, domain, urgency); gate latency p95 < 5ms | FR-022, FR-033 | P-082, P-083, P-084 | WP-X8, WP-0001 |
| **WP-3002** | Signed action artifacts for critical operations with SHA-256 signatures and MAIF structure | Not Started | Action artifacts signed; signature verified pre-execute; audit trail links signature to policy version | FR-023 | P-085, P-086 | WP-1005 |
| **WP-3003** | Override path with TTL and revalidation rules, preventing abuse via reason codes and audit signatures | Not Started | Override flag with 4-hour TTL; revalidation on expiry; override reason logged + signed; audit searchable | FR-023 | P-087, P-088 | WP-3001 |
| **WP-3004** | Immutable audit trail and query interface with causal ordering (Lamport timestamps) and evidence_hash linking | Not Started | Audit log append-only; Lamport ordering; evidence_hash per entry; query API with time-range + actor filters | FR-024 | P-089, P-090, P-091 | WP-1005, WP-0001 |
| **WP-3005** | Policy drift detection and sweep automation with OPAL live distribution | Not Started | OPAL syncs policy changes within 60s; drift detector compares local vs remote policies; sweep automation fixes divergence | FR-025 | P-092, P-093 | WP-X7, WP-3001 |
| **WP-3006** | Compliance evidence retention by domain with tiered storage and domain-tagged archival | Not Started | Evidence stored in tiered storage (hot 30d, cold 1yr); domain tagging per record; compliance report generation | FR-026 | P-094, P-095 | WP-3004 |
| **WP-3007** | Trust boundary checks for environment transitions with OAuth 2.1 CIMD and capability negotiation | Not Started | Env classification (dev/stage/prod); boundary checks enforced; OAuth 2.1 CIMD on cross-boundary MCP; capability ads | FR-027 | P-096, P-097, P-098 | WP-3001 |
| **WP-3008** | Escalation SLA and governance queue operations with priority-based dispatch and continuity snapshots | Not Started | Escalation queue with SLA tracking; priority dispatch; continuity snapshots attached; incoming-owner confirmation | FR-028 | P-099, P-100 | WP-3001 |
| **WP-Y5** | Hierarchical Prompt Orchestration: 4-level prompt hierarchy (platform/domain/workflow/step) with governance policy injection | Not Started | 4-level hierarchy with override rules; policy injection at each level; prompt-audit trail for every execution | FR-042 | P-101, P-102, P-103 | WP-3001 |

**Interdependencies within Phase 3:**
- WP-X8 -> WP-3001 (policy gates follow contract normalization).
- WP-1005 -> WP-3001, WP-3004 (evidence gates policy decisions).
- WP-3001 -> WP-3002, WP-3003, WP-Y5 (gates, overrides, prompt hierarchy depend on policy engine).
- WP-1005, WP-0001 -> WP-3004 (audit trail uses evidence + telemetry).
- WP-X7, WP-3001 -> WP-3005 (drift detection monitors policy + contract changes).

**Critical Gate M3:** Governance/security gates fully enforced. All WP-3xxx + WP-Y5 must pass compliance signoff before Phase 4.

---

### Phase 4: Human-Centered UX and Explainability

| WP | Description | Status | Acceptance Criteria | FR Map | Pattern Map | Depends On |
|----|-------------|--------|-------------------|--------|-----------|------------|
| **WP-4001** | Operator cockpit summary model with 4-pane Mission Control layout and autonomy gradient control | Not Started | Cockpit UI renders 4 panes (Queue, Roster, Events, Details); autonomy dial operable; state refresh < 2s | FR-029, FR-039 | P-104, P-105, P-106 | WP-3001 |
| **WP-4002** | Concise and detailed explanation tiers (3-tier progressive disclosure) with persona-based defaults | Not Started | Tier 1 (summary) always visible; Tier 2 (detail) click-to-expand; Tier 3 (trace) deep dive; defaults by role | FR-030 | P-107, P-108 | WP-4001 |
| **WP-4003** | One-click safe fallback options: Pause / Rollback / Escalate with selective checkpoint recovery | Not Started | Fallback button always visible; Pause halts without revert; Rollback selects checkpoint; Escalate routes to owner | FR-031, FR-040 | P-109, P-110, P-111 | WP-2001, WP-4001 |
| **WP-4004** | Interruption taxonomy and fatigue controls with correlation-first alerting and dedup windows | Not Started | Interruption taxonomy (26 types); alerts deduplicated within 5 min window; alerts-per-hour ceiling enforced; snooze with auto-escalation | FR-032 | P-112, P-113, P-114 | WP-4001 |
| **WP-4005** | State freshness checks and stale-state prevention with "last updated" timestamps on all displays | Not Started | Timestamp + staleness threshold on every display; stale-state blocks action commit; refresh indication active | FR-033 | P-115, P-116 | WP-1004 |
| **WP-4006** | Continuity handoff summaries across shifts with automated snapshots and incoming-owner confirmation | Not Started | Handoff summary generated on shift boundary; attachment includes state, evidence, next steps; confirmation logged | FR-034 | P-117, P-118, P-119 | WP-3008 |
| **WP-4007** | Decision replay and rationale snapshots with what-if mode and pre-flight simulation | Not Started | Replay view steps through timeline; what-if forks at any decision; pre-flight simulates policy changes | FR-035, FR-040 | P-120, P-121, P-122 | WP-1004, WP-3004 |
| **WP-4008** | Feedback loops and confidence calibration with calibration curve tracking and dual confidence/risk indicators | Not Started | Calibration curve tracks "70% confidence -> approval rate"; dual indicator (confidence + risk); color coding (green/yellow/red) | FR-036, FR-041 | P-123, P-124, P-125 | WP-4001 |
| **WP-Y7** | TRAFFIC KPI Dashboard: 10-metric framework (Throughput, Routing accuracy, Accuracy, Freshness, Fallback rate, Interruption, Cost, Knowledge, Rollback SLA, Continuity) with real-time visualization, alerting, trend analysis | Not Started | Dashboard renders 10 KPIs; real-time updates; alerts on threshold breach; trend charts 7d/30d; SLO target lines | FR-043 | P-126, P-127, P-128 | WP-Y6, WP-4001 |

**Interdependencies within Phase 4:**
- WP-3001 -> WP-4001, WP-4002 (cockpit + explanations render policy decisions).
- WP-2001 -> WP-4003 (safe fallback uses checkpoints).
- WP-4001 -> WP-4002, WP-4004, WP-4005, WP-4008 (cockpit base for all UX).
- WP-3008 -> WP-4006 (handoff uses escalation queue).
- WP-1004, WP-3004 -> WP-4007 (replay uses phase transitions + audit trail).
- WP-Y6, WP-4001 -> WP-Y7 (KPI dashboard uses OTel data + cockpit).

**Critical Gate M4:** UX and continuity adoption targets met. All WP-4xxx + WP-Y7 must pass operator acceptance testing before Phase 5.

---

### Phase 5: Adaptive Scale and Continuity Automation

| WP | Description | Status | Acceptance Criteria | FR Map | Pattern Map | Depends On |
|----|-------------|--------|-------------------|--------|-----------|------------|
| **WP-5001** | Adaptive concurrency controller with proactive rate-limit tracking and speculative execution mode | Not Started | Concurrency cap auto-adjusts; proactive slowdown before 429; speculative execution (2 providers, use first) latency < baseline | FR-037, FR-037 | P-129, P-130, P-131 | WP-1002, WP-2003 |
| **WP-5002** | Burst load classification and safe-mode controls with traffic shaping and overload rejection | Not Started | Burst detector classifies load (normal/spike/surge); safe-mode activates on surge; traffic shaping smooths peaks | FR-038 | P-132, P-133 | WP-5001 |
| **WP-5003** | Cost-aware routing and workload shaping with RouteLLM-style provider selection and budget enforcement | Not Started | RouteLLM routing model trains on (prompt, provider, cost, quality); selects cheapest meeting quality threshold; budget alerts | FR-039 | P-134, P-135, P-136 | WP-1001, WP-Y4 |
| **WP-5004** | Non-critical deferral rules with explicit ETA and priority-based resumption | Not Started | Deferral policy defines ETA by task priority; resumed in priority order; deferral latency tracked | FR-040 | P-137, P-138 | WP-1002 |
| **WP-5005** | Long-running continuity watchdog with heartbeat and session resumption guarantees | Not Started | Watchdog heartbeat every 30s; session resumption on timeout < 5 min; active-active failover | FR-041 | P-139, P-140 | WP-1008 |
| **WP-5006** | Handoff integrity enforcement with continuity snapshot validation and ownership transfer | Not Started | Handoff validation checks snapshot completeness; ownership transfer logged; pre-flight checks before resume | FR-042 | P-141, P-142, P-143 | WP-4006, WP-5005 |
| **WP-5007** | Recovery under sustained load drills with chaos tests under 10x nominal load | Not Started | Drill scenarios: 10x load + provider timeout + network partition; recovery time SLA validated; rollback tested | FR-043 | P-144, P-145 | WP-Y3, WP-2001 |
| **WP-5008** | Load-aware recommendation tuning with workload characteristics and routing feedback | Not Started | Tuning engine observes (load, provider_latency, cost, quality); optimizes routing model; feedback loop active | FR-044 | P-146, P-147 | WP-Y4, WP-1007 |
| **WP-Y4** | Cost Tracking and Optimization Service: per-run cost aggregation, budget alerts, cost-per-quality ratio, RouteLLM-style optimization model | Not Started | Per-run cost aggregated across all tool calls; budget alerts at 80%/100%; cost-per-quality tracked; optimization model training | FR-036 | P-148, P-149, P-150 | WP-5003 |
| **WP-Y8** | Provider Scoring and Learning: continuous scoring from historical quality data, prompt-characteristic routing, speculative execution tuning | Not Started | Scoring model tracks (provider, prompt_class, quality); updates daily; routing selects top-3 per class; speculative tuning active | FR-038, FR-044 | P-151, P-152, P-153 | WP-Y4, WP-1007 |

**Interdependencies within Phase 5:**
- WP-1002, WP-2003 -> WP-5001 (concurrency depends on lanes + circuit breaker).
- WP-5001 -> WP-5002 (burst control on adaptive cap).
- WP-1001 -> WP-5003, WP-Y4, WP-Y8 (cost routing + learning use router).
- WP-1002 -> WP-5004 (deferral uses lanes).
- WP-1008 -> WP-5005 (watchdog uses session continuity).
- WP-4006, WP-5005 -> WP-5006 (handoff integrity).
- WP-Y3, WP-2001 -> WP-5007 (sustained-load drills use chaos + checkpoints).
- WP-Y4, WP-1007 -> WP-5008 (tuning uses cost data + child-task routing).

**Critical Gate M5:** Adaptive scale controls stable in production-like load. All WP-5xxx + WP-Y4 + WP-Y8 must pass load tests before Phase 6.

---

### Phase 6: Enterprise Readiness and Launch Closure

| WP | Description | Status | Acceptance Criteria | FR Map | Pattern Map | Depends On |
|----|-------------|--------|-------------------|--------|-----------|------------|
| **WP-6001** | End-to-end dress rehearsal with integrated systems under realistic scenarios | Done (partial) | Rehearsal run complete; all phases execute end-to-end; no blocking bugs; canary → prod checklist green | FR-045 | P-154 | All Phase 5 WPs |
| **WP-6002** | Security and compliance signoff package with audit trail, architecture refs, risk/oversight refs | Done | Closure-pack generated; audit trail verified; architecture documented; risk register signed off | FR-046 | P-155, P-156 | WP-3004, WP-3006 |
| **WP-6003** | Reliability and SLO certification with recovery drills validated and rollback tested | Not Started | SLO targets certified; drills all green; rollback procedure tested 3x; on-call playbooks validated | FR-047 | P-157, P-158 | WP-2001, WP-5007 |
| **WP-6004** | Runbook finalization and on-call readiness with escalation, recovery, decommission links | Done | RUNBOOK.md complete; escalation procedures; recovery playbooks; decommission links | FR-048 | P-159, P-160 | WP-2008, WP-3008 |
| **WP-6005** | KPI baselines and launch thresholds with alerting rules and target lines established | Not Started | KPI baseline thresholds set; alerting rules deployed; dashboard target lines configured; on-call runbook | FR-049 | P-161 | WP-Y7 |
| **WP-6006** | Decommission/sunset plan for temporary controls with targets, migration path, rollback | Done | DECOMMISSIONING_PLAN.md complete; targets for removal; migration path; rollback procedure | FR-050 | P-162, P-163 | WP-3005, WP-5004 |
| **WP-6007** | Post-launch observation and rollback reserve with incident severity classification and escalation | Partial | Observation playbook drafted; rollback reserve capacity defined; incident severity map; escalation SLAs | FR-051 | P-164, P-165 | WP-2008 |
| **WP-6008** | Formal closure and successor roadmap with recommendations for next phase | Not Started | Closure memo signed; recommendations documented; successor roadmap drafted; ownership transfer | FR-052 | P-166, P-167 | WP-6001..6007 |

**Dependencies for Phase 6:**
- All Phase 5 WPs -> WP-6001 (dress rehearsal integrates all work).
- WP-3004, WP-3006 -> WP-6002 (compliance signoff uses audit + evidence).
- WP-2001, WP-5007 -> WP-6003 (SLO certification uses checkpoints + drills).
- WP-2008, WP-3008 -> WP-6004 (runbooks use escalation + oversight).
- WP-Y7 -> WP-6005 (KPI baselines from dashboard).
- WP-3005, WP-5004 -> WP-6006 (decommission plan targets drift + deferral).
- WP-2008 -> WP-6007 (post-launch observation uses DLQ).
- All Phase 6 WPs -> WP-6008 (closure summarizes all).

**Critical Gate M6:** Enterprise launch readiness approved. All WP-6xxx must pass sign-off before go-live.

---

### Phase 10: Adaptive Interface and Tool Ecosystem Convergence

This phase stabilizes operation envelopes, registries, and adapter semantics before autonomous controls.

| WP | Description | Status | Acceptance Criteria | FR Map | Pattern Map | Depends On |
|----|-------------|--------|-------------------|--------|-----------|------------|
| **WP-10001** | Operation envelope schema v2 | Not Started | Uniform schema validated across CLI and MCP; compatible mode + drift-safe defaults | FR-069 | TBD | WP-9001 |
| **WP-10002** | Capability registry service | Not Started | Registry returns stable capabilities, trust metadata, and version constraints under 60ms p95 | FR-070 | TBD | WP-10001 |
| **WP-10003** | Dispatch graph implementation | Not Started | Deterministic operation resolution and policy-aware routing under repeated runs | FR-071 | TBD | WP-10001, WP-10002 |
| **WP-10004** | Adapter admission and trust policy | Not Started | Low-trust adapters blocked on critical lanes; deny rules enforced | FR-073 | TBD | WP-10002 |
| **WP-10005** | Endpoint consolidation and aliases | Not Started | CLI and MCP operation surface parity; alias mapping with deterministic fallback | FR-071 | TBD | WP-10003 |
| **WP-10006** | Unknown-operation migration UX | Not Started | Every unsupported operation returns migration alternative and alternative operation suggestions | FR-074, FR-075 | TBD | WP-10003 |
| **WP-10007** | Dispatch traceability and audit context | Not Started | Dispatch trace stores `dispatch_path`, `rule_reason`, `policy_version` | FR-072 | TBD | WP-10003 |
| **WP-10008** | Plugin lifecycle and conformance checks | Not Started | Plugins require conformance pass before activation; unsafe plugins quarantined | FR-073 | TBD | WP-10002, WP-10007 |
| **WP-10009** | Backward-compatible API evolution controls | Not Started | Compatibility matrix + migration path for breaking schema changes | FR-074 | TBD | WP-10001, WP-10005 |
| **WP-10010** | Cross-phase operations operator documentation | Not Started | One canonical operations guide supports all major operations | FR-069 | TBD | WP-10003, WP-10005 |

**Interdependencies within Phase 10:**
- WP-10001 -> WP-10002 -> WP-10003.
- WP-10003 -> WP-10005, WP-10006, WP-10007.
- WP-10002 -> WP-10004, WP-10008.
- WP-10001 + WP-10007 -> WP-10009.
- WP-10003 + WP-10005 -> WP-10010.

**Critical Gate G10:** Registry-first deterministic dispatch and migration clarity.

---

### Phase 11: Autonomous Optimization and Predictive Resilience

This phase introduces closed-loop optimization controls with governance guardrails and stability constraints.

| WP | Description | Status | Acceptance Criteria | FR Map | Pattern Map | Depends On |
|----|-------------|--------|-------------------|--------|-----------|------------|
| **WP-11001** | SLO regulator loop controller | Not Started | Stable control updates with anti-oscillation guarantees | FR-076 | TBD | WP-10003, WP-10007 |
| **WP-11002** | Forecasting engine hardening | Not Started | Forecast quality for standard plans produced with bounded latency | FR-077 | TBD | WP-11001 |
| **WP-11003** | Predictor confidence calibration | Not Started | Miscalibration triggers controlled pause; calibration dashboard available | FR-077 | TBD | WP-11002 |
| **WP-11004** | Preemption and saturation avoidance policies | Not Started | Saturation risk reduced with bounded provider preemption and rollback assumptions | FR-078 | TBD | WP-11001, WP-11002 |
| **WP-11005** | Self-healing recommendation engine | Not Started | Top-3 recommendations include assumptions and rollback metadata | FR-079 | TBD | WP-11003 |
| **WP-11006** | Adaptive task shaping | Not Started | Dynamic split/merge only with policy justification and owner traceability | FR-080 | TBD | WP-11004 |
| **WP-11007** | Continuity risk predictor | Not Started | Continuity risk alerts before predicted shift or stall events | FR-081 | TBD | WP-11006 |
| **WP-11008** | Learning loop and policy guardrails | Not Started | Parameter updates only with policy approval; rollback manifest emitted | FR-082 | TBD | WP-11003, WP-10007 |
| **WP-11009** | Safe-mode action governance | Not Started | Safe-mode actions require explicit owner and auto-expire | FR-036 | TBD | WP-11008 |
| **WP-11010** | Forecast and control evidence pack | Not Started | G11 evidence pack generated and reproducible | FR-077, FR-079, FR-081 | TBD | WP-11001, WP-11002, WP-11005 |

**Interdependencies within Phase 11:**
- WP-11001 depends on dispatch traceability from WP-10003 and WP-10007.
- WP-11002 and WP-11003 gate forecast quality controls and calibration.
- WP-11004 and WP-11005 follow forecasting + calibration decisions.
- WP-11006 and WP-11007 provide continuity-safe adaptation actions.
- WP-11008 + WP-11009 enforce owner-approved learning updates.
- WP-11010 closes Phase 11 with control evidence.

**Critical Gate G11:** Predictive control runs safely under policy with reproducible evidence.

---

### Phase 12: Enterprise-Grade Intuition, Explainability, and Hardening

This phase hardens replay, escalation, explainability, and release packaging.

| WP | Description | Status | Acceptance Criteria | FR Map | Pattern Map | Depends On |
|----|-------------|--------|-------------------|--------|-----------|------------|
| **WP-12001** | Explainability contract implementation | Not Started | Summary/detail/trace schemas align across all major decision streams | FR-083 | TBD | WP-11010, WP-9002 |
| **WP-12002** | Escalation fatigue and noise control | Not Started | Noise suppression reduces non-critical churn while preserving critical visibility | FR-084 | TBD | WP-12001 |
| **WP-12003** | Replay sandbox hardening | Not Started | Replay never writes state outside explicit execute mode | FR-085 | TBD | WP-12001 |
| **WP-12004** | What-if simulation and branch governance | Not Started | Replays branch deterministically with pre-flight simulation checks | FR-085 | TBD | WP-12003 |
| **WP-12005** | Handoff confidence and continuity envelope | Not Started | Continuity handoff requires explicit confirmation and complete evidence bundle | FR-087, FR-086 | TBD | WP-12003 |
| **WP-12006** | Evidence graph and export bundling | Not Started | Evidence graph has closed-loop links and deterministic manifest export | FR-088 | TBD | WP-12005, WP-10007 |
| **WP-12007** | Persona profiles and access constraints | Not Started | Role-based action limits and defaults enforced per persona | FR-089 | TBD | WP-12005 |
| **WP-12008** | Operational learning assets | Not Started | New operator can complete drill with generated coaching assets | FR-090 | TBD | WP-12007 |
| **WP-12009** | Automation of release docs packaging | Not Started | One-command packaging of PRD/WBS/test artifacts with checksums | FR-090 | TBD | WP-12006, WP-12008 |
| **WP-12010** | Phase 10–12 closure and handoff note | Not Started | Finality evidence and owner approvals compiled for sign-off | FR-090 | TBD | WP-12009 |

**Interdependencies within Phase 12:**
- WP-12001 requires WP-11010 and interface explainability baseline from WP-9002.
- WP-12003 hardens replay safety before branching (WP-12004).
- WP-12005 requires replay guardrails and continuity baseline.
- WP-12006 requires evidence graph completeness from WP-12005 and dispatch audit trace.
- WP-12007 drives persona controls used by WP-12008.
- WP-12010 only after all WPs in 12 and Gates G10–G11 evidence are complete.

**Critical Gate G12:** Replay-safe explainability and deterministic release packaging.

---

## Dependencies: Complete Dependency Chain

### Foundation to Deterministic Routing:
```
WP-0001 (telemetry baseline)
    ↓
WP-Y6 (OTel instrumentation)
    ↓
WP-0002 (canonical schemas)
    ↓
WP-X1 (contract registry)
    ↓
WP-X2 (CSM normalization)
    ↓
WP-X3 (incremental parser)
    ↓
WP-X4 (semantic validation) + WP-X5 (adapter conformance)
    ↓
WP-X6 (fallback policy)
    ↓
WP-X7 (contract telemetry) + WP-X8 (migration controller)
    ↓
WP-1001 (dependency-aware routing engine)
```

### Routing to Multi-Agent Modes:
```
WP-1001 (routing engine) + WP-X2 (CSM)
    ↓
WP-Y1 (multi-agent modes)
    ↓
WP-1006 (conflict arbitration)
```

### Routing to Lanes and Idempotency:
```
WP-1001 (routing engine)
    ↓
WP-1002 (lane model) | WP-1003 (idempotency)
    ↓
WP-1004 (phase transitions)
    ↓
WP-1005 (evidence capture)
```

### Idempotency to Checkpoint/Rollback:
```
WP-1003 (idempotency)
    ↓
WP-2001 (checkpoint/rollback)
    ↓
WP-2004 (recovery playbooks)
    ↓
WP-4003 (safe fallback)
```

### Retry and Circuit Breaker:
```
WP-1001 (routing engine)
    ↓
WP-2002 (retry) | WP-2003 (circuit breaker)
    ↓
WP-Y3 (chaos engineering framework)
    ↓
WP-5007 (recovery under sustained load)
```

### Failure Taxonomy and DLQ:
```
WP-1001 (routing engine)
    ↓
WP-2005 (failure taxonomy: MAST 14-mode)
    ↓
WP-Y2 (dead-letter queue)
    ↓
WP-2008 (controlled oversight path)
```

### Governance and Policy Gates:
```
WP-X8 (contract migration) + WP-0001 (telemetry)
    ↓
WP-3001 (policy pre-check engine: OPA/Rego + ABAC)
    ↓
WP-3002 (signed artifacts) | WP-3003 (override path)
    ↓
WP-1005 (evidence capture) + WP-3004 (audit trail)
    ↓
WP-3005 (drift detection) | WP-3007 (trust boundaries)
    ↓
WP-Y5 (hierarchical prompt orchestration)
```

### Audit and Compliance:
```
WP-1005 (evidence capture) + WP-0001 (telemetry)
    ↓
WP-3004 (immutable audit trail)
    ↓
WP-3006 (evidence retention by domain)
    ↓
WP-6002 (security/compliance signoff)
```

### Cockpit and UX:
```
WP-3001 (policy gates)
    ↓
WP-4001 (operator cockpit)
    ↓
WP-4002 (explanation tiers) | WP-4004 (fatigue controls) | WP-4005 (state freshness) | WP-4008 (calibration)
    ↓
WP-2001 (checkpoint/rollback)
    ↓
WP-4003 (safe fallback)
    ↓
WP-3008 (escalation SLA)
    ↓
WP-4006 (continuity handoff)
```

### KPI and Observability:
```
WP-Y6 (OTel instrumentation)
    ↓
WP-4001 (cockpit) + WP-Y7 (TRAFFIC dashboard)
    ↓
WP-4008 (calibration curves)
    ↓
WP-6005 (KPI baselines and launch thresholds)
```

### Cost and Optimization:
```
WP-1001 (routing engine) + WP-Y4 (cost tracking)
    ↓
WP-5003 (cost-aware routing: RouteLLM)
    ↓
WP-5008 (load-aware tuning)
    ↓
WP-Y8 (provider scoring and learning)
```

### Concurrency and Load:
```
WP-1002 (lane model) + WP-2003 (circuit breaker)
    ↓
WP-5001 (adaptive concurrency) + WP-5002 (burst load)
    ↓
WP-5004 (deferral) | WP-5005 (continuity watchdog)
    ↓
WP-5006 (handoff integrity)
    ↓
WP-5007 (recovery under sustained load)
```

### Handoff and Continuity:
```
WP-3008 (escalation SLA)
    ↓
WP-4006 (continuity handoff)
    ↓
WP-5005 (watchdog) + WP-5006 (handoff integrity)
    ↓
WP-6007 (post-launch observation)
```

### Enterprise Closure:
```
All Phase 1..5 WPs
    ↓
WP-6001 (end-to-end rehearsal)
    ↓
WP-6002 (compliance) + WP-6003 (SLO cert) + WP-6004 (runbook) + WP-6005 (KPI baselines) + WP-6006 (decommission) + WP-6007 (post-launch)
    ↓
WP-6008 (formal closure)
```

### Interface Convergence and Control:
```
WP-9001 (operations protocol v1)
    ↓
WP-10001 (operation envelope v2) + WP-10002 (capability registry)
    ↓
WP-10003 (deterministic dispatch graph)
    ↓
WP-10007 (dispatch trace context)
    ↓
WP-10004 (adapter trust) + WP-10008 (adapter conformance lifecycle)
    ↓
WP-11001 (SLO regulator)
    ↓
WP-12003 (replay sandbox hardening)
    ↓
WP-12006 (evidence graph packaging)
    ↓
WP-12010 (phase 10-12 closure)
```

### Predictive and Explainability Escalation:
```
WP-11001 (SLO regulator)
    ↓
WP-11002 (forecasting) + WP-11003 (calibration)
    ↓
WP-11004 (preemption) + WP-11005 (self-heal recommendations)
    ↓
WP-12001 (explainability contract) + WP-12004 (what-if branch governance)
    ↓
WP-12006 (evidence bundling) + WP-12009 (release pack compiler)
```

---

## Milestones and Gates

| Milestone | Description | Gate | WPs Complete | Date Target |
|-----------|-------------|------|-------------|-------------|
| **M0** | Foundation baseline + OTel instrumentation | Gate A | WP-0001..0005, WP-Y6 | M-1w |
| **MX** | Contract registry + canonical schema + parser hardening | Gate A+ | WP-X1..X8 | M-2w |
| **M1** | Deterministic routing + multi-agent modes in canary | Gate B | WP-1001..1008, WP-Y1 | M-3w |
| **M2** | Recovery hardening + DLQ + chaos verified under drills | Gate C | WP-2001..2008, WP-Y2, WP-Y3 | M-5w |
| **M3** | Governance/security gates + prompt hierarchy enforced | Gate D | WP-3001..3008, WP-Y5 | M-7w |
| **M4** | UX cockpit + TRAFFIC dashboard + continuity adoption | Gate E | WP-4001..4008, WP-Y7 | M-9w |
| **M5** | Adaptive scale + cost optimization + provider scoring stable | Gate F | WP-5001..5008, WP-Y4, WP-Y8 | M-11w |
| **M6** | Enterprise launch readiness approved | Gate G | WP-6001..6008 | M-13w |
| **M10** | Deterministic dispatch and operation compatibility | Gate G10 | WP-10001..10010 | M-15w |
| **M11** | Predictive control and policy-aware self-heal | Gate G11 | WP-11001..11010 | M-17w |
| **M12** | Explainability and release hardening | Gate G12 | WP-12001..12010 | M-19w |

---

## Acceptance Gates (Detailed)

### Gate A: Schema and Telemetry Integrity
- [x] WP-0001 complete: run_id schemas standardized; telemetry baseline established.
- [x] WP-Y6 complete: OTel spans with gen_ai.* attributes on all tool calls.
- [ ] WP-0002 complete: canonical schemas published with Zen 26-tag extension blocks.
- **Approval:** Engineering lead + Platform SRE.

### Gate A+: Contract Normalization (NEW)
- [ ] WP-X1 complete: contract registry with 4+ provider contracts versioned.
- [ ] WP-X2 complete: CSM schema v1 published; all providers produce conforming CSM.
- [ ] WP-X3 complete: parser handles streaming chunks; < 50ms p95 latency.
- [ ] WP-X4 complete: semantic validation deployed; drift events emitted.
- [ ] WP-X5 complete: conformance suite for all 4 providers; drift alarms functional.
- [ ] WP-X6 complete: fallback policy enforced; fallback-rate < 5%.
- [ ] WP-X7 complete: drift detection < 60s; telemetry active.
- [ ] WP-X8 complete: dual-read/write canary rollout tested.
- **Approval:** Engineering lead + Governance/Compliance.

### Gate B: Deterministic Replay and Idempotency
- [ ] WP-1001 complete: routing table live; fallback chains work.
- [ ] WP-1003 complete: IdempotencyKey(4-tuple) enforced; no duplicated side effects.
- [ ] WP-1004 complete: phase state machine enforced.
- [ ] WP-1008 complete: replay tested end-to-end; session resume under chaos.
- [ ] WP-Y1 complete: multi-agent modes selectable; conflict resolution working.
- **Approval:** Engineering lead + QA.

### Gate C: Rollback and Recovery
- [ ] WP-2001 complete: checkpoint/rollback SLA < 10s.
- [ ] WP-2002 complete: retry with jitter; no thundering herd.
- [ ] WP-2003 complete: circuit breaker 3-state; half-open probes working.
- [ ] WP-2004 complete: recovery playbooks automated; compensation handlers functional.
- [ ] WP-2005 complete: MAST 14-mode taxonomy deployed.
- [ ] WP-Y2 complete: DLQ live; poison pill detection active.
- [ ] WP-Y3 complete: chaos test suite green; 20+ scenarios covered.
- **Approval:** SRE + Incident Commander.

### Gate D: Policy, Security, and Audit Controls
- [ ] WP-3001 complete: OPA/Rego policies deployed; gate latency p95 < 5ms.
- [ ] WP-3003 complete: override path with TTL; revalidation on expiry.
- [ ] WP-3004 complete: immutable audit trail with Lamport ordering.
- [ ] WP-3005 complete: OPAL policy sync active; drift detection working.
- [ ] WP-3007 complete: trust boundary checks enforced; OAuth 2.1 CIMD live.
- [ ] WP-Y5 complete: 4-level prompt hierarchy with policy injection.
- **Approval:** Governance/Compliance + Security.

### Gate E: UX Clarity and Operator Efficiency
- [ ] WP-4001 complete: cockpit 4-pane layout; state refresh < 2s.
- [ ] WP-4002 complete: 3-tier explanations with persona defaults.
- [ ] WP-4003 complete: Pause/Rollback/Escalate always visible; safe fallback SLA < 5s.
- [ ] WP-4004 complete: alerts deduplicated; alerts-per-hour ceiling enforced.
- [ ] WP-4006 complete: continuity handoff snapshots generated; confirmation logged.
- [ ] WP-Y7 complete: TRAFFIC dashboard with 10 KPIs; real-time updates.
- **Approval:** Product/Ops + Operator acceptance testing.

### Gate F: Burst Load and Continuity Stress
- [ ] WP-5001 complete: adaptive concurrency; proactive rate limit tracking.
- [ ] WP-5002 complete: burst classifier; safe-mode activates on surge.
- [ ] WP-5003 complete: cost-aware routing; budget alerts functional.
- [ ] WP-5005 complete: watchdog heartbeat; session resumption < 5 min.
- [ ] WP-5006 complete: handoff integrity checks; ownership transfer logged.
- [ ] WP-5007 complete: drills under 10x load pass; recovery SLA validated.
- [ ] WP-Y4 complete: cost tracking per-run; optimization model training.
- [ ] WP-Y8 complete: provider scoring model active; routing tuning functional.
- **Approval:** Platform/SRE + Load testing team.

### Gate G: Launch Readiness and Closure
- [ ] WP-6001 complete: dress rehearsal end-to-end; no blocking bugs.
- [ ] WP-6002 complete: compliance signoff package generated; risk register signed.
- [ ] WP-6003 complete: SLO targets certified; rollback tested 3x.
- [ ] WP-6004 complete: runbooks finalized; on-call ready.
- [ ] WP-6005 complete: KPI baselines set; alerting rules deployed.
- [ ] WP-6006 complete: decommission plan targets set; migration path approved.
- [ ] WP-6007 complete: observation playbook ready; rollback reserve defined.
- [ ] WP-6008 complete: closure memo signed; successor roadmap drafted.
- **Approval:** Executive sponsor + All domain leads.

### Gate G10: Interface Determinism and Migration Safety
- [ ] WP-10001 complete: operation envelopes validated across CLI and MCP.
- [ ] WP-10002 complete: capability registry returns stable version and trust metadata.
- [ ] WP-10003 complete: dispatch path deterministic across repeated invocations.
- [ ] WP-10006 complete: unknown operations return structured migration guidance.
- [ ] WP-10007 complete: dispatch trace fields persisted and queryable.
- **Approval:** Platform lead + Governance/Ops.

### Gate G11: Predictive Control and Safe Optimization
- [ ] WP-11001 complete: control loop stable under anti-oscillation constraints.
- [ ] WP-11002 complete: forecast quality telemetry valid for standard plans.
- [ ] WP-11003 complete: calibration controls pause unsafe auto-adjustments.
- [ ] WP-11005 complete: recommendations include owner and rollback assumptions.
- [ ] WP-11010 complete: G11 evidence pack reproducible.
- **Approval:** SRE + Governance + Product.

### Gate G12: Explainability, Replay Safety, and Deterministic Packaging
- [ ] WP-12001 complete: explainability summary/detail/trace contract stable.
- [ ] WP-12003 complete: replay remains read-only unless execute mode enabled.
- [ ] WP-12006 complete: evidence packaging produces deterministic manifest.
- [ ] WP-12009 complete: PRD/WBS/test pack compile pass.
- [ ] WP-12010 complete: final closure inventory and approvals complete.
- **Approval:** Executive sponsor + Product/Ops + Compliance.

---

## RACI Model

| Role | Phase 0 | Phase X | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 | Phase 6 | Phase 10 | Phase 11 | Phase 12 |
|------|---------|---------|---------|---------|---------|---------|---------|---------|----------|----------|----------|
| **Engineering** | R/A | R/A | R/A | R/A | C | C | R/A | C | R/A | R/A | R/A |
| **Platform/SRE** | C | C | C | R/A | C | C | R/A | R/A | R/A | C | R/A |
| **Governance/Compliance** | C | R/A | C | C | R/A | C | C | R/A | R/A | R/A | R/A |
| **Product/Ops** | C | C | C | C | C | R/A | C | A | C | C | R/A |
| **QA/Testing** | C | C | R/A | R/A | C | C | R/A | R/A | C | R/A | R/A |

**Legend:** R=Responsible (does the work), A=Accountable (final authority), C=Consulted (provides input).

---

## Risk Controls

### Critical Lane Starvation Prevention
- Reserved capacity enforcement: critical lane gets 30% of total concurrency.
- Lane priority queue: urgent tasks dequeue before normal.
- SLA: p99 wait time for critical < 30s.
- **Control:** WP-1002 lane model with automated reserved capacity.

### Override Abuse Prevention
- TTL enforcement: overrides expire after 4 hours.
- Reason codes: every override requires reason + risk classification.
- Audit signature: override decisions signed and logged.
- Revalidation on expiry: policy re-evaluated before action commit.
- **Control:** WP-3003 override path + WP-3004 audit trail.

### Oscillation Damping in Adaptive Cap Changes
- Concurrency cap changes dampened: max 10% change per adjustment.
- Adjustment frequency: min 5 min between changes.
- Observation window: 30 min baseline before tuning.
- **Control:** WP-5001 adaptive concurrency controller with dampening.

### Hard Stale-State Blocks Before Action Commit
- State age check: action commit blocked if state > 60s old.
- Refresh indicator: UI shows "last updated" + staleness flag.
- Force-refresh button: operator can trigger immediate refresh before action.
- **Control:** WP-4005 state freshness checks + WP-4001 cockpit display.

### Continuity Ownership Requirement for Unresolved High-Risk Tasks
- High-risk classification: (confidence < 70% AND new failure mode) OR (manual override in-use).
- Ownership requirement: high-risk task must have assigned owner before shift-end.
- SLA: ownership transfer + continuity snapshot within 30 min of shift boundary.
- **Control:** WP-4006 continuity handoff + WP-3008 escalation SLA.

---

## Closure Criteria

- [x] All phases planned with signed acceptance gates.
- [ ] All 102 work packages tracked with implementation status.
- [ ] Phase 0 baseline complete + OTel instrumentation (M0).
- [ ] Phase X contract normalization complete (MX) and gates Phase 1.
- [ ] Phase 1 routing + multi-agent modes in canary (M1).
- [ ] Phase 2 recovery hardening verified under drills (M2).
- [ ] Phase 3 governance/security gates enforced (M3).
- [ ] Phase 4 UX cockpit + TRAFFIC dashboard live (M4).
- [ ] Phase 5 adaptive scale stable under production-like load (M5).
- [ ] Phase 6 enterprise launch readiness approved (M6).
- [ ] Phase 10 interface convergence complete (M10).
- [ ] Phase 11 predictive controls hardened (M11).
- [ ] Phase 12 explainability and final packaging complete (M12).
- [ ] No unresolved critical risk without documented acceptance.
- [ ] Two stable release cycles post-launch with < 5% incident rate.
- [ ] Complete transfer package for long-term ownership.

---

## Pattern Catalog Reference

This WBS references 100+ transferable patterns from cross-analysis. Key patterns by domain:

### Contract and Schema Design (P-001..P-024)
- P-001: Strict Core + Rich Extension
- P-002: Tag Vocabulary as Typed Schema
- P-003: Exactly-Once Tag Cardinality
- P-004: Namespace-Based Contract Versioning
- P-005..P-024: [See mega-synthesis Part 5]

### Routing and Execution (P-025..P-044)
- P-025: LiteLLM Fallback Chains
- P-026: Function-with-Fallbacks Pattern
- P-027: Provider Scoring Model
- P-028..P-044: [See mega-synthesis Part 5]

### Reliability and Recovery (P-056..P-081)
- P-056: PostgresSaver Checkpoint Model
- P-057: Thread-Based Snapshots
- P-058: Point-in-Time Recovery
- P-059..P-081: [See mega-synthesis Part 5]

### Governance and Policy (P-082..P-103)
- P-082: OPA/Rego Policy Engine
- P-083: ABAC Policy Expressions
- P-084: OPAL Live Distribution
- P-085..P-103: [See mega-synthesis Part 5]

### UX and Observability (P-104..P-153)
- P-104: Mission Control 4-Pane Layout
- P-105: Autonomy Gradient Control
- P-106: Progressive Disclosure 3-Tier
- P-107..P-153: [See mega-synthesis Part 5]

---

## Notes on Implementation Status

Status codes used in WP descriptions:

- **Done**: Artifact complete, tested, deployed.
- **Partial**: Artifact partially complete; gaps identified in gaps doc.
- **Unclear**: Artifact status unknown; requires verification.
- **Not Started**: Artifact planning complete; implementation not yet begun.

All status determinations as of 2026-02-15 per `thegent-gaps-and-discovery-2026-02-14.md`.

---

## Document References

- `thegent-prd-final.md` - Product Requirements Document with acceptance criteria.
- `thegent-dag-final.md` - Detailed DAG with node contracts and service mappings.
- `thegent-research-validation-2026-02-14.md` - Contract validation research with FR mappings.
- `thegent-cross-analysis-matrix-2026-02-14.md` - Cross-codebase analysis findings.
- `thegent-kush-docs-deep-dive-2026-02-14.md` - Kush docs architecture analysis.
- `thegent-mega-research-synthesis-2026-02-14.md` - Comprehensive synthesis with 100+ patterns.
- `thegent-gaps-and-discovery-2026-02-14.md` - Implementation gaps and discovery tasks.
- `thegent-wbs-phase7-9.md` - Post-closure work decomposition for phases 7–9.
- `thegent-dag-phase7-9-extension.md` - Phase 7–9 DAG dependencies and control flow.
- `thegent-wbs-phase10-12.md` - Phase 10–12 WBS extension with sequencing and dependencies.
- `thegent-plan-final-index.md` - Index of all plan artifacts and relationships.
- `thegent-implementation-log-2026-02-14.md` - Log of completed implementations.

---

## Appendix: WP Effort Estimates (Agent-Led Tool Calls)

| Phase | Total WPs | Estimated Tool Calls | Parallel Subagents | Wall Clock |
|-------|-----------|----------------------|-------------------|------------|
| Phase 0 | 6 | 30-45 | 2-3 | 8-15 min |
| Phase X | 8 | 70-105 | 3-4 | 20-30 min |
| Phase 1 | 9 | 60-90 | 3-4 | 18-25 min |
| Phase 2 | 11 | 70-105 | 3-5 | 20-30 min |
| Phase 3 | 9 | 55-80 | 2-3 | 15-22 min |
| Phase 4 | 9 | 55-80 | 2-3 | 15-22 min |
| Phase 5 | 10 | 60-90 | 3-4 | 18-25 min |
| Phase 6 | 8 | 40-60 | 2-3 | 12-18 min |
| **Total** | **102** | **680-1040** | **32-47** | **175-270 min** |

(WP-0001..0005 + WP-X1..X8 + WP-1001..1008 + WP-2001..2008 + WP-3001..3008 + WP-4001..4008 + WP-5001..5008 + WP-6001..6008 + WP-Y1..Y8 + WP-7001..7010 + WP-8001..8010 + WP-9001..9010 + WP-10001..10010 + WP-11001..11010 + WP-12001..12010 = 102 total WPs)

---

**End of WBS Document**

Last Updated: 2026-02-15
Next Review: Upon M10 completion
