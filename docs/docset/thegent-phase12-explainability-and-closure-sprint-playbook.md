# Thegent Phase 12 Sprint Playbook (Bundles E and F)

**Status:** Operational playbook for Bundle E + Bundle F  
**Date:** 2026-02-15  
**Scope:** Execution sequence for explainability, replay safety, persona policies, and closure packaging.

## 1) Bundle E objective (WP-12001 to WP-12006)

- Produce stable explainability contract across summary/detail/trace.
- Harden replay mode to be immutable by default.
- Deliver explainability and continuity evidence required for G12 precheck.

## 2) Bundle E two-week execution plan

### Day 1: Preflight and context checks

- Ensure `Bundle D` complete and evidence pack signed.
- Confirm `phase12.hardening` available and documented.
- Create directory:
  - `artifacts/phase12/chunk_e/`
- Baseline:
  - explainability schema ID,
  - replay write guard flag,
  - branch approval workflow path.

### Day 2: WP-12001 explainability contract

- Implement deterministic summary/detail/trace schema.
- Add schema contract tests and renderer checks.
- Required tests:
  - `TestExplainabilityContract`
  - `TestExplainabilityReplayIntegration`
- Evidence:
  - `artifacts/phase12/chunk_e/explanation_contract_examples.ndjson`
  - `artifacts/phase12/chunk_e/explainability_consistency_report.md`

### Day 3: WP-12002 fatigue controls

- Add escalation scoring and suppression thresholds.
- Ensure critical alerts are exempted from suppression.
- Required tests:
  - `TestFatigueControlRules`
  - `TestFatigueSuppressionAccuracy`
- Evidence:
  - `artifacts/phase12/chunk_e/fatigue_controls.ndjson`
  - `artifacts/phase12/chunk_e/fatigue_impact_report.md`

### Day 4: WP-12003 replay sandbox hardening

- Default replay path to read-only.
- Add execute-mode gate and blocked-write telemetry.
- Required tests:
  - `TestReplaySandboxMutationGuard`
  - `TestReplayMutationProperty`
- Evidence:
  - `artifacts/phase12/chunk_e/replay_safety.ndjson`
  - `artifacts/phase12/chunk_e/replay_mutation_report.md`

### Day 5: WP-12004 what-if and branch governance

- Implement branch creation + deterministic branch ID.
- Add branch approval requirement for promoted branches.
- Required tests:
  - `TestWhatIfBranchEngine`
  - `TestHandoffReplayReadiness`
- Evidence:
  - `artifacts/phase12/chunk_e/what_if_branching.ndjson`
  - `artifacts/phase12/chunk_e/branch_approval_trace.ndjson`

### Day 6: WP-12005 handoff confidence continuity

- Add continuity confidence gate for ownership transfer.
- Add explicit confirmation and handoff snapshot.
- Required tests:
  - `TestHandoffConfidenceGate`
- Evidence:
  - `artifacts/phase12/chunk_e/handoff_continuity.ndjson`
  - `artifacts/phase12/chunk_e/handoff_confirmation_log.ndjson`

### Day 7: WP-12006 evidence graph and packaging

- Build evidence graph with continuity edges.
- Add manifest + checksum output.
- Required tests:
  - `TestEvidenceGraphPackaging`
  - `TestEvidencePackagingFlow`
  - `TestEvidenceGraphCompleteness`
- Evidence:
  - `artifacts/phase12/chunk_e/evidence_graph.ndjson`
  - `artifacts/phase12/chunk_e/evidence_bundling_report.md`

### Day 8: Bundle E stabilization

- Run G12 precheck smoke:
  - `TestExplainabilityContract`
  - `TestReplayMutationProperty`
  - `TestEscalationEvidenceCompleteness`
- Create:
  - `artifacts/phase12/chunk_e/g12_precheck_notes.md`
  - `artifacts/phase12/chunk_e/bundle_e_signoff.md`

## 3) Bundle F objective (WP-12007 to WP-12010)

- Finalize persona controls, learning assets, release packaging, and closure documentation.
- Produce formal final gate readiness and residual risk transfer.

## 4) Bundle F two-week execution plan

### Day 1: Persona policy base

- Seed persona catalog (`SRE`, `Product`, `Security`, `Ops`).
- Implement access matrix evaluation at runtime decision boundary.
- Required tests:
  - `TestPersonaProfiles`
- Evidence:
  - `artifacts/phase12/chunk_f/persona_profiles.ndjson`
  - `artifacts/phase12/chunk_f/persona_access_matrix.json`

### Day 2: WP-12008 operational learning assets

- Build onboarding runbooks and coaching cards from latest evidence.
- Required tests:
  - `TestLearningAssetGeneration`
- Evidence:
  - `artifacts/phase12/chunk_f/operational_learning_assets.ndjson`
  - `artifacts/phase12/chunk_f/continuity_drill_report.md`

### Day 3: WP-12009 release docs packaging

- Add deterministic command for PRD/WBS/test artifact pack.
- Include digest and manifest output.
- Required tests:
  - `TestReleasePackCompiler`
  - `TestReleasePackDeterministicBuild`
  - `TestEvidencePackagingFlow`
- Evidence:
  - `artifacts/phase12/chunk_f/release_pack_summary.ndjson`
  - `artifacts/phase12/chunk_f/release_pack_manifest.ndjson`
  - `artifacts/phase12/chunk_f/release_pack_determinism.md`

### Day 4: WP-12010 closure and finality

- Compile finality note from all bundle evidence and residual risk register.
- Required tests:
  - `TestPhase10to12Finality`
  - `TestPersonaAndReadinessGate`
- Evidence:
  - `artifacts/phase12/chunk_f/phase10_12_finality_bundle.md`
  - `artifacts/phase12/chunk_f/closure_residual_risk_log.md`
  - `artifacts/phase12/chunk_f/finality_signoff_matrix.csv`

### Day 5: Closure governance and final review

- Collect required signatures:
  - Program lead
  - Security
  - Product
  - SRE
- Validate `WBS_TO_ISSUE_IMPORT_MATRIX.md` has WP-12007..WP-12010 done.
- Publish `artifacts/phase12/chunk_f/closure_readiness_readme.md`.

## 5) Phase 12 hard-stop and rollback rules

- Replaying writes in non-execute mode: immediate freeze `phase12.hardening`.
- Persona policy bypass discovered: rollback to last stable matrix and disable new persona constraints.
- Deterministic export mismatch: repeat build from clean state and pin manifest.

## 6) Final acceptance matrix

- Explainability deterministic across summary/detail/trace.
- Replay sandbox mutation guard 100% enforced.
- G12 evidence has no dangling critical edges.
- Closure artifact includes:
  - all final artifact IDs,
  - residual risk table,
  - owner signatures with timestamps.



---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index

