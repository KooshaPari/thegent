# Thegent Phase 10–12 Compact Execution Dashboard

**Status:** Operational control artifact
**Date:** 2026-02-15
**Scope:** One-pane governance and execution view for Phases 10–12 with a machine-readable schema, scoring model, and action automation.

## 1) Purpose

This dashboard is the minimum viable control surface for running final three phases without re-reading the entire corpus. It combines:

- PRD ↔ WBS ↔ DAG ↔ tracker crosswalk
- Gate status (G10, G11, G12) in one view
- Dependency pressure and blocker risk
- Evidence-readiness signal to prevent premature promotion
- Hard-stop escalation triggers and rollback readies

Use this artifact whenever there is active implementation or governance contention.

## 2) Canonical data feeds (single source of truth)

Read these files once at startup and refresh every 30 minutes (or on each significant transition):

1. `thegent-wbs-phase10-12.md`
2. `thegent-phase10-12-optimal-design-prd.md`
3. `thegent-dag-phase10-12-extension.md`
4. `thegent-phase10-12-prd-wbs-crossmap-finalization.md`
5. `thegent-phase10-12-master-traceability-ledger.md`
6. `thegent-phase10-12-implementation-issue-queue.md`
7. `thegent-phase10-12-execution-workboard.md`
8. `thegent-phase10-12-hard-stop-and-rollback-matrix.md`
9. `thegent-phase10-12-closure-readiness-pack-template.md`
10. `thegent-phase10-12-issue-board-seed.json`

## 3) Dashboard schema (compact)

One row per active WP.

### 3.1 Required fields (must exist)

- `wp_id` (string)
- `phase` (10|11|12)
- `bundle` (phase10_bundle_b, phase11_bundle_c, phase11_bundle_d, phase12_bundle_e, phase12_bundle_f)
- `owner` (team or person)
- `status` (Planned | Ready | In Progress | In Review | Blocked | Bundle QA | Ready for Gate | Done)
- `gate` (G0 | G10 | G11 | G12 | none)
- `gate_readiness` (0-100)
- `dependency_state` (open | blocked | satisfied | violating)
- `blockers` (array string)
- `risk_score` (0-100)
- `next_action` (next permissible action)
- `next_action_owner` (string)
- `due_at` (ISO timestamp)
- `evidence_status` (missing | partial | complete | stale)
- `rollback_token` (string or null)
- `doD_ready` (true/false)
- `dor_ready` (true/false)
- `bundle_signoff_pending` (true/false)

### 3.2 Optional fields

- `artifact_refs` (array)
- `active_deviation` (string)
- `last_state_change_at` (ISO timestamp)
- `observed_by` (agent/pilot)
- `confidence` (0-1)
- `policy_flags` (array)

## 4) Scoring model

### 4.1 Gate readiness score

```
gate_readiness = (
  0.30 * status_weight
  + 0.25 * evidence_weight
  + 0.20 * dependency_weight
  + 0.15 * test_weight
  + 0.10 * owner_weight
) * 100
```

Where:

- `status_weight` = {Done:1.0, Ready for Gate:0.95, Bundle QA:0.85, In Review:0.70, In Progress:0.55, Blocked:0.35, Ready:0.25, Planned:0.1}
- `evidence_weight` = 1.0 when complete, 0.5 when partial, 0 when missing
- `dependency_weight` = 1.0 when satisfied, 0.6 when open, 0.0 when violating
- `test_weight` = 1.0 if all required tests have passed runbook evidence, else 0
- `owner_weight` = 1.0 if owner is active and unblocked, else 0.5

### 4.2 Risk score

```
risk_score = 100 - gate_readiness
```

This can be increased by critical conditions:

- +15 for unresolved `L2/L3` hard-stop signals in last 24h
- +10 for missing rollback token on runtime WPs
- +10 for stale evidence (older than 48h)
- +20 for external dependency delay >24h

Clamp 0..100.

## 5) Priority bands and action policy

### 5.1 Routing by status + score

| Band | Gate readiness | Action |
|---|---:|---|
| Green | ≥ 85 | Continue implementation and monitor; queue for next gate review |
| Amber | 65–84 | Freeze non-blocking changes; satisfy remaining evidences before advancing |
| Red | < 65 | Block dependent work; escalate in dashboard sync meeting |
| Critical | < 40 or hard-stop active | Execute stop actions and rollback playbook |

### 5.2 Blocker class mapping

- `X` — external blocker (waiting on external integration)
- `Y` — evidence blocker (missing artifacts / test)
- `Z` — dependency blocker (upstream WP not complete)
- `S` — safety blocker (hard-stop, policy, or rollback required)

## 6) One-page text view

Use this compact row format for real-time standups:

```text
WP | Bundle | Owner | Gate | Status | GR | Risk | Blockers | Next
```

### Example

```
WP-11003 | phase11_bundle_c | Data/Planning | G11 | Bundle QA | 82 | 18 | [Y: calibration evidence pending] | Run TestCalibrationDrift
WP-12004 | phase12_bundle_e | Orchestration | G12 | Ready for Gate | 96 | 4 | [] | Prepare handoff confidence evidence
WP-12005 | phase12_bundle_e | Governance/UX | G12 | Blocked | 38 | 48 | [S: replay safety hard-stop] | Pause ship; execute rollback ladder
```

## 7) Dashboard runtime contract

### 7.1 Refresh conditions

Refresh on:

- Issue moved to new state
- New evidence artifact uploaded
- New hard-stop warning or stop signal
- Gate review transition start/end
- Daily 08:00 UTC sync

### 7.2 Refresh output

The output artifact should be JSON for both automation and human review:

```json
{
  "generated_at": "2026-02-15T00:00:00Z",
  "run_id": "dashboard-2026-02-15-001",
  "phase_mode": "G10->G12",
  "overall_risk": 31,
  "rows": [
    {
      "wp_id": "WP-10003",
      "phase": 10,
      "bundle": "phase10_bundle_b",
      "owner": "core-runtime",
      "status": "In Review",
      "gate": "G10",
      "gate_readiness": 79,
      "dependency_state": "open",
      "blockers": ["Y: artifact dispatch_trace_index missing"],
      "risk_score": 21,
      "due_at": "2026-02-18T18:00:00Z",
      "next_action": "upload artifact",
      "next_action_owner": "platform-runtime",
      "evidence_status": "partial",
      "doD_ready": false,
      "dor_ready": true,
      "bundle_signoff_pending": false,
      "rollback_token": "rtb-10003-v3"
    }
  ]
}
```

## 8) Core control logic (pseudo)

```python
def compute_row_status(row):
    if has_hard_stop(row):
        row["status"] = "Blocked"
        return row
    if row["evidence_status"] == "missing" and row["status"] in {"Ready for Gate", "Bundle QA"}:
        row["status"] = "In Review"
    if row["dependency_state"] == "violating":
        row["status"] = "Blocked"
        row["risk_score"] = max(60, row["risk_score"])
    return row


def dashboard_aggregate(rows):
    overall = {
        "red": 0,
        "amber": 0,
        "green": 0,
        "critical": 0,
    }
    for row in rows:
        if row["gate_readiness"] < 40 or has_hard_stop(row):
            overall["critical"] += 1
        elif row["gate_readiness"] < 65:
            overall["red"] += 1
        elif row["gate_readiness"] < 85:
            overall["amber"] += 1
        else:
            overall["green"] += 1
    return overall
```

## 9) Gate-level alert matrix

### 9.1 G10 readiness watch

Trigger block if:

- Any of `WP-10001..WP-10010` is blocked by hard blocker
- Any runtime-affecting WP has missing rollback token
- Any two consecutive deterministic test fails in `TestEnvelopeToDispatchEndToEnd`

### 9.2 G11 readiness watch

Trigger watch if:

- >20% of `phase11_*` WPs are `risk_score >= 70`
- >2 control-loop safety events not yet triaged
- `thegent-prd-final.md` and `thegent-phase10-12-optimal-design-prd.md` diverge on phase-11 FR set

### 9.3 G12 readiness watch

Trigger hold if:

- Evidence graph broken for any WP-12 completion pack
- Replay mutation test failures in non-canary scope
- Any unresolved `WP-1200`-series blocker flagged after bundle F start

## 10) Suggested dashboard cadence by role

### 10.1 Platform lead (daily)

- Refresh at 08:30 UTC
- Validate all blockers in first 30 minutes
- Escalate `X` and `S` blockers immediately

### 10.2 Bundle owner (every 4 hours)

- Update three top rows only: own bundle + dependencies + dependents
- Recompute `next_action` for incomplete tasks

### 10.3 QA lead (every 2 hours during hardening)

- Cross-check evidence status for any WP in `Bundle QA` or above
- Validate evidence checksums and artifact links

## 11) Board integration pattern

When synced to GitHub/Jira/Linear:

- one dashboard row maps to one issue
- issue label set:
  - `thegent:dashboard`
  - `thegent:bundle_<id>`
  - `thegent:phase_<id>`
  - `dashboard:gr_<score>`
- pin dashboard comment every 12 hours with:
  - top 5 risks
  - top 3 blockers
  - next hard-stop candidate
  - current aggregate state

## 12) Failure modes and remediation

### 12.1 "Everything green, but gate blocked"

Likely one of:
- missing dependency evidence not in PRD crossmap
- crosswalk mismatch (WP exists in issue queue but absent from ledger)
- stale dashboard snapshot

Fix:
1. run PRD/WBS crossmap validation
2. refresh dashboard with latest source files
3. freeze promotion until both are repaired

### 12.2 "Risk score oscillates"

Likely from unstable evidence refresh or flaky control tests.

Fix:
- force deterministic evidence snapshot window
- set flaky tests to "quarantine mode" after 2 repeats
- add confidence guard: promotion only after two consecutive stable scores

## 13) Immediate use sequence (10-minute startup)

1. Build base rows from `thegent-phase10-12-master-traceability-ledger.md`.
2. Resolve all missing mandatory fields from issue queue and tracker.
3. Calculate `gate_readiness` and `risk_score`.
4. Sort by descending risk then ascending due date.
5. Publish 1-page output + machine JSON in sync channel.
6. Block any row with:
   - `risk_score >= 80`, or
   - unresolved hard-stop `S`, or
   - `doD_ready = false` with status `Ready for Gate`.

## 14) Exit criteria

This dashboard is considered effective if:

- at least 95% of WPs have complete schema rows
- all blockers have explicit owner and next_action
- hard-stop and rollback transitions are representable as one-line actions
- all gate-readiness deltas are explained in under 24h

If not, return to the compact dashboard design and enforce stricter schema validation before proceeding to bundle handoffs.


---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index
