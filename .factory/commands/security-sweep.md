---
description: Run a focused security review on the latest work
argument-hint: <branch-or-scope>
---

Perform a security assessment of `$ARGUMENTS`:

- Inspect auth flow, secret handling, network calls, and logging.
- Reference relevant files in `auth/`, `api/`, `providers/`, `integrations/`, and `conf/`.
- Map findings to OWASP/CWE where possible and suggest mitigations plus validation steps.

Respond with:

Summary: <headline>
Findings:
- <area>: <issue + citation>
  Risk: <impact>
  Mitigation: <specific action/test>
Follow-up:
- <owner + due date or ✅ None>
