---
description: Structure a log triage session for errors or anomalies
argument-hint: <issue-or-time-window>
---

Triage `$ARGUMENTS` by inspecting Zen MCP logs:

- Specify which files to inspect (`logs/mcp_server.log`, `logs/mcp_activity.log`, rotated archives).
- Recommend filters (`rg`, `grep`, `jq`) and time windows.
- Note correlating metrics/dashboards if available.
- Provide hypotheses linking log signatures to components.
- Suggest remediation tasks or additional instrumentation.

Respond with:

Summary: <headline>
Checks:
- <log file>: <command/filter> — <what to extract>
Findings:
- <observation> — <impact + component>
Actions:
- <owner>: <task> — <due date or ✅ None>
