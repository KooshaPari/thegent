---
description: Kick off a structured review of a branch, PR, or diff
argument-hint: <branch-or-PR>
---

Review `$ARGUMENTS` using the zen-mcp-server code-review checklist.

Respond with:

1. **Summary** – Intent of the change and impacted packages.
2. **Correctness** – Edge cases, regression risks, and required tests.
3. **Hex Compliance** – Note any domain ↔ adapter boundary leaks or missing ports.
4. **Follow-up** – Concrete tasks with suggested owners or droid delegations.

Reference file paths and link to relevant docs (`work-prompts/`, blueprints) when useful.
