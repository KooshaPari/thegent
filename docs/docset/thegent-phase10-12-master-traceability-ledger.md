# Thegent Phase 10–12 Master Traceability Ledger

**Status:** Master operational ledger for implementation handoff  
**Date:** 2026-02-15  
**Scope:** Full cross-source traceability for `WP-10001` → `WP-12010` across PRD, WBS, DAG, test plan, seed, and issue states.

Use this as the final execution control plane before and during bundle handoffs.

---

## 1) Canonical key sets

### 1.1 FR/NFR references
- PRD FR range: `FR-069`..`FR-090` from `thegent-phase10-12-optimal-design-prd.md`
- NFR range: `NFR-029`..`NFR-040` from `thegent-phase10-12-optimal-design-prd.md`

### 1.2 Source-of-truth documents
- `thegent-wbs-phase10-12.md`
- `thegent-dag-phase10-12-extension.md`
- `thegent-phase10-12-prd-wbs-crossmap-finalization.md`
- `thegent-phase10-12-test-readiness-pack.md`
- `thegent-phase10-12-implementation-issue-queue.md`
- `thegent-phase10-12-issue-board-seed.json`
- `thegent-phase10-12-execution-bundles-playbook.md`
- `thegent-phase10-12-closure-readiness-pack-template.md`

### 1.3 Ledger status states
- `PLANNED` / `BLOCKED` / `IN_PROGRESS` / `REVIEW` / `READY_FOR_GATE` / `DONE`

---

## 2) Master ledger: WP → FR → DAG → tracker

| WP | Phase | Bundle | Owner | FR IDs | NFR IDs | DAG node(s) | Issue key | Required tests | Required artifacts | Gate precondition | Dependencies | Rollback token | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| WP-10001 | 10 | phase10_bundle_b | Platform | FR-069 | NFR-029 | N10001 | THEGENT-WP-10001 | TestOperationEnvelopeV2Schema | artifacts/phase10/operation_envelope_v2.ndjson | requires-g10-pre | WP-9001 | rt-phase10-b-10001 | PLANNED |
| WP-10002 | 10 | phase10_bundle_b | Platform | FR-070 | NFR-029 | N10002 | THEGENT-WP-10002 | TestCapabilityRegistryService | artifacts/phase10/capability_registry_service.ndjson | requires-g10-pre | WP-10001 | rt-phase10-b-10002 | PLANNED |
| WP-10003 | 10 | phase10_bundle_b | Core Runtime | FR-071,FR-072 | NFR-030 | N10003 | THEGENT-WP-10003 | TestDispatchDeterminism, TestEnvelopeToDispatchEndToEnd | artifacts/phase10/dispatch_graph_pathing.ndjson | requires-g10 | WP-10001,WP-10002 | rt-phase10-b-10003 | PLANNED |
| WP-10004 | 10 | phase10_bundle_b | Security/Governance | FR-032 | NFR-032 | N10004 | THEGENT-WP-10004 | TestAdapterTrustPolicy | artifacts/phase10/chunk_b/adapter_trust_gate.ndjson | requires-g10 | WP-10002 | rt-phase10-b-10004 | PLANNED |
| WP-10005 | 10 | phase10_bundle_b | Platform/API | FR-071 | NFR-029 | N10005 | THEGENT-WP-10005 | TestOperationSurfaceConsolidation | artifacts/phase10/chunk_b/operation_coverage_matrix.ndjson | requires-g10-pre | WP-10003 | rt-phase10-b-10005 | PLANNED |
| WP-10006 | 10 | phase10_bundle_b | UX/Core Runtime | FR-074 | NFR-031 | N10006 | THEGENT-WP-10006 | TestMigrationHintRenderer | artifacts/phase10/chunk_b/unknown_operation_hints.ndjson | requires-g10-pre | WP-10003 | rt-phase10-b-10006 | PLANNED |
| WP-10007 | 10 | phase10_bundle_b | Governance | FR-072,FR-075 | NFR-035 | N10007 | THEGENT-WP-10007 | TestDispatchTraceEvent | artifacts/phase10/chunk_b/dispatch_trace_schema.ndjson | requires-g10 | WP-10003,WP-10004,WP-10005 | rt-phase10-b-10007 | PLANNED |
| WP-10008 | 10 | phase10_bundle_b | Platform Arch | FR-073 | NFR-032 | N10008 | THEGENT-WP-10008 | TestAdapterConformanceLifecycle | artifacts/phase10/chunk_b/plugin_conformance_reports.ndjson | requires-g10 | WP-10002,WP-10007 | rt-phase10-b-10008 | PLANNED |
| WP-10009 | 10 | phase10_bundle_b | API/Docs | FR-070,FR-074 | NFR-031 | N10009 | THEGENT-WP-10009 | TestCompatibilityMatrixPolicy | artifacts/phase10/chunk_b/compatibility_matrix.ndjson | requires-g10 | WP-10001,WP-10003 | rt-phase10-b-10009 | PLANNED |
| WP-10010 | 10 | phase10_bundle_b | Docs | FR-083? | NFR-029 | N10010 | THEGENT-WP-10010 | TestOperationsDocsGeneration | artifacts/phase10/chunk_b/operations_ops_guide.ndjson | requires-g10 | WP-10003,WP-10005,WP-10009 | rt-phase10-b-10010 | PLANNED |
| WP-11001 | 11 | phase11_bundle_c | SRE/Ops | FR-076 | NFR-034 | N11001 | THEGENT-WP-11001 | TestSLORegulator | artifacts/phase11/chunk_c/slo_regulator_events.ndjson | requires-g11-pre,requires-g10 | WP-10003,WP-10007 | rt-phase11-c-11001 | PLANNED |
| WP-11002 | 11 | phase11_bundle_c | Data/Planning | FR-077 | NFR-033 | N11002 | THEGENT-WP-11002 | TestForecastEngineRun | artifacts/phase11/chunk_c/forecast_quality.ndjson | requires-g11-pre,requires-g10 | WP-11001 | rt-phase11-c-11002 | PLANNED |
| WP-11003 | 11 | phase11_bundle_c | QA/Governance | FR-077 | NFR-036 | N11003 | THEGENT-WP-11003 | TestCalibrationDrift | artifacts/phase11/chunk_c/calibration_drift.ndjson | requires-g11-pre,requires-g10 | WP-11002 | rt-phase11-c-11003 | PLANNED |
| WP-11004 | 11 | phase11_bundle_c | Core Routing | FR-078 | NFR-034 | N11004 | THEGENT-WP-11004 | TestPreemptiveSaturationPolicy | artifacts/phase11/chunk_c/preemption_policy_events.ndjson | requires-g11-pre,requires-g10 | WP-11001,WP-11002 | rt-phase11-c-11004 | PLANNED |
| WP-11005 | 11 | phase11_bundle_c | Governance/Product | FR-079 | NFR-035 | N11005 | THEGENT-WP-11005 | TestSelfHealRecommendation | artifacts/phase11/chunk_c/self_heal_recommendations.ndjson | requires-g11-pre,requires-g10 | WP-11003,WP-11004 | rt-phase11-c-11005 | PLANNED |
| WP-11006 | 11 | phase11_bundle_d | Orchestration | FR-080 | NFR-034 | N11006 | THEGENT-WP-11006 | TestAdaptiveTaskShaping | artifacts/phase11/chunk_d/adaptive_shaping.ndjson | requires-g11 | WP-11004,WP-11005 | rt-phase11-d-11006 | PLANNED |
| WP-11007 | 11 | phase11_bundle_d | SRE/Product | FR-081 | NFR-034 | N11007 | THEGENT-WP-11007 | TestContinuityRiskPredictor | artifacts/phase11/chunk_d/continuity_predictions.ndjson | requires-g11 | WP-11006 | rt-phase11-d-11007 | PLANNED |
| WP-11008 | 11 | phase11_bundle_d | Governance | FR-082 | NFR-036 | N11008 | THEGENT-WP-11008 | TestLearningLoopGovernance | artifacts/phase11/chunk_d/learning_loop.ndjson | requires-g11 | WP-11003,WP-11007 | rt-phase11-d-11008 | PLANNED |
| WP-11009 | 11 | phase11_bundle_d | Security | FR-076? (safety) | NFR-034 | N11009 | THEGENT-WP-11009 | TestSafeModeGovernance | artifacts/phase11/chunk_d/safe_mode_governance.ndjson | requires-g11 | WP-11008 | rt-phase11-d-11009 | PLANNED |
| WP-11010 | 11 | phase11_bundle_d | QA/Docs | FR-077 | NFR-034 | N11010 | THEGENT-WP-11010 | TestEvidencePackEmit11 | artifacts/phase11/chunk_d/g11_readiness_pack.ndjson | requires-g11 | WP-11001,WP-11002,WP-11005,WP-11008,WP-11009 | rt-phase11-d-11010 | PLANNED |
| WP-12001 | 12 | phase12_bundle_e | Product/UX | FR-083 | NFR-037 | N12001 | THEGENT-WP-12001 | TestExplainabilityContract | artifacts/phase12/chunk_e/explanation_contract_examples.ndjson | requires-g11 | WP-11010 | rt-phase12-e-12001 | PLANNED |
| WP-12002 | 12 | phase12_bundle_e | SRE | FR-084 | NFR-039 | N12002 | THEGENT-WP-12002 | TestFatigueControlRules | artifacts/phase12/chunk_e/fatigue_controls.ndjson | requires-g11 | WP-12001 | rt-phase12-e-12002 | PLANNED |
| WP-12003 | 12 | phase12_bundle_e | Core Runtime | FR-085 | NFR-039 | N12003 | THEGENT-WP-12003 | TestReplaySandboxMutationGuard | artifacts/phase12/chunk_e/replay_safety.ndjson | requires-g12-pre | WP-12001 | rt-phase12-e-12003 | PLANNED |
| WP-12004 | 12 | phase12_bundle_e | Product/Governance | FR-085 | NFR-039 | N12004 | THEGENT-WP-12004 | TestWhatIfBranchEngine | artifacts/phase12/chunk_e/what_if_branching.ndjson | requires-g12-pre | WP-12003 | rt-phase12-e-12004 | PLANNED |
| WP-12005 | 12 | phase12_bundle_e | Governance/UX | FR-086 | NFR-035 | N12005 | THEGENT-WP-12005 | TestHandoffConfidenceGate | artifacts/phase12/chunk_e/handoff_continuity.ndjson | requires-g11,requires-g12-pre | WP-12003,WP-12004 | rt-phase12-e-12005 | PLANNED |
| WP-12006 | 12 | phase12_bundle_e | Compliance | FR-087 | NFR-040 | N12006 | THEGENT-WP-12006 | TestEvidenceGraphPackaging | artifacts/phase12/chunk_e/evidence_graph.ndjson | requires-g11,requires-g12-pre | WP-12005 | rt-phase12-e-12006 | PLANNED |
| WP-12007 | 12 | phase12_bundle_f | Product/Security | FR-089 | NFR-040 | N12007 | THEGENT-WP-12007 | TestPersonaProfiles | artifacts/phase12/chunk_f/persona_profiles.ndjson | requires-g12 | WP-12005 | rt-phase12-f-12007 | PLANNED |
| WP-12008 | 12 | phase12_bundle_f | Documentation | FR-089 | NFR-037 | N12007 | THEGENT-WP-12008 | TestLearningAssetGeneration | artifacts/phase12/chunk_f/operational_learning_assets.ndjson | requires-g12 | WP-12007 | rt-phase12-f-12008 | PLANNED |
| WP-12009 | 12 | phase12_bundle_f | Docs/Automation | FR-088,FR-090 | NFR-040 | N12009 | THEGENT-WP-12009 | TestReleasePackCompiler | artifacts/phase12/chunk_f/release_pack_summary.ndjson | requires-g12 | WP-12006,WP-12008 | rt-phase12-f-12009 | PLANNED |
| WP-12010 | 12 | phase12_bundle_f | Program lead | FR-090 | NFR-040 | N12010 | THEGENT-WP-12010 | TestPhase10to12Finality | artifacts/phase12/chunk_f/phase10_12_finality_bundle.md | requires-g10,requires-g11,requires-g12 | WP-12009,WP-11010 | rt-phase12-f-12010 | PLANNED |

## 3) Gate readiness ledger (by milestone)

### 3.1 G10 ledger

- Required WPs: `WP-10001`..`WP-10010`
- Hard dependencies: all bundle B preconditions and deterministic dispatch evidence
- Blocking failure patterns:
  - missing `dispatch_path_hash`
  - non-deterministic dispatch between CLI/MCP
  - trust/policy fields absent from trace

### 3.2 G11 ledger

- Required WPs: `WP-11001`..`WP-11010`
- Hard dependencies: G10 lock + `phase11.autotune` policy control acceptance
- Blocking failure patterns:
  - unresolved oscillation
  - control confidence bypass
  - unsafe parameter learning updates

### 3.3 G12 ledger

- Required WPs: `WP-12001`..`WP-12010`
- Hard dependencies: deterministic evidence graph + release pack reproducibility + no open L3 incidents
- Blocking failure patterns:
  - replay mutation
  - branch provenance missing
  - unresolved handoff confidence breaches

## 4) Master ledger machine format

### 4.1 JSON schema

```json
{
  "ledger_id": "phase10-12-master-traceability",
  "version": "1.0.0",
  "generated_on": "2026-02-15T00:00:00Z",
  "rows": [
    {
      "wp_id": "WP-10001",
      "phase": 10,
      "bundle": "phase10_bundle_b",
      "owner": "Platform",
      "fr_ids": ["FR-069"],
      "nfr_ids": ["NFR-029"],
      "dag_nodes": ["N10001"],
      "issue_key": "THEGENT-WP-10001",
      "required_tests": ["TestOperationEnvelopeV2Schema"],
      "required_artifacts": ["artifacts/phase10/operation_envelope_v2.ndjson"],
      "gate_preconditions": ["requires-g10-pre"],
      "dependencies": ["WP-9001"],
      "rollback_token": "rt-phase10-b-10001",
      "status": "PLANNED",
      "hard_stop_status": "NONE"
    }
  ]
}
```

### 4.2 CSV schema

`wp_id,phase,bundle,owner,fr_ids,nfr_ids,dag_nodes,issue_key,required_tests,required_artifacts,gate_preconditions,dependencies,rollback_token,status`

## 5) Execution rulebook for this ledger

- If a WP is not in `DONE` with complete tuple fields, downstream WPs must not move forward.
- If a dependency WP is `BLOCKED`, all dependents are blocked regardless of local completion.
- If any `required_artifacts` path is missing, that WP cannot be in `READY_FOR_GATE`.
- If `rollback_token` is missing for runtime-affecting WP, status cannot exceed `IN_PROGRESS`.

## 6) Ledger update workflow

1. Import seed and check for duplicate `issue_key`.
2. Validate every row has non-empty:
   - `issue_key`
   - `fr_ids` (or explicit reason for empty)
   - `required_tests`
   - `required_artifacts`
   - `gate_preconditions`
3. Update `status` based on board position and signed signoffs.
4. Produce per-gate snapshot:
   - `artifacts/phase10/ledger_g10_precheck.ndjson`
   - `artifacts/phase11/ledger_g11_precheck.ndjson`
   - `artifacts/phase12/ledger_g12_precheck.ndjson`
5. Export and attach to gate note:
   - `phase10_12_finality_bundle.md`

## 7) Acceptance criteria for ledger integrity

- 100% of rows have issue keys and rollback tokens.
- 100% of rows have at least one test and one artifact entry.
- 100% of phase-11 and phase-12 rows have cross-gate blockers represented as precondition lists.
- 0 unresolved soft dependency edges across different bundles.
- No duplicate issue ids.

## 8) Cross-reference checklist

- `thegent-phase10-12-prd-wbs-crossmap-finalization.md`
- `thegent-phase10-12-prd-wbs-dag-ticket-validation.md`
- `thegent-phase10-12-execution-synthesis-playbook.md`
- `thegent-phase10-12-bundle-signoff-and-handoff-packages.md`
- `thegent-phase10-12-release-readiness-and-delta-pack.md`
- `thegent-phase10-12-issue-board-seed.json`

## 9) One-line generation guidance

Treat this document as immutable for human review and generate an NDJSON ledger from:
- WBS rows,
- DAG node list,
- cross-map FR/NFR,
- seed ticket rows,
- and current issue-board status.

