# Thegent WBS — Phase 7 to Phase 9 (Next-Wave Execution)

**Status:** Draft  
**Date:** 2026-02-15  
**Scope:** Contract hardening, predictive reliability, autonomous operations, and ecosystem extension.

## 0) Meta constraints

- Entry criteria: Phase 6 go/no-go closure pass recorded and signed.
- Exit criteria: New phases are testable, evidence-bound, and rollback-safe.
- Rollback policy: Any critical contract migration blocker triggers rollback reserve within the run.

## 1) Phase 7 Work Packages (Contract Convergence and Parser Reliability)

| WP-ID | Work package | Estimated effort | Owner type | Dependencies | Deliverable | Acceptance criterion |
|---|---|---|---|---|---|
| WP-7001 | Contract capability negotiation protocol | 3d | Platform lead | WP-6008 | `supported_contract_versions` at session and tool boundaries | Negotiation works across MCP and CLI paths; unknown versions are rejected with clear reason |
| WP-7002 | Contract namespace registry and negotiation metadata | 2d | Platform lead | WP-7001 | Registry service + read endpoint | Registry query returns latest versions and compatibility matrix |
| WP-7003 | Canonical parser state machine for streaming/chunks | 5d | Core runtime | WP-7002 | Streaming parser with strict state + checkpoint API | Partial chunks do not emit final parse or commit state |
| WP-7004 | Partial-state commit guard and recovery protocol | 2d | Core runtime | WP-7003 | `commit_checkpoint` semantics + recovery handler | Recovery from malformed stream is deterministic and no duplicate side effects |
| WP-7005 | Semantic validator policy layer | 4d | Core runtime + Governance | WP-7004 | Phase-aware invariants and cross-tag checks | Semantic policy blocks invalid status/action combinations |
| WP-7006 | Adapter conformance suite v1 (4 providers) | 6d | QA + Contracts | WP-7005, WP-X2 | 50+ sample vectors per provider, CI gate | All providers pass conformance suite |
| WP-7007 | Fallback confidence scoring and downgrade path | 3d | Platform lead | WP-7003, WP-7006 | MCP->XML->raw state transitions with confidence penalties | Confidence delta visible and enforced in gating |
| WP-7008 | Dual-read / dual-write migration controller | 6d | Platform lead + Ops | WP-7001, WP-7007, WP-6008 | Migration switch + canary percentages + health gate | Zero-critical data loss under 1%/2%/5%/100% ramp |
| WP-7009 | Contract health dashboard and trend alerting | 4d | Observability | WP-7007 | Health API + trend tables | Trend deltas visible with owner-level attribution |
| WP-7010 | Contract drift remediation policy hooks | 3d | Governance | WP-7009 | Auto-pause and escalation on critical drift | Drift policy triggers controlled pause + evidence |

### 1.1 Phase 7 gate

- **Gate M7:** 95% of critical runs contain explicit contract metadata and confidence score.
- **Gate M7:** 0 high-confidence parser downgrade incidents in canary windows.
- **Gate M7:** FR-053 to FR-060 evidence suite signed and stored.

## 2) Phase 8 Work Packages (Predictive Reliability and Autonomous Adaptation)

| WP-ID | Work package | Estimated effort | Owner type | Dependencies | Deliverable | Acceptance criterion |
|---|---|---|---|---|---|
| WP-8001 | Plan graph extraction for risk simulation | 4d | Data/Planning | WP-7003 | Dependency graph + critical path extraction | Graph generated for all WBS exports with stable IDs |
| WP-8002 | Monte Carlo / PERT uncertainty engine integration | 6d | Planning | WP-8001 | Duration simulation with p50/p80/p95 outputs | Forecasts persisted for each run and plan template |
| WP-8003 | Bottleneck and contention analyzer | 4d | Planning | WP-8001, WP-8002 | Top bottlenecks + no-slack tasks output | Bottlenecks are reproducible and actionable |
| WP-8004 | Reschedule recommendation service | 5d | Operations | WP-8002, WP-8003 | Suggestion list with ETA, risk, confidence | Recommendations include explicit rollback assumptions |
| WP-8005 | Predictive continuity risk model | 3d | Governance | WP-8003 | Continuity risk bands + ownership-staleness forecasts | Stale ownership risk alerts before shift failures |
| WP-8006 | Surge watcher and preemptive safe-mode control | 4d | SRE | WP-8002 | Surge policy engine + load envelope actions | Safe mode prevents critical lane starvation |
| WP-8007 | Adaptive routing budget guard | 3d | Cost/Performance | WP-8006 | Predictive throttle and deferral control | Deferral decisions logged with rationale |
| WP-8008 | Simulation-backed runbook authoring | 5d | Product + Ops | WP-8004 | Runbook templates with what-if alternatives | Dry-runs confirm actions and expected outcomes |
| WP-8009 | Intervention automation policy | 4d | Governance | WP-8007 | Semi-automated decision and escalation handoff | Human approvals on high-risk interventions |
| WP-8010 | Forecast accuracy audit and calibration | 3d | QA | WP-8002 | Calibration dashboard and anomaly alerts | Forecast quality stays within confidence targets |

### 2.1 Phase 8 gate

- **Gate M8:** 90%+ forecast completion with explainable outputs.
- **Gate M8:** Risk thresholds and intervention options are logged for all critical runs.
- **Gate M8:** No safe-mode toggle executes without owner trace and rollback path.

## 3) Phase 9 Work Packages (Productized Operations and Ecosystem Extension)

| WP-ID | Work package | Estimated effort | Owner type | Dependencies | Deliverable | Acceptance criterion |
|---|---|---|---|---|---|
| WP-9001 | Unified operations surface (operation protocol v1) | 6d | Product lead | WP-8009, WP-7001 | Typed operations (`observe`, `plan`, `replay`, `simulate`) | One command surface for all major operations |
| WP-9002 | Explainability stack (summary/detail/trace) | 5d | Product + UX | WP-9001 | Shared explanation schema and rendering | Same event visible across all 3 levels without divergence |
| WP-9003 | Replay and sandbox environment isolation | 4d | Core runtime | WP-9001 | Read-only replay and non-mutating simulation mode | Replay never mutates state |
| WP-9004 | Continuity handoff enforcement in workflow | 4d | Governance | WP-8005, WP-9002 | Ownership confirmation + snapshot completeness check | Handoff blocks continue only with explicit confirmation |
| WP-9005 | Universal tool adapter layer | 7d | Platform lead | WP-9001 | Adapter wrappers for operation families | Tool calls map to universal ops with schema validation |
| WP-9006 | Decision replay and what-if simulation | 6d | Product + Ops | WP-9003 | What-if replay timeline and alternate branch output | Operators can compare alternatives before commit |
| WP-9007 | Confidence governance and escalation thresholds | 4d | Governance | WP-9002 | Confidence policy engine and escalation mapping | Low-confidence paths escalate by policy |
| WP-9008 | Operator safety controls and fallback UI | 4d | UX | WP-9004, WP-9007 | Pause / rollback / escalate controls with required confirmation | Controls always visible; actions recorded |
| WP-9009 | Evidence continuity and audit linkage | 3d | Compliance | WP-9008, WP-7009 | Continuity artifact and audit cross-links | Every major action has linked artifact |
| WP-9010 | Documentation and training package for phase 7–9 | 3d | Documentation | WP-9001, WP-9002, WP-9003, WP-9004 | Runbooks + onboarding + migration notes | Signed training completion by operators and policy owners |

### 3.1 Phase 9 gate

- **Gate M9:** 100% high-risk actions contain confidence + source evidence link.
- **Gate M9:** All replay runs remain read-only unless explicit execute approval mode is enabled.
- **Gate M9:** WBS-to-artifact mapping exists for all WP-9001 to WP-9010.

## 4) Cross-cutting dependencies

- `WP-7008` depends on `WP-7001` and supports all phase 8/9 operations.
- `WP-8004` consumes `WP-8001` and `WP-8002`.
- `WP-9005` consumes `WP-7001`, `WP-7007`, and `WP-8007`.
- `WP-9009` must remain open until `WP-7009` and `WP-9004` are complete.
- `WP-9010` closes only after `WP-9001`, `WP-9002`, and `WP-9003` produce stable docs and examples.

## 5) Suggested sequencing and timeline

- Weeks 1–2: WP-7001 through WP-7006
- Weeks 3–4: WP-7007 through WP-7010 + gate review
- Weeks 5–6: WP-8001 through WP-8005
- Weeks 7–8: WP-8006 through WP-8010 + calibration
- Weeks 9–10: WP-9001 through WP-9005
- Weeks 11–12: WP-9006 through WP-9010 + final audit

## 6) Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Overlapping migration and simulation changes | Coupled regressions | Stage by gate and freeze parser core during risk simulation rollout |
| Contract churn creates operational noise | Increased escalations and alerts | Introduce confidence thresholds and gradual rollout windows |
| Explainability mismatch across UI/CLI | Operator confusion | Use shared schema IDs and golden trace fixtures |
| Replay misused in production | Unwanted state mutation | Enforce explicit execution mode for mutable operations |

## 7) Owner mapping

- Core runtime: `WP-7001`, `WP-7003`, `WP-7004`, `WP-7007`, `WP-7008`, `WP-8002`, `WP-8006`, `WP-9003`
- Planning/data science: `WP-8001`, `WP-8002`, `WP-8003`, `WP-8004`, `WP-8010`
- SRE/Operations: `WP-8005`, `WP-8006`, `WP-8007`, `WP-8009`, `WP-9001`, `WP-9008`
- Product/UX: `WP-9002`, `WP-9006`, `WP-9004`
- Governance/Compliance: `WP-7005`, `WP-7009`, `WP-7010`, `WP-9007`, `WP-9009`, `WP-9010`

## 8) Immediate ready-to-run next chunk (for implementation team)

1. Implement WP-7001 and WP-7002.
2. Create parser recovery tests for partial-state protection (WP-7003, WP-7004).
3. Implement `TestContractNegotiation` and `TestParserPartialState` classes from PRD mapping.
4. Add phase 7 acceptance checklist to implementation log.



---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index

