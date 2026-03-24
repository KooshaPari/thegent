# 16_NEXT_WAVE_J — next 25 items (Waves 1-8 sequence)

**Follows** `07`–`15`. **Snapshot:** 2026-03-24. **Intent:** Quality & Performance.

## Slice 1 — Performance & Optimization (8)
1. **Startup**: P50/P95 latency audit for `heliosCLI`.
2. **Bundle**: Run `source-map-explorer` on `heliosApp`.
3. **Memory**: Profile `heap` usage for `AgilePlus` desktop.
4. **V8**: Check for de-optimizations in hot loops (`lane_event_handler.ts`).
5. **Assets**: Optimize all `public/` images and icons.
6. **Network**: Audit `fetch` calls and implement retries/timeouts.
7. **Cache**: Verify `LocalBus` event persistence and expiry.
8. **Concurrency**: Audit `worker` thread pool usage in `runtime`.

## Slice 2 — Quality & Testing (8)
9. **Coverage**: Run `vitest --coverage` on all sub-apps.
10. **E2E**: Verify `playwright` tests in `heliosApp`.
11. **Snapshots**: Audit all UI component snapshots.
12. **Mocks**: Standardize `msw` or `nock` for API mocking.
13. **Fuzz**: Add `fuzz` tests for `LocalBus` message handling.
14. **Integration**: Run cross-repo tests for `heliosApp` vs `runtime`.
15. **A11y**: Run `axe-core` on all desktop views.
16. **CI Runtime**: Audit GHA duration and optimize runners.

## Slice 3 — Error Handling & Resilience (8)
17. **Sentry**: Verify DSN and release tracking in production.
18. **Logs**: Standardize `pino` or `winston` log formats.
19. **Errors**: Create a global error code registry for `helios`.
20. **Retries**: Verify exponential backoff for external API calls.
21. **Deadlines**: Implement `AbortController` in all async tasks.
22. **Backpressure**: Audit `LocalBus` for buffer overflows.
23. **Fallback**: Verify offline mode behavior for `heliosApp`.
24. **Recovery**: Test automatic restart after crash (watchdog).

## Slice 4 — Meta (1)
25. **Task Update**: Record performance findings in `05_KNOWN_ISSUES.md`.
