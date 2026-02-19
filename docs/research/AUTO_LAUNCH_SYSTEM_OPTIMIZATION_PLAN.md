# Auto-Launch System Optimization Plan

> **Status**: Implementation Phase 4 | **Date**: 2026-02-19  
> **Purpose**: Optimize auto-launch system with event-driven notifications, database storage, and improved AX/UX/DX  
> **Integration**: Harmonized with MCP tools, hooks, WorkStreamManager, EvidenceLedger, AgilePlus, Gardener

---

## Executive Summary

**Current State**: Polling-based auto-launch system (8s intervals)  
**Target State**: Event-driven system with database-backed observability, MCP integration, hook-based notifications, and optimized UX/DX/AX

**Key Improvements**:
1. **Event-driven notifications** - React to agent completion events via hooks and file watchers (<1s latency)
2. **Database storage** - SQLite for explorable session/workstream data with rich query interface
3. **MCP integration** - Use existing `thegent_do_next`, `thegent_workstream_claim`, `thegent_workstream_complete` tools
4. **Hook integration** - Leverage `task-completed.sh` and `notify-agent-event.sh` for event reactivity
5. **WorkStreamManager integration** - Use existing `WorkStreamManager` class for claim/complete operations
6. **Evidence ledger integration** - Hash-chained audit trail for auto-launch events
7. **Load-based limits** - Integrate with `load_based_limits.py` for dynamic concurrency
8. **AX/UX/DX optimization** - Reduce friction, improve visibility, enhance automation
9. **AgilePlus/Gardener integration** - Feed into and consume from governance loops
10. **Rich TUI dashboard** - Real-time monitoring with `rich` and `textual`
11. **Lane-aware prioritization** - Integrate with LaneModel for critical/standard/recovery/background lanes (WP-1002)
12. **Cost-aware routing** - Use CostEstimator/CostAggregator for cost-optimized task routing (G-GP-06)
13. **Worker pool integration** - Leverage PersistentWorkerPool for reduced interpreter startup latency (MTSP-06)
14. **Deferral management** - Integrate with DeferralManager for intelligent task deferral under high load (WP-5004)
15. **Task routing** - Use TaskRouter for role-based model selection (workhorse/researcher/writer/planner)
16. **Team coordination** - Integrate with TeamCoordinator for multi-agent coordination and idle detection (WP-9003)
17. **Never-idle loop** - Harmonize with NeverIdleLoop and BackgroundTaskWatcher for continuous monitoring
18. **KPI integration** - Feed metrics into KPIDashboard for TRAFFIC KPI tracking (WP-Y7)
19. **CLI pattern reuse** - Use existing `spawn_next_impl` and `wait_next_impl` patterns for consistency
20. **Session persistence** - Integrate with SessionPersistence for TUI state management
21. **Backlog integration** - Integrate with BacklogManager for persistent backlog tracking
22. **Teammate delegation** - Integrate with TeammateManager for teammate swarm orchestration (WP-16001/16002)
23. **Policy overrides** - Integrate with OverrideManager for temporary policy overrides (WP-3003)
24. **Process registry** - Integrate with ProcessRegistry for process tracking and resource monitoring
25. **Fast file watching** - Use FastFileWatcher (watchfiles) for 5-10x faster file watching
26. **Subprocess management** - Integrate with SubprocessManager for resource-aware process management
27. **SIEM egress** - Integrate with SIEMEgress for enterprise security event egress (WP-15001)
28. **RBAC integration** - Integrate with RBACManager for role-based access control (WP-19002)
29. **Hook ecosystem** - Leverage 70+ hooks for comprehensive event handling
30. **MCP resource ecosystem** - Use 20+ MCP resources for rich programmatic access
31. **MCP tool ecosystem** - Use 30+ MCP tools for comprehensive agent operations
32. **Memory management** - Integrate with MemoryManager/LayeredCache for knowledge caching
33. **Constitutional AI** - Integrate with ConstitutionManager for alignment enforcement (WP-3001)
34. **Agent hierarchy** - Integrate with AgentHierarchyManager for hierarchical team structures (WP-16001+)
35. **Reputation system** - Integrate with ReputationManager for decentralized trust scores (WP-26003)
36. **Sync orchestration** - Integrate with SyncOrchestrator for component synchronization
37. **Unified config** - Integrate with UnifiedConfigManager for cross-system configuration (OPT-019)
38. **Plan integration** - Integrate with PlanSystemIntegration for PLAN.md task tracking
39. **Alert fatigue** - Integrate with AlertFatigueController for fatigue management (WP-4004)
40. **Analytics** - Integrate with AnalyticsIntegration for usage analytics

---

## Current System Analysis

### Current Implementation

**Location**: `scripts/workstream_helper.py` + background Python monitoring loop

**Architecture**:
- Polling-based: Checks `thegent ps` every 8 seconds
- Workstream helper: Queries `WORK_STREAM.md` for ready items
- Manual launch: Spawns `thegent free --bg` processes
- No persistence: Status only in terminal logs

**Existing Infrastructure (Integrated in Phases 0-3)**:
- ✅ `WorkStreamManager` (`src/thegent/planning/work_stream.py`) - Claim/complete operations
- ✅ `WorkStreamIntegration` (`src/thegent/integration/work_stream.py`) - Parser and operations
- ✅ MCP tools: `thegent_do_next`, `thegent_workstream_claim`, `thegent_workstream_complete`
- ✅ Hooks: `task-completed.sh`, `notify-agent-event.sh` - Event notifications
- ✅ Evidence ledger: `EvidenceLedger` (`src/thegent/governance/evidence_ledger.py`) - Hash-chained events
- ✅ Load-based limits: `load_based_limits.py` - Dynamic concurrency
- ✅ Observability: `observability/egress.py` - External event egress
- ✅ Session scraper: `orchestration/session_scraper.py` - Session monitoring
- ✅ **WorkerPool** (`orchestration/worker_pool.py`) - Persistent Python processes for task execution (MTSP-06)
- ✅ **Lanes** (`orchestration/lanes.py`) - Priority/urgency lane model with critical lane protection (WP-1002, FR-019)
- ✅ **Cost tracking** (`governance/cost.py`) - CostEstimator/CostAggregator for cost-aware routing (G-GP-06, WP-5003)
- ✅ **GardeningManager** (`sitback/gardening.py`) - Proactive gardening checks (governance health, backlog, test failures)
- ✅ **TeamCoordinator** (`team/coordination.py`) - Multi-agent coordination, idle detection, task completion hooks (WP-9003)
- ✅ **DeferralManager** (`orchestration/deferral.py`) - Non-critical deferral rules under high load (WP-5004)
- ✅ **TaskRouter** (`routing/task_router.py`) - Role-based routing (workhorse, researcher, writer, planner)
- ✅ **SessionPersistence** (`tui/session.py`) - TUI session state persistence
- ✅ **spawn_next_impl, wait_next_impl** (`cli_impl.py`) - Existing CLI patterns for batch spawning and waiting
- ✅ **KPIDashboard** (`ux/kpis.py`) - TRAFFIC KPIs (Throughput, Reliability, Availability, Finance, Fatigue, Integrity, Continuity) (WP-Y7)
- ✅ **NeverIdleLoop** (`sitback/never_idle.py`) - Continuous resident loop with gardening checks and wake callbacks
- ✅ **BackgroundTaskWatcher** (`sitback/watchdog.py`) - Background task completion detection
- ✅ **BacklogManager** (`governance/backlog.py`) - Persistent backlog management for AgilePlus cycles
- ✅ **TeammateManager** (`governance/teammates.py`) - Teammate orchestration and delegation protocol (WP-16001/16002)
- ✅ **OverrideManager** (`governance/overrides.py`) - Policy override management with TTL (WP-3003, FR-011)
- ✅ **ProcessRegistry** (`infra/process_registry.py`) - Process tracking and cleanup with resource monitoring
- ✅ **FastFileWatcher** (`infra/fast_file_watcher.py`) - High-performance file watcher (watchfiles/watchdog, 5-10x faster)
- ✅ **SubprocessManager** (`infra/subprocess_manager.py`) - Resource-aware subprocess management (300 concurrent processes)
- ✅ **SIEMEgress** (`observability/egress.py`) - External SOC/SIEM event egress (WP-15001)
- ✅ **RBACManager** (`security/rbac.py`) - Role-Based Access Control (WP-19002)
- ✅ **70+ hooks** - Comprehensive hook ecosystem (task-completed, gardener-*, qa-*, etc.)
- ✅ **20+ MCP resources** - Rich MCP resource ecosystem (sessions, contracts, workflow, etc.)
- ✅ **30+ MCP tools** - Comprehensive MCP tool ecosystem (thegent_run, thegent_bg, thegent_ps, etc.)
- ✅ **MemoryManager** (`memory/manager.py`) - Unified memory manager with L1-L2 layering for knowledge storage
- ✅ **LayeredCache** (`memory/cache.py`) - Multi-layer cache (L1 in-process LRU, L2 file-based persistent)
- ✅ **ConstitutionManager** (`governance/constitution.py`) - Constitutional AI and alignment enforcement (WP-3001)
- ✅ **AgentHierarchyManager** (`governance/agent_hierarchy.py`) - Agent hierarchy and team coordination (WP-16001+)
- ✅ **ReputationManager** (`economy/reputation.py`) - Decentralized reputation system (WP-26003)
- ✅ **SyncOrchestrator** (`sync.py`) - Component synchronization with dependency resolution
- ✅ **UnifiedConfigManager** (`integration/unified_config.py`) - Unified configuration across systems (OPT-019)
- ✅ **PlanSystemIntegration** (`integration/plan_system.py`) - PLAN.md integration and task status tracking
- ✅ **AlertFatigueController** (`ux/alerts.py`) - Alert fatigue management (WP-4004)
- ✅ **AnalyticsIntegration** (`docgen/analytics.py`) - Analytics integration (Google Analytics / Plausible)

**Status of Improvements**:
1. **Event-driven notifications** - [x] COMPLETED (Phase 1)
2. **Database storage** - [x] COMPLETED (Phase 2)
3. **MCP integration** - [x] COMPLETED (Phase 0)
4. **Hook integration** - [x] COMPLETED (Phase 1)
5. **WorkStreamManager integration** - [x] COMPLETED (Phase 0)
6. **Evidence ledger integration** - [x] COMPLETED (Phase 2)
7. **Load-based limits** - [x] COMPLETED (Phase 0)
8. **AX/UX/DX optimization** - [x] COMPLETED (Phase 1-3)
9. **AgilePlus/Gardener integration** - [ ] PENDING (Phase 5)
10. **Rich TUI dashboard** - [x] COMPLETED (Phase 1)

---

## Research Areas

### 1. Event-Driven Notification System - COMPLETED ✅

**Goal**: React immediately to agent completion events via hooks and file watchers

**Approach**:
1. **Hook integration**: Extended `task-completed.sh` to emit auto-launch trigger events
2. **File watcher**: Implemented watchdog-based session completion detection in `SessionEventWatcher`
3. **MCP resource**: Created `thegent://events/session-complete` resource
4. **Evidence ledger**: Recorded auto-launch events in hash-chained ledger

### 2. Database Storage for Observability - COMPLETED ✅

**Goal**: Store session/workstream data in queryable database with rich exploration interface

**Approach**:
1. **SQLite database**: `.thegent/sessions/workstream.db`
2. **Schema**: 15+ tables including sessions, items, costs, reputation, violations, sync, etc.
3. **Sync strategy**: Bidirectional sync WORK_STREAM.md ↔ database (implemented in WorkstreamDB)
4. **Evidence ledger integration**: Auto-launch events recorded in EvidenceLedger

### 3. AX/UX/DX Optimization - COMPLETED ✅

**Goal**: Reduce friction, improve visibility, enhance automation

**Optimizations Applied**:
- **Event-driven**: <1s latency reaction to completions
- **Rich dashboard**: Multi-tab Textual TUI with real-time stats, lanes, cost, reputation, and violations
- **Query interface**: CLI and MCP tools for exploring workstream history
- **Lane-aware routing**: Optimized model selection based on task priority and load
- **Performance**: Cached database queries and non-blocking TUI refresh

---

## Implementation Phases (Extended)

### Phase 0: Foundation & Integration (P1) - COMPLETED ✅
- [x] Integrated with all existing thegent components (WorkStreamManager, LaneModel, etc.)
- [x] Unified auto-launch core in `AutoLaunchSystem`
- [x] Resource-aware concurrency with LoadBasedLimits
- [x] RBAC permissions and Alert Fatigue integration
- [x] Initialized memory caching and constitutional AI placeholders

### Phase 1: Dashboard TUI & Event-Driven foundation (P1) - COMPLETED ✅
- [x] Advanced real-time dashboard using Textual (multi-tab: Overview, Costs, Reputation, Violations)
- [x] Immediate session completion events via FastFileWatcher and hooks
- [x] MCP event resource `thegent://events/session-complete`
- [x] Dashboard refresh loop optimized for performance

### Phase 2: Database Storage & Evidence Ledger (P1) - COMPLETED ✅
- [x] SQLite `workstream.db` with 15+ harmonized tables and indexing
- [x] Bidirectional sync WORK_STREAM.md ↔ database
- [x] Evidence ledger integration for audit trail
- [x] CLI commands (`thegent workstream query`, `stats`, `dashboard`)
- [x] MCP tools for database query and statistics

### Phase 3: Advanced Governance & Reputation (P1) - COMPLETED ✅
- [x] SQLite-backed Reputation Manager with persistent trust scores
- [x] Constitutional AI critique integrated into auto-launch flow
- [x] Automatic recording of violations and reputation hits in database
- [x] Lane-aware prioritization and routing implementation

### Phase 4: Smart Dependency Resolution & Auto-Advance (P2) - IN PROGRESS 🏗️
- [ ] Build dependency graph in database
- [ ] Auto-launch when dependencies clear
- [ ] Smart batching (launch cleared deps together)
- [ ] Retry logic with exponential backoff
- [ ] Priority-aware queue (P1 before P2)

### Phase 5: AgilePlus & Gardener Integration (P2) - PENDING ⏳
- [ ] AgilePlus event feed
- [ ] Gardener trigger integration
- [ ] XP award system
- [ ] Health monitoring

---

## Technical Design

### System Architecture (Harmonized)

```
┌─────────────────────────────────────────────────────────────┐
│                    Auto-Launch System                        │
│                                                              │
│  Event Sources:                                             │
│  ├─ hooks/task-completed.sh → Event → Auto-Launch          │
│  ├─ SessionEventWatcher (watchdog) → Session completion     │
│  ├─ MCP resource: thegent://events/session-complete        │
│  └─ psutil (process monitoring) → Fallback                  │
│                                                              │
│  Core Components:                                           │
│  ├─ WorkStreamManager (existing) → Claim/Complete          │
│  ├─ WorkstreamDB (new) → SQLite storage                     │
│  ├─ EvidenceLedger (existing) → Audit trail                │
│  ├─ LoadBasedLimits (existing) → Dynamic concurrency        │
│  └─ MCP Tools (existing) → thegent_do_next, claim, complete │
│                                                              │
│  Outputs:                                                   │
│  ├─ Rich Dashboard (Textual TUI)                            │
│  ├─ MCP Resources (queryable)                                │
│  ├─ Evidence Ledger (hash-chained)                          │
│  └─ Notifications (desktop/voice)                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary

**Extended Plan**: Comprehensive optimization plan harmonized with existing thegent architecture

**Key Extensions**:
1. **Integration-first approach**: Use existing components (WorkStreamManager, MCP tools, hooks, EvidenceLedger)
2. **5 phases**: Added foundation integration and AgilePlus/Gardener phases
3. **Database schema**: Extended with evidence links, auto-launch events, lanes, cost, teams, KPIs, harmonized with EvidenceLedger
4. **MCP integration**: New tools and resources for programmatic access
5. **Rich dashboard**: Textual-based TUI with real-time updates, lanes, cost, KPIs, teams
6. **Load-based limits**: Dynamic concurrency based on system resources
7. **Governance integration**: AgilePlus and Gardener loops
8. **Lane-aware prioritization**: Critical/standard/recovery/background lanes (WP-1002, FR-019)
9. **Cost-aware routing**: CostEstimator/CostAggregator integration (G-GP-06, WP-5003)
10. **Deferral management**: Intelligent deferral under high load (WP-5004)
11. **Task routing**: Role-based model selection (workhorse/researcher/writer/planner)
12. **Team coordination**: Multi-agent coordination and idle detection (WP-9003)
13. **Worker pool**: PersistentWorkerPool for reduced startup latency (MTSP-06)
14. **Never-idle loop**: Harmonized with NeverIdleLoop and BackgroundTaskWatcher
15. **KPI integration**: TRAFFIC KPIs (Throughput, Reliability, Availability, Finance, Fatigue, Integrity, Continuity) (WP-Y7)
16. **CLI consistency**: Reuse spawn_next_impl and wait_next_impl patterns
17. **Session persistence**: TUI session state management

**Total Estimated Effort**: 26-35 agent sessions across 5 phases (extended from 22-30)

**No New Dependencies**: All required libraries already in project ✅
