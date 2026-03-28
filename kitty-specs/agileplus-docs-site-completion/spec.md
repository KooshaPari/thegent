# AgilePlus docs site completion

## Goal
Complete the AgilePlus docs site with standardized verification harness and locale entry points.

## Scope
- Add docs test harness (unit, component, e2e) and Playwright config.
- Add locale entry pages for `zh-CN`, `zh-TW`, `fa`, and `fa-Latn`.
- Add docs test scripts (`docs:test:*`, `docs:check`) to docs package.json.
- Preserve existing route map and navigation.

## Acceptance Criteria
- Docs build script remains intact.
- Docs tests cover key routes and locale entry pages.
- Locale entry pages exist under docs.
