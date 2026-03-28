# PLAN — thegent Implementation Plan

**Status:** Living Document | **Version:** 2.0 | **Updated:** 2026-03-27
**Goal:** Execute the Harmonious Agent Experience (HAX) across all platform subsystems.
**Cross-ref:** [PRD.md](./PRD.md) | [FUNCTIONAL_REQUIREMENTS.md](./FUNCTIONAL_REQUIREMENTS.md) | [ADR.md](./ADR.md)

---

## Phase Structure

```
Phase 1: Foundations (DONE)
Phase 2: Memory and Synthesis (IN PROGRESS)
Phase 3: Multi-Provider Routing
Phase 4: Platform Parity and Queuing
Phase 5: Agent Orchestration and Swarm
Phase 6: Governance and Policy Enforcement
Phase 7: TUI, Observability, and SDK
```

---

## Phase 1 — Foundational Optimizations

**Status:** DONE
**Goal:** Persistent tooling daemons, atomic edits, and local memory audit.

| Task ID | Description | Depends On | Status |
|---------|-------------|------------|--------|
| P1.1 | Persistent Serena daemon (MTSP-04): LSP + symbol caching daemon | — | DONE |
| P1.2 | Atomic Transaction tool (MTSP-13): single-call multi-file write | — | DONE |
| P1.3 | Edit Leasing Manager (MTSP-14): per-file lock with timeout | P1.2 | DONE |
| P1.4 | Local memory audit infrastructure (MEM-AUD-01): JSONL append store | — | DONE |
| P1.5 | Bootstrap wizard `thegent install --wizard` (FR-BOOT-004) | — | DONE |
| P1.6 | `thegent doctor` audit command (FR-BOOT-006) | P1.5 | DONE |

---

## Phase 2 — Memory and Synthesis

**Status:** IN PROGRESS
**Goal:** Cross-session, cross-project memory via Gardener agent and Supermemory integration.

Traces to: PRD E8, FR-SESS, FR-AUDIT

| Task ID | Description | Depends On | Status |
|---------|-------------|------------|--------|
| P2.1 | Gardener agent definition (`agents/gardener.md`) | P1.4 | DONE |
| P2.2 | `thegent memory garden` CLI command | P2.1 | DONE |
| P2.3 | `generate_continuity_packet` session synthesis | P2.2 | DONE |
| P2.4 | `SupermemoryProvider` implementation: cloud-scale L3/L4 memory | P2.3 | OPEN |
| P2.5 | Connect `generate_continuity_packet` to Supermemory API (FR-SESS) | P2.4 | OPEN |
| P2.6 | `thegent memory search "<query>"` query surface (FR-SESS) | P2.5 | OPEN |
| P2.7 | `thegent memory snapshot` bundle export (FR-AUDIT-001) | P2.6 | OPEN |
| P2.8 | MAIF audit log: append-only JSONL with checksum chain (FR-AUDIT-001) | P1.4 | OPEN |
| P2.9 | `thegent audit list` CLI rendering (FR-AUDIT-002) | P2.8 | OPEN |

**DAG:**
```
P1.4 --> P2.1 --> P2.2 --> P2.3 --> P2.4 --> P2.5 --> P2.6 --> P2.7
P1.4 --> P2.8 --> P2.9
```

---

## Phase 3 — Multi-Provider Routing

**Status:** PENDING
**Goal:** LiteLLM abstraction, Pareto frontier visualization, automatic failover, cost caps.

Traces to: PRD E5, FR-ROUTE, ADR-001

| Task ID | Description | Depends On | Status |
|---------|-------------|------------|--------|
| P3.1 | Add `litellm` dependency to `pyproject.toml` and `ProviderModelManager` refactor | — | OPEN |
| P3.2 | `LiteLLM_Router` wrapper: cost/speed/quality scoring (FR-ROUTE-001, FR-ROUTE-002) | P3.1 | OPEN |
| P3.3 | Wire `CodexProxyRunner` to consume routing metadata from `LiteLLM_Router` | P3.2 | OPEN |
| P3.4 | `ClipRoxyAdapter` refinement: OpenAI-compatible endpoint passthrough (FR-ROUTE-003) | P3.2 | OPEN |
| P3.5 | Provider cost cap enforcement per-provider and per-session (FR-ROUTE, FR-GOVERN-002) | P3.2 | OPEN |
| P3.6 | `thegent provider list` and `thegent provider add` CLI (FR-ROUTE-004) | P3.1 | OPEN |
| P3.7 | `thegent routing status` with real-time P50/P95 per provider (PRD E5.S4) | P3.2 | OPEN |
| P3.8 | Pareto Frontier Visualization TUI panel (PRD E5.S4) | P3.7 | OPEN |

**DAG:**
```
P3.1 --> P3.2 --> P3.3
P3.1 --> P3.4
P3.2 --> P3.5
P3.1 --> P3.6
P3.2 --> P3.7 --> P3.8
```

---

## Phase 4 — Platform Parity and Queuing

**Status:** PENDING
**Goal:** Unified prompt queue, multi-platform rules sync, $defer/$block directives.

Traces to: PRD E4, E3, FR-DOT, ADR-004, ADR-010

| Task ID | Description | Depends On | Status |
|---------|-------------|------------|--------|
| P4.1 | Unified prompt queue: `.thegent/prompt_queue.jsonl` with push/run/replay (ADR-004) | — | OPEN |
| P4.2 | `$defer` directive parser: push prompt to queue instead of immediate exec (ADR-010) | P4.1 | OPEN |
| P4.3 | `$block <condition>` directive: pause until condition satisfied (ADR-010) | P4.1 | OPEN |
| P4.4 | `$idea <text>` directive: non-blocking idea recording (ADR-010) | P4.1 | OPEN |
| P4.5 | Multi-platform rules sync: `thegent rules sync` propagates CLAUDE.md, AGENTS.md to harnesses (FR-DOT-001) | — | OPEN |
| P4.6 | `thegent mcp sync`: write per-harness MCP config (Claude Desktop, Codex, Cursor) (PRD E4.S1) | — | OPEN |
| P4.7 | `thegent mcp up` / `thegent mcp status`: daemon lifecycle management (PRD E4.S2) | P4.6 | OPEN |
| P4.8 | `thegent skills install <skill>` from registry or local `skills/` (PRD E4.S4) | — | OPEN |
| P4.9 | `thegent hooks install`: hook schema validation and placement (PRD E4.S5) | — | OPEN |
| P4.10 | Greenfield scaffold: `thegent scaffold greenfield` with Taskfile, linters, docsite (PRD E3.S1) | — | OPEN |
| P4.11 | Brownfield scaffold: `thegent scaffold brownfield` adds governance artifacts only (PRD E3.S2) | P4.10 | OPEN |

**DAG:**
```
P4.1 --> P4.2
P4.1 --> P4.3
P4.1 --> P4.4
P4.6 --> P4.7
```

---

## Phase 5 — Agent Orchestration and Swarm

**Status:** PARTIAL (voting/broadcast done; queue and swarm pending)
**Goal:** Multi-agent team protocol, hierarchical dispatch, swarm launch, sitback mode.

Traces to: PRD E6, FR-ORCH, FR-AGENT, ADR-006

| Task ID | Description | Depends On | Status |
|---------|-------------|------------|--------|
| P5.1 | Teammate Coordination Protocol: voting + broadcast (WP-9003) | — | DONE |
| P5.2 | `SubAgentDispatcher` with configurable semaphore and per-node timeout (FR-ORCH-002) | — | DONE |
| P5.3 | `HierarchicalDispatcher`: decomposes objectives into sub-plans (FR-ORCH-005) | P5.2 | OPEN |
| P5.4 | `thegent run agent "<task>" --loop` background agent with log persistence (PRD E6.S1) | P5.2 | OPEN |
| P5.5 | `thegent swarm launch --agents N --task` coordinated swarm (PRD E6.S2) | P5.4 | OPEN |
| P5.6 | Swarm PID file + `thegent swarm status` per-agent state view | P5.5 | OPEN |
| P5.7 | `thegent queue` TUI subsystem: inspect queue, drain items (PRD E6.S3) | P4.1 | OPEN |
| P5.8 | `thegent team start`: launch planner+implementer+reviewer team from `agents.toml` (PRD E6.S4) | P5.3 | OPEN |
| P5.9 | `thegent sitback` long-horizon monitor mode (PRD E6.S5) | P5.4 | OPEN |
| P5.10 | `autopoiesis` mode: agents spawn child agents up to depth limit (FR-AGENT-004) | P5.3 | OPEN |
| P5.11 | `budget_tracker` integration: abort dispatch on cost cap exceeded (FR-ORCH-006) | P3.5 | OPEN |

**DAG:**
```
P5.2 --> P5.3 --> P5.4 --> P5.5 --> P5.6
P5.3 --> P5.8
P5.4 --> P5.9
P5.3 --> P5.10
P4.1 --> P5.7
P3.5 --> P5.11
```

---

## Phase 6 — Governance and Policy Enforcement

**Status:** PENDING
**Goal:** CONSTITUTION.yaml enforcement, quality gate contracts, `thegent governance check`.

Traces to: PRD E7, FR-GOVERN, FR-AUDIT, ADR-009

| Task ID | Description | Depends On | Status |
|---------|-------------|------------|--------|
| P6.1 | `PolicyEngine.await_approval(node)`: HITL gate for high-risk tasks (FR-GOVERN-001) | — | OPEN |
| P6.2 | Role-tool allowlist matrix enforcement (FR-GOVERN-003) | P6.1 | OPEN |
| P6.3 | `CONSTITUTION.yaml` schema and loader: file/dir access rules, cost thresholds (PRD E7.S1) | P6.1 | OPEN |
| P6.4 | `thegent governance check --fix`: audit repos for required governance files (PRD E7.S4) | P6.3 | OPEN |
| P6.5 | Quality gate contracts in `contracts/`: lint, test, coverage, security (PRD E7.S3) | — | OPEN |
| P6.6 | `thegent audit report` human-readable audit summary (FR-AUDIT-002) | P2.8 | OPEN |
| P6.7 | Append-only audit log with checksum chain; tamper detection (FR-AUDIT-001) | P2.8 | OPEN |
| P6.8 | Forensic snapshotting: per-session state snapshot with provenance (PRD E7.S2) | P6.7 | OPEN |

**DAG:**
```
P6.1 --> P6.2
P6.1 --> P6.3 --> P6.4
P6.3 --> P6.5
P2.8 --> P6.6
P2.8 --> P6.7 --> P6.8
```

---

## Phase 7 — TUI, Observability, and SDK

**Status:** PENDING
**Goal:** Full-screen TUI dashboard, OpenTelemetry traces, cost observability, SDK publication.

Traces to: PRD E10, E11, FR-RUST, ADR-008

| Task ID | Description | Depends On | Status |
|---------|-------------|------------|--------|
| P7.1 | `thegent tui`: full-screen dashboard with agents, queue, provider health (PRD E10.S1) | P5.6 | OPEN |
| P7.2 | OpenTelemetry span tree per agent run in TUI (PRD E10.S2) | P7.1 | OPEN |
| P7.3 | Per-session and cumulative cost breakdown by provider/model/project (PRD E10.S3) | P3.7 | OPEN |
| P7.4 | Alert thresholds + desktop notifications for cost/error/queue (PRD E10.S4) | P7.1 | OPEN |
| P7.5 | `thegent-path-resolve` Rust crate: P99 ≤ 1ms binary lookup (FR-RUST-001) | — | OPEN |
| P7.6 | `thegent-discovery` Rust crate: < 50ms manifest scan (FR-RUST-002) | — | OPEN |
| P7.7 | `thegent-crypto` Rust crate: SHA-256 + BLAKE3 bindings (FR-RUST-003) | — | OPEN |
| P7.8 | `thegent-cache` Rust crate: thread-safe LRU with TTL (FR-RUST-004) | P7.7 | OPEN |
| P7.9 | Python SDK: `import thegent` typed API for routing, memory, governance (PRD E11.S1) | P5.11, P3.2 | OPEN |
| P7.10 | TypeScript SDK: `@thegent/sdk` published to npm (PRD E11.S1) | P7.9 | OPEN |
| P7.11 | MCP HTTP endpoint: external integrators call thegent via JSON-RPC (PRD E11.S3) | P4.6 | OPEN |
| P7.12 | VitePress docsite build and publish to GitHub Pages (ADR-008) | P7.9 | OPEN |

**DAG:**
```
P5.6 --> P7.1 --> P7.2
P3.7 --> P7.3
P7.1 --> P7.4
P7.7 --> P7.8
P5.11, P3.2 --> P7.9 --> P7.10
P4.6 --> P7.11
P7.9 --> P7.12
```

---

## Full Cross-Phase DAG (Critical Path)

```
P1.4 --> P2.1..P2.9 (Memory)
P3.1 --> P3.2 --> P3.5 --> P5.11 --> P7.9 (Routing -> Cost Control -> SDK)
P4.1 --> P4.2..P4.4 (Queue Directives)
P4.1 --> P5.7 (Queue TUI)
P5.2 --> P5.3 --> P5.4 --> P5.5 (Orchestration -> Swarm)
P5.3 --> P5.8 (Teams)
P6.1 --> P6.3 (Policy)
P2.8 --> P6.7 (Audit -> Forensics)
P5.6 --> P7.1 --> P7.2 (TUI -> OTel)
```

---

## Current Status Snapshot (2026-03-27)

| Phase | Status | Open Tasks |
|-------|--------|------------|
| Phase 1 — Foundations | DONE | 0 |
| Phase 2 — Memory | IN PROGRESS | P2.4–P2.9 (6) |
| Phase 3 — Routing | PENDING | P3.1–P3.8 (8) |
| Phase 4 — Platform Parity | PENDING | P4.1–P4.11 (11) |
| Phase 5 — Orchestration | PARTIAL | P5.3–P5.11 (9) |
| Phase 6 — Governance | PENDING | P6.1–P6.8 (8) |
| Phase 7 — TUI and SDK | PENDING | P7.1–P7.12 (12) |
| **Total open** | | **54 tasks** |

---

*Epics: E1–E11 in PRD.md | FR IDs: FR-BOOT, FR-DOT, FR-ORCH, FR-AGENT, FR-MCP, FR-ROUTE, FR-GOVERN, FR-AUDIT, FR-RUST | ADRs: ADR-001–010*
