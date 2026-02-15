# E2E Remaining Full-Depth Plan

**Goal:** Cover all remaining CLI surfaces and option combinations in full depth.

**Status:** Chunk 288 (24 tests), Chunk 289 (4 tests), Chunk 290 (6 tests), Chunk 291 (3 tests), and Chunk 292 (7 tests) implemented. Remaining gaps below.

---

## Chunk 288 — Implemented ✅

- TestGovernDataProtectionExecution (2)
- TestPlanAnalyzeDeepOptions (3)
- TestObserveDriftDeepOptions (2)
- TestGovernConformanceCheckDrift (1)
- TestDagPlanReadyFormatJson (2)
- TestHistoryEventsRunId (1)
- TestMcpServiceHelp (1)
- TestArchiveDomainOption (1)
- TestOperationsRecoverFilter (1)
- TestObserveTrendDeepOptions (3)
- TestGovernMigrationAllContracts (2)
- TestGovernEscalateListExecution (3)
- TestHistoryListFormatJson (1)
- TestObserveTrendOwnerOption (1)

## Chunk 289 — Implemented ✅

- TestPlanDagListStatusFormatJson (4): dag list --format json, plan list --format json, dag status --format json, plan status --format json

## Chunk 290 — Implemented ✅

- TestModesFormatJson (3): modes --format json, modes --mode sequential_delegation, modes --mode parallel_consensus --format json
- TestPlanAnalyzePertFormatJson (1): plan analyze --pert --format json
- TestDagListEmptyFormatJson (1): dag list --format json with empty DAG
- TestGovernSweepFormatJson (1): govern sweep --format json

## Chunk 291 — Implemented ✅

- TestOperationsOrchestrateFormatJson (1): operations --operation orchestrate --format json
- TestPlanAnalyzeCombinedOverlays (2): plan analyze --pert --resources, --resources --continuity

## Chunk 292 — Implemented ✅

- TestGovernEscalateAddResolve (4): escalate add/resolve --help, add then resolve, list --past-sla
- TestPlanAnalyzeAllOverlays (2): plan analyze --pert --resources --continuity, with --format json
- TestGovernConformanceFormatJson (1): govern conformance --format json

---

## Gap Audit (All Implemented ✅)

### 1. Govern Data-Protection — Implemented ✅ (Chunk 288)
- `govern data-protection` — exits 0
- `govern data-protection --format json` — JSON output

### 2. Plan Analyze Deep Options (3 → 6 tests)
- `plan analyze --resources` — resource contention overlay
- `plan analyze --continuity` — continuity risk overlay
- `plan analyze --format json` — JSON output

### 3. Observe Drift Deep Options (1 → 4 tests)
- `observe drift --format json` — JSON output
- `observe drift --structural-budget 10 --semantic-budget 15` — custom budgets

### 4. Govern Conformance --check-drift (2 → 3 tests)
- `govern conformance --check-drift` — with empty session dir (deterministic)

### 5. Plan/Dag List Format JSON — Implemented ✅ (Chunk 289)
- `plan list --format json` — JSON output
- `dag list --format json` — JSON output

### 6. History Events --run-id (1 → 2 tests)
- `history events --run-id <fake>` — exits 0 with empty (no match)

### 7. MCP Service Help (0 tests)
- `mcp service --help` — exits 0

### 8. Govern Closure-Pack With DAG (already in TestClosurePack)
- Already covered: `closure-pack --cd <project>` with valid DAG

### 9. Serve Help (already in TestLoginServeHelp)
- Already covered

### 10. Archive --domain (0 tests)
- `archive --domain test --days 1` — optional filter

### 11. Operations All Filters (partial → full)
- `operations --operation orchestrate` (have govern, observe, plan)
- `operations --operation recover` (missing)

### 12. Observe Trend Deep Options (1 → 3 tests)
- `observe trend --payload-type session_contract_health_gate`
- `observe trend --format json`
- `observe trend --all` or `--owner X`

### 13. Migration task-tool, zen (1 → 3 tests)
- `govern migration task-tool task-tool-18`
- `govern migration zen zen-rich-v1`

### 14. Dag/Plan Format Options — Implemented ✅ (Chunk 289)
- `dag status --format json`
- `plan status --format json` (alias)
- `dag ready --format json` (Chunk 288)
- `plan ready --format json` (Chunk 288)

---

## Implementation: Chunk 288 (Full Depth Remaining)

| # | Class | Tests |
|---|-------|-------|
| 1 | TestGovernDataProtectionExecution | 2 |
| 2 | TestPlanAnalyzeDeepOptions | 3 |
| 3 | TestObserveDriftDeepOptions | 2 |
| 4 | TestGovernConformanceCheckDrift | 1 |
| 5 | TestPlanDagListFormatJson | 2 |
| 6 | TestHistoryEventsRunId | 1 |
| 7 | TestMcpServiceHelp | 1 |
| 8 | TestArchiveDomainOption | 1 |
| 9 | TestOperationsAllFilters | 1 |
| 10 | TestObserveTrendDeepOptions | 3 |
| 11 | TestGovernMigrationAllContracts | 2 |
| 12 | TestDagPlanStatusReadyFormatJson | 4 |

**Total: ~22 tests across 12 classes**
