# Implementation Plan — thegent

**Document:** Phased WBS with dependencies for thegent unified agent orchestration
**Version:** 1.0
**Date:** 2026-03-29
**Planned Duration:** 8–10 weeks (4 phases)
**Target:** 2026-06-01

---

## Executive Summary

thegent unifies 10+ AI agents behind a single CLI and orchestration engine. This plan breaks implementation into 4 phases:

1. **Phase 1 (Weeks 1–2): Foundation** — Agent runners, registry, basic CLI
2. **Phase 2 (Weeks 3–4): Resilience** — Retry logic, fallback chains, failure classification
3. **Phase 3 (Weeks 5–7): Memory & Orchestration** — Session state, multi-turn workflows
4. **Phase 4 (Weeks 8–10): Integration & Polish** — MCP server, testing, documentation

---

## Phase 1: Foundation (Weeks 1–2)

### Goal
Establish core agent execution infrastructure: runners, registry, CLI skeleton.

### Work Packages

#### P1.1: Agent Runner Architecture
- **Deliverable:** `AgentRunner` trait + 3 runner implementations
- **Effort:** 16 hours
- **Tasks:**
  - [ ] Define `AgentRunner` trait with `run()` method signature (FR-AGT-001)
  - [ ] Implement `DirectAgentRunner` for native CLIs (claude, gemini, copilot)
  - [ ] Implement `CodexProxyRunner` for HTTP proxy agents (minimax, GLM)
  - [ ] Implement `CursorApiRunner` for OpenAI-compatible endpoints
  - [ ] Unit tests for each runner (mock subprocess, HTTP responses)
  - [ ] Integration tests with real agent binaries (if available)
- **Dependencies:** None
- **Acceptance Criteria:**
  - All 3 runners execute successfully in unit tests
  - Exit codes, stdout, stderr properly captured
  - Timeouts enforced (test with `sleep 100` and 5s timeout)

#### P1.2: Agent Registry & Resolution
- **Deliverable:** Canonical agent registry with name resolution
- **Effort:** 8 hours
- **Tasks:**
  - [ ] Define `AgentRegistry` struct with metadata per agent
  - [ ] Implement `get_runner(agent_name)` resolver
  - [ ] Implement alias resolution (e.g., "cursor" → "cursor-agent")
  - [ ] Implement `get_fallback_agents(agent_name)` with ordering
  - [ ] Unit tests for registry lookups and fallback chains
- **Dependencies:** P1.1 (needs runner types)
- **Acceptance Criteria:**
  - All 10 agents registered with correct runner types
  - Aliases resolve to canonical names
  - Fallback chains return ordered list excluding current agent

#### P1.3: CLI Skeleton & Agent Invocation
- **Deliverable:** `thegent run <agent> <prompt>` command
- **Effort:** 12 hours
- **Tasks:**
  - [ ] Set up Rust CLI project with Clap (argument parsing)
  - [ ] Implement `run` subcommand: `thegent run <agent> <prompt>`
  - [ ] Integrate runner selection from registry
  - [ ] Parse flags: `--model`, `--provider`, `--timeout`, `--workspace`
  - [ ] Output formatting: pretty-print agent response or JSON
  - [ ] Integration test: run actual agent subprocess
- **Dependencies:** P1.2 (needs registry)
- **Acceptance Criteria:**
  - `thegent run claude "hello"` invokes Claude agent
  - Output displayed correctly
  - Non-zero exit code on agent failure
  - Help text present (`thegent run --help`)

### Phase 1 Deliverables
- ✅ `src/runners/mod.rs` (runner trait + implementations)
- ✅ `src/registry.rs` (agent registry)
- ✅ `src/cli/run.rs` (run command)
- ✅ `tests/runners_test.rs` (unit tests)
- ✅ `tests/integration_test.rs` (CLI integration test)

### Phase 1 Validation
- [ ] All unit tests pass
- [ ] `cargo check` clean
- [ ] `cargo test` passes >80% coverage for Phase 1 code

---

## Phase 2: Resilience (Weeks 3–4)

### Goal
Add retry logic, failure classification, and fallback mechanisms for robust production use.

### Work Packages

#### P2.1: Failure Classification
- **Deliverable:** Failure kind detection via stderr pattern matching
- **Effort:** 12 hours
- **Tasks:**
  - [ ] Define `FailureKind` enum: RATE_LIMIT, TRANSIENT, USAGE_LIMIT, UNKNOWN
  - [ ] Create pattern registry for each failure type
  - [ ] Implement `classify_failure(stderr, stdout)` function
  - [ ] Unit tests: verify patterns match/unmatch correctly
  - [ ] Integration test: run agents, check classification accuracy
  - [ ] Maintain pattern version history in config
- **Dependencies:** P1.1 (needs agent execution)
- **Acceptance Criteria:**
  - 429 errors → RATE_LIMIT classification
  - 502/503/504 errors → TRANSIENT
  - "quota exceeded" → USAGE_LIMIT
  - Unknown errors → UNKNOWN (safe default)
  - >90% pattern match accuracy on collected stderr samples

#### P2.2: Exponential Backoff Retry
- **Deliverable:** Tenacity-based retry wrapper
- **Effort:** 10 hours
- **Tasks:**
  - [ ] Add tenacity dependency
  - [ ] Implement `retry_with_backoff(agent_runner, max_attempts, ...)` wrapper
  - [ ] Configure: 4 max attempts, 2s min delay, 60s max delay
  - [ ] Only retry on TRANSIENT and RATE_LIMIT failures
  - [ ] Log retry attempts with timestamps
  - [ ] Unit tests: mock transient failures, verify retries
  - [ ] Integration test: test with real agent (inject delay/failure)
- **Dependencies:** P2.1 (needs failure classification)
- **Acceptance Criteria:**
  - Transient failures retry 2–3 times then succeed
  - Rate limits trigger retry after backoff
  - Total retry time <30s (hard limit)
  - Non-retriable failures fail immediately
  - Logs show attempt count, delay duration

#### P2.3: Fallback Chains
- **Deliverable:** Automatic failover to next agent in chain
- **Effort:** 14 hours
- **Tasks:**
  - [ ] Define fallback chains in registry (Claude → Gemini → Codex → Cursor)
  - [ ] Implement `failover_to_next_agent(current_agent, failure_kind)`
  - [ ] Integrate with `run_with_fallback()` wrapper
  - [ ] Track attempted agents (prevent infinite loops)
  - [ ] User option: `--no-fallback` to disable
  - [ ] Unit tests: verify fallover order, skipped agents
  - [ ] Integration test: simulate agent failure, verify fallback
  - [ ] Logging: record all attempted agents with failure reasons
- **Dependencies:** P1.2 (needs registry fallback chains), P2.1 (needs failure classification)
- **Acceptance Criteria:**
  - First agent fails with USAGE_LIMIT → automatically try next
  - All agents in chain tried before giving up
  - User can disable fallback behavior
  - Clear logs showing which agents were tried and why

#### P2.4: Proxy Lifecycle Management (CLIProxyAPIPlus)
- **Deliverable:** Automated proxy startup/health-check/shutdown
- **Effort:** 16 hours
- **Tasks:**
  - [ ] Create `ProxyManager` struct for CLIProxyAPIPlus lifecycle
  - [ ] Binary resolution: CLIPROXYAPI_CMD env, $PATH, ~/.local/bin fallback
  - [ ] YAML config generation with provider blocks (minimax, GLM, antigravity)
  - [ ] Process startup with subprocess handling
  - [ ] Health polling: GET `/v1/models` until 200 response
  - [ ] Timeout enforcement: 5s default, configurable
  - [ ] Graceful shutdown: SIGTERM on drop
  - [ ] Unit tests: mock process/HTTP responses
  - [ ] Integration test: real proxy startup/shutdown
- **Dependencies:** P1.1 (CodexProxyRunner needs proxy), P1.2 (registry config)
- **Acceptance Criteria:**
  - Proxy process starts and becomes ready within 5s
  - Health check confirms `/v1/models` responds
  - Process terminated cleanly on shutdown (no zombies)
  - Proxy unavailable → clear error message
  - Timeout exceeded → process killed, error reported

### Phase 2 Deliverables
- ✅ `src/failures.rs` (failure classification)
- ✅ `src/retry.rs` (retry wrapper with tenacity)
- ✅ `src/fallback.rs` (fallback chain logic)
- ✅ `src/proxy_manager.rs` (proxy lifecycle)
- ✅ `src/config/patterns.toml` (failure patterns + registry)
- ✅ `tests/failures_test.rs`, `tests/retry_test.rs`, `tests/fallback_test.rs`

### Phase 2 Validation
- [ ] All unit tests pass (>85% coverage)
- [ ] Integration tests pass with mock agents
- [ ] Failure classification accuracy >90%
- [ ] Retry/fallback behavior verified

---

## Phase 3: Memory & Orchestration (Weeks 5–7)

### Goal
Implement session state management and multi-turn workflow orchestration.

### Work Packages

#### P3.1: Session State & Storage
- **Deliverable:** Persistent session storage with conversation history
- **Effort:** 18 hours
- **Tasks:**
  - [ ] Define `Session` struct: ID, created_at, updated_at, messages, metadata
  - [ ] Implement `SessionStore` trait (in-memory + file-based backends)
  - [ ] Session file format: JSONL (append-only for crash safety)
  - [ ] Directory structure: `$HELIOS_HOME/sessions/<session-id>/`
  - [ ] Implement CRUD: create, get, update, list, delete
  - [ ] Unit tests: all store operations
  - [ ] Integration test: persistence across runs
- **Dependencies:** None (can be independent)
- **Acceptance Criteria:**
  - Sessions persist to disk in JSONL format
  - CRUD operations work correctly
  - List operation returns all sessions with metadata
  - Corrupt JSONL recoverable (skip bad line)

#### P3.2: Conversation Memory & Context Window Management
- **Deliverable:** Track message history, manage token limits
- **Effort:** 16 hours
- **Tasks:**
  - [ ] Define `Message` struct: role (user/assistant), content, timestamp
  - [ ] Implement `ContextWindow` manager: track token usage
  - [ ] Token estimation: use `tiktoken` for accurate counts
  - [ ] Context truncation: keep recent messages, drop old ones when limit exceeded
  - [ ] Implement `add_message()`, `get_history()`, `prune_old_messages()`
  - [ ] Unit tests: token counting, truncation logic
  - [ ] Integration test: large conversation, verify history pruned correctly
- **Dependencies:** None (can be independent)
- **Acceptance Criteria:**
  - Token count accurate within 5% of actual
  - Messages oldest-first when history exceeds limit
  - User/system messages preserved (don't drop critical context)
  - Pruning prevents token overflow

#### P3.3: Task Orchestration Engine
- **Deliverable:** Multi-turn workflow execution with error recovery
- **Effort:** 20 hours
- **Tasks:**
  - [ ] Define `Task` and `Workflow` structs (DAG-based)
  - [ ] Implement task executor with branching (if-then-else)
  - [ ] Implement error recovery: retry task, fallback to next agent, abort workflow
  - [ ] Implement tool invocation integration (shell, file, MCP tools)
  - [ ] Output parsing: extract structured results from agent responses
  - [ ] Unit tests: workflow execution, branching, error handling
  - [ ] Integration test: multi-turn workflow (e.g., code analysis → generation → review)
- **Dependencies:** P3.1 (session state), P2.2 (retry logic), P2.3 (fallback)
- **Acceptance Criteria:**
  - Workflows execute in correct order (DAG respects dependencies)
  - Error recovery attempts specified fallback
  - Tool invocations execute and integrate results
  - Output parsing extracts code/suggestions correctly
  - Workflows complete or fail atomically

#### P3.4: Streaming Response Support
- **Deliverable:** Real-time streaming output from agents
- **Effort:** 12 hours
- **Tasks:**
  - [ ] Modify `AgentRunner` trait to support streaming mode
  - [ ] Implement streaming for DirectAgentRunner (subprocess output)
  - [ ] Implement streaming for HTTP proxy runners (Server-Sent Events)
  - [ ] Implement streaming for MCP tools (async iteration)
  - [ ] Buffer management: don't buffer entire response, stream in chunks
  - [ ] Unit tests: mock streaming output
  - [ ] Integration test: stream large agent output (>10MB)
- **Dependencies:** P1.1 (runner implementations)
- **Acceptance Criteria:**
  - Streaming output appears in real-time (not buffered)
  - Works with all 3 runner types
  - No memory bloat (constant memory usage regardless of output size)
  - Streaming can be toggled on/off

### Phase 3 Deliverables
- ✅ `src/session.rs` (session state + storage)
- ✅ `src/memory.rs` (conversation memory + context window)
- ✅ `src/orchestration.rs` (task orchestration engine)
- ✅ `src/streaming.rs` (streaming support)
- ✅ `tests/session_test.rs`, `tests/memory_test.rs`, `tests/orchestration_test.rs`

### Phase 3 Validation
- [ ] All unit tests pass (>80% coverage)
- [ ] Integration tests pass with multi-turn workflows
- [ ] Session persistence verified
- [ ] Context window truncation correct
- [ ] Streaming output real-time

---

## Phase 4: Integration & Polish (Weeks 8–10)

### Goal
Add MCP server, complete testing, finalize documentation, ship production-ready release.

### Work Packages

#### P4.1: MCP Server Implementation
- **Deliverable:** Embedded MCP server exposing thegent tools
- **Effort:** 14 hours
- **Tasks:**
  - [ ] Add MCP server transport (stdio + WebSocket)
  - [ ] Expose `run_agent` tool via MCP protocol
  - [ ] Expose `apply_patch`, `query_knowledge` tools
  - [ ] Implement JSON-RPC 2.0 request/response
  - [ ] Unit tests: tool validation, schema compliance
  - [ ] Integration test: MCP client connects, calls tools
- **Dependencies:** P1.3 (run command), P3.3 (orchestration tools)
- **Acceptance Criteria:**
  - MCP server starts on `thegent mcp --port 9000`
  - External clients discover tools via MCP protocol
  - Tool schemas match FR-SRV-004, FR-SRV-005

#### P4.2: Test Suite Expansion
- **Deliverable:** Comprehensive unit + integration test coverage
- **Effort:** 18 hours
- **Tasks:**
  - [ ] Unit tests for all modules (target >85% coverage)
  - [ ] Integration tests: end-to-end CLI workflows
  - [ ] Property-based tests: failure classification accuracy, token counting
  - [ ] Load tests: orchestration engine with 100+ tasks
  - [ ] Chaos tests: agent failures, network partitions (via fault injection)
  - [ ] CI/CD pipeline: GitHub Actions, cargo test, coverage reports
- **Dependencies:** All previous phases
- **Acceptance Criteria:**
  - Overall coverage >80%
  - All integration tests pass
  - Load tests complete in <30s
  - CI/CD pipeline green on main

#### P4.3: Documentation & Examples
- **Deliverable:** User guide, API reference, example scripts
- **Effort:** 12 hours
- **Tasks:**
  - [ ] USER_JOURNEYS.md: UJ-006 (background app server with IPC)
  - [ ] API reference: runner interface, registry, orchestration API
  - [ ] Example scripts: multi-turn workflow, fallback chain usage
  - [ ] Troubleshooting guide: common errors, debug mode
  - [ ] Architecture guide: runner types, decision rationale
- **Dependencies:** All previous phases
- **Acceptance Criteria:**
  - All public API documented with examples
  - Runnable example scripts in `examples/`
  - ADRs linked from relevant docs

#### P4.4: Performance Optimization & Cleanup
- **Deliverable:** Optimized, production-ready codebase
- **Effort:** 10 hours
- **Tasks:**
  - [ ] Profile agent execution (where is time spent?)
  - [ ] Optimize hot paths (retry backoff, pattern matching)
  - [ ] Remove dead code, consolidate similar modules
  - [ ] Clippy linting: 0 warnings
  - [ ] Code review for architectural consistency
  - [ ] Performance benchmarks: agent invocation latency
- **Dependencies:** All previous phases
- **Acceptance Criteria:**
  - Benchmarks show <100ms overhead for agent dispatch
  - No clippy warnings
  - All modules follow consistent patterns

#### P4.5: Release & Deployment
- **Deliverable:** v0.1.0 release with versioning + changelog
- **Effort:** 6 hours
- **Tasks:**
  - [ ] Update CHANGELOG.md with v0.1.0 entry
  - [ ] Tag: `v0.1.0` with annotated release notes
  - [ ] Release notes: major features, breaking changes, known limitations
  - [ ] Update README.md with quick-start guide
  - [ ] Publish crate to crates.io
  - [ ] Tag GitHub release with binary artifacts
- **Dependencies:** All previous phases
- **Acceptance Criteria:**
  - Crate published to crates.io
  - GitHub release contains binaries
  - Changelog reflects all features completed

### Phase 4 Deliverables
- ✅ `src/mcp_server.rs` (MCP server implementation)
- ✅ `tests/` (comprehensive test suite)
- ✅ `docs/API.md`, `examples/`, troubleshooting guide
- ✅ Performance benchmarks
- ✅ v0.1.0 release tag + changelog

### Phase 4 Validation
- [ ] CI/CD pipeline fully green
- [ ] All tests pass
- [ ] Performance benchmarks meet targets
- [ ] Code review completed
- [ ] Release published

---

## Dependency Graph (DAG)

```
┌─────────────────────────────────────────────────────────┐
│ Phase 4: Integration & Polish (Weeks 8–10)              │
│                                                          │
│ P4.1: MCP Server ◄────────────────────────┐            │
│ P4.2: Test Suite ◄──────┐                 │            │
│ P4.3: Documentation ◄──┐ │                 │            │
│ P4.4: Performance ◄──┐ │ │                 │            │
│ P4.5: Release ◄──────┴─┴─┴──────┐         │            │
└─────────────────────────────────│──────────────────────┘
                                  ▲
                                  │ (depends on all Phase 3)
┌─────────────────────────────────┼──────────────────────┐
│ Phase 3: Memory & Orchestration (Weeks 5–7)            │
│                                  │                      │
│ P3.1: Session State ◄────┐       │                      │
│ P3.2: Memory Manager ◄──┐│       │                      │
│ P3.3: Orchestration ◄───┼┼───────┼──┐                  │
│ P3.4: Streaming ◄─┐      ││       │  │                  │
└──────────────────┼──────┼┼───────┼──────────────────────┘
                   │      ││       │
                   │      ││       ▲ (P2.2, P2.3)
                   │      │└───────┼────────┐
                   │      └────────┼──────┐ │
┌──────────────────┼───────────────┼──────┼─┼────────────┐
│ Phase 2: Resilience (Weeks 3–4)  │      │ │            │
│                  │                │      │ │            │
│ P2.1: Failure Classification ◄──┐│      │ │            │
│ P2.2: Retry ◄─────┐             ││      │ │            │
│ P2.3: Fallback ◄──┼─┐           ││      │ │            │
│ P2.4: Proxy Mgmt ◄─┘ │ (P2.1)   ││      │ │            │
└──────────────────────┼───────────┼┼──────┼─┼────────────┘
                       │           ││      │ │
                       │           ││      │ ▲ (P1.2)
                       │           ││      │ │
┌──────────────────────┼───────────┼┼──────┼─┼────────────┐
│ Phase 1: Foundation (Weeks 1–2) │ │      │ │            │
│                                  │ │      │ │            │
│ P1.1: Agent Runners ◄───┐       │ │      │ │            │
│ P1.2: Registry ◄──────┐ │ (P1.1)│ │      │ │            │
│ P1.3: CLI ◄──────────┐│ │ (P1.2)│ │      │ │            │
└───────────────────────┼┼────────┼──┘      │ │            │
                        ││        │         │ │
                        └┴────────┴─────────┴─┘
```

---

## Timeline Summary

| Phase | Duration | Key Milestones |
|-------|----------|-----------------|
| **Phase 1** | 2 weeks | ✓ Agent runners, registry, basic CLI |
| **Phase 2** | 2 weeks | ✓ Retry logic, fallback chains, proxy management |
| **Phase 3** | 3 weeks | ✓ Session state, memory management, orchestration |
| **Phase 4** | 3 weeks | ✓ MCP server, testing, docs, v0.1.0 release |
| **Total** | **8–10 weeks** | **Target: 2026-06-01** |

---

## Success Criteria

- ✅ All 8 ADRs implemented with working code
- ✅ 10 agents registered and routable
- ✅ Unit test coverage >80%
- ✅ Integration tests pass end-to-end
- ✅ Performance: agent dispatch <100ms overhead
- ✅ Documentation complete (API, examples, troubleshooting)
- ✅ v0.1.0 released to crates.io
- ✅ MCP server operational for external clients

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Agent APIs change frequently | High | High | Maintain fallback chains; abstract runner interface |
| Token counting inaccuracy | Medium | Medium | Use tiktoken library; empirical validation |
| Proxy startup timeouts | Low | Medium | Configurable timeout (default 5s); clear error messages |
| Test flakiness | Medium | Low | Mock external services; seed RNG for reproducibility |
| Performance regression | Low | Medium | Benchmark on each commit; ratchet max latency |

---

## Document Governance

- **Owner:** thegent Architecture Team
- **Last Updated:** 2026-03-29
- **Next Review:** 2026-04-15 (Phase 1 completion)
- **Status:** ✅ Ready for Phase 1 Kickoff
