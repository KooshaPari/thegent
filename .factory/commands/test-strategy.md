---
description: Generate a risk-based testing plan for upcoming work
argument-hint: <feature-or-ticket>
---

Create a testing strategy for `$ARGUMENTS`:

- Identify risk areas across domain, adapters, integrations, and CLIs.
- Recommend pytest suites, fixtures, and contract coverage (cite specific files).
- Suggest smoke or observability checks for deployment confidence.
- Flag gaps and assign follow-up actions.

Format:

Summary: <headline>
Plan:
- <focus area> — <tests + rationale>
Gaps:
- <risk without coverage or ✅ No major gaps>
Readiness:
- <blocking prerequisites, instrumentation, or ✅ Ready once plan executed>
