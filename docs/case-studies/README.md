# Case Studies

This directory contains post-mortem analyses and pattern documentation for major refactoring initiatives in thegent. Each case study captures the problem, solution, timeline, and lessons learned for reference by other Phenotype repos.

---

## Published Case Studies

### Thegent 4-Phase Split: 8→0 Circular Dependencies

**File**: `thegent_4_phase_split.md`  
**Date**: 2026-04-24  
**Status**: Complete ✅

**Problem**: 8 circular dependencies blocked testing, refactoring, and modular design.

**Solution**: 4-phase layered refactoring using core abstractions → execution isolation → ExecutionPort pattern → validation.

**Key Insight**: Introduce port interfaces instead of extracting monolithic functions. Let layers naturally decompose.

**Lessons**:
- DI over direct imports
- Ports/adapters for callbacks
- God functions are architecture symptoms
- Enforce boundaries early (tach.toml)
- Isolate legacy code separately

**Outcome**: 5-layer clean architecture (core → execution → logic → adapters), zero cycles verified, all tests passing.

---

## Planned Case Studies

### AgilePlus Monorepo Decomposition (Pending)

Expected: Q3 2026

- **Scope**: Extract shared error handling, config loading, test fixtures into crates
- **Expected pattern**: Workspace consolidation + multi-crate coordination
- **Reference**: phenotype-infrakit Phase 1 (Lines of Code Audit & Optimization)

### FocalPoint Pipeline Refactoring (Pending)

Expected: Q4 2026

- **Scope**: Split monolithic workflow orchestration into plugins/stages
- **Expected pattern**: Plugin architecture, lazy loading, dependency injection
- **Reference**: heliosCLI execution model

---

## How to Use This Hub

1. **When proposing a large refactor**: Check if a similar pattern exists in these case studies
2. **When blocked by cycles/monoliths**: Read the lesson-learned sections for strategies
3. **When designing new modules**: Use the 5-layer pattern (core → logic → adapters) as a baseline
4. **When onboarding new developers**: Link the relevant case study to explain architectural decisions

---

## Pattern Summary

All case studies in this directory follow a **5-layer hexagonal architecture**:

```
┌─────────────────────────────────────┐
│ Layer 3: External Adapters          │  (CLI, MCP, HTTP, etc.)
│ ├─ No business logic                │
│ └─ Thin wrappers around execution   │
├─────────────────────────────────────┤
│ Layer 2: Business Logic             │  (Agents, Models, Plugins)
│ ├─ Implementations of ports         │
│ └─ Can use execution for orchestration
├─────────────────────────────────────┤
│ Layer 1: Execution Engine           │  (Orchestrator, Router, Planner)
│ ├─ Pure business logic              │
│ └─ No upward imports (DI only)      │
├─────────────────────────────────────┤
│ Layer 0: Core Abstractions          │  (Ports, Domain Types, Errors)
│ ├─ No dependencies                  │
│ └─ Interfaces implemented by Layer 2│
└─────────────────────────────────────┘
```

---

## File Organization

```
docs/case-studies/
├── README.md                     # This file (hub)
├── thegent_4_phase_split.md      # 4-phase circular-dep remediation
└── [future case studies]
```

---

**Last updated**: 2026-04-24  
**Maintainer**: Phenotype Agents
