# Work Breakdown Structure: Claude Code Hooks System Optimization

**Version:** 1.0
**Date:** 2026-02-15
**Timeline:** 4 phases over 4 weeks

---

## Phase 1: Emergency Timeout Fixes (Week 1) - ACTIVE

**Objective:** Eliminate active timeout failures (180s idle, 600s absolute)
**Status:** IN PROGRESS
**Risk:** HIGH (blocking all hook execution under stress)

### P1.1 Git Command Hardening
**Owner:** Platform Infrastructure
**Effort:** 3-4 hours
**Dependencies:** None

- **P1.1.1** Audit all git calls in hooks/lib/common.sh [DONE]
  - Added `timeout 5` to hook_should_run()
  - Verified test-maturity.sh now completes <2s
  - Verified task-completion-verifier.sh now completes <2s

- **P1.1.2** Add timeouts to remaining git commands [IN PROGRESS]
  - `git ls-files` (used in 3+ hooks) → 5s timeout
  - `git status` (used in 2+ hooks) → 10s timeout
  - `git diff` (used in 4+ hooks) → 5s timeout
  - `git show` (used in archive-changes hook) → 5s timeout
  - Test each timeout with slow repo simulation

- **P1.1.3** Test git timeouts with pathological repos
  - Create test repo with 100K files
  - Simulate slow FS (sleep injections)
  - Verify timeout boundaries (not too aggressive)

**Success Criteria:**
- All git commands wrapped with appropriate timeouts
- No timeout failures in normal operation
- Performance regression <50ms

### P1.2 Output Streaming
**Owner:** Platform Infrastructure
**Effort:** 2-3 hours
**Dependencies:** None

- **P1.2.1** Add immediate output to all Stop hooks [IN PROGRESS]
  - test-maturity.sh → `echo "TEST-MATURITY: starting..." >&2` [DONE]
  - task-completion-verifier.sh → immediate output [DONE]
  - quality-gate.sh → add output on entry
  - spec-preflight.sh → add output on entry
  - spec-verifier.sh → add output on entry
  - complexity-ratchet.sh → add output on entry
  - security-pipeline.sh → add output on entry
  - change-doc-tracker.sh → add output on entry
  - post-edit-checker.sh → add output on entry

- **P1.2.2** Verify <100ms first output on all hooks
  - Measure output latency for each hook
  - Fix any hook that exceeds 100ms to first output
  - Document baselines in hooks/PERFORMANCE.md

**Success Criteria:**
- All hooks output within first 100ms
- No 180s idle timeout failures in 1,000 test runs
- Dispatcher receives output continuously

### P1.3 Absolute Timeout Safeguards (600s)
**Owner:** Platform Infrastructure
**Effort:** 2-3 hours
**Dependencies:** P1.1, P1.2

- **P1.3.1** Identify hooks at risk of 600s timeout
  - Analyze hook execution traces (from prior research)
  - Flag any operation >120s
  - Categorize: git, linting, compilation, other

- **P1.3.2** Add checkpoints to long operations
  - Break operations into <120s chunks
  - Add output between chunks (prevent idle timeout)
  - Graceful degradation for timeout scenarios

- **P1.3.3** Test absolute timeout prevention
  - Inject delays to simulate slow operations
  - Verify checkpoints work correctly
  - Test graceful degradation

**Success Criteria:**
- All hooks complete <600s
- No operation exceeds 120s without checkpoint
- Clear error messages on timeout

### P1.4 Validation & Rollout
**Owner:** Platform Infrastructure
**Effort:** 2-3 hours
**Dependencies:** P1.1, P1.2, P1.3

- **P1.4.1** Write test cases for timeout scenarios
  - Unit test: hook_should_run() with timeout
  - Integration test: Stop hooks with git hanging
  - Chaos test: 50 concurrent agents with git delays

- **P1.4.2** Run comprehensive validation
  - All existing tests pass
  - Timeout scenario tests pass
  - Performance regression tests pass (<50ms overhead)

- **P1.4.3** Deploy to production
  - Document changes in CHANGELOG.md
  - Update hooks/README.md with timeout strategy
  - Monitor for any timeout failures

**Success Criteria:**
- All tests pass
- Zero timeout failures in first week of production
- Performance regression <50ms

**Phase 1 Completion:** All timeout failures eliminated, zero 180s idle timeouts

---

## Phase 2: Race Condition Elimination (Week 2)

**Objective:** Fix concurrent execution issues through atomic operations
**Status:** PLANNED
**Risk:** MEDIUM (only impacts concurrent agent scenarios, rare in production)

### P2.1 Atomic File Operations
**Owner:** Platform Infrastructure
**Effort:** 5-6 hours
**Dependencies:** P1.4 (Phase 1 complete)

- **P2.1.1** Analyze qa-state.json access patterns
  - Find all writes to qa-state.json
  - Identify race conditions (append without flock)
  - Document call chains: which hooks write, when, how

- **P2.1.2** Implement atomic write wrapper
  - Create hooks/lib/atomic-write.sh
  - Implement flock-based atomic writes
  - Support atomic append for session-changes.log
  - Fallback to mkdir-based locking (for systems without flock)

- **P2.1.3** Replace all writes with atomic operations
  - qa-state.json → use atomic-write.sh
  - session-changes.log → use atomic append
  - .claude/tmp/* → use atomic operations
  - Verify no direct writes remain

- **P2.1.4** Test atomic operations
  - Unit test: atomic-write.sh with concurrent writers
  - Integration test: 10 concurrent writers to same file
  - Chaos test: 50 concurrent agents, verify no corruption

**Success Criteria:**
- All writes to shared files use atomic operations
- Zero data corruption with 50 concurrent agents
- Lock contention <5%

### P2.2 Session-Scoped Lock Coordination
**Owner:** Platform Infrastructure
**Effort:** 4-5 hours
**Dependencies:** P2.1

- **P2.2.1** Implement lock manager for .claude/tmp/
  - Create hooks/lib/lock-manager.sh
  - Support lock acquisition with timeout
  - Implement FIFO fairness (queue-based)
  - Handle lock cleanup on timeout/crash

- **P2.2.2** Implement lock protocol
  - Lock request message format
  - Lock grant/release handshake
  - Deadlock detection & recovery
  - Support 50+ concurrent lock requesters

- **P2.2.3** Integrate lock manager into agents
  - Update hook-dispatcher to use lock manager
  - Each agent acquires session lock on start
  - Release lock on completion or crash
  - Document lock protocol in hooks/LOCKING.md

- **P2.2.4** Test lock fairness & contention
  - 50 agents concurrent lock acquisition
  - Measure wait times (should be FIFO fair)
  - Verify no starvation or deadlock
  - P95 wait time <100ms

**Success Criteria:**
- Lock manager supports 50+ concurrent agents
- FIFO fairness verified
- P95 lock wait time <100ms
- Zero deadlocks or starvation

### P2.3 Concurrent Agent Testing
**Owner:** QA Infrastructure
**Effort:** 3-4 hours
**Dependencies:** P2.1, P2.2

- **P2.3.1** Write chaos coordination tests
  - Test 50 agents concurrent file access
  - Test lock acquisition/release under pressure
  - Test agent crash recovery (orphaned locks)

- **P2.3.2** Run 10,000+ concurrent operations
  - 50 agents × 200 ops each = 10,000 ops
  - All shared state access (lock, file writes)
  - Verify no data loss or corruption
  - Measure latency percentiles

- **P2.3.3** Test failure scenarios
  - Agent crash during lock hold (cleanup)
  - Agent crash during file write (atomic recovery)
  - Network partition (if applicable)
  - Filesystem full (graceful degradation)

**Success Criteria:**
- 10,000 concurrent operations without failure
- All expected data present and uncorrupted
- Lock wait times <100ms (P95)
- Clear failure messages

**Phase 2 Completion:** Race conditions eliminated, safe 50-agent coordination

---

## Phase 3: Performance Optimization (Week 3)

**Objective:** Reduce hook execution latency by 60-75%
**Status:** PLANNED
**Risk:** LOW (performance improvements, backwards compatible)

### P3.1 Git Caching Layer
**Owner:** Performance Team
**Effort:** 6-8 hours
**Dependencies:** P2.4 (Phase 2 complete)

- **P3.1.1** Design git cache
  - Cache location: ~/.claude/.git-cache/
  - Caching strategy: file-based key-value (git command → output)
  - TTL: 60s per cache entry
  - Invalidation: file system events + periodic cleanup

- **P3.1.2** Implement git cache
  - Create hooks/lib/git-cache.sh
  - Wrapper: git_cached() function
  - Cache key: md5(git command)
  - TTL: check mtime, invalidate if >60s old

- **P3.1.3** Integrate into hook_should_run()
  - Cache git diff --name-only HEAD
  - Cache git ls-files
  - Cache git status --short
  - Measure cache hit rate

- **P3.1.4** Test cache correctness
  - Verify cache hits on repeated calls
  - Verify cache invalidation on git changes
  - Test edge cases: file deletion, merge, rebase
  - Measure latency improvement (target: 70% reduction)

- **P3.1.5** Monitor cache effectiveness
  - Log cache hits vs misses
  - Report cache hit rate in quality-gate output
  - Alert if hit rate drops below 80%

**Success Criteria:**
- Git operations reduced by 70%
- Cache hit rate >85%
- 60s TTL prevents stale data
- Latency improvement verified

### P3.2 Tool Discovery Caching
**Owner:** Performance Team
**Effort:** 4-6 hours
**Dependencies:** P3.1

- **P3.2.1** Analyze tool discovery overhead
  - Identify all `command -v` calls
  - Measure time per tool discovery
  - Find redundant discoveries (called multiple times)

- **P3.2.2** Move to initialization phase
  - Create hooks/lib/tool-registry.sh
  - Run at session start or daemon init
  - Scan PATH once, cache tool list
  - File watcher: detect new tools within 100ms

- **P3.2.3** Replace `command -v` with registry lookup
  - Update all hooks to use tool-registry
  - Remove inline `command -v` calls
  - Measure latency improvement (target: P95 <1ms per lookup)

- **P3.2.4** Test tool registry
  - Verify all tools found on first scan
  - Test PATH changes (should detect within 100ms)
  - Test new binary added to PATH
  - Performance: <10s initialization, <1ms per lookup

**Success Criteria:**
- Tool discovery 1-time initialization (5-10s)
- Subsequent lookups <1ms
- File watchers detect new tools within 100ms
- 99%+ cache hit rate

### P3.3 Hook Filtering Optimization
**Owner:** Performance Team
**Effort:** 3-4 hours
**Dependencies:** P3.2

- **P3.3.1** Analyze hook_should_run() efficiency
  - Profile current implementation
  - Identify bottlenecks (git, pattern matching)
  - Measure baseline latency

- **P3.3.2** Optimize pattern matching
  - Pre-compile filter patterns (not per-call)
  - Use efficient regex (avoid backtracking)
  - Cache compiled patterns in global variables

- **P3.3.3** Implement skip decision cache
  - Cache hook skip decision per session
  - Key: (hook name, file path pattern)
  - Invalidate on file change
  - Measure hit rate

- **P3.3.4** Test optimization
  - Verify no file change detection regressions
  - hook_should_run() <50ms
  - Measure cache hit rate (target: >90%)

**Success Criteria:**
- hook_should_run() latency <50ms
- Skip decision caching >90% hit rate
- No regressions in file change detection

### P3.4 Validation & Measurement
**Owner:** Performance Team
**Effort:** 2-3 hours
**Dependencies:** P3.1, P3.2, P3.3

- **P3.4.1** Comprehensive latency measurement
  - Measure Stop hook execution time
  - Baseline: before optimizations
  - After: each optimization phase
  - Calculate cumulative improvement

- **P3.4.2** Profile production workload
  - Run Stop hooks on realistic projects (100-1000 files)
  - Measure git cache hit rate
  - Measure tool discovery effectiveness
  - Document baseline metrics

- **P3.4.3** Performance regression tests
  - Ensure no degradation from caching
  - Test cache invalidation correctness
  - Test edge cases (large repos, slow FS)

**Success Criteria:**
- Median Stop latency <3s (target: 2-3s)
- P95 latency <6s
- 60-75% latency reduction measured
- Zero performance regressions

**Phase 3 Completion:** 60-75% latency reduction achieved, sub-3s median time

---

## Phase 4: Scaling & Dependency DAG (Week 4)

**Objective:** Scale to 50+ concurrent agents, establish dependency ordering
**Status:** PLANNED
**Risk:** MEDIUM (scaling unproven, requires careful testing)

### P4.1 Concurrent Agent Isolation Mechanism
**Owner:** Platform Infrastructure
**Effort:** 8-10 hours
**Dependencies:** P3.4 (Phase 3 complete)

- **P4.1.1** Research isolation mechanisms
  - APFS Copy-on-Write (macOS)
  - Containers (podman, Docker)
  - Namespace isolation (Linux)
  - FUSE overlays (cross-platform)
  - Document pros/cons of each

- **P4.1.2** Select best approach for macOS/Linux
  - Evaluate APFS COW + Linux alternatives
  - Consider compatibility and performance
  - Decision: [SELECT ONE - documented in ADR-001]

- **P4.1.3** Implement session-scoped isolation
  - Create agents/session-isolation.sh
  - Each agent gets isolated view of .claude/
  - Changes don't affect other agents
  - Cleanup on agent completion or crash

- **P4.1.4** Integration with hook-dispatcher
  - Update dispatcher to set up isolation per agent
  - Transparent to agent code (CLAUDE.md unchanged)
  - Document isolation mechanism in agents/README.md

- **P4.1.5** Test 50-agent isolation
  - Launch 50 concurrent agents
  - Each modifies local .claude/ view
  - Verify changes don't cross-contaminate
  - Cleanup all isolation artifacts

**Success Criteria:**
- 50+ agents with independent file views
- No worktree cleanup required
- Transparent to agent code
- Isolation cleanup verified

### P4.2 Lock Fairness & Backpressure
**Owner:** Platform Infrastructure
**Effort:** 4-5 hours
**Dependencies:** P4.1

- **P4.2.1** Implement fairness in lock acquisition
  - FIFO queue for lock requesters
  - Prevent lock starvation
  - Exponential backoff for contention

- **P4.2.2** Add backpressure when contention high
  - Monitor lock wait times
  - Signal backpressure if P95 >50ms
  - Recommended: throttle new agent launches

- **P4.2.3** Test fairness under load
  - 50 agents competing for locks
  - Measure wait time distribution
  - Verify within 10% variance
  - P95 wait time <50ms

- **P4.2.4** Document lock contention behavior
  - Update hooks/LOCKING.md with measurements
  - Provide guidelines for agent launching
  - Alert thresholds for backpressure

**Success Criteria:**
- Lock wait time fair (within 10% variance)
- P95 wait time <50ms
- No indefinite blocking or starvation
- Clear backpressure signaling

### P4.3 Hook Dependency DAG & Ordering
**Owner:** Platform Infrastructure
**Effort:** 5-6 hours
**Dependencies:** P3.4

- **P4.3.1** Document hook dependencies
  - Analyze which hooks depend on others
  - Example: spec-verifier depends on post-edit-checker output
  - Create dependency matrix in hooks/DEPENDENCIES.md

- **P4.3.2** Define DAG in hook-dispatcher config
  - Format: YAML or JSON hooks.json
  - Nodes: hook names
  - Edges: dependency relationships
  - Optional hooks: marked separately

- **P4.3.3** Implement topological sort
  - Update hook-dispatcher to load DAG
  - Implement topological sort algorithm
  - Execute independent hooks in parallel
  - Respect dependencies for dependent hooks

- **P4.3.4** Logging & traceability
  - Log execution order per hook
  - Show DAG visualization in help
  - Document in hooks/README.md

- **P4.3.5** Test DAG correctness
  - Verify dependency order respected
  - Verify parallel execution for independent hooks
  - Verify failure propagation
  - Edge case: circular dependency detection

**Success Criteria:**
- DAG covers all 15+ hooks
- Dependencies clear and documented
- Topological sort implemented correctly
- Failure propagation working
- Zero circular dependencies

### P4.4 Chaos Testing & Validation
**Owner:** QA Infrastructure
**Effort:** 4-5 hours
**Dependencies:** P4.1, P4.2, P4.3

- **P4.4.1** Write chaos coordination tests
  - 50 agents with isolation + locking + DAG
  - Test normal execution
  - Test agent crashes
  - Test lock contention
  - Test DAG failure scenarios

- **P4.4.2** Run at-scale tests
  - 50 agents × 100 operations = 5,000 ops
  - Measure latency, throughput, fairness
  - Verify isolation correctness
  - Verify lock cleanup

- **P4.4.3** Stress test corner cases
  - Rapid agent launch/shutdown
  - Lock acquisition timeout
  - DAG violation (improper execution order)
  - Cascading failures in DAG

- **P4.4.4** Performance under load
  - Measure Stop hook latency with 50 agents
  - Expected: <5s (some contention expected)
  - Monitor lock wait times
  - Report bottlenecks

**Success Criteria:**
- 5,000 concurrent operations without failure
- All expected data present
- Isolation verified
- Locks properly cleaned up
- <5s Stop latency under full load

### P4.5 Production Deployment & Monitoring
**Owner:** Platform Infrastructure & SRE
**Effort:** 3-4 hours
**Dependencies:** P4.4

- **P4.5.1** Finalize documentation
  - Update all README.md files
  - Document scaling limits and best practices
  - Update CHANGELOG.md
  - Add performance baselines

- **P4.5.2** Canary deployment
  - Deploy to test environment
  - Run with 10 concurrent agents
  - Monitor for issues (lock contention, isolation failures)
  - Verify all metrics

- **P4.5.3** Full deployment
  - Deploy to production
  - Monitor key metrics (latency, lock contention, errors)
  - Alert on anomalies
  - Daily review for first week

- **P4.5.4** Post-deployment validation
  - Real-world testing with developers
  - Collect feedback
  - Measure actual performance improvement
  - Document lessons learned

**Success Criteria:**
- Smooth production rollout
- All metrics within expected ranges
- Zero timeout failures
- Developer feedback positive
- 50+ agent coordination proven

**Phase 4 Completion:** 50-agent scaling achieved, DAG-based hook ordering established

---

## Cross-Phase Tasks

### Documentation Updates (All Phases)
- hooks/README.md - main documentation
- hooks/PERFORMANCE.md - latency baselines
- hooks/LOCKING.md - lock mechanism & protocol
- hooks/DEPENDENCIES.md - hook dependency matrix
- CHANGELOG.md - all changes documented

### Testing Infrastructure (All Phases)
- hooks/tests/unit/ - unit tests for each component
- hooks/tests/integration/ - integration tests
- hooks/tests/chaos/ - chaos/stress tests
- hooks/tests/performance/ - performance benchmarks

### Monitoring & Observability (Phase 3+)
- Structured logging of hook execution
- Metrics: latency, cache hit rate, lock contention
- Alerts: timeouts, race conditions, performance regressions
- Dashboard: hook health & performance

---

## Dependency Graph

```
P1.1 (Git Timeouts)
P1.2 (Output Streaming) ──────┐
P1.3 (Absolute Timeout) ──────┤
                               ├─→ P1.4 (Validation) ─→ Phase 1 Complete
                               │
                    (2 weeks later)
                               │
                               ├─→ P2.1 (Atomic Ops) ────┐
                               └─→ P2.2 (Lock Manager) ──┤
                                   P2.3 (Chaos Tests) ────┤─→ Phase 2 Complete
                                                          │
                                              (1 week later)
                                                          │
                    P3.1 (Git Caching) ────┐            │
                    P3.2 (Tool Registry)    ├─→ P3.4 ───┤─→ Phase 3 Complete
                    P3.3 (Filter Opt)  ────┤            │
                                            │            │
                                 (1 week later)         │
                                            │            │
        P4.1 (Isolation) ────┐              │            │
        P4.2 (Fairness)      ├─→ P4.4 ─────┤────────────┤─→ Phase 4 Complete
        P4.3 (DAG) ───────────┤       (Chaos Tests)     │
                              │                          │
                              └─→ P4.5 (Deployment) ────┘
```

---

## Success Metrics Summary

| Metric | Target | Phase |
|--------|--------|-------|
| Timeout Failure Rate | <0.01% | 1 |
| Race Condition Failures | 0% | 2 |
| Median Stop Latency | <3s | 3 |
| P95 Latency | <6s | 3 |
| Cache Hit Rate | >85% | 3 |
| Lock Contention | <5% | 2,4 |
| Concurrent Agents | 50+ | 4 |
| Code Coverage | >85% | All |

---

## Resource Allocation

| Phase | Team | FTE Weeks | Cost |
|-------|------|-----------|------|
| P1 | Infrastructure | 0.5 | Low |
| P2 | Infrastructure + QA | 1.0 | Medium |
| P3 | Performance + QA | 0.75 | Medium |
| P4 | Infrastructure + QA + SRE | 1.0 | Medium |
| **Total** | **3 people** | **3.25 weeks** | **$20-30K** |

---

## Risk Mitigation

| Risk | Mitigation | Owner |
|------|-----------|-------|
| Git caching invalidation bugs | File watchers + periodic invalidation | Performance |
| Lock deadlock (50 agents) | Formal verification + chaos tests | Infrastructure |
| Isolation mechanism failures | Prototype before full rollout | Infrastructure |
| Performance regression | Benchmarks before/after each phase | QA |
| Production deployment issues | Canary deployment to test first | SRE |

---

## Sign-Off & Review Points

- **Phase 1 Complete:** Zero timeout failures, all tests pass
- **Phase 2 Complete:** 50-agent concurrent tests pass, zero race conditions
- **Phase 3 Complete:** Latency <3s (median), cache hit rate >85%
- **Phase 4 Complete:** 50+ agents scaling verified, DAG enforcement working

All phases subject to code review, performance validation, and production readiness assessment.

