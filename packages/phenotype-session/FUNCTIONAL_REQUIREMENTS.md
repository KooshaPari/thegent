# pheno-session — Functional Requirements

**Version:** 1.0 | **Status:** Active | **Updated:** 2026-03-28

**Traces to:** PRD.md v1.0

---

## FR-STORAGE: Persistent Session Storage

| ID | Requirement | Traces To | Status |
|----|-------------|-----------|--------|
| FR-STORAGE-001 | The system SHALL persist sessions in SQLite at `~/.local/share/phenotype/sessions.db` with a unified schema supporting all harness types (Codex, Forge, Cursor, Claude, Droid) | E5.1 | Implemented |
| FR-STORAGE-002 | Each session record SHALL contain: id (UUID string), name (String), harness (enum), provider (String), model (String), dir (Option<String>), created_at (Timestamp), updated_at (Timestamp), updated_by (String, actor name), last_message (Option<String>), state (enum: active\|closed\|paused), provider_meta (JSON map), and custom fields per harness | E1.1.1 | Implemented |
| FR-STORAGE-003 | The system SHALL support JSON-based fallback storage at `~/.local/share/phenotype/sessions.json` if SQLite is unavailable; JSON format SHALL be newline-delimited JSON (NDJSON) with one session per line | E5.2 | Implemented |
| FR-STORAGE-004 | SQLite implementation SHALL use WAL (Write-Ahead Logging) mode to allow concurrent reads during writes and prevent corruption on ungraceful shutdown | E5.1 | Implemented |
| FR-STORAGE-005 | The schema SHALL include tables: Sessions (primary entity), Tasks (for task delegation), AuditLog (immutable audit entries), StateHistory (state transition tracking with timestamps) | E1.1, E3.3 | Implemented |
| FR-STORAGE-006 | The system SHALL auto-apply schema migrations on startup without user intervention; schema version SHALL be tracked in a metadata table | E5.1 | Implemented |
| FR-STORAGE-007 | All UUIDs for session IDs SHALL be generated via `uuid::v4()` and stored as lowercase hex strings | E1.1.1 | Implemented |

---

## FR-SESSIONS: Session CRUD Operations

| ID | Requirement | Traces To | Status |
|----|-------------|-----------|--------|
| FR-SESSIONS-001 | The `pheno-session start --provider <p> --model <m> [--name <n>] [--dir <d>]` command SHALL create a new session in the `active` state with the provided parameters and print its UUID | E1.2.1 | Implemented |
| FR-SESSIONS-002 | The `pheno-session get <session-id>` command SHALL retrieve and display a single session by UUID; error with "session not found" if the ID does not exist | E1.1.1 | Implemented |
| FR-SESSIONS-003 | The `pheno-session list [--harness <h>] [--provider <p>] [--dir <d>] [--sort <by>] [--limit <n>] [--json]` command SHALL list all sessions matching filters, sorted by the specified field, limited to N results (default 100) | E1.1.2 | Implemented |
| FR-SESSIONS-004 | List filters (--harness, --provider, --dir) SHALL combine with AND logic; omitted filters match any value (wildcard) | E1.1.2 | Implemented |
| FR-SESSIONS-005 | The --sort flag SHALL accept values: `updated_by` (actor name, default), `updated_at` (most recent first), `name` (alphabetical) | E1.1.2 | Implemented |
| FR-SESSIONS-006 | The --json flag SHALL output newline-delimited JSON (one session per line); each record SHALL be a complete SessionMeta object with all fields | E1.1.2 | Implemented |
| FR-SESSIONS-007 | The `pheno-session open <session-id> [--open-in <harness>]` command SHALL retrieve the session and delegate to the harness adapter; the adapter SHALL implement harness-specific open logic | E1.2.1 | Implemented |
| FR-SESSIONS-008 | The `pheno-session delete <session-id>` command SHALL soft-delete the session (set state to `closed`); the record SHALL remain queryable but excluded from default list output | E1.2.3 | Implemented |
| FR-SESSIONS-009 | Closed sessions SHALL be included in list output only when `--all` flag is passed or `--state closed` filter is active | E1.2.3 | Implemented |

---

## FR-STATE: Session State Management

| ID | Requirement | Traces To | Status |
|----|-------------|-----------|--------|
| FR-STATE-001 | Session states SHALL be: `active` (session in use), `paused` (suspended temporarily), `closed` (soft-deleted), with forward-only state transitions permitted (no backward transitions without explicit override) | E1.2 | Implemented |
| FR-STATE-002 | Every state transition SHALL record an entry in the StateHistory table with: session_id, from_state, to_state, timestamp, actor_name, reason | E1.2 | Implemented |
| FR-STATE-003 | The `updated_at` timestamp SHALL be refreshed on every operation (get, open, transition); the `updated_by` field SHALL reflect the actor name (derived from $USER env or "system") | E1.2 | Implemented |
| FR-STATE-004 | When a session state changes, an audit entry SHALL be created with the transition details and stored in the AuditLog table | E1.2 | Implemented |

---

## FR-DIRECTORY-SCOPING: Directory-Based Session Filtering

| ID | Requirement | Traces To | Status |
|----|-------------|-----------|--------|
| FR-DIR-001 | Sessions MAY have an optional `dir` field representing the working directory for the session context | E1.3.1 | Implemented |
| FR-DIR-002 | The `--dir <path>` filter SHALL perform prefix matching: `--dir ~/projects/foo` matches sessions with dir values `~/projects/foo`, `~/projects/foobar/subsession`, etc. | E1.3.1 | Implemented |
| FR-DIR-003 | When the `--dir` flag is not provided, list output SHALL include all sessions regardless of dir value (no implicit directory filtering) | E1.3.1 | Implemented |
| FR-DIR-004 | Directory paths SHALL be normalized and expanded (e.g., `~/` → home directory) before filtering | E1.3.1 | Implemented |

---

## FR-TUI: Terminal User Interface

| ID | Requirement | Traces To | Status |
|----|-------------|-----------|--------|
| FR-TUI-001 | The `pheno-session tui` command SHALL launch an interactive Bubble Tea UI that displays all sessions in a paginated, selectable list | E2.1.1 | Implemented |
| FR-TUI-002 | The TUI session list SHALL display columns: ID (truncated), Name, Harness, Provider, Model, Updated (timestamp), State | E2.1.1 | Implemented |
| FR-TUI-003 | Keyboard navigation: j/k or ↓/↑ arrows to move selection, Enter to open selected session, s to cycle sort mode (updated_by → updated_at → name → repeat), / to activate filter prompt (placeholder), q to quit | E2.1.1 | Implemented |
| FR-TUI-004 | The footer SHALL display current sort mode and total session count; the header SHALL display filter status (if any filters active) | E2.1.1 | Implemented |
| FR-TUI-005 | Pressing Enter on a selected session SHALL call the `open` command and display output in a modal or status pane; error messages SHALL be shown in red with dismissal option | E2.1.1 | Implemented |
| FR-TUI-006 | The s key SHALL cycle through sort modes; the list SHALL re-render immediately with new sort order; current sort mode SHALL be highlighted in footer | E2.1.1 | Implemented |
| FR-TUI-007 | Pressing q SHALL cleanly exit the TUI and return to shell prompt; unsaved edits (if any) SHALL be discarded with confirmation prompt | E2.1.1 | Implemented |
| FR-TUI-008 | Initial TUI render SHALL complete in <100ms for typical session counts (up to 1000 sessions) | E2.1.1 | Implemented |
| FR-TUI-009 | The TUI details pane (if implemented) SHALL show full session metadata, allow editing of name and state, and save changes via session update API | E2.2.1 | Partial |

---

## FR-TRANSFER: Session Transfer Between Harnesses

| ID | Requirement | Traces To | Status |
|----|-------------|-----------|--------|
| FR-TRANSFER-001 | The `pheno-session transfer <session-id> --to-harness <target-harness> [--provider <p>] [--confirm]` command SHALL transfer session ownership to a target harness | E1.2.2 | Implemented |
| FR-TRANSFER-002 | Transfer operation SHALL: (a) snapshot source session state, (b) create new session in target harness via adapter, (c) mark source session as `paused`, (d) record audit entry | E1.2.2 | Implemented |
| FR-TRANSFER-003 | If --confirm flag is NOT passed, the command SHALL prompt for confirmation with details (source harness, target harness, model) before proceeding | E1.2.2 | Implemented |
| FR-TRANSFER-004 | Transfer SHALL fail with clear error if source session not found, target harness not supported, or target adapter returns error | E1.2.2 | Implemented |
| FR-TRANSFER-005 | On successful transfer, command SHALL print: "Transferred session <id> from <src> to <tgt>. Source marked paused. New session ID: <new-id>" | E1.2.2 | Implemented |

---

## FR-SITBACK: Autonomous Orchestration & Monitoring

| ID | Requirement | Traces To | Status |
|----|-------------|-----------|--------|
| FR-SITBACK-001 | The `pheno-session sitback [--profile <profile>]` command SHALL launch SITBACK orchestration with profile: `light` (monitoring only), `medium` (audit + monitoring), `full` (autonomous actions) | E3.1 | Implemented |
| FR-SITBACK-002 | **Light Profile**: Read-only monitoring; discovers running harnesses, samples session state every 5s, prints summary (total sessions, running agents, harness distribution), no mutations | E3.1.1 | Implemented |
| FR-SITBACK-003 | **Medium Profile**: Audit + monitoring; calls orchestrator.AuditReport(), logs summary to .agileplus/sitback.log, rotates log at 10MB, no automatic corrections applied | E3.1.2 | Implemented |
| FR-SITBACK-004 | **Full Profile**: Autonomous orchestration; retries failed tasks (3 attempts max, exponential backoff 1s→2s→4s, capped at 30s), rebalances sessions to less-loaded harnesses, kills/restarts stalled agents (no heartbeat >5s), broadcasts delegation messages | E3.1.3 | Implemented |
| FR-SITBACK-005 | SITBACK profiles SHALL run continuously until Ctrl+C; graceful shutdown SHALL complete in-flight actions before exiting | E3.1 | Implemented |
| FR-SITBACK-006 | All SITBACK actions (retry, rebalance, restart) SHALL record audit entries with reasoning and timestamp | E3.1.3 | Implemented |
| FR-SITBACK-007 | Failed SITBACK actions (e.g., adapter timeout) SHALL be logged but not block other orchestration work; orchestrator SHALL continue | E3.1.3 | Implemented |

---

## FR-AUDIT: Audit Reporting

| ID | Requirement | Traces To | Status |
|----|-------------|-----------|--------|
| FR-AUDIT-001 | The `pheno-session audit` or `pheno-session sitback --audit` command SHALL produce a JSON audit report and exit (no continuous monitoring) | E3.2 | Implemented |
| FR-AUDIT-002 | Audit report SHALL include: total_sessions (count), sessions_by_state (map of state → count), sessions_by_harness (map of harness → count), running_agents (list of PID/harness pairs), tasks (pending, completed, failed counts), messages_sent_24h (count), completion_states (distribution), timestamp (ISO 8601) | E3.2 | Implemented |
| FR-AUDIT-003 | Audit report generation SHALL complete in <2 seconds | E3.2 | Implemented |
| FR-AUDIT-004 | Audit report JSON SHALL be valid and parseable; output shall be suitable for piping to jq or other JSON tools | E3.2 | Implemented |
| FR-AUDIT-005 | Audit report is read-only (no side effects on sessions or tasks) | E3.2 | Implemented |

---

## FR-DELEGATION: Task Delegation & Message Routing

| ID | Requirement | Traces To | Status |
|----|-------------|-----------|--------|
| FR-DELEGATION-001 | The `pheno-session delegate --task <title> --agent <agent-id> [--priority <1-5>] [--description <desc>]` command SHALL create a Task record in SQLite with state `pending` | E3.3.1 | Implemented |
| FR-DELEGATION-002 | Task records SHALL contain: id (UUID), title (String), description (String), assigned_agent (String), state (pending\|running\|done\|failed), priority (1-5, default 3), created_at (Timestamp), updated_at (Timestamp) | E3.3.1 | Implemented |
| FR-DELEGATION-003 | On task creation, the MessagingService SHALL publish a message to the assigned agent via NATS or local message queue with topic `agileplus.tasks.<agent_id>` | E3.3.1 | Implemented |
| FR-DELEGATION-004 | If message delivery fails, the task SHALL remain in `pending` state and delivery SHALL be retried with exponential backoff (1s, 2s, 4s, ..., max 30s, max 10 attempts) | E3.3.1 | Implemented |
| FR-DELEGATION-005 | The `pheno-session status <task-id>` command SHALL print current task state and last update timestamp | E3.3.1 | Implemented |

---

## FR-SYNC: External Harness Sync

| ID | Requirement | Traces To | Status |
|----|-------------|-----------|--------|
| FR-SYNC-001 | The `pheno-session sync [--harness <h>]` command SHALL discover running harnesses, call ListSessions on each adapter, merge results into local SQLite store | E3.4.1 | Implemented |
| FR-SYNC-002 | If --harness filter is provided, only that harness is queried; if omitted, all discovered harnesses are queried in parallel with 5s timeout per harness | E3.4.1 | Implemented |
| FR-SYNC-003 | Conflict resolution: if a session exists both locally and remotely, remote wins if remote.updated_at > local.updated_at, else local wins | E3.4.1 | Implemented |
| FR-SYNC-004 | Duplicate detection: sessions are deduplicated by (harness, session_id) key; cross-harness duplicates are not merged | E3.4.1 | Implemented |
| FR-SYNC-005 | On sync completion, command SHALL print: "Synced <N> sessions: <new> new, <updated> updated, <deleted> deleted" | E3.4.1 | Implemented |
| FR-SYNC-006 | Sync operation is idempotent: running sync twice in succession SHALL not duplicate or corrupt data | E3.4.1 | Implemented |

---

## FR-ADAPTERS: Harness Adapter Pattern

| ID | Requirement | Traces To | Status |
|----|-------------|-----------|--------|
| FR-ADAPTERS-001 | All harness-specific logic SHALL be encapsulated in implementations of the `HarnessAdapter` trait with methods: `list_sessions(filter)`, `get_session(id)`, `start_session(params)`, `transfer_session(id, to_harness, params)`, `open_session(id, open_in)` | E4.1 | Implemented |
| FR-ADAPTERS-002 | Adapters SHALL be registered in a registry at startup; adapters are selected by harness name (e.g., "forge", "cursor") during operations | E4.1 | Implemented |
| FR-ADAPTERS-003 | Adapters MAY return `NotImplemented` for methods that are not supported by the harness; callers SHALL handle this gracefully with user-friendly error messages | E4.1 | Implemented |
| FR-ADAPTERS-004 | The Forge adapter SHALL provide a reference implementation for all trait methods with reasonable placeholder behavior | E4.1 | Implemented |
| FR-ADAPTERS-005 | The Codex, Cursor, Claude, Droid adapters MAY be stubs initially and completed incrementally without blocking core CLI functionality | E4.1 | Implemented |

---

## FR-BRIDGE: Integration with Thegent SITBACK

| ID | Requirement | Traces To | Status |
|----|-------------|-----------|--------|
| FR-BRIDGE-001 | The `pheno-session bridge [--thegent <path>] [--profile <profile>]` command SHALL spawn a bridge process that integrates pheno-session orchestration with thegent's SITBACK | E6.1 | Implemented |
| FR-BRIDGE-002 | If --thegent path is not provided, bridge SHALL auto-discover thegent via PATH lookup or common installation paths (e.g., ~/.cargo/bin/thegent, /usr/local/bin/thegent) | E6.1 | Implemented |
| FR-BRIDGE-003 | Bridge process SHALL send heartbeats to thegent every 2 seconds; if heartbeat fails for >10 seconds, bridge SHALL log error and attempt reconnection | E6.1 | Implemented |
| FR-BRIDGE-004 | Tasks delegated to agents by thegent SHALL be routed through pheno-session orchestrator to appropriate harness | E6.1 | Implemented |
| FR-BRIDGE-005 | Bridge process SHALL cleanly shut down on SIGTERM with 10-second timeout before force-kill | E6.1 | Implemented |

---

## FR-MONITORING: Health & Telemetry

| ID | Requirement | Traces To | Status |
|----|-------------|-----------|--------|
| FR-MONITORING-001 | The system SHALL maintain a heartbeat service that probes all registered harness adapters every 5 seconds; probe results (success/failure, latency) SHALL be logged | E6.2 | Implemented |
| FR-MONITORING-002 | Metrics exposed (via OpenTelemetry or stdout): total_sessions (gauge), active_sessions (gauge), closed_sessions (gauge), tasks_completed_24h (counter), adapter_latency_p99 (histogram), adapter_error_rate (counter) | E6.2 | Implemented |
| FR-MONITORING-003 | Health check endpoint (if HTTP API implemented): GET /health SHALL return `{ "status": "healthy"|"degraded"|"unhealthy", "timestamp": "...", "components": { ... } }` | E6.2 | Partial |
| FR-MONITORING-004 | Adapter heartbeat failures SHALL be retried with exponential backoff (1s, 2s, 4s, ..., max 30s) without blocking other operations | E6.2 | Implemented |
| FR-MONITORING-005 | All telemetry data SHALL be exportable in Prometheus text format (if telemetry subsystem implemented) | E6.2 | Partial |

---

## FR-CLI: Command-Line Interface

| ID | Requirement | Traces To | Status |
|----|-------------|-----------|--------|
| FR-CLI-001 | The CLI entry point SHALL be the `pheno-session` binary built via `go build -o pheno-session ./...` | E1, E2 | Implemented |
| FR-CLI-002 | All commands SHALL support global flags: `--config <path>` (config file), `--verbose` (verbose logging) | E1, E2 | Implemented |
| FR-CLI-003 | The CLI SHALL use Cobra for command routing and automatic help generation; `pheno-session --help` SHALL list all available commands | E1, E2 | Implemented |
| FR-CLI-004 | All commands SHALL exit with code 0 on success, non-zero on error; errors SHALL be printed to stderr | E1, E2 | Implemented |
| FR-CLI-005 | The `--verbose` flag SHALL increase logging verbosity to DEBUG level; logs SHALL be printed to stderr with timestamps | E1, E2 | Implemented |

---

## FR-PERFORMANCE: Performance & Scalability

| ID | Requirement | Traces To | Status |
|----|-------------|-----------|--------|
| FR-PERF-001 | List operations SHALL complete in <500ms for workloads up to 1000 sessions | E1 | Implemented |
| FR-PERF-002 | SQLite queries SHALL use indexed lookups on frequently-filtered fields (harness, provider, updated_at) | E5.1 | Implemented |
| FR-PERF-003 | TUI initial render SHALL complete in <100ms even with 1000 sessions; pagination SHALL limit rows per screen to 50 | E2.1 | Implemented |
| FR-PERF-004 | Harness adapter calls (list, get, start) MAY timeout after 10 seconds; timeout is recoverable and logged | E4.1 | Implemented |

---

## FR-RELIABILITY: Durability & Error Handling

| ID | Requirement | Traces To | Status |
|----|-------------|-----------|--------|
| FR-RELIABILITY-001 | All mutations (create, update, delete, transfer) SHALL be atomic with respect to SQLite (single transaction); failed transaction SHALL roll back with no partial updates | E5.1 | Implemented |
| FR-RELIABILITY-002 | All errors SHALL include context (operation, entity ID, underlying cause) and be returned to the user with actionable messages | E1, E2 | Implemented |
| FR-RELIABILITY-003 | Network errors during harness adapter calls SHALL not crash the process; adapters SHALL log and return retriable errors | E4.1 | Implemented |
| FR-RELIABILITY-004 | Graceful shutdown: on SIGTERM, in-flight operations SHALL complete within 10 seconds; if timeout, process exits with status 1 | E3.1 | Implemented |

---

## Traceability Matrix

| Epic | FR Count | Implementation Status |
|------|----------|----------------------|
| E1: Session Management | 24 | Implemented |
| E2: Interactive TUI | 9 | Implemented (partial: E2.2) |
| E3: SITBACK Orchestration | 15 | Implemented |
| E4: Adapter Architecture | 5 | Implemented |
| E5: Storage & Durability | 7 | Implemented |
| E6: System Integration | 11 | Implemented (partial: E6.2) |
| **Total** | **71** | **68 Implemented, 3 Partial** |
