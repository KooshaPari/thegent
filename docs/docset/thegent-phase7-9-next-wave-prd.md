# Thegent Phase 7–9 Next-Wave PRD (Post-Closure Optimization)

**Status:** Draft for immediate implementation conversion
**Date:** 2026-02-15
**Scope:** Phase 7–9 execution architecture after launch readiness (closure complete)

This document extends the existing PRD with the next three waves:

- Phase 7: Contract Convergence and Parser Reliability
- Phase 8: Predictive Reliability and Autonomous Adaptation
- Phase 9: Productized Operations and Ecosystem Extension

It is written to be converted in chunks into tasks, tests, and change sets.

---

## 1. Strategic objective

- Preserve enterprise production posture while making the platform significantly more robust under non-ideal provider and output conditions.
- Move from “validated but mostly static” to “continuously self-optimizing” with explicit guardrails.
- Encode contract negotiation and parser behavior as first-class operations so downstream tooling can reason about reliability, not just hope for it.

### 1.1 Key outcomes by end of Phase 9

1. No blocking contract schema ambiguity across providers.
2. Parser and fallback quality improvements reduce blind spots in malformed/partial outputs.
3. Predictive planning shortens incident recovery by proactively identifying risk.
4. Operators gain richer control and explainability across long-running runs.
5. Product surface includes universal orchestration operations with stable versioning and migration support.

---

## 2. Product context and constraints

## 2.1 Context

- The platform currently has substantial Phase 1–6 capability and closure evidence.
- Local research confirms high-value patterns:
  - task-tool: strict 18-tag XML contract with exact-once validation semantics.
  - zen: rich status/action/incomplete tag protocol plus MCP-first + XML fallback + extraction utilities.
  - crun: Monte Carlo simulation and resource/bottleneck analysis for PERT-informed planning.
- Next-wave work must avoid breaking current closure guarantees:
  - Deterministic behavior on core pathways.
  - Gate-driven deployment model.
  - Evidence-first compliance artifacts.

## 2.2 Constraints

1. No silent contract downgrade in critical lanes.
2. Fallback paths must preserve reason code, confidence score, and structured trace.
3. Migration steps must remain reversible during rollout.
4. New APIs must expose versioned schema metadata.

---

## 3. Phase 7: Contract Convergence and Parser Reliability

### 3.1 Functional requirements (new FRs)

| FR-ID | Requirement | Acceptance criteria |
|---|---|---|
| FR-053 | Contract capability negotiation at session start | Client and server publish `supported_contract_versions`; selection uses highest mutually compatible version. |
| FR-054 | Dual contract acceptance during migration | During migration window, runtime accepts both old/new contract namespaces. |
| FR-055 | Strict canonical parser with recoverable partial-state model | Streaming parser supports partial XML chunks; partial buffers are never committed as final status. |
| FR-056 | Semantic validator with phase-aware invariants | Cross-field constraints (e.g., status/progress/ result coherence) enforced before promotion. |
| FR-057 | Provider-specific adapter conformance checks | Each provider emits normalized canonical payload with conformance score and drift events. |
| FR-058 | Confidence-aware fallback scoring | Fallback from MCP→XML→raw requires explicit confidence penalty and reason. |
| FR-059 | Dual-read/dual-write migration control | One migration transaction can read old/new and write both safely under configurable window. |
| FR-060 | Contract health trend instrumentation | Health trend report includes drift rate, strictness violations, and confidence distribution by lane/provider. |

### 3.2 Non-functional requirements (new NFRs)

| NFR-ID | Requirement | Target |
|---|---|---|
| NFR-017 | Parser hardening latency | Parse+normalize under load < 50ms p95 in steady state |
| NFR-018 | Fallback determinism | Same input always yields same fallback state transitions. |
| NFR-019 | Drift observability lag | Structural or semantic drift surfaced within 60s |
| NFR-020 | Migration safety | Any release can pause dual-read/write in < 2 minutes |
| NFR-021 | Coverage | Conformance suite includes 4 providers with 50+ sample vectors each |

### 3.3 User experience requirements (Phase 7)

- Operator can see contract version negotiated and parser path used on each run.
- Any fallback event is visible in history with confidence score and reason.
- Failure traces include `root`, `tag_count`, `namespace`, and `schema_profile` metadata.

### 3.4 Implementation scope

- Add contract namespace registry.
- Introduce parser state checkpointing and partial-state guard.
- Add policy gate that blocks critical lanes on non-compliant payloads.
- Expand conformance artifacts to include confidence and drift traces.

### 3.5 Phase 7 acceptance

- 100% of acceptance tests for FR-053..FR-060 pass.
- 2x10 minutes dry-run migration simulations complete with zero critical data loss.
- No unknown namespace/partial payload committed as final evidence for critical WPs.

---

## 4. Phase 8: Predictive Reliability and Autonomous Adaptation

### 4.1 Functional requirements (new FRs)

| FR-ID | Requirement | Acceptance criteria |
|---|---|---|
| FR-061 | PERT + Monte Carlo risk estimate on critical paths | Phase gate computes 50th/80th/95th duration bands for plan-level critical paths. |
| FR-062 | Resource-aware rescheduling assistant | On projected risk, runbook proposes preemptive rescheduling options with confidence range. |
## 4.2 Non-functional requirements (new NFRs)

| NFR-ID | Requirement | Target |
|---|---|---|
| NFR-022 | Prediction quality | 80%+ calibration between predicted and observed schedule risk within 2 release windows. |
| NFR-023 | Intervention time | Risk mitigation suggestion available within 90 seconds of gate pressure signal. |
| NFR-024 | Load responsiveness | Surge classifies within one control interval and enters safe-mode before SLO breach. |

### 4.3 User experience requirements (Phase 8)

- Operators receive “risk snapshot cards” for long plans.
- Predictions are explained by dependency set and bottleneck list.
- The system proposes action options with expected tradeoffs.

### 4.4 Implementation scope

- Add plan simulator using existing planning model structures.
- Add dependency-bottleneck scoring for early warning.
- Add schedule-adjustment suggestions as artifacts with confidence and assumptions.
- Integrate with continuity/watchdog to avoid churn during false positives.

### 4.5 Phase 8 acceptance

- 3 plan templates produce confidence-calibrated forecasts with p90 error bounds.
- Critical-path recovery recommendations include owners and ETA.
- Risk thresholds and actions are logged in machine-parseable schema.

---

## 5. Phase 9: Productized Operations and Ecosystem Extension

### 5.1 Functional requirements (new FRs)

| FR-ID | Requirement | Acceptance criteria |
|---|---|---|
| FR-063 | Operation-level command surface | New ops commands for analysis/review/reprovision/replay use consistent operation schema with typed inputs. |
| FR-064 | Explainability stack for long tasks | Three levels of explanation: summary, detail, deep trace are available from the same source of truth. |
| FR-065 | Universal operation portability | Operation-level wrappers can invoke zen-style tool patterns (`analyze`, `audit`, `debug`, `test`, `trace`) in a normalized envelope. |
| FR-066 | Confidence-and-risk policy for autonomous modes | The system escalates to human for low-confidence or high-risk transitions. |
| FR-067 | What-if replay sandbox | Operators can simulate alternative strategies on open runs without mutating state. |
| FR-068 | Long-run continuity quality gate | Handoff summary requires explicit owner acceptance and snapshot completeness. |

### 5.2 Non-functional requirements (new NFRs)

| NFR-ID | Requirement | Target |
|---|---|---|
| NFR-025 | UX responsiveness | Progressive disclosure updates <= 150 ms local render, full trace <= 800 ms |
| NFR-026 | Replay safety | Replay never mutates production state without explicit approval mode. |
| NFR-027 | Tool portability | Operation invocation payload passes schema validation 99.8%+ |
| NFR-028 | Explainability quality | 95% of escalations include confidence rationale and source evidence link. |

### 5.3 Implementation scope

- Add `observe`, `plan`, `replay`, and `simulate` operations with typed input contracts.
- Add explainability registry and stable schema IDs for output blocks.
- Extend UI/CLI surfaces to expose operation recommendations with explicit confidence, owner, and reversibility.
- Add handoff acceptance enforcement in workflow continuation.

### 5.4 Phase 9 acceptance

- No production state mutation from replay mode.
- 100% of simulated alternatives produce deterministic audit trails.
- Operators can generate and export continuity brief in one click per open critical run.

---

## 6. Test and evidence model

### 6.1 Unit test classes by phase

| Phase | Suggested classes |
|---|---|
| 7 | `TestContractNegotiation`, `TestParserPartialState`, `TestSemanticValidation`, `TestFallbackConfidence`, `TestDualReadWrite` |
| 8 | `TestRiskForecast`, `TestDependencyBottlenecks`, `TestRescheduleSuggestions`, `TestSurgeWatchdog` |
| 9 | `TestOperationsContracts`, `TestExplainabilityLayers`, `TestReplaySafety`, `TestContinuityHandoff` |

### 6.2 Integration test classes by phase

| Phase | Suggested classes |
|---|---|
| 7 | `TestRuntimeCanaryMigration`, `TestContractHealthDrift`, `TestAdapterConformance` |
| 8 | `TestPredictiveIntervention`, `TestPlanRiskPlaybook`, `TestContinuousImprovementLoop` |
| 9 | `TestOperatorFlow`, `TestWhatIfReplayFlow`, `TestModeEscalationPolicy` |

### 6.3 Evidence artifacts required

- `docs/closure/PHASE7_MIGRATION_SMOKE_TESTS.md`
- `artifacts/contracts/contract-negotiation-matrix.ndjson`
- `artifacts/planning/risk-profile.ndjson`
- `artifacts/ops/what-if-replay-cases.ndjson`

---

## 7. Delivery model (chunkable)

1. Chunk A: Contract negotiation + schema registry + parser state safeguards.
2. Chunk B: Semantic validation + conformance suite + drift observability.
3. Chunk C: Migration controller + policy gates + rollback simulation.
4. Chunk D: Risk simulation and proactive reschedule suggestions.
5. Chunk E: Predictive intervention policy + surge watcher integration.
6. Chunk F: Universal operations + explainability + replay safety.
7. Chunk G: End-to-end PRD-to-WBS closure and readiness review.

Each chunk can be scheduled independently with acceptance checks and merge gates.

---

## 8. Open question bank (for phase handoff)

- Should namespace versioning be strictly semantic (`v2`, `v2.1`) or capability-based (`v-xml`, `v-json`)?
- Should replay simulations remain in separate storage or reuse the event log with immutability markers?
- What are the threshold bands for escalation between “stale confidence” and “human escalation required”?
- Which operator persona can own continuous cost optimization actions: SRE, product, or policy?

---

## 9. PRD references and dependency mapping

- Upstream architectural basis: `docs/docset/thegent-prd-final.md`
- Closure state: `docs/closure/PHASE6_READINESS_REPORT.md`
- Existing governance and contract context: `docs/docset/thegent-cross-analysis-matrix-2026-02-14.md`
- Plan and WBS anchors: `docs/docset/thegent-plan-final-index.md`


---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index
