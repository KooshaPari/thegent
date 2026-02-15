# Thegent Phase 3–6 Closure Acceptance Contract Schema

**Status:** Operational specification  
**Date:** 2026-02-15  
**Scope:** Formal schema and validation contract for closing Phase 3–6 work packages before enabling later phase transitions.

## 1) Purpose

Phase 3–6 has broad governance, routing, and reliability foundations. Closure must be deterministic, not subjective.

This contract defines:

- machine-checkable closure fields
- required evidence and gate conditions
- mandatory continuity guarantees for transitions into later phases
- reviewability constraints to avoid ambiguous signoff

## 2) Inputs and canonical artifacts

- `thegent-phase3-6-full-depth-execution-prd.md`
- `thegent-wbs-final.md`
- `thegent-dag-final.md`
- `thegent-prd-test-plan` and `PRD_TEST_PLAN_MATRIX.md`
- `thegent-phase10-12-crosswave-bridge-and-continuity-plan.md`
- `thegent-phase10-12-prd-wbs-crossmap-finalization.md`
- `thegent-phase10-12-master-traceability-ledger.md` (for downstream continuity)

## 3) Required closure object model

Each phase-3–6 closure submission must include:

- `bundle_id`
- `phase`
- `wp_id`
- `wp_title`
- `owner_team`
- `completion_timestamp`
- `evidence_pack`
- `test_pack`
- `signoff_pack`
- `continuity_pack`
- `governance_pack`
- `risk_pack`
- `rollback_pack`
- `drift_pack`
- `validation_result`
- `next_phase_readiness`

## 4) JSON schema (authoritative)

```json
{
  "phase": 3,
  "bundle_id": "phase3_bundle_x",
  "wp_id": "WP-0305",
  "wp_title": "string",
  "owner_team": ["team_a", "team_b"],
  "completion_timestamp": "2026-02-15T00:00:00Z",
  "evidence_pack": {
    "artifacts": [
      {
        "artifact_path": "artifacts/phase3/wp-0305-report.md",
        "type": "markdown|json|ndjson|yaml",
        "sha256": "hex",
        "created_at": "2026-02-15T00:00:00Z",
        "evidence_scope": "unit|integration|manual|security|operational",
        "run_id": "optional"
      }
    ],
    "coverage_ratio": 1.0,
    "critical_missing": []
  },
  "test_pack": {
    "tests_required": ["TestA", "TestB"],
    "tests_run": [
      {"name": "TestA", "status": "passed|failed|blocked", "evidence": "artifacts/.."}
    ],
    "test_coverage": {
      "line": 0.0,
      "branch": 0.0,
      "requirement_coverage": 0.0
    },
    "pass": true
  },
  "signoff_pack": {
    "platform_lead": {"name": "alice", "timestamp": "2026-02-15T00:00:00Z", "decision": "approved"},
    "governance_lead": {"name": "bob", "timestamp": "2026-02-15T00:00:00Z", "decision": "approved"},
    "qa_lead": {"name": "carol", "timestamp": "2026-02-15T00:00:00Z", "decision": "approved"},
    "security_signoff": {"name": "dave", "timestamp": "2026-02-15T00:00:00Z", "decision": "not_required|approved"},
    "exceptions": [{"code": "EXC-001", "approved_by": "governance_lead", "expires_at": "2026-02-20T00:00:00Z"}]
  },
  "continuity_pack": {
    "legacy_contracts_preserved": true,
    "bridging_rules_valid": true,
    "crosswave_risks": [
      {"risk_id": "CR-01", "level": "low|medium|high", "owner": "owner_id", "mitigation": "text"}
    ],
    "continuity_checks_passed": 5,
    "continuity_checks_failed": 0
  },
  "governance_pack": {
    "governance_version": "v1",
    "policy_version": "phase3_6_gov_vX",
    "deviation_log": [
      {"id": "DEV-123", "status": "resolved", "owner": "owner_id", "date": "2026-02-15"}
    ]
  },
  "risk_pack": {
    "open_risks": [
      {"id": "R-001", "severity": "P0|P1|P2|P3", "owner": "owner_id", "mitigation": "text"}
    ],
    "mitigated_count": 3,
    "critical_risks": 0
  },
  "rollback_pack": {
    "rollback_token_required": true,
    "rollback_token": "rtb-phase3-6-wp0305",
    "rollback_procedure": "docs/rollback/runbook.wp-0305.md",
    "rollback_tested": true,
    "rollback_window_minutes": 60
  },
  "drift_pack": {
    "last_drift_scan": "2026-02-15T00:00:00Z",
    "drift_active": false,
    "active_drift_items": [],
    "resolution_plan": []
  },
  "validation_result": {
    "validator": "thegent-phase3-6-closure-acceptance-validator",
    "schema_version": "v2026.02.15",
    "result": "PASS|WARN|FAIL|BLOCK",
    "violations": [
      {"field": "evidence_pack.coverage_ratio", "message": "insufficient evidence", "severity": "P1"}
    ]
  },
  "next_phase_readiness": {
    "phase7_ready": true,
    "phase10_readiness_note": "No crosswave violations expected",
    "handoff_notes": ["brief summary", "known risks", "open tasks"]
  }
}
```

## 5) Mandatory fields by phase band

### 5.1 Phase 3

Minimum required:

- test_pack.tests_required non-empty
- signoff_pack.platform_lead + governance_lead
- continuity_pack.legacy_contracts_preserved = true

### 5.2 Phase 4

Minimum required:
- test_pack.pass = true
- continuity_pack.crosswave_rules_valid = true
- rollback_pack.rollback_tested = true

### 5.3 Phase 5

Minimum required:
- governance_pack.governance_version pinned
- drift_pack.drift_active = false or explicit P2+ issue
- next_phase_readiness.phase7_ready = true

### 5.4 Phase 6

Minimum required:
- all role signoffs plus closure evidence checksum
- risk_pack.critical_risks = 0 or exception log with expiry
- continuity checks failed = 0 for closure lane

## 6) Closure decision matrix

| Matrix field | PASS threshold | WARN threshold | FAIL/block threshold |
|---|---:|---:|---:|
| evidence_pack.coverage_ratio | >= 0.95 | 0.85–0.94 | < 0.85 |
| continuity_checks_failed | 0 | 1 | > 1 |
| open P1/P2 risks | 0 | 1 | >1 |
| rollbacks available | true | true (with caveat) | false |
| drift_pack.drift_active | false | true (deviation filed) | true + P1/P0 |

## 7) Rule ordering (deterministic)

1. schema parse
2. required fields check
3. evidence coverage check
4. test coverage check
5. role signoff check
6. continuity check
7. drift check
8. rollback readiness check
9. next-phase handoff check

No later rule may be skipped.

## 8) Validation pseudocode

```python
def validate_closure(obj):
    if not required_fields(obj):
        return fail("missing_fields")
    if obj["evidence_pack"]["coverage_ratio"] < 0.95:
        return fail("low_coverage")
    if obj["test_pack"]["pass"] is not True:
        return fail("tests_failed")
    if not all_signoffs_present(obj["signoff_pack"], obj["phase"]):
        return fail("missing_signoff")
    if not obj["continuity_pack"]["legacy_contracts_preserved"]:
        return fail("continuity_regressed")
    if obj["drift_pack"]["drift_active"] and has_blocker(obj["drift_pack"]):
        return fail("drift_blocker")
    if not obj["rollback_pack"]["rollback_tested"]:
        return fail("rollback_untested")
    return ok("PASS")
```

## 9) Cross-reference consistency checks

- `wp_id` must exist in `thegent-wbs-final.md`
- `bundle_id` must exist in chunk plan mapping
- every `artifact_path` must exist and pass checksum
- any deviation must have a bounded exception id
- any `next_phase_readiness` block must contain both closure and risk notes

## 10) Interface to phase 10–12 continuation

Phase 3–6 closure outputs must feed phase 10–12 continuity inputs:

- WPS with unresolved `drift_pack.drift_active` cannot be treated as closed in `thegent-phase10-12-master-traceability-ledger.md`.
- missing `policy_version` prevents policy contract inheritance.
- low `test_coverage.requirement_coverage` cannot be overwritten by later-phase claims.

## 11) Data export format

Export one compact NDJSON record per WP:

```json
{"phase":3,"wp_id":"WP-0301","result":"PASS","coverage_ratio":0.98,"drift":false,"next_phase_ready":true}
```

## 12) Audit and immutable logs

- emit signed closure event
- store validation payload and report
- maintain monotonic sequence id
- append to closure audit trail with decision hash

## 13) Exception governance

Allowed exception reasons:

- `DOCS_OVERRUN` (timing only)
- `ENV_VARIANCE` (external dependency delay)
- `MIGRATION_WINDOW` (approved temporary constraint)

Each exception must have:
- owner
- explicit expiry
- approval roles: platform + governance

Without exception, result is `FAIL`.

## 14) Acceptance contract output

Expected output statuses:

- `PASS` -> closure package final and promotable
- `WARN` -> closure package valid only with explicit waiver (expires in 24h)
- `FAIL` -> no phase transition
- `BLOCK` -> rollback and continuity remediation required before any advance

## 15) Exit criteria for phase 3–6 closure package

- schema version and validator version are recorded
- all mandatory fields present
- all P0/P1 blockers resolved or exception-approved
- audit trail hash exists and is signed
- next phase readiness explicitly set for phase7 and phase10 handoff lanes

If exit criteria fail:

- lock phase transition
- publish remediation package
- rerun this schema with updated evidence before retrying
