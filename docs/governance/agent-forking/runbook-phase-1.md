# Agent Forking Runbook — Phase 1

## 1) Operator Commands

Run these commands from `/Users/kooshapari/temp-PRODVERCEL/485/kush`:

1. Set execution context with these environment assignments in one shell session: `PLAN_ID=thegent-phase1-quality`, `PLAN_PATH=governance/agent-forking/plans/pilot-phase-1-thegent-quality.md`, `LEDGER=governance/agent-forking/artifacts/pilot-thegent-phase-1-ledger.jsonl`, `ARTIFACT_DIR=governance/agent-forking/artifacts`, then run `mkdir -p "$ARTIFACT_DIR"`.
2. Audit baseline and scope with this exact sequence: `rg --files -g 'AGENTS.md'`, `ls -1 governance/agent-forking`, `ls -1 thegent/docs/ thegent/config/ thegent/Taskfile.yml` (or equivalent scope path for the target plan).
3. Start lane execution validation in one pass with these commands: `python governance/agent-forking/validate_lane_report.py governance/agent-forking/artifacts/thegent-lane-*.json`, `python -m json.tool governance/agent-forking/artifacts/thegent-lane-1.json`, `python -m json.tool governance/agent-forking/artifacts/thegent-lane-2.json`, `python -m json.tool governance/agent-forking/artifacts/thegent-lane-3.json`.
4. Record immutable event for each significant step by appending one JSON object per line to `"$LEDGER"` with UTC `timestamp`, explicit `actor`, `type`, and evidence text.

## 2) Lane Assignment Checklist

1. Copy `governance/agent-forking/templates/fork_plan.md` into a plan record and bind it to a unique `plan_id`.
2. Create per-lane artifact targets before work begins: `thegent-lane-1` (docs/quality governance focus), `thegent-lane-2` (alias/config validation focus), `thegent-lane-3` (check-discovery/family consistency focus).
3. Assign each lane one `owner`, one objective, and explicit scope list before edits are made.
4. Before any lane writes shared files, verify no file ownership overlap across existing lane assignments.
5. Require each lane to submit a JSON report, markdown notes artifact, and validation block with at least one command and result.
6. Before handoff, re-run per-lane report validation and aggregate failures in one consolidated operator pass.

## 3) Evidence Filing Rules

1. For every evidence item, require a file reference (`path:line` when possible), exact command text (or `no-op` with reason), and execution result (`pass|fail|skip`).
2. For ledger entries, enforce append-only JSONL with mandatory keys `timestamp`, `actor`, `type`, `plan_id`, `message`; include `lane` for lane-scoped changes.
3. For lane reports, require non-empty `validation.commands` and `validation.results`, evidence references in each `findings` item, and pass from `python governance/agent-forking/validate_lane_report.py <lane-report>`.
4. Persist all lane artifacts only under `governance/agent-forking/artifacts/`.
5. Apply redaction: no secrets, raw env values, token-like strings, or auth headers in evidence; use `[REDACTED]` placeholders.

## 4) Rollback / Abort Criteria

1. Trigger immediate abort and rollback if any lane report fails schema validation, any unresolved `critical` conflict is present during merge, any required scope file is missing and cannot be safely recreated, or two consecutive quality gates fail on unchanged scope.
2. On rollback, stop all active lane work, preserve `"$LEDGER"` immutable, revert uncommitted lane artifacts only unless already validated, and rerun failed lanes after a corrected bootstrap.
3. Only resume after a clean ledger record includes conflict status/reason/owner, all pending lanes are re-scheduled with a fresh conflict lock, and preflight plus validation commands pass.

## 5) Escalation Workflow When Conflict Threshold is Exceeded

1. Trigger escalation if `high` conflicts exceed 2, any `critical` conflict appears, or a lane stalls for two check-ins with no status update.
2. First pause all writes to touched files, then post a `type=conflict` mediation entry to the ledger with lane names, file paths, and severity.
3. Route the conflict to one lead resolver for one arbitration round and require a structured outcome.
4. If unresolved after one round, escalate to owner-level decision by next handoff window and place temporary locks on impacted files.
5. Resume only after the conflict is resolved or downgraded in the ledger, owning lane updates report outcomes, and `validate_lane_report.py` plus command evidence are rerun for impacted artifacts.
