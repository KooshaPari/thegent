# Thegent Phase 3-6 Closure Validator Runtime CLI and Adapter Playbook

**Status:** Execution blueprint  
**Date:** 2026-02-15  
**Scope:** Convert the phase 3-6 validator contracts into runnable CLI commands, policy execution paths, and tracker connectors.

## 1) Purpose

This document turns the phase 3-6 validator family into a deterministic runtime product:

- concrete CLI entry points and argument contracts,
- stable JSON/NDJSON output formats,
- deterministic error/exit handling,
- adapter interfaces for issue boards and external task systems,
- rollout plan from shadow mode to hard-gate enforcement.

Use this document after `...automation-package` and `...implementation-blueprint`.

## 2) Inputs and dependencies

Inputs:

- `thegent-phase3-6-closure-validator-schema-v1.json`
- `thegent-phase3-6-closure-acceptance-contract-schema.md`
- `thegent-phase3-6-closure-validator-event-and-waiver-contract-v1.md`
- `thegent-phase3-6-closure-acceptance-pack-template.md`
- `thegent-phase3-6-closure-validator-automation-package.md`

Existing code touchpoints:

- `src/thegent/cli.py` for command registration.
- `scripts/validate/*.py` for runtime implementation modules (proposed).
- `scripts/events/*.py` for event emission validation.
- `.github/workflows/` for gate enforcement.
- issue-board connectors used by policy and automation flows.

## 3) Design principles

### 3.1 Deterministic first

Every command must produce byte-stable output for identical inputs:

- deterministic JSON key ordering,
- sorted violation arrays,
- canonical hash seeds,
- explicit timestamps in UTC.

### 3.2 Non-fragile contracts

Contracts are versioned and never silently changed:

- pack payload uses schema `phase3-6-closure-schema-v1`,
- events use `phase3-6-closure-event-v1`,
- all commands default to strict deny-mode for unknown fields in critical gates.

### 3.3 Adapter tolerant, core strict

Core engine runs with strict mode always enabled for core invariants;
adapters may transform between external systems and the canonical model, but cannot bypass checks.

## 4) Recommended file and module layout

```text
src/thegent/
├── cli.py
└── ...existing command entrypoints...

scripts/
├── validate/
│   ├── closure_runtime.py
│   ├── phase3_6_closure.py
│   ├── phase3_6_batch.py
│   └── crosswave_check.py
├── events/
│   ├── schema.py
│   ├── emit.py
│   ├── validate.py
│   └── signatures.py
├── board/
│   ├── connector.py
│   ├── zen_adapter.py
│   ├── task_tool_adapter.py
│   ├── crun_adapter.py
│   └── tracker_router.py
└── io/
    ├── schema.py
    ├── checksums.py
    └── policy.py

docs/config/
├── phase3-6-closure-validator-policy.yaml
└── phase3-6-closure-validator-scope-template.yaml
```

## 5) CLI command contract

Recommended command prefix for consistency with current repo:

- `thegent validate closure ...` (preferred).
- `thegent-validate ...` wrapper for backward compatibility when needed.

All commands support:

- `--run-id`
- `--trace-id`
- `--json`
- `--strict`
- `--dry-run`
- `--log-level`
- `--timeout-seconds`

### 5.1 `validate closure wp`

Validates one WP closure pack.

```bash
thegent validate closure wp \
  --wp WP-0608 \
  --pack artifacts/phase3-6/WP-0608/closure_pack.json \
  --schema docs/docset/thegent-phase3-6-closure-validator-schema-v1.json \
  --policy docs/config/phase3-6-closure-validator-policy.yaml \
  --json
```

#### Parameters

- `--wp` required. Must match canonical `WP-` pattern.
- `--pack` path to JSON pack.
- `--schema` path or embedded version string.
- `--policy` optional config override.
- `--continuity` bool. If true, enforce continuity checks in phase 6 and above.
- `--next-phase-ready` bool. If true, requires readiness fields for phase transition.
- `--emit-event` bool. If true, writes `closure.validation.result` and optional `closure.validation.failed`.
- `--event-out` output path for event NDJSON.
- `--score` if true, include numeric scoring object.

### 5.2 `validate closure scope`

Validates a phase scope file containing one or more WPs.

```bash
thegent validate closure scope \
  --scope docs/config/phase6-scope.yaml \
  --phase 6 \
  --strict \
  --parallelism 4 \
  --require-continuity \
  --require-next-phase-ready \
  --json
```

### 5.3 `validate closure crosswave`

Crosswave readiness and continuity check before phase migration.

```bash
thegent validate closure crosswave \
  --source docs/docset/thegent-phase3-6-crosswave-bridge-and-continuity-plan.md \
  --target notes/thegent-phase10-12-readiness-pack.md \
  --json
```

### 5.4 `validate closure waiver`

Lifecycle operations for WARN waivers:

- `list`
- `request`
- `approve`
- `reject`
- `close`

### 5.5 `validate closure board`

Board synchronization operations:

- `sync-state`: read command artifacts and sync gate states.
- `drift`: reconcile current state vs ledger.
- `lock`/`unlock`: manual gates.

## 6) CLI output contract

When `--json` is supplied, commands return one of:

- `thegent-validate` single-run object
- `thegent-validate-batch` summary object
- per-line NDJSON for large batches

### 6.1 Single run output schema

```json
{
  "run_id": "run-2026-02-15-0001",
  "tool_version": "closure-validator-v1.0.0",
  "schema_version": "phase3-6-closure-schema-v1",
  "command": "validate closure wp",
  "wp_id": "WP-0608",
  "phase": 6,
  "result": "PASS",
  "result_code": "CLOSE-OK",
  "score": {
    "evidence_ratio": 0.97,
    "test_ratio": 1.0,
    "risk_score": 0.0
  },
  "can_transition": true,
  "violations": [],
  "checks": [
    {
      "name": "schema_validate",
      "status": "PASS",
      "duration_ms": 23,
      "details": "conforms to schema"
    }
  ],
  "timing": {
    "started_at": "2026-02-15T00:00:00Z",
    "ended_at": "2026-02-15T00:00:03Z",
    "duration_ms": 3000
  },
  "artifacts": {
    "pack_sha256": "ab12...",
    "report_path": "artifacts/phase3-6/validation/run_...",
    "event_path": "artifacts/phase3-6/events/closure_events_..."
  }
}
```

### 6.2 Batch output schema

```json
{
  "run_id": "batch-2026-02-15-001",
  "scope": "phase6",
  "total": 3,
  "pass": 1,
  "warn": 1,
  "fail": 1,
  "block": 0,
  "top_violations": [
    {
      "code": "SIGNOFF_MISSING",
      "wp_id": "WP-0603",
      "severity": "P1",
      "message": "Security signoff required for phase 6 with critical risk"
    }
  ],
  "results": [
    { "wp_id": "WP-0602", "result": "PASS" },
    { "wp_id": "WP-0603", "result": "FAIL" }
  ],
  "decisions": {
    "merge_gates": "HOLD",
    "recommended_action": "request_security_signoff"
  }
}
```

## 7) Exit codes

Use exact exits for CI integration:

- `0` PASS and can transition.
- `1` PASS or WARN with advisory only.
- `2` WARN requiring waiver workflow.
- `3` FAIL hard block. merge must stop.
- `4` BLOCK hard stop.
- `5` Schema or integrity validation error.
- `6` Timeout.
- `7` Runtime/system error.

CI should typically fail when exit code `>=3`.

## 8) Validation workflow algorithm

For both single WP and scope:

1. Load policy and schema.
2. Parse and validate JSON against schema.
3. Recompute canonical hash and compare if present.
4. Normalize artifact references:
   - local file existence check,
   - `sha256` checksum check,
   - timestamp recency check.
5. Validate evidence and test completeness.
6. Validate signoff phase requirements.
7. Validate continuity and next-phase readiness if requested.
8. Validate drift and rollback readiness.
9. Aggregate violations and map severity.
10. Compute result and can_transition.
11. Emit event package and summary report.

Every step should record:

- checker name,
- start/end duration,
- pass/warn/fail reason,
- blocking code.

## 9) Severity mapping and merge policy

Map violation severity as follows:

- `P0`, `P1` -> `BLOCK`.
- `P2` -> `FAIL` unless explicit waiver exists and policy allows.
- `P3` -> `WARN` if advisory scope; escalate to `WARN` only once and deduplicate.
- Unmapped severities -> `FAIL` with code `SEVERITY_UNKNOWN`.

Result policy:

- `PASS`: no blocker codes, no unresolved critical risks.
- `WARN`: no blocker codes, unresolved medium residual allowed with governance review.
- `FAIL`: unresolved medium/high if policy strictness requires.
- `BLOCK`: unresolved P0/P1, missing mandatory signoffs, schema violation, missing continuity fields in phase 6.

## 10) Policy engine and config schema

`docs/config/phase3-6-closure-validator-policy.yaml` should include:

```yaml
schema_version: phase3-6-closure-schema-v1
strict_mode_default: false
scores:
  evidence_pass_min: 0.95
  evidence_warn_min: 0.85
  continuity_failed_max: 1
  risk_critical_max: 0
timeouts:
  drift_scan_minutes: 60
  result_ttl_hours: 24
event:
  version: phase3-6-closure-event-v1
  emit_on: ["result","fail","warn","waiver"]
checks:
  require_test_pass: true
  require_crosswave_ready: false
  require_rollback_tested: true
```

### 10.1 Runtime overrides

CLI `--strict` should override policy strictness.

`--next-phase-ready` should raise risk score threshold one level for:

- phase 4+ readiness fields,
- phase 6 continuity lock fields.

## 11) Scope file schema

`docs/config/phase3-6-closure-validator-scope-template.yaml`

```yaml
name: phase6_bundle_d
phase: 6
bundles:
  - phase6_bundle_d
wp_ids:
  - WP-0601
  - WP-0602
  - WP-0603
requirements:
  strict_mode: true
  require_continuity: true
  require_next_phase_ready: true
  require_rollback_tested: true
  max_parallelism: 4
```

## 12) Adapter contract for issue boards and task systems

The validator must work with both strict APIs and external systems.

### 12.1 Canonical internal transition model

Internal event payload:

- `wp_id`
- `result` (`PASS/WARN/FAIL/BLOCK`)
- `can_transition`
- `blocking_codes`
- `required_actions`
- `next_state`

### 12.2 Connector interface

Every connector must implement:

- `probe()`: health and auth check.
- `read_issue(wp_id)`.
- `set_state(issue_id, state, reason)`.
- `add_comment(issue_id, text)`.
- `set_labels(issue_id, labels)`.
- `append_worklog(issue_id, entry)`.
- `close_waiver(issue_id, code)`.
- `emit_event(event)`.

If connector returns partial failure, retry with idempotency by `correlation_id`.

### 12.3 zen adapter

Use canonical command mapping:

- parse `<TaskUpdate>` root and tolerant tags into canonical fields when needed.
- support both CamelCase and snake_case naming where legacy payloads exist.
- preserve raw XML fragment hash for audit.
- when parse confidence is lower than policy threshold, emit `closure.validation.failed` with `EVENT_PARSE_LOW_CONFIDENCE`.

### 12.4 task-tool adapter

Task-tool historical mismatch indicates both `<TaskUpdate>` and `task_graph` naming variants have appeared.

- treat both shapes as inbound candidates,
- validate into canonical form before validation checks,
- reject packets with unsupported root tags in strict mode.

### 12.5 crun adapter

Map plan nodes to closure WP IDs:

- `crun` node identifiers must map to WP IDs.
- required resource/consistency fields should pass to `risk_pack` only as evidence context, never replacing canonical checks.

### 12.6 board state rules

State mapping:

- PASS -> `Ready for Gate`
- WARN -> `In Review`
- FAIL -> `Hold`
- BLOCK -> `Hold + incident`

`can_transition=false` always overrides state recommendations.

## 13) Event emission and waiver behavior

Event contract remains:

- `closure.validation.result`
- `closure.validation.batch.result`
- `closure.validation.failed`
- `closure.waiver.requested`
- `closure.waiver.approved`
- `closure.waiver.rejected`
- `closure.override.triggered`
- `closure.drift.detected`
- `closure.crosswave.blocked`

### 13.1 Event signing

Phase 3 CLI mode: event signatures optional.

Phase 3.3 runtime: signatures mandatory.

Signer requirements:

- stable key id,
- rotated daily if available,
- hash algorithm `sha256`,
- reject unsigned events when strict mode true.

## 14) CI/CD gate behavior

Repository `.github/workflows/phase3-6-closure-validation.yml` should:

1. run command in non-blocking dry mode on PR open,
2. run `validate closure scope` for phase 3 and 4 in advisory mode,
3. run phase 5/6 in strict fail mode for protected branches,
4. enforce hard-stop on exit `>=3`,
5. require explicit waiver label for exit `2`,
6. attach batch summary artifact.

Example:

```yaml
if: github.event_name == 'pull_request'
runs-on: ubuntu-latest
steps:
  - run: python scripts/validate/phase3_6_batch.py --phase 3 --scope ...
  - run: python scripts/validate/phase3_6_batch.py --phase 4 --strict --scope ...
  - run: python scripts/validate/phase3_6_batch.py --phase 5 --strict --require-continuity --scope ...
  - run: python scripts/validate/phase3_6_batch.py --phase 6 --strict --require-continuity --require-next-phase-ready --scope ...
```

## 15) Deterministic artifact naming and retention

Use folder conventions:

- `artifacts/phase3-6/validation/validation_<run_id>_wp_<wp>.json`
- `artifacts/phase3-6/validation/batch_<run_id>.json`
- `artifacts/phase3-6/events/closure_events_<run_id>.ndjson`
- `artifacts/phase3-6/exceptions/<run_id>_exceptions.ndjson`

Retention default:

- validation artifacts: 90 days,
- event NDJSON: 30 days,
- exception log: 180 days.

## 16) Concurrency and performance contract

### 16.1 Scope concurrency

- default parallelism: 4
- max parallelism: 16
- lock contention retry: exponential backoff with jitter
- per-pack timeout: 30s

### 16.2 Performance targets

- 95th percentile single WP < 20s in warm environment.
- 95th percentile batch of 10 WPs < 120s.
- event emission latency < 2s median.

## 17) Security and robustness hardening

- validate all file paths under repo root or explicit allowlist,
- disallow shell execution from pack content,
- mask secrets in logs and reports,
- enforce JSON schema before command execution side effects,
- checksum all output files,
- never persist raw API tokens in event payloads,
- zeroize signer keys from memory as soon as signed.

## 18) Testing strategy

### 18.1 Unit tests

- schema validation with good/bad packs,
- policy overrides and strictness,
- event payload generation,
- exit code mapping,
- idempotency key behavior.

### 18.2 Integration tests

- single WP and scope validation,
- board connector failover and retries,
- crosswave blocked/ready transitions,
- waiver lifecycle states.

### 18.3 Recovery tests

- transient artifact file loss,
- corrupted manifest,
- timeout and partial write recovery,
- stale waiver expiry auto-fail.

### 18.4 Smoke tests

- `thegent validate closure wp ... --dry-run`
- `thegent validate closure scope --phase 6`
- `thegent validate closure crosswave ...`

## 19) Implementation chunks

### Chunk A: Runtime core

- Implement `scripts/validate/phase3_6_closure.py` and strict check pipeline.
- Ensure canonical ordering and deterministic output.
- Add unit coverage for all check functions.

### Chunk B: Batch and policy

- Implement scope parser + policy loader.
- Add concurrency limits and summary rollups.
- Add artifact naming + retention writes.

### Chunk C: Events and waivers

- Implement event schemas and signatures.
- Add waiver request/approve/reject command path.
- Add synthetic events for expiry.

### Chunk D: Connectors

- Implement adapter base and at least one active connector.
- Add zen/task-tool/crun compatibility mode behind feature flags.
- Add reconciliation dry-run.

### Chunk E: CLI integration

- Add commands in `src/thegent/cli.py` and `src/thegent/cli_impl.py`.
- Add integration tests for command parsing and nonzero exit behavior.
- Add command-level JSON output examples.

### Chunk F: CI and rollout

- Add `.github/workflows/phase3-6-closure-validation.yml`.
- Introduce branch-based strictness.
- Add emergency bypass guard with governance override.

## 20) Rollout plan

1. Week 1: command/runtime core in dry-run mode.
2. Week 2: batch validator + reporting.
3. Week 3: board bridge with advisory mode.
4. Week 4: strict branch gates + waiver approvals.
5. Week 5: crosswave migration dry-check and hard-stop.

## 21) Completion criteria for this chunk

- At least one command set is fully usable by operators:
  - `thegent validate closure scope --phase 6`
- Deterministic output validated in CI for 10+ fixtures.
- At least one nontrivial board connector emits transition events.
- crosswave check can block and unblock via explicit evidence updates.



---
## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](../plans/00-MASTER-INDEX.md) — plan index

