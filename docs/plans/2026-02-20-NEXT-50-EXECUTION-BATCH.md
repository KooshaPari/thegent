# Plan: Next 50 Execution Items (2026-02-20)

This batch decomposes the current `WORK_STREAM.md` backlog into 50 executable tasks with dependency-safe ordering and parallel lanes.

## Ordered Batch (50)

| # | Item | Lane | Depends On |
|---|------|------|------------|
| 1 | WL-001 OpenRouter WS auth header forwarding | routing | - |
| 2 | WL-002 OpenRouter provider registration | routing | - |
| 3 | WL-003 OpenRouter LiteLLM backend config | routing | 2 |
| 4 | WL-004 OpenRouter model-id mappings | routing | - |
| 5 | WL-005 OpenRouter SSE keep-alive parsing | routing | - |
| 6 | WL-006 Add `.jscpd.json` scope bounds | infra | - |
| 7 | WL-006 Add `gitleaks` file-size/runtime caps | infra | - |
| 8 | WL-006 Replace recursive grep with bounded `rg` scan | infra | - |
| 9 | WL-006 Add quality reload loop caps | infra | - |
| 10 | WL-007 Add `quality-gate` Rust binary | infra | - |
| 11 | WL-007 Add `security-pipeline` Rust binary | infra | - |
| 12 | WL-007 Add integration tests for both binaries | infra | 10,11 |
| 13 | WL-007 Add benchmark harness vs Bash equivalents | infra | 10,11 |
| 14 | WL-010 `sys setup project init` command | core | - |
| 15 | WL-010 `sys setup project list/show/doctor` | core | 14 |
| 16 | WL-010 `install project` command path | core | 14 |
| 17 | WL-011 OR-08 attribution headers | routing | 1,2,3,4,5 |
| 18 | WL-011 OR-09 forward OpenRouter transforms/provider | routing | 17 |
| 19 | WL-011 OR-10 stream tool-call deltas | routing | 17 |
| 20 | WL-011 OR-11 normalize OpenRouter error structure | routing | 17 |
| 21 | WL-011 OR-12 propagate chunk model -> envelope | routing | 17 |
| 22 | WL-011 OR-13 402/408/502/503 handling | routing | 17 |
| 23 | WL-011 OR-14 emit `usage.cost` | routing | 17 |
| 24 | WL-011 OR-15 `/v1/models` proxy model injection | routing | 17 |
| 25 | WL-011 OR-16 preserve content arrays in transform | routing | 17 |
| 26 | WL-012 P3.1 route executors wiring | routing | - |
| 27 | WL-012 P3.2 orchestrator quorum/arbitration | routing | 26 |
| 28 | WL-012 P3.3 routing audit hash-chain logging | routing | 26 |
| 29 | WL-012 P3.4 hysteresis config surfacing | routing | 26 |
| 30 | WL-013 continuity packet -> Supermemory API provider | core | - |
| 31 | WL-014 queue schema + JSONL persistence | core | - |
| 32 | WL-014 queue TUI list/claim/complete wiring | core | 31 |
| 33 | WL-014 `$defer` injection into queue | core | 31 |
| 34 | WL-015 rules sync for Cursor output | core | - |
| 35 | WL-015 rules sync merge into `CLAUDE.md` | core | - |
| 36 | WL-015 rules sync update Codex skill output | core | - |
| 37 | WL-015 add `--dry-run` and `--platform` flags | core | 34,35,36 |
| 38 | WL-016 persistent Python worker pool | core | - |
| 39 | WL-017 interactive input widget | tui | - |
| 40 | WL-017 table widget (sort/select/paginate) | tui | - |
| 41 | WL-017 timeline widget | tui | - |
| 42 | WL-017 wire widgets into default compositor layout | tui | 39,40,41 |
| 43 | WL-018 Cursor token-file provider schema | routing | - |
| 44 | WL-018 token refresh + executor rebind | routing | 43 |
| 45 | WL-018 validate/appply cursor minimax channel patch | routing | 43 |
| 46 | WL-018 docs updates for Cursor OAuth/setup | docs | 43 |
| 47 | WL-019 HITL gate in PolicyEngine + await_approval event | core | - |
| 48 | WL-019 `thegent govern approve` command | core | 47 |
| 49 | WL-019 `thegent govern reject` command | core | 47 |
| 50 | WL-019 MCP tools for approve/reject | core | 48,49 |

## Immediate Parallel Execution Lanes

- `infra`: 6-13
- `routing`: 1-5, 17-25
- `core`: 14-16, 30-33, 34-38, 47-50
- `tui`: 39-42

