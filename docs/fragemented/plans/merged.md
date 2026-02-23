# Merged Fragmented Markdown

## Source: plans/2026-02-21-ENHANCED_SESSION_SCRAPER.md

# Enhanced Session Scraper Plan (WL-156)

## WL-156 Implementation / Status (2026-02-22)

**Status:** Ready for implementation  
**Owner:** WL-156  
**Scope:** Triggered snapshot capture + normalized event emission for session scraping  
**Blockers:** None

### Trigger Schema (input contract)

```json
{
  "event_name": "session.scraper.snapshot.requested",
  "version": "v1",
  "required": [
    "event_id",
    "occurred_at",
    "trigger",
    "project_root"
  ],
  "properties": {
    "event_id": "uuid-v4",
    "occurred_at": "ISO-8601 UTC",
    "trigger": "manual|hook:pre-commit|hook:post-test|timer:15m|session:end",
    "project_root": "absolute path",
    "tags": "string[]",
    "since": "optional ISO-8601 UTC lower bound",
    "max_prompts": "optional int, default 200"
  }
}
```

### Emitted Event Schema (output contract)

```json
{
  "event_name": "session.scraper.snapshot.created",
  "version": "v1",
  "required": [
    "event_id",
    "request_event_id",
    "occurred_at",
    "snapshot_id",
    "snapshot_path",
    "summary"
  ],
  "properties": {
    "event_id": "uuid-v4",
    "request_event_id": "uuid-v4",
    "occurred_at": "ISO-8601 UTC",
    "snapshot_id": "snapshot-YYYYMMDDTHHMMSSffffffZ",
    "snapshot_path": "docs/dumps/session-snapshots/YYYY-MM-DD/*.json",
    "summary": {
      "prompts": "int",
      "commands": "int",
      "files": "int",
      "facts": "int",
      "decisions": "int",
      "tags": "int",
      "sources": "string[]"
    }
  }
}
```

```json
{
  "event_name": "session.scraper.snapshot.failed",
  "version": "v1",
  "required": [
    "event_id",
    "request_event_id",
    "occurred_at",
    "error_code",
    "error_message"
  ],
  "properties": {
    "event_id": "uuid-v4",
    "request_event_id": "uuid-v4",
    "occurred_at": "ISO-8601 UTC",
    "error_code": "SCRAPER_IO|SCRAPER_PARSE|SCRAPER_RUNTIME",
    "error_message": "string",
    "partial_snapshot_path": "optional path"
  }
}
```

### Immediate Next Coding Steps

1. Add `SessionScrapeRequestEvent`, `SessionSnapshotCreatedEvent`, and `SessionSnapshotFailedEvent` `TypedDict` contracts in `thegent/src/thegent/orchestration/state/session_scraper.py`.
2. Add `emit_snapshot_event(...)` in `thegent/src/thegent/orchestration/state/session_scraper.py` and call it from `persist_snapshot(...)` success/failure branches.
3. Add trigger normalization (`manual`, `hook:*`, `timer:*`, `session:end`) in `collect_snapshot(...)` to enforce the schema above.
4. Add unit tests in `thegent/tests/test_unit_session_scraper.py` that validate emitted payload shape for both `snapshot.created` and `snapshot.failed`.
5. Add one batch regression in `thegent/tests/test_unit_session_scraper_batch6.py` that verifies `request_event_id` propagation from request -> created/failed events.


---

## Source: plans/2026-02-21-SESSION_MEMORY_SYSTEM.md

# Session Memory System Plan (WL-155)

## Execution

### Implementation checklist
- [ ] Confirm baseline contracts in `thegent/src/thegent/session/manager.py` and `thegent/src/thegent/session/conversation_dumper.py`.
- [ ] Align capture hooks in `thegent/src/docs_engine/capture/session_hook.py` and `thegent/src/docs_engine/capture/writer.py` with session-memory write/read flow.
- [ ] Validate memory-layer integration points in `thegent/src/thegent/memory/memory_manager.py` and `thegent/src/thegent/infra/memory.py`.
- [ ] Wire/verify CLI surface for session-memory access in `thegent/src/thegent/cli/apps/session.py` and `thegent/src/thegent/cli/apps/memory.py`.
- [ ] Add/update focused coverage in `thegent/tests/session/test_session_manager.py`, `thegent/tests/thegent/session/test_conversation_dumper.py`, and `thegent/tests/memory/test_memory_manager.py`.

### Artifact paths
- Plan artifact: `docs/plans/2026-02-21-SESSION_MEMORY_SYSTEM.md`
- Session runtime code: `thegent/src/thegent/session/`
- Capture pipeline code: `thegent/src/docs_engine/capture/`
- Memory integration code: `thegent/src/thegent/memory/`
- Validation artifacts: `thegent/tests/session/`, `thegent/tests/memory/`, `thegent/tests/docs_engine/`

### Acceptance criteria
- Session lifecycle paths (`create/start/update/end`) persist and retrieve memory without regression in `thegent/src/thegent/session/`.
- Capture output written by `thegent/src/docs_engine/capture/` is consumable by session-memory readers without schema drift.
- Memory manager reads/writes are deterministic for the same session inputs in `thegent/src/thegent/memory/`.
- CLI session/memory commands resolve to the same canonical session id/path behavior for identical inputs.
- Targeted tests for session + memory paths pass with no new failures in touched suites.

---

## Source: plans/2026-02-21-doc-system-design.md

# Agent-Driven Documentation System — Design Doc

**Date:** 2026-02-21
**Status:** Approved — Implementation Ready
**Owner:** Agent (Claude)
**Scope:** thegent + trace + workspace (federation hub)

---

## Executive Summary

Build a fully agent-driven documentation system that covers the complete lifecycle: raw conversation dumps → idea notes → research → specs → worklogs → changelogs → retrospectives → knowledge base extracts. Zero human authoring required. All doc types indexed in SQLite for bidirectional traceability, queried by VitePress data loaders and FastMCP tools.

**Three outputs:**
1. **VitePress docsite** (thegent + trace, 5 views: lab / docs / kb / audit / pm-prep)
2. **SQLite doc index** (all frontmatter + relations, queried by MCP tools + sidebar generator)
3. **Federation hub** (workspace-level VitePress aggregating both projects, replacing MkDocs)

**Out of scope for this phase:** PM/Jira-like Kanban (trace future), companion Next.js app, Fumadocs migration.

---

## 1. Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | VitePress stays as primary docsite (thegent + trace) | 6,000-line sidebar-auto.ts, 8 plugins, full enhancement plan already written — migration to Fumadocs discards all of it |
| D2 | MkDocs workspace hub migrates to VitePress federation hub | Single stack, cross-project-links plugin already works, consistent dev model |
| D3 | SQLite as doc index DB (phase 1) | Zero ops, ships with Python stdlib, embedded in docs-engine package, upgrade path to Postgres later |
| D4 | Fumadocs not adopted | VitePress + Vue components covers all needed surfaces; Next.js runtime not warranted now |
| D5 | docs-engine lives in thegent as Python package | Follows existing pattern (vitepress-agent-workflow.py, generate-sidebar.py, etc.) |
| D6 | Promotion is hybrid | Category auto-promote + frontmatter `status` field + agent-triggered rewrite |
| D7 | Raw Layer 0 docs excluded from VitePress build | Extends existing srcExclude in config.ts |

---

## 2. Doc Type Taxonomy (26 types, 5 layers)

### Layer 0 — Raw/Ephemeral (never built into VitePress)

| Type | File Pattern | Created By | Retention |
|------|-------------|------------|-----------|
| ConversationDump | `docs/research/CONVERSATION_DUMP_YYYY-MM-DD.md` | session-end hook | 90 days then archive |
| SessionMemory | `.claude/.../memory/MEMORY.md` | agent explicit | permanent |
| ScratchNote | `docs/scratch/YYYYMMDD-*.md` | any agent | 48h then auto-promote or discard |
| AgentWorklog | `docs/reference/WORK_STREAM.md` entries | claim/complete pattern | permanent |

### Layer 1 — Informal/Working (VitePress `/lab/` view only)

| Type | File Pattern | Created By | Promoted To |
|------|-------------|------------|-------------|
| IdeaNote | `docs/ideas/YYYY-MM-DD-{slug}.md` | any agent / `docs idea` CLI | ResearchDoc or DesignDoc |
| ResearchDoc | `docs/research/{TOPIC}.md` | research agent | DesignDoc or FR |
| DebugLog | `docs/debug/YYYY-MM-DD-{issue}.md` | any agent | IncidentRetro if significant |
| ChangeProposal | `docs/changes/{name}/proposal.md` | any agent | ChangeDesign |
| WorklogEntry | `docs/worklogs/WL-{NNN}.md` | post-commit hook | Promoted automatically (audit layer) |

### Layer 2 — Formal/Spec (VitePress `/docs/` view)

| Type | File Pattern | Created By | ID System |
|------|-------------|------------|-----------|
| PRD | `PRD.md` (root) | BMAD pm agent | E{n}.{m} epics |
| FunctionalRequirements | `FUNCTIONAL_REQUIREMENTS.md` (root) | BMAD analyst | FR-{CAT}-{NNN} |
| ADR | `docs/adr/ADR-{NNN}-{slug}.md` | BMAD architect | ADR-{NNN} |
| UserJourney | `USER_JOURNEYS.md` (root) | BMAD ux agent | UJ-{N} |
| ImplementationPlan | `PLAN.md` (root) | BMAD sm | P{n}.{m} tasks |
| ContextDoc | `docs/context/{technology}.md` | any agent | — |
| ArchitectureDoc | `docs/reference/ARCHITECTURE_*.md` | architect agent | — |
| DesignDoc | `docs/plans/YYYY-MM-DD-{topic}-design.md` | brainstorming skill | — |

### Layer 3 — Delivery/Audit (VitePress `/audit/` view, append-only)

| Type | File Pattern | Created By | Trigger |
|------|-------------|------------|---------|
| SprintPlan | `docs/sprints/SPRINT-{NNN}.md` | BMAD sm | sprint-planning workflow |
| ChangeDesign | `docs/changes/{name}/design.md` | architect agent | proposal approved |
| ChangeTasks | `docs/changes/{name}/tasks.md` | sm agent | design approved |
| TestLogEntry | `docs/test-logs/YYYY-MM-DD-{run}.md` | post-test hook | test suite completes |
| Changelog | `CHANGELOG.md` (root) | git-cliff | `git tag` |
| CompletionReport | `docs/reports/YYYY-MM-DD-{feature}-complete.md` | story-done workflow | BMAD story-done |

### Layer 4 — Retrospective/Knowledge (VitePress `/kb/` view)

| Type | File Pattern | Created By | Trigger |
|------|-------------|------------|---------|
| SprintRetro | `docs/retros/SPRINT-{NNN}-retro.md` | BMAD sm | retrospective workflow |
| EpicRetro | `docs/retros/EPIC-{id}-retro.md` | BMAD sm | epic complete |
| IncidentRetro | `docs/retros/INCIDENT-{id}-retro.md` | any agent | debug log promoted |
| KnowledgeExtract | `docs/kb/{topic}/{slug}.md` | semantic indexer | nightly run |

---

## 3. Universal Frontmatter Schema

All docs (except ConversationDump) use this base frontmatter:

```yaml
---
# Required
type: idea | research | debug | proposal | worklog | prd | fr | adr | journey | plan | context | arch | design | sprint | change-design | change-tasks | test-log | changelog | completion | retro | kb
status: draft | active | staging | published | archived | deprecated
date: YYYY-MM-DD
title: "Human-readable title"

# Traceability (fill what applies)
relates_to: []          # list of doc IDs or file paths
traces_to: []           # FR-XXX-NNN, ADR-NNN, E{n}.{m} IDs
author: agent           # "agent" or harness name
session_id: ""          # thegent session ID if applicable
git_commit: ""          # SHA if commit-linked

# Layer-specific
layer: 0 | 1 | 2 | 3 | 4
tags: []
---
```

**Pydantic enforcement:** `docs_engine.schema` validates every doc on write. Pre-write hook rejects docs missing required fields.

---

---

## Source: plans/2026-02-21-doc-system-impl-plan.md

# Agent-Driven Documentation System — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a fully agentic doc system: capture → index (SQLite) → promote → surface (VitePress), covering all 26 doc types across 5 lifecycle layers with MCP tools, CLI, git hooks, and a semantic knowledge extractor.

**Architecture:** `docs_engine` Python package in `thegent/` owns schema validation (Pydantic), SQLite indexing (via watchdog), capture hooks (session/commit/test), sidebar generation, semantic extraction, and FastMCP tool registration. VitePress consumes the SQLite index via TypeScript data loaders. A workspace-level VitePress hub replaces MkDocs.

**Tech Stack:** Python (Pydantic, typer, watchdog, Jinja2, structlog, orjson), SQLite (stdlib), FastMCP, VitePress (Vue 3, TypeScript), git-cliff (Rust CLI), watchdog for fs events.

**Design doc:** `docs/plans/2026-02-21-doc-system-design.md`

---

## Phase 1 — Foundation: Schema + DB + DocWriter

### Task 1: Package scaffold + base Pydantic schema

**Files:**
- Create: `thegent/docs_engine/__init__.py`
- Create: `thegent/docs_engine/schema/__init__.py`
- Create: `thegent/docs_engine/schema/base.py`
- Create: `thegent/docs_engine/schema/registry.py`
- Test: `thegent/tests/docs_engine/test_schema_base.py`

**Step 1: Write failing tests**

```python
# thegent/tests/docs_engine/test_schema_base.py
import pytest
from docs_engine.schema.base import DocFrontmatter, DocType, DocStatus, DocLayer

def test_base_schema_requires_type():
    with pytest.raises(Exception):
        DocFrontmatter(status="draft", date="2026-02-21", title="x", layer=1)

def test_base_schema_valid():
    doc = DocFrontmatter(
        type=DocType.IDEA,
        status=DocStatus.DRAFT,
        date="2026-02-21",
        title="My idea",
        layer=DocLayer.INFORMAL,
    )
    assert doc.type == DocType.IDEA
    assert doc.layer == DocLayer.INFORMAL

def test_base_schema_rejects_invalid_status():
    with pytest.raises(Exception):
        DocFrontmatter(type=DocType.IDEA, status="NOPE", date="2026-02-21", title="x", layer=1)
```

**Step 2: Run to verify failure**

```bash
cd thegent && uv run pytest tests/docs_engine/test_schema_base.py -v
```
Expected: `ModuleNotFoundError: No module named 'docs_engine'`

**Step 3: Implement**

```python
# thegent/docs_engine/schema/base.py
from __future__ import annotations
from enum import StrEnum
from typing import Optional
from pydantic import BaseModel, Field
import datetime

class DocType(StrEnum):
    CONVERSATION_DUMP = "conversation-dump"
    SESSION_MEMORY = "session-memory"
    SCRATCH = "scratch"
    AGENT_WORKLOG = "agent-worklog"
    IDEA = "idea"
    RESEARCH = "research"
    DEBUG_LOG = "debug-log"
    CHANGE_PROPOSAL = "change-proposal"
    WORKLOG = "worklog"
    PRD = "prd"
    FR = "fr"
    ADR = "adr"
    USER_JOURNEY = "user-journey"
    IMPL_PLAN = "impl-plan"
    CONTEXT_DOC = "context-doc"
    ARCH_DOC = "arch-doc"
    DESIGN_DOC = "design-doc"
    SPRINT_PLAN = "sprint-plan"
    CHANGE_DESIGN = "change-design"
    CHANGE_TASKS = "change-tasks"
    TEST_LOG = "test-log"
    CHANGELOG = "changelog"
    COMPLETION_REPORT = "completion-report"
    SPRINT_RETRO = "sprint-retro"
    EPIC_RETRO = "epic-retro"
    INCIDENT_RETRO = "incident-retro"
    KB_EXTRACT = "kb-extract"

class DocStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    STAGING = "staging"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"

class DocLayer(int):
    RAW = 0
    INFORMAL = 1
    FORMAL = 2
    AUDIT = 3
    KB = 4

class DocFrontmatter(BaseModel):
    type: DocType
    status: DocStatus
    date: str  # YYYY-MM-DD
    title: str
    layer: int = Field(ge=0, le=4)
    relates_to: list[str] = Field(default_factory=list)

---

## Source: plans/DOCUMENTATION_EXPANSION_TODO.md

# Documentation Expansion TODO

Last updated: 2026-02-22

## Claimed Items

### DOCEXP-001 — `docs/research/SESSION_RESEARCH_COMPLETE.md`
- Status: **IN PROGRESS**
- Owner: **Codex agent (this session)**
- Next actions:
  - Build concise section skeleton for session-level synthesis.
  - Add TODO placeholders mapped to concrete source files.
  - Keep links practical/minimal for fast downstream fill-in.

### DOCEXP-002 — `docs/research/CONVERSATION_DUMP_2026-02-16_COMPLETE.md`
- Status: **IN PROGRESS**
- Owner: **Codex agent (this session)**
- Next actions:
  - Build concise section skeleton for 2026-02-16 dump completion.
  - Add TODO placeholders mapped to concrete source files.
  - Cross-link to upstream dump and related 2026-02-16 artifacts.

---

## Source: plans/PHASE_3_STALE_AGENT_CLEANUP.md

# Phase 3: Stale Agent Cleanup & L3 Support

**Status:** 🎯 READY FOR IMPLEMENTATION
**Date:** 2026-02-19
**Estimated Duration:** 1-2 hours
**Prerequisite:** Phase 1 & 2 ✅ COMPLETE

---

## Overview

Phase 3 adds critical production capabilities:
1. **Stale Agent Cleanup** - Detect, recover, and remove dead agents
2. **L3 Agent Support** - Register sub-agents under L2
3. **Advanced Queries** - Find agents by project, level, role

---

## Phase 3A: Stale Agent Cleanup (30-45 min)

### Specification

**Stale Agent Detection**
- Query registry for agents with no heartbeat update for >5 minutes
- AgentIdentity has `last_heartbeat` timestamp
- Calculate: `now - last_heartbeat > TTL` (default TTL=300s)

**Recovery Mechanism**
```python
def recover_stale_agent(agent_id: str) -> bool:
    """Attempt to recover a stale agent."""
    # 1. Check if agent still exists in metrics
    if agent_id not in self.metrics:
        # Already dead, just unregister
        return False

    metrics = self.metrics[agent_id]

    # 2. Try pause → resume (graceful recovery)
    try:
        self.pause_agent(agent_id)
        time.sleep(1)  # Brief pause
        self.resume_agent(agent_id)
        return True
    except Exception:
        return False
```

**Unregistration**
- If recovery fails, unregister from registry
- Remove from agent_id_map
- Log escalation event

### Implementation Plan

**New Methods in SwarmController:**

1. `cleanup_stale_agents()` - Main cleanup entry point
   ```python
   def cleanup_stale_agents(self) -> None:
       """Clean up stale agents from registry."""
       if not (self.agent_registry and AGENT_IDENTITY_AVAILABLE):
           return

       try:
           stale = self.agent_registry.get_stale_agents()
           for agent_id in stale:
               if not self.recover_stale_agent(agent_id):
                   # Recovery failed, unregister
                   self.agent_registry.unregister_agent(agent_id)
                   if agent_id in self.agent_id_map:
                       del self.agent_id_map[agent_id]
       except Exception as e:
           self.logger.debug(f"Phase 3a: Cleanup failed: {e}")
   ```

2. `recover_stale_agent(agent_id)` - Attempt recovery
   - Pause agent (signal SIGSTOP)
   - Wait 1 second
   - Resume agent (signal SIGCONT)
   - Update heartbeat
   - Return success

3. Update `monitor_cycle()` to call cleanup
   ```python
   # Phase 3a: Cleanup stale agents (every 10 cycles)
   if self.cycle_count % 10 == 0:  # Every ~50 seconds
       self.cleanup_stale_agents()
   self.cycle_count += 1
   ```

### Testing Plan

**Unit Tests (New)**
- Test stale agent detection
- Test recovery success
- Test unregistration
- Test with multiple stale agents

**Integration Tests**
- Kill an agent process
- Wait for stale detection
- Verify recovery attempt
- Verify unregistration if recovery fails

---

## Phase 3B: L3 Agent Support (20-30 min)

### Specification

**L3 Hierarchy**
```
L1 (Strategic Lead)
└── L2 (Named Worker)
    └── L3 (Executor)
        - Capabilities: micro_task_execution
        - Parent: L2
        - No children
```

---

## Source: plans/PHASE_4_MCP_TRANSPORT_SPECIFICATION.md

# Phase 4: MCP Transport for Real-time Sync

**Date:** 2026-02-19
**Status:** Planning
**Phases:** 4A (MCP Server Setup) + 4B (Real-time Sync) + 4C (Cross-Civilization Communication)
**Estimated Duration:** 2-3 hours
**Confidence:** 85% (new module, well-defined scope)

---

## Executive Summary

Phase 4 adds real-time synchronization to the civilization framework via MCP (Model Context Protocol). Currently, the registry is file-based with in-memory caching. Phase 4 introduces streaming heartbeats, reactive updates, and cross-civilization agent communication.

---

## Architecture Overview

### Current State (Phase 1-3)
```
┌─────────────────────────────────┐
│  SwarmController (L1 Agent)     │
├─────────────────────────────────┤
│  Agent Identity System          │
│  ├─ GlobalAgentRegistry         │
│  │  ├─ In-memory cache          │
│  │  └─ Disk persistence         │
│  └─ Heartbeat tracking (5min)   │
├─────────────────────────────────┤
│  ~/.claude/civilization/        │
│  registry.json                  │
└─────────────────────────────────┘
```

### With Phase 4 (MCP Transport)
```
┌──────────────────────────────────────────────┐
│         MCP Server (TCP/stdio)               │
│         ├─ Real-time Registry Sync           │
│         ├─ Streaming Heartbeats              │
│         └─ Agent Communication               │
└──────────────┬───────────────────────────────┘
               │
┌──────────────┴───────────────────────────────┐
│         SwarmController (L1 Agent)           │
├──────────────────────────────────────────────┤
│  Agent Identity System + MCP Client          │
│  ├─ GlobalAgentRegistry                      │
│  ├─ Streaming Heartbeat Handler              │
│  └─ Agent Message Broker                     │
├──────────────────────────────────────────────┤
│  ~/.claude/civilization/registry.json        │
└──────────────────────────────────────────────┘
```

---

## Phase 4A: MCP Server Setup

### Objectives
1. Create MCP server wrapping GlobalAgentRegistry
2. Define MCP resources and tools
3. Initialize server in swarm_controller.py
4. Maintain backward compatibility

### Implementation Details

#### 4A.1: MCP Server Class
```python
# scripts/civilization_mcp_server.py

class CivilizationMCPServer:
    """MCP server for civilization framework registry."""

    def __init__(self, registry: GlobalAgentRegistry):
        self.registry = registry
        self.server = MCPServer("civilization")

        # Register resources
        self.register_resources()

        # Register tools
        self.register_tools()

    def register_resources(self):
        """Register MCP resources for registry data."""
        # civilization://agents/{agent_id}
        # civilization://projects/{project}
        # civilization://statistics
        # civilization://hierarchy/{parent_id}

    def register_tools(self):
        """Register MCP tools for registry operations."""
        # register_agent(name, level, role, ...)
        # update_heartbeat(agent_id)
        # get_agent(agent_id)
        # query_agents(filter)
        # cleanup_stale()

    def start(self, host="localhost", port=3848):
        """Start MCP server."""
        pass
```

#### 4A.2: MCP Resources

| Resource | URI | Type | Purpose |
|----------|-----|------|---------|
| Agent | `civilization://agents/{agent_id}` | Read-only | Get agent metadata |
| Project | `civilization://projects/{project}` | Read-only | List agents in project |
| Statistics | `civilization://statistics` | Read-only | Registry stats (count, projects, levels) |
| Hierarchy | `civilization://hierarchy/{parent_id}` | Read-only | Get children of agent |
| Active | `civilization://active` | Read-only | List active agents |
| Stale | `civilization://stale` | Read-only | List stale agents (>5min) |

#### 4A.3: MCP Tools

| Tool | Input | Output | Purpose |
|------|-------|--------|---------|
| `update_heartbeat` | `{agent_id}` | `{success, timestamp}` | Update agent heartbeat |

---

## Source: plans/PHASE_5_ADVANCED_FEATURES_SPECIFICATION.md

# Phase 5: Advanced Features - Specification & Planning

**Date:** 2026-02-19
**Status:** Planning
**Phases:** 5A (Conflict Resolution) + 5B (Agent Memory) + 5C (Dashboards)
**Estimated Duration:** 2.5-3 hours
**Confidence:** 80% (new domains, well-defined scope)

---

## Executive Summary

Phase 5 adds three advanced capabilities to the civilization framework:

1. **5A: Conflict Resolution Protocol** - Handle agent disagreements, dual registrations, state conflicts
2. **5B: Agent Memory Persistence** - Store and retrieve agent execution history, decisions, learnings
3. **5C: Civilization-wide Dashboards** - Real-time monitoring and status visualization

---

## Phase 5A: Conflict Resolution Protocol

### Objectives
1. Detect registration conflicts (same agent, multiple entries)
2. Implement conflict resolution strategies (last-write-wins, voting, merge)
3. Handle state divergence (heartbeat inconsistencies)
4. Log conflict history for audit trail

### Problem Space
**Scenarios:**
- Agent registered twice under different IDs
- Registry inconsistency (in-memory vs disk)
- Duplicate L2 agents for same work
- Stale parent references
- Circular relationships

### Resolution Strategies

#### 1. Last-Write-Wins (LWW)
```python
def resolve_duplicate_agents(agent_id1, agent_id2):
    """Keep newer registration, discard older."""
    a1 = registry.get_agent(agent_id1)
    a2 = registry.get_agent(agent_id2)

    if a1.last_heartbeat > a2.last_heartbeat:
        registry.unregister_agent(agent_id2)
        return agent_id1
    else:
        registry.unregister_agent(agent_id1)
        return agent_id2
```

#### 2. Voting-Based
```python
def resolve_with_voting(conflicting_agents):
    """Ask other agents which registration is correct."""
    votes = {}
    for agent_id in conflicting_agents:
        # Send conflict resolution message to peers
        # Collect votes
        pass
    # Winner is agent with most votes
```

#### 3. Merge Strategy
```python
def merge_agents(agent_id1, agent_id2):
    """Combine child_agent_ids, capabilities, scope_tags."""
    a1 = registry.get_agent(agent_id1)
    a2 = registry.get_agent(agent_id2)

    merged = AgentIdentity(
        agent_id=agent_id1,  # Keep first
        child_agent_ids=list(set(a1.child_agent_ids + a2.child_agent_ids)),
        capabilities=list(set(a1.capabilities + a2.capabilities)),
        scope_tags={**a1.scope_tags, **a2.scope_tags}
    )
    return merged
```

### Implementation Plan

**5A.1: Conflict Detection (30 min)**
- Duplicate agent ID detection (same project:uuid:L:role)
- Parent reference validation
- Circular relationship detection
- State consistency checks

**5A.2: Conflict Log (20 min)**
- Store conflicts in `~/.claude/civilization/conflicts.json`
- Log conflict time, type, resolution, outcome
- Support queries by agent, time, type

**5A.3: Resolution Engine (40 min)**
- Implement LWW strategy
- Implement voting protocol
- Implement merge strategy
- Auto-select strategy based on conflict type

**5A.4: Testing & Integration (30 min)**
- Unit tests for each strategy
- Integration tests with Phase 1-4
- Regression tests

---

## Phase 5B: Agent Memory Persistence

### Objectives
1. Store agent execution history (tasks completed, decisions made)
2. Persist agent learnings (patterns, optimizations)
3. Support memory queries (what has agent done?)
4. Enable agent self-improvement (learn from history)

### Memory Model

#### AgentMemory Structure
```python
@dataclass

---

## Source: plans/PHASE_6_MEMORY_ENHANCEMENTS_SPECIFICATION.md

# Phase 6: Advanced Memory Enhancements Specification

**Status:** Planning Phase (Awaiting Prioritization)
**Date:** 2026-02-19
**Scope:** Memory backend upgrades, search, analytics, and sharing
**Estimated Effort:** 3-4 hours
**Confidence:** 75%

---

## Overview

Phase 6 enhances the Phase 5B Memory system with:
1. **SQLite Backend**: Replace JSONL with SQL for better query performance
2. **Full-Text Search**: Index and search memory content
3. **Memory Relationships**: Link related memories across agents
4. **Analytics**: Trend analysis and pattern detection
5. **Sharing**: Inter-agent memory sharing and learning

---

## Phase 5 Recap

### Delivered (Phase 5A-C)
- **Phase 5A**: Conflict Resolution (304 LOC, 14 tests)
- **Phase 5B**: Agent Memory - JSONL storage (446 LOC, 20 tests)
- **Phase 5C**: Civilization Dashboards (396 LOC, 22 tests)
- **Total**: 1,146 LOC, 56 tests, 100% passing

### Current Memory System (Phase 5B)
```
Storage:     ~/.claude/civilization/agents/{agent_id}/memory.jsonl
Format:      Line-delimited JSON, one memory per line
Operations:  store, query, stats, purge, clear
Query Types: by type, by time range, by importance
Limitation:  Linear scan for every query (O(n))
```

### Known Limitations
- No index: Every query scans all memories (slow for large datasets)
- No relationships: Memories are isolated per agent
- No search: Can't find memories by content keywords
- No analytics: Can't detect patterns or trends
- No sharing: Agents can't learn from each other's memories
- Unbounded growth: Old memories need manual purge

---

## Phase 6 Architecture

### 6.1: SQLite Backend Migration

**Goal**: Upgrade from JSONL to SQL database for better performance

```
Current (JSONL):
├─ ~/.claude/civilization/agents/{agent_id}/memory.jsonl
└─ Memory file (line-delimited JSON)

Phase 6 (SQLite):
├─ ~/.claude/civilization/memories.db (single file)
├─ Tables:
│  ├─ memories (id, agent_id, type, timestamp, content, importance)
│  ├─ memory_relationships (memory_id, related_memory_id, strength)
│  └─ memory_index (content_hash, keyword, memory_id)
└─ Indexes:
   ├─ agent_id + timestamp
   ├─ agent_id + type
   ├─ timestamp DESC
   └─ importance DESC
```

**Benefits:**
- Indexed queries (O(log n) vs O(n))
- Atomic transactions
- Relationship tracking
- Single file (easier backup)
- Atomic purges

**Compatibility:** Provide migration tool (JSONL → SQLite)

### 6.2: Full-Text Search

**Goal**: Index and search memory content

```python
MemoryService.search_memories(agent_id, query: str) -> List[AgentMemory]
# Example: search_memories("project-a", "database optimization")

# Under the hood:
# 1. Parse query → keywords
# 2. Search memory_index table
# 3. Rank by TF-IDF
# 4. Return top 10 results
```

**Schema:**
```sql
CREATE TABLE memory_index (
    id INTEGER PRIMARY KEY,
    memory_id TEXT,
    keyword TEXT,
    frequency INTEGER,
    FOREIGN KEY(memory_id) REFERENCES memories(id)
);

CREATE INDEX idx_keyword ON memory_index(keyword);
```

**Performance:**
- Initial indexing: <100ms (per memory)
- Search: <10ms (100 keywords)
- Index size: ~20 bytes per keyword

### 6.3: Memory Relationships

**Goal**: Link related memories within and across agents

```python
# Within agent: "I learned X, which helps with Y"

---

