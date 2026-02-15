---
description: Checklist to verify quality gates before opening or merging a PR
argument-hint: <branch-or-task>
---

Prepare `$ARGUMENTS` for review by confirming every quality gate:

- Run `python -m pytest -xvs` and `ruff check .`; embed pass/fail evidence.
- Execute targeted suites if touching providers (`python communication_simulator_test.py --tests ...`).
- Inspect `logs/mcp_server.log` for new warnings; capture relevant snippets.
- Confirm required docs/tests updates are staged and linked.
- Summarize proof artifacts (command output paths, screenshots, log refs).

Respond with:

Summary: <ready / blockers>
Evidence:
- <command>: <result + link to artifact>
Follow-ups:
- <owner>: <action> — <due date or ✅ Done>
