# Thegent Phase 10–12 Drift Reconciliation Playbook

**Status:** Operational hardening artifact
**Date:** 2026-02-15
**Scope:** Detecting and correcting inconsistencies among PRD, WBS, DAG, tracker, and evidence artifacts before or during gates.

## 1) Why this exists

A stable execution environment fails when artifacts drift while gates continue to pass by local convention only. Drift causes:

- tickets approved against stale FR/WP mappings,
- gate checks that pass with incorrect dependency assumptions,
- evidence claims pointing to non-canonical artifacts,
- hard-stop rules applied to outdated control surfaces.

This playbook makes drift explicit and enforceable.

## 2) Drift domains

### 2.1 Identity drift

Expected invariant:

- one canonical `wp_id` exists across:
  - WBS (`thegent-wbs-phase10-12.md`)
  - PRD crossmap (`thegent-phase10-12-prd-wbs-crossmap-finalization.md`)
  - tracker seed (`thegent-phase10-12-issue-board-seed.json`)
  - issue queue (`thegent-phase10-12-implementation-issue-queue.md`)
  - traceability ledger (`thegent-phase10-12-master-traceability-ledger.md`)

Failure symptom:
- duplicate IDs, missing IDs, alias-like typos (WP-1001 vs WP-10001).

### 2.2 Lifecycle drift

Expected invariant:

- status transitions must follow:
  `Planned → Ready → In Progress → In Review → Bundle QA → Ready for Gate → Done`
- cannot regress from any state unless rollback runbook executed.

Failure symptom:
- direct transition `Ready → Done`,
- `Blocked` without state history entry and blocker owner,
- `Done` row still with unresolved required fields in ledger.

### 2.3 Dependency drift

Expected invariant:

- dependency graph in WBS and DAG must converge:
  every WBS dependency should either:
  - match a direct DAG predecessor edge or
  - be annotated as a reasoned tracker-only dependency with explicit rationale.

Failure symptom:
- edge exists in WBS but no DAG predecessor,
- DAG predecessor not present in WBS dependencies,
- cycle introduced outside migration event.

### 2.4 Evidence drift

Expected invariant:

- each `WP` has stable artifact references and checksum-tracked evidence bundle.

Failure symptom:
- reference points to stale or missing files,
- checksum mismatch,
- duplicate artifact names reused across WPs.

### 2.5 Governance drift

Expected invariant:

- gate readiness status in ledger and workboard must agree with gate lock matrix and hard-stop rules.

Failure symptom:
- `Bundle QA` marked complete with active `S` hard-stop,
- `Ready for Gate` without signoff token,
- stale PRD/WBS cross-map but current gate not updated.

## 3) Drift taxonomy and priority

| Class | Severity | Default escalation | Response window |
|---|---:|---|---|
| Identity drift | P1 | Program lead + owner | 0.5 business day |
| Lifecycle drift | P1 | Lead engineer + QA lead | 4 hours |
| Dependency drift | P0 | Platform lead + release lead | 2 hours |
| Evidence drift | P2 | QA + Docs + owner | 1 day |
| Governance drift | P0 | Program lead + governance lead | 2 hours |

## 4) Source-of-truth reconciliation order

Run in this order for deterministic correction:

1. `thegent-wbs-phase10-12.md`
2. `thegent-phase10-12-crossmap-finalization`
3. `thegent-phase10-12-master-traceability-ledger.md`
4. `thegent-issue-board-seed.json`
5. `thegent-implementation-issue-queue.md`
6. `thegent-phase10-12-hard-stop-and-rollback-matrix.md`
7. relevant launch/readiness docs

Any correction starts from step 1 and cascades to dependent artifacts only.

## 5) Canonical correction workflow (one WP)

### 5.1 detect

- identify mismatch set:
  - `wp_id` missing in any source,
  - dependency not represented in DAG or ledger,
  - gate status mismatch.

### 5.2 isolate

- lock WP in tracker:
  - status -> `Blockers`
  - add block code:
    - `DRIFT_ID` / `DRIFT_LIFECYCLE` / `DRIFT_DEP` / `DRIFT_EVID` / `DRIFT_GOV`

### 5.3 reconcile

- update root source:
  - for identity/dependency/evidence issues, update WBS and/or PRD map first.
- run validation on all linked artifacts (ledger + issue seed + automation).

### 5.4 release

- move row to `In Review`
- append correction summary in issue history
- release from lock only when compact dashboard gate score remains valid for two consecutive checks.

## 6) Automated checks (minimal set)

### 6.1 Identity checks

- all `wp_id`s in WBS and tracker are subsets each other;
- zero unknown prefixes (`WP-` + 5 digits);
- no duplicate artifact references with different WP IDs.

### 6.2 DAG/WBS checks

- every WBS dependency edge appears in DAG or allowed exception list;
- no dependency cycles after latest merge;
- transitive dependency depth ≤ 7 for phase 10–12 critical route.

### 6.3 Lifecycle checks

- transitions only through allowed adjacency matrix;
- status `Done` requires `Evidence` and `DAG` gates to be green;
- no transition to `Ready for Gate` if hard-stop active in related phase.

### 6.4 Evidence checks

- SHA exists on every evidence artifact;
- checksums reverified on each phase boundary;
- evidence path includes run identifier and timestamp.

### 6.5 Governance checks

- gate lock conditions satisfied (`G10`, `G11`, `G12`) and lock tokens present;
- rollback token mandatory where `bundle` in (`phase10_bundle_b`, `phase11_bundle_d`, `phase12_bundle_e`);
- hard-stop mapping from matrix represented in incident channel.

## 7) Drift triage matrix by gate

### Gate 10

- Priority classes: Identity, Lifecycle, Dependency
- Response target: `< 4h` for P1, `< 24h` for P2
- Temporary workarounds: no new runtime changes if P1 unresolved

### Gate 11

- Priority classes: Dependency, Governance, Evidence
- Response target: `< 2h` for P0/P1
- Temporary workarounds: suspend phase11 control experiments, continue docs-only edits

### Gate 12

- Priority classes: Governance, Evidence, Lifecycle
- Response target: `< 1h` for any governance severity
- Temporary workarounds: freeze release pack generation and publish readiness hold

## 8) Incident report format for drift

```text
DRIFT-INCIDENT:
  id: DRIFT-YYYYMMDD-####
  wp_ids: [WP-11003, WP-11004]
  gate: G11
  class: DRIFT_DEP
  severity: P0
  detected_at: 2026-02-15T00:00:00Z
  detected_by: dashboard-runner
  summary: Dependency edge missing in DAG for control continuity route
  impact: G11 cannot be safely validated
  owner: platform-lead
  action:
    - lock wp_ids
    - add temporary blocker flag
    - patch DAG and dependency map
    - regenerate ledger and issue seed
    - rerun validation script
  resolved_at: [if known]
  evidence:
    - files touched
    - commit hash
    - validation run id
```

## 9) Recovery playbook

### 9.1 If drift is accidental and low risk

- correct directly in source-of-truth
- rerun auto-validation
- clear blocker with evidence stamp
- resume execution in same gate

### 9.2 If drift is systemic

- pause active gate movement
- run full issue-board and tracker freeze
- conduct 90-minute correction sprint (owners from each source artifact)
- regenerate traceability ledger
- release under `drift-reconciled` status only after 24h clean check window

### 9.3 If drift indicates hidden process failure

- escalate to postmortem path
- record process failure root cause
- add a "never regress again" guard in validation script
- optionally add a mandatory schema check to child-gated CI

## 10) Continuous control loop

1. Run automatic drift scan every 2 hours (or after every merge wave).
2. Publish output into dashboard as a risk-bearing field.
3. Assign ownership in board comments and issue blocking labels.
4. Ensure next gate readiness uses post-scan risk score.
5. After two consecutive zero-drift checks, release blocked WPs.

## 11) Hardening recommendations

- add machine-readable schema for every WBS/DAG/seed artifact
- require drift report as part of milestone acceptance
- require rollback token on all runtime-variant WPs
- prevent manual status edits outside board tooling without signed webhook events
- add smoke tests that intentionally inject synthetic drift and assert rejection

## 12) Exit criteria

Drift reconciliation is complete for a WP when:

- identity consistency restored across all sources
- lifecycle timeline reflects valid transition sequence
- dependency and evidence checks pass
- no blocking class remains at or above P1
- compact dashboard risk score remains `>= 85` for at least 2 consecutive scans

If any class remains unresolved, do not promote gate stage.


---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index
