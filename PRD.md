# Product Requirements Document (PRD): Harmonious Agent Experience (HAX)

**Status:** Draft | **Version:** 1.1 | **Generated:** 2026-02-16 | **Updated:** 2026-03-30
**Goal:** Unify fragmented agent capabilities into a single, harmonious orchestration layer across all platforms (Claude, Codex, Cursor, etc.).

---

## 1. Executive Summary
`thegent` started as a set of fragmented tools and research audits. The **Harmonious Agent Experience (HAX)** initiative consolidates these into a unified platform. It supercedes individual platform limitations by providing a cross-platform queue, universal memory (Supermemory.ai), intelligent routing (LiteLLM), and autonomous governance.

## 2. Core Pillars

### 2.1 Universal Memory & Context (L3/L4)
- **Requirement**: Move from local file-based memory to a cloud-scale graph memory (Supermemory.ai).
- **Benefit**: Cross-session and cross-project knowledge persistence. Agents remember decisions made across different platforms.

### 2.2 Intelligent Multi-Provider Routing
- **Requirement**: Integrate LiteLLM to route tasks based on cost, quality, and speed (Pareto frontier).
- **Benefit**: Optimized spend and performance. Automated failover when a provider is down or capped.

### 2.3 Multi-Platform Parity & Supercedence
- **Requirement**: Harmonize Claude Code hooks, Cursor rules, and Codex notifications.
- **Benefit**: Unified `$defer`, `$block`, and `$idea` syntax works everywhere. Single `rules sync` command updates all environments.

### 2.4 Autonomous Governance & Self-Healing
- **Requirement**: Implement the "Gardener" agent for automated documentation updates and the "Simulation Sandbox" for risk assessment.
- **Benefit**: Reduced documentation debt and safer agent operations in production.

## 3. Key Feature Plans (Consolidated)

### 3.1 The Unified Queue (WP-7001)
- **Feature**: A single, project-aware prompt queue stored in `.thegent/prompt_queue.jsonl`.
- **Interactions**: `thegent queue tui`, `thegent run $defer`, and MCP tools for queue management.

### 3.2 The Gardner & Memory Synthesis (MEM-AUD-02)
- **Feature**: Automated background synthesis of audit logs and session history into `CLAUDE.md`, `ADR.md`, and `PRD.md`.
- **Interactions**: `thegent memory garden` command.

### 3.3 Multi-Tenant Process Orchestration (MTSP)
- **Feature**: Consolidate redundant MCP servers and LSPs into persistent daemons (e.g., persistent Serena).
- **Benefit**: Massive reduction in process sprawl and resource consumption.

### 3.4 Multi-Agent Team Protocol (WP-9003)
- **Feature**: Cross-platform coordination (Voting, Broadcast, Task Sync) for swarms of agents.

## 4. Success Metrics (Baseline)
- **Consolidation**: 100% of Feb 2026 fragmented plans integrated into the Master WBS.
- **Process Count**: < 10 persistent processes per active multi-agent session.
- **Latency**: < 10ms for queue operations; < 100ms for routing resolution.
- **Documentation**: 0 documentation debt; `CLAUDE.md` and `PRD.md` always reflect the latest state via Gardener.

---

## 5. Feature Epics

### Epic E1: Multi-Provider Agent Orchestration (Weeks 1-2)
**Objective:** Unify agent invocation across 10+ providers (Claude, Codex, Gemini, Copilot, Cursor, Antigravity, Minimax, GLM, Roo, Kilo) with failover, retry, and output normalization.

**User Stories:**
- **US-E1.1:** Diagnose Timeout Failures (P1, In Progress)
- **US-E1.2:** Add Timeouts to Git Commands & Output Streaming (P1, In Progress)
- **US-E1.3:** Direct Agent Invocation via Native CLIs (P1, Pending)
- **US-E1.4:** Codex Proxy Router via CLIProxyAPIPlus (P1, Pending)
- **US-E1.5:** Cursor API Backend Integration (P1, Pending)

**Acceptance Criteria:**
- [ ] All 10 agents (claude, gemini, codex, copilot, cursor-agent, cursor-api, antigravity, minimax, glm, roo, kilo) execute via native CLI or proxy
- [ ] Provider fallback chain executes with exponential backoff (2s-60s, max 4 retries)
- [ ] Failure classification (RATE_LIMIT, TRANSIENT, USAGE_LIMIT, UNKNOWN) covers 95% of observed errors
- [ ] Agent registry resolves aliases and returns correct runner type
- [ ] Noisy stderr patterns (node warnings, hook messages) filtered before returning results
- [ ] CLIProxyAPIPlus lifecycle (startup, health-check, shutdown) fully managed
- [ ] Zero timeouts on agent execution (timeout capture → EXIT_TIMEOUT=124)

**Key FR Traces:** FR-AGT-001, FR-AGT-002, FR-AGT-003, FR-AGT-004, FR-AGT-005, FR-AGT-006, FR-AGT-007, FR-AGT-008, FR-AGT-009, FR-AGT-010, FR-AGT-011

---

### Epic E2: Contract & Normalization Layer (Weeks 3-4)
**Objective:** Normalize heterogeneous agent outputs (XML, plain text, JSONL) into a unified `CanonicalStructuredMessage` contract with semantic validation and drift detection.

**User Stories:**
- **US-E2.1:** Canonical Structured Message (CSM) Schema (P1, Pending)
- **US-E2.2:** Incremental XML Parser for Agent Outputs (P1, Pending)
- **US-E2.3:** Output Adapter Registry with Fallback (P1, Pending)
- **US-E2.4:** Contract Telemetry & Drift Detection (P1, Pending)
- **US-E2.5:** Semantic Validation of CSM Invariants (P1, Pending)

**Acceptance Criteria:**
- [ ] CSM schema defined with all 11 fields (task_id, status, phase, progress, objective, summary, issues, actions_completed, next_steps, evidence_set_hash, decision_reason_code)
- [ ] XML output adapter normalizes copilot, gemini, claude, codex outputs with 95%+ success rate
- [ ] Incremental parser handles partial/streaming XML without blocking
- [ ] Generic plain text adapter provides 0.7 confidence fallback for any output
- [ ] Adapter registry covers 8+ providers with provider-specific XML mappings
- [ ] Telemetry records (timestamp, event_type, run_id, provider, confidence, success) persisted to JSONL
- [ ] Drift budget tracking (5% structural, 10% semantic) enforced via policy gates
- [ ] All CSM invariants validated (e.g., COMPLETED requires progress >= 1.0)
- [ ] Contract version registry (csm-v1, task-tool-18, zen-rich-v1) supports migration windows

**Key FR Traces:** FR-CTR-001, FR-CTR-002, FR-CTR-003, FR-CTR-004, FR-CTR-005, FR-CTR-006, FR-CTR-007, FR-CTR-008, FR-CTR-009, FR-CTR-010, FR-CTR-011, FR-CTR-012, FR-CTR-013

---

### Epic E3: Governance & Cost Control (Weeks 5-7)
**Objective:** Implement cost estimation, daily aggregation, and input guardrails (prompt length, blocklist, allowlists, CWD restriction).

**User Stories:**
- **US-E3.1:** Cost Estimation per Run (P2, Pending)
- **US-E3.2:** Daily Cost Aggregation by Owner (P2, Pending)
- **US-E3.3:** Input Guardrails — Prompt Length & Blocklist (P1, Pending)
- **US-E3.4:** Agent & Model Allowlists (P1, Pending)
- **US-E3.5:** CWD Restriction Guardrail (P2, Pending)

**Acceptance Criteria:**
- [ ] Cost estimation uses pricing table ($/1k input/output tokens by model) with fallback heuristic
- [ ] Daily cost aggregation sums finish events with `cost_usd` field, filtered to current UTC date
- [ ] Prompt length guardrail rejects prompts > 65536 chars (configurable)
- [ ] Prompt blocklist patterns reject matching prompts with remediation guidance
- [ ] Agent allowlist enforced when non-empty; defaults to all registered agents
- [ ] Model allowlist enforced when non-empty; supports model aliases (haiku, sonnet, opus)
- [ ] CWD restriction rejects executions outside `cwd_allowed_prefixes` (when configured)
- [ ] All guardrails configurable via environment variables (THGENT_PROMPT_MAX_CHARS, etc.)
- [ ] Guardrail failures return `GuardrailResult` with rail_id, violation reason, and remediation

**Key FR Traces:** FR-GOV-001, FR-GOV-002, FR-GOV-003, FR-GOV-004, FR-GOV-005, FR-GOV-006, FR-GOV-007

---

### Epic E4: Run Execution & Policy Gate (Weeks 8-10)
**Objective:** Persist run metadata with hash-chained audit trail, manage state transitions (RUNNING/PAUSED/COMPLETED/FAILED), and enforce OPA policies with trust scores.

**User Stories:**
- **US-E4.1:** Run Metadata Model & Registry (P1, Pending)
- **US-E4.2:** Hash-Chained Audit Trail (P1, Pending)
- **US-E4.3:** Run State Tracking (P1, Pending)
- **US-E4.4:** Idempotency Token Lookup (P2, Pending)
- **US-E4.5:** Trust Score Calibration (P2, Pending)
- **US-E4.6:** Checkpoint Registry for DAG State (P2, Pending)
- **US-E4.7:** Policy Engine with OPA Integration (P1, Pending)

**Acceptance Criteria:**
- [ ] RunMeta model captures 25+ fields (run_id, agent, model, mode, exit_code, status, cost_usd, timestamp, policy_result, audit trail hash)
- [ ] Run registry persisted to `run_registry.jsonl` with SHA-256 hash chaining (prev_hash → hash)
- [ ] Schema version marker written to first record; forward compatibility maintained
- [ ] Run state derived from event stream: start→RUNNING, finish→COMPLETED/FAILED, pause→PAUSED, resume→RUNNING
- [ ] Idempotency token lookup finds most recent run; merges start+finish events
- [ ] Trust score calibration computed per agent as avg_feedback_score / avg_confidence, clamped [0.5, 2.0]
- [ ] Checkpoint registry persists DAG snapshots with checkpoint_id, reason, dag_content
- [ ] Policy engine delegates to OPA when THGENT_OPA_URL configured; Python fallback when OPA unreachable
- [ ] Critical-lane policy: deny runs with confidence < 0.9; deny unknown agents; block on contract drift
- [ ] Production policy: deny runs below trust_score_threshold (default 0.8)

**Key FR Traces:** FR-EXE-001, FR-EXE-002, FR-EXE-003, FR-EXE-004, FR-EXE-005, FR-EXE-006, FR-EXE-007, FR-EXE-008, FR-EXE-009, FR-EXE-010

---

### Epic E5: Model Routing & Configuration (Weeks 11-13)
**Objective:** Define static model catalog with 25+ models, implement dynamic scraping with cache, and provide Pydantic settings for 15+ configuration parameters.

**User Stories:**
- **US-E5.1:** Static Model Catalog with Route Resolution (P1, Pending)
- **US-E5.2:** Model Alias Normalization (P1, Pending)
- **US-E5.3:** Model Blacklist Enforcement (P1, Pending)
- **US-E5.4:** Dynamic Model Scraping with Cache (P2, Pending)
- **US-E5.5:** Pydantic Settings with Environment Binding (P1, Pending)
- **US-E5.6:** Agent-Specific Default Models (P1, Pending)

**Acceptance Criteria:**
- [ ] Static catalog covers Anthropic (haiku-4.5, sonnet-4.5, opus-4.6), Gemini (flash variants), Codex 5.3, proxy providers (8+ models per provider)
- [ ] Each route specifies provider, backend_type (direct/proxy), model_alias, priority, cost_weight
- [ ] Alias normalization maps "haiku" → claude-haiku-4.5, "sonnet" → claude-sonnet-4.5, "opus" → claude-opus-4.6
- [ ] Blacklist enforces: Claude < 3.x, Gemini < 1.x (pro variants blocked), GPT-4, Codex without 5.3
- [ ] Model scraping from cursor (--list-models) and proxy (GET /v1/models) with 300s TTL cache
- [ ] Proxy models classified into buckets (antigravity, minimax, glm, roo, kilo, gemini, claude) by ID substring
- [ ] ThegentSettings as Pydantic BaseSettings with THGENT_ prefix, .env support
- [ ] Per-agent defaults: cursor_agent_cmd (gemini-3-flash), default_gemini_model (gemini-2.0-flash), etc.
- [ ] Timeout configuration: default_timeout (90s, range 10-3600), default_timeout_claude (300s)
- [ ] Retention policies (sessions, registry, health) configurable with per-domain overrides
- [ ] Startup validation ensures session directory exists and is writable (fail-fast)

**Key FR Traces:** FR-MOD-001, FR-MOD-002, FR-MOD-003, FR-MOD-004, FR-MOD-005, FR-MOD-006, FR-CFG-001, FR-CFG-002, FR-CFG-003, FR-CFG-004, FR-CFG-005, FR-CFG-006

---

## 6. Epic Timeline & Phasing

| Epic | Weeks | Priority | Status | Effort |
|------|-------|----------|--------|--------|
| **E1: Multi-Provider Orchestration** | 1-2 | P1 | In Progress | 8 pts |
| **E2: Contract & Normalization** | 3-4 | P1 | Pending | 10 pts |
| **E3: Governance & Cost Control** | 5-7 | P1/P2 | Pending | 8 pts |
| **E4: Run Execution & Policy Gate** | 8-10 | P1/P2 | Pending | 12 pts |
| **E5: Model Routing & Configuration** | 11-13 | P1/P2 | Pending | 10 pts |
| **Total** | **13 weeks** | — | — | **48 pts** |

---

## 7. Epic Success Metrics

| Metric | Target | Definition |
|--------|--------|-----------|
| Agent Coverage | 11/11 | All agents (claude, gemini, codex, copilot, cursor-agent, cursor-api, antigravity, minimax, glm, roo, kilo) execute without timeout |
| Runner Types | 3/3 | DirectAgentRunner, CodexProxyRunner, CursorApiRunner all implemented |
| Failure Classification | 95% | RATE_LIMIT, TRANSIENT, USAGE_LIMIT cover 95%+ observed errors |
| Retry Success Rate | 90% | 90%+ of transient failures resolved by exponential backoff retry |
| Output Normalization | 95% | 95%+ of agent outputs normalize to CSM with confidence >= 0.4 |
| Contract Drift | <5% structural, <10% semantic | Drift rates stay within budgets via policy gates |
| Cost Tracking | 100% | All runs tracked with USD cost estimates; daily aggregation per owner |
| Policy Gate Pass Rate | 95%+ | 95%+ of runs clear guardrails and OPA policies |
| Session Persistence | 100% | All run metadata persisted with hash-chained audit trail |
| Documentation Sync | 0 debt | PRD, ADR, PLAN auto-updated via Gardener agent |

---

*Cross-ref: [PLAN.md](./PLAN.md) | [ADR.md](./ADR.md) | [FUNCTIONAL_REQUIREMENTS.md](./FUNCTIONAL_REQUIREMENTS.md) | [USER_JOURNEYS.md](./USER_JOURNEYS.md)*
