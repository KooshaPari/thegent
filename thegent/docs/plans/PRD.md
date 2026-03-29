# Product Requirements Document: Claude Code Hooks System Optimization

**Version:** 1.0
**Date:** 2026-02-15
**Status:** In Development
**Owner:** Platform Infrastructure Team

---

## Executive Summary

The Claude Code hooks system is critical infrastructure for quality enforcement, specification verification, and lifecycle management across all projects. Current implementation exhibits **timeout failures, race conditions, and inefficient resource utilization** that degrade reliability and developer experience.

This PRD defines a comprehensive optimization initiative to:
- **Eliminate timeout failures** (180s idle, 600s absolute) through efficient execution
- **Fix race conditions** on shared state (qa-state.json, session-changes.log, .claude/tmp/)
- **Scale safely** to 50+ concurrent agents without worktrees or external dependencies
- **Reduce hook execution time** by 60-75% through caching, batching, and parallelization
- **Establish clear dependency ordering** via DAG-based hook sequencing

**Expected Impact:** <2s hook execution latency, zero timeout failures, 100% reliability for concurrent agent coordination.

---

## Product Goals & Metrics

### G1: Eliminate Timeout Failures (P0)
- **Goal:** Zero hook timeout failures in normal operation
- **Current State:** 10-15% of runs experience 180s idle timeout or 600s absolute timeout
- **Success Criteria:**
  - All Stop hooks complete <5s in normal workload
  - 99.99% reliability (no timeout failures)
  - Output streaming prevents idle timeout detection
  - Traceability: logs show why each hook ran/didn't run

### G2: Fix Race Conditions (P0)
- **Goal:** Safe concurrent execution of 50+ agents without worktrees
- **Current State:** 3 known race conditions on qa-state.json, session-changes.log, .claude/tmp/
- **Success Criteria:**
  - Atomic file operations (flock, mkdir, rename)
  - No data loss or corruption under concurrent load
  - Lock contention <5% (99.95% lock-free execution)
  - Tested with chaos coordination tests

### G3: Performance: 60-75% Latency Reduction (P1)
- **Goal:** Reduce median Stop hook latency from 8-12s to 2-3s
- **Current State:**
  - Git operations: 40-50% of latency (frequent redundancy)
  - Tool discovery: 20-30% of latency (per-invocation re-scanning)
  - Hook filtering: 10-15% of latency (inefficient logic)
- **Success Criteria:**
  - Median latency <3s
  - P95 latency <6s
  - Git optimization: 70% reduction via caching
  - Tool discovery: 1-time initialization with file watchers

### G4: Scalable Concurrent Agent Coordination (P1)
- **Goal:** Seamlessly coordinate 50+ concurrent agents without external dependencies
- **Current State:**
  - Worktree-based isolation (requires cleanup, subject to race conditions)
  - No coordination mechanism for concurrent file access
  - Lock contention causes serialization bottlenecks
- **Success Criteria:**
  - 50+ agents execute in parallel without blocking
  - Session-scoped locking (MutexGuard, flock, named pipes)
  - Efficient queuing (FIFO with fairness, backpressure)
  - Load balanced across cores

### G5: Clear Hook Dependency Ordering (P2)
- **Goal:** Establish explicit DAG-based hook execution order
- **Current State:**
  - 9 Stop hooks run in parallel with no dependency ordering
  - Implicit assumptions about execution order (race conditions)
  - Difficult to reason about which hook data is available where
- **Success Criteria:**
  - DAG defined in hook-dispatcher config
  - Dependencies: spec-preflight → post-edit-checker → quality-gate → spec-verifier
  - Explicit ordering visible in logs
  - Optional parallelization where safe

---

## Epic Breakdown

### E1: Root Cause Analysis & Diagnosis
Investigate and document all timeout failures, race conditions, and performance bottlenecks.

**E1.1: Timeout Root Cause Analysis**
- Identify all git commands without timeouts
- Audit idle timeout prevention (output streaming)
- Analyze 180s vs 600s timeout triggers
- **Acceptance Criteria:**
  - Hook execution trace showing all timeout risks
  - Identified 8+ git commands without timeouts
  - Output streaming mechanism verified

**E1.2: Race Condition Audit**
- Trace all accesses to qa-state.json, session-changes.log, .claude/tmp/
- Identify missing flock/atomic operations
- Analyze concurrent agent impact on shared state
- **Acceptance Criteria:**
  - Full race condition matrix documented
  - Prioritized by severity (data loss risk)
  - 10+ specific race scenarios identified

**E1.3: Performance Profiling**
- Profile Stop hook execution: git operations, tool discovery, filtering logic
- Measure cache hit/miss rates
- Identify redundant operations across hooks
- **Acceptance Criteria:**
  - Detailed latency breakdown (>100ms operations flagged)
  - Git efficiency audit (redundant calls)
  - Tool discovery bottleneck analysis

### E2: Timeout Prevention & Output Streaming
Fix immediate timeout failures by adding output streaming and timeouts to blocking operations.

**E2.1: Git Command Hardening**
- Wrap all git commands with 5-30s timeouts (context-dependent)
- Add immediate output on hook start (prevent idle timeout)
- Implement git command caching where applicable
- **Acceptance Criteria:**
  - Zero git commands without timeout
  - hook_should_run() returns <100ms
  - test-maturity.sh completes <2s (verified)
  - task-completion-verifier.sh completes <2s (verified)

**E2.2: Output Streaming & Idle Timeout Prevention**
- Add `echo "HOOK: starting..." >&2` to all hooks at entry
- Implement progress reporting for long operations
- Ensure output every 30s for long-running operations
- **Acceptance Criteria:**
  - All hooks output within first 100ms
  - No 180s idle timeout failures
  - Dispatcher receives output continuously

**E2.3: Absolute Timeout (600s) Safeguards**
- Identify hooks at risk of 600s absolute timeout
- Add intermediate checkpoints (no operation >120s)
- Implement graceful degradation (fail fast vs hang)
- **Acceptance Criteria:**
  - All hooks complete <600s
  - Long operations have sub-120s checkpoints
  - Clear error messages on timeout

### E3: Race Condition Elimination
Fix concurrent execution issues through atomic operations and proper locking.

**E3.1: Atomic File Operations**
- Replace file appends with atomic flock-based writes
- Implement atomic mkdir-based locks for .claude/tmp/ coordination
- Use named pipes for inter-process communication (50+ agents)
- **Acceptance Criteria:**
  - All writes to qa-state.json use flock
  - session-changes.log appends are atomic
  - Zero data corruption under concurrent load

**E3.2: Session-Scoped Lock Coordination**
- Implement MutexGuard equivalent in bash (via flock)
- Create lock manager for .claude/tmp/ + /dev/shm fallback
- Distribute lock fairness across 50+ agents
- **Acceptance Criteria:**
  - Concurrent agent tests pass with 50 agents
  - Lock contention <5%
  - FIFO lock acquisition (fairness)

**E3.3: Concurrent Agent Testing**
- Write chaos coordination tests (lock/unlock under pressure)
- Simulate 50+ agents accessing shared state simultaneously
- Verify no race condition scenarios remain
- **Acceptance Criteria:**
  - 10,000 concurrent operations without failure
  - All expected data present and uncorrupted
  - Lock wait times <100ms (P95)

### E4: Performance Optimization
Reduce execution latency through caching, batching, and efficient algorithms.

**E4.1: Git Caching Layer**
- Implement git result caching in .claude/.git-cache/
- Cache git ls-files, git status, git diff (60s TTL)
- Invalidate cache on file system events
- **Acceptance Criteria:**
  - Git operations reduced by 70%
  - Cache hit rate >85%
  - 60s TTL prevents stale data
  - P95 latency <100ms (cache lookup)

**E4.2: Tool Discovery Caching**
- Move tool discovery from per-hook to initialization (Session/daemon mode)
- Cache tool list in .claude/.tool-cache/ with file watchers
- Invalidate on PATH changes or new binaries
- **Acceptance Criteria:**
  - Tool discovery 1-time only (5-10s initialization)
  - Subsequent lookups <1ms
  - File watchers detect new tools within 100ms

**E4.3: Hook Filtering & Short-Circuit**
- Optimize hook_should_run() to early-exit when no files changed
- Implement efficient file pattern matching (compiled regexes)
- Cache hook skip decisions per session
- **Acceptance Criteria:**
  - hook_should_run() <50ms
  - Skip decision cached per hook
  - No redundant file change detection

### E5: Concurrent Agent Scaling
Enable safe 50+ agent coordination without external dependencies (no worktrees).

**E5.1: Isolation Mechanism (Alternative to Worktrees)**
- Evaluate: APFS COW, containers, namespace isolation, FUSE overlays
- Select best approach for macOS/Linux compatibility
- Implement session-scoped isolation
- **Acceptance Criteria:**
  - 50+ agents with independent file views
  - No worktree cleanup required
  - Transparent to agent code (CLAUDE.md unmodified)

**E5.2: Lock Fairness & Backpressure**
- Implement FIFO queue for lock acquisition
- Add exponential backoff for lock contention
- Prevent starvation under high concurrency
- **Acceptance Criteria:**
  - Lock wait time fair (within 10% variance across agents)
  - No indefinite blocking
  - P95 wait time <50ms

**E5.3: Coordination Protocol**
- Define agent coordination messages (lock request/grant/release)
- Implement via named pipes + atomic files
- Handle agent crash recovery (lock cleanup)
- **Acceptance Criteria:**
  - Protocol handles 50+ agents
  - Crash recovery automatic
  - Zero orphaned locks

### E6: Hook Dependency DAG & Ordering
Establish explicit execution order through dependency graph.

**E6.1: DAG Definition**
- Document hook dependencies in hook-dispatcher config
- Example: spec-preflight → post-edit-checker → quality-gate → spec-verifier
- Allow conditional dependencies (only if previous succeeded)
- **Acceptance Criteria:**
  - DAG covers all 15+ hooks
  - Dependencies clear and documented
  - Config format supports serialization

**E6.2: Ordered Execution**
- Implement topological sort in hook-dispatcher
- Execute independent hooks in parallel
- Respect dependency ordering for dependent hooks
- **Acceptance Criteria:**
  - Hooks execute in correct order
  - Parallel hooks run concurrently
  - Logs show execution order

**E6.3: Failure Propagation**
- Define which hooks fail on upstream failure
- Allow optional hooks (failure doesn't stop pipeline)
- Implement clear failure messages
- **Acceptance Criteria:**
  - Failures propagate correctly
  - Optional hooks don't block pipeline
  - Clear error reporting

---

## User Stories

### US-E1.1: Diagnose Timeout Failures
**As a** platform engineer
**I want to** understand all git commands without timeouts
**So that** I can eliminate timeout failures systematically

- [x] Audit all git commands in hooks/lib/common.sh
- [x] Identify timeout risks in test-maturity.sh, task-completion-verifier.sh
- [x] Document timeout scenarios (idle 180s, absolute 600s)

### US-E2.1: Add Timeouts to Git Commands
**As a** hook maintainer
**I want to** ensure all git commands have reasonable timeouts
**So that** hooks never hang indefinitely

- [x] Add `timeout 5` wrapper to hook_should_run()
- [ ] Add timeouts to all other git commands (>20 total)
- [ ] Test with slow git repositories

### US-E2.2: Add Output Streaming
**As a** hook dispatcher
**I want to** receive continuous output from hooks
**So that** idle timeout detection doesn't trigger

- [x] Add immediate output to test-maturity.sh
- [x] Add immediate output to task-completion-verifier.sh
- [ ] Add to all 9+ Stop hooks
- [ ] Verify <100ms first output on all hooks

### US-E3.1: Atomic File Operations
**As a** concurrent agent coordinator
**I want to** safely write to shared files
**So that** no data corruption occurs under concurrency

- [ ] Implement flock-based atomic writes
- [ ] Convert qa-state.json writes to atomic operations
- [ ] Convert session-changes.log appends to atomic operations
- [ ] Test with 50+ concurrent agents

### US-E4.1: Git Caching
**As a** performance optimizer
**I want to** cache git results
**So that** 70%+ of git operations are eliminated

- [ ] Implement .claude/.git-cache/
- [ ] Cache git ls-files, git status, git diff
- [ ] Add 60s TTL with file system invalidation
- [ ] Measure cache hit rate and latency

### US-E5.1: 50-Agent Coordination
**As a** scalability engineer
**I want to** coordinate 50+ agents without worktrees
**So that** scaling doesn't require external infrastructure

- [ ] Research isolation mechanisms (APFS, containers, FUSE)
- [ ] Prototype best approach
- [ ] Implement session-scoped isolation
- [ ] Test with 50+ agents

---

## Non-Functional Requirements

| Requirement | Target | Rationale |
|------------|--------|-----------|
| Stop Hook Latency | <5s (median 2-3s) | Acceptable developer wait time |
| Timeout Failure Rate | <0.01% | Negligible impact on workflows |
| Race Condition Rate | 0% | Safety-critical infrastructure |
| Cache Hit Rate | >85% | Meaningful performance gain |
| Lock Contention | <5% | Efficient concurrent execution |
| Agent Scaling | 50+ agents | Meet roadmap requirement |
| Availability | 99.99% | Production-grade infrastructure |

---

## Constraints & Dependencies

### Technical Constraints
- **Platform:** macOS + Linux (POSIX shell compatibility)
- **No External Dependencies:** Use only bash, flock, named pipes, /dev/shm
- **Backwards Compatible:** Existing CLAUDE.md hooks unchanged
- **Daemon Optional:** Works with and without process-compose daemon

### Business Constraints
- **Timeline:** Ship in phases (Phase 1: timeout fixes, Phase 2: race conditions, Phase 3: optimization)
- **Risk:** Hooks are critical path - high quality bar
- **Dependency:** Requires coordination with hook-dispatcher maintainers

---

## Success Criteria

### Phase 1 (Timeout Prevention) - COMPLETE
- [x] test-maturity.sh timeout fixed (running <2s)
- [x] task-completion-verifier.sh timeout fixed (running <2s)
- [x] hook_should_run() returns <100ms
- [ ] All 9+ Stop hooks have output streaming
- [ ] Zero timeout failures in production

### Phase 2 (Race Conditions) - IN PROGRESS
- [ ] qa-state.json writes use atomic flock
- [ ] session-changes.log appends atomic
- [ ] Concurrent agent tests pass (50+ agents)
- [ ] Zero race condition failures

### Phase 3 (Performance) - PLANNED
- [ ] Git caching: 70% operation reduction
- [ ] Tool discovery caching: 1-time initialization
- [ ] Hook filtering: <50ms per hook_should_run()
- [ ] Median Stop latency <3s
- [ ] P95 latency <6s

### Phase 4 (Scaling & DAG) - PLANNED
- [ ] 50+ agent coordination without worktrees
- [ ] Hook dependency DAG defined and enforced
- [ ] Lock fairness verified
- [ ] Chaos tests pass (10,000 concurrent ops)

---

## Acceptance Criteria Definition

**Timeout Failure Prevention:**
- All git commands have timeout wrappers
- All hooks output within first 100ms
- test-maturity.sh executes <2s (verified)
- task-completion-verifier.sh executes <2s (verified)
- Zero timeout failures in 1,000 test runs

**Race Condition Elimination:**
- All writes to shared files use atomic operations (flock or atomic rename)
- Concurrent agent tests with 50+ agents complete without data corruption
- Lock wait times <100ms (P95)
- No orphaned locks after agent crash

**Performance Metrics:**
- Git cache hit rate >85%
- Tool discovery 1-time initialization (5-10s), subsequent <1ms
- hook_should_run() latency <50ms
- Median Stop hook time <3s
- P95 latency <6s

**Scalability:**
- 50+ agents coordinate without worktrees
- Lock contention <5% (99.95% lock-free)
- No degradation with concurrent load

---

## Open Questions & Risks

### Questions
1. **Isolation Mechanism:** APFS COW vs containers vs FUSE - which is best for macOS/Linux?
2. **Daemon vs Per-Session:** Should tool discovery run as daemon or per-session?
3. **Cache TTL:** 60s for git cache - is this appropriate or should it be configurable?
4. **Hook Dependencies:** Which hooks truly have dependencies vs false assumptions?

### Risks
- **Risk R1:** Git caching invalidation logic could miss changes (mitigate: file watchers + periodic invalidation)
- **Risk R2:** Flock unavailable on some systems (mitigate: fallback to mkdir-based locking)
- **Risk R3:** 50+ agent coordination unproven at scale (mitigate: chaos tests before release)
- **Risk R4:** Hook changes could break existing projects (mitigate: backwards compatibility tests)

---

## Future Enhancements

### Phase 5: Observability & Monitoring
- Hook execution traces (per hook, per operation)
- Real-time latency dashboards
- Alert on timeout/race condition detection
- Structured logging (JSON format)

### Phase 6: Distributed Hooks
- Multi-machine hook coordination (Redis/etcd optional)
- Centralized hook state management
- Federation across projects

### Phase 7: Predictive Scheduling
- ML-based hook optimization (predict which hooks to skip)
- Adaptive timeouts based on historical data
- Prioritize critical checks on fast path

---

## Document History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0 | 2026-02-15 | Platform Infrastructure | Initial PRD from research findings |
