---
description: Prep a release readiness checklist for zen-mcp-server
argument-hint: <release-tag-or-window>
---

Draft a release readiness checklist for `$ARGUMENTS`:

- Verify migration stories, data changes, or feature flags that require coordination.
- Confirm required test suites, smoke runs, and dashboards to watch.
- Include rollback plan triggers and owners.
- Reference relevant docs (`release-playbook.md`, `delivery-blueprint` sections).

Respond with:

Summary: <one-line readiness signal>
Checklist:
- [ ] <item> — <owner + rationale>
Risks:
- <risk + mitigation or ✅ None>
Rollbacks:
- <trigger + action or ✅ Standard rollback suffices>
