# heliosCLI docs site completion

## Goal
Complete the docs site with the standard verification harness: VitePress build support, unit/component/e2e docs tests, and the canonical locale entry pages.

## Scope
- Add or normalize docs scripts for build/test/check flows.
- Add missing docs harness files for unit, component, and e2e coverage.
- Add locale entry pages for `zh-CN`, `zh-TW`, `fa`, and `fa-Latn` if missing.
- Keep dead-link and route coverage aligned with the existing docs surface.

## Acceptance Criteria
- `docs:build` succeeds.
- `docs:test` covers unit, component, and e2e docs checks.
- Canonical locale entry pages exist and route correctly.
- Public docs routes are verified without 404 regressions.
