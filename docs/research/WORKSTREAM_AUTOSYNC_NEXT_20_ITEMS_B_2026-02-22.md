# Workstream Autosync Next 20 Items B (WL-181..WL-200) — 2026-02-22

## Scope

Second execution wave for fully automatic board reflection and hands-off agent workflows.

## Batch Items

1. WL-181: Add status drift detector with severity tiers.
2. WL-182: Add stale item detector (no local/remote updates in threshold window).
3. WL-183: Add board-id collision detector across GitHub and Linear.
4. WL-184: Add automatic row normalization for malformed WL headers.
5. WL-185: Add local snapshot rollback command for bad reflection cycles.
6. WL-186: Add sync dry-run diff printer for human-readable previews.
7. WL-187: Add external write batching for low-churn runs.
8. WL-188: Add partitioned sync by WL ranges (`WL-100..WL-150`).
9. WL-189: Add configurable ignore list for specific WL IDs.
10. WL-190: Add strict mode that fails on unmapped external states.
11. WL-191: Add mapping cache for GitHub field IDs and Linear workflow states.
12. WL-192: Add resilient startup checks for auth scopes and endpoint reachability.
13. WL-193: Add per-connector timeout controls (GitHub vs Linear).
14. WL-194: Add connector-level circuit breaker integration.
15. WL-195: Add structured event log stream for every reflection decision.
16. WL-196: Add Prometheus-compatible metrics export path.
17. WL-197: Add policy file for sync governance (`.thegent/sync-policy.yaml`).
18. WL-198: Add full e2e replay test fixture from sample WORK_STREAM input.
19. WL-199: Add docs for multi-project tenancy autosync patterns.
20. WL-200: Add release checklist and migration notes for enabling autosync in existing repos.
