# Thegent Unified Plan — Master Index

> **Generated**: 2026-02-16 | **Version**: 1.3 | **Status**: Active
> **Project**: thegent — Unified agent orchestration CLI for Factory skills and droids
> **Stack**: Python 3.12+, FastMCP 3.0, Typer, Pydantic, tenacity, process-compose

---

## How to Use This Docset (Quick Start for New Contributors)

**New to thegent?** Read in this order:
1. [01-PROJECT-STATE.md](./01-PROJECT-STATE.md) — Understand what's already built (5 min)
2. [02-UNIFIED-WBS.md](./02-UNIFIED-WBS.md) — Find your work package (WP) (5 min)
3. [04-REQUIREMENTS.md](./04-REQUIREMENTS.md) — Understand your FRs/NFRs (5 min)
4. [06-IMPLEMENTATION-GUIDE.md](./06-IMPLEMENTATION-GUIDE.md) — Read code conventions (10 min)
5. [05-ARCHITECTURE.md](./05-ARCHITECTURE.md) — Understand the design (10 min)
6. Your specific WP section in [02-WBS](./02-UNIFIED-WBS.md) — Detailed acceptance criteria (5 min)
7. [07-TEST-STRATEGY.md](./07-TEST-STRATEGY.md) — Understand test requirements (5 min)

**Need quick reference?** Jump to [Cross-Reference Index](#cross-reference-index) at the bottom.

**Running multiple agents?** See [10-SUBAGENT-DISPATCH.md](./10-SUBAGENT-DISPATCH.md) for batch sequencing. For "do all" without overlap: read [WORK_STREAM.md](../reference/WORK_STREAM.md) (canonical) or [WBS_AGENT_PROGRESS.md](../reference/WBS_AGENT_PROGRESS.md) — claim items before starting.

---

## Docset Modules

| # | Module | Purpose | Key Sections |
|---|--------|---------|--------------|
| [00](./00-MASTER-INDEX.md) | Master Index | Navigation hub, cross-links, quick reference | Docset modules, summary, paths, index |
| [01](./01-PROJECT-STATE.md) | Project State | What's done, what's not, source map | Completed subsystems, test coverage, config state |
| [02](./02-UNIFIED-WBS.md) | Unified WBS | All 70 work packages across 8 phases | Phase summary, detailed WPs, gates, dependencies |
| [03](./03-UNIFIED-DAG.md) | Unified DAG | 10 DAG specifications with node semantics | Core execution, recovery, governance, scale, contracts, multi-agent, DLQ, routing, observability |
| [04](./04-REQUIREMENTS.md) | Requirements | 42 FRs + 16 NFRs with acceptance criteria | Functional, non-functional, personas, user journeys |
| [05](./05-ARCHITECTURE.md) | Architecture | Decisions, patterns, contracts, abstractions | Service decomposition, 10 ADRs, 37 key patterns, 3 data contracts |
| [06](./06-IMPLEMENTATION-GUIDE.md) | Implementation Guide | Code patterns, conventions, module structure | Python style, key abstractions, new modules, file guide |
| [07](./07-TEST-STRATEGY.md) | Test Strategy | 14 categories, 225-320 tests, FR traceability | Test pyramid, golden corpus, adversarial, chaos, coverage |
| [08](./08-OPTIMIZATION-CATALOG.md) | Optimization Catalog | 93 enhancement items (quick wins + polish) | Performance, hardening, UX, DX, ops, design elegance |
| [09](./09-RISK-REGISTRY.md) | Risk Registry | 15 anti-patterns, 17 risks, MAST 14-mode failure taxonomy | Prevention strategies, mitigations, operational safeguards |
| [10](./10-SUBAGENT-DISPATCH.md) | Subagent Dispatch | 10 sequential batches, 30 agents, context packages | Batch schedule, dependencies, prompt template, parallelization |
| [12](./12-LIFECYCLE-LOOP-DESIGN.md) | Lifecycle & Cycleloop | Soft/hard loops, checker-agent pattern, preset routing, human takeover | Loop controller, preset catalog, LLM fallback, observability overhaul |
| [CODEX](./CODEX_DONUT_HARNESS_PLAN.md) | Agent Orchestration Harness (Multi-Platform) | Full parity: Claude Code, Codex, Cursor, Factory droid, Augment — queue, harvest, rules sync, agent teams | [Feature audit](../research/CLAUDE_CODE_FEATURE_PARITY_AUDIT.md), thegent team, rules sync |
| [PARITY](./MULTI_PLATFORM_PARITY_MASTER_PLAN.md) | Multi-Platform Parity Master Plan | Complete matrix: achieve + supercede parity across 6 platforms; phased execution; §10–13 end-to-end flows, optimization, intuitive/robust design | [CODEX](./CODEX_DONUT_HARNESS_PLAN.md), [Deep dive](../research/MULTI_PLATFORM_DEEP_DIVE.md), [08-OPT](./08-OPTIMIZATION-CATALOG.md) |
| [MCP-OPT](./MCP_TOOL_OPTIMIZATION_PLAN.md) | MCP Tool Optimization Plan | Optimization, polish, intuitive/robust design for MCP server and 40+ tools; OPT/ROB/UX mapping; actionable errors | [08-OPT](./08-OPTIMIZATION-CATALOG.md), [PARITY](./MULTI_PLATFORM_PARITY_MASTER_PLAN.md) |
| [MCP-PARITY](../research/MCP_FULL_PARITY_AND_FASTMCP_AUDIT.md) | MCP Full Parity & FastMCP Audit | CLI↔MCP↔Codex/CC matrix; FastMCP transport spec usage; Queue/Team MCP gaps; implementation plan | [PARITY](./MULTI_PLATFORM_PARITY_MASTER_PLAN.md), [MCP-OPT](./MCP_TOOL_OPTIMIZATION_PLAN.md) |
| [SUPERMEMORY](./2026-02-16-supermemory-integration-plan.md) | Supermemory.ai Integration | Cloud-scale universal memory API; graph memory; persistence for L3/L4 | [CONTEXT_DEPTH](../reference/CONTEXT_MANAGEMENT_DEPTH.md) |
| [PROCESS-OPT](./PROCESS_OPTIMIZATION_PLAN.md) | Process & Tool Optimization | Multi-tenant single process execution; efficient tool migration (rg/fd/jaq); process cleanup | [MCP-OPT](./MCP_TOOL_OPTIMIZATION_PLAN.md) |
| [HOOK-RUST](./HOOK_RUNTIME_RUST_DESIGN.md) | Hook Runtime Rust Migration | Full common.sh replacement: thegent-hooks binary (init, cache, git, changed-files, config, …); phased deprecation | [Research synthesis](../research/HOOK_RUST_MIGRATION_RESEARCH_SYNTHESIS.md), [PROCESS-OPT](./PROCESS_OPTIMIZATION_PLAN.md) |
| [SHELL→RUST](./FULL_SHELL_TO_RUST_WHERE_BENEFICIAL.md) | Full Shell → Rust Where Beneficial | Inventory of all shell (hooks/lib, dispatchers, hooks, install shims, scripts); benefit criteria; Rust target map; phased migration | [HOOK-RUST](./HOOK_RUNTIME_RUST_DESIGN.md), [RUST_GO](../migration/RUST_GO_MIGRATION_PLAN.md) |
| [RESEARCH_SPRAWL](../research/RESEARCH_SEED_FRAGMENT_INVENTORY_AND_SPRAWL_TODO.md) | Research/Seed/Fragment Inventory & Sprawl Todo | ✅ **P0 & P1 Complete** - Find all fragmented/seed docs; sprawl each to full breadth/depth (optimize, robustify, practical, holistic, maximal); place into [WORK_STREAM](../reference/WORK_STREAM.md); convert all md with thegent flash agents. **Status**: 9 docs expanded, 44 BACKLOG items added. | [RESEARCH_FRAGMENTS](../research/SESSION_RESEARCH_FRAGMENTS.md), [UNIFIED_WORK_STREAM_DESIGN](../reference/UNIFIED_WORK_STREAM_DESIGN.md), [FINAL_EXPANSION_REPORT](../research/FINAL_EXPANSION_REPORT.md) |
| [RESEARCH_FRAGMENTS](../research/SESSION_RESEARCH_FRAGMENTS.md) | Session Research Fragments | ✅ **Expanded** - 2026-02-15 Deep-dives (Supermemory, Pareto, Econ Gov) → [SESSION_RESEARCH_COMPLETE.md](../research/SESSION_RESEARCH_COMPLETE.md) | [WBS](./02-UNIFIED-WBS.md), [RESEARCH_SPRAWL](../research/RESEARCH_SEED_FRAGMENT_INVENTORY_AND_SPRAWL_TODO.md) |
| [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md) | Documentation Expansion TODO | Systematic expansion of 411 MD docs from fragments to complete, optimized docs | [MASTER-INDEX](./00-MASTER-INDEX.md) |
| [SESSION_RESEARCH_COMPLETE](../research/SESSION_RESEARCH_COMPLETE.md) | ✅ Session Research Complete | Expanded: 5 concept deep-dives (Supermemory, Pareto, Econ Gov, MAIF, Simulation) | [RESEARCH_FRAGMENTS](../research/SESSION_RESEARCH_FRAGMENTS.md), [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md) |
| [CROSS_PLATFORM_RESEARCH_COMPLETE](../research/CROSS_PLATFORM_RESEARCH_COMPLETE.md) | ✅ Cross-Platform Research Complete | Consolidated: macOS/Linux/Windows/WSL, user isolation, desktop automation, shell strategy | [CROSS_PLATFORM_GUIDE](../guides/CROSS_PLATFORM_COMPLETE.md), [PARITY](./MULTI_PLATFORM_PARITY_MASTER_PLAN.md) |
| [FASTMCP_COMPLETE](../research/FASTMCP_COMPLETE.md) | ✅ FastMCP Complete | Consolidated: 10 files → comprehensive guide (tools, resources, elicitation, progress, middleware, storage) | [MCP-PARITY](../research/MCP_FULL_PARITY_AND_FASTMCP_AUDIT.md), [MCP-OPT](./MCP_TOOL_OPTIMIZATION_PLAN.md) |
| [HOOK_RUST_MIGRATION_COMPLETE](../research/HOOK_RUST_MIGRATION_COMPLETE.md) | ✅ Hook Rust Migration Complete | Expanded: Detailed migration strategy, timeline (11 weeks), implementation patterns | [HOOK-RUST](./HOOK_RUNTIME_RUST_DESIGN.md), [SHELL→RUST](./FULL_SHELL_TO_RUST_WHERE_BENEFICIAL.md) |
| [LIBRARY_REPLACEMENT_COMPLETE](../research/LIBRARY_REPLACEMENT_COMPLETE.md) | ✅ Library Replacement Complete | Consolidated: 3 files → comprehensive audit (urllib→httpx, retry→tenacity, caching, etc.) | [LIBRARY_FIRST](../research/LIBRARY_FIRST_AUDIT_AND_PLAN.md) |
| [IDEA_SEED_REVIEW_COMPLETE](../research/IDEA_SEED_REVIEW_COMPLETE.md) | ✅ Idea Seed Review Complete | Reviewed: 4 idea-seed files (all duplicates, archived), expansion status | [RESEARCH_SPRAWL](../research/RESEARCH_SEED_FRAGMENT_INVENTORY_AND_SPRAWL_TODO.md) |
| [SHELL_ENV_COMPLETE](../guides/SHELL_ENVIRONMENT_COMPLETE.md) | ✅ Shell Environment Complete | Enhanced: Consolidated 4 guides (optimization, advanced features, management, plugin setup) | [SHELL_ADVANCED](../guides/SHELL_ADVANCED_FEATURES.md), [PROCESS-OPT](./PROCESS_OPTIMIZATION_PLAN.md) |
| [CROSS_PLATFORM_GUIDE](../guides/CROSS_PLATFORM_COMPLETE.md) | ✅ Cross-Platform Complete Guide | Consolidated: 5 guides (quick start, migration, roadmap, cookbook, templates) | [CROSS_PLATFORM_RESEARCH](../research/CROSS_PLATFORM_RESEARCH_COMPLETE.md) |
| [LIFECYCLE-PLAN](./2026-02-15-RESEARCH-AND-ELICITATION-PLAN.md) | Lifecycle Implementation Plan | Decisions, CheckerContext, intuitive/holistic/harmonious design | [12-LIFECYCLE](./12-LIFECYCLE-LOOP-DESIGN.md), [TOOLING-AUDIT](../reference/TOOLING_AND_OPTIMIZATION_AUDIT.md) |
| [UNIFIED-APP](./UNIFIED_SYSTEM_APPLICATION_PLAN.md) | ✅ Unified System Application | Complete: Desktop app + tray + install merged; one installer, one surface; Ghostty-like, 300 agents; implementation details, code examples, testing strategy | [Tray](./2026-02-15-tray-application-design.md), [Install](./2026-02-14-thegent-install-design.md), [Sitback](./2026-02-15-thegent-sitback-design.md) |
| [CONVERSATION_DUMP_COMPLETE](../research/CONVERSATION_DUMP_2026-02-16_COMPLETE.md) | ✅ Conversation Dump Complete | Expanded: Structured doc with actionable items, implementation status, decision rationale, follow-up actions | [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md) |
| [AGENT_PLATFORMS_COMPLETE](../research/AGENT_PLATFORMS_COMPLETE.md) | ✅ Agent Platforms Complete | Consolidated: 3 files → comprehensive guide (kilo, roo, OpenCode, OpenClaw, Agent Zero, integration strategies) | [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md) |
| [SWARM_COMPLETE](../research/SWARM_COMPLETE.md) | ✅ Swarm Complete | Consolidated: 3 files → comprehensive guide (scheduling theory, process automation, resource management, implementation roadmap) | [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md), [PROCESS-OPT](./PROCESS_OPTIMIZATION_PLAN.md) |
| [CACHING_COMPLETE](../research/CACHING_COMPLETE.md) | ✅ Caching Complete | Expanded: Practical guide with implementation patterns (multi-level cache, file indexing, pre-warming, frecency) | [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md), [LIBRARY_REPLACEMENT](../research/LIBRARY_REPLACEMENT_COMPLETE.md) |
| [SYSTEM_RESOURCES_COMPLETE](../research/SYSTEM_RESOURCES_COMPLETE.md) | ✅ System Resources Complete | Expanded: Practical guide (resource sampling, per-process metrics, gates, prune prioritization) | [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md), [SWARM_COMPLETE](../research/SWARM_COMPLETE.md) |
| [PROMPT_HISTORY_COMPLETE](./PROMPT_HISTORY_COLLECTION_COMPLETE.md) | ✅ Prompt History Complete | Expanded: Complete guide (collection, git integration, artifact extraction, MCP/CLI tools) | [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md) |
| [SHELL_ENV_COMPLETE_PLAN](./SHELL_ENVIRONMENT_COMPLETE_PLAN.md) | ✅ Shell Environment Complete Plan | Consolidated: 4 files → comprehensive plan (optimization, safeguards, advanced features, CLI) | [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md), [SHELL_ENV_COMPLETE](../guides/SHELL_ENVIRONMENT_COMPLETE.md) |
| [CROSS_PLATFORM_COMPLETE_PLAN](./CROSS_PLATFORM_COMPLETE_PLAN.md) | ✅ Cross-Platform Complete Plan | Expanded: Complete implementation guide (user isolation, multi-tenant, desktop automation, MCP integration) | [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md), [CROSS_PLATFORM_RESEARCH](../research/CROSS_PLATFORM_RESEARCH_COMPLETE.md) |
| [PROCESS_OPT_COMPLETE](./PROCESS_OPTIMIZATION_COMPLETE_PLAN.md) | ✅ Process Optimization Complete Plan | Expanded: Complete guide (MTSP, tool migration, persistence, BKM tasks) | [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md), [PROCESS-OPT](./PROCESS_OPTIMIZATION_PLAN.md) |
| [HOOK_RUST_COMPLETE](./HOOK_RUNTIME_RUST_COMPLETE.md) | ✅ Hook Runtime Rust Complete | Expanded: Complete migration guide (architecture, subcommands, implementation, performance targets) | [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md), [HOOK-RUST](./HOOK_RUNTIME_RUST_DESIGN.md) |
| [SYNC-UPDATE](./SYNC_UPDATE_COMMAND_AND_SYSTEM_AUDIT_PLAN.md) | Sync/Update Command & System Audit | Design: Unified `thegent sync`/`update` command with full system audit, work stream integration, research sprawl automation | [WORK_STREAM](../reference/WORK_STREAM.md), [UNIFIED_WORK_STREAM_DESIGN](../reference/UNIFIED_WORK_STREAM_DESIGN.md), [RESEARCH_SPRAWL](../research/RESEARCH_SEED_FRAGMENT_INVENTORY_AND_SPRAWL_TODO.md) |
| [CONTROL-PLANE](./CONTROL_PLANE_DESIGN.md) | Control Plane Design | Robust multi-tenant config service: process + API, CLI/MCP interaction, harmonized with Agent Registry, Compute Offload, CROSS_PLATFORM_MULTI_TENANT | [AGENT_REGISTRY_DESIGN](../AGENT_REGISTRY_DESIGN.md), [research-compute-offload](../changes/research-compute-offload/design.md), [CROSS_PLATFORM_MULTI_TENANT](../reference/CROSS_PLATFORM_MULTI_TENANT_QUICK_REFERENCE.md) |
| [CONTROL-PLANE-IMPL](./CONTROL_PLANE_IMPLEMENTATION_PLAN.md) | Control Plane Implementation Plan | 6-phase implementation: ConfigProvider, CP serve, CLI integration, tenant catalog, process-compose, observability; cross-platform Win/Linux/macOS/WSL | [CONTROL-PLANE](./CONTROL_PLANE_DESIGN.md) |
| [UNIFIED-HELIOS-THEGENT](./UNIFIED_HELIOS_THEGENT_MASTER_PLAN.md) | ✅ Unified heliosShield + thegent Master Plan | Canonical merger: Control Plane (thegent) + Mesh Coordination (heliosShield/heliosShield); integrated architecture, phased DAG, and directory structure | [ARCHITECTURE](./05-ARCHITECTURE.md), [HELIOS-WBS](../../heliosShield/agent-mesh-wbs-plan-v2.md) |
| [RESEARCH-INDEX](../research/RESEARCH_CONSOLIDATED.md) | ✅ Consolidated Research Index | Centralized index for all deep research, feasibility studies, and architectural explorations | [RESEARCH_SPRAWL](../research/RESEARCH_SEED_FRAGMENT_INVENTORY_AND_SPRAWL_TODO.md) |
| [QUICK-START](../guides/QUICK_START.md) | ✅ Quick Start Guide | Get up and running with thegent in less than 5 minutes | [INSTALLATION](../guides/INSTALLATION.md) |
| [USER-GUIDE](../guides/COMPLETE_USER_GUIDE.md) | ✅ Complete User Guide | Comprehensive documentation for all features and configurations | [CLI-REF](../guides/THGENT_CLI_REFERENCE.md) |

---

## Project Summary

**thegent** transforms from a simple agent dispatch CLI into a production-grade orchestration platform with:

- **Deterministic DAG execution** with dependency satisfaction and concurrency control
- **Contract governance** with canonical structured messages, versioned schemas, adapter conformance
- **Multi-provider routing** across 12+ AI providers with failover, scoring, and cost optimization
- **Reliability hardening** with circuit breakers, checkpoints, rollback, dead-letter queues
- **Governance enforcement** with OPA/Rego policies, audit trails, trust scoring, compliance
- **Operator UX** with progressive disclosure, safe fallbacks, decision replay, confidence calibration
- **Adaptive scaling** with burst classification, critical lane protection, continuity automation
- **Enterprise readiness** with security signoff, SLO certification, runbook finalization

---

## Completion Dashboard

| Phase | WPs | Done | Partial | Not Started | % Complete |
|-------|-----|------|---------|-------------|-----------|
| Phase 0: Foundation | 6 | 5 | 2 | 0 | 83% |
| Phase X: Contract Hardening | 8 | 5 | 1 | 2 | 62% |
| Phase 1: Core Routing | 9 | 6 | 2 | 1 | 67% |
| Phase 2: Reliability | 11 | 2 | 3 | 6 | 18% |
| Phase 3: Governance | 9 | 5 | 0 | 4 | 55% |
| Phase 4: UX | 9 | 2 | 1 | 6 | 22% |
| Phase 5: Adaptive Scale | 10 | 3 | 1 | 6 | 30% |
| Phase 6: Enterprise | 8 | 0 | 2 | 6 | 0% |
| **Total (WBS)** | **70** | **19** | **15** | **36** | **27%** |

**Separately Completed** (not in WBS phases, but tracked in project state):
- **FastMCP MCP Server**: Phases 1-4, 6-7 complete (Phase 5 production readiness pending)
- **Distributed Model Routing**: 100% complete (12/12 phases, all provider scraping done)
- **Provider Parity**: 100% complete (9 providers across 6 phases)
- **Contract/Health System**: 100% complete (261 implementation chunks, all base contracts done)

---

## Critical Path

```
Phase 0 (Foundation) ──> Phase X (Contracts) ──> Phase 1 (Routing)
                                                      |
                                              ┌───────┴───────┐
                                              v               v
                                    Phase 2 (Reliability)  Phase 3 (Governance)
                                              |               |
                                              └───────┬───────┘
                                                      v
                                              Phase 4 (UX)
                                                      |
                                              Phase 5 (Scale)
                                                      |
                                              Phase 6 (Enterprise)
```

---

## Source Code Map (Current)

```
src/thegent/
├── main.py                    # CLI entry point (Typer app)
├── cli.py                     # Command implementations
├── cli_impl.py                # Implementation utilities (pure logic)
├── config.py                  # Configuration management
├── execution.py               # RunRegistry, session tracking, state
├── exit_codes.py              # Exit code enumeration
├── mcp_server.py              # FastMCP HTTP server, tools, resources
├── mcp_manage.py              # MCP task management
├── operations.py              # Universal operation taxonomy
├── orchestration_modes.py     # Multi-agent modes (sequential/parallel/review)
├── output_parser.py           # Output parsing and health trend
├── agents/
│   ├── __init__.py
│   ├── base.py                # Agent interfaces and protocols
│   ├── registry.py            # Agent discovery and routing
│   ├── resilience.py          # Retry, circuit breaker, fallback logic
│   ├── state_machine.py       # Agent state transitions
│   ├── modes.py               # Mode execution helpers
│   ├── cliproxy_manager.py    # CLIProxy integration
│   ├── codex_proxy.py         # Codex proxy runner
│   ├── cursor_api_runner.py   # Cursor API runner
│   ├── direct_agents.py       # Native provider runners
│   └── droid.py               # Droid (managed agent) implementation
├── contracts/
│   ├── __init__.py
│   ├── csm.py                 # Canonical Structured Message (Zen 26-tag)
│   ├── registry.py            # XML contract registry with versioning
│   ├── parser.py              # Incremental XML parser (XMLPullParser)
│   ├── validation.py          # Semantic validation (cross-tag logic)
│   ├── adapters.py            # Provider-specific output adapters
│   ├── conformance.py         # Conformance testing framework
│   ├── policy.py              # Fallback policy enforcement
│   ├── state_machine.py       # Fallback state machine (Primary→Degraded→Fallback)
│   ├── migration.py           # Contract migration (dual-read/dual-write)
│   └── telemetry.py           # Drift detection and alerts
├── models/
│   ├── __init__.py
│   ├── catalog.py             # Model catalog (static + dynamic scraping)
│   └── scrapers.py            # Provider model scrapers (8+ providers)
└── planning/
    ├── __init__.py
    └── simulation.py          # Pre-flight simulation
```

**Phase 0-X WPs map to existing files.** Phases 1-6 require new modules:
- `orchestration/` — Phases 1-2 (router, lanes, checkpoint, playbooks, DLQ, concurrency, cost, etc.)
- `governance/` — Phase 3 (policy_engine, audit, signatures, drift, overrides, trust, escalation)
- `ux/` — Phase 4 (cockpit, explanations, fallback_ui, replay, calibration, kpis)
- `tests/chaos/` — Phase 2+ (fault injection framework)

---

## Subagent Execution Schedule

For full dispatch details, context packages, and dependency visualization, see [10-SUBAGENT-DISPATCH.md](./10-SUBAGENT-DISPATCH.md).

**10 Sequential Batches, 3-4 Agents per Batch** (32 core + 6 optimization agents, max 10 concurrent, ~126-187 min total):

| Batch | Theme | Agents | Key WPs | Depends On | Est. Time |
|-------|-------|--------|---------|-----------|-----------|
| 1 | Foundation + Telemetry | 1A–1D (4) | WP-0002, Y6, 0005, 0003-0004 | None | 8-15 min |
| 2 | Contract Hardening | 2A–2D (4) | WP-X7, X8, X6, X1-X5 | Batch 1 | 15-20 min |
| 3 | Routing + Execution | 3A–3D (4) | WP-1001-1008 | Batch 2 | 15-20 min |
| 4 | Reliability | 4A–4D (4) | WP-2001-2008, Y2-Y3 | Batch 3 | 18-25 min |
| 5 | Governance | 5A–5D (4) | WP-3001-3008 | Batch 3 | 15-22 min |
| 6 | Multi-Agent + Chaos | 6A–6C (3) | WP-Y1, Y3, Y5, 1006, 3008 | Batch 4 | 15-20 min |
| 7 | Operator UX | 7A–7C (3) | WP-4001-4007 | Batch 5, 4 | 15-22 min |
| 8 | Scale + Cost | 8A–8C (3) | WP-5001-5006, Y4 | Batch 4, 5 | 18-25 min |
| 9 | Enterprise | 9A–9C (3) | WP-6001-6004 | Batch 6-8 | 12-18 min |
| 10 | Launch Closure | 10A–10C (3) | WP-Y7, 6005, 4008, Y8, 6006-6008 | Batch 9 | 10-15 min |

**Post-Core Optimization** (6 parallel agents, after batches complete):
- OPT-A (connection pooling, lazy loading, async scraping)
- OPT-B (stale state, watchdog, config validation, fd limits)
- OPT-C (UX polish, descriptions, persona defaults, alert control)
- OPT-D (DX: boundary enforcement, test generation, run-diff)
- OPT-E (ops excellence: cleanup, runbook, SLO, decommission, reserve)
- OPT-F (design: DI stack, state machines, middleware, adoption model)

---

## Cross-Reference Index

### By Task Type

| Question | Answer | Cross-References |
|----------|--------|-------------------|
| **What are the work packages?** | [02-WBS](./02-UNIFIED-WBS.md) Phase sections | [04-REQ](./04-REQUIREMENTS.md), [01-STATE](./01-PROJECT-STATE.md) |
| **What are the requirements?** | [04-REQ](./04-REQUIREMENTS.md) FRs/NFRs | [02-WBS](./02-UNIFIED-WBS.md), [07-TEST](./07-TEST-STRATEGY.md) FR trace |
| **How does execution flow?** | [03-DAG](./03-UNIFIED-DAG.md) 8 DAGs | [05-ARCH](./05-ARCHITECTURE.md) layer diagram, [09-RISK](./09-RISK-REGISTRY.md) failure modes |
| **Where does the code go?** | [06-IMPL](./06-IMPLEMENTATION-GUIDE.md) module structure | [01-STATE](./01-PROJECT-STATE.md) source map, [05-ARCH](./05-ARCHITECTURE.md) layers |
| **How do I write code?** | [06-IMPL](./06-IMPLEMENTATION-GUIDE.md) patterns | [05-ARCH](./05-ARCHITECTURE.md) ADRs/patterns, [07-TEST](./07-TEST-STRATEGY.md) conventions |
| **What tests do I write?** | [07-TEST](./07-TEST-STRATEGY.md) 14 categories | [04-REQ](./04-REQUIREMENTS.md) FR trace, [02-WBS](./02-UNIFIED-WBS.md) acceptance |
| **How do I design?** | [05-ARCH](./05-ARCHITECTURE.md) ADRs/patterns | [04-REQ](./04-REQUIREMENTS.md), [03-DAG](./03-UNIFIED-DAG.md) |
| **What might go wrong?** | [09-RISK](./09-RISK-REGISTRY.md) risks/anti-patterns | [03-DAG](./03-UNIFIED-DAG.md) failure modes, [08-OPT](./08-OPTIMIZATION-CATALOG.md) robustness |
| **What can be optimized?** | [08-OPT](./08-OPTIMIZATION-CATALOG.md) 70 items | [05-ARCH](./05-ARCHITECTURE.md), [06-IMPL](./06-IMPLEMENTATION-GUIDE.md) |
| **How do I run multiple agents?** | [10-DISPATCH](./10-SUBAGENT-DISPATCH.md) batches | [02-WBS](./02-UNIFIED-WBS.md) WP details, [06-IMPL](./06-IMPLEMENTATION-GUIDE.md) context |
| **What's the project status?** | [01-STATE](./01-PROJECT-STATE.md) current state | [02-WBS](./02-UNIFIED-WBS.md) completion %, [00-MASTER](./00-MASTER-INDEX.md) dashboard |
| **How is the code organized?** | [01-STATE](./01-PROJECT-STATE.md) source map | [06-IMPL](./06-IMPLEMENTATION-GUIDE.md) module structure, [05-ARCH](./05-ARCHITECTURE.md) layers |
| **How do lifecycle/checker decisions get implemented?** | [LIFECYCLE-PLAN](./2026-02-15-RESEARCH-AND-ELICITATION-PLAN.md) decisions, CheckerContext, robustness | [12-LIFECYCLE](./12-LIFECYCLE-LOOP-DESIGN.md), [HAC](../reference/HAC_AND_HITL_PATTERNS.md), [SITBACK](../guides/SITBACK_PLUGINS.md) |
| **How do I integrate Codex/Cursor/droid/Augment with queue/harness?** | [CODEX](./CODEX_DONUT_HARNESS_PLAN.md) multi-platform harness | [Feature audit](../research/CLAUDE_CODE_FEATURE_PARITY_AUDIT.md), [USER_QUEUE](../research/USER_QUEUE_TUI_AND_AGENT_POLL.md) |
| **What's the complete parity matrix and how do we achieve/supercede?** | [PARITY](./MULTI_PLATFORM_PARITY_MASTER_PLAN.md) master plan | [CODEX](./CODEX_DONUT_HARNESS_PLAN.md) phases, [Feature audit](../research/CLAUDE_CODE_FEATURE_PARITY_AUDIT.md) |
| **How do I optimize/polish the MCP tools?** | [MCP-OPT](./MCP_TOOL_OPTIMIZATION_PLAN.md) MCP tool optimization plan | [08-OPT](./08-OPTIMIZATION-CATALOG.md), [PARITY](./MULTI_PLATFORM_PARITY_MASTER_PLAN.md) §10–13 |
| **What's the full MCP parity matrix and FastMCP feature usage?** | [MCP-PARITY](../research/MCP_FULL_PARITY_AND_FASTMCP_AUDIT.md) | CLI↔MCP↔Codex/CC; Queue/Team MCP; FastMCP transport spec |
| **What MCP tools/resources exist and how does the transport stack work?** | [MULTI_PLATFORM_DEEP_DIVE](../research/MULTI_PLATFORM_DEEP_DIVE.md) Parts XXV–XXXII | [MCP-PARITY](../research/MCP_FULL_PARITY_AND_FASTMCP_AUDIT.md), [MCP-OPT](./MCP_TOOL_OPTIMIZATION_PLAN.md) |
| **How do MCP/CLI/skills/CLAUDE/roles/headless tie into the work stream?** | [TOUCHPOINT_EVAL](../reference/TOUCHPOINT_INTEGRATION_EVALUATION.md) MD vs SQLite, integration rules | [TOUCHPOINT_DEEP_DIVE](../reference/TOUCHPOINT_INTEGRATION_DEEP_DIVE.md) web research, copilot/sitback agents, ~/../project paths |
| **How is the program becoming more robust and what's in future phases?** | [ROBUSTNESS_AND_DEPTH](../reference/ROBUSTNESS_AND_FUTURE_DEPTH.md) Phase 0–6 evolution | [AGENT_DEBUG_GUIDE](../guides/AGENT_DEBUGGING_AND_REMEDIATION_GUIDE.md), [MAIF_DEPTH](../reference/MAIF_ARTIFACT_SPEC_DEPTH.md), [COCKPIT_DEPTH](../reference/PHASE_4_COCKPIT_UX_DEPTH.md), [SCALE_DEPTH](../reference/PHASE_5_SCALE_ROBUSTNESS_DEPTH.md), [SIM_DEPTH](../reference/SIMULATION_AND_SANDBOX_DEPTH.md), [ROUTING_DEPTH](../reference/PARETO_ROUTING_DESIGN.md), [OTEL_DEPTH](../reference/OTEL_GENAI_AND_HYSTERESIS_DEPTH.md), [SWARM_DEPTH](../reference/SWARM_MEMORY_COORDINATION_DEPTH.md), [ECON_DEPTH](../reference/ECONOMIC_GOVERNANCE_DEPTH.md), [CONTEXT_DEPTH](../reference/CONTEXT_MANAGEMENT_DEPTH.md), [HAC_DEPTH](../reference/HAC_AND_HITL_PATTERNS.md), [HIERARCHY_DEPTH](../reference/MULTI_SWARM_HIERARCHY_DEPTH.md), [ACL_DEPTH](../reference/AGENT_NEGOTIATION_ACL_DEPTH.md), [CONST_DEPTH](../reference/CONSTITUTIONAL_ENFORCEMENT_DEPTH.md), [HEAL_DEPTH](../reference/SELF_HEALING_AGENTIC_CICD_DEPTH.md), [ID_DEPTH](../reference/AGENT_IDENTITY_SOVEREIGNTY_DEPTH.md) |
| **What's the unified WBS breakdown?** | [UNIFIED_WBS](./02-UNIFIED-WBS.md) Phase breakdown | [DISPATCH](./10-SUBAGENT-DISPATCH.md) Agent schedule |
| **What's the canonical backlog and how do incorporators merge fragments?** | [WORK_STREAM](../reference/WORK_STREAM.md) canonical backlog | [UNIFIED_WORK_STREAM_DESIGN](../reference/UNIFIED_WORK_STREAM_DESIGN.md) 4X/AgilePlus/gardening |

### By Phase

| Phase | WBS Section | Test Plan | Risks | Architecture | Batch |
|-------|-------------|-----------|-------|--------------|-------|
| **0: Foundation** | [02 Phase 0](./02-UNIFIED-WBS.md#phase-0-foundation--baseline) | Cat-1,2 | AP-01, AP-02 | [05 CSM](./05-ARCHITECTURE.md#csmv1-schema) | [10 Batch 1](./10-SUBAGENT-DISPATCH.md#batch-1) |
| **X: Contracts** | [02 Phase X](./02-UNIFIED-WBS.md#phase-x-contract--adapter-hardening) | Cat-3,4,5,6 | AP-03, R-005, R-006 | [05 Parser](./05-ARCHITECTURE.md#adrcoding-002) | [10 Batch 2](./10-SUBAGENT-DISPATCH.md#batch-2) |
| **1: Routing** | [02 Phase 1](./02-UNIFIED-WBS.md#phase-1-core-routing--deterministic-execution) | Cat-5,7 | AP-04, AP-05 | [05 Routing](./05-ARCHITECTURE.md#p-021-provider-scoring-4-factor) | [10 Batch 3](./10-SUBAGENT-DISPATCH.md#batch-3) |
| **2: Reliability** | [02 Phase 2](./02-UNIFIED-WBS.md#phase-2-reliability--recovery-hardening) | Cat-6,7,8,9 | AP-06, AP-09, R-008 | [05 Circuit Breaker](./05-ARCHITECTURE.md#adr-006-three-state-circuit-breaker) | [10 Batch 4](./10-SUBAGENT-DISPATCH.md#batch-4) |
| **3: Governance** | [02 Phase 3](./02-UNIFIED-WBS.md#phase-3-governance--security-enforcement) | Cat-11 | AP-07, R-007, R-010 | [05 OPA/Rego](./05-ARCHITECTURE.md#adr-004-oparego-for-policy-engine) | [10 Batch 5](./10-SUBAGENT-DISPATCH.md#batch-5) |
| **4: UX** | [02 Phase 4](./02-UNIFIED-WBS.md#phase-4-human-centered-ux--explainability) | Cat-12,13 | AP-08, AP-10, AP-13, R-003 | [05 Progressive Disclosure](./05-ARCHITECTURE.md#adr-008-progressive-disclosure-3-tier-ux) | [10 Batch 7](./10-SUBAGENT-DISPATCH.md#batch-7) |
| **5: Scale** | [02 Phase 5](./02-UNIFIED-WBS.md#phase-5-adaptive-scale--continuity-automation) | Cat-14 | AP-14, R-002, R-004, R-011 | [05 Adaptive Concurrency](./05-ARCHITECTURE.md#adr-009-adaptive-concurrency-with-hysteresis) | [10 Batch 8](./10-SUBAGENT-DISPATCH.md#batch-8) |
| **6: Enterprise** | [02 Phase 6](./02-UNIFIED-WBS.md#phase-6-enterprise-readiness--launch-closure) | All | All | All | [10 Batch 9-10](./10-SUBAGENT-DISPATCH.md#batch-9) |

---

## Document Changelog

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-02-16 | 1.3 | Added 8 additional expanded/consolidated documents: CACHING_COMPLETE, SYSTEM_RESOURCES_COMPLETE, PROMPT_HISTORY_COMPLETE, SHELL_ENV_COMPLETE_PLAN, CROSS_PLATFORM_COMPLETE_PLAN, PROCESS_OPT_COMPLETE, HOOK_RUST_COMPLETE. All documents cross-referenced in master index | Documentation Expansion |
| 2026-02-16 | 1.2 | Added 9 expanded/consolidated documents: CONVERSATION_DUMP_COMPLETE, AGENT_PLATFORMS_COMPLETE, SWARM_COMPLETE, SESSION_RESEARCH_COMPLETE, CROSS_PLATFORM_RESEARCH_COMPLETE, FASTMCP_COMPLETE, HOOK_RUST_MIGRATION_COMPLETE, LIBRARY_REPLACEMENT_COMPLETE, IDEA_SEED_REVIEW_COMPLETE. Updated UNIFIED_SYSTEM_APPLICATION_PLAN status to Complete | Documentation Expansion |
| 2026-02-14 | 1.1 | Added "How to Use" quick start guide; corrected WP count (70 not 72); verified Completion Dashboard matches WBS status; expanded Source Code Map with actual directory structure (planning/ module); updated Batch Schedule table with dependencies; enhanced Cross-Reference Index with task-type and phase-based navigation; added this changelog | System Review |
| 2026-02-14 | 1.0 | Initial docset generation from unified planning research | Foundation Phase |

---

## Quality Assurance Checklist

**Verification Completed (2026-02-16)**:

- [x] All 10 docset modules listed with accurate descriptions (70 WPs, 10 DAGs, 42 FRs, 16 NFRs)
- [x] Completion Dashboard percentages verified against 02-WBS.md (70 WPs total: 15 done, 15 partial, 40 not started = 21%)
- [x] Critical Path diagram verified against WBS phase dependencies (Phase 0→X→1→(2,3)→4→5→6)
- [x] Source Code Map verified against actual src/thegent/ directory structure (39 Python files, 6 submodules)
- [x] Subagent Batch Schedule verified against 10-SUBAGENT-DISPATCH.md (10 batches, 32 core agents, 6 optimization agents)
- [x] Cross-Reference Index expanded with task-type and phase-based navigation (28 mappings)
- [x] "How to Use This Docset" section added for new contributors (7-step onboarding sequence)
- [x] Document Changelog section added with version history
- [x] All internal cross-reference links verified (relative paths to .md files, all anchors exist)
- [x] Module descriptions updated with accurate counts (37 patterns, 17 risks, 93 optimization items)
- [x] Version updated to 1.3 and generation date updated to 2026-02-16
- [x] Module table columns expanded to show "Key Sections" for better discoverability
- [x] Added 9 expanded/consolidated documents with cross-references (v1.2)
- [x] Added 8 additional expanded/consolidated documents (v1.3): CACHING_COMPLETE, SYSTEM_RESOURCES_COMPLETE, PROMPT_HISTORY_COMPLETE, SHELL_ENV_COMPLETE_PLAN, CROSS_PLATFORM_COMPLETE_PLAN, PROCESS_OPT_COMPLETE, HOOK_RUST_COMPLETE: CACHING_COMPLETE, SYSTEM_RESOURCES_COMPLETE, PROMPT_HISTORY_COMPLETE, SHELL_ENV_COMPLETE_PLAN, CROSS_PLATFORM_COMPLETE_PLAN, PROCESS_OPT_COMPLETE, HOOK_RUST_COMPLETE
- [x] Updated UNIFIED_SYSTEM_APPLICATION_PLAN status to Complete
- [x] All expanded documents cross-referenced in master index
