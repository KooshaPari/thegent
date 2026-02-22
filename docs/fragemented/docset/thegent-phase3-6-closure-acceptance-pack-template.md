# Thegent Phase 3–6 Closure Acceptance Pack Template

**Status:** Operational template
**Date:** 2026-02-15
**Scope:** Standardized closure package for phase 3–6 WPs to produce deterministic handoff into later waves.

## 1) Pack header

```text
Pack ID: THR-3-6-CL-XXXX
WP: WP-0XYZ
Phase: 3 | 4 | 5 | 6
Bundle: phase3_bundle_a | phase4_bundle_b | phase5_bundle_c | phase6_bundle_d
Owner: ____________________
Completion timestamp: ____________________
Validator: thegent-phase3-6-closure-acceptance-contract-validator
```

## 2) Evidence manifest (required)

| Artifact | Path | Type | SHA | Created | Scope | Proof |
|---|---|---|---|---|---|---|
| Design evidence | `artifacts/phase3-6/<wp>/design.md` | markdown | | | requirements | |
| Implementation evidence | `artifacts/phase3-6/<wp>/implementation.ndjson` | ndjson | | | changes | |
| Test evidence | `artifacts/phase3-6/<wp>/tests.ndjson` | ndjson | | | tests | |
| Safety evidence | `artifacts/phase3-6/<wp>/safety.json` | json | | | hard-stop/rollback | |
| Drift evidence | `artifacts/phase3-6/<wp>/drift_report.json` | json | | | drift checks | |
| Signoff evidence | `artifacts/phase3-6/<wp>/signoff.md` | markdown | | | governance | |

## 3) Closure criteria checklist

### 3.1 Completion criteria

- [ ] All planned implementation tasks for WP completed
- [ ] All required tests in scope are passing
- [ ] All evidence artifacts present and checksummed
- [ ] All open risks at P1/P2 are explicitly mitigated or exception-approved
- [ ] Rollback token exists and rollback procedure validated

### 3.2 Coverage criteria

- [ ] Requirement coverage ratio >= 0.95
- [ ] Test requirement coverage >= 0.95
- [ ] All FR mappings validated against WBS
- [ ] All mandatory non-functional checks pass

### 3.3 Governance criteria

- [ ] Platform lead signoff completed
- [ ] Governance lead signoff completed
- [ ] QA signoff completed
- [ ] Security signoff present if risk classification is P1+
- [ ] No unresolved drift blocker at P1 or above

## 4) Signoff block

```text
Signoff status:
- Platform lead: approved / rejected / pending
- Governance lead: approved / rejected / pending
- QA lead: approved / rejected / pending
- Security lead: approved / rejected / pending
- Timestamp: ______________________
- Approval correlation id: ______________________
```

## 5) Risk and continuity section

### 5.1 Open risk register

| Risk ID | Severity | Owner | Mitigation | ETA | Residual |
|---|---|---|---|---|---|
| R-001 | P0/P1/P2/P3 |  |  |  |  |
| R-002 |  |  |  |  |  |

### 5.2 Continuity risk register

| Continuity ID | Type | Severity | Owner | Mitigation | State |
|---|---|---|---|---|---|
| CR-01 | contract | low/med/high |  |  | open/resolved |
| CR-02 | governance | low/med/high |  |  | open/resolved |

## 6) Drift status

```text
Last drift scan: ____________________
Active drift: yes / no
Active drift items:
- [ ] item-01: ____________________
- [ ] item-02: ____________________
Resolution notes:
___________________________
___________________________
```

If drift is active:

- [ ] Drift owner assigned
- [ ] Corrective timeline defined
- [ ] Exit criteria for each drift item documented
- [ ] Exception attached (if required and timeboxed)

## 7) Test results block

### 7.1 Required tests

- Required test list:
  - `test_1`
  - `test_2`
  - `test_3`

### 7.2 Executed tests

| Test | Result | Evidence path | Failure root cause | Re-run status |
|---|---|---|---|---|
|  | passed/failed/block |  |  | not_run/retry_passed/retry_failed |
|  |  |  |  |  |

## 8) Continuity checks

- [ ] WBS identity preserved (`WP` IDs unchanged unless migration approved)
- [ ] DAG edge consistency checked
- [ ] PRD-FR link remains traceable
- [ ] Legacy gating assumptions preserved
- [ ] Any changed assumption has migration note + date

## 9) Rollback readiness check

- Rollback token: `_________________________________`
- Rollback procedure path: `_________________________________`
- Rollback validation evidence:
  - [ ] rollback dry-run executed
  - [ ] rollback duration measured
  - [ ] rollback exit cleanup checklist complete

Rollback readiness score:

- [ ] 0-3 min
- [ ] 4-10 min
- [ ] 11-30 min
- [ ] > 30 min (requires governance exception)

## 10) Next phase handoff

### Phase 7–9 handoff

- `phase7_ready`: yes / no
- Open preconditions:
  - [ ] contract continuity lock
  - [ ] governance lock
  - [ ] evidence continuity lock

### Phase 10–12 handoff (if applicable)

- `phase10_ready`: yes / no
- Cross-wave checks:
  - [ ] continuity schema passed
  - [ ] bridge contract checklist included
  - [ ] hard-stop inheritance validated

## 11) Exception handling

Exception required if any `WARN` entry exists:

- Exception code: `_____________________`
- Exception rationale:
  - [ ] external dependency delay
  - [ ] temporary migration window
- Approval:
  - governance lead: ______________________
  - platform lead: ______________________
- Expiry:
  - [ ] 24h
  - [ ] 48h
  - [ ] longer (requires committee)

## 12) Final closure declaration

```text
Closure decision:
- Decision: PASS / WARN / FAIL
- Approver set: [names]
- Correlation ID: [uuid]
- Validity: [standard / temporary waiver]

I confirm:
- evidence is complete
- risks are bounded
- rollbacks are available
- next phase preconditions are met and documented
```

## 13) Appendix A — Minimum machine parse fields

At minimum these fields must be parseable by the closure validator:

- `phase`, `wp_id`, `bundle_id`, `completion_timestamp`
- `evidence_pack.coverage_ratio`
- `test_pack.pass`
- `signoff_pack.platform_lead.decision`
- `signoff_pack.governance_lead.decision`
- `signoff_pack.qa_lead.decision`
- `continuity_pack.legacy_contracts_preserved`
- `rollback_pack.rollback_token`
- `rollback_pack.rollback_tested`
- `drift_pack.drift_active`
- `validation_result.result`

## 14) Appendix B — Reviewer quick-start

For reviewers:

1. Verify all required evidence SHA fields are present.
2. Confirm test list includes all FR-related tests.
3. Verify crosswave continuity checks.
4. Verify rollback token exists.
5. Confirm all required signoff fields are set and time-bounded.

If any item fails, set decision to `FAIL` unless a waiver block is explicit and within policy.

## 15) Appendix C — Example accepted package

```text
Pack ID: THR-3-6-CL-0007
WP: WP-0608
Phase: 6
Bundle: phase6_bundle_d
Decision: PASS
Evidence coverage: 0.97
Risk score: 0
Drift: none
Rollback tested: yes
Phase7 ready: yes
```



---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index
