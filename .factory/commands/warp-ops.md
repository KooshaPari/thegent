---
description: Align Warp terminal workflows with zen-mcp-server automation
argument-hint: <workflow-or-session>
---

For `$ARGUMENTS`, prepare Warp terminal integration steps:

- Reference `docs/guides/warp.md` sections for TUI components and config.
- Ensure `warp_config.yaml` matches required biometrics/progress settings.
- Map Warp panes to `/commands` and droid invocations (e.g., `/log-triage`, `security-auditor`).
- Outline verification steps (Textual UI rendering, streaming updates, metrics).

Respond with:

Summary: <headline>
Setup:
- <step>: <command or config file>
Workflow:
- <pane/action>: <command or droid>
Validation:
- <check>: <expected outcome>
