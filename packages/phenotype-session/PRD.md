# pheno-session — Product Requirements Document

**Version:** 1.0 | **Status:** Active | **Last Updated:** 2026-03-28

---

## Executive Summary

pheno-session is a unified session orchestrator for LLM harnesses (Forge, Codex, Cursor, Claude, Droid). It provides:

1. **Session Persistence**: Store, list, and manage sessions across multiple LLM providers/harnesses with a unified schema
2. **Session Transfer**: Move active sessions between harnesses while preserving context and history
3. **Interactive TUI**: Browse and manage sessions via an intuitive terminal interface with sorting, filtering, and real-time state
4. **SITBACK Orchestration**: Autonomous monitoring, task delegation, audit reporting, and health discovery for multi-agent systems
5. **Sync & Delegation**: Bidirectional sync with external harnesses, task delegation to agents, and automatic message routing

---

## Epics and User Stories

### E1: Session Management Foundation

Users need a unified interface to create, list, browse, and manage sessions across all LLM harnesses.

#### E1.1: Session Persistence and Schema

**User Story E1.1.1**: As a developer, I want to create a new session with a specific provider/model so that I can start an LLM conversation.

- System SHALL persist sessions in SQLite at `~/.local/share/phenotype/sessions.db` (or fall back to JSON at `~/.local/share/phenotype/sessions.json`)
- Session fields: id (UUID), name, harness (codex|forge|cursor|claude|droid), provider, model, dir (working directory), created_at, updated_at, updated_by (actor name), last_message (summary), state (active|closed|paused), provider_meta (arbitrary JSON)
- Acceptance Criteria:
  - `pheno-session start --provider forge --model gpt-4o --name "my-session"` creates a session and prints its ID
  - Session is immediately queryable via `pheno-session get <session-id>`
  - Schema supports optional `dir` scoping for directory-specific sessions

**User Story E1.1.2**: As a user, I want to list all my sessions sorted by recency so that I can find active work.

- `pheno-session list` returns all sessions sorted by `updated_by` (last actor) descending
- Flags: `--harness <h>`, `--provider <p>`, `--dir <dir>`, `--sort <by>` (updated_by|updated_at|name), `--limit <n>`, `--json`
- Default: All sessions, sorted by updated_by, limit 100
- Acceptance Criteria:
  - Output is human-readable table with columns: ID, Name, Harness, Provider, Model, Updated, State
  - `--json` outputs newline-delimited JSON records
  - Filters combine with AND logic
  - Return empty list gracefully if no matching sessions

#### E1.2: Session Lifecycle Management

**User Story E1.2.1**: As a developer, I want to open a session in a specific harness so that I can resume work.

- `pheno-session open <session-id> --open-in <harness>` opens the session (harness-specific behavior, delegates to adapter)
- State remains active/paused as before; updated_at is refreshed
- Acceptance Criteria:
  - Command succeeds and prints harness-specific URI or status
  - Error if session is not found or target harness is invalid
  - updated_at timestamp is recorded

**User Story E1.2.2**: As a user, I want to transfer a session from one harness to another so that I can continue work in a different IDE/tool.

- `pheno-session transfer <session-id> --to-harness <target> [--provider <p>] [--confirm]` transfers ownership
- Snapshot session state, create session in target harness, mark source as paused/archived
- Acceptance Criteria:
  - Source session updated_by set to "transfer", state marked paused
  - New session created in target harness with same context
  - Audit entry recorded
  - `--confirm` skips confirmation prompts

**User Story E1.2.3**: As an operator, I want to close/delete sessions so that my session store doesn't grow indefinitely.

- `pheno-session delete <session-id>` soft-deletes (sets state to closed, does not erase record)
- Acceptance Criteria:
  - Session remains queryable but marked closed
  - `list` excludes closed sessions by default; `list --all` includes them
  - Audit entry recorded with actor name

#### E1.3: Work Directory Scoping

**User Story E1.3.1**: As a user in a specific project directory, I want to list only sessions relevant to that directory.

- `pheno-session list --dir <path>` filters sessions with matching dir prefix
- Default behavior lists all sessions (dir filter off)
- Acceptance Criteria:
  - `--dir ~/projects/foo` returns only sessions with dir matching ~/projects/foo*
  - No dir flag returns all sessions
  - Combine with other filters (--harness, --provider)

---

### E2: Interactive TUI

Users want a rich, keyboard-driven interface to browse, sort, and manage sessions without remembering CLI flags.

#### E2.1: Session Browser TUI

**User Story E2.1.1**: As a user, I want to browse sessions in a TUI with keyboard navigation so that I can quickly find and open sessions.

- `pheno-session tui` launches Bubble Tea interactive UI
- Display: paginated session list with selectable rows, current sort order, filter status
- Keybindings: j/k or arrow keys to move, Enter to open, s to cycle sort, / to filter (placeholder), q to quit
- Default sort: updated_by (descending)
- Acceptance Criteria:
  - Starts immediately (fast initial render <100ms)
  - j/k navigation wraps at list boundaries
  - Enter opens selected session in default harness (delegates to adapter)
  - s cycles through sort modes: updated_by → updated_at → name → (back to updated_by)
  - Displays current sort order in footer
  - q cleanly exits

#### E2.2: Session Details & Actions

**User Story E2.2.1**: As a user, I want to view and edit session details (name, state) in the TUI so that I can organize my sessions.

- Tab or arrow-right/left to navigate between list and details panes
- Details pane shows: id, name (editable), harness, provider, model, state, created_at, updated_at
- Acceptance Criteria:
  - Editable fields highlighted
  - Changes saved on Enter
  - Undo available with Escape
  - Audit entry recorded for each edit

---

### E3: SITBACK Orchestration

Autonomous monitoring, task delegation, and health discovery for multi-harness, multi-agent systems.

#### E3.1: SITBACK Profiles & Autonomous Monitoring

**User Story E3.1.1**: As a system operator, I want a light monitoring profile that reads session and harness state without taking any actions.

- `pheno-session sitback --profile light` runs read-only monitoring
- Discovers running harnesses (Forge, Codex, Cursor, Claude, Droid) via process introspection
- Outputs: total sessions, running agents, harness distribution, state breakdown
- Runs continuously until interrupted, updates every 5s
- Acceptance Criteria:
  - No mutations to session state
  - Handles missing harnesses gracefully (not found → skipped)
  - Outputs human-readable status every 5s
  - Keyboard interrupt (Ctrl+C) exits cleanly

**User Story E3.1.2**: As a system operator, I want a medium profile that audits harness health and reports issues without taking corrective action.

- `pheno-session sitback --profile medium` runs audit + monitoring
- Calls `AuditReport` from orchestrator: total sessions, running agents, pending/completed/failed tasks, messages sent
- Outputs audit summary to stdout and logs to `.agileplus/sitback.log`
- Runs continuously
- Acceptance Criteria:
  - Audit data reflects current state (sessions, task status, messages)
  - Issues (failed tasks, stale agents) highlighted in output
  - No automatic corrections applied
  - Log file rotated when >10MB

**User Story E3.1.3**: As a system operator, I want a full profile that autonomously rebalances sessions, retries failed tasks, and restarts stalled agents.

- `pheno-session sitback --profile full` runs autonomous orchestration
- Actions:
  - Retry failed tasks with exponential backoff (max 3 attempts, max 30s between retries)
  - Move sessions to less-loaded harnesses
  - Kill and restart stalled agents (no heartbeat in 5s)
  - Broadcast delegation messages to all agents
- Runs continuously with action logging
- Acceptance Criteria:
  - Each action recorded in audit trail with reasoning
  - Failed actions logged but do not block other operations
  - Configuration: max retries, timeouts, rebalance thresholds
  - Graceful shutdown on Ctrl+C (completes in-flight actions)

#### E3.2: Audit Reporting

**User Story E3.2.1**: As an operator, I want a single audit report command that summarizes system health.

- `pheno-session audit` or `pheno-session sitback --audit` produces a JSON report
- Report includes:
  - Total sessions (by state, by harness)
  - Running agents (discovered via process introspection)
  - Pending/completed/failed task counts
  - Messages sent in last 24h
  - Completion state distribution
  - Harness distribution
  - Timestamp of generation
- Acceptance Criteria:
  - JSON output is valid and parseable
  - Report generated in <2s
  - Can be piped to files or parsed by other tools
  - No side effects (read-only operation)

#### E3.3: Task Delegation & Messaging

**User Story E3.3.1**: As a system, I want to delegate tasks to agents and track their progress.

- Orchestrator defines Task struct: id, title, description, assigned_agent, state (pending|running|done|failed), priority, created_at, updated_at
- `pheno-session delegate --task <title> --agent <agent-id> --priority <1-5>` creates a delegated task
- Task stored in SQLite under Tasks table
- Messaging service delivers task notification to agent via NATS
- Acceptance Criteria:
  - Task created with UUID and stored
  - Notification sent to agent
  - Task state transitions tracked
  - Failed delivery retried with backoff

#### E3.4: Sync and External Harness Coordination

**User Story E3.4.1**: As an operator, I want to sync session state from all harnesses to a unified store.

- `pheno-session sync` discovers all running harnesses, calls their session list endpoints, merges results into local SQLite
- Conflict resolution: remote timestamp wins if newer, else local wins
- Acceptance Criteria:
  - All harnesses queried (with timeout 5s per harness)
  - Returned sessions merged into local store
  - Duplicates detected by (harness, session_id) key and deduplicated
  - Report printed: "synced 42 sessions, 3 new, 2 updated, 1 deleted"

---

### E4: Adapter Architecture

Pluggable provider adapters allow extensibility to new harnesses without core changes.

#### E4.1: Adapter Pattern

**User Story E4.1.1**: As a developer, I want to implement support for a new harness (e.g., Deepseek, Claude) by writing a harness adapter.

- Define HarnessAdapter trait: `ListSessions(filter) -> []SessionMeta`, `GetSession(id) -> SessionMeta`, `StartSession(params) -> SessionMeta`, `TransferSession(id, to_harness, params) -> SessionMeta`, `OpenSession(id, open_in) -> error`
- Implementations: Forge (partial), stubs for Codex, Cursor, Claude, Droid
- Registry pattern: adapters discovered at startup, selected by name
- Acceptance Criteria:
  - Adapter trait is stable (no breaking changes without major version bump)
  - New adapter requires <200 lines of boilerplate code
  - Forge adapter provides reference implementation
  - Each adapter can implement only relevant methods (others return NotImplemented)

---

### E5: Storage & Durability

Sessions must persist reliably and be queryable efficiently.

#### E5.1: SQLite Storage

**User Story E5.1.1**: As a user, I want my sessions to persist even if the tool crashes.

- SQLite implementation at `~/.local/share/phenotype/sessions.db`
- WAL mode enabled for concurrent read/write
- Schema: tables Sessions (id, name, harness, provider, model, dir, state, created_at, updated_at, updated_by, last_message, provider_meta), Tasks, AuditLog, StateHistory
- Auto-migration on startup
- Acceptance Criteria:
  - Sessions queryable immediately after restart
  - No corruption on ungraceful shutdown (WAL guarantees)
  - Schema versioning allows future migrations without breaking existing installations

#### E5.2: JSON Fallback

**User Story E5.2.1**: As a user without SQLite availability, I want to fall back to JSON storage for local development.

- JSON file at `~/.local/share/phenotype/sessions.json`
- Simple array of SessionMeta objects, one per line (newline-delimited JSON)
- Loaded into memory on startup, written atomically on change
- Acceptance Criteria:
  - No dependency on sqlite3 library
  - `pheno-session tui --sqlite` forces SQLite creation if not present
  - Fall back to JSON transparently if SQLite unavailable
  - Warn user that JSON is not recommended for production use

---

### E6: System Integration & Monitoring

pheno-session integrates with the broader Phenotype ecosystem (thegent, AgilePlus).

#### E6.1: Bridge to Thegent SITBACK

**User Story E6.1.1**: As a developer using thegent, I want pheno-session to act as a harness adapter within thegent's orchestration system.

- `pheno-session bridge --thegent <path> [--profile <profile>]` bridges pheno-session to thegent's sitback implementation
- Auto-discovers thegent binary if path not specified
- Orchestrator delegates tasks to agents, pheno-session routes to appropriate harness
- Acceptance Criteria:
  - Bridge starts and remains healthy (heartbeat every 2s)
  - Tasks delegated to agents are routed correctly
  - Bridge can be stopped without affecting running sessions
  - Logging integration with thegent

#### E6.2: Telemetry & Heartbeat

**User Story E6.2.1**: As an operator, I want to monitor pheno-session health via heartbeat and metrics.

- Heartbeat service: periodic checks of all running harness adapters (every 5s)
- Metrics: session count, task throughput, adapter response times, error rates
- Exposed via OpenTelemetry (stdout, NATS, or external collector)
- Acceptance Criteria:
  - Heartbeat failures logged and recoverable
  - Metrics expose: total_sessions, active_sessions, tasks_completed, adapter_latency_p99
  - Health check endpoint (HTTP or gRPC) returns healthy/degraded/unhealthy

---

## Constraints & Assumptions

1. **Single-user primary use case**: Designed for solo developers and autonomous agents; concurrent writes are serialized by SQLite
2. **Harness discovery**: Process introspection assumes common process names/patterns; DNS/port-scanning alternative for networked harnesses deferred
3. **No authentication**: Local file-based storage assumes trusted environment
4. **Async/concurrent**: Uses Go's goroutines for concurrent harness querying; SITBACK profiles run on a single event loop
5. **Offline first**: All features work offline except external harness sync and NATS event publishing

---

## Non-Functional Requirements

1. **Performance**: List operations complete in <500ms for 1000 sessions
2. **Durability**: No data loss on crash (SQLite WAL guarantees)
3. **Maintainability**: Clear separation between CLI, TUI, orchestration, storage, and adapters
4. **Observability**: All state transitions logged to audit trail with timestamps and actor attribution
5. **Extensibility**: Adapter pattern allows new harnesses without core changes

---

## Related Documentation

- README.md — Quick start and command reference
- FUNCTIONAL_REQUIREMENTS.md — Detailed SHALL statements for acceptance testing
- PLAN.md — Phased implementation roadmap with DAG dependencies
- ADRs in Phenotype governance — Architecture decisions
