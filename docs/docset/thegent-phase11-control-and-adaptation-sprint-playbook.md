# Thegent Phase 11 Sprint Playbook (Bundles C and D)

**Status:** Operational playbook for Bundle C + Bundle D  
**Date:** 2026-02-15  
**Scope:** Execution sequence for control baseline (adaptive loops) and adaptation governance.

## 1) Bundle C objective (WP-11001 to WP-11005)

- Establish deterministic predictive control surface.
- Add anti-oscillation guardrails and calibration gates.
- Produce reproducible control evidence for G11 precheck.

## 2) Bundle C day-by-day (2-week sprint)

### Day 1: Preflight and guardrails

- Confirm `phase11_bundle_c` status is `Ready`.
- Verify prerequisites:
  - `WP-10003` and `WP-10007` in evidence-certain state.
  - Feature flag `phase11.autotune` set to controlled mode.
  - Kill switch documented and accessible.
- Create baseline files:
  - `artifacts/phase11/chunk_c/` and `artifacts/phase11/chunk_c/slo_contract.json`.

### Day 2: WP-11001 — SLO regulator

- Implement regulator with hysteresis and bounded action deltas.
- Add monotonic controls for state transitions.
- Required tests:
  - `TestSLORegulator`
  - `LoadStepResponseChaosSpec`
- Evidence:
  - `artifacts/phase11/chunk_c/slo_regulator_events.ndjson`
  - `artifacts/phase11/chunk_c/regulator_tuning_log.ndjson`

### Day 3: WP-11002 — Forecast engine hardening

- Add p50/p80/p95 output contract and deterministic inference path.
- Add forecast event schema and latency ceilings.
- Required tests:
  - `TestForecastEngineRun`
  - `BenchmarkForecastLatency`
- Evidence:
  - `artifacts/phase11/chunk_c/forecast_quality.ndjson`
  - `artifacts/phase11/chunk_c/forecast_drift_log.ndjson`

### Day 4: WP-11003 — Calibration and drift pause

- Implement confidence tracker + pause action when below threshold.
- Add calibration report outputs and policy hooks.
- Required tests:
  - `TestCalibrationDrift`
  - `TestCalibrationDriftProperty`
- Evidence:
  - `artifacts/phase11/chunk_c/calibration_drift.ndjson`
  - `artifacts/phase11/chunk_c/calibration_report.md`

### Day 5: WP-11004 — Saturation and preemption policy

- Implement queue/provider saturation monitor and safe avoidance.
- Add preemption rationale and rollback metadata.
- Required tests:
  - `TestPreemptiveSaturationPolicy`
  - `BenchmarkSLOControllerThroughput`
- Evidence:
  - `artifacts/phase11/chunk_c/preemption_policy_events.ndjson`
  - `artifacts/phase11/chunk_c/saturation_guard_log.ndjson`

### Day 6: WP-11005 — Self-heal recommendations

- Add recommendation ranking with assumption and rollback fields.
- Add policy approvals for auto-apply path.
- Required tests:
  - `TestSelfHealRecommendation`
  - `TestSelfHealControlFlow`
- Evidence:
  - `artifacts/phase11/chunk_c/self_heal_recommendations.ndjson`
  - `artifacts/phase11/chunk_c/recommendation_rationale.ndjson`

### Day 7: Bundle C integration + freeze

- Run full bundle C suite:
  - `TestSLORegulator`
  - `TestForecastEngineRun`
  - `TestCalibrationDrift`
  - `TestPreemptiveSaturationPolicy`
  - `TestSelfHealRecommendation`
- Produce combined evidence:
  - `artifacts/phase11/chunk_c/chunk_c_g11_precheck.md`
  - `artifacts/phase11/chunk_c/chunk_c_signoff.md`
- Blocker if any instability:
  - disable `phase11.autotune`
  - revert control actions to static thresholds

## 3) Bundle D objective (WP-11006 to WP-11010)

- Extend adaptive behavior under policy governance.
- Add continuity predictor and safe-mode controls.
- Package control evidence for official G11 readiness.

## 4) Bundle D day-by-day (next 2 weeks)

### Day 1: Shape model and continuity readiness

- Confirm preconditions from Bundle C.
- Validate shift/freeze calendar is imported into continuity predictor.
- Prepare:
  - `artifacts/phase11/chunk_d/task_shaping_contract.json`
  - `artifacts/phase11/chunk_d/continuity_risk_contract.json`

### Day 2: WP-11006 — Adaptive task shaping

- Add split/merge controls with policy gating.
- Add reversal log and owner trace.
- Required tests:
  - `TestAdaptiveTaskShaping`
  - `TestTaskShapingPolicy`
- Evidence:
  - `artifacts/phase11/chunk_d/adaptive_shaping.ndjson`
  - `artifacts/phase11/chunk_d/task_shaping_risk_log.ndjson`

### Day 3: WP-11007 — Continuity predictor

- Add pre-shift risk scoring and warning emission.
- Required tests:
  - `TestContinuityRiskPredictor`
  - `TestReshapeUnderSurge`
- Evidence:
  - `artifacts/phase11/chunk_d/continuity_predictions.ndjson`
  - `artifacts/phase11/chunk_d/continuity_false_positive_review.md`

### Day 4: WP-11008 — Learning loop guardrails

- Add signed policy flow for control parameter changes.
- Add manifests for each change with before/after state.
- Required tests:
  - `TestLearningLoopGovernance`
  - `TestPolicySignedChangeManifest`
- Evidence:
  - `artifacts/phase11/chunk_d/learning_loop.ndjson`
  - `artifacts/phase11/chunk_d/policy_change_manifest.ndjson`

### Day 5: WP-11009 — Safe-mode governance

- Implement safe-mode lifecycle states and expiry.
- Add rollback + event continuity checks.
- Required tests:
  - `TestSafeModeGovernance`
  - `TestSafeModeReentry`
  - `TestControlRollbackLatency`
- Evidence:
  - `artifacts/phase11/chunk_d/safe_mode_governance.ndjson`
  - `artifacts/phase11/chunk_d/safe_mode_drill_report.md`

### Day 6: WP-11010 — Evidence pack

- Build deterministic G11 evidence bundle.
- Include:
  - control events,
  - recommendation outputs,
  - policy-signoff evidence,
  - stability profile.
- Required tests:
  - `TestEvidencePackEmit11`
- Evidence:
  - `artifacts/phase11/chunk_d/g11_readiness_pack.ndjson`
  - `artifacts/phase11/chunk_d/g11_gate_evidence.ndjson`
- If missing any critical event, hold transition to `Ready for Gate`.

### Day 7: Bundle D pre-G11 handoff

- Run `LoadStepResponseChaosSpec` under Bundle D control path.
- Validate no unsafe repeated mode changes:
  - oscillation, safe-mode mismatch, policy mismatch.
- Publish `artifacts/phase11/chunk_d/g11_gate_note_candidate.md`.
- Set `Bundle D` state to `Ready for Gate`.

## 5) Combined bundle C+D hard-stop matrix

### Kill switch rules

- `phase11.autotune=false` on:
  - sustained oscillation (2 windows),
  - repeated safe-mode mismatch,
  - control rollback latency breach.

### Evidence lock rules

- Evidence manifest must include:
  - deterministic `run_id`,
  - `policy_version`,
  - `policy_digest`,
  - `rollback_token`,
  - evidence owner.

### Acceptance checklist

- All tests from bundle pages pass.
- `artifacts/phase11/chunk_c/` and `artifacts/phase11/chunk_d/` contain manifest, signoff, and timestamp.
- No unapproved recommendation auto-apply.

## 6) Suggested PR review template for phase 11

```
## PR summary
- Bundles covered: phase11_bundle_c / phase11_bundle_d
- WPs: [list]
- Flags modified: phase11.autotune
- Kill-switch tested: yes/no

## Evidence
- manifest_id:
- tests run:
- control evidence files:

## Gate
- G11 precheck passes: yes/no
- risks introduced:
- rollback token:
```



---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index

