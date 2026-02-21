# Thegent: Unified Design Decisions and Contracts

**Date:** 2026-02-14
**Status:** Authoritative
**Scope:** Complete extraction of contracts, architecture, orchestration, and implementation gaps

---

## Table of Contents

1. [Contracts & Standards](#contracts--standards)
2. [Architecture & Layers](#architecture--layers)
3. [Orchestration Design](#orchestration-design)
4. [Implementation Items](#implementation-items)
5. [Identified Gaps & Remediation](#identified-gaps--remediation)

---

## Contracts & Standards

### 1.1 Contract Authority

**Source:** `docs/contracts/CONTRACT_AUTHORITY.md`

#### Purpose
Single source of truth for structured output contracts. All agent outputs, XML protocols, and provider-specific formats normalize to the canonical schema.

#### Contract Registry

| Contract ID | Version | Description | Compatibility |
|-------------|---------|-------------|---------------|
| csm | csm-v1 | Canonical Structured Message (unified schema) | task-tool-18, zen-rich-v1 |
| task-tool | task-tool-18 | Task-tool 18-tag XML (snake_case) | csm-v1 |
| zen | zen-rich-v1 | Zen rich protocol (status, progress, actions, files) | csm-v1 |

#### Canonical Schema (CSM v1)

All agent outputs normalize to `CanonicalStructuredMessage`:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| task_id | str | No | Task identifier |
| run_id | str | No | Run correlation ID |
| chunk_id | str | No | Chunk identifier |
| status | enum | Yes | pending, in_progress, completed, failed, blocked, cancelled |
| phase | enum | No | planner, operator, reviewer, unknown |
| progress | float | No | 0.0–1.0 |
| objective | str | No | Task objective |
| summary | str | No | Condensed summary |
| actions_completed | list[str] | No | Completed action list |
| issues | list[str] | No | Issues encountered |
| next_steps | list[str] | No | Recommended next steps |
| evidence_set_hash | str | No | Governance evidence hash |
| policy_gate_id | str | No | Policy gate identifier |
| decision_reason_code | str | No | Decision rationale code |
| schema_version | str | Yes | Always "csm-v1" |
| source_contract | str | No | Original contract (task-tool-18, zen-rich-v1, etc.) |

#### Versioning Policy

- **contract_id**: Logical contract (csm, task-tool, zen)
- **version**: Semantic version string (e.g., csm-v1, task-tool-18)
- **compatible_with**: Versions that can be normalized to this contract
- **deprecated**: If true, do not use for new integrations

**Migration Strategy:** Use dual-read/dual-write windows when upgrading. Never remove a version without a deprecation period.

#### Adapter Contract

Provider adapters implement `OutputAdapter`:

- **provider**: Provider identifier (copilot, gemini, codex, claude, etc.)
- **normalize(raw, context) -> AdapterResult**: Convert raw output to CSM

**Requirements:**
- Return `AdapterResult` with `csm` and `confidence` (0.0–1.0)
- Populate `parse_errors` on partial failure
- Set `source_contract` when known

#### Implementation Location

- **Registry**: `src/thegent/contracts/registry.py`
- **CSM schema**: `src/thegent/contracts/csm.py`
- **Adapters**: `src/thegent/contracts/adapters.py`
- **Usage**: `from thegent.contracts import get_registry, CanonicalStructuredMessage, normalize_output`

---

### 1.2 Fallback Control Plane

**Source:** `docs/contracts/FALLBACK_POLICY.md`

#### Purpose
When agent output cannot be normalized via a provider adapter (XML, JSON, etc.), thegent falls back to plain-text extraction. This defines the **fallback control plane**: policy, observability, and guardrails.

#### Policy Configuration

| Config | Default | Description |
|--------|---------|--------------|
| `THGENT_NORMALIZATION_POLICY_ALLOW_FALLBACK` | true | Allow plain-text fallback when adapter fails |
| `THGENT_NORMALIZATION_POLICY_MIN_CONFIDENCE` | 0.4 | Minimum confidence threshold; below triggers policy violation |
| `THGENT_NORMALIZATION_POLICY_MAX_FALLBACK_RATE` | 0.3 | Max global fallback rate (30%); above triggers policy violation |
| `THGENT_NORMALIZATION_POLICY_STRICT_PROVIDERS` | "" | Comma-separated providers that must never use fallback |

#### Fallback Flow

1. **Adapter attempt**: Provider adapter (e.g., XMLOutputAdapter for gemini) normalizes raw output
2. **On failure**: If adapter throws or returns parse_errors, fallback is considered
3. **Fallback**: `extract_condensed()` produces minimal CSM with `source_contract="fallback-plain"`, confidence 0.3–0.5
4. **Policy evaluation**: `evaluate_fallback()` checks strict providers, confidence, global fallback rate
5. **Telemetry**: `ContractTelemetry.record_normalization()` records fallback events for observability

#### MCP and CLI Parity

Both MCP `thegent_run` and CLI `thegent run` use the same `run_with_failover` path:

- Calls `normalize_output(agent, raw)` after each run
- Evaluates `evaluate_fallback()` with config-driven `FallbackPolicy`
- Records to `ContractTelemetry` for drift detection

**Key Decision:** MCP fallback policy = same as CLI; no separate MCP-specific policy.

#### Observability

- **ContractTelemetry**: Tracks fallback rate per provider and globally
- **Drift detection**: `analyze_drift()` flags significant fallback rate increases
- **Session dir**: Telemetry stored under `THGENT_SESSION_DIR` (default `.thegent/sessions`)

#### Guardrails

| Guardrail | Behavior |
|-----------|----------|
| Strict provider | If provider in `strict_providers`, fallback is blocked; `SemanticValidationError` raised when `allow_fallback=False` |
| Confidence threshold | Below `min_confidence_threshold` → policy violation logged |
| Max fallback rate | Global rate > `max_fallback_rate` → policy violation logged |
| Parse error class | `parse_truncated` from `extract_condensed_validated` → adapter result returned (no fallback to COMPLETED) |

#### Implementation Location

- **Policy**: `src/thegent/contracts/policy.py` — `FallbackPolicy`, `evaluate_fallback`
- **Config**: `src/thegent/config.py` — `normalization_policy_*`
- **Telemetry**: `src/thegent/contracts/telemetry.py` — `ContractTelemetry`
- **Usage**: `src/thegent/cli_impl.py` — `run_with_failover`

---

## Architecture & Layers

### 2.1 Architecture Layer Boundaries

**Source:** `docs/ARCHITECTURE_LAYERS.md` | Enforced by `scripts/check_boundaries.py` in CI

#### Layer Dependency Graph

```
config          (no deps)
output_parser   (no deps)
contracts       → config
models          → config, contracts
execution       → config, contracts, models
agents          → config, contracts, models
operations      → config
orchestration_modes (no deps)

cli_impl        → config, contracts, models, execution, agents, output_parser, operations, orchestration_modes
cli             → config, contracts, models, execution, agents, output_parser, cli_impl, operations, orchestration_modes
mcp_server      → config, contracts, models, execution, agents, output_parser, operations, orchestration_modes, cli_impl
main            → config, contracts, models, execution, agents, cli_impl, cli
```

#### Layer Responsibilities

| Layer | Responsibility | Constraints |
|-------|-----------------|-------------|
| **config** | Configuration schema and management | No dependencies; foundational |
| **output_parser** | Raw output parsing and normalization | No dependencies; used by contracts |
| **contracts** | Schema, adapters, validation, policy, telemetry | May use config only; no agents/execution |
| **models** | Model management and routing | May use config, contracts |
| **execution** | Run lifecycle, registry, checkpoint management | May use config, contracts, models |
| **agents** | Runners, registry, resilience, state_machine | May use config, contracts, models |
| **operations** | Operation definitions and discovery | May use config only |
| **orchestration_modes** | Multi-agent orchestration patterns | No dependencies |
| **cli_impl** | Shared CLI/MCP implementation | May use all core layers |
| **mcp_server** | MCP tools/resources | May use cli_impl and core layers |
| **cli** | CLI interface | May use all except mcp_server |

#### Verification

```bash
python scripts/check_boundaries.py
# or
pytest tests/test_ci_architecture.py -v
```

**Enforcement:** CI pipeline blocks commits that violate dependencies.

---

### 2.2 Design Decisions by Layer

#### Contracts Layer

**Decision 1: Single Contract Authority**
- **Rationale**: Prevent adapter fragmentation and schema drift
- **Implementation**: `ContractAuthority` in `contracts/registry.py` is SOT
- **Enforcement**: All adapters must register with authority; unregistered contracts cause `ContractNotFoundError`

**Decision 2: Fallback as Policy, Not Exception**
- **Rationale**: Graceful degradation with observability, not silent failures
- **Implementation**: `FallbackPolicy` evaluates confidence, provider restrictions, global fallback rate
- **Enforcement**: Policy violations logged; high fallback rates trigger alerts via `ContractTelemetry`

**Decision 3: Provider Adapters are Pluggable**
- **Rationale**: Support multiple providers (copilot, gemini, codex, claude, etc.) without code duplication
- **Implementation**: `OutputAdapter` interface; providers register adapters in `ContractRegistry`
- **Enforcement**: New providers require adapter implementation in `contracts/adapters.py`

#### Execution Layer

**Decision 4: Run Registry is Immutable**
- **Rationale**: Audit trail and recovery; no silent state changes
- **Implementation**: `RunRegistry` writes to `run_registry.jsonl`; append-only
- **Enforcement**: No in-place edits; new events create new lines

**Decision 5: Checkpoint Registry Includes Continuity**
- **Rationale**: Support pause/resume workflows and owner handoff
- **Implementation**: `CheckpointRegistry` stores `run_id`, `phase`, `progress`, `continuity_snapshot`
- **Enforcement**: Resuming from checkpoint validates frontier is ready (no duplicate dispatch)

---

## Orchestration Design

### 3.1 Multi-Agent Orchestration Modes

**Source:** `docs/MULTI_AGENT_MODE_CATALOG.md`

#### Formal Mode Definitions

| Mode | Description | Phases | Use Case | Risk | Implementation |
|------|-------------|--------|----------|------|-----------------|
| **sequential_delegation** | Step-wise specialization: each agent hands off to next in sequence | planner → operator → ... | Multi-step workflows where each step requires different expertise | medium | DAG `depends_on`; handoff via task completion |
| **parallel_consensus** | Independent solution synthesis: multiple agents run in parallel, result aggregated | operator, operator, ... | Critical tasks requiring quorum or consensus (e.g., low-confidence escalation) | low | DAG task `quorum` field; multi-agent runs with leader/follower arbitration |
| **review_loop** | Planner/Operator/Reviewer enforcement: explicit phase gates with approval | planner → operator → reviewer | Governance-heavy workflows with explicit review gates | high | CSMPhase.REVIEWER; governance gates; `decision_reason_code` validation |

#### Mode Selection Policy

| Condition | Suggested Mode |
|-----------|----------------|
| confidence < 0.5 | parallel_consensus |
| risk = high, urgency ≠ critical | review_loop |
| default | sequential_delegation |

**Design Rationale:**
- Low confidence → need multiple opinions (consensus)
- High risk + time to deliberate → explicit review gates
- Standard case → sequential specialization (planner → operator → reviewer if needed)

#### Discovery Interfaces

| Interface | Command | MCP Tool | Resource | Description |
|-----------|---------|----------|----------|-------------|
| **CLI** | `thegent modes` or `thegent modes --format json` | — | — | List all modes; JSON output |
| **MCP Tool** | — | `thegent_list_modes` | — | Machine-readable mode catalog |
| **MCP Resource** | — | — | `thegent://modes` or `thegent://modes{?mode}` | RESTful resource access |
| **Meta Discovery** | — | — | `thegent://meta` | Meta resource includes `orchestration_modes` list |

#### Implementation Location

- **Catalog**: `src/thegent/orchestration_modes.py`
- **CLI**: `thegent modes` command (main.py)
- **MCP**: `thegent_list_modes` tool, `thegent://modes` resource

---

### 3.2 State-Aware Orchestration

**Source:** `docs/STATE_AWARE_ORCHESTRATION_DESIGN.md`

#### Current State

| Component | Location | Purpose | Status |
|-----------|----------|---------|--------|
| **RunRegistry** | `execution.py` | Persists run start/finish/feedback to `run_registry.jsonl`; hash chaining for audit | ✓ Implemented |
| **CheckpointRegistry** | `execution.py` | Persists DAG checkpoints (reason, dag_content, owner) to `checkpoint_registry.jsonl` | ✓ Implemented |
| **session_dir** | `.thegent/sessions` | Root for run logs, registry, checkpoints | ✓ Implemented |
| **dag checkpoint** | CLI | `thegent dag checkpoint`, `thegent dag rollback`, `thegent dag checkpoints` | ✓ Implemented |
| **Auto-checkpoint** | CLI | On DAG status change (terminal task), creates checkpoint | ✓ Implemented |

**Gap:** Run-level pause/resume, continuity packets, and explicit interruption semantics are not implemented.

#### Target Capabilities

##### 3.2.1 State Persistence for Multi-Step

- **Run state**: Extend RunRegistry to track `running | paused | completed | failed`
- **Checkpoint format**: Add `run_id`, `phase`, `progress`, `continuity_snapshot` to checkpoint schema
- **Resume from checkpoint**: `thegent run --resume-from <checkpoint_id>` restores context and continues

##### 3.2.2 Interruption / Resume

- **Pause**: Operator or policy triggers pause; run state → `paused`; checkpoint created with continuity packet
- **Resume**: `thegent run --resume <run_id>` or `thegent dag resume --run <run_id>` restores from last checkpoint
- **Idempotent semantics**: Resume only from valid ready frontier (no duplicate dispatch)

##### 3.2.3 Continuity Packets

Structured handoff format for owner transition:

```json
{
  "continuity_packet_id": "cp_abc123",
  "run_id": "run_xyz",
  "created_at_utc": "2026-02-14T12:00:00Z",
  "phase": "operator",
  "progress": 0.65,
  "summary": "Completed steps 1–3; step 4 in progress",
  "next_action": "resume_ready_frontier",
  "unresolved_risks": [],
  "owner": "alice",
  "handoff_to": "bob"
}
```

#### Phased Implementation Plan

##### Phase 1: Run State Extension (Low Effort)

- Add `run_state` to RunRegistry events: `running`, `paused`, `completed`, `failed`
- Add `register_pause(run_id, reason, continuity_snapshot)` and `register_resume(run_id)`
- No CLI changes yet; prepare data model

##### Phase 2: Continuity Packet Schema

- Define `ContinuityPacket` dataclass in `execution.py`
- Store in checkpoint or new `continuity_registry.jsonl`
- `thegent dag checkpoint` optionally emits continuity packet

##### Phase 3: Pause / Resume CLI

- `thegent run --pause` (when running) → create checkpoint + continuity packet, set run_state=paused
- `thegent run --resume <run_id>` → load checkpoint, restore context, continue dispatch
- MCP: `thegent_pause_run(session_id)`, `thegent_resume_run(session_id)`

##### Phase 4: MCP Context Integration

- When FastMCP supports `ctx.set_state`/`ctx.get_state`, wire run state and continuity snapshot
- Progress+confidence snapshots in `ctx.report_progress()` payload

#### Interface Sketch

```python
# execution.py extensions
class RunState(str, Enum):
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

def register_pause(self, run_id: str, reason: str, continuity: dict) -> None: ...
def register_resume(self, run_id: str) -> None: ...
def get_run_state(self, run_id: str) -> RunState | None: ...
```

---

## Implementation Items

### 4.1 Core Orchestration Features

**Source:** `docs/ORCHESTRATION.md`

#### 1. Unified Execution Lifecycle (Phase 1)
- **Run IDs & Correlation**: Every action tracked with unique `run_id` and optional `correlation_id`
- **Run Registry**: Persistent JSONL store of all execution metadata (start/end events, durations, exit codes)
- **Telemetry Contracts**: Standardized fields for agent, model, lane, and confidence

#### 2. Dependency-aware DAG Orchestration (Phase 1 & 2)
- **Routing Engine**: Executes tasks in parallel based on dependencies
- **Quorum & Arbitration**: Supports multi-agent consensus for critical tasks
- **Confidence-aware Routing**: Automatically escalates low-confidence tasks to 2-agent quorum
- **Evidence Capture**: Every completed task links to execution record (session ID)

#### 3. Resilience & Self-healing (Phase 2 & 5)
- **Adaptive Retries**: Exponential backoff for transient failures (rate limits)
- **Circuit Breakers**: Prevents cascading failures by isolating unstable agents or models
- **Checkpoint/Rollback**: Immutable point-in-time snapshots of DAG state
- **Auto-Reconciliation**: Recovers from crashes by syncing DAG state with live OS processes on restart

#### 4. Governance & Security (Phase 3)
- **Policy Engine**: Enforces rules based on environment (trust score gates in production)
- **Signed Artifacts**: Cryptographic signatures ensure integrity of run registry
- **Immutable Audit Trail**: Verifiable history of orchestration actions
- **Governance Overrides**: Authorized bypass for critical recovery with mandatory rationale

#### 5. Operator Cockpit & UX (Phase 4)
- **Cockpit Summary**: High-level overview of session health and resource states
- **Decision Replay**: Detailed rationales stored for every execution failure
- **One-click Fallbacks**: Simplified recovery through automated agent swapping
- **Feedback Loops**: Operator-driven confidence calibration

#### CLI Command Reference

| Command | Description |
|---------|-------------|
| `thegent cockpit` | High-level orchestration health summary |
| `thegent history list` | View recent execution runs |
| `thegent history verify` | Audit registry integrity |
| `thegent dag run` | Execute DAG with auto-reconciliation |
| `thegent dag sync --watch` | Health-monitoring loop for active tasks |
| `thegent dag checkpoint` | Create state snapshot |
| `thegent benchmark` | Latency and success rate metrics |
| `thegent archive` | Cleanup old session data |

---

### 4.2 Contract Implementation Items

**Source:** `docs/contracts/CONTRACT_AUTHORITY.md`, `docs/contracts/FALLBACK_POLICY.md`

#### Contract Registry Implementation

| Task | Location | Status |
|------|----------|--------|
| Contract ID + Version Management | `src/thegent/contracts/registry.py` | Implement `ContractRegistry` class with contract_id, version, compatibility_with, deprecated fields |
| CSM Schema Definition | `src/thegent/contracts/csm.py` | Implement `CanonicalStructuredMessage` dataclass with all required fields |
| Adapter Interface | `src/thegent/contracts/adapters.py` | Implement `OutputAdapter` base class; providers override `normalize(raw, context)` |
| Provider Adapters | `src/thegent/contracts/adapters.py` | Implement adapters for copilot, gemini, codex, claude; register with ContractRegistry |
| Migration Utilities | `src/thegent/contracts/migration.py` | Dual-read/dual-write window for version upgrades; deprecation tracking |

#### Fallback Policy Implementation

| Task | Location | Status |
|------|----------|--------|
| FallbackPolicy Dataclass | `src/thegent/contracts/policy.py` | Define config-driven policy with allow_fallback, min_confidence, max_fallback_rate, strict_providers |
| evaluate_fallback() Function | `src/thegent/contracts/policy.py` | Implement policy evaluation logic; raise `SemanticValidationError` on violation |
| ContractTelemetry | `src/thegent/contracts/telemetry.py` | Track fallback rate per provider and globally; implement `analyze_drift()` for drift detection |
| run_with_failover() Integration | `src/thegent/cli_impl.py` | Wire normalize_output() and evaluate_fallback() into run path; record to telemetry |
| Config Environment Variables | `src/thegent/config.py` | Expose `THGENT_NORMALIZATION_POLICY_*` environment variables |

---

## Identified Gaps & Remediation

### 5.1 Contract & Parser Gaps

**Source:** `docs/GAP_ANALYSIS_AND_REMEDIATION.md` | Gap IDs: G-RV-01 through G-RV-08

#### G-RV-01: Contract Registry (Not Done)

**Issue:** No authoritative contract registry.

**Remediation:** Define contract_id, contract_version, compatibility matrix, migration windows.

**Implementation:**
1. Create `ContractRegistry` in `src/thegent/contracts/registry.py`
2. Register canonical contracts: csm-v1, task-tool-18, zen-rich-v1
3. Document compatibility matrix

#### G-RV-02: Canonical Message Normalization (Not Done)

**Issue:** task-tool-18 and Zen rich protocol lack unified normalization.

**Remediation:** Map both formats to canonical schema (CSM).

**Implementation:**
1. Implement `CanonicalStructuredMessage` dataclass
2. Create adapters for task-tool-18 → CSM, zen-rich-v1 → CSM
3. Test bidirectional normalization

#### G-RV-03: Parser Hardening (Done)

**Status:** Implemented: IncrementalXMLParser (get_partial_state), TruncatedParseError/InvalidTagError, ParseResult, extract_condensed_validated.

#### G-RV-04: Semantic Validation (Done)

**Status:** Added: FAILED/IN_PROGRESS invariants, phase-aware (PLANNER/OPERATOR/REVIEWER) validators.

#### G-RV-05: Provider Adapter Layer (Partial)

**Issue:** Adapters for copilot/gemini/codex/claude incomplete.

**Remediation:** Build full adapter contracts for all supported providers.

**Implementation:**
1. Implement copilot adapter (handles Azure OpenAI output format)
2. Implement gemini adapter (handles JSON + XML mixed output)
3. Implement codex adapter (legacy OpenAI format)
4. Implement claude adapter (handles Anthropic structured output)
5. Register all adapters with ContractRegistry

#### G-RV-06: Fallback Control Plane (Done)

**Status:** `docs/contracts/FALLBACK_POLICY.md` complete; policy, observability, guardrails documented; MCP=CLI parity established.

#### G-RV-07: Contract Telemetry (Done)

**Status:** Emit schema.drift.structural / schema.drift.semantic events; get_drift_budget_status; observe drift --structural-budget / --semantic-budget.

#### G-RV-08: Migration and Rollout (Not Done)

**Issue:** No contract upgrade playbook.

**Remediation:** Document canary, dual mode, rollback steps.

**Implementation:**
1. Create `docs/contracts/MIGRATION_PLAYBOOK.md` with upgrade steps
2. Implement dual-read window (old + new parsers running simultaneously)
3. Implement dual-write window (write to both old + new storage)
4. Define rollback criteria and procedure
5. Document deprecation timeline (e.g., 90-day support for old contract)

---

### 5.2 FastMCP Implementation Gaps

**Source:** `docs/GAP_ANALYSIS_AND_REMEDIATION.md` | Gap IDs: G-FM-01 through G-FM-07

#### G-FM-01: Phase 5: Production Readiness (Not Done)

**Issue:** Auth, stateless_http, Redis backend, session state store, deployment guide missing.

**Remediation:**

1. Implement OAuth + Bearer token auth for MCP server
2. Configure stateless HTTP mode (no in-process state)
3. Integrate Redis backend for session/cache storage
4. Create `docs/FASTMCP_DEPLOYMENT_GUIDE.md` with K8s, Docker Compose examples

#### G-FM-02: Additional Research Tasks (Not Done)

**Issue:** Research docs not created.

**Remediation:** Execute thegent bg cursor-agent for:

1. `docs/research/FASTMCP_STORAGE_EVENTSTORE.md` — Event sourcing patterns for MCP state
2. `docs/research/FASTMCP_MIDDLEWARE.md` — Custom middleware for logging, auth, rate limiting
3. `docs/research/FASTMCP_SAMPLING_TELEMETRY.md` — Sampling strategies for high-volume telemetry

#### G-FM-03: Verification Runbook (Done)

**Status:** `docs/VERIFICATION_RUNBOOK.md` exists — checklist for server, tools, resources, prompts, CLI parity.

#### G-FM-04: Icons and UX Hints (Optional → Required)

**Issue:** Tool icons/hints not implemented.

**Remediation:** When FastMCP supports icon/hint API, add to:
- `thegent_run`, `thegent_bg`, `thegent_stop`, `thegent_logs`, `thegent_ps`

#### G-FM-05: Testing Strategy (Not Complete)

**Issue:** Unit, contract, integration, chaos, load, timeout tests incomplete.

**Remediation:** Implement per-tool:

1. **Unit tests**: Mock FastMCP context, test tool logic in isolation
2. **Contract tests**: Verify ToolResult shape, structured_content format
3. **Integration tests**: Real MCP server, real execution context
4. **Chaos tests**: Inject failures (timeout, malformed input, auth failure)
5. **Load tests**: Concurrent tool calls, rate limiting
6. **Timeout tests**: Verify graceful timeout handling

#### G-FM-06: Phase Checklist (Not Verified)

**Issue:** Error messages, tool descriptions, ToolResult shape not audited.

**Remediation:**

1. Audit error messages for actionability (include remediation hints)
2. Audit tool descriptions for agent clarity (action-oriented, not descriptive)
3. Verify all ToolResult return structured_content + meta.execution_time_ms
4. Verify input validation covers all parameter constraints

#### G-FM-07: CLI Single Source of Truth (Audit Needed)

**Issue:** No Makefile/scripts bypass; all docs use thegent run/bg/etc.

**Remediation:**

1. Audit all entry points (CLI, MCP, scripts)
2. Ensure no Makefile targets bypass CLI
3. Update all docs to use thegent commands (no direct script invocation)

---

### 5.3 Contract Authority Gaps

**Source:** `docs/GAP_ANALYSIS_AND_REMEDIATION.md` | Gap IDs: G-KD-01

#### G-KD-01: Contract Authority (Not Done)

**Issue:** No authoritative contract source with contract_id + version + adapter.

**Remediation:**

1. Create `docs/contracts/CONTRACT_AUTHORITY.md` (Status: Done)
2. Implement `ContractRegistry` with registration API
3. For each provider, implement and register adapter
4. Define migration policy for deprecated contracts

**Implementation:**
- Location: `src/thegent/contracts/registry.py`, `src/thegent/contracts/adapters.py`
- Status: CONTRACT_AUTHORITY.md published; registry implementation in progress

---

### 5.4 State-Aware Orchestration Gaps

**Source:** `docs/GAP_ANALYSIS_AND_REMEDIATION.md` | Gap ID: G-KD-03

#### G-KD-03: State-Aware Orchestration (Partial)

**Issue:** Pause/resume, continuity packets not implemented.

**Remediation:** Phased implementation (Phases 1–4 per section 3.2)

**P1 (Immediate):**
- Add `run_state` to RunRegistry: RUNNING, PAUSED, COMPLETED, FAILED
- Implement `register_pause()`, `register_resume()`, `get_run_state()`

**P2 (Next):**
- Define `ContinuityPacket` dataclass
- Store in `continuity_registry.jsonl`

**P3 (Following):**
- CLI: `thegent run --pause`, `thegent run --resume <run_id>`
- MCP: `thegent_pause_run()`, `thegent_resume_run()`

**P4 (Hardening):**
- Wire to FastMCP `ctx.set_state()`, `ctx.get_state()`
- Snapshot progress + confidence

---

### 5.5 Multi-Agent Mode Gaps

**Source:** `docs/GAP_ANALYSIS_AND_REMEDIATION.md` | Gap ID: G-KD-04

#### G-KD-04: Multi-Agent Mode Catalog (Done)

**Status:** Complete

- Catalog: `src/thegent/orchestration_modes.py`
- CLI: `thegent modes`
- MCP: `thegent_list_modes`, `thegent://modes`
- Docs: `docs/MULTI_AGENT_MODE_CATALOG.md`

---

### 5.6 Architecture Guardrails Gaps

**Source:** `docs/GAP_ANALYSIS_AND_REMEDIATION.md` | Gap ID: G-KD-05

#### G-KD-05: Architecture Guardrails in CI (Done)

**Status:** Complete

- Enforcement: `scripts/check_boundaries.py`, `tests/test_ci_architecture.py`
- Docs: `docs/ARCHITECTURE_LAYERS.md`
- Moved: `state_machine` moved to `agents` layer

---

### 5.7 CLIProxy & Provider Parity Gaps

**Source:** `docs/GAP_ANALYSIS_AND_REMEDIATION.md` | Gap IDs: G-CP-01 through G-CP-03

#### G-CP-01: Cursor Phase 2 (Not Done)

**Issue:** No Cursor dedicated block (token provider, refresh, rebindExecutors).

**Remediation:** Implement Phase 2 in cliproxyapi-plusplus:
- `cursor:` schema definition
- Token provider integration
- Cursor API refresh mechanism
- Executor rebinding

#### G-CP-02: Phase 1 Foundation (Unclear)

**Issue:** Cursor/MiniMax config, patch unclear.

**Remediation:**
1. Verify patch: `patches/cursor-minimax-channels.patch`
2. Test patch application
3. Regenerate if needed

#### G-CP-03: Provider Parity (Cursor Incomplete)

**Issue:** Cursor lacks full parity with Kiro (token-file, cursor-api, refresh).

**Remediation:** Achieve full parity:
- token-file support
- cursor-api integration
- Refresh mechanism

---

### 5.8 Distributed Model Routing Gaps

**Source:** `docs/GAP_ANALYSIS_AND_REMEDIATION.md` | Gap IDs: G-DM-01 through G-DM-04

**Status:** All items marked Done

- Dynamic scraping adapters implemented (gemini, claude, proxy, cursor/copilot)
- list_models_impl uses scraped catalog with fallback
- list-models --by-model unified view
- MCP thegent_list_models returns scraped catalog

---

### 5.9 Discovery Gaps

**Source:** `docs/GAP_ANALYSIS_AND_REMEDIATION.md` | Gap IDs: G-DS-01 through G-DS-05

#### G-DS-01: Schema Discovery Consolidation (Done)

**Status:** Verify `thegent://meta` exposes route_schema_version, output_parser_schema_version, health schema.

#### G-DS-02: Contract Introspection (Done)

**Status:** Verify `thegent models contract`, resolve-model-route, session-contracts surfaces.

#### G-DS-03: Health Payload Discovery (Done)

**Status:** Verify gate/report/trend schema_version, payload_type in all outputs.

#### G-DS-04: Provider Capability Discovery (Partial)

**Issue:** list-models --by-model incomplete.

**Remediation:** Ensure list-models --by-model shows model → [providers] mapping.

#### G-DS-05: MCP Resource Discovery (Verify)

**Issue:** MCP resources not verified.

**Remediation:** Audit all resources:
- `thegent://meta`
- `thegent://sessions`
- `thegent://models`
- `thegent://dag`
- `thegent://modes`
- `thegent://operations`

---

### 5.10 Governance & Policy Gaps

**Source:** `docs/GAP_ANALYSIS_AND_REMEDIATION.md` | Gap IDs: G-GP-01 through G-GP-09

| ID | Item | Status | Implementation |
|----|------|--------|-----------------|
| G-GP-01 | OPA integration | In plan | Implement OPA as policy decision point per WP-3001 |
| G-GP-02 | NeMo Guardrails | In plan | Input rails for schema/safety before OPA |
| G-GP-03 | Audit trail hash chain | In plan | Implement per WP-3004 |
| G-GP-04 | Circuit breakers | Partial | WP-2003; verify per-subsystem config |
| G-GP-05 | HITL patterns | In plan | WP-3008, WP-4004 |
| G-GP-06 | Cost governance | In plan | WP-5003 |
| G-GP-07 | Compliance evidence | In plan | WP-3006, WP-6002 |
| G-GP-08 | Sandboxing | In plan | WP-3007, FR-014 |
| G-GP-09 | Trust scoring | In plan | WP-0004, WP-4008 |

**Remediation:** Verify each WP-3001–WP-3008 implementation status against research recommendations.

---

### 5.11 Optimization & Polish Gaps

**Source:** `docs/GAP_ANALYSIS_AND_REMEDIATION.md` | Gap IDs: G-OP-01 through G-OP-10

#### G-OP-01 through G-OP-10: MCP Middleware & Tool Optimization

| ID | Item | Status | Remediation |
|----|------|--------|-------------|
| G-OP-01 | ResponseCachingMiddleware | Done | Verify TTL 30s for ps, list_agents, list_droids, list_models |
| G-OP-02 | RateLimitingMiddleware | Done | Verify max_requests_per_second=10, burst=20 |
| G-OP-03 | ResponseLimitingMiddleware | Done | Verify max_size=500_000 for thegent_logs |
| G-OP-04 | Tool descriptions | Audit | Agent-optimized, action-oriented descriptions |
| G-OP-05 | Parameter docs | Audit | Clear defaults, units, constraints (timeout, tail) |
| G-OP-06 | Error messages | Audit | Actionable with remediation hints |
| G-OP-07 | ToolResult structured_content | Verify | All tools return structured_content + meta.execution_time_ms |
| G-OP-08 | SLO targets | Verify | p50 <50ms (ps), <20ms (status), etc. |
| G-OP-09 | Health route | Verify | @mcp.custom_route("/health") for monitoring |
| G-OP-10 | Graceful shutdown | Verify | Drain in-flight; wait up to 30s |

**Remediation:**
1. Audit middleware configuration
2. Audit tool descriptions, parameter docs, error messages
3. Verify ToolResult shape and SLO targets
4. Verify health route and graceful shutdown

---

## Consolidated Priority Order

### P0 (Immediate)

1. **Contract registry + canonical schema + adapter scaffolding** (G-RV-01, G-RV-02, G-CA-01)
   - Implement ContractRegistry, CSM dataclass, OutputAdapter interface
   - Register task-tool-18, zen-rich-v1, csm-v1

2. **Contract authority publication** (G-KD-01)
   - Publish CONTRACT_AUTHORITY.md (Done)
   - Verify adapter registration API in place

3. **Cursor Phase 2 dedicated block** (G-CP-01)
   - Add cursor: schema, token provider, refresh, rebindExecutors

### P1 (Next)

1. **Universal operation interfaces** (G-KD-02)
   - Status: Done (thegent operations, thegent_list_operations, thegent://operations, meta.operations)

2. **Incremental parser and structural validation** (G-RV-03)
   - Status: Done (IncrementalXMLParser, TruncatedParseError, ParseResult, extract_condensed_validated)

3. **Dynamic scraping adapters** (G-DM-01)
   - Status: Done (gemini, claude, proxy, cursor/copilot adapters)

4. **FastMCP Phase 5 production readiness** (G-FM-01)
   - Auth (Bearer/OAuth), stateless_http, Redis backend, deployment guide

5. **Plan index artifacts** (G-PI-01, G-PI-02, G-PI-03)
   - WBS-to-issue import matrix
   - DAG node-to-service contract checklist
   - PRD test plan matrix

### P2 (Following)

1. **Semantic validation and fallback control plane** (G-RV-04, G-RV-06)
   - Status: Done (FAILED/IN_PROGRESS invariants, phase-aware validators, FallbackPolicy)

2. **State-aware orchestration** (G-KD-03)
   - Phase 1: Run state extension
   - Phase 2: Continuity packet schema
   - Phase 3: Pause/resume CLI
   - Phase 4: MCP context integration

3. **Multi-agent mode catalog** (G-KD-04)
   - Status: Done

4. **FastMCP research docs** (G-FR-01, G-FR-02, G-FR-03)
   - FASTMCP_STORAGE_EVENTSTORE.md
   - FASTMCP_MIDDLEWARE.md
   - FASTMCP_SAMPLING_TELEMETRY.md

5. **Full verification runbook** (G-FM-03)
   - Status: Done

### P3 (Hardening)

1. **CI architecture guardrails** (G-KD-05)
   - Status: Done (check_boundaries.py, test_ci_architecture.py, ARCHITECTURE_LAYERS.md)

2. **Conformance test suite and drift alarms** (G-RV-07, G-RV-08)
   - Implement contract telemetry and drift detection
   - Migration playbook with canary, dual mode, rollback

3. **Fallback state machine** (G-CA-02)
   - State transitions for fallback scenarios
   - Parser-quality in routing decisions
   - Fallback KPI tracking

4. **FastMCP testing strategy** (G-FM-05)
   - Unit, contract, integration, chaos, load, timeout tests

5. **Governance WP implementation** (G-GP-01–G-GP-09)
   - Verify OPA, NeMo, audit trail, circuit breakers, HITL, cost, compliance, sandbox, trust implementations

### P4 (Enhancement)

1. **Simulation overlays** (G-CA-04)
   - PERT overlays for workflow planning
   - Resource contention simulation
   - Continuity risk scoring

2. **Migration controller and canary** (G-RV-08)
   - Contract upgrade playbook
   - Canary rollout strategy
   - Deprecation timeline

3. **Native Python Cursor client** (G-CA-01)
   - If cursor-api server dependency unacceptable, implement native client

4. **Icons and UX hints** (G-FM-04)
   - Add to thegent_run, thegent_bg, thegent_stop, thegent_logs, thegent_ps

---

## Summary Checklist

- [ ] All P0 items have implementation or explicit acceptance
- [ ] All "optional" items from plans are either implemented or documented as deferred with rationale
- [ ] All research tasks (FastMCP plan §11) have produced docs
- [ ] WBS-to-issue, DAG-to-service, PRD-to-test matrices exist
- [ ] Discovery surface is documented and audited
- [ ] Tool descriptions, error messages, and ToolResult shapes are audited
- [ ] Verification runbook is complete with pass/fail for each item
- [ ] Contract registry and canonical schema are in place
- [ ] Fallback policy and drift alarms are operational
- [ ] State-aware orchestration Phase 1 (run state extension) is implemented
- [ ] Multi-agent modes are discoverable and selectable
- [ ] Architecture boundaries are enforced in CI

---

## References

- **Contracts:**
  - `docs/contracts/CONTRACT_AUTHORITY.md`
  - `docs/contracts/FALLBACK_POLICY.md`

- **Architecture:**
  - `docs/ARCHITECTURE_LAYERS.md`
  - `src/thegent/contracts/registry.py`
  - `src/thegent/contracts/csm.py`
  - `src/thegent/contracts/adapters.py`
  - `src/thegent/contracts/policy.py`
  - `src/thegent/contracts/telemetry.py`

- **Orchestration:**
  - `docs/ORCHESTRATION.md`
  - `docs/MULTI_AGENT_MODE_CATALOG.md`
  - `docs/STATE_AWARE_ORCHESTRATION_DESIGN.md`
  - `src/thegent/orchestration_modes.py`
  - `src/thegent/execution.py`

- **Gap Analysis:**
  - `docs/GAP_ANALYSIS_AND_REMEDIATION.md`

---

**Document Generated:** 2026-02-14
**Status:** Authoritative Design Reference
