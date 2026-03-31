# AgilePlus Methodology Specification

> **Version**: 1.0 | **Status**: Active | **Project**: thegent

---

## Overview

AgilePlus is the project management and methodology framework used for tracking all work in thegent. It combines agile principles with structured governance to ensure systematic, traceable development across distributed teams and multi-project environments.

---

## Core Mandate

All work MUST be tracked in AgilePlus:

- **Reference CLI**: `cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus && agileplus <command>`
- **Work Packages**: All tasks are represented as beads (issues) in the AgilePlus system
- **Convoys**: Groupings of related work packages that ship together

---

## Branch Discipline

### Worktree Structure

Feature branches are organized using a structured worktree pattern:

```
repos/worktrees/<project>/<category>/<branch>
```

### Repository Governance

- **Canonical Repository**: Tracks `main` only
- **Feature Development**: Occurs in dedicated worktrees
- **Integration Checkpoints**: Return to `main` for merge/integration

### Creating Worktrees

```bash
thg_new_worktree <domain> <scale> <change-anchor> [start-point]
```

The helper refuses to branch from a dirty or non-main primary checkout.

---

## Work Requirements

### Before Implementation

1. **Check for AgilePlus spec** before implementing any feature or fix
2. **Review existing work packages** to avoid duplication
3. **Verify spec alignment** with current codebase state

### During Implementation

1. **Update work package status** as work progresses
2. **Use structured commits** with references to work package IDs
3. **Checkpoint significant milestones** for crash recovery

### Quality Gates

All code changes must pass pre-submission quality gates:

```bash
task quality
```

If a quality gate fails:
- Fix the issue and re-run the failing gate
- Repeat until all gates pass
- If unresolvable, escalate with full failure output

---

## AgilePlus Entities

### Beads (Work Packages)

The fundamental unit of work in AgilePlus:

| Field | Description |
|-------|-------------|
| `bead_id` | Unique identifier (UUID) |
| `type` | `issue`, `convoy`, `task` |
| `status` | `open`, `in_progress`, `in_review`, `done` |
| `priority` | `low`, `medium`, `high`, `critical` |
| `title` | Short description |
| `body` | Detailed specification |
| `assignee_agent_bead_id` | Agent responsible for execution |
| `parent_bead_id` | Parent convoy if applicable |
| `metadata` | Additional context (convoy_id, feature_branch) |

### Convoys

Groupings of related beads that ship together:

- Multiple work packages can belong to one convoy
- Convoys track progress across related features
- Named with pattern: `convoy/<purpose>/<convoy_id>/head`

### Waves

Execution batches that organize work for parallel completion:

- Wave completion events are recorded in the evidence ledger
- Each wave has a scope and set of deliverables
- Status tracking: `wave-XX-complete`

---

## UTF-8 Encoding

All markdown files must use UTF-8 encoding:

```bash
# Validate encoding (in AgilePlus repo)
cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
agileplus validate-encoding --all --fix
```

Avoid:
- Smart quotes
- Em-dashes
- Special characters that may cause encoding issues

---

## Agent Workflow

### GUPP Principle

**Work is on your hook** — execute immediately:

1. Receive a bead (work item)
2. Start working right away
3. No preamble, no status updates, no asking for permission
4. Produce code, commits, and results

### Agent Lifecycle

1. **Prime**: Get full context via `gt_prime`
2. **Work**: Implement the bead requirements
3. **Commit**: Make small, focused commits frequently
4. **Push**: Push after every commit (ephemeral disk)
5. **Checkpoint**: Call `gt_checkpoint` after significant milestones
6. **Done**: Call `gt_done` when complete

### Pre-Submission Gates

Before calling `gt_done`, run ALL quality gates:

1. `task quality` — Run lint, typecheck, tests

If any gate fails:
- Fix the issue and re-run
- Repeat until all gates pass
- If unresolvable, escalate via `gt_escalate`

---

## Escalation

When stuck for more than a few attempts at the same problem:

1. Call `gt_escalate` with:
   - Clear description of what's wrong
   - What you've tried
   - Relevant context

2. Continue working on other aspects if possible, or wait for guidance

---

## Communication

### Mail System

- Use `gt_mail_send` for coordination, questions, or status sharing
- Use `gt_mail_check` periodically or when expecting coordination messages

### Nudges

For time-sensitive coordination:
- `gt_nudge` delivers immediately at the agent's next idle moment
- Use for: wake up an agent, request status check, notify of blocking issue

### Status Updates

Call `gt_status` at meaningful phase transitions:
- Beginning a new file
- Running tests
- Installing packages
- Pushing a branch

Write for a teammate watching the dashboard — not a log line.

---

## Evidence Ledger

AgilePlus maintains a JSONL evidence ledger that tracks:

- Wave completions
- Workspace harmonization phases
- Cleanup actions
- Architecture status
- ECO (Enhancement/Capability/Optimization) tracking

Example events:

```json
{"event":"wave-83-complete","timestamp":"...","scope":"phenotype/repos","actions":{"security_alerts":"27_fixed_1_open","wave70_claims":"7_closed","agileplus":"5_shipped","backlog":"200_archived"}}
```

---

## Integration with thegent

Thegent is integrated with AgilePlus through:

1. **Work Stream Sync**: Bi-directional sync with GitHub Projects and Linear
2. **Registry Integration**: Agent personas for different roles
3. **Quality Gates**: Automated testing and linting
4. **Governance**: Policy enforcement for agent actions

### thegent Commands for AgilePlus

```bash
thegent plan next              # Find next actionable item
thegent sync autopilot         # Sync work stream
thegent sync autopilot --once   # Run sync once
thegent worktree new <domain> <scale> <change-anchor> [start-point]
thegent worktree state <change-anchor> <new-state>
```

---

## References

- AgilePlus CLI: `/Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus`
- AgilePlus Evidence Ledger: `agileplus/evidence_ledger.jsonl`
- thegent AGENTS.md: Project-specific agent rules
