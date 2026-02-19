# Thegent Phase 10–12 PRD-WBS-DAG-Ticket Validation Framework

**Status:** Operational hardening doc  
**Date:** 2026-02-15  
**Scope:** Deterministic traceability and schema validation across PRD, WBS, DAG, implementation queue, and tracker artifacts for Phases 10–12.

Use this framework as the final pre-implementation and pre-gate quality bar.

## 1) Validation objective

A phase-10/11/12 WP is production-eligible only when all layers agree:

- PRD requirement coverage (FR-069..FR-090 + NFR-029..NFR-040)
- WBS identity and ownership
- DAG execution node and predecessor order
- Ticket identity and dependency status
- Tracker state and evidence manifest readiness
- Gate lock and rollback constraints

## 2) Canonical crosswalk contract

For every active WP, the following tuple must exist and be internally consistent:

- `wp_id`
- `phase`
- `bundle`
- `issue_key`
- `dag_node(s)`
- `fr_ids`
- `nfr_ids`
- `required_tests`
- `required_artifacts`
- `gate_preconditions`
- `dependencies`
- `rollback_token`
- `owner`
- `acceptance` (DoD checklist + DoR checklist)

If any tuple item is missing, the WP cannot move to `Bundle QA`.

## 3) Required source-of-truth map

### 3.1 WBS source
- `thegent-wbs-phase10-12.md` (WP definitions, dependencies, sequencing)

### 3.2 Requirements source
- `thegent-phase10-12-optimal-design-prd.md`
- `thegent-phase10-12-prd-wbs-crossmap-finalization.md`

### 3.3 Execution graph source
- `thegent-dag-phase10-12-extension.md`

### 3.4 Tracker source
- `thegent-phase10-12-issue-board-seed.json`
- `thegent-phase10-12-implementation-issue-queue.md`
- `thegent-phase10-12-execution-workboard.md`
- `thegent-phase10-12-execution-bundles-playbook.md`
- `thegent-phase10-12-hard-stop-and-rollback-matrix.md`
- `thegent-phase10-12-issue-board-automation.md`
- `thegent-phase10-12-closure-readiness-pack-template.md`

## 4) WP-level validation matrix (required per-phase coverage)

### 4.1 Phase 10 (interface convergence and trust)

| WP | WBS owner | FR | DAG node | Issue row | Must-have evidence | Must-have tests |
|---|---|---|---|---|---|
| WP-10001 | Platform lead | FR-069 | N10001 | THEGENT-WP-10001 | `artifacts/phase10/*operation_envelope_v2*` | TestOperationEnvelopeV2Schema |
| WP-10002 | Platform lead | FR-070 | N10002 | THEGENT-WP-10002 | `artifacts/phase10/*capability_registry*` | TestCapabilityRegistryService |
| WP-10003 | Core runtime | FR-071, FR-072 | N10003 | THEGENT-WP-10003 | `artifacts/phase10/*dispatch_graph*` | TestDispatchDeterminism; TestEnvelopeToDispatchEndToEnd |
| WP-10004 | Security/Governance | FR-032 | N10004 | THEGENT-WP-10004 | `artifacts/phase10/*trust*` | TestAdapterTrustPolicy |
| WP-10005 | Platform/API | FR-071 | N10005 | THEGENT-WP-10005 | `artifacts/phase10/*operation_coverage*` | TestOperationSurfaceConsolidation |
| WP-10006 | UX/Core runtime | FR-074 | N10006 | THEGENT-WP-10006 | `artifacts/phase10/*unknown_operation*` | TestMigrationHintRenderer |
| WP-10007 | Governance | FR-072, FR-075 | N10007 | THEGENT-WP-10007 | `artifacts/phase10/*dispatch_trace*` | TestDispatchTraceEvent |
| WP-10008 | Platform architecture | FR-073 | N10008 | THEGENT-WP-10008 | `artifacts/phase10/*plugin_conformance*` | TestAdapterConformanceLifecycle |
| WP-10009 | API/Docs | FR-070, FR-074 | N10009 | THEGENT-WP-10009 | `artifacts/phase10/*compatibility*` | TestCompatibilityMatrixPolicy |
| WP-10010 | Documentation | FR-083? (docs clarity) | N10010 | THEGENT-WP-10010 | `artifacts/phase10/*operations_ops_guide*` | TestOperationsDocsGeneration |

### 4.2 Phase 11 (control and continuity)

| WP | WBS owner | FR | DAG node | Issue row | Must-have evidence | Must-have tests |
|---|---|---|---|---|---|
| WP-11001 | SRE/Ops | FR-076 | N11001 | THEGENT-WP-11001 | `artifacts/phase11/*slo_regulator*` | TestSLORegulator |
| WP-11002 | Data/Planning | FR-077 | N11002 | THEGENT-WP-11002 | `artifacts/phase11/*forecast*` | TestForecastEngineRun |
| WP-11003 | QA/Governance | FR-077 | N11003 | THEGENT-WP-11003 | `artifacts/phase11/*calibration*` | TestCalibrationDrift |
| WP-11004 | Core routing | FR-078 | N11004 | THEGENT-WP-11004 | `artifacts/phase11/*preemption*` | TestPreemptiveSaturationPolicy |
| WP-11005 | Governance/Product | FR-079 | N11005 | THEGENT-WP-11005 | `artifacts/phase11/*self_heal*` | TestSelfHealRecommendation |
| WP-11006 | Orchestration | FR-080 | N11006 | THEGENT-WP-11006 | `artifacts/phase11/*adaptive*` | TestAdaptiveTaskShaping |
| WP-11007 | SRE/Product | FR-081 | N11007 | THEGENT-WP-11007 | `artifacts/phase11/*continuity*` | TestContinuityRiskPredictor |
| WP-11008 | Governance | FR-082 | N11008 | THEGENT-WP-11008 | `artifacts/phase11/*learning_loop*` | TestLearningLoopGovernance |
| WP-11009 | Security | FR-086 | N11009 | THEGENT-WP-11009 | `artifacts/phase11/*safe_mode*` | TestSafeModeGovernance |
| WP-11010 | QA/Docs | FR-077 | N11010 | THEGENT-WP-11010 | `artifacts/phase11/*g11*` | TestEvidencePackEmit11 |

### 4.3 Phase 12 (hardening and closure)

| WP | WBS owner | FR | DAG node | Issue row | Must-have evidence | Must-have tests |
|---|---|---|---|---|---|
| WP-12001 | Product/UX | FR-083 | N12001 | THEGENT-WP-12001 | `artifacts/phase12/*explanation*` | TestExplainabilityContract |
| WP-12002 | SRE | FR-084 | N12002 | THEGENT-WP-12002 | `artifacts/phase12/*fatigue*` | TestFatigueControlRules |
| WP-12003 | Core runtime | FR-085 | N12003 | THEGENT-WP-12003 | `artifacts/phase12/*replay*` | TestReplaySandboxMutationGuard |
| WP-12004 | Product/Governance | FR-085 | N12004 | THEGENT-WP-12004 | `artifacts/phase12/*what_if*` | TestWhatIfBranchEngine |
| WP-12005 | Governance/UX | FR-086 | N12005 | THEGENT-WP-12005 | `artifacts/phase12/*handoff*` | TestHandoffConfidenceGate |
| WP-12006 | Compliance | FR-087 | N12006 | THEGENT-WP-12006 | `artifacts/phase12/*evidence_graph*` | TestEvidenceGraphPackaging |
| WP-12007 | Product/Security | FR-089 | N12007 | THEGENT-WP-12007 | `artifacts/phase12/*persona*` | TestPersonaProfiles |
| WP-12008 | Documentation | FR-089 | N12001? / N12007 | THEGENT-WP-12008 | `artifacts/phase12/*learning*` | TestLearningAssetGeneration |
| WP-12009 | Documentation/Automation | FR-088, FR-090 | N12009 | THEGENT-WP-12009 | `artifacts/phase12/*release_pack*` | TestReleasePackCompiler |
| WP-12010 | Program lead | FR-090 | N12010 | THEGENT-WP-12010 | `artifacts/phase12/*finality*` | TestPhase10to12Finality |

## 5) Tracker schema contract

### 5.1 Seed schema (required fields)

Each ticket object must contain:

```yaml
issue_key: string          # e.g., THEGENT-WP-10004
wp_id: string              # WP-10004
title: string
status: enum(Planned, In Progress, In Review, Blockers, Bundle QA, Ready for Gate, Done)
assignee: string
bundle: string             # phase10_bundle_b, phase11_bundle_c, ...
phase: string|integer      # "10" | "11" | "12"
labels: array[string]
dependencies: array[string] # WP ids
required_tests: array[string]
required_artifacts: array[string]
gate_preconditions: array[string]
rollback_token: string
dor_checks: array[string]
dor_checks_status: map       # optional runtime-computed per run
dod_checks: array[string]
dod_checks_status: map       # optional runtime-computed per run
evidence_manifest: array[string] | null
```

### 5.2 Matrix schema (WBS→Issue)

Each WBS row must include:

```yaml
wp_id
issue_key
status
owner
dependencies
evidence_manifest
gate_lock
rollforward_risk
```

Any missing mandatory field => `FAILED` crosswalk.

## 6) Gate and dependency lock matrix (execution)

### 6.1 Gate prerequisites

| Gate | Must-have upstream WPs | Hard stop if missing |
|---|---|---|
| G10 | WP-10001..WP-10010 | stop all phase-11 runtime changes |
| G11 | WP-11001..WP-11010 + G10 | stop autonomous control and task shaping |
| G12 | WP-12001..WP-12010 + G10 + G11 | stop release-pack, replay hardening, persona path changes |

### 6.2 Bundle preconditions

- Bundle C/D requires `bundle_b_done = true`.
- Bundle E/F requires `bundle_c_d_signoff = true` and `g11_pack_ready`.
- Bundle F requires `closure_readiness_template completed`.

## 7) Validation runs (recommended cadence)

Use this sequence at each phase boundary:

1. **Crosswalk run:** verify every WP has complete tuple from section 2.
2. **DAG run:** verify predecessor links and no dangling nodes.
3. **Tracker run:** verify all issue keys are unique and dependencies are closed or explicitly blocked.
4. **Test lock run:** verify all required tests are present in test plan and linked.
5. **Artifact run:** verify required artifact exists and is referenced by PRD/WBS/ticket.
6. **Rollback run:** verify rollback token is present for runtime-affecting WPs.
7. **Hard-stop run:** verify no active L2/L3 from last 24h without closure notes.

## 8) Minimal deterministic validation pseudocode

```python
def validate_phase10_12(seed, wbs, prd_xmap, dag, issue_queue):
    issues = {t["wp_id"]: t for t in seed["tickets"]}
    for wp_row in wbs["wps"]:
        wp_id = wp_row["wp_id"]
        frs = prd_xmap.get(wp_id, [])
        issue = issues.get(wp_id)
        if issue is None:
            fail(f"missing issue for {wp_id}")
        if not issue["required_tests"]:
            fail(f"missing required tests for {wp_id}")
        if not issue["required_artifacts"]:
            fail(f"missing artifacts for {wp_id}")
        if not issue["rollback_token"]:
            fail(f"missing rollback token for {wp_id}")
        check_gate_ready(issue)
        check_dag_links(dag, wp_id)
        check_dependency_closure(issue["dependencies"])
        check_artifact_exist(issue["required_artifacts"])
    return True
```

## 9) Migration-safe execution rules

No crosswalk schema changes can be made without:

- bumping seed version,
- recording migration reason,
- updating:
  - crossmap,
  - issue templates,
  - workboard schema,
  - and this validation doc.

## 10) Phase-by-phase implementation pass (operational)

### Phase 10 pass
- Validate all WPs 10001–10010 tuple completeness and dependency closure.
- Run DAG check for nodes N10001..N10010.
- Produce `artifacts/phase10/crosswalk_pre_g10_pass.ndjson`.

### Phase 11 pass
- Validate WPs 11001–11010 against live G10 closure and phase11-specific guardrails.
- Produce `artifacts/phase11/crosswalk_pre_g11_pass.ndjson`.

### Phase 12 pass
- Validate closure bundle and finality traceability to WPs 12001–12010.
- Produce `artifacts/phase12/crosswalk_pre_g12_pass.ndjson`.

## 11) Acceptance evidence template

Create and persist this evidence file for each phase pass:

```json
{
  "phase": "10",
  "checker": "crosswalk-engine",
  "run_id": "uuid",
  "result": "PASS",
  "wp_count": 10,
  "missing_fields": [],
  "active_hard_stops": [],
  "seed_hash": "sha256:...",
  "artifacts_validated": 9,
  "test_contracts_ok": true,
  "created_at": "2026-02-15T00:00:00Z",
  "signed_by": "Program Lead"
}
```

## 12) Failure handling and unblock protocol

- Any `missing required_tests` failure => move WP to `Blockers` with reason.
- Any `missing required_artifacts` failure => stop acceptance and freeze dependent WPs.
- Any `missing rollback_token` for runtime path => block `Ready for Gate`.
- Any crosswalk mismatch (`WP` present in one source but not another) => open an explicit crosswalk debt issue and pause.

## 13) Final closure dependency closure

For finality, the checklist is:

- `section 10` and `section 11` and `section 12` all PASS
- Seed replay run has exact same result hash as initial pass
- All hard-stop L3 instances have close notes with rollback timestamps
- `WP-12010` can proceed to `Ready for Gate` only after evidence manifests match

## 14) Tooling and reuse notes

- Reuse this file as the authoritative validation spec in:
  - `--mode=dry-run` checks,
  - CI crosswalk jobs,
  - and one-pager launch readiness checks.
- Pair with:
  - `thegent-phase10-12-issue-board-automation.md` (mechanical sync),
  - `thegent-phase10-12-hard-stop-and-rollback-matrix.md` (runtime controls),
  - `thegent-phase10-12-closure-readiness-pack-template.md` (finality formatting).



---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index

