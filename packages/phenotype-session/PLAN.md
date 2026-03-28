# pheno-session — Implementation Plan

**Version:** 1.0 | **Status:** In Progress | **Date:** 2026-03-28

This plan maps the PRD epics and user stories to phased work packages (WPs) with explicit DAG dependencies. The system is a Go CLI/TUI application using Cobra, Bubble Tea, and SQLite.

---

## Phase 1: Foundation & Storage

**Status:** Mostly Complete

Core domain model, storage layer, and CLI scaffolding.

| Task ID | Description | Depends On | Status |
|---------|-------------|------------|--------|
| P1.1 | Domain model: SessionMeta struct with all fields (id, name, harness, provider, model, dir, timestamps, state, provider_meta) | — | Done |
| P1.2 | Session state enum: active, paused, closed with transition validation logic | — | Done |
| P1.3 | SQLite adapter: schema creation, WAL mode, auto-migration on startup | — | Done |
| P1.4 | SQLite schema: Sessions table with indexes on (harness, provider, updated_at), Tasks table, AuditLog table, StateHistory table | P1.3 | Done |
| P1.5 | JSON fallback storage: NDJSON persistence and parsing for sessions | P1.1 | Done |
| P1.6 | Store interface trait: define common API for both SQLite and JSON backends | P1.2, P1.3, P1.5 | Done |
| P1.7 | Cobra CLI scaffolding: root command, global flags (--config, --verbose), subcommand routing | — | Done |
| P1.8 | Error handling: domain errors, storage errors, adapter errors with context and recovery hints | P1.1-P1.7 | Done |

**Deliverables:**
- SessionMeta domain model fully defined
- SQLite database with all schema tables, indexes, auto-migration
- Store trait with two implementations (SQLite, JSON)
- Cobra CLI entry point with help system

---

## Phase 2: Core CLI Commands

**Status:** Mostly Complete

Session CRUD and state management commands.

| Task ID | Description | Depends On | Status |
|---------|-------------|------------|--------|
| P2.1 | CLI: `pheno-session start --provider <p> --model <m> [--name <n>] [--dir <d>]` — creates session and prints UUID | P1.7, P1.6 | Done |
| P2.2 | CLI: `pheno-session list [--harness <h>] [--provider <p>] [--dir <d>] [--sort <by>] [--limit <n>] [--json]` with filtering and sorting | P1.6, P1.7 | Done |
| P2.3 | CLI: `pheno-session get <session-id>` — retrieve and display single session with all metadata | P1.6, P1.7 | Done |
| P2.4 | CLI: `pheno-session delete <session-id>` — soft-delete (mark closed), update state history and audit log | P1.6, P1.7 | Done |
| P2.5 | Directory filtering logic: --dir prefix matching, path normalization, integration with list command | P2.2 | Done |
| P2.6 | Sorting implementation: updated_by (actor), updated_at (timestamp), name (alphabetical) with desc/asc configuration | P2.2 | Done |
| P2.7 | JSON output formatting: newline-delimited JSON, validation, pipe-friendly output | P2.2 | Done |
| P2.8 | State transition validation: forward-only transitions, audit entry creation, StateHistory logging | P1.2, P1.6 | Done |
| P2.9 | Actor attribution: derive actor from $USER env, override via --actor flag | P1.1, P2.1-P2.4 | Done |

**Deliverables:**
- `pheno-session start`, `list`, `get`, `delete` commands fully functional
- All list filters and sorting modes working
- JSON output mode for tool integration
- Audit trail fully populated for all mutations

---

## Phase 3: TUI Implementation

**Status:** In Progress

Interactive terminal user interface using Bubble Tea.

| Task ID | Description | Depends On | Status |
|---------|-------------|------------|--------|
| P3.1 | Bubble Tea app skeleton: main loop, event handling, model/view/update pattern | P1.7 | Done |
| P3.2 | Session list view: display paginated list of sessions with columns (ID, Name, Harness, Provider, Model, Updated, State) | P1.6, P3.1 | Done |
| P3.3 | Keyboard navigation: j/k or arrow keys to move selection, wrap at boundaries | P3.2 | Done |
| P3.4 | Sort cycling: s key cycles through updated_by → updated_at → name → repeat; footer shows current sort | P3.2, P2.6 | Done |
| P3.5 | Open session: Enter key invokes adapter.open on selected session, displays output in modal or status pane | P3.2, P4.1 | Done |
| P3.6 | Filter prompt: / key activates filter mode (placeholder implementation), Escape cancels | P3.2 | Planned |
| P3.7 | Help overlay: ? key shows keybindings, dismissible | P3.1 | Planned |
| P3.8 | Details pane (optional): tab/arrow to switch between list and details, editable name/state fields, save on Enter | P3.2 | Partial |
| P3.9 | Performance optimization: lazy-load sessions >500 items, pagination buffer strategy, <100ms initial render | P3.2 | Done |
| P3.10 | Error handling in TUI: display errors in red, dismissible modal, continue running | P3.1-P3.9 | Done |

**Deliverables:**
- `pheno-session tui` command launches interactive browser
- All keybindings functional (j/k, s, Enter, q)
- Performance targets met (<100ms initial render)
- Graceful error display and recovery

---

## Phase 4: Adapter Architecture

**Status:** In Progress

Provider-specific session management via pluggable adapters.

| Task ID | Description | Depends On | Status |
|---------|-------------|------------|--------|
| P4.1 | HarnessAdapter trait: ListSessions, GetSession, StartSession, TransferSession, OpenSession methods with standardized signatures | P1.1 | Done |
| P4.2 | Adapter registry: startup discovery, selection by harness name, fallback to stub if not found | P4.1 | Done |
| P4.3 | Forge adapter: reference implementation with reasonable placeholder behavior for all trait methods | P4.1, P4.2 | Done |
| P4.4 | Codex adapter: stub implementation (returns NotImplemented or basic passthrough) | P4.1, P4.2 | Done |
| P4.5 | Cursor adapter: stub implementation | P4.1, P4.2 | Done |
| P4.6 | Claude adapter: stub implementation | P4.1, P4.2 | Done |
| P4.7 | Droid adapter: stub implementation | P4.1, P4.2 | Done |
| P4.8 | Adapter error handling: NotImplemented, timeout, network errors with user-friendly messages | P4.1-P4.7 | Done |
| P4.9 | Adapter heartbeat service: probes all adapters every 5s, logs success/latency/failure (separate from main flow) | P4.1 | Done |

**Deliverables:**
- HarnessAdapter trait fully defined and documented
- Forge adapter with complete reference implementation
- Stubs for Codex, Cursor, Claude, Droid ready for future implementation
- Adapter registry and discovery working
- Heartbeat monitoring in background

---

## Phase 5: Transfer & SITBACK

**Status:** In Progress

Session transfer between harnesses and autonomous orchestration framework.

| Task ID | Description | Depends On | Status |
|---------|-------------|------------|--------|
| P5.1 | Transfer logic: snapshot session, create new session in target harness via adapter, mark source paused, record audit | P1.6, P4.1, P2.8 | Done |
| P5.2 | Transfer command: `pheno-session transfer <session-id> --to-harness <t> [--provider <p>] [--confirm]` with confirmation prompt | P5.1 | Done |
| P5.3 | Orchestrator struct: stores sessions, tasks, adapters; provides DelegateTask, GetAuditReport, ListTasks methods | P1.1, P1.6, P4.1 | Done |
| P5.4 | Task model: id, title, description, assigned_agent, state (pending|running|done|failed), priority, timestamps | — | Done |
| P5.5 | Tasks table schema: store tasks with indexed lookups by (assigned_agent, state) | P1.4, P5.4 | Done |
| P5.6 | MessagingService: publish task notifications to NATS (or local message queue), retry with exponential backoff | P5.4, P5.5 | Done |
| P5.7 | SITBACK light profile: read-only monitoring, harness discovery, session sampling every 5s, print summary | P5.3, P4.9 | Done |
| P5.8 | SITBACK medium profile: audit + monitoring, call orchestrator.AuditReport(), log to .agileplus/sitback.log with 10MB rotation | P5.3, P5.7 | Done |
| P5.9 | SITBACK full profile: autonomous actions — task retry (3 attempts, exponential backoff), session rebalance, agent restart (no heartbeat >5s) | P5.3, P5.7, P5.8 | Done |
| P5.10 | Harness discovery: process introspection to find Forge, Codex, Cursor, Claude, Droid processes by name/pattern | P5.7 | Done |
| P5.11 | Audit report generation: AuditReport struct with total_sessions, sessions_by_state, sessions_by_harness, running_agents, task counts, etc. | P1.4, P5.3 | Done |
| P5.12 | Audit command: `pheno-session audit` or `pheno-session sitback --audit` produces JSON report and exits (no continuous mode) | P5.11 | Done |
| P5.13 | Delegation command: `pheno-session delegate --task <title> --agent <agent-id> [--priority <p>] [--description <d>]` creates task and sends notification | P5.5, P5.6 | Done |
| P5.14 | Graceful shutdown: SITBACK profiles trap SIGTERM, complete in-flight actions within 10s, then exit | P5.7-P5.9 | Done |

**Deliverables:**
- Transfer command fully functional with confirmation
- Orchestrator framework (task delegation, audit, action orchestration)
- SITBACK light, medium, full profiles operational
- Task delegation with NATS messaging
- Audit reporting with JSON output

---

## Phase 6: Bridge & Integration

**Status:** In Progress

Integration with thegent SITBACK and external systems.

| Task ID | Description | Depends On | Status |
|---------|-------------|------------|--------|
| P6.1 | Thegent bridge: `pheno-session bridge [--thegent <path>] [--profile <p>]` spawns bridge process | P5.3, P5.7-P5.9 | Done |
| P6.2 | Thegent auto-discovery: PATH lookup, common installation paths (~/.cargo/bin, /usr/local/bin) | P6.1 | Done |
| P6.3 | Bridge heartbeat: send heartbeat to thegent every 2s, timeout 10s, log failures, attempt reconnection | P6.1 | Done |
| P6.4 | Task routing: tasks delegated via thegent are routed through pheno-session orchestrator to appropriate harness | P6.1, P5.6 | Done |
| P6.5 | Bridge graceful shutdown: SIGTERM → complete in-flight, close connection, exit cleanly within 10s | P6.1 | Done |
| P6.6 | Sync command: `pheno-session sync [--harness <h>]` discovers harnesses, calls ListSessions on adapters, merges with conflict resolution | P1.6, P4.1 | Done |
| P6.7 | Conflict resolution: remote wins if remote.updated_at > local.updated_at, else local wins | P6.6 | Done |
| P6.8 | Deduplication: (harness, session_id) key uniqueness, cross-harness duplicates not merged | P6.6 | Done |
| P6.9 | Sync report: print "Synced <N>: <new> new, <updated> updated, <deleted> deleted" on completion | P6.6 | Done |

**Deliverables:**
- Bridge command and thegent integration
- Sync command with conflict resolution and deduplication
- Heartbeat monitoring for bridge health

---

## Phase 7: Telemetry & Monitoring

**Status:** Planned

Health checks, metrics, and observability.

| Task ID | Description | Depends On | Status |
|---------|-------------|------------|--------|
| P7.1 | Metrics collection: total_sessions, active_sessions, closed_sessions, tasks_completed, adapter_latency | P1.6, P4.9 | Planned |
| P7.2 | OpenTelemetry integration: export metrics to stdout, NATS, or external collector | P7.1 | Planned |
| P7.3 | Health check endpoint (optional HTTP API): GET /health returns status, components, timestamp | P1.6, P7.1 | Planned |
| P7.4 | Prometheus text format export (optional): /metrics endpoint if HTTP enabled | P7.2 | Planned |
| P7.5 | Structured logging: all events logged with timestamp, level, actor, operation, context | P1.8 | Planned |

**Deliverables:**
- Metrics exposed in observable format
- Health check endpoint functional
- Prometheus-compatible metrics export

---

## Phase 8: Testing & Validation

**Status:** Planned

Unit tests, integration tests, and acceptance criteria verification.

| Task ID | Description | Depends On | Status |
|---------|-------------|------------|--------|
| P8.1 | Unit tests: Store trait implementations (SQLite, JSON), adapter registry, state transitions | P1.3-P1.6, P4.1-P4.2 | Planned |
| P8.2 | Integration tests: CLI commands (start, list, get, delete, transfer) with real store | P2.1-P2.9 | Planned |
| P8.3 | TUI tests: keyboard input, rendering, state consistency (via test harness) | P3.1-P3.10 | Planned |
| P8.4 | Adapter tests: Forge adapter with mock HTTP server, timeout handling | P4.1, P4.3 | Planned |
| P8.5 | SITBACK tests: light/medium/full profiles with mock orchestrator, task delegation | P5.1-P5.14 | Planned |
| P8.6 | Acceptance criteria: validate all FRs against test suite, >80% coverage target | P2.1-P5.14 | Planned |
| P8.7 | E2E tests: full workflow (start, list, transfer, sync, audit) with real fixtures | P2.1-P6.9 | Planned |

**Deliverables:**
- Comprehensive test suite with >80% coverage
- All FRs mapped to tests
- E2E test scenarios for major workflows

---

## Phase 9: Documentation & Release

**Status:** Planned

Documentation, release artifacts, and user guides.

| Task ID | Description | Depends On | Status |
|---------|-------------|------------|--------|
| P9.1 | README.md: quick start, command reference, flags, configuration | All phases | In Progress |
| P9.2 | API documentation: adapter trait, orchestrator interface, messaging protocol | P4.1, P5.3 | Planned |
| P9.3 | Architecture guide: design decisions, module structure, extension points | All phases | Planned |
| P9.4 | Installation & setup guide: building from source, dependencies, configuration | P1.7 | Planned |
| P9.5 | User guide: tutorial for common workflows (start, list, transfer, TUI, SITBACK) | P2.1-P5.14 | Planned |
| P9.6 | Binary release: build artifacts for macOS/Linux, publish to GitHub Releases | P1.7 | Planned |
| P9.7 | Docker image: Dockerfile for containerized deployment | P9.6 | Planned |

**Deliverables:**
- Complete user and developer documentation
- Release binaries for major platforms
- Docker image for containerized use

---

## Dependency Graph (DAG)

```
P1 (Foundation)
  ├─→ P2 (CLI Commands)
  │   ├─→ P3 (TUI)
  │   ├─→ P4 (Adapters)
  │   │   └─→ P5 (Transfer & SITBACK)
  │   │       └─→ P6 (Bridge & Integration)
  │   └─→ P5
  └─→ P4
      └─→ P5
          └─→ P6
              └─→ P7 (Telemetry)
              └─→ P8 (Testing)
              └─→ P9 (Documentation)
```

**Critical Path:** P1 → P2 → P5 (Transfer/Delegation) → P6 (Bridge) → P7/P8/P9

---

## Success Criteria

### Phase Completion Gates

- **Phase 1 Complete**: SQLite schema applied, Store trait working, CLI scaffolding functional
- **Phase 2 Complete**: All session CRUD commands working, state history tracked, audit trail populated
- **Phase 3 Complete**: TUI launches and navigates without crashes, <100ms initial render
- **Phase 4 Complete**: Adapter registry working, Forge adapter provides reference implementation, stubs ready for extension
- **Phase 5 Complete**: Transfer works, SITBACK profiles running, task delegation operational, audit reports generated
- **Phase 6 Complete**: Bridge to thegent functional, sync command working with conflict resolution
- **Phase 7 Complete**: Metrics exposed, health check endpoint (if implemented) responding
- **Phase 8 Complete**: >80% test coverage, all FRs traced to test cases
- **Phase 9 Complete**: User documentation complete, release binaries built and tested

### Cross-Phase Acceptance

- No sessions lost on ungraceful shutdown (SQLite WAL guarantees)
- All state transitions logged to audit trail with actor and timestamp
- Adapter timeouts handled gracefully (logged, retriable, non-blocking)
- SITBACK orchestration produces no data corruption or duplicate sessions
- CLI performance targets met: list <500ms, TUI render <100ms

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| SQLite schema migration complexity | Low | Medium | Phase 1 includes schema versioning; test migrations before release |
| Harness adapter implementation gaps | Medium | Medium | Stubs allow phased implementation; adapters fail gracefully with NotImplemented |
| SITBACK autonomous action conflicts | Low | High | Audit trail tracks all actions; full profile includes dry-run mode (future ADR) |
| TUI rendering performance degradation | Low | Medium | Lazy-load sessions >500 items, paginate with buffer strategy |
| Thegent bridge integration complexity | Medium | Low | Bridge is optional; pheno-session functions independently without it |
| Test coverage shortfall | Medium | Medium | Phase 8 includes acceptance testing against all FRs; coverage gates in CI |

---

## Resource Estimates

Assuming a single agent with parallelizable subtasks:

| Phase | Subtasks | Parallelizable | Estimated WallClock |
|-------|----------|----------------|-------------------|
| P1 | 8 | 4-5 | 8-10 min |
| P2 | 9 | 3-4 | 10-12 min |
| P3 | 10 | 2-3 | 12-15 min |
| P4 | 9 | 5 | 8-10 min |
| P5 | 14 | 4-5 | 15-20 min |
| P6 | 9 | 3-4 | 10-12 min |
| P7 | 5 | 2-3 | 5-8 min |
| P8 | 7 | 2-3 | 10-15 min |
| P9 | 7 | 2-3 | 8-10 min |
| **Total** | **78** | — | **86-122 min (1.4-2 hours)** |

With proper parallelization (subagents for independent tasks), expect 60-80 minutes wall clock.
