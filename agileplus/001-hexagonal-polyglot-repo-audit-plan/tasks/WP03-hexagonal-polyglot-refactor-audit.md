---
work_package_id: "WP03"
title: "Hexagonal Polyglot Refactor Audit"
lane: "planned"
subtasks:
  - "Map current boundaries"
  - "Identify ports and adapters"
  - "Score KISS DRY SOLID gaps"
  - "Plan language-specific extraction candidates"
phase: "Phase 2 - Architecture Audit"
assignee: ""
agent: ""
shell_pid: ""
review_status: ""
reviewed_by: ""
history:
  - timestamp: "2026-06-05T00:00:00Z"
    lane: "planned"
    agent: "codex"
    action: "Created architecture audit work package"
---

# Work Package Prompt: WP03 - Hexagonal Polyglot Refactor Audit

Audit thegent, sharecli, and owned Phenotype tooling for hexagonal architecture, KISS, DRY, SOLID, and polyglot extraction readiness.

## Acceptance Criteria

- Current architecture maps identify domain, application, adapter, and infrastructure boundaries.
- Shared contracts are listed for Python, Rust, Go, Zig, TypeScript, and other active languages.
- Refactor recommendations include risk, expected payoff, validation gate, and rollback path.
- The audit avoids creating abstractions without demonstrated duplication or boundary pressure.
