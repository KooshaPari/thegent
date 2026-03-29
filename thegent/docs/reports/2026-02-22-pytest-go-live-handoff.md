# Pytest Optimization Task 96-100 Go-Live Handoff

## Scope

This handoff covers tasks 96-100 from the pytest optimization plan in `docs/reports/2026-02-22-pytest-optimization-and-atoms-research.md` and the resulting governance additions for requirement extraction, lane promotion, and traceability cleanup.

## Completed Gates

- `task test:requirements:map` now emits `requirements-map/v1` artifact and writes `requirements-map.mdown`.
- `task test:requirements:promotion-criteria` now emits stable promotion criteria fields for optional lane promotion readiness.
- `requirements-diagram` rendering is available for FR/requirement graph visualization with truncation control.
- `task test:traceability:quarterly-cleanup` now emits `traceability-cleanup/v1` and `traceability-cleanup-issue/v1` contracts.
- PR and lane docs now reference the new traceability maintenance workflow.

## Config Gates to Keep Enabled

- PR gate health aggregation in `test:pr-gate`.
- `task test:requirements:map` output schema contract fields.
- `task test:requirements:promotion-criteria` for optional lane promotion readiness.
- `task test:traceability:quarterly-cleanup` scheduled cadence check.
- `test:collect:templates` nightly job in CI remains separate and unchanged.

## Go-Live Checklist

- [ ] Confirm `requirements-map.json` exists and `schema_version` is `requirements-map/v1`.
- [ ] Confirm `requirements-diagram` artifact is committed from the nightly traceability refresh.
- [ ] Confirm `requirements-promotion-criteria.json` shows readiness flags and reasons.
- [ ] Confirm `requirements-promotion` for target lanes is either `ready_to_require_optional_lanes: true` with explicit change request, or `false` and held.
- [ ] Confirm `requirements-cleanup-issue.json` is produced and either `status` is `closed` or triaged.
- [ ] Confirm CI artifact upload includes `artifacts/pytest/traceability/*` on template nightly runs.

## Rollback Triggers and Actions

- Trigger 1: `requirements-promotion-criteria` returns `ready_for_lane_promotion: false` for two consecutive nightlies while optional lanes are forced required.
  - Action: revert optional lane policy, set lane state back to `optional`, and keep historical run evidence in evidence ticket.
- Trigger 2: recurring `requirements-cleanup-issue` status `open` for two consecutive weekly checks.
  - Action: suspend gate hardening of marker removals, run cleanup task with a temporary threshold bump, then rerun traceability scan.
- Trigger 3: extractor schema mismatch in consumer tooling.
  - Action: keep parser consumers on previous working artifact path, run a limited compatibility check, then re-run `requirements-map`.

## On-Call Ownership

Primary owner: `quality-and-governance`.

- First responder: `quality-and-governance` for schema drift or lane promotion contract failures.
- Runbook holder: `ci-and-test-operations` for CI artifact/upload or task runner failures.
- Escalation owner: `wave-orchestration` for unresolved promotion or cleanup blockers.

## Open Risks and Monitoring

- Keep an eye on stale debt growth so cleanup issue volume does not outpace quarterly cleanup capacity.
- Treat diagram truncation as expected under large FR maps; keep `--max-nodes` at a nightly-reviewed level.
- Re-verify FR IDs in `docs/reference/FR_TRACKER.md` before forcing optional lane transitions.
