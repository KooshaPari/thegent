# Merged Fragmented Markdown

## Source: reference/AGENTS_ACTIVE.md

# AGENTS_ACTIVE

Active agent tracking for the swarm controller. This file is auto-updated by the Swarm Controller monitoring loop.

**Last Updated**: None (awaiting first controller run)

---

## Agent Status Summary

| Total | Healthy | Unhealthy | Paused | Dead | Queue Depth |
|-------|---------|-----------|--------|------|-------------|
| 0 | 0 | 0 | 0 | 0 | 0 |

---

## Active Agents

| Agent ID | Status | PID | Restarts | CPU % | Memory % | Errors | Last Activity |
|----------|--------|-----|----------|-------|----------|--------|---------------|
| researcher-1 | IDLE (awaiting assignment) | -- | 0 | -- | -- | 0 | 2026-02-19 13:00 - Phase 2 already COMPLETED, notified L1, awaiting new assignment |

---

## Recent Events

### Healthy Agents
(None currently tracked)

### Paused Agents
(None currently tracked)

### Unhealthy Agents
(None currently tracked)

### Dead Agents
(None currently tracked)

---

## Health Trends

### Queue Depth (24h)
```
Pending:  [████░░░░░░░░░░░░░░] 5
Claimed:  [██░░░░░░░░░░░░░░░░] 2
Completed: [██████████████████] 50
```

### Agent Success Rate (24h)
```
Success: 95% [██████████████████░]
Errors:  5%  [█░░░░░░░░░░░░░░░░░]
```

### System Resources (24h)
```
CPU:     [████░░░░░░░░░░░░░░] avg 40%
Memory:  [███░░░░░░░░░░░░░░░] avg 35%
```

---

## Configuration

| Setting | Value |
|---------|-------|
| Health Check Interval | 10s |
| Stale Threshold | 30s |
| SLO Multiplier | 1.5x |
| Max Concurrent Agents | 10 |
| Min Concurrent Agents | 1 |
| CPU Threshold | 80% |
| Memory Threshold | 70% |
| Max Restart Attempts | 3 |
| Scale Up Queue Threshold | 5 items |
| Scale Down Queue Threshold | 2 items |

---

## Quick Links

- **Controller Log**: `.claude/swarm_controller.log`
- **Controller State**: `.claude/swarm_state.json`
- **Configuration**: `config/swarm_controller_config.yaml`
- **Usage Guide**: `docs/guides/SWARM_CONTROLLER_USAGE.md`
- **Work Stream**: `docs/reference/WORK_STREAM.md`

---

## Escalation Contacts

### Level 1 (Operational)
- Check logs: `tail -100 .claude/swarm_controller.log`
- Resume agent: `python scripts/swarm_controller.py --resume-agent <id>`
- Check health: `python scripts/swarm_controller.py --report`

### Level 2 (Engineering)
- Investigate root cause in agent logs
- Review controller configuration
- Check system resources (CPU, memory, disk)

### Level 3 (Critical)
- Dead agents (exceeded max restart attempts)
- Sustained resource pressure (>1 hour)
- Queue backlog growing (pending >> completed)

---

## Notes

This file is managed by the Swarm Controller. Manual updates are possible but will be overwritten on next controller cycle.

To manually update:
```bash
# Resume a paused agent
python scripts/swarm_controller.py --resume-agent <agent-id>

# Pause an agent
python scripts/swarm_controller.py --pause-agent <agent-id>

---

## Source: reference/COORDINATION.md

# Multi-Level Coordination (L1/L2/L3)

**Status:** Active | **Last Updated:** 2026-02-18 | **Framework:** Three-Level Hierarchy

---

## Overview

The multi-level coordination system defines three hierarchical layers for managing concurrent work across a distributed team of AI agents and human operators. This framework ensures safe, predictable, and observable multi-actor execution without resource conflicts or work duplication.

### Three-Level Hierarchy

```
┌─────────────────────────────────────────────────────┐
│          L1: Coordinator (Claude Code)              │
│  - User intent & strategic decisions                │
│  - Work item creation & triage                       │
│  - Dependency resolution & conflict arbitration      │
│  - Progress monitoring & reporting                   │
└─────────────────────────────────────────────────────┘
                           │
                           │ Delegates to
                           ▼
┌─────────────────────────────────────────────────────┐
│        L2: Teammates (Named Agents)                 │
│  - Component ownership (auth, api, frontend, etc.)  │
│  - Task claiming & execution                        │
│  - Blockedby/Blocks relationship management         │
│  - Sub-task delegation to L3                        │
└─────────────────────────────────────────────────────┘
                           │
                           │ Dispatches to
                           ▼
┌─────────────────────────────────────────────────────┐
│       L3: Thegent Agents (Free/Premium)             │
│  - Sub-task execution (exploration, implementation) │
│  - Pattern searches, file operations                │
│  - Parallel work on independent subtasks            │
│  - Background execution (--bg)                      │
└─────────────────────────────────────────────────────┘
```

---

## Level 1: Coordinator (Claude Code)

**Role:** Strategic orchestrator and decision maker.

### Responsibilities

1. **User Intent Capture**
   - Clarify ambiguous requests
   - Translate user language into structured work items
   - Set strategic direction and priorities

2. **Work Stream Management**
   - Create new work items in `docs/reference/WORK_STREAM.md`
   - Triage and prioritize based on dependencies
   - Monitor overall progress (PENDING → CLAIMED → COMPLETED)

3. **Team Coordination**
   - Create teams with `TeamCreate` when multi-actor work needed
   - Assign L2 teammates with clear, isolated components
   - Maintain team roster in `~/.claude/teams/{team-name}/config.json`

4. **Dependency Resolution**
   - Identify blockedBy/Blocks relationships
   - Detect and resolve circular dependencies
   - Create work items to unblock stalled tasks

5. **Decision Gates**
   - Architecture decisions (technology choices, patterns)
   - Resource allocation (how many agents, which models)
   - Conflict resolution (when agents disagree or have conflicting goals)
   - Trade-off decisions (speed vs. quality, breadth vs. depth)

6. **Progress Reporting**
   - Summarize completed phases
   - Report blockers and risks
   - Update trackers and status documents

### Tools Used

- `TeamCreate` - Create new teams with designated agents
- `TaskCreate`, `TaskUpdate`, `TaskList` - Work stream management
- `SendMessage` - Direct communication with L2 teammates
- `Read`, `Write` - Work stream and documentation updates
- `Bash` - Work stream queries and reports

### Decision Authority

L1 has **final authority** on:
- Strategic direction and priorities
- Team composition and role assignments
- Architecture and major design choices
- Conflict resolution between teams or agents
- Resource constraints and SLOs

L1 **delegates execution** to L2 but retains veto power over direction changes.

---

## Level 2: Teammates (Named Agents)

**Role:** Component owners responsible for specific functional areas or features.

### Responsibilities

1. **Component Ownership**
   - Own specific modules, services, or features (e.g., "auth", "api", "frontend")
   - Understand all code and dependencies within component
   - Responsible for component health and test coverage

2. **Task Claiming & Execution**
   - Monitor `WORK_STREAM.md` for available work
   - Claim items by adding to CLAIMED section with agent_id and timestamp
   - Move claimed items to IN_PROGRESS during active work
   - Complete items by moving to COMPLETED with duration

3. **Sub-Task Decomposition**

---

## Source: reference/COORDINATION_INDEX.md

# Phase 6: Coordination Setup - Complete Index

**Status:** Complete | **Last Updated:** 2026-02-18 | **Total Documents:** 5

---

## Overview

This index documents the complete coordination framework for Phase 6, enabling multi-agent teams to work safely and efficiently on shared codebases.

### Documents Created

| Document | Size | Purpose | Status |
|----------|------|---------|--------|
| **COORDINATION.md** | 24 KB | Three-level hierarchy, workflows, recovery | ✓ Complete |
| **AGENTS_ACTIVE.md** | 8.5 KB | Agent registry, team management | ✓ Complete |
| **TUI_DASHBOARD_DESIGN.md** | 34 KB | Dashboard mockup, implementation plan | ✓ Complete |
| **FAILURE_RECOVERY_PLAYBOOK.md** | 27 KB | 10 FRP scenarios, decision tree | ✓ Complete |
| **COORDINATION_INDEX.md** | This file | Cross-reference and navigation | ✓ Complete |

**Total:** 93.5 KB of coordination documentation

---

## Quick Navigation

### For Claude Code (L1 Coordinators)

**Getting Started:**
1. Read: [COORDINATION.md - Level 1 Section](COORDINATION.md#level-1-coordinator-claude-code)
2. Review: [AGENTS_ACTIVE.md - Team Composition Patterns](AGENTS_ACTIVE.md#team-composition-patterns)
3. Understand: [TUI_DASHBOARD_DESIGN.md - Overview](TUI_DASHBOARD_DESIGN.md#overview)

**Operational Tasks:**
- Creating a team → [COORDINATION.md - Team Coordination](COORDINATION.md#team-coordination)
- Assigning work → [AGENTS_ACTIVE.md - Commands](AGENTS_ACTIVE.md#commands-for-registry-management)
- Monitoring progress → [TUI_DASHBOARD_DESIGN.md - Full Dashboard](TUI_DASHBOARD_DESIGN.md#full-dashboard-layout-160x40-minimum)
- Resolving failures → [FAILURE_RECOVERY_PLAYBOOK.md - Decision Tree](FAILURE_RECOVERY_PLAYBOOK.md#recovery-decision-tree)

### For L2 Teammates (Named Agents)

**Getting Started:**
1. Read: [COORDINATION.md - Level 2 Section](COORDINATION.md#level-2-teammates-named-agents)
2. Learn: [COORDINATION.md - CLAIMED Workflow](COORDINATION.md#claimed-workflow)
3. Practice: [COORDINATION.md - COMPLETED Workflow](COORDINATION.md#completed-workflow)

**During Execution:**
- Finding work → `thegent plan do-next`
- Claiming task → [COORDINATION.md - CLAIMED Step 3](COORDINATION.md#3-agent-claims-item)
- Updating status → [COORDINATION.md - COMPLETED Step 4](COORDINATION.md#4-unblock-downstream-tasks)
- Reporting blockers → [COORDINATION.md - CLAIMED Workflow - Step 5](COORDINATION.md#5-commit--push)
- When stuck → [FAILURE_RECOVERY_PLAYBOOK.md - FRP-6](FAILURE_RECOVERY_PLAYBOOK.md#frp-6-slo-breach-task-running-10x-estimate)

### For L3 Thegent Agents

**Getting Started:**
1. Read: [COORDINATION.md - Level 3 Section](COORDINATION.md#level-3-thegent-agents-freepremium)
2. Understand: [AGENTS_ACTIVE.md - Agent Lifecycle States](AGENTS_ACTIVE.md#agent-lifecycle-states)

**During Execution:**
- Follow L2 instructions exactly
- Report results via file writes or stdout
- If stuck, escalate to L2 (don't make decisions)
- No independent work claiming

---

## Workflow Quick Reference

### CLAIMED Workflow (L2)

```
1. Read WORK_STREAM.md
2. Find task with Status=PENDING, Dependencies=met
3. Add to CLAIMED section with agent_id + timestamp
4. Change task Status from PENDING → CLAIMED
5. Commit & push immediately
6. Start work on task
```

📄 **Full details:** [COORDINATION.md - CLAIMED Workflow](COORDINATION.md#claimed-workflow)

### COMPLETED Workflow (L2)

```
1. Finish implementation, tests, docs
2. Remove from CLAIMED, add to COMPLETED
3. Update original task Status → COMPLETED
4. Update related trackers (PLAN_STATUS, CODE_ENTITY_MAP)
5. Commit & push
6. Move dependent tasks to available queue
```

📄 **Full details:** [COORDINATION.md - COMPLETED Workflow](COORDINATION.md#completed-workflow)

### Recovery Workflows (L1)

| Failure | Handler | Reference |
|---------|---------|-----------|
| Agent timeout | Release task, force kill if needed | [FRP-1](FAILURE_RECOVERY_PLAYBOOK.md#frp-1-agent-crashtimeout-during-execution) |
| Race condition | Break tie, lock WORK_STREAM.md | [FRP-2](FAILURE_RECOVERY_PLAYBOOK.md#frp-2-duplicate-task-claims-race-condition) |
| Circular dependency | Break cycle by redesign | [FRP-3](FAILURE_RECOVERY_PLAYBOOK.md#frp-3-circular-dependencies) |
| File merge conflict | Manual merge + verify | [FRP-4](FAILURE_RECOVERY_PLAYBOOK.md#frp-4-file-conflict-multiple-agents-editing-same-file) |
| Regression after completion | Reopen task, fix, test | [FRP-5](FAILURE_RECOVERY_PLAYBOOK.md#frp-5-regression-after-completion) |
| SLO breach (10x estimate) | Investigate, split, adjust | [FRP-6](FAILURE_RECOVERY_PLAYBOOK.md#frp-6-slo-breach-task-running-10x-estimate) |
| Git conflict in WORK_STREAM | Manual merge, prevent future | [FRP-7](FAILURE_RECOVERY_PLAYBOOK.md#frp-7-git-conflict-in-work_streammd) |
| Blocker 30+ min | Escalate dependency | [FRP-8](FAILURE_RECOVERY_PLAYBOOK.md#frp-8-blocker-slo-breach-task-waiting-30-minutes) |
| Permission/file lock error | Fix perms, remove lock | [FRP-9](FAILURE_RECOVERY_PLAYBOOK.md#frp-9-permissionfile-locking-issues) |
| No more work | Verify complete, next phase | [FRP-10](FAILURE_RECOVERY_PLAYBOOK.md#frp-10-work-stream-depletion-all-tasks-claimedcomplete) |

---

## File Locations

### Primary Coordination Files

```
docs/reference/
├── COORDINATION.md ..................... Three-level hierarchy & workflows
├── AGENTS_ACTIVE.md .................... Agent registry & team management

---

## Source: reference/EXECUTION_KICKOFF_2026-02-18.md

# Execution Kickoff: Multi-Level Agent Coordination

**Date:** 2026-02-18 | **Status:** ACTIVE | **L1 Lead:** Claude Code
**Work Stream:** `docs/reference/WORK_STREAM.md` (canonical source of truth)

---

## Overview

This document activates the **3-level agent hierarchy** for parallel work execution:

```
┌─────────────────────────────┐
│  L1: Claude Code (Main)     │  ← Strategic decisions, blockers, dependencies
├─────────────────────────────┤
│  L2: Named Teammates (3)    │  ← Task claiming, component ownership, L3 delegation
├─────────────────────────────┤
│  L3: Thegent Agents (free)  │  ← Sub-task execution, exploration, implementation
└─────────────────────────────┘
```

---

## L2 Teammate Agents (Named)

### researcher-1
- **Role:** Discovery, analysis, research tasks
- **Component:** Phase 2 (Async State & Snapshots)
- **Capabilities:** Code exploration, file analysis, pattern discovery
- **Work Items:** TGNT-P2.1 → TGNT-P2.4
- **Cycle Time Target:** 5-15 min per item
- **Status:** IDLE → Ready to claim

**Claim Protocol:**
1. Read WORK_STREAM.md PENDING section for Phase 2
2. Pick highest-priority unclaimed item with met dependencies
3. Add to CLAIMED table: `| researcher-1 | TGNT-P2.X | In Progress | 2026-02-18 13:XX |`
4. Execute via `thegent free "Implement TGNT-P2.X: <description>"`
5. On completion, update WORK_STREAM.md: move from PENDING → COMPLETED
6. Return to step 1 until Phase 2 exhausted or blocker encountered

### builder-1
- **Role:** Feature implementation, core system building
- **Component:** Phase 3 (Caching & Metrics)
- **Capabilities:** System design, implementation, testing
- **Work Items:** TGNT-P3.1 → TGNT-P3.5
- **Cycle Time Target:** 8-20 min per item
- **Status:** IDLE → Ready to claim

**Claim Protocol:** (Same as researcher-1, but Phase 3 items)

### integrator-1
- **Role:** Integration, testing, coordination
- **Component:** Phase 4-5 (Intelligence & Context)
- **Capabilities:** Integration testing, E2E scenarios, validation
- **Work Items:** TGNT-P4.* → TGNT-P5.*
- **Cycle Time Target:** 5-15 min per item
- **Status:** IDLE → Standby (unblock after Phase 2-3 complete)

**Trigger:** Activate when **both** Phase 2 AND Phase 3 have **≥50% completion**

---

## First Batch: Phase 2-3 Parallelization (NOW)

### Batch Summary
- **Duration:** ~25-40 min (both workers in parallel)
- **Goal:** Complete Phase 2 (Discovery) + Phase 3 (Building)
- **Independent:** Yes (no Phase 2 → Phase 3 dependencies)
- **Next Gate:** Check Phase 4 prerequisites before integrator-1 activation

### Phase 2: Async State & Snapshots (researcher-1)

| ID | Title | Depends On | Effort | Notes |
|----|-------|-----------|--------|-------|
| TGNT-P2.1 | Async state snapshots (jq serialization) | TGNT-P0.4 | ~5min | Use jq for JSON extraction + timestamps |
| TGNT-P2.2 | State diff calculation (recursive, null handling) | TGNT-P2.1 | ~8min | Detect changed fields, preserve structure |
| TGNT-P2.3 | State versioning (SHA256 hash per snapshot) | TGNT-P2.1 | ~5min | Unique version ID per state change |
| TGNT-P2.4 | Timeline aggregation (reverse chronological) | TGNT-P2.3 | ~5min | Query capabilities: `state at <time>` |

**Researcher Execution Flow:**
```
1. thegent free --do-next  # Auto-claim TGNT-P2.1
2. Implement async snapshots
3. Mark COMPLETED in WORK_STREAM
4. thegent free --do-next  # Auto-claim TGNT-P2.2
5. ... repeat for P2.3, P2.4
6. Check Phase 2 status: all COMPLETED? → Signal integrator-1 to standby
```

### Phase 3: Caching & Metrics (builder-1)

| ID | Title | Depends On | Effort | Notes |
|----|-------|-----------|--------|-------|
| TGNT-P3.1 | Rebuild strategy (invalidation heuristics) | TGNT-P0.4 | ~8min | When to invalidate entire cache vs partial |
| TGNT-P3.2 | Partial rebuild (diff-aware re-execution) | TGNT-P3.1 | ~10min | Only re-run affected downstream items |
| TGNT-P3.3 | Preload optimization (predict hot keys) | TGNT-P0.4 | ~8min | Load likely-accessed entries at startup |
| TGNT-P3.4 | Build timing (profile hot paths, cutoff threshold) | TGNT-P3.1, TGNT-P3.2 | ~5min | Measure rebuild cost, skip if <10ms gain |
| TGNT-P3.5 | Cache integration test (end-to-end scenario) | TGNT-P3.1 → TGNT-P3.4 | ~10min | Verify cache improves harness speed by ≥20% |

**Builder Execution Flow:**
```
1. thegent free --do-next  # Auto-claim TGNT-P3.1
2. Implement rebuild strategy
3. Mark COMPLETED in WORK_STREAM
4. thegent free --do-next  # Auto-claim TGNT-P3.2
5. ... repeat for P3.3 → P3.5
6. Check Phase 3 status: all COMPLETED? → Signal completion to L1
```

---

## Execution Checklist

### Pre-Execution (L1 - This Step)
- [x] WORK_STREAM.md prepared with 186 tasks (all phases)
- [x] COORDINATION.md documents L1/L2/L3 workflows
- [x] AGENTS_ACTIVE.md created with team registry
- [x] Failure recovery playbook (10 scenarios)
- [x] Phase 2-3 work items identified (independent, no blocking)

---

## Source: reference/FAILURE_RECOVERY_PLAYBOOK.md

# Failure Recovery Playbook

**Status:** Active | **Last Updated:** 2026-02-18 | **Scope:** Multi-agent coordination failures

---

## Overview

This playbook defines recovery procedures for common failure scenarios in multi-level coordination. Each scenario includes detection, root cause analysis, and step-by-step recovery with fallback options.

### Quick Symptom Matcher

| Symptom | Root Cause | Playbook Section |
|---------|-----------|------------------|
| Task claimed but no progress for 10+ min | Agent crash/hang | FRP-1 |
| Two agents claim same task | Race condition in WORK_STREAM.md | FRP-2 |
| Task A depends on B, B depends on A | Circular dependency | FRP-3 |
| Multiple agents editing same file, merge conflict | Concurrent file edits | FRP-4 |
| Task marked complete, but downstream finds bug | Incomplete testing/QA | FRP-5 |
| Task estimate 5m, now 45+ min running | SLO breach / scope creep | FRP-6 |
| CLAIMED and PENDING both show same task | Git conflict in WORK_STREAM.md | FRP-7 |
| Blocker waiting 30+ min, upstream task stuck | Dependency SLO breach | FRP-8 |
| Agent reports file already exists / can't create | Permission or file locking issue | FRP-9 |
| All agents idle, no work items available | Work stream depletion | FRP-10 |

---

## FRP-1: Agent Crash/Timeout During Execution

**Symptom:** Task in CLAIMED section, agent not responding, no status update for 10+ minutes.

**Detection:**
```bash
# Check for stale sessions (no update in 10 min)
thegent ps | grep -v updated
# or check WORK_STREAM.md for old timestamps
grep "IN_PROGRESS" docs/reference/WORK_STREAM.md | awk -F'|' '{print $3}' | while read ts; do
  age=$(($(date +%s) - $(date -d "$ts" +%s)))
  if [ $age -gt 600 ]; then echo "STALE: $ts ($age seconds)"; fi
done
```

### Recovery Steps

**Option A: Graceful Recovery (Preferred)**

1. **Attempt Soft Shutdown** (30-second timeout)
   ```bash
   thegent wait {session_id} --timeout 30
   ```
   - If agent responds, it can finish or gracefully abort
   - Check logs to understand what happened:
     ```bash
     tail -100 .process-compose/logs/{session_id}.log
     ```

2. **If Agent Responds:** Let it finish or ask to abort
   ```bash
   # Send message to agent (if TeamCreate used)
   SendMessage type=message recipient="{agent-name}" \
     content="Task running long. Finish if close, else abort and we'll restart."
   ```

3. **Move Task Back to PENDING**
   - Remove from CLAIMED section in WORK_STREAM.md
   - Mark original row as PENDING (revert from CLAIMED)
   - Add note: "Released due to timeout, can be reclaimed"

4. **Commit & Push**
   ```bash
   git add docs/reference/WORK_STREAM.md docs/reference/AGENTS_ACTIVE.md
   git commit -m "Release TGNT-P6.1 due to timeout (stale for 15 min)"
   git push origin main
   ```

**Option B: Force Terminate (If Soft Timeout Fails)**

1. **Force Kill Session** (immediate, no cleanup)
   ```bash
   thegent kill {session_id} --force
   ```

2. **Check for Partial Files**
   ```bash
   # Look for incomplete edits (e.g., .swp, .tmp files)
   git status | grep -E "\.swp|\.tmp|\.bak"
   # If found, clean up:
   rm -f {incomplete-files}
   ```

3. **Abort Any Pending Git Operations**
   ```bash
   # Check for dangling lock files
   ls -la .git/ | grep lock
   # If found, remove (only if process is truly dead)
   rm -f .git/index.lock
   ```

4. **Move Task Back to PENDING** (same as Option A, step 3)

5. **Update AGENTS_ACTIVE.md**
   ```markdown
   | agent-id | ... | ERROR | TGNT-P6.1 | -- | 2026-02-18T14:30:00Z | 2026-02-18T15:45:00Z | 75 min | Force killed after timeout |
   ```

6. **Post-Mortem Analysis**
   - Review task estimate vs. actual
   - Was task scope too large? (should be split)
   - Was task estimate too aggressive? (should be revised)
   - Add note to task for next attempt:
     ```markdown
     | TGNT-P6.1 | ... | ~8min | PENDING | Notes: Consider splitting or increasing estimate |
     ```

### Preventive Measures

1. **Shorter Estimates:** Tasks estimated > 20 min should be split into smaller tasks
2. **Health Checks:** Dashboard auto-alerts if task > 150% of estimate
3. **Heartbeat:** L2 teammates send status update every 5-10 min for long tasks
4. **SLO Timeout:** Automatic timeout at 2x estimate (with warning at 1.5x)

---

## Source: reference/PHASE_1_AGENT_IDENTITY_IMPLEMENTATION.md

# Phase 1: Agent Identity System & Global Registry

**Status:** ✅ Complete
**Date:** 2026-02-19
**Completion:** Agent identity system with global registry implemented and tested

---

## Overview

Phase 1 of the Multi-Tenant Civilization Framework establishes the **foundational agent identity and discovery system** that enables cross-project communication and hierarchical coordination.

### What This Phase Delivers

1. **Unique Agent Identity System** - Every agent gets a globally unique ID: `{project}:{uuid}:L{1-3}:{role}`
2. **Global Agent Registry** - Centralized registry at `~/.claude/civilization/registry.json` for service discovery
3. **Hierarchical Relationships** - Parent-child tracking (L1→L2, L2→L3) with relationship management
4. **Multi-Project Support** - Agents across different projects can discover and communicate
5. **Persistence & Durability** - Registry persists to disk, survives agent restarts

---

## Architecture

### Agent Identity

Each agent has a unique identity captured in `AgentIdentity`:

```
{project}:{uuid}:L{1-3}:{role}

Example: "thegent:abc123:L2:builder"
         "kush:def456:L1:coordinator"
```

**Components:**
- `project` - Project name/path (e.g., "thegent", "kush")
- `uuid` - 8-character unique identifier
- `level` - Hierarchy level (L1, L2, L3)
- `role` - Agent role (coordinator, researcher, builder, integrator, monitor, generic)

### Global Registry

**Location:** `~/.claude/civilization/registry.json`

**Structure:**
```json
{
  "thegent:abc123:L1:coordinator": {
    "project": "thegent",
    "uuid": "abc123",
    "level": "L1",
    "role": "coordinator",
    "created_at": 1234567890.0,
    "last_heartbeat": 1234567890.0,
    "capabilities": ["orchestration", "monitoring"],
    "scope_tags": {"tier": "strategic"},
    "parent_agent_id": null,
    "child_agent_ids": ["thegent:def456:L2:builder"],
    "peer_agent_ids": [],
    "is_active": true,
    "status_message": "healthy",
    "session_id": "session-123",
    "mcp_endpoint": "127.0.0.1:3847"
  },
  ...
}
```

### Hierarchy Model

```
L1 (Strategic Lead - Orchestrator)
├── L2 (Named Worker - Component Owner)
│   ├── L3 (Executor - Free Tier)
│   └── L3 (Executor - Free Tier)
├── L2 (Named Worker - Component Owner)
│   └── L3 (Executor - Free Tier)
└── Peer L1 (Another Project's L1 - for cross-project coordination)
```

---

## Implementation Files

### `scripts/agent_identity_system.py` (427 LOC)

Core implementation with:

1. **Enums:**
   - `AgentLevel` - L1_STRATEGIC, L2_WORKER, L3_EXECUTOR
   - `AgentRole` - RESEARCHER, BUILDER, INTEGRATOR, COORDINATOR, MONITOR, GENERIC

2. **AgentIdentity Dataclass:**
   - Core identity fields (project, uuid, level, role)
   - Timestamps (created_at, last_heartbeat)
   - Relationships (parent_agent_id, child_agent_ids, peer_agent_ids)
   - Capabilities and scope tags
   - Methods: `to_dict()`, `from_dict()`, `agent_id` property

3. **GlobalAgentRegistry Class:**
   - `register_agent()` - Add/update agent
   - `unregister_agent()` - Remove agent (with cleanup)
   - `get_agent()` - Retrieve by ID
   - `get_agents_by_project()` - Filter by project
   - `get_agents_by_level()` - Filter by L1/L2/L3
   - `get_agents_by_role()` - Filter by role
   - `set_relationship()` - Create parent-child relationships
   - `get_hierarchy()` - Retrieve family tree
   - `update_heartbeat()` - Keep-alive mechanism
   - `get_stats()` - Registry statistics
   - Persistence: `_load_from_disk()`, `_save_to_disk()`

4. **AgentIdentityFactory Class:**
   - `create_l1_agent()` - Create strategic leader
   - `create_l2_agent()` - Create named worker with parent
   - `create_l3_agent()` - Create executor with parent
   - Automatic registry integration and relationship setup

### `scripts/test_agent_identity_system.py` (361 LOC)

---

## Source: reference/PHASE_1_MATERIALS_INDEX.md

# Phase 1 Materials Index: Agent Identity System & Global Registry

**Navigation Guide for Phase 1 Deliverables**
**Status:** ✅ Complete | **Date:** 2026-02-19 | **Version:** 1.0

---

## Quick Navigation

### For Developers
1. **Start here:** `PHASE_1_QUICK_REFERENCE.md` (5 min read)
2. **Deep dive:** `PHASE_1_AGENT_IDENTITY_IMPLEMENTATION.md` (15 min read)
3. **Code:** `scripts/agent_identity_system.py` (427 LOC)
4. **Tests:** `scripts/test_agent_identity_system.py` (17 passing tests)

### For Integration
1. **Start here:** `INTEGRATING_AGENT_IDENTITY_WITH_SWARM_CONTROLLER.md` (10 min read)
2. **Implementation:** See step-by-step integration guide
3. **Timeline:** 3-4 hours for full integration

### For Project Managers
1. **Executive summary:** `PHASE_1_COMPLETION_SUMMARY_2026-02-19.md`
2. **Status:** ✅ Complete, 100% tests passing, ready for integration
3. **Next phase:** Phase 2 - Service Discovery Protocol

### For Architects
1. **Architecture:** `PHASE_1_AGENT_IDENTITY_IMPLEMENTATION.md` § Architecture
2. **Integration strategy:** `INTEGRATING_AGENT_IDENTITY_WITH_SWARM_CONTROLLER.md`
3. **Design decisions:** See ADRs in main project

---

## File Organization

```
kush/
├── scripts/
│   ├── agent_identity_system.py         ← Core implementation (427 LOC)
│   └── test_agent_identity_system.py    ← Unit tests (361 LOC, 17 tests)
│
├── docs/
│   ├── reference/
│   │   ├── PHASE_1_AGENT_IDENTITY_IMPLEMENTATION.md    ← Full spec
│   │   ├── PHASE_1_QUICK_REFERENCE.md                  ← Quick ref
│   │   └── PHASE_1_MATERIALS_INDEX.md                  ← This file
│   │
│   ├── guides/
│   │   └── INTEGRATING_AGENT_IDENTITY_WITH_SWARM_CONTROLLER.md  ← Integration
│   │
│   └── reports/
│       └── PHASE_1_COMPLETION_SUMMARY_2026-02-19.md    ← Executive summary
│
└── ~/.claude/civilization/
    └── registry.json                    ← Global registry (created on first use)
```

---

## Document Descriptions

### 1. PHASE_1_QUICK_REFERENCE.md
**Type:** Quick Reference Card
**Read Time:** 5 minutes
**Audience:** All developers
**Content:**
- One-minute overview
- Quick start code snippets
- Common operations table
- Agent roles and levels
- Filtering examples
- Serialization patterns
- Testing instructions
- Common errors & fixes

**When to use:** Quick lookup, getting started, quick examples

---

### 2. PHASE_1_AGENT_IDENTITY_IMPLEMENTATION.md
**Type:** Technical Specification
**Read Time:** 15 minutes
**Audience:** Implementers, architects
**Content:**
- Complete architecture overview
- AgentIdentity dataclass specification
- GlobalAgentRegistry API documentation
- AgentIdentityFactory patterns
- Usage examples (detailed)
- SwarmController integration paths
- Completion checklist
- Known limitations & mitigations
- Validation test results

**When to use:** Deep understanding, integration planning, troubleshooting

---

### 3. INTEGRATING_AGENT_IDENTITY_WITH_SWARM_CONTROLLER.md
**Type:** Integration Roadmap
**Read Time:** 10 minutes for overview, 1-2 hours for implementation
**Audience:** Implementation engineers
**Content:**
- Current state assessment
- Integration strategy (5 steps)
- Step-by-step implementation
- Data flow diagrams
- Complete integration example
- Testing strategy
- Backward compatibility notes
- Common pitfalls & solutions
- Success criteria

**When to use:** Planning SwarmController integration, implementation execution

---

### 4. PHASE_1_COMPLETION_SUMMARY_2026-02-19.md
**Type:** Executive Summary
**Read Time:** 10 minutes
**Audience:** Project managers, executives, stakeholders

---

## Source: reference/PHASE_1_QUICK_REFERENCE.md

# Phase 1: Agent Identity System - Quick Reference

**TL;DR:** Global agent registry with unique IDs and hierarchical relationships

---

## One-Minute Overview

```
Every agent gets a unique ID:  {project}:{uuid}:L{1-3}:{role}
Example:                       thegent:abc123:L2:builder

Registry location:             ~/.claude/civilization/registry.json

Hierarchy:                      L1 (Lead) → L2 (Workers) → L3 (Executors)

Discovery:                      registry.get_agents_by_project("thegent")
```

---

## Quick Start

### Import

```python
from agent_identity_system import (
    GlobalAgentRegistry,
    AgentIdentityFactory,
    AgentLevel,
    AgentRole,
)
```

### Initialize

```python
registry = GlobalAgentRegistry()
factory = AgentIdentityFactory(registry)
```

### Create Agents

```python
# L1: Strategic leader
l1 = factory.create_l1_agent("thegent", AgentRole.COORDINATOR)

# L2: Named worker with parent
l2 = factory.create_l2_agent("thegent", AgentRole.BUILDER, l1.agent_id)

# L3: Executor with parent
l3 = factory.create_l3_agent("thegent", l2.agent_id)
```

---

## Common Operations

| Operation | Code | Returns |
|-----------|------|---------|
| Get agent | `registry.get_agent(agent_id)` | `AgentIdentity \| None` |
| Find all in project | `registry.get_agents_by_project("thegent")` | `List[AgentIdentity]` |
| Find all L1 leaders | `registry.get_agents_by_level(AgentLevel.L1_STRATEGIC)` | `List[AgentIdentity]` |
| Find by role | `registry.get_agents_by_role(AgentRole.BUILDER)` | `List[AgentIdentity]` |
| Get hierarchy | `registry.get_hierarchy(l1_agent_id)` | `Dict[str, Any]` |
| Heartbeat ping | `registry.update_heartbeat(agent_id)` | `bool` |
| Find stale | `registry.get_stale_agents(ttl_seconds=300)` | `List[AgentIdentity]` |
| Statistics | `registry.get_stats()` | `Dict[str, int]` |

---

## Agent Roles

| Role | Use Case |
|------|----------|
| `COORDINATOR` | Orchestration, scheduling, decision-making |
| `RESEARCHER` | Investigation, analysis, discovery |
| `BUILDER` | Implementation, construction, execution |
| `INTEGRATOR` | Integration, coordination, testing |
| `MONITOR` | Observation, health checks, metrics |
| `GENERIC` | Default for L3 executors |

---

## Agent Levels

| Level | Example | Capabilities |
|-------|---------|--------------|
| **L1** | Coordinator | Orchestration, monitoring, escalation |
| **L2** | Named Worker | Component execution, sub-delegation |
| **L3** | Executor | Task execution, reporting |

---

## Agent ID Format

```
{project}:{uuid}:L{level}:{role}

Parts:
- project: "thegent", "kush", etc.
- uuid: 8-character random hex
- level: L1, L2, or L3
- role: coordinator, builder, researcher, etc.

Examples:
- thegent:abc123:L1:coordinator
- kush:def456:L2:builder
- thegent:ghi789:L3:generic
```

---

## Accessing Agent Properties

```python
agent = registry.get_agent(agent_id)

# Identity
agent.project                  # "thegent"

---

## Source: reference/RESILIENCE_PATTERN_COMPARISON.md

# Resilience Pattern Comparison & Decision Trees

**Document Version**: 1.0
**Date**: 2026-02-19
**Category**: Reference, Decision Support
**Purpose**: Quick lookup for pattern selection and configuration

---

## Quick Decision Tree

```
┌─────────────────────────────────────────────────────────────┐
│ What's your problem?                                        │
└─────────────────────────────────────────────────────────────┘
        ↓
┌───────────────────────┬───────────────────────┬─────────────────────┐
│ FAILING               │ SLOW                  │ OVERLOADED          │
│ (errors, crashes)     │ (high latency)        │ (high load)         │
└───────────────────────┴───────────────────────┴─────────────────────┘
        ↓                       ↓                       ↓
   ┌────────────┐          ┌──────────────┐      ┌──────────────────┐
   │ Temporary? │          │ Dependency?  │      │ Traffic spike?   │
   └────────────┘          └──────────────┘      └──────────────────┘
       ↙    ↘                  ↙    ↘                  ↙    ↘
      YES   NO               YES   NO               YES   NO
      ↓     ↓                ↓     ↓                ↓     ↓
   RETRY  CIRCUIT          TIMEOUT  SCALE       SHED  ADAPT
   BACKOFF  BREAKER        FALLBACK  WORKERS    LOAD  CONC
```

---

## Pattern Comparison Table

### Complete Feature Matrix

| Feature | Retry | Circuit Breaker | Bulkhead | Timeout | Throttle | Load Shed | Adaptive |
|---------|-------|-----------------|----------|---------|----------|-----------|----------|
| **Transient Failures** | ✅ | - | - | - | - | - | - |
| **Cascading Failure** | - | ✅ | ✅ | - | - | ✅ | - |
| **Slow Responses** | - | - | ✅ | ✅ | - | - | ✅ |
| **Resource Exhaustion** | - | - | ✅ | - | ✅ | ✅ | - |
| **Overload Protection** | - | - | - | - | ✅ | ✅ | ✅ |
| **Auto Recovery** | - | ✅ | - | ✅ | - | - | ✅ |
| **Fair Share** | - | - | ✅ | ✅ | ✅ | - | ✅ |
| **Fast Failure** | - | ✅ | - | ✅ | - | - | - |
| **Config Complexity** | Low | Medium | Low | Low | Medium | Medium | High |
| **Operational Overhead** | Low | Medium | Low | Low | Medium | Medium | High |

### Implementation Complexity

| Pattern | Lines of Code | Maintenance | Learning Curve |
|---------|---------------|-------------|-----------------|
| Retry | < 10 | Minimal | Beginner |
| Circuit Breaker | 50-100 | Medium | Intermediate |
| Bulkhead | 20-50 | Low | Beginner |
| Timeout | < 5 | Minimal | Beginner |
| Throttle | 30-80 | Low-Medium | Intermediate |
| Load Shed | 40-100 | Medium | Intermediate |
| Adaptive Concurrency | 100-200 | High | Advanced |

### Performance Impact

| Pattern | CPU Overhead | Memory Overhead | Latency | Throughput |
|---------|--------------|-----------------|---------|------------|
| Retry | Low | Low | +100-1000ms | -10-30% |
| Circuit Breaker | Very Low | Low | 0-5ms | +5-20% |
| Bulkhead | Low | Medium | 0-10ms | +10-30% |
| Timeout | Very Low | Low | 0ms | 0% |
| Throttle | Very Low | Medium | +50-500ms | -5-50% |
| Load Shed | Low | Low | 0-5ms | +5-20% |
| Adaptive Conc | Medium | High | -5-20% | +20-40% |

---

## Pattern Scenario Matrix

### When to Use Each Pattern

#### SCENARIO: External API Integration

| Aspect | Pattern | Recommendation |
|--------|---------|-----------------|
| **Primary** | Circuit Breaker | Prevent cascading failures when API is down |
| **Secondary** | Retry + Backoff | Handle transient network errors |
| **Tertiary** | Timeout | Prevent hanging requests |
| **Fallback** | Cached Response | Use stale data if API down |
| **Config** | CB: fail_max=5, timeout=60s | |
| | Retry: max_attempts=3, exp_backoff | |
| | Timeout: 30s HTTP, 5s DB | |

#### SCENARIO: Database Connection Management

| Aspect | Pattern | Recommendation |
|--------|---------|-----------------|
| **Primary** | Connection Pool | Reuse connections; prevent exhaustion |
| **Secondary** | Bulkhead | Separate pools for OLTP vs OLAP |
| **Tertiary** | Timeout | Kill slow queries |
| **Quaternary** | Circuit Breaker | Detect DB unavailability |
| **Config** | Pool size: 20-50 | |
| | Max wait: 5-30s | |
| | Query timeout: 5-10s | |

#### SCENARIO: Microservice Mesh

| Aspect | Pattern | Recommendation |
|--------|---------|-----------------|
| **Primary** | Circuit Breaker | Service-to-service failure isolation |
| **Secondary** | Retry + Backoff | Transient service restarts |
| **Tertiary** | Timeout | Prevent resource exhaustion |
| **Quaternary** | Bulkhead | Isolate critical paths |
| **Quinary** | Load Shed | Graceful degradation under spike |
| **Config** | Per-service circuit breaker | |
| | Deadline propagation (timeouts) | |

#### SCENARIO: Background Task Queue

| Aspect | Pattern | Recommendation |
|--------|---------|-----------------|

---

## Source: reference/TUI_DASHBOARD_DESIGN.md

# TUI Dashboard Design & Implementation

**Status:** Design Phase | **Last Updated:** 2026-02-18 | **Purpose:** Real-time coordination monitoring

---

## Overview

The TUI Dashboard provides L1 coordinators with real-time visibility into:
- Work stream status (PENDING, CLAIMED, COMPLETED)
- Active agents and their progress
- Blockers and dependencies
- Health metrics and SLO status
- Phase progress and predictions

### Design Principles

1. **Dense Information** - Show as much relevant data as possible in fixed screen space
2. **Actionable** - Highlight issues that require immediate action
3. **Auto-Refresh** - Update every 2-5 seconds without user intervention
4. **Keyboard-Driven** - Navigate and interact via hotkeys, no mouse required
5. **Color-Coded** - Use colors for status (green=good, yellow=warning, red=critical)
6. **ASCII-Safe** - Use Unicode box drawing, compatible with all terminals

---

## Full Dashboard Layout (160x40 minimum)

```
┌────────────────────────────────────────────────────────────────────────────┐
│ KUSH COORDINATION MONITOR - 2026-02-18 15:30:45 UTC [PHASE 6: Git Parallel]│
├────────────────────────────────────────────────────────────────────────────┤
│ Status: ●ACTIVE │ PENDING: 12 │ CLAIMED: 3 │ COMPLETED: 5 │ BLOCKED: 2   │
├─────────────────────────────────────────────────┬──────────────────────────┤
│ ACTIVE AGENTS (3/5)                             │ PHASE 6: 45% COMPLETE   │
├────────────┬────────────┬─────────────────┬──────┼──────────────────────────┤
│ Agent      │ Task ID    │ Task Title      │ Elapsed      │ Est  │ Status    │
├────────────┼────────────┼─────────────────┼─────────────┼──────┼───────────┤
│ dev-1      │ TGNT-P6.1  │ GIT_INDEX ...   │ [████░░░] 15m│ 8m   │ On track │
│ tester     │ TGNT-P6.3  │ CAS ref update  │ [██░░░░░] 4m │ 5m   │ Early    │
│ integrator │ TGNT-P6.5  │ git status cmd  │ [███░░░░] 7m │ 3m   │ Over     │
├─────────────────────────────────────────────────┴──────────────────────────┤
│ BLOCKERS & DEPENDENCIES (2)                                                │
├────────────┬───────────────────────┬─────────────┬──────────────────────────┤
│ Blocked ID │ Blocked By (Ready?)   │ Time Waiting│ Action                   │
├────────────┼───────────────────────┼─────────────┼──────────────────────────┤
│ TGNT-P6.7  │ TGNT-P6.5 (2m left)   │ 5 min       │ Will auto-unblock soon  │
│ TGNT-P7.1  │ PHASE 6 (50%, 8m ETA) │ 18 min      │ Start parallel prep work?│
├────────────────────────────────────────────────────────────────────────────┤
│ NEXT AVAILABLE (top 5)                                                      │
├────────────┬─────────────────────────────┬──────┬────────┬──────────────────┤
│ Task ID    │ Title                       │ Est. │ Ready? │ Recommended Agent│
├────────────┼─────────────────────────────┼──────┼────────┼──────────────────┤
│ TGNT-P6.6  │ Performance benchmarks       │ 10m  │ ✓ YES  │ Idle agent-2     │
│ TGNT-P6.8  │ Documentation updates       │ 5m   │ ✓ YES  │ Idle agent-4     │
│ TGNT-P6.9  │ Integration test suite      │ 15m  │ ✗ WAIT │ Waiting: P6.7    │
├────────────────────────────────────────────────────────────────────────────┤
│ RECENT COMPLETIONS (last 30 min)                                           │
├────────────┬────────────────┬────────────────┬──────────────────────────────┤
│ Task ID    │ Agent          │ Completed      │ Duration │ Quality Check    │
├────────────┼────────────────┼────────────────┼──────────┼──────────────────┤
│ TGNT-P6.4  │ dev-2          │ 15:18 (12m ago)│ 22 min   │ ✓ PASS (tests)   │
│ TGNT-P6.2  │ implementation │ 15:05 (25m ago)│ 18 min   │ ✓ PASS (lint)    │
│ TGNT-P6.0  │ research       │ 14:55 (35m ago)│ 10 min   │ ✓ PASS (review)  │
├────────────────────────────────────────────────────────────────────────────┤
│ HEALTH METRICS                                                             │
├────────────────────────────────────────────────────────────────────────────┤
│ • Avg Task Duration:    18 min (est: 8 min, +125%) ⚠ SLO WATCH             │
│ • Cycle Time:           18 min (target: 15 min) ⚠ Trending upward         │
│ • Agent Utilization:    60% (3/5 active) ✓ Healthy                        │
│ • Success Rate:         100% (0 errors in last 10 tasks) ✓ Good           │
│ • Blocker Count:        2 (1 medium, 1 low) ✓ Acceptable                  │
│ • Phase ETA:            16:45 UTC (45 min from now)                        │
│ • Quality Gate:         ✓ PASS (lint, tests, coverage) – Ready to merge    │
├────────────────────────────────────────────────────────────────────────────┤
│ COMMANDS: [A]gents [W]orkstream [B]lockers [S]tats [H]elp [Q]uit • F5 refresh
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Screen Breakdowns

### 1. Header (Fixed Top)

```
┌────────────────────────────────────────────────────────────────────────────┐
│ KUSH COORDINATION MONITOR - 2026-02-18 15:30:45 UTC [PHASE 6: Git Parallel]│
├────────────────────────────────────────────────────────────────────────────┤
│ Status: ●ACTIVE │ PENDING: 12 │ CLAIMED: 3 │ COMPLETED: 5 │ BLOCKED: 2   │
└────────────────────────────────────────────────────────────────────────────┘
```

**Components:**
- **Title**: Always visible, shows project and current phase
- **Timestamp**: UTC time, auto-updates every second
- **Status Indicator**: Colored dot (● green=healthy, ● yellow=warning, ● red=critical)
- **Quick Stats**: Count of items in each state

**Color Coding:**
- Green: All metrics healthy, no blockers
- Yellow: 1-2 warnings, SLO approaching, 1-2 blockers
- Red: Active failures, multiple blockers, critical SLO breaches

### 2. Active Agents Section (Scrollable)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ACTIVE AGENTS (3/5)                                                         │
├────────────┬────────────┬─────────────────┬────────────┬──────┬──────────────┤
│ Agent      │ Task ID    │ Task Title      │ Elapsed    │ Est  │ Status       │
├────────────┼────────────┼─────────────────┼────────────┼──────┼──────────────┤
│ dev-1      │ TGNT-P6.1  │ GIT_INDEX...    │ [████░░░] │ 8m   │ ✓ On track   │
│            │            │                 │ 15m / 8m   │      │              │
├────────────┼────────────┼─────────────────┼────────────┼──────┼──────────────┤
│ tester     │ TGNT-P6.3  │ CAS ref update  │ [██░░░░░] │ 5m   │ ✓ Early      │
│            │            │                 │ 4m / 5m    │      │              │
├────────────┼────────────┼─────────────────┼────────────┼──────┼──────────────┤
│ integrator │ TGNT-P6.5  │ git status cmd  │ [███░░░░] │ 3m   │ ⚠ Over time  │
│            │            │                 │ 7m / 3m    │      │              │

---

## Source: reference/WORK_STREAM.md

# Unified Work Stream

**Status:** Active | **Last Updated:** 2026-02-18 | **Total Items:** 130+ | **Source:** thegent/PLAN.md + sharecli/PLAN.md

---

## Schema

| Column | Description |
|--------|-------------|
| **ID** | Unique task identifier (format: `{PROJECT}-{PHASE}.{TASK}` or `P{PHASE}.{TASK}`) |
| **Title** | Task description (brief, <80 chars) |
| **Type** | `feature` \| `refactor` \| `bugfix` \| `infra` \| `research` \| `docs` |
| **Project** | `thegent` or `sharecli` |
| **Phase** | Phase number (0-18) or epic name |
| **Depends On** | Prerequisite task IDs (comma-separated) |
| **Effort** | Estimate: `~3min` / `~5min` / `~8min` / `~10min` / `~15min` / `~20min` |
| **Status** | `PENDING` / `CLAIMED` / `IN_PROGRESS` / `COMPLETED` / `BLOCKED` |

---

## PENDING

All actionable, unassigned work items. Ordered by project, phase, then task ID.

### thegent: Phase 0 (Foundation - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P0.1 | Symlink dispatch mechanism (`bin/harness` + N symlinks) | infra | -- | ~5min | COMPLETED |
| TGNT-P0.2 | Agent detection via `/proc` tree walk with macOS `ps` fallback | infra | TGNT-P0.1 | ~5min | COMPLETED |
| TGNT-P0.3 | `rules.conf` parser (command, strategy, options) | infra | TGNT-P0.1 | ~3min | COMPLETED |
| TGNT-P0.4 | Coalesce strategy (flock + SHA256 cache key + atomic writes) | infra | TGNT-P0.2, TGNT-P0.3 | ~10min | COMPLETED |
| TGNT-P0.5 | Queue strategy (bounded concurrency pool with slot files) | infra | TGNT-P0.3 | ~8min | COMPLETED |
| TGNT-P0.6 | Debounce strategy (delay + coalesce within window) | infra | TGNT-P0.3 | ~5min | COMPLETED |
| TGNT-P0.7 | `harness sync` symlink generator from rules.conf | infra | TGNT-P0.3 | ~3min | COMPLETED |
| TGNT-P0.8 | `nocache_args` safety (`--fix` / `--write` -> queue fallback) | infra | TGNT-P0.4 | ~3min | COMPLETED |

### thegent: Phase 1 (Quick Wins - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P1.1 | Lock timeout via `HARNESS_LOCK_TIMEOUT` (fallback to uncached) | infra | TGNT-P0.4 | ~3min | COMPLETED |
| TGNT-P1.2 | Stale-while-revalidate (serve stale + background refresh) | infra | TGNT-P0.4 | ~5min | COMPLETED |
| TGNT-P1.3 | Prometheus metrics endpoint (`harness metrics`) | infra | TGNT-P0.4 | ~5min | COMPLETED |
| TGNT-P1.4 | Cache compression (zstd for outputs > 10KB) | infra | TGNT-P0.4 | ~5min | COMPLETED |
| TGNT-P1.5 | JSON metrics export (`harness metrics json`) | infra | TGNT-P1.3 | ~2min | COMPLETED |

### thegent: Phase 2 (Intelligence - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P2.1 | 5-level priority queue (critical/high/normal/low/background) | feature | TGNT-P1.1 | ~8min | COMPLETED |
| TGNT-P2.2 | Priority aging (+1 level per 5s waiting, prevents starvation) | feature | TGNT-P2.1 | ~3min | COMPLETED |
| TGNT-P2.3 | Fair share scheduling (per-agent quota with penalty for over-use) | feature | TGNT-P2.1 | ~8min | COMPLETED |
| TGNT-P2.4 | Semantic coalescing (path normalization, `.` -> project root) | feature | TGNT-P0.4 | ~5min | COMPLETED |
| TGNT-P2.5 | Queue timeout protection (fallback execution on timeout) | feature | TGNT-P2.1 | ~3min | COMPLETED |

### thegent: Phase 3 (Performance - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P3.1 | L1 memory cache (`/dev/shm`, 100MB max, 60s TTL) | infra | TGNT-P0.4 | ~8min | COMPLETED |
| TGNT-P3.2 | L2 disk cache (`var/cache`, compressed, persistent) | infra | TGNT-P0.4 | ~5min | COMPLETED |
| TGNT-P3.3 | L2-to-L1 promotion on cache hit (automatic) | infra | TGNT-P3.1, TGNT-P3.2 | ~5min | COMPLETED |
| TGNT-P3.4 | I/O scheduler integration (ionice priority classes) | feature | TGNT-P2.1 | ~5min | COMPLETED |
| TGNT-P3.5 | Negative stat cache (track nonexistent files, 5s TTL) | feature | TGNT-P3.1 | ~3min | COMPLETED |
| TGNT-P3.6 | Page cache warmer (bulk read by file type before exec) | feature | TGNT-P0.4 | ~5min | COMPLETED |

### thegent: Phase 4 (Coordination - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P4.1 | Intent broadcasting (agents signal planned file ops) | feature | TGNT-P0.4 | ~8min | COMPLETED |
| TGNT-P4.2 | Intent conflict checking (write-write, read-write detection) | feature | TGNT-P4.1 | ~5min | COMPLETED |
| TGNT-P4.3 | Wait-for graph construction from lock records | feature | TGNT-P0.5 | ~8min | COMPLETED |
| TGNT-P4.4 | DFS cycle detection for deadlocks | feature | TGNT-P4.3 | ~5min | COMPLETED |
| TGNT-P4.5 | Deadlock auto-resolution (abort youngest waiter) | feature | TGNT-P4.4 | ~3min | COMPLETED |
| TGNT-P4.6 | Fair share tracking with 50% decay smoothing | feature | TGNT-P2.3 | ~5min | COMPLETED |

### thegent: Phase 5 (Polish - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P5.1 | Interactive dashboard (TUI with cache/queue/intent/fair share) | feature | TGNT-P1.3, TGNT-P2.3, TGNT-P4.1 | ~10min | COMPLETED |
| TGNT-P5.2 | Self-tuning report (analyze metrics, detect low hit rate/contention) | feature | TGNT-P1.3, TGNT-P3.1 | ~8min | COMPLETED |
| TGNT-P5.3 | Auto-fix recommendations (color-coded severity, safe auto-apply) | feature | TGNT-P5.2 | ~5min | COMPLETED |
| TGNT-P5.4 | Rules suggestion engine (generate rules from observed patterns) | feature | TGNT-P5.2 | ~5min | COMPLETED |
| TGNT-P5.5 | L1 vs L2 benchmark command | feature | TGNT-P3.1, TGNT-P3.2 | ~3min | COMPLETED |

### thegent: Phase 6 (Git Parallelism - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P6.1 | Per-agent `GIT_INDEX_FILE` management (init, copy, cleanup) | feature | TGNT-P4.1 | ~8min | COMPLETED |
| TGNT-P6.2 | Git plumbing commit pipeline (hash-object -> write-tree -> commit-tree) | feature | TGNT-P6.1 | ~10min | COMPLETED |
| TGNT-P6.3 | CAS ref update with exponential backoff + jitter retry | feature | TGNT-P6.2 | ~5min | COMPLETED |
| TGNT-P6.4 | Scoped staging (agent-to-file mapping, parallel when non-overlapping) | feature | TGNT-P6.1 | ~5min | COMPLETED |
| TGNT-P6.5 | `harness git status` per-agent view (show each agent's staged changes) | feature | TGNT-P6.4 | ~3min | COMPLETED |

### thegent: Phase 7 (Smart Merge - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P7.1 | Mergiraf integration (AST merge for Python/JS/TS/Rust/Go/Java/C) | feature | TGNT-P6.3 | ~10min | COMPLETED |
| TGNT-P7.2 | Conflict prediction from intents (trial merge before commit) | feature | TGNT-P4.1, TGNT-P6.3 | ~8min | COMPLETED |
| TGNT-P7.3 | Import union auto-resolve (Python/JS import conflicts -> sorted union) | feature | TGNT-P7.1 | ~5min | COMPLETED |
| TGNT-P7.4 | JSON/YAML structural merge (deep merge via jq, ours-wins on conflict) | feature | TGNT-P7.1 | ~5min | COMPLETED |

### thegent: Phase 8 (File Coordination - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P8.1 | OCC version check on write (record version at claim, verify before commit) | feature | TGNT-P4.1 | ~8min | COMPLETED |
| TGNT-P8.2 | HLC timestamp generation (millisecond physical + logical counter) | feature | TGNT-P8.1 | ~5min | COMPLETED |
| TGNT-P8.3 | Lease-based file claims registry (read/write/exclusive with flock) | feature | TGNT-P8.1 | ~8min | COMPLETED |
| TGNT-P8.4 | Lease renewal and expiry (background cleanup daemon) | feature | TGNT-P8.3 | ~5min | COMPLETED |

### thegent: Phase 9 (Request Coalescing v2 - COMPLETE)


---

