# Kilo Gastown Methodology Specification

> **Purpose**: Document the Kilo Gastown methodology for orchestrating multi-agent work in thegent
> **Rig ID**: 7e993294-ef1f-4fee-bf0a-44c164e18ab2
> **Town ID**: 78a8d430-a206-4a25-96c0-5cd9f5caf984

---

## 1. Overview

Kilo Gastown is a distributed agent orchestration methodology that enables coordinated multi-agent execution across rigs and worktrees. thegent serves as the orchestration hub, managing convoys of related work, delegating tasks via gt_sling/gt_sling_batch, tracking bead lifecycle states, and providing progress visibility through gt_list_convoys.

---

## 2. Core Concepts

### 2.1 Convoys

A **convoy** is a collection of related beads (work items) that are dispatched together as a unit. Convoys provide:

- **Grouping**: Related work items are bundled for coordinated delivery
- **Feature Branching**: Each convoy maps to a feature branch (e.g., `convoy/agileplus-kilo-specs-thegent/be996e0e/head`)
- **Progress Tracking**: Convoy-level status via `gt_list_convoys`

**Convoy Structure**:
```yaml
convoy_id: be996e0e-88f3-4e74-be79-02ae91ddfefe
title: "AgilePlus + Kilo Specs: thegent"
feature_branch: convoy/agileplus-kilo-specs-thegent/be996e0e/head
status: open  # open | in_progress | merged | closed
```

### 2.2 Beads

A **bead** is the fundamental work item unit in Gastown. Beads have:

**Bead Types**:
| Type | Purpose |
|------|---------|
| `issue` | Work items, bugs, features |
| `convoy` | Parent container for related beads |
| `merge_request` | Code review/merge tracking |

**Bead Lifecycle**:
```
open → in_progress → in_review → merged/closed
         ↓
      blocked (escalation)
```

**Bead States**:
| State | Description |
|-------|-------------|
| `open` | Created, not started |
| `in_progress` | Being worked |
| `in_review` | Submitted for review |
| `blocked` | Waiting on dependency or escalation |
| `merged` | Code merged |
| `closed` | Completed without merge |

### 2.3 Delegation: gt_sling and gt_sling_batch

**gt_sling** dispatches a single bead to an agent:
```bash
gt_sling --bead-id <bead_id> --agent-id <agent_id>
```

**gt_sling_batch** dispatches multiple beads simultaneously:
```bash
gt_sling_batch --bead-ids <id1,id2,...> --agent-id <agent_id>
```

**Delegation Patterns**:
1. **Single Dispatch**: One bead per agent (gt_sling)
2. **Batch Dispatch**: Multiple independent beads to same agent (gt_sling_batch)
3. **Convoy Dispatch**: All beads in a convoy to multiple agents

### 2.4 Merge Modes

Work is integrated via different merge modes:

| Mode | Description | Use Case |
|------|-------------|----------|
| `merge` | Standard git merge to main | Single agent, small changes |
| `squash` | Squash commits before merge | Batched work, clean history |
| `rebase` | Rebase onto main | Linear history, dependent work |
| `fast_forward` | Direct pointer move | Already integrated |

### 2.5 gt_list_convoys

Progress tracking command:
```bash
gt_list_convoys --rig-id <rig_id>
```

Returns convoy status including:
- Active convoys
- Bead counts by state
- Blocked beads requiring attention

---

## 3. thegent as Orchestration Hub

### 3.1 thegent's Role

thegent coordinates sub-agents and rigs through:

1. **Bead Management**: Creates, assigns, and tracks beads
2. **Convoy Dispatch**: Groups beads into convoys for coordinated delivery
3. **Agent Pool**: Manages available agents (polecats, refinery, etc.)
4. **Worktree Coordination**: Isolates work in `repos/worktrees/<project>/<category>/<branch>`

### 3.2 Agent Hierarchy

```
Town (78a8d430)
└── Rig (7e993294)
    ├── thegent (orchestration hub)
    ├── Refinery (merge/refinement)
    └── Polecat-29 (worker agent)
```

### 3.3 Rig Structure

Each rig has:
- **Rig ID**: Unique identifier
- **Town ID**: Parent town grouping
- **Worktrees**: Isolated git worktrees per agent/task
- **Shared State**: Via bead status and convoy tracking

---

## 4. Workflow Example

### 4.1 Creating a Convoy

1. **Initialize**: Create convoy bead
   ```bash
   gt_bead_create --type convoy --title "Feature X"
   ```

2. **Add Beads**: Attach related work items
   ```bash
   gt_bead_create --type issue --title "Implement X" --convoy-id <convoy_id>
   ```

3. **Dispatch**: Assign to agent(s)
   ```bash
   gt_sling_batch --bead-ids <id1,id2> --agent-id polecat-29
   ```

### 4.2 Agent Execution

Agent workflow:
1. **Prime**: Call `gt_prime` for context (hooked bead, mail, open beads)
2. **Work**: Implement according to bead requirements
3. **Commit**: Small, focused commits with descriptive messages
4. **Checkpoint**: Call `gt_checkpoint` after milestones
5. **Done**: Push branch, call `gt_done`

### 4.3 Review and Merge

1. **Submit**: `gt_done` transitions bead to `in_review`
2. **Refinery**: Picks up for merge evaluation
3. **Merge**: Uses appropriate merge mode
4. **Close**: Bead transitions to `merged` or `closed`

---

## 5. Quality Gates

Before calling `gt_done`, run all quality gates:

```bash
task quality
```

Gates include:
- Lint checks
- Type checks  
- Unit tests
- Integration tests

---

## 6. Coordination Patterns

### 6.1 Mail and Nudges

**gt_mail_send**: Formal persistent message
```bash
gt_mail_send --to-agent-id <id> --subject "..." --body "..."
```

**gt_nudge**: Immediate wake-up signal
```bash
gt_nudge --target-agent-id <id> --message "..."
```

### 6.2 Escalation

Blocked beads escalate via:
```bash
gt_escalate --title "Issue description" --body "..." --priority high
```

Creates escalation bead routed to supervisor/mayor.

### 6.3 Checkpointing

Save progress for crash recovery:
```bash
gt_checkpoint --data '{"step": "completed", "files": [...]}'
```

---

## 7. thegent-Specific Implementation

### 7.1 Branch Discipline

```
repos/worktrees/<project>/<category>/<branch>
```

Example:
```
repos/worktrees/thegent/gt/polecat-29/c4c630ce
```

### 7.2 Canonical Repository

- Main branch (`main`) is canonical
- All feature work in worktrees
- Return to main for merge/integration checkpoints

### 7.3 Sub-Agent Coordination

thegent dispatches work to sub-agents via:
1. **CLI runner**: `thegent run <agent> "<command>"`
2. **Batch dispatch**: `thegent dispatch batch --count N`
3. **MCP tools**: Via MCP server interface

---

## 8. References

- AgilePlus Methodology: `docs/plans/AGILEPLUS_SPEC.md`
- Subagent Dispatch: `docs/plans/10-SUBAGENT-DISPATCH.md`
- Lifecycle Loop: `docs/plans/12-LIFECYCLE-LOOP-DESIGN.md`
- thegent Architecture: `ARCHITECTURE_OVERVIEW.md`
