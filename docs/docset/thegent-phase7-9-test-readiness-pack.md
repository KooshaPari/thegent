# Thegent Phase 7–9 Test and Readiness Pack

**Status:** Draft
**Date:** 2026-02-15
**Scope:** Concrete test matrix and evidence checklist for PRD phases 7–9.

## 1) Test philosophy for Phase 7–9

The test pack remains compatible with the existing chunking approach:

- Unit tests enforce deterministic behavior in parser, negotiation, and contract handling.
- Integration tests validate end-to-end contracts across CLI, MCP, and artifact outputs.
- Resilience tests validate prediction and adaptation behavior under pressure.
- Governance tests validate evidence completeness and escalation readiness.

## 2) Phase 7 test matrix

### 2.1 Unit tests

| WP | Test class | Focus | Expected outcome |
|---|---|---|---|
| WP-7001 | `TestContractNegotiationUnit` | Supported version exchange and fallback logic | Highest compatible version selected; unsupported versions produce explicit errors |
| WP-7002 | `TestContractNamespaceRegistry` | Registry lookup and metadata shape | Stable response with compatibility matrix |
| WP-7003 | `TestStreamingParserStateMachine` | incremental chunk acceptance behavior | Partial chunks stored only in checkpoint, no false final states |
| WP-7004 | `TestParserCheckpointRecovery` | commit guard and resume rules | Failed chunk does not replay side effects |
| WP-7005 | `TestSemanticInvariantValidator` | cross-field + phase constraints | Invalid status/action combinations blocked |
| WP-7007 | `TestFallbackConfidenceScoring` | confidence penalty path and event emission | Explicit penalty score with reason and path |
| WP-7008 | `TestDualReadWriteController` | migration window and version reads/writes | Both versions written and readable in dual mode |
| WP-7009 | `TestContractHealthAggregation` | drift and trend calculations | Deterministic trend payload and owner labels |
| WP-7010 | `TestContractDriftGate` | gate logic and critical escalation | Gate denies critical lane on unresolved drift |

### 2.2 Integration tests

| WP | Test class | Focus | Expected outcome |
|---|---|---|---|
| WP-7001 / WP-7002 | `TestNegotiationEndToEnd` | CLI and MCP negotiation path | Contract metadata appears in CLI/MCP responses |
| WP-7003 / WP-7004 | `TestParserWithMalformedChunks` | mixed chunk quality in real stream | Partial parse returns confidence warning and safe continue/abort behavior |
| WP-7005 / WP-7006 | `TestConformanceAndValidation` | adapter outputs through semantic checks | Invalid provider payload blocked with machine-readable issue |
| WP-7008 / WP-7010 | `TestMigrationSimulation` | full migration canary sequence | 1% -> 5% -> 25% -> 100% path with telemetry |

### 2.3 Phase 7 evidence and artifacts

- `docs/closure/WP7001_NEGOTIATION_SMOKE.md`
- `artifacts/contracts/contract_compat_matrix.ndjson`
- `artifacts/contracts/phase7_parser_health.ndjson`
- `artifacts/contracts/phase7_drift_gates.ndjson`

## 3) Phase 8 test matrix

### 3.1 Unit tests

| WP | Test class | Focus | Expected outcome |
|---|---|---|---|
| WP-8001 | `TestPlanGraphExtraction` | dependency graph extraction from WBS plans | Deterministic graph IDs and edge lists |
| WP-8002 | `TestPertMonteCarlo` | distribution and confidence band correctness | p50/p80/p95 stable and bounded |
| WP-8003 | `TestBottleneckScoring` | zero-slack and high-dependency detection | Predictable bottleneck classification |
| WP-8004 | `TestRescheduleAdvisor` | recommendation confidence and assumptions | Recommendation includes ETA + confidence + rationale |
| WP-8005 | `TestContinuityRiskModel` | stale ownership and handoff risk scoring | Alerts raised at defined thresholds |
| WP-8006 | `TestSurgePredictor` | surge classifier and action mapping | Consistent safe-mode entry under synthetic pressure |
| WP-8007 | `TestAdaptiveBudgetControls` | deferral and throttle logic | Non-critical deferral with explainable rationale |
| WP-8008 | `TestSimulationRunbook` | replay of what-if runbooks | Simulation output references expected changes |
| WP-8009 | `TestInterventionPolicy` | escalation thresholds and routing | Safe path escalation with owner + evidence |
| WP-8010 | `TestForecastCalibration` | calibration curve and drift check | Forecast quality remains within policy bounds |

### 3.2 Integration tests

| WP | Test class | Focus | Expected outcome |
|---|---|---|---|
| WP-8001 / WP-8002 / WP-8010 | `TestForecastPipeline` | end-to-end planning simulation flow | Forecast appears in runtime event stream |
| WP-8005 / WP-8007 | `TestContinuityUnderSurge` | ownership and load pressure resilience | Safe-mode avoids starvation of critical lane |
| WP-8008 / WP-8009 | `TestRunbookIntervention` | full remediation path simulation | Runbook executes non-destructive suggestion previews |

### 3.3 Phase 8 evidence and artifacts

- `artifacts/planning/phase8_forecast_report.ndjson`
- `artifacts/planning/phase8_bottlenecks.ndjson`
- `artifacts/planning/phase8_interventions.ndjson`
- `artifacts/planning/phase8_calibration.ndjson`

## 4) Phase 9 test matrix

### 4.1 Unit tests

| WP | Test class | Focus | Expected outcome |
|---|---|---|---|
| WP-9001 | `TestOperationProtocolSchema` | typed operations and request payloads | Invalid operations fail early with schema errors |
| WP-9002 | `TestExplainabilityLevels` | summary/detail/trace consistency | Single source of truth across three levels |
| WP-9003 | `TestReplaySandboxIsolation` | no mutable paths when in replay mode | Replay remains read-only by default |
| WP-9004 | `TestHandoffConfirmation` | owner acknowledgment and snapshot completeness | Workflow blocked until confirmation recorded |
| WP-9005 | `TestUniversalAdapterMapper` | adapter wrapping for operation families | Mapped tool responses follow contract |
| WP-9006 | `TestWhatIfSimulation` | branching scenario generation | Alternative timelines and diffs computed |
| WP-9007 | `TestEscalationByConfidence` | policy thresholds for escalation | Low-confidence transitions always escalate |
| WP-9008 | `TestFallbackControlsSafety` | UI/CLI action visibility and preconditions | Controls visible and require confirmation |
| WP-9009 | `TestEvidenceLinkage` | cross-link closure/evidence IDs | Evidence IDs are present in replay and action logs |
| WP-9010 | `TestPhase7To9ReadinessDocs` | documentation and training completeness checks | Docs present and machine-parseable |

### 4.2 Integration tests

| WP | Test class | Focus | Expected outcome |
|---|---|---|---|
| WP-9001 / WP-9002 / WP-9003 | `TestOpsFlowEndToEnd` | observe/plan/replay pipeline with schema checks | Operation flow returns deterministic event IDs |
| WP-9004 / WP-9008 | `TestContinuityHandoffFlow` | handoff + fallback controls | Blocked handoff prevents unsafe continuation |
| WP-9006 / WP-9007 | `TestWhatIfEscalationFlow` | policy + simulation + escalation output | Escalation reasons appear and are acted on |
| WP-9009 / WP-9010 | `TestReadinessFinalReview` | artifacts + onboarding + signoff data | Review pack builds without manual edits |

### 4.3 Phase 9 evidence and artifacts

- `artifacts/ops/operation_protocol_report.ndjson`
- `artifacts/ops/explainability_matrix.ndjson`
- `artifacts/ops/replay_audit.ndjson`
- `artifacts/ops/handoff_guard_audit.ndjson`

## 5) Readiness gates for implementation sprint

### 5.1 Gate M7

- No unresolved critical drift in contract health.
- Parser downgrade events have explicit operator visibility.
- Dual-read/write rollback rehearsal completed.

### 5.2 Gate M8

- Forecast calibration baseline established.
- No unplanned safe-mode oscillation events for critical lanes.
- Intervention policy outputs include owner + assumption + rollback path.

### 5.3 Gate M9

- Replay path audit is read-only by default.
- Explainability and confidence are present for all high-risk actions.
- Evidence links are complete for all Phase 9 WPs.

## 6) Recommended execution chunking

- **Chunk 1:** Build and validate phases 7001–7004, with unit/integration gates.
- **Chunk 2:** Add phases 7005–7010, plus phase health and drift alert tests.
- **Chunk 3:** Implement phases 8001–8010, plus forecast/risk tests.
- **Chunk 4:** Implement phases 9001–9010, operator-facing schema + replay safety.
- **Chunk 5:** Build final phase 7–9 readiness pack and conduct full gate review.



---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index
