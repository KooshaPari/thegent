---
work_package_id: "WP01"
title: "Document evidence classification"
lane: "done"
subtasks:
  - "T101"
  - "T102"
phase: "Phase 1 – Coverage Mapping"
assignee: ""
agent: ""
shell_pid: ""
review_status: ""
reviewed_by: ""
history:
  - timestamp: "2026-03-28T12:00:00Z"
    lane: "planned"
    agent: "system"
    action: "WP created"
  - timestamp: "2026-03-28T12:30:00Z"
    lane: "done"
    agent: "codex"
    action: "Documented frontmatter standards and WBS"
---

# Work Package Prompt: WP01 – Document evidence classification

- Enumerate every tutorial/how-to/API/reference/CLI leaf that should be gated (English + translated index/guide nodes). Use the heuristics in `.vitepress/config.mts` to classify and record any exceptions.
- Confirm the frontmatter key is `type` and standardize the `evidence_bundle` naming conventions (one bundle per doc family or translation slice).
- Draft a mini guide (copyable snippet) so future contributors know how to add a new bundle and how to name artifacts.
- Link the list back into the docs session WBS so the plan remains discoverable.
