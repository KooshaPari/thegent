# Documentation Consolidation & Implementation WBS

**Purpose**: Complete end-to-end work breakdown structure for:
1. Consolidate guides/reference/checklists (~295 MD files)
2. Create unified work stream entries for implementation tasks
3. Begin implementation of prioritized research findings

**Date**: 2026-02-17
**Status**: Plan Complete | Execution Ready

---

## Executive Summary

| Phase | Description | Duration | Effort | Priority |
|-------|-------------|----------|--------|----------|
| **Phase A** | Documentation Audit & Categorization | 2 hrs | 4 agent-hrs | P1 |
| **Phase B** | Guides Consolidation (42 files) | 4 hrs | 8 agent-hrs | P1 |
| **Phase C** | Reference Consolidation (84 files) | 6 hrs | 12 agent-hrs | P1 |
| **Phase D** | Checklists Consolidation (1 file) | 1 hr | 2 agent-hrs | P2 |
| **Phase E** | Work Stream Entry Creation | 3 hrs | 6 agent-hrs | P1 |
| **Phase F** | Implementation Sprint 1 (P1 items) | 8 hrs | 16 agent-hrs | P1 |
| **Phase G** | Implementation Sprint 2 (P2 items) | 12 hrs | 24 agent-hrs | P2 |

**Total Effort**: ~72 agent-hours
**Estimated Duration**: 2-3 days (parallel execution)

---

## Phase A: Documentation Audit & Categorization

### A.1 Current State Analysis

| Task | ID | Description | Depends | Output |
|------|-----|-------------|---------|--------|
| A.1.1 | DOC-AUDIT-001 | Count and categorize docs/guides/*.md | — | Inventory list |
| A.1.2 | DOC-AUDIT-002 | Count and categorize docs/reference/*.md | — | Inventory list |
| A.1.3 | DOC-AUDIT-003 | Count and categorize docs/checklists/*.md | — | Inventory list |
| A.1.4 | DOC-AUDIT-004 | Identify orphaned/duplicate docs | A.1.1, A.1.2, A.1.3 | Duplicates report |
| A.1.5 | DOC-AUDIT-005 | Assess docs needing EXTENSION_SUMMARY | A.1.4 | Gap analysis |

### A.2 Documentation Classification Matrix

| Category | Guides | Reference | Checklists | Total |
|----------|--------|----------|------------|-------|
| Architecture | 5 | 12 | 0 | 17 |
| CLI/Tools | 8 | 15 | 0 | 23 |
| Configuration | 4 | 8 | 0 | 12 |
| Development | 6 | 10 | 0 | 16 |
| Governance | 3 | 8 | 1 | 12 |
| Integration | 5 | 12 | 0 | 17 |
| Operations | 4 | 6 | 0 | 10 |
| Security | 2 | 5 | 0 | 7 |
| Troubleshooting | 5 | 8 | 0 | 13 |
| **Total** | **42** | **84** | **1** | **127** |

### A.3 Naming Convention Standards

| Pattern | Description | Action |
|---------|-------------|--------|
| `*.md` | Canonical docs | Keep as-is |
| `*_COMPLETE.md` | Completion reports | Consolidate to single file |
| `*_SUMMARY.md` | Summary docs | Merge to parent |
| `*_EXPANDED.md` | Extended versions | Merge to base |
| `*_GUIDE.md` | How-to guides | Keep, standardize format |
| `*_REFERENCE.md` | Reference docs | Keep, add to index |
| `*_PLAN.md` | Planning docs | Archive to docs/plans/ |

---

## Phase B: Guides Consolidation (42 files)

### B.1 Core Architecture Guides

| Task | ID | File | Action | Ext. Summary |
|------|-----|------|--------|--------------|
| B.1.1 | GUIDE-ARCH-001 | AGENT_DEBUGGING_AND_REMEDIATION_GUIDE.md | Extend | ✅ |
| B.1.2 | GUIDE-ARCH-002 | AGENT_INSTRUCTIONS_THEGENT.md | Extend | ✅ |
| B.1.3 | GUIDE-ARCH-003 | architecture-enforcement.md | Extend | ✅ |
| B.1.4 | GUIDE-ARCH-004 | BKM_IMPLEMENTATION_GUIDES.md | Extend | ✅ |
| B.1.5 | GUIDE-ARCH-005 | AUTOMATED_DEMOS.md | Create EXT | ✅ |

### B.2 Cross-Platform Guides

| Task | ID | File | Action | Ext. Summary |
|------|-----|------|--------|--------------|
| B.2.1 | GUIDE-XP-001 | CROSS_PLATFORM_COMPLETE.md | Merge | — |
| B.2.2 | GUIDE-XP-002 | CROSS_PLATFORM_DEVELOPER_COOKBOOK.md | Extend | ✅ |
| B.2.3 | GUIDE-XP-003 | CROSS_PLATFORM_IMPLEMENTATION_TEMPLATES.md | Extend | ✅ |
| B.2.4 | GUIDE-XP-004 | CROSS_PLATFORM_MIGRATION_GUIDE.md | Extend | ✅ |
| B.2.5 | GUIDE-XP-005 | CROSS_PLATFORM_QUICK_START.md | Extend | ✅ |
| B.2.6 | GUIDE-XP-006 | CROSS_PLATFORM_ROADMAP.md | Merge | — |
| B.2.7 | GUIDE-XP-007 | HYBRID_ENV_QUICK_START.md | Extend | ✅ |

### B.3 Shell & Environment Guides

| Task | ID | File | Action | Ext. Summary |
|------|-----|------|--------|--------------|
| B.3.1 | GUIDE-SH-001 | SHELL_ADVANCED_FEATURES.md | Extend | ✅ |
| B.3.2 | GUIDE-SH-002 | FIX_SHELL_CORRUPTION.md | Extend | ✅ |
| B.3.3 | GUIDE-SH-003 | FIX_SHELL_FORK_ERRORS.md | Extend | ✅ |
| B.3.4 | GUIDE-SH-004 | QUICK_FIX_SHELL_SETUP.md | Extend | ✅ |
| B.3.5 | GUIDE-SH-005 | RUNTIME_OPTIMIZATION.md | Extend | ✅ |
| B.3.6 | GUIDE-SH-006 | DOCTOR_FIXES.md | Extend | ✅ |

### B.4 Integration Guides

| Task | ID | File | Action | Ext. Summary |
|------|-----|------|--------|--------------|
| B.4.1 | GUIDE-INT-001 | PROVIDER_SETUP_GUIDE.md | Extend | ✅ |
| B.4.2 | GUIDE-INT-002 | OXLINT_INTEGRATION_GUIDE.md | Extend | ✅ |
| B.4.3 | GUIDE-INT-003 | PROMPTS_TOOLING.md | Extend | ✅ |
| B.4.4 | GUIDE-INT-004 | JOB_POOL_USAGE.md | Extend | ✅ |
| B.4.5 | GUIDE-INT-005 | OAUTH_ONLY_AUTHENTICATION.md | Extend | ✅ |
| B.4.6 | GUIDE-INT-006 | OPERATIONAL_LEARNING.md | Extend | ✅ |

### B.5 Phase Guides

| Task | ID | File | Action | Ext. Summary |
|------|-----|------|--------|--------------|
| B.5.1 | GUIDE-PH-001 | PHASE_4_QUICK_START.md | Extend | ✅ |
| B.5.2 | GUIDE-PH-002 | PHASE_7_9_GUIDE.md | Extend | ✅ |
| B.5.3 | GUIDE-PH-003 | PHASE_10_GUIDE.md | Extend | ✅ |
| B.5.4 | GUIDE-PH-004 | PHASE_11_GUIDE.md | Extend | ✅ |

### B.6 Anti-Patterns & Standards

| Task | ID | File | Action | Ext. Summary |
|------|-----|------|--------|--------------|
| B.6.1 | GUIDE-AP-001 | anti-patterns.md | Extend | ✅ |
| B.6.2 | GUIDE-AP-002 | index.md | Update | — |

---

## Phase C: Reference Consolidation (84 files)

### C.1 Agent & Runtime References

| Task | ID | File | Action | Status |
|------|-----|------|--------|--------|
| C.1.1 | REF-AGT-001 | AGENT_IDENTITY_SOVEREIGNTY_DEPTH.md | Extend | ✅ |
| C.1.2 | REF-AGT-002 | AGENT_NEGOTIATION_ACL_DEPTH.md | Extend | ✅ |
| C.1.3 | REF-AGT-003 | AGENT_OS_PRINCIPALS_DEPTH.md | Extend | ✅ |
| C.1.4 | REF-AGT-004 | HAC_AND_HITL_PATTERNS.md | Extend | ✅ |
| C.1.5 | REF-AGT-005 | SWARM_MEMORY_COORDINATION_DEPTH.md | Extend | ✅ |

### C.2 Architecture References

| Task | ID | File | Action | Status |
|------|-----|------|--------|--------|
| C.2.1 | REF-ARC-001 | ARCHITECTURE_LAYERS.md | Extend | ✅ |
| C.2.2 | REF-ARC-002 | DOMINANCE_PROOF_REFERENCE.md | Extend | ✅ |
| C.2.3 | REF-ARC-003 | ECONOMIC_GOVERNANCE_DEPTH.md | Extend | ✅ |
| C.2.4 | REF-ARC-004 | GARDENER_ARCHITECTURE.md | Extend | ✅ |
| C.2.5 | REF-ARC-005 | HOOK_OPTIMIZATION_STRATEGY.md | Extend | ✅ |
| C.2.6 | REF-ARC-006 | INTEGRATION_ARCHITECTURE.md | Extend | ✅ |
| C.2.7 | REF-ARC-007 | MULTI_SWARM_HIERARCHY_DEPTH.md | Extend | ✅ |
| C.2.8 | REF-ARC-008 | OTEL_GENAI_AND_HYSTERESIS_DEPTH.md | Extend | ✅ |
| C.2.9 | REF-ARC-009 | ROBUSTNESS_AND_FUTURE_DEPTH.md | Extend | ✅ |
| C.2.10 | REF-ARC-010 | SIMULATION_AND_SANDBOX_DEPTH.md | Extend | ✅ |
| C.2.11 | REF-ARC-011 | SWARM_PROCESS_OPTIMIZATIONS.md | Extend | ✅ |
| C.2.12 | REF-ARC-012 | TASK_ROUTING_DESIGN.md | Extend | ✅ |

### C.3 Model Routing References

| Task | ID | File | Action | Status |
|------|-----|------|--------|--------|
| C.3.1 | REF-MOD-001 | COMPLETE_PROVIDER_ROUTING_MAP.md | Extend | ✅ |
| C.3.2 | REF-MOD-002 | MODEL_RANKING_CORRECTED.md | Extend | ✅ |
| C.3.3 | REF-MOD-003 | MODEL_ROUTING_DECISION_TREE.md | Extend | ✅ |
| C.3.4 | REF-MOD-004 | MODEL_ROUTING_INDEX.md | Extend | ✅ |
| C.3.5 | REF-MOD-005 | MODEL_ROUTING_SUMMARY.md | Extend | ✅ |
| C.3.6 | REF-MOD-006 | MODEL_SELECTION_INDEX.md | Extend | ✅ |
| C.3.7 | REF-MOD-007 | PARETO_INDEX.md | Extend | ✅ |
| C.3.8 | REF-MOD-008 | PARETO_ROUTING_DESIGN.md | Extend | ✅ |
| C.3.9 | REF-MOD-009 | ROUTING_DECISION_MATRIX.md | Extend | ✅ |
| C.3.10 | REF-MOD-010 | ROUTING_FINAL_RECOMMENDATION.md | Extend | ✅ |
| C.3.11 | REF-MOD-011 | ROUTING_IMPLEMENTATION_ARCHITECTURE.md | Extend | ✅ |
| C.3.12 | REF-MOD-012 | ROUTING_QUICK_CARD.md | Extend | ✅ |
| C.3.13 | REF-MOD-013 | ROUTING_SYSTEM_MASTER_SUMMARY.md | Extend | ✅ |
| C.3.14 | REF-MOD-014 | TASK_ROUTING_QUICK_REF.md | Extend | ✅ |

### C.4 Pareto References

| Task | ID | File | Action | Status |
|------|-----|------|--------|--------|
| C.4.1 | REF-PAR-001 | PARETO_ALGORITHM_PSEUDOCODE.md | Extend | ✅ |
| C.4.2 | REF-PAR-002 | PARETO_EXECUTIVE_SUMMARY.md | Extend | ✅ |
| C.4.3 | REF-PAR-003 | PARETO_FRONTIER_ANALYSIS.md | Extend | ✅ |
| C.4.4 | REF-PAR-004 | PARETO_FRONTIER_COMPLETE_ANALYSIS.md | Extend | ✅ |
| C.4.5 | REF-PAR-005 | PARETO_FRONTIER_MATRIX.md | Extend | ✅ |
| C.4.6 | REF-PAR-006 | PARETO_FRONTIER_QUICK_REFERENCE.md | Extend | ✅ |
| C.4.7 | REF-PAR-007 | PARETO_FRONTIER_TABLE.md | Extend | ✅ |
| C.4.8 | REF-PAR-008 | PARETO_FRONTIER_TERMINAL_BENCH_2_0.md | Extend | ✅ |
| C.4.9 | REF-PAR-009 | PARETO_VISUALIZATION.md | Extend | ✅ |

### C.5 Cross-Platform References

| Task | ID | File | Action | Status |
|------|-----|------|--------|--------|
| C.5.1 | REF-XP-001 | CROSS_PLATFORM_API_REFERENCE.md | Extend | ✅ |
| C.5.2 | REF-XP-002 | CROSS_PLATFORM_MULTI_TENANT_QUICK_REFERENCE.md | Extend | ✅ |
| C.5.3 | REF-XP-003 | INDEXING_AND_OPTIMIZATION_SYSTEMS.md | Extend | ✅ |
| C.5.4 | REF-XP-004 | PHASE_3_5_QUICK_REFERENCE.md | Extend | ✅ |
| C.5.5 | REF-XP-005 | PHASE_4_COCKPIT_UX_DEPTH.md | Extend | ✅ |
| C.5.6 | REF-XP-006 | PHASE_5_SCALE_ROBUSTNESS_DEPTH.md | Extend | ✅ |
| C.5.7 | REF-XP-007 | POSIX_PWSH_SHELL_STRATEGY.md | Extend | ✅ |
| C.5.8 | REF-XP-008 | PROVIDER_LIMITS_AND_FALLBACK.md | Extend | ✅ |
| C.5.9 | REF-XP-009 | PROVIDER_MODEL_BEHAVIOR.md | Extend | ✅ |
| C.5.10 | REF-XP-010 | PROVIDER_MODEL_REFERENCE.md | Extend | ✅ |
| C.5.11 | REF-XP-011 | RUST_TOOLING.md | Extend | ✅ |
| C.5.12 | REF-XP-012 | SLO_TARGETS.md | Extend | ✅ |
| C.5.13 | REF-XP-013 | STARSHIP_SETUP.md | Extend | ✅ |
| C.5.14 | REF-XP-014 | TERMINAL_BENCH_2_0_CORRECTED_FRONTIER.md | Extend | ✅ |
| C.5.15 | REF-XP-015 | TOOLING_AND_GLOBAL_OPTIMIZATIONS_AUDIT.md | Extend | ✅ |
| C.5.16 | REF-XP-016 | TOUCHPOINT_INTEGRATION_DEEP_DIVE.md | Extend | ✅ |
| C.5.17 | REF-XP-017 | TOUCHPOINT_INTEGRATION_EVALUATION.md | Extend | ✅ |
| C.5.18 | REF-XP-018 | ZEN_INTEGRATION.md | Extend | ✅ |

### C.6 Monitoring References

| Task | ID | File | Action | Status |
|------|-----|------|--------|--------|
| C.6.1 | REF-MON-001 | MONITORING_ALERT_RULES.md | Extend | ✅ |
| C.6.2 | REF-MON-002 | MONITORING_DASHBOARD_SPEC.md | Extend | ✅ |
| C.6.3 | REF-MON-003 | MONITORING_METRICS_REFERENCE.md | Extend | ✅ |
| C.6.4 | REF-MON-004 | MONITORING_README.md | Extend | ✅ |
| C.6.5 | REF-MON-005 | MONITORING_SETUP_GUIDE.md | Extend | ✅ |

### C.7 Integration References

| Task | ID | File | Action | Status |
|------|-----|------|--------|--------|
| C.7.1 | REF-INT-001 | FR_TRACKER.md | Update | — |
| C.7.2 | REF-INT-002 | FRONTMATTER_BACKMATTER_INTEGRATION_POINTS.md | Extend | ✅ |
| C.7.3 | REF-INT-003 | GARDENER_ARCHITECTURE.md | Extend | ✅ |
| C.7.4 | REF-INT-004 | HYBRID_ENV_SUMMARY.md | Extend | ✅ |
| C.7.5 | REF-INT-005 | INTEGRATION_INDEX.md | Update | — |
| C.7.6 | REF-INT-006 | INTEGRATION_QUICK_START.md | Extend | ✅ |
| C.7.7 | REF-INT-007 | INTEGRATION_SUMMARY.txt | Update | — |
| C.7.8 | REF-INT-008 | MAIF_ARTIFACT_SPEC_DEPTH.md | Extend | ✅ |
| C.7.9 | REF-INT-009 | MODEL_ROUTING_TERMINAL_BENCH_2_0_QUICK_REF.md | Extend | ✅ |

### C.8 Other References

| Task | ID | File | Action | Status |
|------|-----|------|--------|--------|
| C.8.1 | REF-OTH-001 | CLAUDE_CORE_GUIDELINES.md | Extend | ✅ |
| C.8.2 | REF-OTH-002 | CLAUDE_THEGENT_RUNTIME_APPENDIX.md | Extend | ✅ |
| C.8.3 | REF-OTH-003 | CONTEXT_MANAGEMENT_DEPTH.md | Extend | ✅ |
| C.8.4 | REF-OTH-004 | COST_ENFORCEMENT_POLICY.md | Extend | ✅ |
| C.8.5 | REF-OTH-005 | CONSTITUTIONAL_ENFORCEMENT_DEPTH.md | Extend | ✅ |
| C.8.6 | REF-OTH-006 | SELF_HEALING_AGENTIC_CICD_DEPTH.md | Extend | ✅ |
| C.8.7 | REF-OTH-007 | SITBACK_PLUGINS.md | Extend | ✅ |
| C.8.8 | REF-OTH-008 | START_HERE.md | Update | — |
| C.8.9 | REF-OTH-009 | TESTING.md | Extend | ✅ |
| C.8.10 | REF-OTH-010 | TROUBLESHOOTING.md | Extend | ✅ |

---

## Phase D: Checklists Consolidation (1 file)

| Task | ID | File | Action | Status |
|------|-----|------|--------|--------|
| D.1.1 | CHK-001 | index.md | Update | — |

---

## Phase E: Work Stream Entry Creation

### E.1 Implementation Tasks from Research

| Task | ID | Description | Research Source | Priority |
|------|-----|-------------|-----------------|----------|
| E.1.1 | WS-IMPL-001 | Implement Supermemory integration | SESSION_RESEARCH_FRAGMENTS | P1 |
| E.1.2 | WS-IMPL-002 | Implement Pareto routing | PARETO_FRONTIER_* | P1 |
| E.1.3 | WS-IMPL-003 | Implement cost governance | COST_ROUTING_DEFERRED | P1 |
| E.1.4 | WS-IMPL-004 | Build thegent-hooks binary | HOOK_RUST_MIGRATION_* | P1 |
| E.1.5 | WS-IMPL-005 | Replace urllib with httpx | LIBRARY_REPLACEMENT_* | P1 |
| E.1.6 | WS-IMPL-006 | Migrate retry to tenacity | TENACITY_RETRY_* | P1 |
| E.1.7 | WS-IMPL-007 | Replace polling with watchdog | WATCHDOG_TRIGGER | P1 |
| E.1.8 | WS-IMPL-008 | Implement TUI compositor | TUI_COMPOSITOR_* | P1 |
| E.1.9 | WS-IMPL-009 | Implement compute offloading | HYBRID_ENV_* | P2 |
| E.1.10 | WS-IMPL-010 | Implement idea seed system | IDEA_SEEDS_* | P1 |

### E.2 Documentation Tasks

| Task | ID | Description | Target | Priority |
|------|-----|-------------|--------|----------|
| E.2.1 | WS-DOC-001 | Add EXTENSION_SUMMARY to all guides | guides/*.md | P1 |
| E.2.2 | WS-DOC-002 | Add EXTENSION_SUMMARY to all reference | reference/*.md | P1 |
| E.2.3 | WS-DOC-003 | Standardize guide formatting | guides/*.md | P2 |
| E.2.4 | WS-DOC-004 | Update reference index | reference/index.md | P1 |
| E.2.5 | WS-DOC-005 | Create doc cross-reference index | reference/XREF_INDEX.md | P2 |

### E.3 Work Stream Entry Template

```markdown
| ID | Title | Source Doc | Priority | Depends | Effort |
|----|-------|------------|----------|---------|--------|
| WS-XXX-000 | Description | DOC_NAME.md | P1/P2/P3 | ID1, ID2 | N hrs |
```

---

## Phase F: Implementation Sprint 1 (P1 Items)

### F.1 Critical Path - Library Replacements

```
F.1.1 (urllib→httpx) ─┬─→ F.1.2 (retry→tenacity) ─┬─→ F.1.3 (watchdog)
                        │                           │
                        └───────────────────────────┘
```

| Task | ID | Description | Input | Output |
|------|-----|-------------|-------|--------|
| F.1.1 | IMPL-LIB-001 | Replace urllib with httpx (7 files) | LIBRARY_REPLACEMENT_AUDIT | Updated files |
| F.1.2 | IMPL-LIB-002 | Migrate retry to tenacity (4 files) | TENACITY_RETRY_AUDIT | Updated files |
| F.1.3 | IMPL-LIB-003 | Replace polling with watchdog (1 file) | File watching audit | Updated file |

### F.2 Critical Path - Hook Rust Migration

```
F.2.1 ──→ F.2.2 ──→ F.2.3 ──→ F.2.4
```

| Task | ID | Description | Input | Output |
|------|-----|-------------|-------|--------|
| F.2.1 | IMPL-HOOK-001 | Build thegent-hooks binary | HOOK_RUST_MIGRATION_* | Binary |
| F.2.2 | IMPL-HOOK-002 | Migrate hooks to use thegent-hooks (opt-in) | F.2.1 | Updated hooks |
| F.2.3 | IMPL-HOOK-003 | Make thegent-hooks default | F.2.2 | Updated hooks |
| F.2.4 | IMPL-HOOK-004 | Add performance benchmarks | F.2.1 | Benchmark report |

### F.3 Critical Path - TUI Compositor

| Task | ID | Description | Input | Output |
|------|-----|-------------|-------|--------|
| F.3.1 | IMPL-TUI-001 | Select TUI framework | TUI_COMPOSITOR_COMPARISON.md | Selection |
| F.3.2 | IMPL-TUI-002 | Implement core compositor | F.3.1 | Core module |
| F.3.3 | IMPL-TUI-003 | Integrate with thegent | F.3.2 | Integration |

---

## Phase G: Implementation Sprint 2 (P2 Items)

### G.1 Library Replacements (P2)

| Task | ID | Description | Effort |
|------|-----|-------------|--------|
| G.1.1 | IMPL-LIB-101 | Replace custom caching with cachetools (5 files) | 4 hrs |
| G.1.2 | IMPL-LIB-102 | Replace circuit breaker with pybreaker (1 file) | 2 hrs |
| G.1.3 | IMPL-LIB-103 | Replace PyYAML with ruamel.yaml (15 files) | 6 hrs |
| G.1.4 | IMPL-LIB-104 | Replace ANSI stripping with rich (5 files) | 2 hrs |

### G.2 Advanced Features

| Task | ID | Description | Depends | Effort |
|------|-----|-------------|---------|--------|
| G.2.1 | IMPL-ADV-001 | Implement compute offloading | HYBRID_ENV docs | 8 hrs |
| G.2.2 | IMPL-ADV-002 | Implement idea seed system | IDEA_SEEDS docs | 4 hrs |
| G.2.3 | IMPL-ADV-003 | Implement Supermemory integration | research doc | 6 hrs |
| G.2.4 | IMPL-ADV-004 | Implement Pareto routing | PARETO docs | 6 hrs |

---

## DAG Dependencies Summary

```
┌─────────────────────────────────────────────────────────────────────┐
│                     PHASE A: DOCUMENTATION AUDIT                      │
│                    (A.1.1 → A.1.2 → A.1.3 → A.1.4 → A.1.5)           │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PHASE B: GUIDES CONSOLIDATION                     │
│              (B.1.1-B.1.5) → (B.2.1-B.2.7) → (B.3.1-B.3.6)          │
│              (B.4.1-B.4.6) → (B.5.1-B.5.4) → (B.6.1-B.6.2)          │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PHASE C: REFERENCE CONSOLIDATION                  │
│              (C.1.1-C.1.5) → (C.2.1-C.2.12) → (C.3.1-C.3.14)        │
│              (C.4.1-C.4.9) → (C.5.1-C.5.18) → (C.6.1-C.6.5)        │
│                                → (C.7.1-C.7.9) → (C.8.1-C.8.10)      │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PHASE D: CHECKLISTS                               │
│                           (D.1.1)                                     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  PHASE E: WORK STREAM ENTRIES                          │
│              (E.1.1-E.1.10) → (E.2.1-E.2.5)                         │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│  PHASE F: SPRINT 1 (P1)     │   │  PHASE G: SPRINT 2 (P2)     │
│  IMPL-LIB-001 → IMPL-LIB-003 │   │  IMPL-LIB-101 → IMPL-LIB-104│
│  IMPL-HOOK-001 → IMPL-HOOK-004│   │  IMPL-ADV-001 → IMPL-ADV-004│
│  IMPL-TUI-001 → IMPL-TUI-003 │   │                             │
└─────────────────────────────┘   └─────────────────────────────┘
```

---

## Success Criteria

### Phase Completion
- [ ] All 42 guides have EXTENSION_SUMMARY
- [ ] All 84 reference docs have EXTENSION_SUMMARY  
- [ ] All 127 docs indexed and cross-referenced
- [ ] Work stream entries created for all P1/P2 tasks

### Implementation Completion
- [ ] urllib → httpx migration complete (7 files)
- [ ] retry → tenacity migration complete (4 files)
- [ ] polling → watchdog migration complete (1 file)
- [ ] thegent-hooks binary built and functional
- [ ] TUI compositor core implemented

### Quality Gates
- [ ] All docs pass lint (markdownlint)
- [ ] All cross-references valid
- [ ] No broken internal links
- [ ] Consistent formatting across all docs

---

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| Agent timeouts during extension | High | Use batch processing, smaller batches |
| Merge conflicts during consolidation | Medium | Sequential processing, branch isolation |
| Invalid cross-references | Medium | Automated link checking |
| Documentation drift | Low | Regular sync with WORK_STREAM |

---

## References

- [WORK_STREAM.md](./WORK_STREAM.md) - Unified work stream
- [LIBRARY_REPLACEMENT_AUDIT_DEEP.md](./research/LIBRARY_REPLACEMENT_AUDIT_DEEP.md) - Library replacement details
- [HOOK_RUST_MIGRATION_RESEARCH_SYNTHESIS.md](./research/HOOK_RUST_MIGRATION_RESEARCH_SYNTHESIS.md) - Hook migration details
- [TUI_COMPOSITOR_COMPARISON.md](./research/TUI_COMPOSITOR_COMPARISON.md) - TUI framework selection

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-17 | Claude Code | Initial WBS |

