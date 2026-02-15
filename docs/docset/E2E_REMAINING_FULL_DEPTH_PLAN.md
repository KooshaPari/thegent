# E2E Remaining Full-Depth Plan

**Goal:** Cover all remaining CLI surfaces and option combinations in full depth.

**Status:** Chunks 288, 289, 290, 291, 292, and 293 are implemented. Remaining gaps below.

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

## Chunk 293 — Implemented ✅

- `observe_summary` trend-plumbing hardening in CLI, MCP tool/resource, and parity tests
- Unit test: `test_unit_cli.py::TestObserveSummaryImpl::test_observe_summary_impl_trend_samples_controls_query_and_summary`
- Unit test: `test_unit_mcp.py::TestObserveSummaryMCPContracts` (2 tests)
- Unit test: `test_unit_mcp.py::TestMCPObserveSummaryContract::test_observe_summary_resource_returns_json_payload`
- E2E test: `TestObserveSummaryCustom::test_observe_summary_trend_samples_rich_exposes_projection`

---

## Gap Audit (All Implemented ✅)

### 1. Govern Data-Protection — Implemented ✅ (Chunk 288)
- `govern data-protection` — exits 0
- `govern data-protection --format json` — JSON output

### 2. Plan Analyze Deep Options — Implemented ✅ (Chunks 288, 290, 291, 292)
- `plan analyze --resources`, `--continuity`, `--format json`, `--pert`, combined overlays

### 3. Observe Drift Deep Options — Implemented ✅ (Chunk 288)
- `observe drift --format json`, `--structural-budget`, `--semantic-budget`

### 4. Govern Conformance — Implemented ✅ (Chunks 288, 292)
- `govern conformance --check-drift`, `--format json`

### 5. Plan/Dag List Format JSON — Implemented ✅ (Chunk 289)
- `plan list --format json` — JSON output
- `dag list --format json` — JSON output

### 6. History Events --run-id — Implemented ✅ (Chunk 288)
- `history events --run-id <fake>` — exits 0 with empty (no match)

### 7. MCP Service Help — Implemented ✅ (Chunk 288)
- `mcp service --help` — exits 0

### 8. Govern Closure-Pack With DAG (already in TestClosurePack)
- Already covered: `closure-pack --cd <project>` with valid DAG

### 9. Serve Help (already in TestLoginServeHelp)
- Already covered

### 10. Archive --domain — Implemented ✅ (Chunk 288)
- `archive --domain test --days 1` — optional filter

### 11. Operations All Filters — Implemented ✅ (Chunks 288, 291)
- `operations --operation orchestrate`, `recover`, `govern`, `observe`, `plan`, `--format json`

### 12. Observe Trend Deep Options — Implemented ✅ (Chunk 288)
- `observe trend --payload-type`, `--format json`, `--all`, `--owner`

### 13. Migration task-tool, zen — Implemented ✅ (Chunk 288)
- `govern migration task-tool task-tool-18`, `govern migration zen zen-rich-v1`

### 14. Dag/Plan Format Options — Implemented ✅ (Chunk 289)
- `dag status --format json`
- `plan status --format json` (alias)
- `dag ready --format json` (Chunk 288)
- `plan ready --format json` (Chunk 288)

### 15. Observe Summary Trend Wiring — Implemented ✅
- `observe summary --trend-samples` now forwarded through CLI → `observe_summary_impl` (main + MCP)
- MCP observe summary resource/tool now include trend samples and trend meta in response metadata
- Completed: rich-format end-to-end coverage now asserts `trend_samples_requested`, `trend_effective_samples`,
  and query payload visibility in human-readable output.

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
