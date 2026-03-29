# Pilot Plan: thegent Same-Agent Fork (Phase 1)

- `plan_id`: `thegent-phase1-quality-2026-02-22`
- `title`: `thegent quality checks with same-agent fork`
- `objective`: `Validate forked same-agent workflow on static quality and reporting tasks.`
- `scope`: `thegent quality command family and task evidence collection only.`
- `max_parallel_lanes`: `3`
- `context_snapshot_version`: `ctx-thegent-quality-v1`

## Scope for Phase 1

1. `thegent/docs/guides/QUALITY_ASSURANCE.md` review and evidence capture.
2. `thegent/config/deprecated_quality_aliases.json` cleanup validation.
3. `thegent/docs/plans/*` status cross-check.

## Lanes

### Lane thegent-lane-1

1. Focus: Governance and docs consistency.
2. Files: `thegent/docs/guides/QUALITY_ASSURANCE.md`, `thegent/docs/plans/WL-123-RETIRE-DEPRECATED-QUALITY-ALIASES-PLAN.md`.
3. Checks: `python cli.py quality` (if available in environment).

### Lane thegent-lane-2

1. Focus: Deprecated alias validation and task keyword cleanup.
2. Files: `thegent/config/deprecated_quality_aliases.json`, `thegent/config/*.json`.
3. Checks: `python -m json.tool thegent/config/deprecated_quality_aliases.json`, `rg -n "quality:full|strict-full|task quality:full" thegent`.

### Lane thegent-lane-3

1. Focus: Parent-orchestrated check candidate discovery.
2. Files: `thegent/Taskfile.yml`, `cliproxyapi-plusplus/Taskfile.yml`, `trace/Taskfile.yml`.
3. Checks: `rg -n "parent|quality" thegent/Taskfile.yml cliproxyapi-plusplus/Taskfile.yml trace/Taskfile.yml`.

## Completion Conditions

1. All three lane reports validate against schema.
2. One shared evidence ledger entry created at `governance/agent-forking/artifacts/pilot-thegent-phase-1-ledger.jsonl`.
3. No unresolved conflicts above `0` critical/high.
4. If all checks pass, move to phase 2 across repos.

## Runbook (Operator)

1. Create filled plan report from template at `governance/agent-forking/templates/fork_plan.md`.
2. Launch each lane independently with bootstrap context.
3. Persist each lane output as JSON at `governance/agent-forking/artifacts/thegent-lane-1.json`, `governance/agent-forking/artifacts/thegent-lane-2.json`, and `governance/agent-forking/artifacts/thegent-lane-3.json`.
4. Validate all outputs in one pass with `python governance/agent-forking/validate_lane_report.py governance/agent-forking/artifacts/thegent-lane-*.json`.
5. Write consolidated notes to `governance/agent-forking/observations/thegent-phase-1-summary.md`.
