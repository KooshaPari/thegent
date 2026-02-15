---
description: Structure an incident retro from collected notes
argument-hint: <incident-summary>
---

Turn `$ARGUMENTS` into a concise post-incident retro:

- Timeline of key events (UTC) and detection vector.
- Root cause analysis referencing modules/services.
- Immediate fixes vs. long-term prevention tasks with owners.
- Required documentation updates (runbooks, playbooks, dashboards).

Output:

Summary: <headline>
Timeline:
- <time> — <event>
Root Cause:
- <factor> — <evidence>
Actions:
- <owner> — <task> — <target date>
Docs:
- <document>: <update needed>
