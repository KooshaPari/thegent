# Kilo Gastown Methodology Specification

> **Version**: 1.0 | **Status**: Active | **Project**: thegent

---

## Overview

Gastown is the distributed agent orchestration framework used by Kilo to coordinate multi-agent work across isolated rigs. It provides a hierarchical structure of towns, rigs, and agents that collaborate through typed message passing, shared work beads, and coordinated convoys.

---

## Architecture

### Town

The top-level coordination unit:

- Contains multiple rigs
- Provides cross-rig communication bridges
- Maintains town-wide bead registry
- Routes escalation requests

### Rig

An isolated agent execution environment:

- Contains one or more agents (polecats)
- Has dedicated worktree for each agent
- Owns a bead store for work assignment
- Tracks agent status and checkpoint state

### Agent

The fundamental execution unit within a rig:

- Identified by unique agent ID and role (polecat, refinery, patrol)
- Has dedicated worktree workspace
- Processes beads from its hook
- Communicates via typed mail and nudges

---

## Bead Lifecycle

### Bead Types

| Type | Purpose |
|------|---------|
| `issue` | Work package to be executed |
| `convoy` | Grouping of related issues for coordinated delivery |
| `task` | Internal subtask |
| `merge_request` | Review request for code submission |
| `escalation` | Urgent issue requiring human or supervisor intervention |

### Bead States

```
open -> in_progress -> in_review -> done
                      \-> escalated
```

### Bead Fields

| Field | Description |
|-------|-------------|
| `bead_id` | Unique identifier (UUID) |
| `type` | `issue`, `convoy`, `task`, `merge_request`, `escalation` |
| `status` | `open`, `in_progress`, `in_review`, `done`, `escalated` |
| `priority` | `low`, `medium`, `high`, `critical` |
| `title` | Short description |
| `body` | Detailed specification or instructions |
| `assignee_agent_bead_id` | Agent responsible for execution |
| `parent_bead_id` | Parent convoy or task |
| `metadata` | Additional context (convoy_id, feature_branch, rig_id) |

---

## Convoys

Convoys group related beads that ship together across multiple agents or rigs:

- **Pattern**: `convoy/<purpose>/<convoy_id>/head`
- **Feature Branch**: Derived from convoy metadata
- **Progress Tracking**: Via `gt_list_convoys`
- **Ready to Land**: Marked when all constituent beads are done

### Convoy Lifecycle

1. Create convoy bead to track related work
2. Add issue beads with `convoy_id` metadata
3. Track progress via `gt_list_convoys`
4. When all beads done, mark `ready_to_land: 1`
5. Refinery merges when ready

---

## Agent Roles

### Polecat

Standard execution agent:

- Processes hooked beads from its queue
- Implements features, fixes bugs, writes tests
- Follows GUPP principle (execute immediately)
- Pushes commits to review queue

### Refinery

Integration and merge agent:

- Picks up beads from review queue
- Validates merges, runs quality gates
- Requests changes or approves merges
- Closes beads when complete

### Patrol

Monitoring and triage agent:

- Monitors system health
- Creates triage request beads
- Routes issues to appropriate agents
- Maintains operational status

---

## Delegation: gt_sling and gt_sling_batch

### gt_sling

Single bead delegation to another agent:

```bash
gt_sling --to <agent_id> --bead <bead_id> [--priority <priority>]
```

Used for:
- Transferring specific work items
- Requesting specialized assistance
- Distributing load across agents

### gt_sling_batch

Multiple bead delegation in one operation:

```bash
gt_sling_batch --to <agent_id> --beads <bead_id_1,bead_id_2,...>
```

Used for:
- Bulk transfer of related items
- Wave-based work distribution
- Delegating entire work packages

---

## Merge Modes

Agents support different merge strategies:

### Direct Merge

Push to main branch after review approval:

```
agent pushes -> refinery reviews -> direct merge
```

### Squash Merge

All commits squashed into single commit:

```
agent commits -> refinery squashes -> single commit to main
```

### Rebase Merge

Rebase feature branch before merge:

```
agent commits -> refinery rebases -> fast-forward merge
```

### Hotfix Mode

Emergency fixes bypass standard queue:

```
agent -> immediate review -> fast-track merge
```

---

## Progress Tracking: gt_list_convoys

Display all active convoys and their status:

```bash
gt_list_convoys [--rig <rig_id>] [--status <status>]
```

Output includes:
- Convoy ID and title
- Member bead count
- Completion percentage
- Ready to land status
- Feature branch name

---

## thegent as Orchestration Hub

Thegent serves as the central coordination layer:

### Worktree Management

Each agent in a rig has dedicated worktree:

```
repos/worktrees/<project>/<category>/<branch>
```

### Agent Coordination

thegent coordinates via:

1. **Hooked Beads**: Each polecat has a `current_hook_bead_id`
2. **Mail System**: Async typed messaging between agents
3. **Nudges**: Time-sensitive wake-up calls
4. **Checkpoints**: Crash recovery state persistence

### Rig Operations

| Command | Purpose |
|---------|---------|
| `gt_prime` | Get full agent context |
| `gt_done` | Complete bead, push to review |
| `gt_checkpoint` | Save recovery state |
| `gt_bead_status` | Inspect bead state |
| `gt_bead_close` | Close completed bead |

---

## Quality Gates

Before submitting work:

1. `task quality` - Run all lint, typecheck, tests

If gates fail:
- Fix issues locally
- Re-run gates
- Escalate if unresolvable

---

## Escalation

Escalation routes urgent issues:

1. **Agent Escalation**: `gt_escalate` creates escalation bead
2. **Cross-Rig Escalation**: Routed to town supervisor
3. **Human Escalation**: Routed to project maintainers

Escalation bead includes:
- Original bead ID
- Problem description
- Context and history
- Severity assessment

---

## Communication

### Mail

Typed persistent messages:

```bash
gt_mail_send --to <agent_id> --subject <subject> --body <body>
gt_mail_check
```

### Nudges

Immediate delivery at agent idle:

```bash
gt_nudge --target <agent_id> --message <message> [--mode immediate|queue]
```

### Status Updates

Plain-language dashboard updates:

```bash
gt_status --message <description>
```

Write for teammates, not logs. One or two sentences.

---

## References

- Gastown Rig: `7e993294-ef1f-4fee-bf0a-44c164e18ab2`
- Town ID: `78a8d430-a206-4a25-96c0-5cd9f5caf984`
- thegent AGENTS.md: Project-specific agent rules
