# Harmonious Agent Experience (HAX) — Architecture Decision Records

**Project**: thegent (Agent Orchestration Platform)
**Last Updated**: 2026-03-25
**Owner**: Engineering Team

---

## ADR-001: Multi-Platform Agent Routing via LiteLLM Abstraction Layer

**Date**: 2026-03-25
**Status**: Accepted
**Context**: thegent must coordinate agents across Claude, Cursor, Codex, Copilot, and Gemini—each with different APIs, rate limits, and pricing. Direct integration to each platform API creates vendor lock-in and duplicates routing logic. LiteLLM (open-source) provides a unified interface with built-in fallback, cost tracking, and latency optimization.

**Decision**: Introduce LiteLLM as the routing abstraction layer. All agent calls go through a LiteLLM wrapper that handles provider selection based on cost/speed/quality trade-offs, automatic failover, token usage tracking, and request/response logging.

**Consequences**:
- Single point of abstraction: changes to provider APIs localized to LiteLLM config
- Enables provider diversity: can A/B test model quality on same prompt
- Cost optimization: route expensive tasks to cheaper models without degrading quality

**Alternatives Considered**:
- Direct API integration per provider: Duplicates fallback logic; tight coupling
- Unified API wrapper (hand-written): More control but higher maintenance burden

---

## ADR-002: Universal Memory via Supermemory.ai (L3/L4 Knowledge Graph)

**Date**: 2026-03-25
**Status**: Accepted
**Context**: thegent agents operate across multiple projects and sessions. Currently, memory is local to each agent. This violates the "Harmonious Agent Experience"—an agent in project A cannot recall decisions made in project B. Cross-project knowledge persistence requires a centralized, semantic memory store.

**Decision**: Integrate Supermemory.ai as the universal memory backend. Agent session summaries are automatically synthesized and stored in Supermemory's graph memory. Agents query Supermemory before task execution to retrieve similar decisions.

**Consequences**:
- Cross-session knowledge transfer: agents learn from each other's work
- Reduces duplicate analysis: "Have we solved this pattern before?"
- Privacy/security: Supermemory.ai is cloud service; sensitive code/credentials must be redacted
- Cost: per-query pricing; budget required

**Alternatives Considered**:
- Local SQLite graph database: Works for single-machine; doesn't scale to 1000+ agents
- Vector database (Pinecone, Weaviate): Good for search but not designed for cross-session synthesis

---

## ADR-003: Daemon-Based Process Orchestration (Persistent MCP Servers)

**Date**: 2026-03-25
**Status**: Accepted
**Context**: Current thegent spawns new processes for every MCP server invocation. At scale (1000 agents), this creates process explosion, startup latency (2-3s), and resource waste. A persistent daemon model reduces overhead dramatically.

**Decision**: Implement persistent daemon processes for high-volume tools: Serena (LSP + symbol caching), Playwright (browser automation), and MCP server (file I/O, git operations). Daemons expose gRPC or socket-based APIs. thegent CLI routes requests via name/port registry. Daemons auto-restart on crash.

**Consequences**:
- Latency improvement: <100ms per tool call (vs. 2-3s startup)
- Complexity increase: daemon lifecycle management, port binding, socket cleanup
- Coupling: daemons shared across agents; one crash affects multiple agents (mitigated by auto-restart)
- Resource efficiency: process count capped at <10 per session

**Alternatives Considered**:
- Stateless spawning (current): Simple but unscalable
- Containerized tooling (Docker): Slow startup; same problem

---

## ADR-004: Unified Queue with JSONL Format (.thegent/prompt_queue.jsonl)

**Date**: 2026-03-25
**Status**: Accepted
**Context**: thegent agents generate prompts scattered across CLI args, stdin, and config files. A unified queue enables priority scheduling, batch processing, replayability, and audit trails.

**Decision**: Implement a project-aware prompt queue stored in `.thegent/prompt_queue.jsonl`. Each line is an immutable prompt record. CLI commands: push, tui, run --batch, replay.

**Consequences**:
- Single source of truth for prompts; enables scheduling and batch processing
- JSONL format is human-readable and easily parseable
- Queue grows unbounded; periodic archival required
- Integration with MCP tools: `thegent run $defer` pushes to queue instead of executing immediately

**Alternatives Considered**:
- Database (SQLite): Overkill; JSONL is simple and version-controllable
- Message queue (NATS): Over-engineered for local dev workflow

---

## ADR-005: The Gardener Agent (Automated Documentation Synthesis)

**Date**: 2026-03-25
**Status**: Accepted
**Context**: thegent documentation is scattered across CLAUDE.md, ADR.md, PRD.md. As agents execute work, decisions accumulate in session logs and PR comments. Documentation becomes stale because manual updates are tedious.

**Decision**: Implement a background "Gardener" agent that runs periodically. The Gardener scans session logs and PR comments, extracts decisions/patterns via LLM analysis, and updates CLAUDE.md, ADR.md, and PRD.md. Output is git-committed.

**Consequences**:
- Documentation always reflects current understanding; zero staleness
- Requires LLM integration (Claude for analysis)
- Risk: Gardener hallucinates decisions (mitigated by human review)
- Enables continuous improvement cycle: work → synthesis → updated docs → next work

**Alternatives Considered**:
- Manual documentation updates: Humans forget; docs stale within weeks
- Static scaffolding: Generated once; quickly outdated

---

## ADR-006: Multi-Agent Team Protocol (Voting, Broadcast, Task Sync)

**Date**: 2026-03-25
**Status**: Accepted
**Context**: As thegent scales to 50+ concurrent agents, coordination becomes critical. Agents must agree on decisions, share discoveries, and synchronize work to prevent duplicate effort.

**Decision**: Implement multi-agent team protocol with three primitives:
1. **Voting**: Agents vote on architectural decisions. Majority wins. Stored in `.thegent/decisions.jsonl`.
2. **Broadcast**: Agent publishes findings (e.g., "Use httpx instead of requests"). Other agents subscribe per-topic.
3. **Task Sync**: Central task registry (`.thegent/tasks.jsonl`) tracks active work. Agents claim tasks; prevents duplicates.

Communication via NATS (distributed) or local file watches (single-machine). gRPC provides inter-agent RPC calls.

**Consequences**:
- Enables swarm-like behavior: agents act as team, not individuals
- Requires careful consensus design: voting rules, quorum thresholds
- Scales to 1000 agents; voting latency ~100ms
- Auditable: all votes and broadcasts logged for replay

**Alternatives Considered**:
- Centralized orchestrator: Single point of failure
- No coordination: Duplicate work, conflicting decisions

---

## ADR-007: TypeScript for Frontend/CLI (Node.js + Bun Package Manager)

**Date**: 2026-03-25
**Status**: Accepted
**Context**: thegent CLI targets developers familiar with Node.js. Python CLI is slower (~500ms startup). Frontend benefits from unified language across web and desktop (via Tauri).

**Decision**: Implement thegent CLI in TypeScript using Commander.js. Use Bun as package manager (faster than npm/pnpm). Frontend uses React + TypeScript + VitePress for documentation. All frontends (web, desktop) built from same codebase.

**Consequences**:
- Unified tech stack: JavaScript/TypeScript across CLI and frontend
- Fast startup: Bun provides <100ms CLI command launch
- Ecosystem: npm packages available for most needs
- Cost: Node.js runtime; minimal for typical deployments

**Alternatives Considered**:
- Python CLI (typer): Slower startup; not native to web/Tauri
- Go CLI: Excellent for speed but requires separate codebase

---

## ADR-008: VitePress for Documentation with Embedded React Widgets

**Date**: 2026-03-25
**Status**: Accepted
**Context**: thegent documentation requires guides, API references, decision trees, and executable examples. Static Markdown is insufficient. Operators need interactive examples (run scenario, see output).

**Decision**: Use VitePress as documentation platform. Markdown files can embed React components for interactive code examples, Mermaid diagrams, API explorers, and decision trees. Auto-builds on CI; published to GitHub Pages.

**Consequences**:
- Rich, interactive docs; higher engagement
- Requires React component authoring; slight learning curve
- Build time: ~10s for 100+ pages
- Great SEO: VitePress generates static HTML

**Alternatives Considered**:
- Docusaurus: Excellent but slower builds
- ReadTheDocs: Markdown-only; no interactive components

---

## ADR-009: Git as Source of Truth for Session State

**Date**: 2026-03-25
**Status**: Accepted
**Context**: thegent session state (files edited, decisions made, test results) must be version-controlled and auditable. External databases introduce operational burden. Git is already present in every project.

**Decision**: Store thegent session metadata in `.thegent/` directory, committed to Git:
- `.thegent/session.jsonl` — immutable session log
- `.thegent/decisions.jsonl` — voting and decision records
- `.thegent/prompt_queue.jsonl` — executed prompts + results
- `.thegent/agents/` — per-agent state

All files are Git-tracked. Session completion triggers: `git add .thegent/ && git commit -m "session: <summary>"`

**Consequences**:
- Full audit trail: `git log .thegent/`
- Replay capability: `git checkout <session-hash>::.thegent/`
- Distributed across clones: no external database needed
- Mergeable: multiple agents work in parallel; Git handles conflicts

**Alternatives Considered**:
- External database: Decouples from project; harder to audit
- Distributed consensus (IPFS): Overkill; Git already provides consensus

---

## ADR-010: Defer/Block Directives for Prompt Scheduling

**Date**: 2026-03-25
**Status**: Accepted
**Context**: Agents encounter tasks not immediately actionable ("defer until dependency X is ready") or blocked ("waiting for user input"). Encoding intent in prompt text is ambiguous. Formal directives make intent explicit.

**Decision**: Introduce three directives in prompts:
1. **$defer**: Push prompt to queue for later execution.
2. **$block <condition>**: Pause execution until condition is met.
3. **$idea <text>**: Non-blocking note for future work.

Directives are parsed by CLI and converted to queue entries, blocking locks, or ideas.

**Consequences**:
- Makes workflow explicit; easier to understand agent intent
- Enables automated scheduling and dependency management
- Requires directive parser (regex + JSONL); minimal overhead
- Synergizes with multi-agent coordination: $block enables agents to wait for each other

**Alternatives Considered**:
- Natural language ("please defer"): Ambiguous; requires NLP
- Environment variables: Hidden from prompt context; easy to miss

---

**Document History**:
- v2.0 (2026-03-25): Comprehensive ADR rewrite. 10 decisions covering platform routing, memory, orchestration, documentation, and coordination.
- v1.0 (earlier): Initial ADR set with legacy format.

*Cross-ref: [ARCHITECTURE.md](./docs/plans/05-ARCHITECTURE.md) | [PRD.md](./PRD.md)*
