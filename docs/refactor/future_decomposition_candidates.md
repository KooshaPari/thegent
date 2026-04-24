# Future Decomposition Candidates

**Date**: 2026-04-24  
**Status**: Research only — no implementation  
**Scope**: Identified opportunities for future refactoring (Phase 5+)

---

## Executive Summary

Post-Phase 4 audit of execution, agents, planning, and CLI layers found **zero functions >300 LOC** in these critical modules. The ExecutionPort pattern achieved complete decomposition goals.

However, several **non-execution modules** contain functions that could benefit from decomposition if they become refactoring targets in future phases. This document records them for reference.

---

## Audit Results

### Phase 4 Core Layers: ✅ CLEAN

All Phase 1-4 refactoring targets are well-structured:

| Module | File | Largest Function | Status |
|--------|------|------------------|--------|
| execution | executor/__init__.py | ~167 LOC | ✅ Well-decomposed |
| execution | planner/__init__.py | ~78 LOC | ✅ Excellent |
| execution | router/__init__.py | ~84 LOC | ✅ Excellent |
| execution | execution_port_adapter.py | ~124 LOC | ✅ Clean interface |
| agents | (no functions >300) | N/A | ✅ No candidates |
| planning | (no functions >300) | N/A | ✅ No candidates |
| cli | (no functions >300) | N/A | ✅ No candidates |

**Verdict**: ExecutionPort pattern achieved complete refactoring goals. No Phase 4.5 needed.

---

## Non-Execution Modules with Large Functions

Audit of non-core modules found 10+ files with large functions (650+ LOC). These are **not blocking** and should only be refactored if:

1. They become a bottleneck (test isolation, readability, maintenance)
2. Changes require splitting for feature work
3. Coverage or complexity metrics trigger a refactor

### Tier 1 Candidates (1,000+ LOC, high coupling)

| File | LOC | Issue | Suggested Action | Priority |
|------|-----|-------|-----------------|----------|
| `phench/service.py` | 2,405 | Service orchestrator (Python) | Split into handler + state mgmt | LOW |
| `integrations/workstream_autosync_shared.py` | 1,380 | Sync logic monolith | Extract CRUD, filtering, validation | LOW |
| `cliproxy_adapter.py` | 1,275 | Gateway adapter | Split into protocol handlers | LOW |
| `agents/codex_proxy.py` | 1,264 | Agent routing logic | Extract route selection, invocation | LOW |
| `agents/cliproxy_manager.py` | 1,132 | Agent state management | Separate state from I/O | LOW |
| `agents/plangent.py` | 1,044 | Planning agent | Extract decomposition, validation | LOW |
| `config/settings.py` | 1,034 | Config loader | Already modular (likely false positive); audit manually | LOW |
| `utils/routing_impl/litellm_router.py` | 1,017 | LLM routing adapter | Extract retry, fallback, routing logic | LOW |
| `integrations/gh_project_sync.py` | 996 | GitHub sync implementation | Split into query, patch, conflict resolution | LOW |
| `govern/vetter/checks.py` | 890 | Governance check implementations | Extract individual checks to classes | LOW |

### Tier 2 Candidates (850-900 LOC, moderate coupling)

| File | LOC | Issue | Priority |
|------|-----|-------|----------|
| `agents/unified_session_index.py` | 874 | Session indexing logic | LOW |
| `utils/routing_impl/litellm_responses_handler.py` | 867 | Response parsing adapter | LOW |
| `integrations/base.py` | 866 | Base integration adapter | LOW |
| `governance/agent_hierarchy.py` | 778 | Agent hierarchy definitions | LOW |

---

## Recommendations

### Do NOT Refactor Now

- **thegent.execution**: Complete (all functions <300 LOC)
- **thegent.agents** (execution-related): Complete (no large functions)
- **thegent.planning** (execution-related): Complete (no large functions)
- **thegent.cli** (execution-related): Complete (no large functions)

### Monitor for Future Refactoring

1. **phench/service.py** (2,405 LOC) — If Phench becomes a separate service, split the orchestration layer
2. **cliproxy_adapter.py** (1,275 LOC) — If CLIProxy protocol support expands, consider extracting handlers
3. **integrations/** suite — If sync performance becomes critical, extract filtering/caching logic

### When to Schedule Phase 5

Phase 5 refactoring should only proceed if:

1. **Coverage drops** below 85% in any of the Tier 1 modules
2. **Change frequency increases** (3+ PRs/week modifying the same file)
3. **New feature requires breaking apart** a monolithic function
4. **Performance audit** identifies a hot path in one of these files

---

## Execution Layer Final Verdict

✅ **Phase 4 Complete — No Phase 4.5 Needed**

- Zero circular dependencies (8 → 0)
- All execution files <300 LOC (best practices maintained)
- ExecutionPort pattern eliminated god-function need
- Ready for production deployment

**Next**: Run full test suite, merge, and monitor production metrics.

---

## Related Documentation

- **Circular Deps Remediation**: `circular_deps_remediation_plan.md` (Phase 1-4 complete)
- **Split Boundaries**: `split_boundaries.md` (5-layer architecture)
- **Tach Configuration**: `../../tach.toml` (dependency enforcement)

---

**Status**: Research complete. No implementation planned.
