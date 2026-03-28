---
work_package_id: "WP03"
title: "Validation and automation"
lane: "planned"
subtasks:
  - "T301"
  - "T302"
phase: "Phase 3 – Validation & Automation"
assignee: ""
agent: ""
shell_pid: ""
review_status: ""
reviewed_by: ""
history:
  - timestamp: "2026-03-28T12:10:00Z"
    lane: "planned"
    agent: "system"
    action: "WP created"
---

# Work Package Prompt: WP03 – Validation and automation

- Run `npm run docs:evidence` and record the output (timestamp, warnings) in the session worklog; treat the chunk size warning as a known issue for now.
- Capture a regression guard recipe so future builds rerun the gate automatically (Playwright snippet, npm script, or CI job).
- Identify any docs that remain blocked (missing bundles, translations) and log them under `05_KNOWN_ISSUES.md` in the session folder.
