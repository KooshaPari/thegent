---
description: Quick housekeeping sweep for logs, envs, and small chores
argument-hint: <scope-or-timeframe>
---

For `$ARGUMENTS`, collect light operational tasks the agent should clear:

- Check logs (`logs/mcp_server.log*`, `logs/mcp_activity.log*`) for warnings/errors and note follow-up commands.
- Verify environment sync (dotenv drift, secrets rotation, config templates).
- List dependency bumps, script refreshes, or dashboard checks due this week.
- Suggest droid handoffs (`ops-concierge`, `security-auditor`) when deeper action is needed.

Respond with:

Summary: <headline>
Tasks:
- <item> — <command/droid + due>
Escalate:
- <issue> — <owner or ✅ None>
