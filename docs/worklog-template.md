# <Project Name> - Worklog

> Last Updated: 2026-03-25
> Managed via: AgilePlus

## Worklog Structure

This project follows the AgilePlus worklog standard. All work MUST be tracked in AgilePlus.

### AgilePlus Feature Specs

All feature work is tracked in the AgilePlus repository:
```
/Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
```

Use `agileplus` CLI to manage features:
```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
agileplus specify --title "<feature>" --description "<desc>"
agileplus list
agileplus show <feature-id>
```

---

## Past Work (Completed)

### [Feature ID] - Feature Title

**Status**: Shipped
**Completed**: YYYY-MM-DD
**Spec**: `<link to spec.md in AgilePlus>`
**PRs**: `<link to merged PRs>`

**Summary**:
Brief description of what was delivered.

**Key Decisions**:
- Decision 1
- Decision 2

**Lessons Learned**:
- What went well
- What could be improved

---

## Present Work (In Progress)

### [Feature ID] - Feature Title

**Status**: In Progress
**Started**: YYYY-MM-DD
**Spec**: `<link to spec.md in AgilePlus>`
**Current WP**: WP0X

**Progress**:
- [x] WP01 - Completed task
- [x] WP02 - Completed task
- [ ] WP03 - In progress
- [ ] WP04 - Blocked by X

**Blockers**:
- Blocker 1 (blocking WP03)
- Blocker 2

**Next Steps**:
1. Complete WP03
2. Start WP04
3. Open PR for WP02

---

## Future Work (Planned)

### [Feature ID] - Feature Title

**Status**: Planned
**Priority**: High/Medium/Low
**Spec**: `<link to spec.md in AgilePlus>`
**Dependencies**: `<list of blocking features>`

**Description**:
Brief description of planned feature.

**Estimated Work**:
- WPs: WP01-WP0X
- Estimated time: X days

---

## Quick Reference

### AgilePlus CLI

```bash
# Specify new feature
cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
agileplus specify --title "Feature Name" --description "Brief description"

# List all features
agileplus list

# Show feature details
agileplus show <feature-id>

# Update work package status
agileplus status <feature-id> --wp <wp-id> --state <state>

# Validate encoding
agileplus validate-encoding --feature <feature-id>
```

### State Definitions

| State | Description |
|-------|-------------|
| `specified` | Feature spec created |
| `planned` | Architecture decided |
| `tasks_created` | Work packages defined |
| `in_progress` | Implementation underway |
| `for_review` | Awaiting review |
| `merged` | Code merged to main |
| `shipped` | Feature released |
| `blocked/stuck` | Needs resolution |
| `superseded` | Replaced by another feature |

### Directory Structure

```
<project>/
  kitty-specs/
    <feature-id>/
      spec.md          # Feature specification
      plan.md          # Architecture and plan
      meta.json        # Feature metadata
      tasks/
        WP01.md        # Work package 1
        WP02.md        # Work package 2
```
