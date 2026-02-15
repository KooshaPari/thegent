# Thegent Phase 3–6 Closure Validator Automation Package

**Status:** Execution package  
**Date:** 2026-02-15  
**Scope:** Operational CI + hook-based automation for enforcing phase-3–6 closure acceptance contracts.

## 1) Purpose

This package operationalizes:

- `thegent-phase3-6-closure-acceptance-contract-schema.md`
- `thegent-phase3-6-closure-acceptance-pack-template.md`
- cross-wave continuity rules

into hard-stop-aware automated checks.

## 2) Package components

1. Validator contract
2. Command interface
3. CI workflow
4. Issue-board and PR hook integration
5. Exception and override control
6. Re-run and audit protocol

## 3) Validation command surface

### 3.1 Single WP validation

```bash
thegent-validate phase3-6 closure \
  --wp WP-0608 \
  --contract docs/docset/thegent-phase3-6-closure-acceptance-contract-schema.md \
  --pack artifacts/phase3-6/wp-0608/closure_pack.json \
  --strict
```

Expected output:

- `result`: PASS/WARN/FAIL/BLOCK
- `violations`: zero or more structured records
- `validator_version`: package version
- `evidence_hash`: manifest hash

### 3.2 Bulk phase validation

```bash
thegent-validate phase3-6 closure --phase 3 --scope docs/docset/bundles/phase3.yaml --strict
thegent-validate phase3-6 closure --phase 4 --scope docs/docset/bundles/phase4.yaml
thegent-validate phase3-6 closure --phase 5 --scope docs/docset/bundles/phase5.yaml --require continuity
thegent-validate phase3-6 closure --phase 6 --scope docs/docset/bundles/phase6.yaml --require next-phase-ready
```

### 3.3 Cross-wave continuity check

```bash
thegent-validate phase3-6 closure --phase 6 \
  --continuity-check \
  --target-crosswave thegent-phase10-12-closure-readiness-and-delta-pack.md
```

## 4) CLI contract schema

### 4.1 Input contract (`--pack`)

```json
{
  "phase": 6,
  "wp_id": "WP-0608",
  "bundle_id": "phase6_bundle_d",
  "validation_level": "standard|strict|continuity",
  "closure_pack": "path/to/closure_pack.json",
  "crosswave_target": [
    "thegent-phase10-12-crosswave-bridge-and-continuity-plan.md"
  ]
}
```

### 4.2 Output record

```json
{
  "run_id": "run-2026-02-15-001",
  "tool": "closure_validator",
  "wp_id": "WP-0608",
  "phase": 6,
  "result": "PASS",
  "result_code": "CLOSE-OK",
  "score": {
    "evidence_ratio": 0.97,
    "tests_ratio": 1.0,
    "risk_score": 0.0
  },
  "violations": [],
  "recommendation": "ready_for_phase7_and_phase10_handoff"
}
```

## 5) Validation stages and ordering

Checks must run in strict order:

1. parse schema
2. required-field completeness
3. evidence file existence + checksum verification
4. test-pack consistency check
5. required signoff check
6. continuity contract check (for phase 6 and above)
7. rollback readiness check
8. crosswave drift check
9. exception validity check
10. decision emission + audit write

## 6) Gate mapping matrix

### 6.1 Phase 3 gates

```text
WP complete -> evidence check -> tests -> phase3_gate_candidate
```

Blockers:
- missing evidence
- failed required tests

### 6.2 Phase 4 gates

```text
phase3_gate_candidate -> continuity baseline -> rollback readiness -> phase4_gate
```

Blockers:
- continuity_pack invalid
- rollback untested

### 6.3 Phase 5 gates

```text
phase4_gate -> crosswave precheck -> governance checks -> phase5_gate
```

Blockers:
- missing governance version
- unresolved drift with P1/P0 class

### 6.4 Phase 6 gates

```text
phase5_gate -> closure readiness -> full signoff -> phase6_gate
```

Blockers:
- missing security signoff (if required)
- open P1 risk without active exception

## 7) CI workflows

### 7.1 GitHub Actions example

```yaml
name: phase3-6-closure-validation
on:
  pull_request:
    paths:
      - "docs/docset/**"
      - "artifacts/phase3-6/**"
jobs:
  validate-phase3-6-closure:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate Phase 3 closure packs
        run: |
          thegent-validate phase3-6 closure --phase 3 --scope docs/docset/bundles/phase3.yaml --strict
      - name: Validate Phase 4-6 closure packs
        run: |
          thegent-validate phase3-6 closure --phase 4 --scope docs/docset/bundles/phase4.yaml --strict
          thegent-validate phase3-6 closure --phase 5 --scope docs/docset/bundles/phase5.yaml --strict --require continuity
          thegent-validate phase3-6 closure --phase 6 --scope docs/docset/bundles/phase6.yaml --strict --require next-phase-ready
      - name: Validate crosswave handoff gates
        run: |
          thegent-validate crosswave --source docs/docset/thegent-phase3-6-crosswave-bridge-and-continuity-plan.md --phase 10
```

### 7.2 PR gate policy

- On any failing `FAIL/BLOCK` result: fail the PR.
- On `WARN`: block production label required or waiver label required.
- On `PASS`: allow merge if all required signoff checks pass.

## 8) Issue-board automation hooks

### 8.1 Hook events

| Event | Input | Action |
|---|---|---|
| `wp_pack_created` | closure_pack.json | queue validation job |
| `wp_pack_updated` | updated evidence/artifacts | rerun validation for affected WP |
| `wp_pack_closed` | final decision submitted | emit gate-ready event |
| `continuity_scan_failed` | crosswave mismatch | force `HOLD` label |
| `manual_override_requested` | override reason | require multi-role approval |

### 8.2 Automated comment payload

```text
Closure validation result for WP-0608:
result=PASS, score=0.97, next_phase=phase7_ready=true
evidence_files=8, drift_active=false, rollback_tested=true
action=ready_for_gate
run_id=run-2026-02-15-001
```

### 8.3 State mapping to tracker lanes

- `Planned` if no pack exists
- `Ready` if pack parsed and mandatory fields present
- `In Review` if validation result is `WARN`
- `Bundle QA` if result is `PASS` and no rollback dependency
- `Ready for Gate` if phase-level gate checks passed
- `Done` only when all signatures recorded and next-phase readiness confirmed

## 9) Hard-stop and exception behavior

### 9.1 Hard-stop conditions

- missing rollback token
- active drift with unresolved P1/P0
- invalid continuity check for phase 6

### 9.2 Exception behavior

- exception entries require:
  - owner
  - expiry timestamp
  - reason code (`DOCS_OVERRUN`, `ENV_VARIANCE`, `MIGRATION_WINDOW`)
  - dual approval IDs
- exception check is denied if expiry < now
- emergency override auto-expires in 2h unless renewed by governance lead + platform lead

## 10) Artifact checks (detailed)

### 10.1 Evidence evidence

- file exists
- checksum present
- created timestamp in window
- scope matches phase+bundle

### 10.2 Test evidence

- `tests_required` not empty
- all `tests_required` represented in `tests_run`
- all required tests have status `passed`

### 10.3 Signoff evidence

- required signoffs present based on phase
- timestamp not older than 30 days
- decision field not stale

### 10.4 Continuity evidence

- bridge lock fields present
- policy version present for phase5/6
- next_phase_readiness explicit with reason note

## 11) Batch audit output format

```json
{
  "run_id": "batch-2026-02-15-001",
  "scope": "docs/docset/bundles/phase6.yaml",
  "started_at": "2026-02-15T00:00:00Z",
  "summary": {
    "total": 10,
    "pass": 8,
    "warn": 1,
    "fail": 1,
    "block": 0
  },
  "top_violations": [
    {"wp_id": "WP-0609", "code": "DRIFT_ACTIVE", "severity": "P1"}
  ]
}
```

## 12) Integration with PRD→WBS/DAG contract tools

- phase3-6 validator outputs are fed into:
  - `thegent-phase10-12-prd-wbs-dag-ticket-validation.md`
  - `thegent-phase3-6-crosswave-bridge-and-continuity-plan.md`
  - `thegent-phase10-12-master-traceability-ledger.md`
  - `thegent-phase10-12-prd-wbs-crossmap-finalization.md`

Any transition failure must include corresponding issue references in issue board for traceability.

## 13) Suggested repository layout (for implementation)

```text
scripts/
  validate/
    phase3_6_closure.py
    phase3_6_batch.py
    crosswave_check.py
  schema/
    phase3_6_closure_contract.json
  hooks/
    board_state_mapper.py
    event_dispatcher.py
.github/workflows/
  phase3-6-closure-validation.yml
```

## 14) Deployment strategy

- phase 1: dry-run validator in CI (non-blocking)
- phase 2: warnings to issue comments only
- phase 3: enforce hard fail on FAIL/BLOCK
- phase 4: require explicit approvals for WARN in production paths

## 15) Exit criteria

- all phase3–6 closure packs pass `PASS` or controlled `WARN` with waiver
- no stale exceptions
- no unresolved P1/P0 blockers blocking phase transitions
- crosswave checks pass before Phase 10 artifact freeze

