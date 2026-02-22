# Workstream Autosync Next 20 Items (WL-161..WL-180) — 2026-02-22

## Scope

This batch defines the next 20 execution items for automatic synchronization between:

- local `docs/reference/WORK_STREAM.md`
- GitHub Projects v2
- Linear

## Batch Items

1. WL-161: Add board-id-first status reconciliation policy with deterministic conflict precedence.
2. WL-162: Push status/priority updates to GitHub custom fields (not only draft body creation).
3. WL-163: Pull GitHub status updates into local status lines with audit trail row comments.
4. WL-164: Add Linear state-id mapping (Todo/In Progress/Done) with explicit transition table.
5. WL-165: Add Linear priority push/pull parity with P0/P1/P2/P3 normalization.
6. WL-166: Add dedup index persisted in local cache for cross-cycle idempotency.
7. WL-167: Add remote deletion/archive handling policy and local reflection strategy.
8. WL-168: Add scoped sync filters (area, priority, prefix, status).
9. WL-169: Add batch limiter and backoff for API rate limiting across GitHub and Linear.
10. WL-170: Add retry/error budget and hard-fail thresholds with clear operator alerts.
11. WL-171: Add `thegent sync autopilot status` with health/snapshot summary.
12. WL-172: Add `thegent sync autopilot doctor` for credential/scope/field validation.
13. WL-173: Add structured cycle metrics emission for observability dashboards.
14. WL-174: Add periodic integrity check: local items vs external items mismatch report.
15. WL-175: Add lock discipline for single-writer autosync when multiple daemons run.
16. WL-176: Add process-compose/dev lifecycle docs and restart semantics for autosync.
17. WL-177: Add unit tests for parser/reflection edge cases and malformed markdown blocks.
18. WL-178: Add integration tests for GitHub sync cycle with mocked `gh` responses.
19. WL-179: Add integration tests for Linear GraphQL sync cycle with fixture payloads.
20. WL-180: Add user-facing quick-start for zero-touch board reflection setup.

## Acceptance Direction

- Every item must preserve idempotency and avoid duplicate external artifacts.
- External pull updates must be reflected locally in deterministic, traceable form.
- Errors must fail loudly; no silent fallbacks.
