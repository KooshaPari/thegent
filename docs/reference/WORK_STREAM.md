# Unified Work Stream — Canonical

> **Purpose**: Single source of truth for all project work. All agents read this file. See [UNIFIED_WORK_STREAM_DESIGN.md](./UNIFIED_WORK_STREAM_DESIGN.md) for design and incorporator workflow.
> **Read**: Before picking work. **Claim**: Append to CLAIMED. **Update**: Move to COMPLETED when done.

---

## Instructions for Agents

1. **Before picking work**: Read BACKLOG; filter out items in CLAIMED; pick items whose Depends are satisfied.
2. **When starting**: Append to CLAIMED (ID, Agent, Started). Use unique agent_id (e.g. `agent-1`, `session-{hash}`).
3. **When completing**: Remove from CLAIMED; add to COMPLETED; update source file (e.g. 02-UNIFIED-WBS.md) if applicable.
4. **Incorporator**: Run `thegent plan incorporate` (or incorporator agent) to merge new fragments from plans, research, specs.

---

## BACKLOG (not started)

| ID | Title | Source | Priority | Depends |
|----|-------|--------|----------|---------|
| research-cross-platform-remote | Remote compute implementation | CROSS_PLATFORM_RESEARCH_CONSOLIDATED.md | P2 | HYBRID_ENV |
| research-hook-rust-phase2 | Migrate hooks to use thegent-hooks (opt-in) | HOOK_RUST_MIGRATION_RESEARCH_SYNTHESIS_EXPANDED.md | P1 | ✅ Phase 1 Complete |
| research-hook-rust-phase3 | Make thegent-hooks default, deprecate common.sh | HOOK_RUST_MIGRATION_RESEARCH_SYNTHESIS_EXPANDED.md | P1 | research-hook-rust-phase2 |
| research-hook-rust-phase4 | Native Rust hooks for critical paths | HOOK_RUST_MIGRATION_RESEARCH_SYNTHESIS_EXPANDED.md | P2 | research-hook-rust-phase3 |
| research-hook-rust-gix | Optional gix integration for Git operations | HOOK_RUST_MIGRATION_RESEARCH_SYNTHESIS_EXPANDED.md | P2 | ✅ Phase 1 Complete |
| research-hook-rust-benchmarks | Performance benchmarks and comparison | HOOK_RUST_MIGRATION_RESEARCH_SYNTHESIS_EXPANDED.md | P1 | ✅ Phase 1 Complete |
| research-library-http | Replace urllib with httpx (7+ files) | PACKAGE_REPLACEMENT_IMPLEMENTATION_PLAN.md | P1 | ✅ Complete |
| research-library-retry | Migrate manual retry loops to tenacity (4 files) | LIBRARY_REPLACEMENT_CONSOLIDATED.md | P1 | ✅ Complete |
| research-library-watchdog | Replace polling with watchdog (1 file) | PACKAGE_REPLACEMENT_IMPLEMENTATION_PLAN.md | P1 | ✅ Complete |
| research-library-cache | Replace custom caching with cachetools (5 files) | LIBRARY_REPLACEMENT_CONSOLIDATED.md | P2 | ✅ Complete |
| research-library-circuit-breaker | Replace custom circuit breaker with pybreaker (1 file) | LIBRARY_REPLACEMENT_CONSOLIDATED.md | P2 | ✅ Complete |
| research-library-yaml | Replace PyYAML with ruamel.yaml (15 files) | LIBRARY_REPLACEMENT_CONSOLIDATED.md | P2 | ✅ Complete |
| research-library-ansi | Replace custom ANSI stripping with rich (5 files) | LIBRARY_REPLACEMENT_CONSOLIDATED.md | P2 | ✅ Complete |
| research-library-diskcache | Replace scrapers cache with diskcache (1 file) | PACKAGE_REPLACEMENT_IMPLEMENTATION_PLAN.md | P2 | ✅ Complete |
| research-library-psutil | Add psutil for resource monitoring (2 files) | PACKAGE_REPLACEMENT_IMPLEMENTATION_PLAN.md | P2 | ✅ Complete |
| research-library-md5-sha256 | Replace md5 with sha256 (1 file) | PACKAGE_REPLACEMENT_IMPLEMENTATION_PLAN.md | P3 | ✅ Complete |
| research-library-env-settings | Consolidate os.environ → ThegentSettings (15+ files) | PACKAGE_REPLACEMENT_IMPLEMENTATION_PLAN.md | P3 | - |
| research-library-tomlkit | Add tomlkit to dependencies | PACKAGE_REPLACEMENT_IMPLEMENTATION_PLAN.md | P3 | ✅ Complete |
| research-phase13-cost-sensitivity | Cost-sensitivity experiment framework | PHASE_DOCUMENTS_EXPANDED.md | P2 | WP-5003, research-economic-governance |
| research-phase13-policy-federation | Multi-tenant policy federation | PHASE_DOCUMENTS_EXPANDED.md | P1 | WP-3001, research-cross-platform-coordination |
| research-phase13-tenant-boundary-tests | Tenant boundary test matrix | PHASE_DOCUMENTS_EXPANDED.md | P1 | research-cross-platform-isolation |
| research-phase13-compliance-profiles | Compliance profile mapping | PHASE_DOCUMENTS_EXPANDED.md | P2 | WP-3006, research-cross-platform-security |
| research-phase14-autonomous-learning | Autonomous learning surface map | PHASE_DOCUMENTS_EXPANDED.md | P2 | WP-5001, research-pareto-routing |
| research-phase14-cost-sensing-tests | Cost-sensing test matrix | PHASE_DOCUMENTS_EXPANDED.md | P2 | WP-5003, research-phase13-cost-sensitivity |
| research-phase15-enterprise-compliance-tests | Enterprise compliance test matrix | PHASE_DOCUMENTS_EXPANDED.md | P2 | research-phase13-compliance-profiles |
| research-phase15-enterprise-lifecycle | Enterprise lifecycle surface map | PHASE_DOCUMENTS_EXPANDED.md | P2 | research-cross-platform-coordination |
| research-governance-escalation-dlq | Integrate escalation queue with DLQ | GOVERNANCE_WP_GAPS_EXPANDED.md | P2 | WP-3008, WP-2002 |
| research-governance-policy-federation | Multi-tenant policy federation | GOVERNANCE_WP_GAPS_EXPANDED.md | P1 | WP-3001, research-phase13-policy-federation |
| research-governance-compliance-reports | Automated compliance reporting | GOVERNANCE_WP_GAPS_EXPANDED.md | P2 | WP-3006, research-phase13-compliance-profiles |
| research-cost-routing-implementation | Implement advanced cost routing (deferred) | COST_ROUTING_DEFERRED_EXPANDED.md | P2 | WP-5003, unblock criteria |
| research-always-write-dumps | CLAUDE.md: always write conversation dumps to docs/ | CONVERSATION_DUMP_2026-02-16.md §6 | P2 | — |
| scratch-doctor-fix | Proactive doctor --fix for detected environment issues | scratchpad/session_review.md | P2 | — |
| scratch-thegent-shims | Ship thegent-shims (Rust) for git/grep/find/agent; Phase 2 FULL_SHELL_TO_RUST | FULL_SHELL_TO_RUST_WHERE_BENEFICIAL.md | P1 | — |
| scratch-doctor-shim-check | thegent doctor: check shim version and binary availability | scratchpad/session_review.md | P2 | — |
| phase13-compliance-profile | Compliance profile mapping (EU-AI-ACT, US-SEC, SOX, GDPR) | phase13-compliance-profile-mapping.md | P2 | WP-13002 |
| phase13-tenant-boundary | Tenant boundary test matrix (TB-001–TB-005) | phase13-tenant-boundary-test-matrix.md | P2 | phase13-policy-federation |
| phase13-policy-federation | Policy federation surface map (FederatedPolicyEngine) | phase13-policy-federation-surface-map.md | P2 | — |
| phase13-cost-sensitivity | Cost sensitivity experiment (baseline + A/B) | phase13-cost-sensitivity-experiment-plan.md | P2 | phase13-policy-federation |
| phase14-cost-sensing | Cost sensing and learning test matrix (AL-001–AL-006) | phase14-cost-sensing-test-matrix.md | P2 | WP-5003 |
| phase14-autonomous-learning | Autonomous learning surface map | phase14-autonomous-learning-surface-map.md | P2 | WP-5003 |
| phase15-enterprise-lifecycle | Enterprise lifecycle and compliance surface map | phase15-enterprise-lifecycle-surface-map.md | P2 | — |
| phase15-enterprise-compliance | Enterprise compliance test matrix (EC-001–EC-006) | phase15-enterprise-compliance-test-matrix.md | P2 | phase15-enterprise-lifecycle |
| gov-wp-3003-enhance | Emit governance.override.expired (optional) | GOVERNANCE_WP_GAPS.md | P3 | — |
| gov-wp-3008-dlq | EscalationQueue + DLQ integration (deferred) | GOVERNANCE_WP_GAPS.md | P2 | — |
| cost-wp-y4 | Per-run cost aggregation (orchestration/cost.py) | COST_ROUTING_DEFERRED.md | P2 | — |
| cost-budget-alerts | Budget alerts and cost-overage gates | COST_ROUTING_DEFERRED.md | P2 | cost-wp-y4 |
| cost-wp-5003 | Cost-quality optimization (RouteLLM-style) | COST_ROUTING_DEFERRED.md | P2 | cost-wp-y4 |
| WP-28003 | Poison Pill Detection in Swarm Memory | 02-UNIFIED-WBS.md | P2 | WP-24003 |
| WP-29002 | Societal Impact Simulation | 02-UNIFIED-WBS.md | P2 | WP-14001 |
| WP-32001 | Sensory Context Bridge (Audio/Video) | 02-UNIFIED-WBS.md | P2 |  |
| WP-32002 | Bio-Digital Confidence Calibration | 02-UNIFIED-WBS.md | P3 | WP-4008 |
| WP-34003 | Light-Speed Compensation Planning | 02-UNIFIED-WBS.md | P3 | WP-14001 |
| WP-35002 | Cross-Region Latency-Aware Scheduling | 02-UNIFIED-WBS.md | P2 | WP-31001 |
| WP-36002 | Biological Feedback Confidence Injection | 02-UNIFIED-WBS.md | P3 | WP-32002 |
| WP-36003 | Molecular Computing Simulation sandbox | 02-UNIFIED-WBS.md | P3 | WP-31002 |
| WP-38003 | Parallel Timeline State Merging | 02-UNIFIED-WBS.md | P2 | WP-38001 |
| WP-39003 | Recursive Reward Modeling Optimization | 02-UNIFIED-WBS.md | P2 | WP-16003 |
| WP-40002 | Distributed Sensor Mesh Orchestration | 02-UNIFIED-WBS.md | P2 | WP-26001 |
| WP-41001 | Neural-Link Cognitive Offloading (Sim) | 02-UNIFIED-WBS.md | P3 | WP-36002 |
| WP-41002 | Human-Agent Co-Consciousness Interface | 02-UNIFIED-WBS.md | P3 |  |
| WP-42001 | Stellar Energy Harvesting Bridge (Sim) | 02-UNIFIED-WBS.md | P3 | WP-31001 |
| WP-42002 | Matrioshka Brain Resource Allocation | 02-UNIFIED-WBS.md | P3 | WP-35001 |
| WP-42003 | Cold-Storage Data Archiving (Planet-Scale) | 02-UNIFIED-WBS.md | P3 | WP-36001 |
| WP-43002 | Gravity-Aware Task Scheduling | 02-UNIFIED-WBS.md | P3 | WP-14001 |
| WP-44002 | Cross-Substrate Migration Logic | 02-UNIFIED-WBS.md | P2 | WP-23002 |
| WP-44003 | Virtualized Consciousness Bridge | 02-UNIFIED-WBS.md | P3 | WP-41002 |
| WP-45003 | Final State Consensus Protocol | 02-UNIFIED-WBS.md | P1 | WP-24001 |
| vitepress-playwright-setup | Set up Playwright for browser recordings | VITEPRESS_RICH_DOCUMENTATION_IMPLEMENTATION_PLAN.md | P1 | - |
| vitepress-api-docs-generator | Auto-generate API docs from docstrings | VITEPRESS_RICH_DOCUMENTATION_IMPLEMENTATION_PLAN.md | P1 | vitepress-mermaid-setup |
| vitepress-architecture-generator | Auto-generate architecture diagrams from code | VITEPRESS_RICH_DOCUMENTATION_IMPLEMENTATION_PLAN.md | P1 | vitepress-mermaid-setup |
| vitepress-cli-examples-generator | Auto-generate CLI examples | VITEPRESS_RICH_DOCUMENTATION_IMPLEMENTATION_PLAN.md | P1 | vitepress-code-playground |
| vitepress-demo-gif-generator | Auto-generate demo GIFs from scripts | VITEPRESS_RICH_DOCUMENTATION_IMPLEMENTATION_PLAN.md | P1 | vitepress-vhs-setup |
| vitepress-auto-sidebar | Auto-generate sidebar from directory structure | VITEPRESS_RICH_DOCUMENTATION_IMPLEMENTATION_PLAN.md | P2 | - |
| vitepress-llm-output | Generate LLM-friendly documentation (.llms.txt) | VITEPRESS_RICH_DOCUMENTATION_IMPLEMENTATION_PLAN.md | P2 | - |
| vitepress-agent-workflow | Create agent workflow for auto-population | VITEPRESS_RICH_DOCUMENTATION_IMPLEMENTATION_PLAN.md | P1 | vitepress-mermaid-setup, vitepress-code-playground, vitepress-vhs-setup |
| docgen-sticky-nav | Implement sticky sidebar and header | DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md | P1 | - |
| docgen-algolia-search | Integrate Algolia search with suggestions | DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md | P1 | - |
| docgen-content-tabs | Create content tabs component | DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md | P1 | - |
| docgen-api-python-enhanced | Enhance Python API generator (mkdocstrings-like) | DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md | P1 | vitepress-api-docs-generator |
| docgen-api-typescript | Create TypeScript/JavaScript API generator | DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md | P1 | - |
| docgen-performance-code-split | Optimize code splitting for faster loads | DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md | P1 | - |
| docgen-performance-images | Image optimization (WebP/AVIF, lazy loading) | DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md | P1 | - |
| docgen-edit-links | Add edit-on-GitHub links | DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md | P1 | - |
| docgen-math-support | Add KaTeX math support | DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md | P2 | - |
| docgen-code-annotation | Implement code annotation component | DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md | P2 | - |
| docgen-openapi | Add OpenAPI/Swagger integration | DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md | P2 | - |
| docgen-versioning | Implement version switcher | DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md | P2 | - |
| docgen-analytics | Add Google Analytics / Plausible integration | DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md | P2 | - |
| docgen-watch-mode | Implement watch mode for auto-regeneration | DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md | P2 | - |
| docgen-link-checker | Automated link checking | DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md | P1 | - |
| docgen-code-validator | Code example validation | DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md | P2 | - |
| docgen-parallel-generation | Parallel documentation generation | DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md | P1 | vitepress-agent-workflow |
| docgen-incremental-generation | Incremental generation (only changed files) | DOCGEN_DOCSITE_IMPROVEMENT_PLAN.md | P1 | vitepress-agent-workflow |
| sync-unified-command | Unified sync/update command implementation | SYNC_UPDATE_COMMAND_AND_SYSTEM_AUDIT_PLAN.md | P1 | — |
| sync-work-stream-integration | Work stream auto-incorporation | SYNC_UPDATE_COMMAND_AND_SYSTEM_AUDIT_PLAN.md | P1 | sync-unified-command |
| sync-audit-framework | System audit framework | SYNC_UPDATE_COMMAND_AND_SYSTEM_AUDIT_PLAN.md | P1 | sync-unified-command |
| sync-research-integration | Research sprawl integration | SYNC_UPDATE_COMMAND_AND_SYSTEM_AUDIT_PLAN.md | P1 | sync-work-stream-integration |
| sync-plan-consolidation | Plan consolidation automation | SYNC_UPDATE_COMMAND_AND_SYSTEM_AUDIT_PLAN.md | P1 | sync-work-stream-integration |
| dx-improve-verbosity-batch-files | Batch file operations to reduce tool calls | FRICTION_LOG.md | P1 | - |
| dx-improve-path-handling | Normalize path handling across all operations | FRICTION_LOG.md | P1 | - |
| dx-improve-file-reading-efficiency | Use offset/limit for targeted file reading | FRICTION_LOG.md | P2 | - |
| ax-improve-reusable-helpers | Create reusable helper library for common patterns | FRICTION_LOG.md | P1 | - |
| ax-improve-workstream-operations | Automate work stream operations (read, parse, update) | FRICTION_LOG.md | P1 | - |
| ux-improve-error-messages | Make error messages actionable with suggested fixes | FRICTION_LOG.md | P2 | - |
| research-agent-hierarchy-mvp | Agent Hierarchy & Maximal MVP (SmolGents + codex/cc/droid harness) | SMOLGENTS_MVP_AND_LANGGRAPH_CC_VISION.md | P1 | - |
| research-agent-hierarchy-implementation | Implement AgentHierarchyManager (Phase 1) | AGENT_HIERARCHY_AND_TEAM_STRUCTURE.md | P2 | research-agent-hierarchy-mvp |
| impl-agent-crew-maximal-mvp | Implement Agent Crew stack (Crew, CrewExecutor, WorkflowEngine, RouterManager, MonitoringEngine) | SMOLGENTS_MVP_AND_LANGGRAPH_CC_VISION.md | P1 | research-agent-hierarchy-mvp |
| impl-agent-crew-codex-harness | Wire codex/cc/droid harness as agent_executor for Crew | SMOLGENTS_MVP_AND_LANGGRAPH_CC_VISION.md | P1 | impl-agent-crew-maximal-mvp |

*Run `thegent plan incorporate` to refresh from plans, research, specs.*

---

## CLAIMED (in progress — do not pick)

| ID | Agent | Started |
|----|-------|---------|
| WP-32002 | claude-code-session-20260219T015615 | 2026-02-19T01:56:15.705702Z |
| WP-41002 | claude-code-session-20260219T015615 | 2026-02-19T01:56:15.705704Z |
| research-library-env-settings | composer | 2026-02-19T06:05:35Z |
| research-hook-rust-phase2 | thegent-main-session | 2026-02-19T12:30:00Z |
| research-phase13-policy-federation | composer | 2026-02-18 |
| impl-agent-crew-maximal-mvp | 20260219T060501Z-copilot-p55181-14d16d33 | 2026-02-19T06:05:01Z |
| research-hook-rust-gix | 20260219T060639Z-copilot-p10063-98a11994 | 2026-02-19T06:06:39Z |

---

## COMPLETED (this session / recent)
| ID | Agent | Completed | Notes |
|----|-------|-----------|-------|
| research-cross-platform-shell | thegent-main-session | 2026-02-19 | Implemented POSIX + PowerShell strategy |
| research-cross-platform-desktop | thegent-main-session | 2026-02-19 | Implemented desktop automation stubs |
| research-cross-platform-security | thegent-main-session | 2026-02-19 | Implemented security hardening features |
| research-cross-platform-performance | thegent-main-session | 2026-02-19 | Implemented performance benchmarking |
| research-cross-platform-coordination | thegent-main-session | 2026-02-19 | Implemented multi-tenant coordination stubs |
| impl-hook-rust-breaker | thegent-main-session | 2026-02-19 | Implement breaker-check/record/reset in Rust |
| impl-hook-rust-debounce | thegent-main-session | 2026-02-19 | Implement debounce in Rust |
| impl-hook-rust-incremental | thegent-main-session | 2026-02-19 | Implement incremental-check/record in Rust |
| impl-hook-rust-learning | thegent-main-session | 2026-02-19 | Implement learning subcommands in Rust |
| impl-hook-rust-fr-index | thegent-main-session | 2026-02-19 | Implement fr-ids/fr-index in Rust |
| impl-hook-rust-affected-tests | thegent-main-session | 2026-02-19 | Implement affected-tests in Rust |
| impl-hook-rust-prewarm-report | thegent-main-session | 2026-02-19 | Implement prewarm/report in Rust |
| research-tui-compositor | thegent-main-session | 2026-02-19 | Research complete, report created |
| research-compute-offload | thegent-main-session | 2026-02-19 | Research complete, report created |
| research-idea-seed-system | thegent-main-session | 2026-02-19 | Research complete, report created |
| research-remote-compute-impl | thegent-main-session | 2026-02-19 | Research complete, report created |
| research-cross-platform-isolation | thegent-main-session | 2026-02-19 | Research complete, report created |
| research-supermemory-integration | thegent-main-session | 2026-02-19 | Research complete, report created |
| research-pareto-routing | thegent-main-session | 2026-02-19 | Research complete, report created |
| research-economic-governance | thegent-main-session | 2026-02-19 | Research complete, report created |
| research-maif-artifacts | thegent-main-session | 2026-02-19 | Research complete, report created |
| research-simulation-replay | thegent-main-session | 2026-02-19 | Research complete, report created |
| WP-16003 | claude-code | 2026-02-18 | ShareCLI Coordination Bridge - implementation complete in sharecli_bridge.py |
| WP-16004 | claude-code | 2026-02-18 | AST-aware Conflict Resolution (SmartMerge) - implementation complete |
| WP-39003 | claude-code | 2026-02-18 | Recursive Reward Modeling Optimization - implementation complete in reward_model.py |
| scratch-doctor-shim-check | composer | 2026-02-18 | Enhanced doctor.py to check shim versions, binary availability, and executable permissions |
| scratch-doctor-fix | composer | 2026-02-18 | Implemented proactive doctor --fix functionality in doctor.py |
| research-agent-hierarchy-mvp | manual | 2026-02-18 | SMOLGENTS_MVP_AND_LANGGRAPH_CC_VISION.md |
| research-library-cache | kooshapari-minimax | 2026-02-18T12:15:00Z |
| research-library-retry | worker-droid | 2026-02-18 |
| research-library-watchdog | subagent | 2026-02-18T10:35:00Z |
| research-library-http | worker-droid | 2026-02-18 |
| docgen-link-checker | worker-droid | 2026-02-18T00:58:00 |
| docgen-sticky-nav | worker-droid | 2026-02-18 |
| docgen-content-tabs | worker-droid | 2026-02-18 |
| docgen-nav-tabs | subagent | 2026-02-18T00:00:00 |
| vitepress-api-docs-generator | subagent | 2026-02-18T00:00:00 |
| vitepress-mermaid-setup | subagent | 2026-02-18T00:38:00 |
| vitepress-code-playground | subagent | 2026-02-18T00:00:00 |
| docgen-edit-links | subagent | 2026-02-18T00:00:00 |
| docgen-math-support | dx-improver | 2026-02-18T12:00:00 |
| dx-improve-verbosity-batch-files | dx-improver | 2026-02-18T12:00:00 |
| dx-improve-path-handling | dx-improver | 2026-02-18T12:00:00 |
| ax-improve-reusable-helpers | ax-improver | 2026-02-18T12:00:00 |
| ax-improve-workstream-operations | ax-improver | 2026-02-18T12:00:00 |
| research-llm-proxy-depth | agent-kooshapari | 2026-02-19 | LLM_PROXY_RESEARCH_AUDIT_PLAN.md |
| impl-shell-install-target | agent-kooshapari | 2026-02-19 | Added shell target to thegent install |
| impl-system-shims-expansion | agent-kooshapari | 2026-02-19 | Expanded install-shims --system to include grep, find, jq, thegent-shim |
| impl-git-lock-cleanup-target | agent-kooshapari | 2026-02-19 | Added git-lock-cleanup as target to thegent install |
| dx-improve-file-reading-efficiency | agent-kooshapari | 2026-02-19 | Implemented read_file_optimized and efficient read_file_lines; migrated CLI continuation and session watcher |
| ux-improve-error-messages | agent-kooshapari | 2026-02-19 | Introduced print_error with remediation hints and updated high-visibility error spots |
| item-xp-1 | auto-launch | 2026-02-19T11:34:51.516631+00:00 |
