# Thegent Phase 10–12 Issue Board Automation Playbook

**Status:** Finalized implementation-oriented playbook  
**Date:** 2026-02-15  
**Scope:** Scripted import, state sync, and gate-aware automation for GitHub/Jira/Linear from the phase10-12 seed.

This document turns `thegent-phase10-12-issue-board-seed.json` into operationally synchronized issue flows with minimal manual effort and reproducible mapping.

## 1) Automation goals

1. Generate issue entities from a single source of truth seed in deterministic order.
2. Preserve dependency semantics (`depends_on`, blockers, parent ticket links).
3. Enforce required metadata on every ticket at creation (DoR/DoD/checklist fields).
4. Drive board movement by check results and feature flags.
5. Emit import and sync logs for audit.

## 2) Minimal architecture

```text
Seed Loader -> Validator -> Normalizer -> Platform Adapter -> Issue Upsert -> Linker -> Board Sync -> Gate Auditor
```

- **Seed Loader** reads `thegent-phase10-12-issue-board-seed.json`.
- **Validator** enforces schema/version and required field invariants.
- **Normalizer** maps internal keys to tracker field schema.
- **Adapter** sends normalized payload to GitHub/Jira/Linear.
- **Linker** attaches dependency edges and bundle fields.
- **Board Sync** applies automation rules and status transitions.
- **Gate Auditor** recalculates readiness from tests/evidence state.

## 3) Seed validation checklist

Abort import on schema violations.

- `metadata.version` must be semver-like and supported.
- Every WP in `tickets` must have:
  - unique `issue_key`
  - non-empty `title`, `wp_id`, `bundle`, `phase`
  - at least one `required_test` when `dor_checks` is non-empty
  - `rollback_token`
- Every dependency must point to ticket in the same seed.
- Board columns must contain all required lanes from seed.

## 4) Field mapping (canonical source -> tracker)

| Seed field | GitHub | Jira | Linear |
|---|---|---|---|
| `issue_key` | `#` in body prefix | Issue label or custom key | ID alias / title prefix |
| `title` | Issue title | Summary | Title |
| `status` | Project status | Workflow state | State |
| `assignee` | Assignee | Assignee | Owner |
| `bundle` | Labels + custom field | Component + label | Label + team |
| `phase` | Label (`phase-10`, `phase-11`, `phase-12`) | Custom field | Custom field |
| `labels` | Labels | Labels | Labels |
| `dependencies` | Issue links (blocks/blocking) | Issue links (`blocks`) | Dependency block |
| `required_tests` | Checklist section in body + custom field `x_test_plan` | Custom field | Custom fields |
| `required_artifacts` | Checklist section in body + custom field `x_artifacts` | Custom field | Custom fields |
| `dor_checks` | Body "Definition of Readiness" | Custom field | Section body |
| `dod_checks` | Body "Definition of Done" | Custom field | Section body |
| `gate_preconditions` | `x_gates` + tags | Custom field | Custom fields |
| `evidence_manifest` | Linked file/release artifact | Attachment/URL field | Artifact link |
| `rollback_token` | `x_rollback_token` | Custom field | Custom field |

## 5) Standard payload pattern

All platforms use one normalized body template:

```md
## Work package
- WP: WP-10001
- Bundle: phase10_bundle_b
- Phase: 10

## Definition of Readiness
- ...

## Definition of Done
- ...

## Required tests
- ...

## Required artifacts
- ...

## Rollback
- rollback_token: rt-phase10-b-10001
- kill_switch: phase10.interface_v2
```

## 6) Import command model

### 6.1 One-shot import

- `--mode import`  
  Create all tickets and dependencies from seed.
- `--mode sync`  
  Update existing tickets only when metadata changed.
- `--mode dry-run`  
  Parse and validate without writing any changes.

### 6.2 Recommended CI pipeline

1. `validate-seed` job on every PR touching `thegent-phase10-12-issue-board-seed.json`.
2. `sync-issues --provider=gh` in staging org on merge to branch.
3. `sync-issues --provider=linear` after GitHub sync completes.
4. `gate-auditor` job that reads required test state and pushes issue transitions.

## 7) Suggested implementation: deterministic import script (pseudo)

```python
import json
import hashlib
from pathlib import Path

def hash_seed(seed_path: str) -> str:
    data = Path(seed_path).read_bytes()
    return hashlib.sha256(data).hexdigest()

def normalize(ticket):
    return {
      "title": f"[{ticket['issue_key']}] {ticket['title']}",
      "custom": {
        "wp_id": ticket["wp_id"],
        "bundle": ticket["bundle"],
        "phase": ticket["phase"],
        "required_tests": ticket["required_tests"],
        "required_artifacts": ticket["required_artifacts"],
        "dor_checks": ticket["dor_checks"],
        "dod_checks": ticket["dod_checks"],
        "rollback_token": ticket["rollback_token"],
        "gate_preconditions": ticket["gate_preconditions"],
      },
      "labels": ticket["labels"],
      "dependencies": ticket["dependencies"]
    }

def sync_ticket(api, source, ticket):
    body = normalize(ticket)
    found = source.find_issue(ticket["issue_key"])
    if not found:
        source.create_issue(**body)
    else:
        source.update_issue(found.id, **body)
```

## 8) Platform-specific adapters

### 8.1 GitHub adapter

- Use `gh issue create` and GraphQL for custom project fields where available.
- Enforce dedupe by checking exact title prefix `[{issue_key}]`.
- Move columns by column node id if using Projects v2:
  - Backlog → Ready only when all `dor_checks` satisfied.
  - Ready → Bundle QA when all required tests pass.
  - Bundle QA → Ready for Gate when all `dod_checks` pass.
  - Ready for Gate → Done only when all gate preconditions are signed.

### 8.2 Jira adapter

- Use bulk create endpoint where possible for performance.
- Represent dependencies as:
  - Outward: `blocks`
  - Inward: `is blocked by`
- Persist seed hash on issue in custom field `customfield_seed_hash`.

### 8.3 Linear adapter

- Resolve issue idempotency by `identifier` prefix and `labels`.
- Add links:
  - `subtask_of` for implementation dependencies where needed.
  - `blocks` relation for strict blockers.
- Persist dependency graph in team comments if no custom field exists.

## 9) State transition automation rules

| Rule | Condition | Action |
|---|---|---|
| R1 | all `dor_checks` true + dependencies closed | move to `Ready` |
| R2 | tests in `required_tests` pass + artifact hash attached | move to `Bundle QA` |
| R3 | all `dod_checks` complete + rollback token exists | move to `Ready for Gate` |
| R4 | gate condition for row satisfied (`requires-g10`, `requires-g11`, `requires-g12`) | keep blocked until explicit `gate_signoff` tag |
| R5 | any hard-stop event active for bundle | keep at current state or move to `Blockers` |

## 10) Duplicate control and idempotency

To avoid duplicate imports:

- Use deterministic issue key in title/body.
- Use deterministic content hash for each ticket:
 - `sha256(normalized_payload + seed_hash + bundle_version)`
- If hash unchanged and issue exists, update only mutable runtime fields.
- If hash changed and issue is closed, reopen only with explicit flag `--override-closed`.

## 11) Evidence synchronization checks

Automation should verify before gate transitions:

- PR links exist for modified WPs.
- Artifact references resolve (e.g., `artifacts/phase10/chunk_b/...` exists or remote URL 200).
- `evidence_manifest_id` has checksum and `policy_digest`.
- `required_tests` are present in test registry with matching version tags.

## 12) Failure handling and rerun strategy

- `429`/rate-limit: exponential backoff (1s, 2s, 4s, 8s...) with max 8 retries.
- conflict conflict/version mismatch:
  1) re-fetch issue,
  2) re-apply patch by field,
  3) mark in dry-run audit report if still failing.
- unresolved dependency: fail fast and print dependency chain with shortest path.
- malformed URL/artifact path: block ticket transition and annotate as `evidence-blocker`.

## 13) Rollback of automation changes

- Keep a rollback manifest in VCS:
  - ticket ids created,
  - transitions applied,
  - dependencies attached,
  - automation commit hash.
- To rollback:
  1. Re-run with `--rollback` on saved manifest,
  2. remove added/modified dependencies first,
  3. delete created tickets in reverse topological order.

## 14) Recommended operating cadence

- Day 0: Dry-run seed import with `--mode=import --provider=gh`.
- Day 1: GitHub/Jira/Linear import, sync check.
- Day 2: Attach test hooks and board automations.
- Daily: run gate auditor and post Blockers digest at standup.
- Weekly: rerun import in `--mode=sync --validate-only` to detect drift.

