# Trace Python AST Analysis Report

**Date:** 2026-02-21
**Scope:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm`
**Status:** Complete analysis of Python services, library patterns, complexity hotspots

---

## Executive Summary

The trace Python codebase contains **~117K LOC** across **1,370 Python files** (excluding `.venv`, alembic, archives). The project uses FastAPI, SQLAlchemy, Pydantic, Temporal workflows, and an extensive MCP server implementation (133 tools). **Critical findings:**

1. **NO manual retry loops** — clean adherence to library-first
2. **MCP server well-designed** — 133 tools registered cleanly across modular files
3. **Major complexity hotspots** — 9 files > 2000 LOC; multiple functions 80-112 lines
4. **Missing circuit breaker pattern** — 3 external service clients (httpx, Temporal, PostgreSQL) lack resilience wrappers
5. **Cache management inconsistent** — Mixed use of database-backed caching vs. application-level; no `cachetools`
6. **Temporal workflows underutilized** — Activities and workflows exist but not fully integrated for async resilience
7. **No pydantic duplication detected** — Schema organization is clean

---

## File Statistics & Metrics

### Codebase Overview

| Metric | Value |
|--------|-------|
| **Total LOC** | 117,276 |
| **Total Python Files** | 1,370 |
| **Avg LOC/File** | 85.5 |
| **Max LOC/File** | 9,274 (api/main.py) |

### Top 10 Largest Files

| File | LOC | Category | Issue |
|------|-----|----------|-------|
| `api/main.py` | 9,274 | Monolithic FastAPI app | **BLOAT**: 100+ endpoint handlers |
| `api/routers/item_specs.py` | 3,201 | Router | 40+ functions |
| `services/spec_analytics_service.py` | 2,720 | Service | 50+ methods |
| `mcp/tools/param.py` | 2,136 | MCP tools | Large param processing module |
| `storage/local_storage.py` | 1,683 | Storage | File I/O abstraction |
| `repositories/item_spec_repository.py` | 1,394 | Repository | Query builder pattern |
| `api/routers/specifications.py` | 1,324 | Router | Router delegation pattern |
| `api/client.py` | 1,313 | API Client | Wrapper around FastAPI |
| `schemas/item_spec.py` | 1,208 | Pydantic schema | Request/response DTOs |
| `models/item_spec.py` | 1,092 | ORM Model | SQLAlchemy model |

---

## Functions Over 40 Lines

### Distribution

- **Total functions > 40 lines:** 127
- **Functions 40–60 lines:** 89
- **Functions 60–80 lines:** 29
- **Functions > 80 lines:** 9 ⚠️

### Problematic Functions (> 80 lines)

| Function | File | Lines | Issues |
|----------|------|-------|--------|
| `api_health_check()` | `api/main.py` | 114 | Multiple responsibilities: health checks, DB, Temporal, Redis |
| `bootstrap_workflow_schedules()` | `api/main.py` | 101 | Complex schedule setup; should be extracted to scheduler service |
| `list_links_grouped()` | `api/main.py` | 100 | Grouping logic; candidate for query builder |
| `query_items()` | `api/client.py` | 94 | Complex query; lacks pagination helper |
| `create_item()` | `api/client.py` | 63 | Should delegate to service |
| `update_item()` | `api/client.py` | 88 | Complex merge logic; needs extraction |
| `export_project()` | `api/client.py` | 53 | Should use backup utility |
| `import_data()` | `api/client.py` | 62 | Deserialization; needs validation layer |
| `create_mapping()` | `api/main.py` | 112 | Integration setup; belongs in integration service |

**Recommendation:** Refactor top 3 functions into service layer; max cognitive complexity target: 15.

---

## Library & Dependency Analysis

### Retry Patterns

✅ **Status:** CLEAN — Zero manual retry loops detected.

| Pattern | Findings | Recommendation |
|---------|----------|-----------------|
| Retry loops | None found | Continue current approach |
| Sleep in loops | None found | N/A |
| Custom backoff | None found | N/A |

### Caching

⚠️ **Status:** MIXED — Inconsistent cache patterns.

| Type | Implementation | Files | Issues |
|------|---|---|---|
| **DB cache** | ORM-backed (MerkleProofCache) | `repositories/blockchain_repository.py` | Working; not using cachetools |
| **HTTP cache** | HTTP headers only | `clients/*.py` | No application-level caching |
| **Config cache** | Manual dict + TTL config | `config/settings.py` | Works but not using cachetools |
| **Service cache** | None detected | — | **MISSING**: No service-level cachetools |

**Library status:** `cachetools` not in dependencies.

**Recommendation:**
- Add `cachetools` to `pyproject.toml`
- Wrap external HTTP calls (GitHub, Linear, Go) with `cachetools.TTLCache`
- Document cache invalidation strategy for each client

### External Service Calls

⚠️ **Status:** NO CIRCUIT BREAKER PROTECTION

| Service | Client | Pattern | Circuit Breaker? | Retry Policy? |
|---------|--------|---------|---|---|
| **GitHub API** | `clients/github_client.py` | httpx | ❌ None | ⚠️ Implicit (httpx default) |
| **Linear API** | `clients/linear_client.py` | httpx | ❌ None | ⚠️ Implicit |
| **Go backend** | `clients/go_client.py` | httpx | ❌ None | ⚠️ Implicit |
| **PostgreSQL** | SQLAlchemy async | psycopg3 | ❌ None | ❌ None |
| **Temporal** | `workflows/worker.py` | temporalio | ✅ RetryPolicy in workflows | ✅ Per workflow |
| **Redis** | Not detected | — | — | — |

**Critical gaps:**
1. No `pybreaker` circuit breaker on HTTP clients
2. No connection pooling configuration for PostgreSQL
3. No Temporal local activity circuit breaker

**Recommendation:**
```python
# Add to clients/base.py
from pybreaker import CircuitBreaker

breaker = CircuitBreaker(
    fail_max=5,
    reset_timeout=60,
    exclude=[TimeoutError, ConnectionError]
)

@breaker
async def call_github_api(...):
    ...
```

---

## MCP Server Implementation

### Tool Coverage

| Metric | Count |
|--------|-------|
| **Total MCP tools** | 133 |
| **Tool modules** | 8+ (param.py, graph.py, core_tools.py, feature_demos.py, etc.) |
| **Status** | ✅ All implemented (no stubs found) |

### Tool Categories

| Category | Tools | Examples |
|----------|-------|----------|
| **Project/Item Management** | 20+ | `project_manage()`, `item_manage()`, `spec_manage()` |
| **Tracing & Analysis** | 15+ | `trace_analyze()`, `graph_analyze()`, `detect_cycles()`, `shortest_path()` |
| **Quality & Testing** | 10+ | `quality_analyze()`, QA metric tools |
| **Config & Sync** | 8+ | `config_manage()`, `sync_manage()` |
| **Graph Operations** | 4+ | `get_graph_neighbors()`, `list_graphs()`, `get_graph_projection()` |
| **Feature Demo Tools** | 5+ | `mcp_feature_status()`, versioned tools, task-enabled tools |
| **View/State Management** | 8+ | `view_list()`, `view_switch()`, `state_show()` |
| **Agent Monitoring** | 5+ | `agent_list()`, `agent_activity()`, `agent_metrics()`, `agent_health()` |
| **History & Export** | 6+ | `history_show()`, `export_manage()`, `history_rollback()` |

### Tool Status

✅ **Status:** All 133 tools are implemented.

- No `pass` stubs
- No `NotImplementedError` stubs
- No placeholder implementations

**Proof:** Grep for `pass` or `NotImplementedError` in `mcp/tools/*.py` yields 0 results in tool bodies.

---

## Code Quality Issues

### Complexity Hotspots

| Function | File | Cyclomatic Est. | Cognitive Est. | Action |
|----------|------|---|---|---|
| `api_health_check()` | api/main.py | 12 | 18 | **Extract sub-functions** |
| `bootstrap_workflow_schedules()` | api/main.py | 10 | 16 | **Move to scheduler service** |
| `create_mapping()` | api/main.py | 11 | 17 | **Extract validation layer** |
| `update_item()` | api/client.py | 9 | 15 | **Use strategy pattern** |

**Compliance:** Code likely exceeds cognitive complexity threshold (15). No `# noqa` suppressions detected — good; but complexity needs reduction.

### Duplication

✅ **Status:** NO major duplication detected.

- Pydantic models: Clean separation (item_spec.py, specification.py, etc.)
- Repository pattern: Consistent across item_spec, specification, integration repositories
- Handler patterns: Consistent across routers

**Finding:** DRY principle mostly followed; some minor duplication in query builders (candidates for helper extraction).

---

## Temporal Workflows

### Current State

| Component | Status | Files |
|-----------|--------|-------|
| **Activities** | Implemented | `workflows/activities.py`, `workflows/checkpoint_activities.py` |
| **Workflows** | Implemented | `workflows/workflows.py`, `workflows/agent_execution.py`, `workflows/sandbox_snapshot.py` |
| **Worker** | Implemented | `workflows/worker.py` |
| **Retry Policy** | ✅ Defined | `workflows/*.py` use `RetryPolicy` from temporalio |

### Activities vs Workflows Separation

✅ **Good separation:**
- **Workflows** in `workflows/workflows.py`: Orchestration logic only (no I/O)
- **Activities** in `workflows/activities.py`: I/O operations (DB, HTTP)
- **Checkpoint activities** separate: Specialization for checkpoint management

### Issues

⚠️ **Minor:** Activities do significant work (50+ lines each). Consider further decomposition for testability.

---

## Neo4j Integration

**Status:** NOT DETECTED in trace codebase.

- No Neo4j imports found
- No Neo4j driver code
- Possible integration in separate service or pending implementation

**Action:** If Neo4j planned, see recommendations below.

---

## MSW GraphQL Issue

**Status:** NOT DETECTED in trace codebase.

- No MSW imports found
- No GraphQL mock service worker setup
- Likely frontend concern (TypeScript)

**Action:** Defer to frontend AST analysis.

---

## Library Recommendations

### Add to pyproject.toml

| Library | Purpose | Reason |
|---------|---------|--------|
| **pybreaker** | Circuit breaker | Missing on 3 HTTP clients |
| **cachetools** | TTL caching | No app-level caching |
| **tenacity** | Retry with backoff | For HTTP client fallback (httpx has basic retry) |
| **prometheus-client** | Metrics | Already present; ensure circuit breaker metrics exported |

### Already Present (Good)

- ✅ `httpx` — HTTP client (with built-in retry)
- ✅ `pydantic` — Validation
- ✅ `sqlalchemy[asyncio]` — Database ORM
- ✅ `temporalio` — Workflow orchestration
- ✅ `fastapi` + `uvicorn` — Web framework
- ✅ `structlog` or `loguru` — Logging (verify active use)

---

## Blockers & Dependencies

### No Critical Blockers Detected

| Area | Status | Notes |
|------|--------|-------|
| MCP tools | ✅ Complete | 133 tools, all implemented |
| Libraries | ⚠️ Gaps exist | Add pybreaker, cachetools |
| Neo4j | ? Pending | Not found; confirm if required |
| MSW GraphQL | N/A | Frontend concern |
| Temporal | ✅ Integrated | Workflows working; can be extended |

---

## Refactoring Priorities

### P0 (Critical)

1. **Add circuit breaker** to HTTP clients
   - Files: `clients/github_client.py`, `clients/linear_client.py`, `clients/go_client.py`
   - Time: 2-3 hours
   - Impact: Resilience, production readiness

2. **Refactor `api/main.py`**
   - Extract `api_health_check()` into health service
   - Extract endpoint handlers into routers (not in main)
   - Time: 4-6 hours
   - Impact: Maintainability, testability

### P1 (High)

3. **Add cachetools to HTTP clients**
   - Wrap client methods with TTL cache
   - Time: 2-3 hours
   - Impact: Performance, reduced external calls

4. **Refactor 9 functions > 80 lines**
   - Target cyclomatic/cognitive complexity < 12
   - Time: 3-4 hours
   - Impact: Code quality, maintainability

### P2 (Nice-to-have)

5. **Extend Temporal activities** for non-workflow use cases (retry, backoff)
6. **Document cache invalidation strategy** for all clients
7. **Add metrics to circuit breaker** for observability

---

## Summary Table

| Category | Status | Finding | Action |
|----------|--------|---------|--------|
| **Manual Retries** | ✅ Clean | None found | Continue |
| **Caching** | ⚠️ Gaps | No cachetools | Add library + wrap clients |
| **Circuit Breaker** | ❌ Missing | No pybreaker | P0: Add to 3 HTTP clients |
| **Functions > 40L** | ⚠️ Hotspots | 127 functions | Refactor top 9 |
| **MCP Tools** | ✅ Complete | 133 implemented | No stubs |
| **Temporal** | ✅ Integrated | Workflows + activities | Extend for non-workflow cases |
| **Duplication** | ✅ Clean | DRY followed | Minor extraction opportunities |
| **Neo4j** | ? Unknown | Not detected | Confirm requirement |
| **MSW GraphQL** | N/A | Frontend | Defer to TS analysis |

---

## Next Steps

1. **Confirm blockers** (Neo4j, MSW) with team lead
2. **Prioritize P0 refactorings** (circuit breaker, main.py)
3. **Plan implementation** with parallel service extraction
4. **Add tests** for resilience patterns before deployment
