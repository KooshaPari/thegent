# 04 — Unified Requirements

> Cross-ref: [00-MASTER-INDEX](./00-MASTER-INDEX.md) | [02-WBS](./02-UNIFIED-WBS.md) | [07-TEST](./07-TEST-STRATEGY.md)

---

## Functional Requirements (FR-001 through FR-042)

### Core Orchestration (FR-001 — FR-014)

| ID | Requirement | WP | Status | Test Category | Acceptance Criteria |
|----|-------------|-----|--------|---|---|
| FR-001 | Dependency-aware deterministic routing | WP-1001 | PARTIAL | Cat-1: Replay suite (5+ tests) | Dependency graph extracted correctly; tasks routed to correct provider; replay shows identical ordering |
| FR-002 | Idempotent execution envelopes for action safety | WP-1003 | PARTIAL | Idempotency (5+ tests) | Same run_id + step + action_type always produces same effect; duplicate submissions rejected |
| FR-003 | Policy pre-check before execution | WP-3001 | PARTIAL | Cat-11: Policy evaluation (5+ tests) | Every task checked against governance rules; policy blocks respected; < 50ms eval time |
| FR-004 | Mandatory evidence collection for promotion | WP-1005 | NOT DONE | Evidence lint (5+ tests) | All evidence present before promotion; hash verification passes; completeness audit trail |
| FR-005 | Integrity and regression gates before release | WP-2006 | NOT DONE | Regression probes (5+ tests) | All integrity checks pass; no behavioral regression vs baseline; regression tests automated |
| FR-006 | Checkpoint rollback for failed promotions | WP-2001 | PARTIAL | Rollback (5+ tests) | Failed promotion triggers checkpoint rollback; state restored within 60s; recovery complete |
| FR-007 | Retry and circuit-breaker strategy by failure class | WP-2002, WP-2003 | PARTIAL | Cat-7: Circuit breaker (15+ tests) | Each failure class mapped to retry strategy; circuit breakers per-provider; state transitions verified |
| FR-008 | Recovery playbook selection by known failure pattern | WP-2004 | NOT DONE | Playbook (5+ tests) | Failure classified automatically; playbook matched to pattern; execution within SLA |
| FR-009 | Human oversight path for repeated/unknown failures | WP-2008 | NOT DONE | HITL (3+ tests) | Escalation path triggered after 3 repeated failures; human approves recovery action |
| FR-010 | Signed action artifacts for critical operations | WP-3002 | NOT DONE | Signature (5+ tests) | Critical actions cryptographically signed; signatures verified before execution |
| FR-011 | Override controls with reason code and expiry | WP-3003 | NOT DONE | Override TTL (5+ tests) | Reason code required for override; TTL enforced; revalidation on expiry |
| FR-012 | Immutable audit event trail | WP-3004 | NOT DONE | Hash chain (5+ tests) | All gate/override/rollback events immutable; hash chain validated; retrieval < 500ms |
| FR-013 | Policy drift detection and governance sweep | WP-3005 | NOT DONE | Drift alarm (5+ tests) | Policy changes detected within 60s; drift alarms fire automatically; sweep finds violations |
| FR-014 | Trust boundary validation for environment transitions | WP-3007 | NOT DONE | Boundary (5+ tests) | Trust checks enforced at environment transitions; cross-env actions blocked without approval |

### UX & Operator (FR-015 — FR-024)

| ID | Requirement | WP | Status | Test Category | Acceptance Criteria |
|----|-------------|-----|--------|---|---|
| FR-015 | Concise and detailed explanation tiers | WP-4002 | NOT DONE | Cat-12: Progressive disclosure (15+ tests) | Tier 1 summary required before action; Tier 2 detail available on demand; < 200ms render time |
| FR-016 | One-click safe fallback for risky choices | WP-4003 | NOT DONE | Fallback UX (5+ tests) | Fallback option always visible for risky decisions; one-click execution; safety confirmed |
| FR-017 | Stale-state execution block | WP-4005 | NOT DONE | Stale state (5+ tests) | Stale state detected; execution blocked until refresh; warning displayed to operator |
| FR-018 | Continuity snapshot and owner handoff | WP-4006, WP-5006 | NOT DONE | Handoff (5+ tests) | Snapshots generated at shift boundaries; new owner confirms receipt; 100% coverage of critical tasks |
| FR-019 | Adaptive load controls with critical lane protection | WP-5001, WP-5002 | NOT DONE | Burst simulation (5+ tests) | Critical lane protected under burst; adaptive caps prevent oscillation; p95 latency stable < 2x normal |
| FR-020 | Non-critical deferral with explicit ETA | WP-5004 | NOT DONE | Deferral (3+ tests) | Non-critical items deferred during burst; explicit ETA provided; resumption automatic |
| FR-021 | Continuity watchdog for stale ownership | WP-5005 | NOT DONE | Watchdog (3+ tests) | Long-running tasks monitored; ownership staleness detected; escalation triggered after threshold |
| FR-022 | Decision replay with rationale snapshot | WP-4007 | NOT DONE | Replay (5+ tests) | Decision rationale captured at decision time; replay reconstructs full context; rationale human-readable |
| FR-023 | Role-aware confidence calibration | WP-4008 | NOT DONE | Cat-13: Calibration (5+ tests) | ECE computation correct; over/under-confidence flagged; calibration curve tracked over time |
| FR-024 | Closure pack generation for launch and audit | WP-6008 | NOT DONE | Closure (3+ tests) | Closure pack generated at launch; all evidence included; audit trail complete and verifiable |

### Contract & Adapter (FR-025 — FR-031) — NEW from Research

| ID | Requirement | WP | Status | Test Category | Acceptance Criteria |
|----|-------------|-----|--------|---|---|
| FR-025 | Contract version negotiation for structured outputs | WP-X1 | DONE | Negotiation (5+ tests) | Contract registry functional; version negotiation succeeds; capability advertisement accurate |
| FR-026 | Canonical Structured Message (CSM) normalization across XML protocols | WP-X2 | DONE | Cat-1+2: Golden corpus (50+ tests) | Task-tool 18-tag corpus passes; Zen 26-tag corpus passes; normalization lossless |
| FR-027 | Incremental XML parser with recoverable partial-state | WP-X3 | DONE | Cat-3: Adversarial XML (40+ tests) | Parser handles truncated output; recovers from unclosed tags; partial state buffered safely |
| FR-028 | Semantic validation with cross-tag invariants | WP-X4 | DONE | Cat-4: Semantic validation (15+ tests) | Cross-tag invariants enforced; status-progress coherence checked; action-result consistency verified |
| FR-029 | Provider adapter conformance tests and drift alarms | WP-X5 | DONE | Cat-5: Provider drift (20+ tests) | Per-provider adapters pass conformance; drift alarms fire within 60s; test vectors comprehensive |
| FR-030 | Policy-governed fallback routing with SLO budgets | WP-X6 | PARTIAL | Cat-6: Fallback chaos (10+ tests) | MCP → XML → raw fallback chain working; SLO budgets enforced; quality thresholds respected |
| FR-031 | Dual-read/dual-write migration support for contract upgrades | WP-X8 | NOT DONE | Migration (5+ tests) | Dual-read active during migration; dual-write staged; rollback to old contract possible; no data loss |

### Cross-Cutting Enhancements (FR-032 — FR-042) — NEW from Research

| ID | Requirement | WP | Status | Test Category | Acceptance Criteria |
|----|-------------|-----|--------|---|---|
| FR-032 | Multi-agent orchestration mode selection (sequential/parallel/hierarchical) | WP-Y1 | NOT DONE | Cat-10: Multi-agent (10+ tests) | Mode selection logic correct; sequential delegation passes output; parallel consensus aggregates; hierarchical decomposes |
| FR-033 | ABAC policy expressions for fine-grained routing decisions | WP-3001+ | NOT DONE | Cat-11: ABAC evaluation (10+ tests) | ABAC attribute resolution correct; policy evaluation accurate; 100 concurrent evals stable |
| FR-034 | Dead-letter queue with poison pill detection for permanently failing items | WP-Y2 | NOT DONE | Cat-8: DLQ (10+ tests) | Item fails 3x → poison pill detected; quarantine active; DLQ drain workflow manual; metrics tracked |
| FR-035 | Chaos engineering fault injection framework for recovery testing | WP-Y3 | NOT DONE | Cat-9: Chaos injection (20+ tests) | Provider timeout injection works; storage write failure injected; network partition simulated; recovery verified |
| FR-036 | Cost tracking per-run with budget alerts and cost-per-quality optimization | WP-Y4 | NOT DONE | Cost tracking (5+ tests) | Per-run cost calculated; budget alerts fire on threshold; cost-per-quality optimized; reports accurate |
| FR-037 | Speculative execution for latency-critical paths | WP-5001+ | NOT DONE | Cat-14: Speculative (5+ tests) | Two providers called simultaneously; first response wins; cancellation clean; dual-cost tracked |
| FR-038 | Prompt-characteristic routing (complexity/domain/length classification) | WP-1007+ | NOT DONE | Routing (5+ tests) | Prompt classified by complexity/domain/length; routing decision matches classification; latency tracking accurate |
| FR-039 | Autonomy gradient control per domain/lane in operator cockpit | WP-4001+ | NOT DONE | Autonomy (3+ tests) | Autonomy level per domain configurable; cockpit displays current gradient; overrides respected |
| FR-040 | Pre-flight simulation ("dry run") before irreversible actions | WP-4003+ | NOT DONE | Simulation (5+ tests) | Simulation runs without side effects; output matches expected for dry-run; user confirms before execute |
| FR-041 | Calibration curve tracking for confidence threshold tuning | WP-4008+ | NOT DONE | Calibration (5+ tests) | Calibration curve computed over time; threshold tuning reflects learning; ECE improves monotonically |
| FR-042 | Hierarchical prompt orchestration (platform/domain/workflow/step) | WP-Y5 | NOT DONE | Prompt hierarchy (5+ tests) | Prompt hierarchy enforced; platform-level overrides respected; workflow customization per domain |

---

## Non-Functional Requirements (NFR-001 through NFR-016)

### Original (NFR-001 — NFR-008)

| ID | Requirement | Target | WP | Status | Test Strategy | Acceptance Criteria |
|----|-------------|--------|-----|--------|---|---|
| NFR-001 | P95 routing latency within SLO under normal load | < 250ms p95 | WP-1001 | NOT DONE | Latency SLO tracking | Measured in load tests; reported in observability dashboards |
| NFR-002 | Stable critical-path latency under burst load | < 350ms p95 (5x traffic) | WP-5001 | NOT DONE | Burst simulation (5+ tests) | Critical lane protected; p95 stable under 5x traffic; no oscillation |
| NFR-003 | No non-deterministic promotion in replay tests | 0 violations | WP-1004 | NOT DONE | Determinism suite (1000+ runs) | 100% replay consistency; identical ordering on replay |
| NFR-004 | Policy checks available in production windows | 99.95% uptime | WP-3001 | NOT DONE | SLO monitoring | Policy engine uptime tracked; SLA breaches logged and alerted |
| NFR-005 | Rollback completion within incident SLA | < 60s p95 | WP-2001 | NOT DONE | Rollback execution traces | Incident logs show completion time; verified in drills |
| NFR-006 | Continuity snapshots complete for critical work | 100% coverage | WP-4006 | NOT DONE | Snapshot audit trail | All open critical tasks have snapshots; no gaps in coverage |
| NFR-007 | Audit query retrieval within operational SLA | < 500ms p95 | WP-3004 | NOT DONE | Audit read-path latency SLO | Query latency measured; SLO compliance tracked |
| NFR-008 | Operator rationale rendering within UX latency | < 100ms progressive disclosure | WP-4002 | NOT DONE | Rendering traces | Cockpit rendering latency instrumented; < 100ms p95 |

### New from Research (NFR-009 — NFR-016)

| ID | Requirement | Target | WP | Status | Test Strategy | Acceptance Criteria |
|----|-------------|--------|-----|--------|---|---|
| NFR-009 | Parse + normalize latency preserved under p95 routing SLO | < 50ms (no regression) | WP-X3 | NOT DONE | XML latency tracking | Parse+normalize adds < 50ms to routing latency |
| NFR-010 | Schema drift detection SLA | < 60s | WP-X7 | NOT DONE | Drift detection tests | Drift alarms fire within 60s of contract change |
| NFR-011 | Fallback-induced failure rate | < 1% | WP-X6 | NOT DONE | Fallback reliability tests | Fallback mode maintains < 1% additional failure rate |
| NFR-012 | Zero silent contract downgrade in critical lanes | 0 events | WP-X6 | NOT DONE | Critical lane monitoring | Contract downgrades audited and never silent; audit log entry required |
| NFR-013 | OTel GenAI semantic convention compliance | 100% spans | WP-Y6 | NOT DONE | OTel instrumentation coverage | All orchestration spans use GenAI semantic conventions |
| NFR-014 | Structured JSON logging on all orchestration events | 100% events | WP-0001 | DONE | Logging audit | All events logged as structured JSON; schema validation passes |
| NFR-015 | EU AI Act risk classification tagging on orchestration decisions | All actions | WP-3001 | NOT DONE | Risk classification audit | Every orchestration decision tagged with risk classification |
| NFR-016 | Provider routing cost reduction via optimization | >= 20% reduction at maintained quality | WP-5003 | NOT DONE | Cost tracking and A/B tests | Cost-per-quality metric improved by >= 20% vs baseline |

---

## Personas & FR Mappings

| Persona | Primary Goals | Key FRs | Supporting FRs | Key NFRs | Test Categories |
|---------|---|---------|---|----------|---|
| **Operator** | Execute decisions with clarity; maintain situational awareness | FR-001, 015, 016, 017, 022, 039 | FR-002, 004, 006, 020, 023 | NFR-001, 008 | Cat-1 (routing), Cat-12 (disclosure), Cat-13 (calibration) |
| **Incident Lead** | Recover from failures; coordinate response | FR-006, 007, 008, 009 | FR-002, 005, 021, 022 | NFR-005 | Cat-7 (circuit breaker), Playbook, HITL |
| **Platform/SRE** | Ensure stability, SLOs, runbook quality | FR-005, 019, 021, 035, 037 | FR-001, 002, 007, 013 | NFR-001, 002, 004 | Cat-9 (chaos), Burst simulation, Watchdog |
| **Governance/Compliance** | Enforce policy, audit, retention | FR-003, 010, 011, 012, 013, 014, 033 | FR-004, 005, 009 | NFR-004, 007, 015 | Cat-11 (policy/ABAC), Hash chain, Drift alarm |
| **Product Owner** | Measure value; launch readiness; cost | FR-024, 036 | FR-001, 005, 019, 039 | NFR-016 | Cost tracking, Closure |

---

## User Journeys

| Journey | Steps | FRs | Personas | Acceptance Criteria |
|---------|-------|-----|----------|---|
| **UJ-1: Standard Execution** | Submit chunk → validate → route → execute → gate → promote → close | FR-001, 002, 003, 004, 005 | Operator, Platform/SRE | Deterministic routing verified (FR-001); idempotency enforced (FR-002); policy holds respected (FR-003); evidence complete (FR-004); integrity gate passes (FR-005) |
| **UJ-2: Policy Hold** | Submit → policy check → hold → human review → approve/deny → audit | FR-003, 010, 011, 012 | Operator, Governance | Policy blocks enforced (FR-003); override with reason code (FR-011); signed actions if critical (FR-010); immutable audit trail (FR-012) |
| **UJ-3: Failure Recovery** | Failure detected → classify → playbook select → execute → rollback if needed → validate → close/handoff | FR-006, 007, 008, 009 | Incident Lead, Platform/SRE | Checkpoint rollback restores state (FR-006); circuit breaker trips/recovers (FR-007); playbook auto-selects (FR-008); human escalation on repeated failures (FR-009) |
| **UJ-4: Burst Load** | Traffic spike detected → adaptive mode triggered → critical lane protected → load shed → restore normal | FR-019, 020, 021, 037 | Platform/SRE, Operator | Critical lane p95 < 350ms under 5x load (FR-019); non-critical items deferred with ETA (FR-020); continuity watchdog active (FR-021); speculative execution reduces latency (FR-037) |
| **UJ-5: Shift Handoff** | Shift end → continuity snapshot generated → new owner receives → confirms receipt → acknowledgment logged | FR-018, 021, 022 | Operator, Incident Lead | Snapshots 100% coverage of open critical tasks (FR-018); watchdog monitors stale ownership (FR-021); decision replay with rationale captured (FR-022) |

---

## Phase Gates & Acceptance Criteria

| Gate | Phase | Criteria | Key FRs | Key WPs | Test Validation | Launch Blocker |
|------|-------|----------|---------|---------|---|---|
| **A** | Phase 0 | Schema integrity; telemetry baseline; OTel compliance | FR-026, NFR-013, NFR-014 | WP-0001, WP-0002, WP-Y6 | Golden corpus; OTel instrumentation; JSON schema validation | No |
| **X** | Phase X | Contract registry operational; adapters pass conformance; adversarial parser robust | FR-025-031, NFR-009-010, NFR-012 | WP-X1-X8 | 50-70 tests: golden corpus (18+26 tag), adversarial XML, provider drift, semantic validation | Yes |
| **B** | Phase 1 | Deterministic replay 100% consistent; idempotency enforced; evidence complete | FR-001, 002, 004, 005 | WP-1001-1005 | 1000+ replay runs; idempotency token validation; evidence audit | Yes |
| **C** | Phase 2 | Rollback succeeds within SLA; recovery playbooks tested; chaos drills pass | FR-006, 007, 008, 034, 035 | WP-2001-2008, WP-Y2-Y3 | Rollback execution traces; circuit breaker state machine; DLQ poison pill; chaos injection results | Yes |
| **D** | Phase 3 | Policy checks enforced; audit trail immutable; drift detection active; signed actions verified | FR-003, 010-014, 033 | WP-3001-3008, WP-Y5 | Policy bypass blocked; signature verification; audit query < 500ms; drift alarm < 60s | Yes |
| **E** | Phase 4 | UX comprehension tests pass; safe fallback works; decision replay renders; stale state blocked | FR-015-018, 022, 023, 039, 040 | WP-4001-4008, WP-Y7 | Operator comprehension studies; fallback UX tests; replay rendering latency < 200ms | No |
| **F** | Phase 5 | Critical path stable under burst; adaptive caps avoid oscillation; continuity snapshots at every boundary | FR-019-021, 036, 037 | WP-5001-5008, WP-Y4, WP-Y8 | Burst simulation with 5x traffic; cost tracking A/B tests; speculative execution clean cancellation | No |
| **G** | Phase 6 | Launch dress rehearsal passes; compliance signoff received; KPI baselines met; runbook certified | FR-024, all NFRs | WP-6001-6008 | Dress rehearsal execution; SLO compliance report; runbook certification; two stable release cycles | Yes |

---

## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](./00-MASTER-INDEX.md) — plan index
- [07-TEST-STRATEGY.md](./07-TEST-STRATEGY.md) — test categories and traceability
