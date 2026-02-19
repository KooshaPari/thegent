# Thegent Phase 10–12 Bundle Signoff and Handoff Packages

**Status:** Final operations package  
**Date:** 2026-02-15  
**Scope:** Bundle-level signoff, role-based accountability, and closure handoff evidence for Phases 10–12.

Use this package as the gating layer between planning and deployment. It should be completed before bundle closure and before moving to subsequent gate boundaries.

## 1) Purpose and scope

The package standardizes:

- what must be true for each bundle to transition forward,
- what artifacts and checks required for handoff,
- owner signoff format and timestamps,
- residual risk persistence requirements,
- rollback posture at bundle boundaries.

## 2) Bundle signoff model

Each bundle has four required handoff blocks:

1. **Technical lock** — all bundle WPs pass required tests and required artifacts exist.
2. **Safety lock** — hard-stop status clear (`L2/L3` not active unresolved).
3. **Governance lock** — gate preconditions explicitly signed by owners.
4. **Continuity lock** — downstream dependencies have acceptance copies and rollback plan.

No bundle can be marked `Bundle Complete` until all four locks are green.

## 3) Bundle B signoff package (Phase 10 trust/conformance)

### 3.1 Entry criteria

- `WP-10001` and `WP-10002` completed enough to support deterministic dispatch.
- `phase10_bundle_b` preconditions from `thegent-phase10-12-execution-bundles-playbook.md` met.
- `requires-g10-pre` not blocked.

### 3.2 Completion checklist

- [ ] WBS dependencies valid for all phase-10 WPs in bundle.
- [ ] `TestOperationSurfaceConsolidation`, `TestDispatchDeterminism`, `TestDispatchTraceEvent` passing (or waived with documented exception).
- [ ] Deterministic dispatch behavior validated in CLI and MCP parity suite.
- [ ] Unknown-op migration guidance exists for 100% unknown-case captures.
- [ ] Trust policy deny-by-default works for critical lanes.
- [ ] Evidence pack includes:
  - `artifacts/phase10/chunk_b/dispatch_trace_schema.ndjson`
  - `artifacts/phase10/chunk_b/unknown_operation_hints.ndjson`
  - `artifacts/phase10/chunk_b/compatibility_matrix.ndjson`
  - `artifacts/phase10/chunk_b/trust_policy_signoff.md`

### 3.3 Mandatory signoffs

- Platform lead
- Security lead
- Governance lead
- QA lead
- Program lead

## 4) Bundle C signoff package (Phase 11 control baseline)

### 4.1 Entry criteria

- Bundle B hard completion lock complete.
- `WP-11001` control baseline implementation complete.
- `phase11.autotune` allowed and documented.

### 4.2 Completion checklist

- [ ] `TestSLORegulator`, `TestForecastEngineRun`, `TestCalibrationDrift`, `TestSelfHealRecommendation` passing.
- [ ] No unresolved oscillation events in the latest 48h control window.
- [ ] Control actions carry confidence + rollback context.
- [ ] Forecast and control evidence can reproduce from deterministic seed.
- [ ] Evidence pack includes:
  - `artifacts/phase11/chunk_c/slo_regulator_events.ndjson`
  - `artifacts/phase11/chunk_c/forecast_quality.ndjson`
  - `artifacts/phase11/chunk_c/self_heal_recommendations.ndjson`

### 4.3 Mandatory signoffs

- SRE lead
- Product lead
- Governance lead
- Platform lead

## 5) Bundle D signoff package (Phase 11 adaptation governance)

### 5.1 Entry criteria

- Bundle C output stable in canary.
- `WP-11010` evidence path started or ready for dependency closure.

### 5.2 Completion checklist

- [ ] `TestAdaptiveTaskShaping`, `TestContinuityRiskPredictor`, `TestLearningLoopGovernance`, `TestSafeModeGovernance` passing.
- [ ] Continuity risk warnings trigger pre-shift checks by policy.
- [ ] Task shaping and safe-mode transitions are auditable and reversible.
- [ ] Evidence pack includes:
  - `artifacts/phase11/chunk_d/adaptive_shaping.ndjson`
  - `artifacts/phase11/chunk_d/continuity_predictions.ndjson`
  - `artifacts/phase11/chunk_d/learning_loop.ndjson`
  - `artifacts/phase11/chunk_d/safe_mode_governance.ndjson`

### 5.3 Mandatory signoffs

- Governance lead
- Security lead
- SRE lead
- Program lead

## 6) Bundle E signoff package (Phase 12 explainability and replay hardening)

### 6.1 Entry criteria
- Bundle D closure complete and accepted.
- `requires-g11` passed.

### 6.2 Completion checklist

- [ ] `TestExplainabilityContract`, `TestReplaySandboxMutationGuard`, `TestWhatIfBranchEngine` passing.
- [ ] Handoff gate confidence events include confidence + owner + timestamp.
- [ ] Replay outputs and branch outputs include immutable provenance.
- [ ] Evidence pack includes:
  - `artifacts/phase12/chunk_e/explanation_contract_examples.ndjson`
  - `artifacts/phase12/chunk_e/replay_safety.ndjson`
  - `artifacts/phase12/chunk_e/what_if_branching.ndjson`
  - `artifacts/phase12/chunk_e/handoff_continuity.ndjson`

### 6.3 Mandatory signoffs

- Product lead
- UX lead
- Compliance lead
- Core runtime lead

## 7) Bundle F signoff package (Phase 12 closure and finality)

### 7.1 Entry criteria

- Bundles B–E completed with no unresolved `L3`.
- Evidence graph completed and export reproducible.

### 7.2 Completion checklist

- [ ] `TestEvidenceGraphPackaging`, `TestReleasePackCompiler`, `TestPhase10to12Finality` passing.
- [ ] Release pack deterministic export run is reproducible.
- [ ] `artifacts/phase12/phase10_12_finality_bundle.md` exists and signed.
- [ ] Residual risk register attached with clear owner and reopen conditions.
- [ ] Evidence inventory has no placeholders.

### 7.3 Mandatory signoffs

- Program lead (required primary)
- Compliance lead
- SRE lead
- Security lead
- Product lead

## 8) Bundle handoff record schema

Use this JSON schema for each handoff.

```json
{
  "bundle_id": "phase10_bundle_b",
  "phase": 10,
  "status": "PASS",
  "handoff_id": "handoff-phase10-b-v1",
  "review_window_utc": {
    "start": "2026-02-15T00:00:00Z",
    "end": "2026-02-15T00:00:00Z"
  },
  "gate": "G10",
  "gates": {
    "requires_g10_pre": true,
    "requires_g10": false
  },
  "wp_status": [
    {"wp_id": "WP-10001", "status": "DONE"},
    {"wp_id": "WP-10002", "status": "DONE"}
  ],
  "hard_stop_state": {
    "active": [],
    "resolved_last_24h": 0
  },
  "artifacts": [
    "artifacts/phase10/chunk_b/dispatch_trace_schema.ndjson",
    "artifacts/phase10/chunk_b/compatibility_matrix.ndjson"
  ],
  "tests": [
    "TestDispatchDeterminism",
    "TestOperationSurfaceConsolidation"
  ],
  "signoff": [
    {"role":"Platform Lead","name":"", "status":"PENDING", "timestamp_utc":"", "evidence":"artifacts/phase10/chunk_b/.."},
    {"role":"Security Lead","name":"", "status":"PENDING", "timestamp_utc":"", "evidence":"artifacts/phase10/chunk_b/.."}
  ],
  "notes": [],
  "residual_risk": {
    "open": [],
    "deferred": []
  },
  "rollback_condition": "phase10.interface_v2 disabled and issue tracker state unchanged"
}
```

## 9) Mandatory handoff files by bundle

| Bundle | Handoff artifact | Location |
|---|---|---|
| Bundle B | `bundle_b_handoff_note.md` | `artifacts/phase10/chunk_b/` |
| Bundle C | `bundle_c_handoff_note.md` | `artifacts/phase11/chunk_c/` |
| Bundle D | `bundle_d_handoff_note.md` | `artifacts/phase11/chunk_d/` |
| Bundle E | `bundle_e_handoff_note.md` | `artifacts/phase12/chunk_e/` |
| Bundle F | `bundle_f_handoff_note.md` | `artifacts/phase12/chunk_f/` |

## 10) Handoff note template

Each handoff note should include:

```md
# Bundle X Handoff Note

- Bundle: phaseXX_bundle_y
- Handoff ID:
- Date:
- Lead: 
- Scope delivered:
  - WP list:
  - Artifacts:
  - Gates:
- Open risks:
  - risk_id: ...
  - owner: ...
  - mitigation:
  - rollback:
- Evidence manifest hash:
- Rollback token checklist:
  - tokens:
  - expiry/revocation notes:
- Signoff:
  - Platform:
  - Governance:
  - SRE:
  - Security:
  - Product:
  - Program:
- Next-bundle dependencies enabled:
  - bundle precondition:
  - required action for unblock:
```

## 11) Bundle-to-bundle transition matrix

| From | To | Transition gate | Blocking conditions |
|---|---|---|---|
| Bundle B | Bundle C | requires-g10 + bundle_b_signoff | Any unresolved trust or dispatch parity risk |
| Bundle C | Bundle D | requires-g11-pre + bundle_c_signoff | Control drift unresolved |
| Bundle D | Bundle E | requires-g11 + bundle_d_signoff | Unsafe shaping/continuity open risk |
| Bundle E | Bundle F | requires-g12-pre + bundle_e_signoff | Replay mutation or handoff confidence gap |
| Bundle F | Closure | requires-g12 + bundle_f_signoff | Open residual risk without explicit defer plan |

## 12) Rollback conditions by bundle

- **Bundle B:** disable `phase10.interface_v2`, freeze runtime dispatch changes, replay previous stable registry config.
- **Bundle C:** disable `phase11.autotune`, pin controls to static SLO policy, resume audit mode.
- **Bundle D:** disable policy learning updates, force manual control mode for continuity and handoff.
- **Bundle E:** force replay read-only, block what-if branch promotion, maintain explainability readback-only mode.
- **Bundle F:** stop finality updates, disable auto-release pack generation, retain current release candidate state.

## 13) Acceptance summary checks

Each bundle handoff must assert:

- [ ] all WPs in bundle are in `Done` or higher,
- [ ] all required hard-stop and rollback checks passed,
- [ ] all mandatory evidence files exist and include checksums,
- [ ] all required owners signed with timestamp,
- [ ] next-bundle dependencies documented in tracker notes.

## 14) Cross-references

- `thegent-phase10-12-execution-bundles-playbook.md`
- `thegent-phase10-12-hard-stop-and-rollback-matrix.md`
- `thegent-phase10-12-prd-wbs-dag-ticket-validation.md`
- `thegent-phase10-12-closure-readiness-pack-template.md`
- `thegent-phase10-12-issue-board-automation.md`



---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index

