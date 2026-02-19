# Product Requirements Document (PRD): Harmonious Agent Experience (HAX)

**Status:** Draft | **Version:** 1.0 | **Generated:** 2026-02-16
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

## 4. Success Metrics
- **Consolidation**: 100% of Feb 2026 fragmented plans integrated into the Master WBS.
- **Process Count**: < 10 persistent processes per active multi-agent session.
- **Latency**: < 10ms for queue operations; < 100ms for routing resolution.
- **Documentation**: 0 documentation debt; `CLAUDE.md` and `PRD.md` always reflect the latest state via Gardener.

---
*Cross-ref: [PLAN.md](./PLAN.md) | [ADR.md](./ADR.md) | [FUNCTIONAL_REQUIREMENTS.md](./FUNCTIONAL_REQUIREMENTS.md)*
