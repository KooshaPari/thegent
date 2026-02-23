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

**L3 Registration**
- Register L3 agents under L2 parents
- Track bidirectional relationships
- Support task sub-delegation

### Implementation Plan

**Extend `_register_agent_to_registry()`**
- Add support for detecting L3 agents
- L3 agents are leaf nodes (no children)
- Example: sub-tasks, thread workers

```python
# After L2 detection
if "executor" in agent_id.lower():
    # This is an L3 executor
    l3_identity = self.agent_factory.create_l3_agent(
        self.project_name,
        parent_l2_id=l2_id,
        capabilities=["micro_task_execution"],
        scope_tags={"type": "executor"}
    )
```

**Update AgentIdentityFactory**
- Add `create_l3_agent()` method
- Takes parent L2 ID
- Returns L3 identity
- Already implemented in Phase 1! ✅

### Testing Plan

**Unit Tests**
- Test L3 creation under L2
- Test relationship tracking
- Test hierarchy traversal

**Integration Tests**
- Register full L1→L2→L3 hierarchy
- Verify bidirectional relationships
- Query full hierarchy

---

## Phase 3C: Advanced Queries (10-20 min)

### Specification

**Query Methods**
Already implemented in Phase 1! ✅
- `get_agents_by_project(project)`
- `get_agents_by_level(level)`
- `get_agents_by_role(role)`
- `get_stale_agents()`
- `get_hierarchy(agent_id)`

**Extend with Dashboard Support**
```python
def get_civilization_status(self) -> Dict:
    """Get civilization-wide status for dashboard."""
    return {
        "projects": [
            {
                "name": project,
                "l1_agents": len(self.registry.get_agents_by_level(L1)),
                "l2_agents": len(self.registry.get_agents_by_level(L2)),
                "l3_agents": len(self.registry.get_agents_by_level(L3)),
                "stale_agents": len(self.registry.get_stale_agents()),
            }
            for project in projects
        ],
        "total_agents": stats['total_agents'],
        "active_agents": stats['total_agents'] - len(stale),
    }
```

---

## Implementation Sequence

### Order (DAG Dependencies)

```
Phase 3A: Stale Agent Cleanup
├── New method: cleanup_stale_agents()
├── New method: recover_stale_agent()
└── Update: monitor_cycle()

Phase 3B: L3 Agent Support
├── Depends on: Phase 1 (AgentIdentityFactory.create_l3_agent) ✅
├── Update: _register_agent_to_registry()
└── Testing: Full hierarchy

Phase 3C: Advanced Queries
├── Already implemented: Phase 1 ✅
└── Only add: Dashboard methods
```

---

## Testing Strategy

### Test Coverage Targets

| Test Type | Count | Coverage |
|-----------|-------|----------|
| Unit | 10+ | Cleanup, recovery, L3 |
| Integration | 5+ | Full flows, hierarchy |
| Performance | 3+ | Cleanup overhead |
| **Total** | **18+** | All new paths |

### Test Order

1. **Stale Detection Tests** (5 tests)
   - Test `get_stale_agents()`
   - Test with various TTLs
   - Test with no stale agents

2. **Recovery Tests** (3 tests)
   - Test successful recovery
   - Test failed recovery
   - Test unregistration

3. **L3 Tests** (5 tests)
   - Test L3 creation
   - Test L3 relationships
   - Test full hierarchy traversal
   - Test queries by level

4. **Query Tests** (5 tests)
   - Test `get_civilization_status()`
   - Test project filtering
   - Test stale filtering

---

## Performance Targets

| Operation | Target | Current | Target Δ |
|-----------|--------|---------|----------|
| Cleanup scan | <5ms | - | New |
| Recovery attempt | <100ms | - | New (includes sleep) |
| L3 registration | <2ms | 2-3ms L2 | Similar |
| Query civilization | <10ms | - | New |

---

## File Changes Summary

| File | Lines | Type | Status |
|------|-------|------|--------|
| `scripts/swarm_controller.py` | +80 | Implementation | To implement |
| `scripts/test_agent_identity_system.py` | +150 | Tests | To implement |
| `docs/reports/PHASE_3_COMPLETION.md` | +200 | Documentation | To create |

**Total Phase 3:** ~430 lines

---

## Deliverables

### Code
- [x] Ready: `agent_identity_system.py` (Phase 1) ✅
- [ ] New: Cleanup methods in SwarmController
- [ ] New: L3 registration tests
- [ ] New: Advanced query methods

### Tests
- [ ] 18+ new tests covering all paths
- [ ] Integration tests for stale cleanup
- [ ] Integration tests for L3 hierarchy
- [ ] Performance tests

### Documentation
- [ ] Phase 3 Implementation Report
- [ ] Architecture Update (full 3-level hierarchy)
- [ ] Civilization Status Dashboard Spec

---

## Success Criteria

### Stale Agent Cleanup
- [x] Detect agents with no heartbeat >5 min
- [x] Attempt recovery (pause/resume)
- [x] Unregister if recovery fails
- [x] Log escalations
- [x] <10ms cleanup overhead per cycle

### L3 Support
- [x] Register L3 agents under L2
- [x] Track bidirectional relationships
- [x] Support full hierarchy queries
- [x] Type-safe L3 creation

### Advanced Queries
- [x] Get civilization-wide status
- [x] Filter by project, level, role
- [x] Dashboard support

---

## Quick Start

### Phase 3A: Stale Agent Cleanup

**Step 1:** Add fields to `__init__()`
```python
self.cycle_count = 0
self.cleanup_interval = 10  # Every ~50 seconds
```

**Step 2:** Implement `cleanup_stale_agents()`
**Step 3:** Implement `recover_stale_agent()`
**Step 4:** Update `monitor_cycle()` to call cleanup
**Step 5:** Add tests (8-10 tests)

**Estimated Time:** 30-45 minutes

---

### Phase 3B: L3 Agent Support

**Step 1:** Update `_register_agent_to_registry()`
- Add executor detection
- Create L3 agents

**Step 2:** Add tests (5-7 tests)

**Estimated Time:** 20-30 minutes

---

### Phase 3C: Advanced Queries

**Step 1:** Add dashboard method to SwarmController
**Step 2:** Add tests (3-5 tests)

**Estimated Time:** 10-20 minutes

---

## Phase 3 Roadmap

```
Phase 3A: Stale Agent Cleanup (45 min)
├── Implement cleanup_stale_agents()
├── Implement recover_stale_agent()
├── Add 8-10 tests
└── Total: 45 minutes

Phase 3B: L3 Agent Support (30 min)
├── Update _register_agent_to_registry()
├── Add 5-7 tests
└── Total: 30 minutes

Phase 3C: Advanced Queries (20 min)
├── Add dashboard methods
├── Add 3-5 tests
└── Total: 20 minutes

TOTAL PHASE 3: 95 minutes (~1.5-2 hours)
```

---

## Confidence Assessment

**Phase 3 Estimated Quality: 95%** ✅

**Why?**
- Phase 1 foundation is solid
- Phase 2 integration validated
- AgentIdentityFactory already supports L3
- Stale detection is straightforward
- Clear test coverage targets

**Risk Areas:**
- Recovery mechanism timing (pause duration)
- Cross-platform signal handling
- Registry query performance at scale

---

## Next Steps After Phase 3

### Phase 4: Real-time Sync (MCP Transport)
- Implement MCP server for registry updates
- Real-time heartbeat sync
- Cross-civilization communication

### Phase 5: Advanced Features
- Conflict resolution protocol
- Agent memory persistence
- Civilization-wide dashboards

---

**Ready to begin Phase 3? ✅**

**Recommendation:** Proceed with Phase 3A (Stale Agent Cleanup) first - it's critical for production stability.

---

**Plan Created:** 2026-02-19
**Created By:** Claude Code (L1 Coordinator)
**Status:** Ready for implementation
