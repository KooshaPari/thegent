# {Doc Type} Tracker

**Last Updated:** {Date}
**Tracked Document:** {Reference to the source document being tracked — e.g., PRD v1.0, PLAN v1.0}

---

## Summary

| Status | Count |
|--------|-------|
| COMPLETE | {n} |
| IN-PROGRESS | {n} |
| PLANNED | {n} |
| NOT-STARTED | {n} |
| BLOCKED | {n} |
| SKIPPED | {n} |
| **Total** | **{n}** |

---

## Progress Overview

```
COMPLETE:     [{bar}] {n}/{total} ({%}%)
IN-PROGRESS:  [{bar}] {n}/{total} ({%}%)
NOT-STARTED:  [{bar}] {n}/{total} ({%}%)
```

---

## Detailed Status

### {Category/Phase 1}: {Name}

| ID | Title | Status | Progress | Code Location | Notes |
|----|-------|--------|----------|---------------|-------|
| {id} | {title} | COMPLETE | 100% | `{file}:{start}-{end}` | {notes — e.g., "Tested and verified"} |
| {id} | {title} | IN-PROGRESS | {%}% | `{file}:{start}-{end}` | {notes — e.g., "Core logic done, needs tests"} |
| {id} | {title} | NOT-STARTED | 0% | — | {notes — e.g., "Blocked by {id}"} |
| {id} | {title} | BLOCKED | {%}% | `{file}:{start}-{end}` | {blocker description} |

### {Category/Phase 2}: {Name}

| ID | Title | Status | Progress | Code Location | Notes |
|----|-------|--------|----------|---------------|-------|
| {id} | {title} | {status} | {%}% | `{file}:{lines}` | {notes} |
| {id} | {title} | {status} | {%}% | `{file}:{lines}` | {notes} |

### {Category/Phase 3}: {Name}

| ID | Title | Status | Progress | Code Location | Notes |
|----|-------|--------|----------|---------------|-------|
| {id} | {title} | {status} | {%}% | `{file}:{lines}` | {notes} |

{Continue for all categories/phases...}

---

## Blockers & Dependencies

| Blocker | Affects | Owner | Resolution |
|---------|---------|-------|------------|
| {Description of blocker} | {List of blocked IDs} | {Who can resolve} | {Planned resolution or workaround} |

---

## Recent Changes

| Date | ID | Change | By |
|------|----|--------|----|
| {Date} | {id} | {Description of change — e.g., "Status: NOT-STARTED -> IN-PROGRESS"} | {agent/person} |
| {Date} | {id} | {Description of change} | {agent/person} |

---

<!--
Tracker Guidelines:
  - Status values: COMPLETE, IN-PROGRESS, PLANNED, NOT-STARTED, BLOCKED, SKIPPED
  - Code Location: use file:line-range format (e.g., src/auth.ts:42-87)
  - Update "Last Updated" timestamp on every modification
  - Progress percentages: 0%, 25%, 50%, 75%, 100% (avoid false precision)
  - Notes should be actionable — what remains, what blocks, what was verified
  - Group by category/phase matching the source document structure
  - Keep Recent Changes log for audit trail
-->
