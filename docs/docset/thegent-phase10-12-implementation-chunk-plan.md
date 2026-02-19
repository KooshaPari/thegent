# Thegent Phase 10–12 Implementation Chunk Plan

**Status:** Finalized chunk execution plan  
**Date:** 2026-02-15  
**Scope:** Convert Phase 10–12 addendum artifacts into execution chunks with deterministic handoff outputs.

This plan maps the new PRD/WBS/DAG/Test pack for Phases 10–12 into 6 execution chunks with explicit entry criteria, owners, dependencies, and exit conditions.

---

## 1) Execution model

- **Mode:** Chunked, evidence-first implementation.
- **Rule:** No chunk exits complete without:
  - required unit/integration tests,
  - required artifacts written,
  - gate decision note for dependent gates.
- **Default ownership pattern:** Parallelizable WPs by domain where dependencies permit.

### 1.1 Governing quality bars

- **Mandatory evidence:** each chunk must leave at least:
  - 1 evidence artifact in the matching phase folder,
  - 1 passing gate-precondition checklist,
  - 1 updated owner decision log entry.
- **Gate sequencing:** `G10` must pass before any control-plane runtime changes from Phase 11 are enabled.
- **Change control:** any control parameter change without rollback path is rejected in PR review.

## 2) Chunk A — Interface foundation and deterministic dispatch (Phase 10: WP-10001 → WP-10003, WP-10006)

### 2.1 Scope
- Define operation envelope v2 (`WP-10001`).
- Stand up capability registry and bootstrap (`WP-10002`).
- Implement core deterministic dispatch resolver (`WP-10003`).
- Add unknown-op migration suggestions (`WP-10006`).

### 2.2 Deliverables
- `thegent-phase10-12-draft/contracts/operation_envelope_v2.json` (or equivalent schema artifact).
- Deterministic dispatch traces for CLI and MCP invocations.
- Compatibility responses with migration hints.

### 2.3 Test set
- `TestOperationEnvelopeV2Schema`
- `TestCapabilityRegistryService`
- `TestDispatchDeterminism`
- `TestMigrationHintRenderer`
- `TestEnvelopeToDispatchEndToEnd`

### 2.4 Exit criteria
- G10 precondition satisfied:
  - interface parity established,
  - unknown-op events include migration context,
  - no critical unhandled operation path in canary smoke.

## 3) Chunk B — Trust and conformance control (Phase 10: WP-10004 → WP-10010)

### 3.1 Scope
- Adapter trust policy and deny-by-default behavior for critical lanes (`WP-10004`).
- Endpoint consolidation and operation alias parity (`WP-10005`).
- Dispatch trace/audit context persistence (`WP-10007`).
- Plugin registration + conformance lifecycle (`WP-10008`).
- Compatibility matrix and migration CLI (`WP-10009`).
- Operator operations documentation bundle (`WP-10010`).

### 3.2 Deliverables
- Adapter trust manifests and policy checks in runtime.
- Conformance gating path for adapters.
- Dispatch trace schema + operator guide.

### 3.3 Test set
- `TestAdapterTrustPolicy`
- `TestOperationSurfaceConsolidation`
- `TestDispatchTraceEvent`
- `TestAdapterConformanceLifecycle`
- `TestCompatibilityMatrixPolicy`
- `TestUnknownOperationFlow`
- `TestOperationsDocsGeneration`

### 3.4 Exit criteria
- All phase-10 evidence artifacts produced and signed.
- Traceability query returns immutable dispatch rows with reason context.

## 4) Chunk C — Autonomous control baseline (Phase 11: WP-11001 → WP-11005)

### 4.1 Scope
- SLO regulator and control graph (`WP-11001`).
- Forecast engine and calibration checks (`WP-11002`, `WP-11003`).
- Preemptive saturation policies (`WP-11004`).
- Self-healing suggestion ranking engine (`WP-11005`).

### 4.2 Deliverables
- Closed-loop control with no unstable actions under simulation.
- Forecast/prediction event stream and calibration dashboard.

### 4.3 Test set
- `TestSLORegulator`
- `TestForecastEngineRun`
- `TestCalibrationDrift`
- `TestPreemptiveSaturationPolicy`
- `TestSelfHealRecommendation`
- `TestForecastLoopIntegration`

### 4.4 Exit criteria
- G11 conditions pass in canary:
  - oscillation controls verified,
  - auto-suggestion includes owner + rollback evidence,
  - evidence pack generated.

## 5) Chunk D — Predictive continuity and controlled adaptation (Phase 11: WP-11006 → WP-11010)

### 5.1 Scope
- Task shaping (`WP-11006`) and continuity risk prediction (`WP-11007`).
- Learning loop with policy guardrails (`WP-11008`).
- Safe-mode governance (`WP-11009`).
- Phase 11 evidence pack (`WP-11010`).

### 5.2 Deliverables
- Predictive continuity safeguards before high-stake shift windows.
- Controlled adaptation with explicit rollback manifests.

### 5.3 Test set
- `TestAdaptiveTaskShaping`
- `TestContinuityRiskPredictor`
- `TestLearningLoopGovernance`
- `TestSafeModeGovernance`
- `TestEvidencePackEmit11`
- `TestSelfHealControlFlow`
- `TestReshapeUnderSurge`

### 5.4 Exit criteria
- G11 fully marked pass:
  - continuity risk alerts before predicted break,
  - policy-approved adaptation updates only,
  - safe-mode paths reversible with audit trail.

## 6) Chunk E — Explainability and replay hardening (Phase 12: WP-12001 → WP-12006)

### 6.1 Scope
- Explainability schema contract and rendering (`WP-12001`).
- Fatigue/noise controls (`WP-12002`).
- Replay sandbox isolation (`WP-12003`).
- What-if branch governance (`WP-12004`).
- Continuity confidence gate (`WP-12005`).
- Evidence graph packager (`WP-12006`).

### 6.2 Deliverables
- Stable explanation contract across summary/detail/trace.
- Replay remains read-only by default.
- Evidence graph with edge-complete manifest.

### 6.3 Test set
- `TestExplainabilityContract`
- `TestFatigueControlRules`
- `TestReplaySandboxMutationGuard`
- `TestWhatIfBranchEngine`
- `TestHandoffConfidenceGate`
- `TestEvidenceGraphPackaging`
- `TestExplainabilityReplayIntegration`

### 6.4 Exit criteria
- Replay safety and explanation consistency proven in integration smoke.
- Evidence package can be exported and re-hydrated.

## 7) Chunk F — Persona, packaging, and final closure (Phase 12: WP-12007 → WP-12010)

### 7.1 Scope
- Persona profiles and access constraints (`WP-12007`).
- Operational learning assets (`WP-12008`).
- Release pack compiler (`WP-12009`).
- Closure/handoff note and finality (`WP-12010`).

### 7.2 Deliverables
- Persona-aware action constraints and operation templates.
- One-command PRD/WBS/test pack release artifact compiler.
- Final signed closure artifact (`phase10-12_finality_bundle`).

### 7.3 Test set
- `TestPersonaProfiles`
- `TestLearningAssetGeneration`
- `TestReleasePackCompiler`
- `TestPhase10to12Finality`
- `TestPersonaAndReadinessGate`

### 7.4 Exit criteria
- G12 pass:
  - explainability/replay/escaltation gates validated,
  - packaging deterministic and checksummed,
  - final artifact inventory complete.

## 8) End-to-end sequencing (recommended)

1. Chunk A + Chunk B (Phase 10 foundation and trust).
2. Chunk C + Chunk D (Phase 11 autonomous control hardening).
3. Chunk E + Chunk F (Phase 12 hardening and closure).
4. Final synthesis: update `thegent-plan-final-index.md` and all phase cross-references.

## 9) Expanded chunk definitions (production cadence)

### 9.1 Chunk A detailed exit criteria

- **Pre-req:** WP-10001 design approved, registry schema draft and adapter audit list available.
- **Implementation scope:** WP-10001, WP-10002, WP-10003, WP-10006.
- **Parallelizable in-chunk:** CLI route parser, MCP adapter wrappers, schema unit fixtures.
- **Exit artifacts:**
  - `artifacts/phase10/chunk_a/dispatch_path_hash_examples.ndjson`
  - `artifacts/phase10/chunk_a/compatibility_hints_examples.ndjson`
  - Signed chunk evidence note (`chunk_a_evidence_v1.md`).

### 9.2 Chunk B detailed exit criteria

- **Pre-req:** Chunk A pass, G10 pre-checks visible.
- **Implementation scope:** WP-10004, WP-10005, WP-10007, WP-10008, WP-10009, WP-10010.
- **Parallelizable in-chunk:** Governance policy module + adapter test fixtures.
- **Exit artifacts:**
  - `artifacts/phase10/chunk_b/trust_policy_denylist.ndjson`
  - `artifacts/phase10/chunk_b/adapter_conformance_reports.ndjson`
  - `artifacts/phase10/chunk_b/operations_coverage_matrix.ndjson`
  - Signed chunk evidence note (`chunk_b_evidence_v1.md`).

### 9.3 Chunk C detailed exit criteria

- **Pre-req:** WP-11001 architecture review complete.
- **Implementation scope:** WP-11001, WP-11002, WP-11003, WP-11004, WP-11005.
- **Parallelizable in-chunk:** Forecast service + SLO telemetry + ranking engine.
- **Exit artifacts:**
  - `artifacts/phase11/chunk_c/control_event_window.ndjson`
  - `artifacts/phase11/chunk_c/calibration_audit.ndjson`
  - `artifacts/phase11/chunk_c/self_heal_runbook.ndjson`
  - Signed chunk evidence note (`chunk_c_evidence_v1.md`).

### 9.4 Chunk D detailed exit criteria

- **Pre-req:** Chunk C pass and safe-mode policy model approved.
- **Implementation scope:** WP-11006, WP-11007, WP-11008, WP-11009, WP-11010.
- **Exit artifacts:**
  - `artifacts/phase11/chunk_d/task_shaping_examples.ndjson`
  - `artifacts/phase11/chunk_d/continuity_predictions.ndjson`
  - `artifacts/phase11/chunk_d/learning_guard_events.ndjson`
  - `artifacts/phase11/chunk_d/g11_gate_evidence.ndjson`
  - `artifacts/phase11/chunk_d/signed_chunk_evidence.md`

### 9.5 Chunk E detailed exit criteria

- **Pre-req:** Phase 11 gates marked pass for runtime safety; explainability spec reviewed.
- **Implementation scope:** WP-12001, WP-12002, WP-12003, WP-12004, WP-12005, WP-12006.
- **Exit artifacts:**
  - `artifacts/phase12/chunk_e/explanation_contract_examples.ndjson`
  - `artifacts/phase12/chunk_e/replay_safety_matrix.ndjson`
  - `artifacts/phase12/chunk_e/handoff_risk_log.ndjson`
  - `artifacts/phase12/chunk_e/evidence_graph.ndjson`
  - `artifacts/phase12/chunk_e/g12_precheck_notes.md`

### 9.6 Chunk F detailed exit criteria

- **Pre-req:** Explainability and replay controls pass smoke.
- **Implementation scope:** WP-12007, WP-12008, WP-12009, WP-12010.
- **Exit artifacts:**
  - `artifacts/phase12/chunk_f/persona_contract_snapshot.ndjson`
  - `artifacts/phase12/chunk_f/learning_assets_checklist.ndjson`
  - `artifacts/phase12/chunk_f/release_pack_manifest.ndjson`
  - `artifacts/phase12/chunk_f/phase10_12_finality_pack.md`

## 10) Suggested staffing plan per chunk

| Chunk | Team | Roles | Cadence |
|---|---|---|---|
| A/B | 2 backend, 1 API, 1 QA | parser/schema, registry, dispatch, conformance | 5 days each |
| C/D | 1 SRE, 1 platform, 1 governance, 1 QA | controller/forecast/continuity controls | 10 days combined |
| E/F | 1 UX, 1 backend, 1 docs, 1 security | explainability/replay/packaging/compliance | 8 days combined |

## 11) Hard stop conditions

- Skip/abort a chunk only when:
  1) critical production control regression is observed,
  2) gate evidence is incomplete,
  3) rollback path not validated.
- If hard stop occurs, return to previous stable gate and reopen PRD addendum diff for owner signoff.

## 9) Cross-cutting controls across all chunks

- Never merge adaptive control behavior until G10 is green.
- Enforce schema compatibility checks before any operation execution on canary.
- Keep all new command surfaces under existing CLI/MCP parity checks.
- Keep release artifacts generated as machine-readable NDJSON plus markdown summaries.


---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index

