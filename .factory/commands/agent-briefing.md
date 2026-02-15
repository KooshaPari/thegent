---
description: Share a quick agent briefing referencing canonical docs
argument-hint: <task-context>
---

Compose an agent briefing for `$ARGUMENTS` before coding:

- Reference `AGENTS.md`, relevant `docs/plans/*.md`, and `work-prompts/` entries.
- Summarize build/test commands and guardrails that apply.
- Specify success criteria, evidence required (tests, logs), and constraints (paths, tooling).

Respond with:

Briefing:
- Context: <what we're doing and why>
- Constraints: <paths, tooling, guardrails>
- Evidence: <tests, artifacts, docs to update>
- References: <doc links>
