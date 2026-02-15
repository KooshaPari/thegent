---
description: Package an operations handoff for on-call or deployment rotations
argument-hint: <handoff-window>
---

Prepare an operations handoff for `$ARGUMENTS`:

- Summarize system health, outstanding incidents, and active mitigations.
- List critical dashboards, log paths, and alert runbooks.
- Document scheduled deploys, feature flags, and migration timing.
- Provide escalation contacts and communication channels.

Reply with:

Summary: <headline>
Status:
- <service>: <state> — <note>
Watchlist:
- <signal>: <threshold> — <action>
Schedule:
- <event>: <time + owner>
Escalation:
- <contact> — <channel>
