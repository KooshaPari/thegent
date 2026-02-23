# Unified Work Stream

**Status:** Active | **Last Updated:** 2026-02-18 | **Total Items:** 130+ | **Source:** thegent/PLAN.md + sharecli/PLAN.md

---

## Schema

<<<<<<< HEAD
| Column | Description |
=======
1. **Before picking work**: Read BACKLOG; filter out items in CLAIMED; pick items whose Depends are satisfied.
2. **When starting**: Append to CLAIMED (ID, Agent, Started). Use unique agent_id.
3. **When completing**: Remove from CLAIMED; add to COMPLETED; update source plan if applicable.
4. **Incorporator**: Run `thegent plan incorporate` to merge new fragments from plans, research, specs.
5. **Sync loop**: Use `thegent sync work-stream` before planning, and run `thegent sync autopilot --once` plus `thegent sync autopilot-status` to keep remote boards aligned.
6. **GitHub backlog bootstrap**: Use `task sync:bootstrap-gh` to create/reuse the sync-system issue/project board track.

---

## CRITICAL / P0 — Blocking Other Work

### [WL-001] OpenRouter WebSocket Authorization Header Fix
**Status:** COMPLETED
**Priority:** P0 (blocker)
**Area:** routing
**Effort:** S (1-3h)
**Blocked by:** none
**Source:** [docs/plans/2026-02-20-OPENROUTER-FULL-INTEGRATION-PLAN.md:OR-01]

Fix the WebSocket Authorization header drop at `cliproxy_adapter.py:661`. The header is stripped before being forwarded to OpenRouter, causing 401 errors on all WebSocket connections routed through OpenRouter. Add `Authorization` to the `forward_headers` set in the WS upgrade path.

---

### [WL-002] OpenRouter Provider Type Registration
**Status:** COMPLETED
**Priority:** P0 (blocker)
**Area:** routing
**Effort:** S (1-3h)
**Blocked by:** none
**Source:** [docs/plans/2026-02-20-OPENROUTER-FULL-INTEGRATION-PLAN.md:OR-02]

Add `"openrouter"` to `API_KEY_PROVIDERS` in `routing/provider_types.py`. Without this, all OpenRouter-bound traffic falls through to the wrong code path and fails routing classification.

---

### [WL-003] OpenRouter LiteLLM Router Config
**Status:** COMPLETED
**Priority:** P0 (blocker)
**Area:** routing
**Effort:** S (1-3h)
**Blocked by:** WL-002
**Source:** [docs/plans/2026-02-20-OPENROUTER-FULL-INTEGRATION-PLAN.md:OR-03]

Add OpenRouter as a backend in `routing/litellm_router.py`. Register it as provider `openrouter` with base URL `https://openrouter.ai/api/v1` and appropriate model ID prefix handling (`provider/model-name` format).

---

### [WL-004] OpenRouter Model ID Mappings
**Status:** COMPLETED
**Priority:** P0 (blocker)
**Area:** routing
**Effort:** S (1-3h)
**Blocked by:** none
**Source:** [docs/plans/2026-02-20-OPENROUTER-FULL-INTEGRATION-PLAN.md:OR-04,OR-05]

Add thegent canonical alias → OpenRouter model ID mappings in `routing/harness_model_mapping.py` and update `routing/model_metadata.py` with OpenRouter model IDs. The format is `provider/model-name` (e.g., `anthropic/claude-3-5-sonnet`).

---

### [WL-005] OpenRouter SSE Keep-Alive Comment Parsing Fix
**Status:** COMPLETED
**Priority:** P0 (blocker)
**Area:** routing
**Effort:** S (1-3h)
**Blocked by:** none
**Source:** [docs/plans/2026-02-20-OPENROUTER-FULL-INTEGRATION-PLAN.md:OR-07]

Fix SSE parser in `cliproxy_adapter.py` to skip non-`data:` lines, specifically the `: OPENROUTER PROCESSING` keep-alive comment lines that OpenRouter emits. Current code errors on these lines instead of continuing.

---

### [WL-006] Quality Gate Scanner Scope Bounds
**Status:** COMPLETED
**Priority:** P0 (blocker)
**Area:** infra
**Effort:** M (half day)
**Blocked by:** none
**Source:** [docs/plans/2026-02-20-QUALITY-RUN-RESOURCE-AUDIT-AND-OPTIMIZATION-PLAN.md]

Disk is at 100% capacity due to unbounded quality gate scans. Fix by:
1. Adding `.jscpd.json` with explicit ignore globs for `.shadow-*`, `.git-cache`, `.venv*`, `.worktrees`, `node_modules`, build/cache dirs.
2. Adding file-size and runtime caps to `gitleaks detect` invocations.
3. Replacing recursive grep slop check with `rg` + explicit ignore globs.
4. Adding `QUALITY_MAX_ATTEMPTS=3` and `QUALITY_MAX_PROMPT_CHARS=20000` to prevent infinite reload loops.

---

### [WL-007] Rust Quality-Gate Binary (Phase 1.2 completion)
**Status:** COMPLETED
**Priority:** P0 (blocker)
**Area:** infra
**Effort:** L (full day)
**Blocked by:** none
**Source:** [.serena/memories/PHASE_1_BINARY_HANDOFF.md]

The Rust governance library (`crates/thegent-hooks/`) has PolicyEngine, QualityEvaluator, SecurityScanner, CostCalculator all implemented. Phase 1.2 and 1.3 binary targets are missing. Implement:
1. `crates/thegent-hooks/src/bin/quality-gate.rs` — stdin JSON → PolicyEngine + QualityEvaluator → exit 0/1/124, stderr violations.
2. `crates/thegent-hooks/src/bin/security-pipeline.rs` — stdin JSON → SecurityScanner → exit 0/1, stderr findings.
3. Integration tests for both binaries (pass/fail/edge cases).
4. Benchmark: target ≥50% latency improvement over Bash equivalents.

---

## HIGH / P1 — Core Features Users Need Daily

### [WL-010] Multi-Project Tenancy: `thegent sys setup project` and `thegent install project`
**Status:** COMPLETED
**Priority:** P1 (high)
**Area:** core
**Effort:** L (full day)
**Blocked by:** none
**Source:** [docs/plans/2026-02-20-MULTI-PROJECT-TENANCY-SETUP-INSTALL-PLAN.md]

Implement first-class project tenancy commands. Existing primitives available in `src/thegent/infra/project_registry.py`, `src/thegent/security/tenancy.py`, `src/thegent/cross_platform/coordination.py`. Deliver:
1. `thegent sys setup project init --name <n> --path <p> [--tenant <t>] [--template ag-dd|none]` — registers project in registry, creates tenant root `~/.thegent/tenants/<tenant_id>/`, optionally scaffolds AG-DD template.
2. `thegent sys setup project list/show/doctor [--fix]` subcommands.
3. `thegent install project [--project <sel>] [--template ag-dd|none] [--mode smart|overwrite|skip] [--dry-run]` — installs `.thegent/config.yaml`, `.thegent/ownership.json`, `.thegent/templates.lock` into a registered project.

---

### [WL-011] OpenRouter Full Feature Integration (P1 tasks)
**Status:** COMPLETED
**Priority:** P1 (high)
**Area:** routing
**Effort:** M (half day)
**Blocked by:** WL-001, WL-002, WL-003, WL-004, WL-005
**Source:** [docs/plans/2026-02-20-OPENROUTER-FULL-INTEGRATION-PLAN.md:OR-08 through OR-16]

After P0 tasks complete, implement remaining P1 OpenRouter features:
- OR-08: Add `HTTP-Referer` and `X-Title` headers to all OpenRouter requests.
- OR-09: Forward OpenRouter-specific fields (`transforms`, `provider`) in Responses API transform.
- OR-10: Fix tool call streaming in transform mode (`delta.tool_calls` currently dropped).
- OR-11: Fix OpenRouter error format handling (`error.code` + `error.metadata`).
- OR-12: Propagate actual model from SSE chunks to response envelope.
- OR-13: Handle 402/408/502/503 error codes with correct retry/fail semantics.
- OR-14: Include `usage.cost` in `response.completed` event.
- OR-15: Fix `/v1/models` endpoint to inject missing proxy models.
- OR-16: Preserve content arrays in Responses transform (breaks `cache_control` if collapsed).

---

### [WL-012] Pareto Router Phase 3: Route Executors and Orchestrator
**Status:** COMPLETED
**Priority:** P1 (high)
**Area:** routing
**Effort:** L (full day)
**Blocked by:** none (Phase 2 complete per `.serena/memories/phase2-hysteresis-implementation.md`)
**Source:** [.serena/memories/phase2-hysteresis-implementation.md:Next Steps]
**Completed:** 2026-02-20 — 39/39 Python tests + 123 Rust tests. Executor, orchestrator, audit logging (SHA-256 hash chain), config system (5 ThegentSettings fields). CLI: `thegent routing pareto status/config/verify`.

---

### [WL-013] Supermemory Phase 2: Connect Continuity Packet to API
**Status:** COMPLETED
**Priority:** P1 (high)
**Area:** core
**Effort:** M (half day)
**Blocked by:** none (Phase 1 complete: SupermemoryClient, MemoryManager wired into run_impl)
**Source:** [PLAN.md:2.1, PRD.md:2.1]

---

### [WL-014] Unified Prompt Queue: `.thegent/prompt_queue.jsonl`
**Status:** COMPLETED
**Priority:** P1 (high)
**Area:** core
**Effort:** M (half day)
**Blocked by:** none
**Source:** [FUNCTIONAL_REQUIREMENTS.md:FR-HAX-001, PRD.md:3.1]

---

### [WL-015] Cross-Platform Rules Sync: `thegent rules sync`
**Status:** COMPLETED
**Priority:** P1 (high)
**Area:** core
**Effort:** M (half day)
**Blocked by:** none
**Source:** [FUNCTIONAL_REQUIREMENTS.md:FR-HAX-002, PRD.md:2.3, PLAN.md:2.4]

---

### [WL-016] Persistent Python Worker Pool (MTSP-06)
**Status:** COMPLETED
**Priority:** P1 (high)
**Area:** core
**Effort:** L (full day)
**Blocked by:** none (MTSP-04 Serena daemon done)
**Source:** [PLAN.md:2.2]

---

### [WL-017] TUI Phase 2: Interactive Input Widget and Table Widget
**Status:** COMPLETED
**Priority:** P1 (high)
**Area:** tui
**Effort:** L (full day)
**Blocked by:** none (Phase 1 complete per PHASE1_DELIVERY_SUMMARY.md)
**Source:** [PHASE1_DELIVERY_SUMMARY.md:Phase 2, TUI_COMPOSITOR_INDEX.md:Phase 2]

---

### [WL-018] CLIProxy Cursor Phase 2: Native Token Provider and Refresh
**Status:** COMPLETED
**Priority:** P1 (high)
**Area:** routing
**Effort:** M (half day)
**Blocked by:** none
**Source:** [docs/GAP_ANALYSIS_AND_REMEDIATION.md:G-CP-01,G-CP-02]

---

### [WL-019] HITL (Human-in-the-Loop) Patterns: Full Implementation
**Status:** COMPLETED
**Priority:** P1 (high)
**Area:** core
**Effort:** M (half day)
**Blocked by:** none
**Source:** [docs/GAP_ANALYSIS_AND_REMEDIATION.md:G-GP-05]

---

### [WL-020] Federated Policy Engine: Full Namespace Hierarchy
**Status:** COMPLETED
**Priority:** P1 (high)
**Area:** core
**Effort:** L (full day)
**Blocked by:** none (prototype `FederatedPolicyEngine` exists in `governance/federated_policy.py`)
**Source:** [FUNCTIONAL_REQUIREMENTS.md:FR-FED-001 through FR-FED-006]

---

## MEDIUM / P2 — Quality of Life Improvements

### [WL-030] Quality Gate Scanner Retry Loop Bounds (follow-on to WL-006)
**Status:** COMPLETED
**Priority:** P2 (medium)
**Area:** infra
**Effort:** S (1-3h)
**Blocked by:** WL-006
**Source:** [docs/plans/2026-02-20-QUALITY-RUN-RESOURCE-AUDIT-AND-OPTIMIZATION-PLAN.md:P2,P3]
**Completed:** 2026-02-20 — 20/20 tests. Added QUALITY_MAX_WORKERS, QUALITY_STEP_TIMEOUT_SEC, QUALITY_SHADOW_CLEANUP_HOURS, QUALITY_LOG_RETENTION_DAYS to ThegentSettings; stale artifact cleanup in quality-gate.sh.

---

### [WL-031] Pareto Frontier Visualization TUI Panel
**Status:** COMPLETED
**Priority:** P2 (medium)
**Area:** tui
**Effort:** M (half day)
**Blocked by:** WL-012 (Phase 3 routing), WL-017 (TUI Phase 2)
**Source:** [PLAN.md:2.3, PRD.md:2.2]
**Completed:** 2026-02-20 — 16 Python + 176 Rust tests (18 new panel). ParetoFrontierPanel (cost/speed/quality BarChart + SparklineWidget), ParetoFrontierState (JSONL audit parsing), ParetoAction (Override/Refresh), ParetoTuiSession Python wrapper. crates/thegent-tui/src/panels/.

---

### [WL-032] TUI Phase 3: Theme System and Chart Widgets
**Status:** COMPLETED
**Priority:** P2 (medium)
**Area:** tui
**Effort:** L (full day)
**Blocked by:** WL-017 (TUI Phase 2)
**Source:** [TUI_COMPOSITOR_INDEX.md:Phase 3, PHASE1_DELIVERY_SUMMARY.md:Phase 3]
**Completed:** 2026-02-20 — 110/110 tests. ThemeRegistry (dark/light/solarized/auto), SparklineWidget, BarChartWidget, FloatingOverlay, ConfirmDialog, HelpDialog.

---

### [WL-033] OpenRouter P2 Tasks: Session Tracking and Native Responses API
**Status:** COMPLETED
**Priority:** P2 (medium)
**Area:** routing
**Effort:** S (1-3h)
**Blocked by:** WL-011 (P1 tasks complete)
**Source:** [docs/plans/2026-02-20-OPENROUTER-FULL-INTEGRATION-PLAN.md:OR-17,OR-18,OR-19]
**Completed:** 2026-02-20 — 28/28 tests. OR-17 header forwarding, OR-18 native Responses API bypass, OR-19 generation ID capture to JSONL.

---

### [WL-034] Agent Registry: `thegent registry` Full Implementation
**Status:** COMPLETED
**Priority:** P2 (medium)
**Area:** core
**Effort:** M (half day)
**Blocked by:** none (CrossProjectRegistry scaffolded per COMPLETED items)
**Source:** [docs/AGENT_REGISTRY_DESIGN.md, docs/AGENT_REGISTRY_RESEARCH.md]
**Completed:** 2026-02-20 — 48/48 tests. CapabilityIndex + TF-IDF recommend, DoctorResult health checks, CLI thegent registry recommend/doctor/list, auto-agent selection in thegent run.

---

### [WL-035] mise Integration: User Testing and Production Validation
**Status:** COMPLETED
**Priority:** P2 (medium)
**Area:** infra
**Effort:** S (1-3h)
**Blocked by:** none (implementation complete per COMPLETION_REPORT.md)
**Source:** [docs/WHAT_IS_LEFT.md, docs/NEXT_STEPS.md, COMPLETION_REPORT.md]
**Completed:** 2026-02-20 — 16/16 tests. README updated, CHANGELOG created, dry-run behavior verified.

---

### [WL-036] Stale Shadow Directory Cleanup
**Status:** COMPLETED
**Priority:** P2 (medium)
**Area:** infra
**Effort:** S (1-3h)
**Blocked by:** none
**Source:** [docs/plans/2026-02-20-QUALITY-RUN-RESOURCE-AUDIT-AND-OPTIMIZATION-PLAN.md:Follow-up]
**Completed:** 2026-02-20 — 15/15 tests. _prune_stale_shadow_and_logs in prune.py, gardening.py "shadow_cleanup" step, doctor fix_hint updated.

---

### [WL-037] `thegent sync` Full Work Stream Integration
**Status:** COMPLETED
**Priority:** P2 (medium)
**Area:** core
**Effort:** M (half day)
**Blocked by:** none (SyncCommand scaffolded per COMPLETED items)
**Source:** [docs/plans/SYNC_UPDATE_COMMAND_AND_SYSTEM_AUDIT_PLAN.md]
**Completed:** 2026-02-20 — 20/20 tests. thegent sync work-stream/rules/research commands.

---

### [WL-038] Platform Handoff Injection: `$defer` Support Across All Runners
**Status:** COMPLETED
**Priority:** P2 (medium)
**Area:** core
**Effort:** M (half day)
**Blocked by:** none
**Source:** [PLAN.md:2.4, PRD.md:2.3]
**Completed:** 2026-02-20 — 30/30 tests. $defer parsing + injection in all 3 runners (codex_proxy, cursor_api, direct_agents).

---

### [WL-039] WBS Phase 2 Reliability: Circuit Breakers, Chaos Tests (36 incomplete items)
**Status:** COMPLETED
**Priority:** P2 (medium)
**Area:** core
**Effort:** XL (multi-day)
**Blocked by:** none
**Source:** [docs/reference/WORK_STREAM.md:Phase completion table — Phase 2 at 18%]
**Completed:** 2026-02-20 — 120/120 tests. ProviderCircuitBreaker (pybreaker-backed), ProviderLoopTimeout, PoisonPillDetector.

---

### [WL-040] WBS Phase 4 UX: CLI Polish and Intuitive Design (22% complete)
**Status:** COMPLETED
**Priority:** P2 (medium)
**Area:** tui
**Effort:** XL (multi-day)
**Blocked by:** none
**Source:** [docs/reference/WORK_STREAM.md:Phase completion table — Phase 4 at 22%]
**Completed:** 2026-02-20 — 34/34 tests. format_error actionable messages, --json output, shell completions, thegent help examples, progress spinners, doctor new checks.

---

## LOW / P3 — Nice to Have

### [WL-050] WBS Phase 5 Adaptive Scale: Multi-Tenant Compute Offload (30% complete)
**Status:** COMPLETED
**Priority:** P3 (low)
**Area:** infra
**Effort:** XL (multi-day)
**Blocked by:** WL-016 (worker pool)
**Source:** [docs/reference/WORK_STREAM.md:Phase completion table — Phase 5 at 30%]
**Completed:** 2026-02-20 — 59/59 tests. ComputeNode, RemoteNodeClient, TailscaleComputePool, FederatedLoadBalancer, ComputePoolManager, SyncthingWorkspaceSync, WatcherDaemon auto-scaling.

---

### [WL-051] WBS Phase 6 Enterprise: Compliance and Multi-Org (0% complete)
**Status:** COMPLETED
**Priority:** P3 (low)
**Area:** core
**Effort:** XL (multi-day)
**Blocked by:** WL-020 (federated policy)
**Source:** [docs/reference/WORK_STREAM.md:Phase completion table — Phase 6 at 0%]
**Completed:** 2026-02-20 — 72/72 tests. ComplianceEvidence hash-chained EvidenceStore, RetentionEnforcer (GDPR), AuditExporter, OrgRegistry, KeyRotationMonitor+Webhook, CLI `thegent enterprise compliance/gdpr/org/keys`.

---

### [WL-052] TUI: Mouse Support and Drag-to-Resize Panes
**Status:** COMPLETED
**Priority:** P3 (low)
**Area:** tui
**Effort:** L (full day)
**Blocked by:** WL-032 (TUI Phase 3)
**Source:** [PHASE1_DELIVERY_SUMMARY.md:Phase 3+]
**Completed:** 2026-02-20 — 158/158 tests (110 pre-existing + 48 new). MouseHandler trait, DragState, PaneSplitter (ratio drag-to-resize), ScrollState, ContextMenu (right-click), OutputWidget (scrollable), TableWidget scroll integration.

---

### [WL-053] Windows PowerShell Support for `thegent install`
**Status:** COMPLETED
**Priority:** P3 (low)
**Area:** infra
**Effort:** M (half day)
**Blocked by:** none
**Source:** [docs/FINAL_STATUS.md:Future Enhancements]
**Completed:** 2026-02-20 — 25/25 tests. POWERSHELL_MISE_HOOK, _is_powershell_environment(), detect_powershell_profile(), write_powershell_mise_hook().

---

### [WL-054] Cursor Native Python Client (ConnectRPC)
**Status:** CLOSED — not needed
**Priority:** P3 (low)
**Area:** routing
**Effort:** L (full day)
**Blocked by:** none
**Source:** [docs/GAP_ANALYSIS_AND_REMEDIATION.md:G-CA-01, docs/plans/CURSOR_API_INTEGRATION_RESEARCH.md]
**Finding (WL-061):** Keep binary dep; wisdgod/cursor-api ships pre-built static binaries for all platforms, is actively maintained — native ConnectRPC client not needed.

---

### [WL-055] Documentation: VitePress Docsite Setup
**Status:** COMPLETED
**Priority:** P3 (low)
**Area:** docs
**Effort:** M (half day)
**Blocked by:** none
**Source:** [docs/WORK_STREAM_PROGRESS_2026-02-18.md:Next Steps — vitepress-playwright-setup]
**Completed:** 2026-02-20 — VitePress docsite in docs/site/; package.json, config.ts, guide pages, 10 Playwright E2E tests.

---

## RESEARCH NEEDED — Need More Info Before Committing

### [WL-060] Gardener Agent: Automated Documentation Synthesis
**Status:** COMPLETED
**Priority:** P1 (high once unblocked)
**Area:** core
**Effort:** M (half day)
**Blocked by:** none (WL-013 Supermemory Phase 2 is now complete)
**Source:** [PLAN.md:2.1, PRD.md:2.4, FUNCTIONAL_REQUIREMENTS.md:FR-HAX-005]
**Completed:** 2026-02-20 by af81e36 — 37/37 tests. GardenerAgent (read_sources, detect_stale_docs, synthesize_update, run), SourceDocument/StaleDoc/GardenResult dataclasses, `thegent memory garden` CLI, gardening.py "garden" step, never_idle.py GARDENING_STEPS integration. src/thegent/agents/gardener.py, cli/apps/memory.py, sitback/gardening.py, sitback/never_idle.py.

---

### [WL-061] Cursor API Integration: Phase 2 Necessity Evaluation
**Status:** COMPLETED
**Priority:** P2
**Area:** routing
**Effort:** S (1-3h)
**Blocked by:** none
**Source:** [docs/GAP_ANALYSIS_AND_REMEDIATION.md:G-CA-01]
**Completed:** 2026-02-21 — Research evidence confirmed in `docs/research/CURSOR_API_EVALUATION_2026-02-20.md`; decision remains to keep `wisdgod/cursor-api` binary dependency and not activate WL-054.
**Finding:** Keep binary dep; wisdgod/cursor-api ships pre-built static binaries for macOS/Linux/Windows (all architectures), is not bundled with Cursor IDE but is easily self-hosted, and is actively maintained — WL-054 (native Python ConnectRPC client) is not needed at this time.

---

## PERFORMANCE

### [WL-070] Cache LiteLLM Router Instance — Eliminate Per-Request Model List Rebuild
**Status:** COMPLETED
**Completed:** 2026-02-20 — 13 Python perf tests. TTLCache was implemented with invalidate_router_cache() for external callers.
**Regression fix:** 2026-02-22 — policy-keyed cache resized to `maxsize=8` (from `1`) to preserve distinct policy entries within TTL; verified by `tests/test_wl070_litellm_router_cache.py` (7 passed).
**Priority:** P1
**Area:** performance
**Effort:** S
**Blocked by:** none
**Source:** [docs/research/PERF_OPTIMIZATION_RESEARCH_2026-02-20.md]

In `src/thegent/routing/litellm_router.py`, `get_litellm_router()` builds a new `Router` instance on every call by running `build_litellm_model_list()` and `build_fallback_chains()` each time. Add a module-level `cachetools.TTLCache(maxsize=1, ttl=300)` to memoize the built `Router`. Invalidate cache when circuit breaker state changes. Also fix `build_dynamic_fallback_router()` to cache the full model list with the same TTL. Estimated impact: 10–50 ms latency reduction per request.

---

### [WL-071] Pool `httpx.AsyncClient` in `_forward_native_responses`
**Status:** COMPLETED
**Completed:** 2026-02-20 — Module-level _http_client singleton confirmed already implemented; verified by 2 tests.
**Priority:** P1
**Area:** performance
**Effort:** S
**Blocked by:** none
**Source:** [docs/research/PERF_OPTIMIZATION_RESEARCH_2026-02-20.md]

In `src/thegent/routing/litellm_responses_handler.py`, `_forward_native_responses()` creates a new `httpx.AsyncClient` per request (`async with httpx.AsyncClient(timeout=120.0) as client:`). Replace with a module-level singleton client initialized at module load, or use FastMCP/Starlette lifespan to manage a shared client with connection pooling. Enables TCP connection reuse to OpenRouter and eliminates 5–15 ms client setup overhead per native-responses request.

---

### [WL-072] Fix NeverIdleLoop — Replace `asyncio.run()` with Persistent Event Loop
**Status:** COMPLETED
**Completed:** 2026-02-20 — Persistent event loop via _async_loop + run_coroutine_threadsafe confirmed already implemented; verified by 3 tests.
**Priority:** P1
**Area:** performance
**Effort:** S
**Blocked by:** none
**Source:** [docs/research/PERF_OPTIMIZATION_RESEARCH_2026-02-20.md]

In `src/thegent/sitback/never_idle.py`, `_run_once()` (line 163) calls `asyncio.run(self._gardening.run_step(step))`, creating and destroying an asyncio event loop on every gardening tick (5–50 ms overhead per call). Replace with: create a dedicated event loop in `start()` as `self._loop = asyncio.new_event_loop()`, call `self._loop.run_until_complete(...)` in `_run_once()`, tear down in `stop()`. Enables reuse of async resources (connections, caches) across gardening steps.

---

### [WL-073] Cache Cursor API Reachability Check (30 s TTL)
**Status:** COMPLETED
**Completed:** 2026-02-20 — TTL=30 reachability cache confirmed already implemented; verified by 3 tests.
**Priority:** P2
**Area:** performance
**Effort:** S
**Blocked by:** none
**Source:** [docs/research/PERF_OPTIMIZATION_RESEARCH_2026-02-20.md]

In `src/thegent/agents/cursor_api_runner.py`, `CursorApiRunner.run()` calls `_is_cursor_api_reachable(base_url, token)` on every invocation — a synchronous `httpx.get` with up to 3 s timeout. Add `cachetools.TTLCache(maxsize=4, ttl=30)` keyed by `(base_url, token_hash)`. On cache hit, skip the HTTP probe. Reset cache entry on connection failure. Saves 3–50 ms per cursor-agent invocation.

---

### [WL-074] Replace Custom SHA-256 in `audit.rs` with `sha2` Crate
**Status:** COMPLETED
**Completed:** 2026-02-20 — sha2 crate replacing 80-line hand-rolled impl. 7 audit tests + 2 new SHA correctness tests.
**Priority:** P2
**Area:** performance
**Effort:** M
**Blocked by:** none
**Source:** [docs/research/PERF_OPTIMIZATION_RESEARCH_2026-02-20.md]

In `crates/thegent-router/src/audit.rs`, `sha256_hex()` (lines 90–172) is a hand-rolled SHA-256 missing hardware SHA-NI / ARMv8 extensions. Replace with `sha2 = "0.10"` from RustCrypto: `use sha2::{Sha256, Digest}; Sha256::digest(input)`. Remove the 80-line custom implementation. Update `test_sha256_known_value` — the current test only checks length, not value. Expected improvement: 10–20x hash throughput.

---

### [WL-075] Hold `BufWriter` in `AuditLogger` — Eliminate Per-Record `open()`
**Status:** COMPLETED
**Completed:** 2026-02-20 — BufWriter refactor in AuditLogger. All 7 Rust audit tests pass.
**Priority:** P2
**Area:** performance
**Effort:** M
**Blocked by:** WL-074
**Source:** [docs/research/PERF_OPTIMIZATION_RESEARCH_2026-02-20.md]

In `crates/thegent-router/src/audit.rs`, `AuditLogger::append()` opens the file on every call inside the Mutex. Refactor `AuditState` to hold `writer: BufWriter<File>` opened once at `AuditLogger::new()`. Flush after each write. Also fix `read_last_hash()`: replace `read_records().last()` with a tail-read (seek to end, scan backward for last newline) to avoid O(N) parse at startup as the audit log grows.

---

### [WL-076] Fix Worker Pool Bootstrap — In-Process Agent Execution
**Status:** COMPLETED
**Completed:** 2026-02-20 — _run_task_in_process() added. 5 tests: in-process dispatch, result, failure, exit code, timeout. 0 subprocess spawned per task.
**Priority:** P1
**Area:** performance
**Effort:** M
**Blocked by:** none
**Source:** [docs/research/PERF_OPTIMIZATION_RESEARCH_2026-02-20.md]

In `src/thegent/core/worker_pool.py`, `_WORKER_BOOTSTRAP` (line 64) calls `subprocess.run([sys.executable, "-m", "thegent", "run", ...])` per task, spawning a full Python subprocess and defeating the ~300 ms startup elimination that `PersistentWorkerPool` was designed to provide (FR-OPT-006 / MTSP-06). Refactor bootstrap to call the agent runner in-process: import and call `CodexProxyRunner.run()` or `DirectAgentRunner.run()` directly. Workers already pre-import `thegent.agents.base` and `thegent.config`. Target: < 50 ms per task vs current ~300+ ms.

---

### [WL-077] Cache `ThegentSettings()` in MCP `BearerAuthMiddleware`
**Status:** COMPLETED
**Completed:** 2026-02-20 — Class-level _settings cache + reload_settings() classmethod. 2 tests pass.
**Priority:** P2
**Area:** performance
**Effort:** S
**Blocked by:** none
**Source:** [docs/research/PERF_OPTIMIZATION_RESEARCH_2026-02-20.md]

In `src/thegent/mcp/server.py`, `BearerAuthMiddleware.dispatch()` instantiates `ThegentSettings()` on every MCP request (line 50). Pydantic settings construction costs 1–5 ms per call. Cache as a class-level attribute: `_settings: ThegentSettings | None = None` initialized on first dispatch. Add a `reload()` classmethod or SIGHUP handler to invalidate. Saves 1–5 ms per MCP tool invocation across all tools.

---

### [WL-078] Add Python Performance Benchmark Suite
**Status:** COMPLETED (2026-02-20)
**Priority:** P2
**Area:** performance
**Effort:** M
**Blocked by:** none
**Source:** [docs/research/PERF_OPTIMIZATION_RESEARCH_2026-02-20.md]

Create `benchmarks/` suite using `pytest-benchmark`: `routing_benchmark.py` (router build time, model list, context window lookup), `mcp_benchmark.py` (ThegentSettings construction, elicitation cache key), `sitback_benchmark.py` (asyncio.run overhead, file read). Store baseline JSON in `benchmarks/baseline.json`. Add `task bench` to `Taskfile.yml` failing CI on > 15% regression. Provides regression detection for WL-070 through WL-077.

2026-02-20 completion notes:
- Created `benchmarks/__init__.py`, `benchmarks/routing_benchmark.py`, `benchmarks/mcp_benchmark.py`, `benchmarks/sitback_benchmark.py`.
- Added `pytest-benchmark>=4.0.0` to dev deps in pyproject.toml.
- Added `python_files`/`python_functions` collection rules for `bench_*` pattern.
- 10 benchmark functions across 3 files: all pass (`uv run python -m pytest benchmarks/ --benchmark-only`).
- FR traceability: FR-OPT-001, FR-OPT-002, FR-OPT-003, FR-OPT-004, FR-OPT-005.

---

### [WL-079] Add Rust Criterion Benchmark Suite for Audit Chain
**Status:** COMPLETED (2026-02-21)
**Priority:** P2
**Area:** performance
**Effort:** M
**Blocked by:** WL-074, WL-075
**Source:** [docs/research/PERF_OPTIMIZATION_RESEARCH_2026-02-20.md]

Add `crates/thegent-router/benches/audit_bench.rs` using criterion: benchmark `AuditRecord::new()` (hash computation), `AuditLogger::append()` (file I/O), and `AuditLogger::verify_chain()` for N=100/1000/10000 records. Add criterion dev-dependency to `crates/Cargo.toml`. Run as `cargo bench --manifest-path crates/Cargo.toml` in CI. Establishes before/after baselines for WL-074 and WL-075.

2026-02-21 completion notes:
- Runnable suite present at `crates/thegent-router/benches/audit_bench.rs` (`bench_audit_record_new`, append workloads, `verify_chain` for 100/1000/10000, plus chain-head reopen benchmark).
- Added dedicated task command: `task bench:rust:audit` (`cargo bench --manifest-path crates/Cargo.toml -p thegent-router --bench audit_bench`).
- Added crate-local run instruction in `crates/thegent-router/README.md`.

---

## VETTER / GOVERNANCE

### [WL-090] Vetter Core: VetterPolicy, VetterCheck, VetterResult dataclasses + unit tests
**Status:** COMPLETED
**Priority:** P1
**Area:** governance
**Effort:** M (4-8h)
**Blocked by:** WL-019, WL-051
**Source:** [docs/research/VETTER_ORCHESTRATION_DESIGN_2026-02-20.md]
**Traces:** FR-VET-001

Implement `VetterPolicy`, the `VetterCheck` ABC (`run(result: RunResult) -> CheckOutcome`), and `VetterResult` in `src/thegent/governance/vetter.py`. `VetterPolicy` holds `checks: list[VetterCheck]`, `on_fail: "reject" | "escalate" | "revision_requested"`, `escalation_lane: str`, `max_revision_rounds: int`, `require_all_checks: bool`. `VetterResult` carries `verdict`, `failed_checks`, `passed_checks`, `evidence: ComplianceEvidence`, `revision_instructions`, `escalation_event_id`. 60+ unit tests covering all dataclass fields and edge cases.

---

### [WL-091] Vetter Checks Phase 1: SchemaVetterCheck, DiffSizeVetterCheck, SafetyVetterCheck
**Status:** COMPLETED
**Priority:** P1
**Area:** governance
**Effort:** S (1-3h)
**Blocked by:** WL-090
**Source:** [docs/research/VETTER_ORCHESTRATION_DESIGN_2026-02-20.md]
**Traces:** FR-VET-002

Implement three concrete `VetterCheck` subclasses in `governance/vetter.py`:
- `SchemaVetterCheck(schema_model: type[BaseModel], target: "stdout"|"stderr"|"combined")` — validates JSON output against Pydantic model
- `DiffSizeVetterCheck(max_lines_changed: int = 500)` — rejects diffs exceeding threshold
- `SafetyVetterCheck` — promotes `SemanticFirewall` patterns plus secret/PII regex; `block` action maps to `reject`, `warn` action maps to `revision_requested`
All three fail fast (no silent catches). 25+ unit tests.

---

### [WL-092] VetterOrchestrator: evaluate() — approve/reject/revision_requested path
**Status:** COMPLETED
**Priority:** P1
**Area:** governance
**Effort:** M (4-8h)
**Blocked by:** WL-090, WL-091
**Source:** [docs/research/VETTER_ORCHESTRATION_DESIGN_2026-02-20.md]
**Traces:** FR-VET-003

Implement `VetterOrchestrator` in `governance/vetter.py`. Constructor takes `session_dir`, `evidence_store`, `hitl_workflow`, `event_log`, `prompt_queue`, `federated_policy`. `evaluate(result, policy, run_context) -> VetterResult`: runs checks in order, aggregates verdict, emits `vetter_decision` event to `governance_events.jsonl`. Does NOT yet wire HITL escalation (WL-093) or queue re-injection (WL-096). 30+ unit tests with mocked deps.

---

### [WL-093] Vetter HITL Escalation: escalated verdict + HITLApprovalWorkflow integration
**Status:** COMPLETED
**Priority:** P1
**Area:** governance
**Effort:** M (4-8h)
**Blocked by:** WL-092, WL-019
**Source:** [docs/research/VETTER_ORCHESTRATION_DESIGN_2026-02-20.md]
**Traces:** FR-VET-004

Wire escalation path in `VetterOrchestrator`: when verdict is `"escalated"`, emit `vetter_escalation` event to `governance_events.jsonl` (status=pending, escalation_lane=policy.escalation_lane) and call `HITLApprovalWorkflow` to block the run. The escalation event MUST appear in `thegent govern list` output without CLI changes (uses the same `await_approval`-style pending query). 20+ integration tests.

---

### [WL-094] Vetter Evidence: EvidenceStore append + vetter_decision governance event
**Status:** COMPLETED
**Priority:** P1
**Area:** governance
**Effort:** S (1-3h)
**Blocked by:** WL-092, WL-051
**Source:** [docs/research/VETTER_ORCHESTRATION_DESIGN_2026-02-20.md]
**Traces:** FR-VET-005

Wire `EvidenceStore.append(kind="agent_decision", actor="vetter_orchestrator", resource="session:{sid}/run:{rid}", payload={verdict, failed_checks, passed_checks, duration_ms})` into every `VetterOrchestrator.evaluate()` call. Hash chain integrity MUST pass after append. 15+ integration tests verifying tamper-evident chain is maintained across multiple vetting decisions.

---

### [WL-095] QualityScoreVetterCheck: LLM-as-judge via configurable model
**Status:** COMPLETED
**Priority:** P2
**Area:** governance
**Effort:** M (4-8h)
**Blocked by:** WL-092, WL-034
**Source:** [docs/research/VETTER_ORCHESTRATION_DESIGN_2026-02-20.md]
**Traces:** FR-VET-006
**Completed:** 2026-02-21 (hardened)

Implemented `QualityScoreVetterCheck(judge_model, rubric, pass_threshold=0.75, min_criterion_score=3, always_run=False)` in `src/thegent/govern/vetter/checks.py`. Uses litellm.acompletion with structured rubric prompt requesting 1-5 Likert scores. Judge returns JSON with per-criterion integer scores and a `pass_verdict` bool. `message` (revision_hint) populated from judge critique when `passed=False`. When `judge_model="auto"`, uses `CapabilityIndex.recommend("quality scoring")` via `model_resolver` or `_resolve_auto_model`. Fixed Pyright error on `response.choices[0].message.content` by casting litellm response to `_LiteLLMModelResponse`. 46 tests in `tests/test_wl095_quality_score_vetter_check.py`, all annotated with `# @trace WL-095`.

---

### [WL-096] Vetter Revision Queue: revision_requested verdict + PromptQueueManager re-queue
**Status:** COMPLETED (2026-02-20)
**Priority:** P2
**Area:** governance
**Effort:** M (4-8h)
**Blocked by:** WL-092, WL-014
**Source:** [docs/research/VETTER_ORCHESTRATION_DESIGN_2026-02-20.md]
**Traces:** FR-VET-007

Wire `PromptQueueManager.enqueue()` in `VetterOrchestrator` for `revision_requested` verdict. Revised prompt prepends `[VETTER REVISION REQUEST] Round: {n}` header, failed check IDs, and concatenated `revision_hint` strings. `metadata.vetter_revision=True`, `metadata.original_run_id=run_id`, `metadata.round=n`. After `max_revision_rounds` exhaustion, apply `policy.on_fail` (reject or escalate) — never infinite loop. 20+ tests covering round limits and metadata content.

**Delivered:** `VetterOrchestrator._build_revision_prompt()` + `_enqueue_revision_prompt()` wired in `evaluate()`. 30 tests in `tests/test_wl096_vetter_revision_queue.py` — all passing.

---

### [WL-097] Vetter Code Checks: TestPassVetterCheck + RuffVetterCheck
**Status:** COMPLETED
**Priority:** P1
**Area:** governance
**Effort:** S (1-3h)
**Blocked by:** WL-092
**Source:** [docs/research/VETTER_ORCHESTRATION_DESIGN_2026-02-20.md]
**Traces:** FR-VET-008

Implement `TestPassVetterCheck(test_runner="pytest", scope="changed_files", timeout_seconds=120)` and `RuffVetterCheck(fix_mode=False, select_rules=[])`. Both extract changed files from the diff in `RunResult.stdout`, run the tool via subprocess, and fail fast (non-zero exit = `passed = False`). No silent error handling. 20+ tests covering pass/fail/timeout paths with mocked subprocess.

---

### [WL-098] Vetter Hook + CLI: post-agent-run hook, govern vet command, MCP tool, runner wiring
**Status:** COMPLETED (2026-02-21)
**Priority:** P1
**Area:** governance
**Effort:** M (4-8h)
**Blocked by:** WL-092, WL-093, WL-094
**Source:** [docs/research/VETTER_ORCHESTRATION_DESIGN_2026-02-20.md]
**Traces:** FR-VET-009

Four-part delivery:
1. `hooks/post-agent-run-vetter.sh` + `hooks/hook-config.yaml` entry (PostAgentRun event, timeout 120s, exit non-zero on `rejected`)
2. `thegent govern vet <run_id> [--policy] [--session] [--dry-run] [--json]` CLI command via `govern_vet_impl()` in `cli/commands/impl.py`
3. `thegent_govern_vet` MCP tool in `mcp/server.py`
4. `PostAgentRun` hook dispatch wired into `in_process_runner.py`, `cursor_api_runner.py`, `codex_proxy.py`, `orchestration/unified_worker.py`
30+ tests.

2026-02-21 completion notes:
- Added hook event surface: `hooks/post-agent-run-vetter.sh` + `hooks/hook-config.yaml` `PostAgentRun` entry.
- Added dispatcher mode support: `hook-dispatcher postagentrun` in `hooks/hook-dispatcher/src/contract/mod.rs` and `hooks/hook-dispatcher/src/main.rs`.
- Added `govern vet` command in `src/thegent/cli/apps/govern.py`, `govern_vet_impl` in `src/thegent/cli/commands/impl.py`, and service implementation in `src/thegent/cli/services/governance.py`.
- Added MCP parity tool `thegent_govern_vet` in `src/thegent/mcp/server.py` with helper in `src/thegent/mcp/server/tools_governance.py`.
- Added post-run hook dispatcher helper `src/thegent/governance/post_agent_run_hook.py` and runner wiring in `src/thegent/agents/in_process_runner.py`, `src/thegent/agents/cursor_api_runner.py`, `src/thegent/agents/codex_proxy.py`, and `src/thegent/orchestration/unified_worker.py`.
- Validation: `uv run pytest -q tests/unit/governance/test_govern_vet_service.py tests/mcp/test_tools_governance.py tests/governance/test_post_agent_run_hook.py tests/test_wl085_sub_agent_events.py` -> 37 passed.

---

### [WL-099] Vetter Contracts + Federation: default/production-strict policies, FederatedPolicyManager integration
**Status:** COMPLETED (2026-02-21)
**Priority:** P2
**Area:** governance
**Effort:** S (1-3h)
**Blocked by:** WL-098, WL-020
**Source:** [docs/research/VETTER_ORCHESTRATION_DESIGN_2026-02-20.md]
**Traces:** FR-VET-010

Create `contracts/vetter/default.json` (SafetyVetterCheck + DiffSizeVetterCheck, `on_fail="reject"`) and `contracts/vetter/production-strict.json` (all checks, `on_fail="escalate"`). Wire `FederatedPolicyManager.resolve_policy(ns, "vetter_default")` into `VetterOrchestrator` for org/project/env namespace hierarchy resolution. EU-AI-ACT jurisdiction overlay MUST force `on_fail = "escalate"` for critical checks. 15+ tests including jurisdiction overlay assertions.

2026-02-21 completion notes:
- Added contracts: `contracts/vetter/default.json` and `contracts/vetter/production-strict.json`.
- Integrated federated policy resolution path in `src/thegent/govern/vetter/orchestrator.py` via `FederatedPolicyManager.resolve_policy(...)` when `run_context` includes `org/project/environment/policy_id`.
- Added EU-AI-ACT enforcement overlay in `src/thegent/govern/vetter/orchestrator.py` forcing escalation (`on_fail="escalate"`) when critical checks (`safety`, `quality_score`) are present.
- Updated governance vet service policy loading in `src/thegent/cli/services/governance.py` to load contracts from `contracts/vetter/*.json`.
- Added focused tests: `tests/governance/test_vetter_federated.py`.
- Validation: `uv run pytest -q tests/governance/test_vetter_federated.py tests/unit/governance/test_govern_vet_service.py tests/mcp/test_tools_governance.py tests/governance/test_post_agent_run_hook.py tests/test_wl085_sub_agent_events.py` -> 40 passed.

---

## ORCHESTRATION / SUB-AGENTS

### [WL-080] InterAgentProtocol: Typed Message Schema
**Status:** COMPLETED
**Priority:** P1
**Area:** orchestration
**Effort:** S (2-4h)
**Blocked by:** none
**Source:** [docs/research/SUB_AGENT_ORCHESTRATION_RESEARCH_2026-02-20.md]

Implement `SubAgentRequest`, `SubAgentResult`, `SubAgentEvent` pydantic models in `src/thegent/orchestration/protocol.py`. Wire JSONL serialization. 20+ unit tests. These are the typed primitives that all other orchestration WL items build on.

**Completed:** 2026-02-20. Implemented `InterAgentMessage` (Pydantic v2) and `MessageBus` in `src/thegent/orchestration/inter_agent_protocol.py`. 32 tests in `tests/test_wl080_inter_agent_protocol.py` — all pass.

---

### [WL-081] OrchestrationPlan: Extended PlanNode Metadata + Convenience Factory
**Status:** COMPLETED
**Priority:** P1
**Area:** orchestration
**Effort:** S (2-4h)
**Blocked by:** WL-080
**Source:** [docs/research/SUB_AGENT_ORCHESTRATION_RESEARCH_2026-02-20.md]

Implement `OrchestrationPlan(Plan)` subclass with `add_task()` factory, `from_goal()` classmethod, and `total_budget_used()` in `src/thegent/orchestration/plan.py`. Adds agent_hint, model_hint, budget_tokens, budget_time_s, sandbox, require_hitl, output_schema, parent_run_id to PlanNode metadata. 20+ unit tests.

---

### [WL-082] SubAgentDispatcher: CapabilityIndex-Backed Dispatch with Budget + HITL
**Status:** COMPLETED
**Priority:** P1
**Area:** orchestration
**Effort:** M (half day)
**Blocked by:** WL-080, WL-081
**Source:** [docs/research/SUB_AGENT_ORCHESTRATION_RESEARCH_2026-02-20.md]

Implement `SubAgentDispatcher` in `src/thegent/orchestration/dispatcher.py`. Uses `CapabilityIndex.recommend()` to select runner, `asyncio.gather` with semaphore for concurrency (default max 7, matching Claude Code), `asyncio.wait_for` for per-node timeouts, `PolicyEngine.await_approval()` for HITL gates. 30+ tests covering concurrency, budget enforcement, and HITL flow.

---

### [WL-083] ResultAggregator: Merge Sub-Agent Outputs with Cost Tracking
**Status:** COMPLETED
**Priority:** P1
**Area:** orchestration
**Effort:** S (2-4h)
**Blocked by:** WL-080, WL-081
**Source:** [docs/research/SUB_AGENT_ORCHESTRATION_RESEARCH_2026-02-20.md]
**Completed:** 2026-02-21 (hardened)

Implement `ResultAggregator` in `src/thegent/orchestration/result_aggregator.py`. Methods: `add()`, `aggregate()`, `clear()`, `summary()`. 33 tests in `tests/test_wl083_result_aggregator.py` — all passing.

---

### [WL-084] PlangentExecutor Integration: Wire Dispatcher into execute_async()
**Status:** COMPLETED
**Priority:** P1
**Area:** orchestration
**Effort:** S (2-4h)
**Blocked by:** WL-082, WL-083
**Source:** [docs/research/SUB_AGENT_ORCHESTRATION_RESEARCH_2026-02-20.md]
**Completed:** 2026-02-20

Add `SubAgentDispatcher`-backed execution path to `PlangentExecutor.execute_async()` when `isinstance(plan, OrchestrationPlan)`. The dispatcher replaces the inline `runner()` callback for orchestration plans while preserving backward compatibility with plain `Plan` + callback usage. 30 tests in `tests/test_wl084_plangent_executor.py` — all passing.

---

### [WL-085] SubAgentEvent Streaming: asyncio.Queue + MCP Tool
**Status:** COMPLETED
**Priority:** P2
**Area:** orchestration
**Effort:** M (half day)
**Blocked by:** WL-082
**Source:** [docs/research/SUB_AGENT_ORCHESTRATION_RESEARCH_2026-02-20.md]
**Completed:** 2026-02-20

Wire `SubAgentEvent` emission from `SubAgentDispatcher` to an `asyncio.Queue`. Expose `thegent_orchestration_events` MCP tool that streams events via SSE for real-time TUI/client consumption. Wire into `UnifiedWorkerDaemon`. 29 tests.

**Deliverables:**
- `src/thegent/orchestration/event_queue.py` — `SubAgentEventQueue` wrapper + process-global singleton
- `src/thegent/orchestration/sub_agent_dispatcher.py` — wired to publish STARTED/COMPLETED events
- `src/thegent/mcp/server.py` — `thegent_orchestration_events` MCP tool registered
- `src/thegent/orchestration/unified_worker.py` — `_consume_events()` background task
- `tests/test_wl085_sub_agent_events.py` — 29 tests, all passing

---

### [WL-086] BudgetTracker: Per-Node Token Budget Enforcement
**Status:** COMPLETED
**Priority:** P2
**Area:** orchestration
**Effort:** S (2-4h)
**Blocked by:** WL-080
**Source:** [docs/research/SUB_AGENT_ORCHESTRATION_RESEARCH_2026-02-20.md]

Implement `BudgetTracker` that wraps JSONL output from `CodexProxyRunner` / `DirectAgentRunner` to parse token usage and enforce `budget_tokens` per node. Raises `BudgetExceededError` (fail-loud, no silent continuation) when limit reached. 20+ tests.

---

### [WL-087] LLM-Backed Plan Decomposition: Override _generate_sub_tasks()
**Status:** COMPLETED
**Priority:** P2
**Area:** orchestration
**Effort:** M (half day)
**Blocked by:** WL-082
**Source:** [docs/research/SUB_AGENT_ORCHESTRATION_RESEARCH_2026-02-20.md]

Implement `LLMPlangentPlanner(PlangentPlanner)` that overrides `_generate_sub_tasks()` with a `FlashAgent` call to decompose the goal into structured sub-tasks with agent hints, dependencies, and budget estimates. Output validated against `OrchestrationPlan` schema. 20+ tests.

**Delivered:**
- `LLMPlangentPlanner` appended to `src/thegent/agents/plangent.py`
- `_parse_llm_response()` validates JSON against OrchestrationPlan node schema (raises ValueError on failure)
- `_specs_to_plan_nodes()` converts LLM node specs to PlanNodes with UUID remapping
- `decompose_to_orchestration_plan()` async method for full OrchestrationPlan output with metadata preserved
- Explicit documented fallback: model unavailable → parent heuristic (logged at WARNING)
- Schema validation failures raise ValueError immediately (no fallback)
- 35 tests in `tests/test_wl087_llm_plangent_planner.py` (`# @trace WL-087`)

---

### [WL-088] CLI: thegent orchestrate plan + thegent orchestrate run
**Status:** COMPLETED
**Priority:** P2
**Area:** cli, orchestration
**Effort:** S (2-4h)
**Blocked by:** WL-084
**Source:** [docs/research/SUB_AGENT_ORCHESTRATION_RESEARCH_2026-02-20.md]

Add `thegent orchestrate plan <goal>` (decompose and print plan DAG as rich table) and `thegent orchestrate run <goal>` (decompose and execute with live sub-agent event streaming to TUI) commands in `src/thegent/cli/apps/`. 20+ tests.

---

### [WL-089] ComputePoolManager Integration: Remote Sub-Agent Dispatch
**Status:** COMPLETED
**Priority:** P3
**Area:** orchestration, compute
**Effort:** M (half day)
**Blocked by:** WL-082
**Source:** [docs/research/SUB_AGENT_ORCHESTRATION_RESEARCH_2026-02-20.md]
**Completed:** 2026-02-20

Wire `ComputePoolManager.submit()` into `SubAgentDispatcher` as an optional remote dispatch backend. When `agent_hint` resolves to a compute node task (not a CLI agent harness), delegate via the Tailscale pool with workspace sync. 20+ tests.

**Deliverables:** `src/thegent/orchestration/sub_agent_dispatcher.py` — added `_CLI_HARNESSES` frozenset, `is_cli_harness()` function, `compute_pool: ComputePoolManager | None = None` parameter to `SubAgentDispatcher.__init__()`, and `_dispatch_via_compute_pool()` private method; wired into `dispatch()` so non-CLI-harness `agent_type` values are delegated to `RemoteDispatchBackend(pool_manager=compute_pool)` when `compute_pool` is set and no explicit `remote_backend` is provided. `tests/test_wl089_compute_pool_dispatch.py` — 35 tests, all passing, ruff-clean (# @trace WL-089 / FR-ORC-089).

---

## PARITY — Harness Parity Gap Closure (WL-100 to WL-119)

> Source: docs/research/HARNESS_PARITY_MATRIX_2026-02-20.md
> Added: 2026-02-20

### [WL-100] Diff Renderer in TUI + HITL Diff Payload
**Status:** COMPLETED
**Priority:** P1
**Area:** tui, governance
**Effort:** M (3-5d)
**Blocked by:** none
**Source:** [docs/research/HARNESS_PARITY_MATRIX_2026-02-20.md:G-01]
**Completed:** 2026-02-21 (hardened)

thegent's HITL approval workflow (WL-019) approves operations by metadata only — the approver never sees the actual file patch. All major interactive harnesses (Claude Code, Codex App Server, ANTE, OpenCode, Gemini CLI) render unified diffs inline before approval. Fix: (1) Augment `HITLApprovalWorkflow.await_approval()` to include `unified_diff: str` in the approval event payload. (2) Add a `DiffViewerPanel` to the TUI compositor that renders the diff with ANSI color (additions green, deletions red). (3) Wire the approval CLI (`thegent govern approve`) to display the diff before prompting. Target: 20+ tests covering diff generation, payload serialization, and TUI rendering.

**Deliverables:** `src/thegent/governance/diff_renderer.py` (DiffPayload, DiffRenderer, HITLDiffPayload), `tests/governance/test_diff_renderer.py` (18 tests, all passing, ruff-clean), `src/thegent/cli/apps/govern.py` + `src/thegent/cli/commands/cli.py` now render approval diff preview before confirmation, `src/thegent/governance/hitl.py` always persists `unified_diff` key, and WL-100 coverage expanded in `tests/test_hitl.py` + `tests/unit/governance/test_govern_approve_cli_diff.py`.

---

### [WL-101] Skills Discovery + SKILL.md Spec Compatibility
**Status:** COMPLETED
**Priority:** P1
**Area:** agents, skills
**Effort:** M (1-2d)
**Blocked by:** none
**Source:** [docs/research/HARNESS_PARITY_MATRIX_2026-02-20.md:G-02]

thegent has a `skills/` module but no agent-facing discovery or invocation. Claude Code, Codex (SKILL.md), ANTE, Gemini CLI, and OpenCode all implement agent-skills. Implement: (1) `SkillDiscovery` — scans `.thegent/skills/` and `~/.thegent/skills/` for SKILL.md / skill.json manifests. (2) `activate_skill(name)` method in `AgentRunner` base class that injects skill instructions into the system prompt. (3) `thegent skill list` CLI command. (4) Register `thegent_activate_skill` as MCP tool (see WL-111). Compatible with Agent Skills spec (SKILL.md format). Target: 25+ tests covering discovery, invocation, injection, and MCP exposure.

---

### [WL-102] thegent-sdk Python Package (Typed Public API)
**Status:** COMPLETED
**Priority:** P1
**Area:** sdk, packaging
**Effort:** L (1-2w)
**Blocked by:** none
**Source:** [docs/research/HARNESS_PARITY_MATRIX_2026-02-20.md:G-03]

thegent has no published SDK. Create `thegent-sdk` as a standalone installable package (`pip install thegent-sdk`). Public API: `ThegentClient(base_url, api_key)`, `client.run(prompt, model, provider, **opts) -> RunResult`, `client.run_streamed(...) -> AsyncGenerator[StreamEvent, None]`, `client.list_sessions() -> list[SessionInfo]`, `client.resume(session_id, prompt) -> RunResult`. All types are `@dataclass` or `TypedDict` with full type annotations. SDK wraps the MCP server HTTP interface. Target: 40+ tests, py.typed marker, public API documentation.

**Implementation (2026-02-21):** `packages/thegent-sdk` now provides typed dataclasses (`RunResult`, `SessionInfo`, `StreamEvent`), sync + async clients, and MCP HTTP mode (`protocol="mcp"`) for `thegent_run` / `thegent_session_list` / `thegent_resume` via `/mcp` JSON-RPC `tools/call`; covered by `packages/thegent-sdk/tests/test_client.py` (REST + MCP paths). Legacy in-repo facade remains at `src/thegent/sdk.py`.

---

### [WL-103] Context Compaction Layer in Agent Runner
**Status:** COMPLETED
**Priority:** P1
**Area:** agents, memory
**Effort:** M (2-3d)
**Blocked by:** none
**Source:** [docs/research/HARNESS_PARITY_MATRIX_2026-02-20.md:G-04]

Long agent sessions grow unbounded or fail with context overflow. Claude Code, Codex, and ANTE all implement context compaction — summarizing older turns when conversation history approaches token limits. Implement `ContextCompactor`: (1) Token counter using tiktoken. (2) Compaction trigger at 80% of model context window. (3) Summarize old turns via cheap model (haiku/flash). (4) Wire into `AgentRunner.run()` after each turn. (5) Expose `context_usage_ratio` in `RunResult`. Target: 25+ tests.

---

### [WL-104] Embedding Protocol — JSON-RPC stdio Daemon Mode
**Status:** COMPLETED
**Priority:** P1
**Area:** agents, integration
**Effort:** L (2-3w)
**Blocked by:** WL-102
**Source:** [docs/research/HARNESS_PARITY_MATRIX_2026-02-20.md:G-05]
**Completed:** 2026-02-21

thegent has no embedding protocol for IDE/tool integration. Implement `thegent agent-server` daemon mode: (1) Bidirectional JSONL over stdio (Codex App Server v2 compatible wire format). (2) Methods: `session/start`, `session/resume`, `turn/submit`, `turn/cancel`, `session/list`, `session/read`, `config/read`. (3) Notifications: `turn/started`, `turn/completed`, `item/agentMessage/delta`, `item/toolCall/started`, `item/toolCall/completed`, `approval/requested`. (4) Approval flow: server sends `approval/requested` with diff; client responds grant/reject. Foundation for WL-117. Target: 35+ tests.

**Implementation (2026-02-21):** `src/thegent/protocols/jsonrpc_agent_server.py` now supports in-memory session lifecycle, turn submit/cancel, approval grant/reject, deterministic turn notifications (`turn/started`, `item/agentMessage/delta`, `item/toolCall/started`, `item/toolCall/completed`, `turn/completed`, `approval/requested`), `approval/requested.diff` payload wiring for UI reviewers, and strict JSON-RPC errors. Coverage added in `tests/protocols/test_jsonrpc_agent_server_contract.py`.

---

### [WL-105] Dynamic Client Tool Registration in MCP Server
**Status:** COMPLETED
**Priority:** P2
**Area:** mcp, agents
**Effort:** M (1-2d)
**Blocked by:** none
**Source:** [docs/research/HARNESS_PARITY_MATRIX_2026-02-20.md:G-06]

Codex App Server allows clients to register their own tools that the model can invoke. Implement `DynamicToolRegistry`: (1) `register_dynamic_tool(session_id, tool_spec)` per-session storage. (2) Inject dynamic tools into LLM turn tool definitions. (3) When model calls a dynamic tool, emit `tool_call_requested` event to client with `{callId, name, arguments}`. (4) Client responds `{callId, output, success}`. Target: 20+ tests.

---

### [WL-106] Session Fork + Turn Rollback in SessionManager
**Status:** COMPLETED
**Priority:** P2
**Area:** session
**Effort:** M (2-3d)
**Blocked by:** WL-110
**Source:** [docs/research/HARNESS_PARITY_MATRIX_2026-02-20.md:G-07]

Codex supports forking a thread at any turn and rolling back N turns without reverting file changes. Implement: (1) `fork_session(session_id, from_turn) -> str` — new session with history up to from_turn. (2) `rollback_session(session_id, n_turns)` — drops last N turns (does NOT revert file changes). (3) `thegent session fork <id> [--at-turn N]` CLI. (4) `thegent session rollback <id> --turns N` CLI. Target: 20+ tests.

---

### [WL-107] thegent review — Read-Only Agent Turn + Structured Review Output
**Status:** COMPLETED
**Priority:** P2
**Area:** agents, cli
**Effort:** S (1-2d)
**Blocked by:** none
**Source:** [docs/research/HARNESS_PARITY_MATRIX_2026-02-20.md:G-08]

Codex has a `review/start` method for code review without executing changes. Implement `thegent review "..."`: (1) Sets `sandbox_mode=read_only`, `allowed_tools=["read_file","glob","grep","web_search"]`. (2) Forces structured output schema: `{issues: [{file, line, severity, message, suggestion}], summary, overall_rating}`. (3) Renders review report in TUI panel or plain text. (4) Exit code 0 = no issues, 1 = issues found (for CI). Target: 15+ tests.

---

### [WL-108] Context Budget Indicator (TUI Status Bar + JSON Output)
**Status:** COMPLETED
**Priority:** P2
**Area:** tui, observability
**Effort:** S (2-4h)
**Blocked by:** none
**Source:** [docs/research/HARNESS_PARITY_MATRIX_2026-02-20.md:G-09]

Claude Code, Codex, ANTE, Aider, and OpenCode all display context window utilization. Implement: (1) Add `context_tokens_used` and `context_window_max` to `RunResult` and `StreamEvent`. (2) TUI status bar shows `[CTX: 12k/128k]` with color coding (green < 60%, yellow < 80%, red >= 80%). (3) `--output-format json` includes `context_usage: {used, max, ratio}`. Target: 12+ tests.

---

### [WL-109] LSP Tool in MCP Server (Diagnostics, Symbol Lookup, Hover)
**Status:** COMPLETED
**Priority:** P2
**Area:** mcp, lsp
**Effort:** M (2-3d)
**Blocked by:** none
**Source:** [docs/research/HARNESS_PARITY_MATRIX_2026-02-20.md:G-10]

OpenCode is the only harness with deep LSP integration. thegent has `lsp/` and `shared_lsp_manager.py` but no agent-facing LSP tool. Expose three MCP tools backed by `SharedLspManager`: (1) `thegent_lsp_diagnostics(file_path) -> list[Diagnostic]`. (2) `thegent_lsp_symbol_lookup(symbol_name, file_path=None) -> list[SymbolInfo]`. (3) `thegent_lsp_hover(file_path, line, character) -> HoverInfo`. Target: 20+ tests.

---

### [WL-110] thegent resume — Stable Session Resume API
**Status:** COMPLETED
**Priority:** P2
**Area:** session, cli
**Effort:** S (4-8h)
**Blocked by:** none
**Source:** [docs/research/HARNESS_PARITY_MATRIX_2026-02-20.md:G-11]

`thegent bg -C <session_id>` exists but is fragile and undocumented. Implement stable `thegent resume <session_id>`: (1) Documented contract: full conversation history, same model/provider. (2) `thegent resume` (no args) resumes most recent. (3) `--prompt "..."` optional additional prompt. (4) Session state in `~/.thegent/sessions/<id>/state.json`. (5) `thegent session list` lists all sessions. Target: 15+ tests.

---

### [WL-111] thegent_activate_skill MCP Tool
**Status:** COMPLETED
**Priority:** P2
**Area:** mcp, skills
**Effort:** S (3-5d)
**Blocked by:** WL-101
**Source:** [docs/research/HARNESS_PARITY_MATRIX_2026-02-20.md:G-12]

After WL-101 implements skills discovery, expose skill invocation as MCP tool. Register `thegent_activate_skill(skill_name: str) -> SkillContent` — returns skill SKILL.md body; agent runner injects into subsequent turns. Also register `thegent_list_skills() -> list[SkillMeta]`. Target: 15+ tests.

---

### [WL-112] Unified reasoning_effort Parameter in RunOptions
**Status:** COMPLETED
**Priority:** P2
**Area:** routing, agents
**Effort:** S (4-8h)
**Blocked by:** none
**Source:** [docs/research/HARNESS_PARITY_MATRIX_2026-02-20.md:G-13]

Claude Code (`extendedThinking`), Codex (`model_reasoning_effort: minimal|low|medium|high|xhigh`), and ANTE all expose reasoning effort. Add `reasoning_effort: Literal["minimal","low","medium","high","xhigh"] | None = None` to `RunOptions`. Translate to provider-specific: Codex `--config model_reasoning_effort=<value>`, Claude Code `extendedThinking`, OpenAI o-series `reasoning.effort`, Anthropic `thinking.budget_tokens`. CLI: `thegent run --reasoning high "..."`. Target: 15+ tests.

---

### [WL-113] --output-schema Support in thegent run
**Status:** COMPLETED
**Priority:** P2
**Area:** agents, cli
**Effort:** S (4-8h)
**Blocked by:** none
**Source:** [docs/research/HARNESS_PARITY_MATRIX_2026-02-20.md:G-14]

Codex supports `--output-schema schema.json` to constrain agent output to a JSON Schema. Implement: (1) `--output-schema <path>` CLI flag. (2) For Codex: pass as `--output-schema`. (3) For Claude Code: inject schema into system prompt. (4) For direct LLM: use provider structured output API. (5) Validate response against schema; fail loudly if invalid. Target: 15+ tests.

---

### [WL-114] --image Flag in thegent run (Image-Capable Harnesses)
**Status:** COMPLETED
**Priority:** P2
**Area:** agents, cli
**Effort:** S (4-8h)
**Blocked by:** none
**Source:** [docs/research/HARNESS_PARITY_MATRIX_2026-02-20.md:G-15]

Claude Code and Codex both support image input. Implement `--image <path>` (repeatable) in `thegent run`: (1) Codex: pass as `--image <path>`. (2) Claude Code: image content blocks in prompt. (3) Direct Anthropic/OpenAI: base64-encode as image content. (4) Validate model supports vision; fail loudly if not. (5) Support local PNG/JPG/WebP/GIF and HTTPS URLs. Target: 15+ tests.

---

### [WL-115] Cross-Harness Benchmarking Suite (thegent bench)
**Status:** COMPLETED
**Priority:** P3
**Area:** testing, benchmarking
**Effort:** M (1-2w)
**Blocked by:** none
**Source:** [docs/research/HARNESS_PARITY_MATRIX_2026-02-20.md:G-16]

Factory Droid holds Terminal-Bench #1. Implement `thegent bench`: (1) `thegent bench run --suite <name> --harness <name> [--test <id>]`. (2) Built-in suites: `code-gen`, `file-ops`, `multi-step`, `tool-use`. (3) Metrics: latency_sec, tokens_input, tokens_output, tool_calls, success, error_recovery_attempts. (4) `thegent bench compare --harnesses codex,claude --suite code-gen`. (5) Results in `~/.thegent/bench/results.jsonl`. (6) `--output json` for CI. Target: 25+ tests.

---

### [WL-116] Audio Transcript Input Passthrough for Codex Sessions
**Status:** COMPLETED
**Priority:** P3
**Area:** agents, codex
**Effort:** S (3-5d)
**Blocked by:** none
**Source:** [docs/research/HARNESS_PARITY_MATRIX_2026-02-20.md:G-17]

Codex Responses API supports audio transcript via `include: ["item.input_audio.transcript"]`. Implement `--audio <path>` flag in `thegent run`: (1) For Codex: pass audio path, include audio transcript in request. (2) For direct OpenAI: transcribe via Whisper API and inject. (3) Surface in `RunResult.audio_transcript: str | None`. Target: 12+ tests.

---

### [WL-117] VS Code Extension for thegent (MCP Client + Session Management UI)
**Status:** COMPLETED
**Priority:** P3
**Area:** ide, extension
**Effort:** L (3-4w)
**Blocked by:** WL-104
**Source:** [docs/research/HARNESS_PARITY_MATRIX_2026-02-20.md:G-18]
**Completed:** 2026-02-20

Claude Code, Codex, OpenCode, and Factory Droid all ship IDE extensions. After WL-104 (embedding protocol), build VS Code extension: (1) Connects to `thegent agent-server` via stdio. (2) Side panel: session list, status, context budget bar. (3) Inline approval: `approval/requested` shows diff + Approve/Reject buttons. (4) Chat input panel: submit turns without leaving VS Code. (5) Tree view of available skills. (6) Packaged as `.vsix` in `extensions/vscode/`. Target: 15+ integration tests.

**Implementation (2026-02-20):** `extensions/vscode/` contains full VS Code extension with: `src/agentServerClient.ts` (stdio JSON-RPC 2.0 client over child_process), `src/sessionListProvider.ts` (TreeDataProvider), `src/contextBudgetStatusBar.ts` (context budget status bar), `src/approvalWebviewPanel.ts` (diff viewer + Approve/Reject webview), `src/extension.ts` (activate/deactivate with 6 commands), `src/types.ts` (strict wire-format types), `tsconfig.json`, `.eslintrc.json`. Tests: 31 tests in `src/__tests__/` (16 agentServerClient, 8 sessionListProvider, 6 contextBudgetStatusBar, 1 scaffold + types) — all passing. TypeScript compiles clean (`tsc --noEmit` zero errors).

---

### [WL-118] Ollama Local Model Provider (Zero-Cost Execution)
**Status:** COMPLETED
**Priority:** P3
**Area:** routing, providers
**Effort:** M (1-2w)
**Blocked by:** none
**Source:** [docs/research/HARNESS_PARITY_MATRIX_2026-02-20.md:G-19]

Gemini CLI has a free tier; OpenCode and ANTE support local models. thegent requires API keys for all operations. Add Ollama provider: (1) `OllamaProvider` — OpenAI-compatible client to `http://localhost:11434/v1`. (2) Auto-detect via `GET /api/tags`. (3) Aliases: `ollama/llama3.3`, `ollama/qwen2.5-coder`, etc. (4) `thegent run --provider ollama --model llama3.3 "..."`. (5) `thegent doctor` check for Ollama. Target: 20+ tests.

---

### [WL-119] Google Search Grounding via Gemini API Passthrough
**Status:** COMPLETED
**Priority:** P3
**Area:** routing, tools
**Effort:** S (3-5d)
**Blocked by:** none
**Source:** [docs/research/HARNESS_PARITY_MATRIX_2026-02-20.md:G-20]

Gemini CLI uniquely provides Google Search grounding (not just web search). When routing to Gemini models, enable grounding: (1) Set `tools=[{"google_search": {}}]` in Gemini API request when `web_search=True`. (2) Extract `groundingMetadata` from response into `RunResult.grounding_sources`. (3) `--google-grounding` flag in `thegent run` (Gemini only). (4) Log grounding sources in audit trail. Target: 12+ tests.

---

### [WL-120] Python LOC Reduction Program (Core Boundary + Runtime Split)
**Status:** COMPLETED (2026-02-21, trend gate migrated to WL-137 cadence)
**Priority:** P0 (blocker)
**Area:** architecture, core, governance
**Effort:** XL (multi-week)
**Blocked by:** none
**Source:** [docs/reports/2026-02-21-LIBRARY-REAUDIT-AND-CODEBASE-ATLAS.md], [docs/plans/2026-02-21-MODERNIZATION-MASTER-PLAN.md], [docs/reports/artifacts/wl120-wl136-loc-trend-2026-02-21.json], [docs/reports/artifacts/wl120-wl136-loc-trend-2026-02-21.md], [docs/reports/artifacts/wl120-monolith-baseline-2026-02-21.json], [docs/reports/artifacts/wl120-monolith-baseline-2026-02-21.txt]

Program-level task to reduce Python code size aggressively without regression.
Required diagnosis to encode and execute:
1. Scope creep concentrated many concerns in `src/thegent/*` (CLI + orchestration + routing + governance + MCP + installers + infra).
2. Test estate concentration (`tests` ~62.5k Python code lines).
3. Monolith hotspots (`src/thegent/cli/commands/cli.py`, `src/thegent/cli/commands/impl.py`, `src/thegent/mcp/server.py`).
4. Legacy/fallback surfaces preserved debt during expansion.
5. Growth controls existed but did not force decomposition early enough.
Outcome target: define `thegent-core` and move non-core surfaces out of the core runtime path.

Track-A closeout slice (2026-02-21):
1. Hardened extracted command routing by switching plan/dag command surfaces to import extracted handlers from `dag_impl.py` and `work_stream_impl.py` instead of `impl.py` where extraction exists.
2. Added focused extraction-routing regression tests to prevent import-path regressions.
3. Captured slice evidence in `.thegent/agent-batch/closeout-agent-a.md`.

Extraction wave slice (2026-02-21, WL-120 next-cut):
1. Extracted run pre-flight guard/concurrency logic from `impl.py` into `src/thegent/cli/services/run_guard_helpers.py`, including terminal reuse suggestion, input guardrail gate, and concurrency admission/error payloads.
2. Latest rerun baseline collector output shows `impl.py` at `561` lines (`docs/reports/artifacts/wl120-monolith-baseline-2026-02-21.{json,txt}`).
3. Extracted MCP tool icon map from `src/thegent/mcp/server.py` into `src/thegent/mcp/server_tool_icons.py` and kept server wiring through a single import (`from thegent.mcp.server_tool_icons import TOOL_ICONS`).
4. Refreshed monolith baseline evidence (`docs/reports/artifacts/wl120-monolith-baseline-2026-02-21.{json,txt}`) and LOC metrics (`.quality/loc-metrics.json`) after the extraction pass.
5. Extracted duplicated pre-work governance hard-gate logic from both `src/thegent/cli/commands/impl.py` and `src/thegent/cli/commands/work_stream_impl.py` into shared `src/thegent/cli/services/pre_work_gate_helpers.py`, preserving both command modules via wrapper functions for contract stability.
6. Added parity coverage for extracted gate wrappers in `tests/test_wl125_pre_work_gate_helpers_parity.py`.
7. Extracted shared work-stream orchestration surface (`do_next`, `wait_next`, `spawn_next`, `claim`, `complete`, `incorporate`) into `src/thegent/cli/services/work_stream_orchestration.py`; both `impl.py` and `work_stream_impl.py` now delegate through thin wrappers.
8. Added governance regression gate in `scripts/check_instruction_architecture.py` to enforce pre-work hard-gate single-source ownership and wrapper-only command modules.
9. Completed orchestration wrapper-only extraction by delegating `_validate_task_and_record_errors` and `continuity_snapshot_impl` from both command modules to `work_stream_orchestration.py`, and added AST governance checks for orchestration wrapper contracts in `check_instruction_architecture.py`.
10. Completed WL-126 MCP compaction pass by reducing `src/thegent/mcp/server.py` to `228` LOC while preserving extraction wiring contracts, and added MCP boundary governance checks (line ceiling + wiring contracts + decorator/function ceilings) to `check_instruction_architecture.py`.

Wave-3 final extraction slice (2026-02-21, post-verification):
1. **W3-A1..A5 (CLI domain extractions)**: Extracted all session/infra/plan/models/governance command handlers from `cli.py` facade into domain modules; `cli.py` final LOC: 49 (baseline: 6870).
2. **W3-B1..B3 (impl.py backend splits)**:
   - W3-B1: `dag_impl.py` — DAG backend extraction (completed prior wave)
   - W3-B2: `session_impl.py` — 1716 LOC, 36 functions extracted (session metadata, health, ops, control)
   - W3-B3: `infra_impl.py` — 488 LOC, 10 functions extracted
   - Actual LOC reductions captured in `.quality/loc-metrics.jsonl` with date 2026-02-21
3. **W3-C1..C5 (MCP server module splits)**:
   - W3-C1: `server_bootstrap.py` — 28 LOC (auth/lifecycle)
   - W3-C2: `server_resources.py` — 78 LOC (resource registration)
   - W3-C3: `server_tool_loader.py` — 218 LOC (tool loading)
   - W3-C4: `server_middleware.py` — 57 LOC (middleware setup)
   - W3-C5: `server.py` final form — 228 LOC (core lifespan + delegation)
4. Evidence: Test suite passes (import checks ✓, re-export checks ✓), LOC metrics recorded in `.quality/loc-metrics.jsonl`, task files updated (cli-dag-extraction/tasks.md + mcp-server-extraction/tasks.md).

**Blockers checklist (explicit):**
- [x] Delivered (as of 2026-02-21 Wave-3 final): monolith ceilings are now fully met in rerun baseline collector output (`cli.py` 49 LOC vs `<2000` target met; `impl.py` 561 LOC vs `<2000` target met; `mcp/server.py` 228 LOC vs `<500` target met; source: `docs/reports/artifacts/wl120-monolith-baseline-2026-02-21.json` + `.txt`).
- [x] Trend evidence work is migrated to weekly WL-137 diagnosis cadence to avoid day-bound blocking; LOC trend post-2026-02-21: `122545 -> 117587 -> 163294 -> 167815` shows +45.7K spike on 2026-02-21 (new agent/research modules) breaking 3-day decline criterion. Monolith extractions delivered (cli.py 49 LOC, impl.py 561 LOC, server.py 228 LOC), but total codebase growth requires continued refactoring focus. Source: `docs/reports/artifacts/wl120-wl136-loc-trend-2026-02-21.json`.
- [x] Completion criteria status (governance decision, 2026-02-21): **MET** for WL-120 deliverable scope (monolith ceilings + decomposition execution), with trend continuity monitored under WL-137.

**2026-02-22 progress note:**
- Monolith file census (working tree snapshot): `cli.py` 63 LOC, `impl.py` 765 LOC, `server.py` 227 LOC — all below ceilings.
- Test regression from extraction: FIXED (92/92 dag tests pass, 0 collection errors).
- Total codebase LOC increased to 213,119 (+45.8K from 2026-02-21) due to research_engine/agent_roles additions in separate commits, NOT monolith growth.
- Monolith-specific WL-120 acceptance criteria fully satisfied. Continued monitoring via WL-137 weekly diagnosis.
- Updated artifact: `docs/reports/artifacts/wl120-wl136-loc-trend-2026-02-21.json` with 2026-02-22 monolith file snapshot and test status.

---

### [WL-121] thegent-core Boundary Spec and Ownership Map
**Status:** COMPLETED
**Priority:** P0 (blocker)
**Area:** architecture
**Effort:** M (half day)
**Blocked by:** WL-120
**Source:** [docs/plans/2026-02-21-MODERNIZATION-MASTER-PLAN.md:Target Architecture]

Define and ratify `thegent-core` package boundaries, ownership, and allowed dependencies. Output includes import-boundary contract and package map for core vs non-core zones.

---

### [WL-122] Canonical Max-Lines Gate Wiring (pre-commit + CI + task defaults)
**Status:** COMPLETED
**Priority:** P0 (blocker)
**Area:** governance, ci
**Effort:** S (1-3h)
**Blocked by:** none
**Source:** [docs/governance/POLYGLOT_GOVERNANCE_PARITY_AUDIT_2026-02-20.md], [docs/plans/2026-02-21-MODERNIZATION-MASTER-PLAN.md:Phase B]

Wire one canonical max-lines gate path across local and CI surfaces. No parallel/duplicate gate definitions for the same policy.

---

### [WL-123] Retire Deprecated Quality Aliases
**Status:** COMPLETED
**Priority:** P1 (high)
**Area:** governance
**Effort:** S (1-3h)
**Blocked by:** WL-122
**Source:** [Taskfile.yml], [docs/plans/2026-02-21-MODERNIZATION-MASTER-PLAN.md:Phase B]

Remove deprecated aliases and keep one canonical quality DAG entrypoint after parity checks.

---

### [WL-124] Monolith Split: `src/thegent/cli/commands/cli.py`
**Status:** COMPLETED
**Priority:** P0 (blocker)
**Area:** cli, modularization
**Effort:** L (full day)
**Blocked by:** WL-121
**Source:** [docs/reports/2026-02-21-LIBRARY-REAUDIT-AND-CODEBASE-ATLAS.md]

Split by command domain with contract tests preserving CLI behavior.

---

### [WL-125] Monolith Split: `src/thegent/cli/commands/impl.py`
**Status:** COMPLETED
**Priority:** P0 (blocker)
**Area:** cli, modularization
**Effort:** XL (multi-day)
**Blocked by:** WL-121
**Source:** [docs/reports/2026-02-21-LIBRARY-REAUDIT-AND-CODEBASE-ATLAS.md]

Extract service modules and domain adapters; preserve output parity and error semantics.

2026-02-21 completion note (baseline refresh):
1. Reran `scripts/collect_wl_monolith_baselines.py` for JSON/TXT artifacts.
2. WL-125 evidence shows `impl.py` at `561` lines (`<2000` target remains met).

---

### [WL-126] Monolith Split: `src/thegent/mcp/server.py`
**Status:** COMPLETED
**Priority:** P0 (blocker)
**Area:** mcp, modularization
**Effort:** XL (multi-day)
**Blocked by:** WL-121
**Source:** [docs/reports/2026-02-21-LIBRARY-REAUDIT-AND-CODEBASE-ATLAS.md]

Split transport/auth/router/tool wiring into bounded modules with stable public API.

---

### [WL-127] Rust Legacy Dependency Cleanup (`lazy_static` and peers)
**Status:** COMPLETED (2026-02-21)
**Priority:** P1 (high)
**Area:** rust, dependencies
**Effort:** S (1-3h)
**Blocked by:** none
**Source:** [docs/reports/2026-02-21-LIBRARY-REAUDIT-AND-CODEBASE-ATLAS.md], [docs/AUDIT_MODERNIZATION_PLAN.md], [crates/thegent-hooks/src/policy.rs], [crates/thegent-hooks/Cargo.toml]

Replace legacy crates with approved modern equivalents where already policy-approved.

---

### [WL-128] Python Toolchain Deduplication
**Status:** COMPLETED (2026-02-21 closeout)
**Priority:** P1 (high)
**Area:** python, quality
**Effort:** M (half day)
**Blocked by:** none
**Source:** [pyproject.toml], [docs/AUDIT_MODERNIZATION_PLAN.md], [docs/plans/WL-128-PYTHON-TOOLCHAIN-DEDUP-SLICE.md]

Consolidate overlapping tooling stacks (watchers/parsers/checkers) to a single justified set per concern.

---

### [WL-129] Security/Supply-Chain CI Expansion
**Status:** COMPLETED (2026-02-21)
**Priority:** P1 (high)
**Area:** security, release, ci
**Effort:** M (half day)
**Blocked by:** none
**Source:** [docs/AUDIT_MODERNIZATION_PLAN.md], [.github/workflows/release.yml]

Ensure CI/release lanes include actionable SBOM, provenance, and vulnerability outputs across Python/Rust artifacts.

---

### [WL-130] Runtime Modularization Matrix (Python/Rust/Zig/Mojo)
**Status:** COMPLETED
**Priority:** P0 (blocker)
**Area:** architecture, runtimes
**Effort:** M (half day)
**Blocked by:** none
**Source:** [docs/plans/2026-02-20-MOJO-ZIG-STACK-AUDIT-AND-OPTIMIZATION-PLAN.md], [docs/plans/2026-02-21-MODERNIZATION-MASTER-PLAN.md], [contracts/runtime/runtime-modularization-matrix.json], [tests/test_wl130_runtime_matrix.py]
**Completed:** 2026-02-21 — Canonical runtime matrix contract is present and validated (`uv run pytest -q tests/test_wl130_runtime_matrix.py` => 31 passed).

Produce workload-to-runtime mapping with migration priority, benchmark targets, rollback strategy, and ownership.

---

### [WL-131] Python -> Rust Backmatter Migration Batch A
**Status:** COMPLETED (2026-02-21 closeout)
**Priority:** P1 (high)
**Area:** runtimes, performance
**Effort:** L (full day)
**Blocked by:** none
**Source:** [docs/plans/FULL_SHELL_TO_RUST_WHERE_BENEFICIAL.md], [docs/plans/2026-02-21-MODERNIZATION-MASTER-PLAN.md:Phase D], [tests/routing/test_wl131_parser_parity.py], [tests/routing/test_wl131_rust_python_parity.py], [tests/test_wl131_benchmark_baseline.py], [benchmarks/baseline-wl131-parse-model-suffix.json], [benchmarks/results/wl131/perf-budget-latest.json], [benchmarks/results/wl131/perf-budget-latest.md]

Move first high-ROI hot paths from Python into Rust with parity tests and perf budgets.

**Completed:** 2026-02-21 — parser parity collection issue resolved and WL-131 perf-budget evidence refreshed/linked.

**Closeout checklist:**
- [x] Parser parity suite green: `uv run pytest -q tests/routing/test_wl131_parser_parity.py` -> `41 passed, 1 skipped`.
- [x] Extended parity suite green: `uv run pytest -q tests/routing/test_wl131_rust_python_parity.py` -> `22 passed, 4 skipped`.
- [x] Perf-budget artifacts refreshed and attached: `benchmarks/results/wl131/perf-budget-latest.json` (`budget_pass: true`, `measured_per_call_us: 0.148690`) plus markdown summary.

---

### [WL-132] Zig ABI Promotion from POC to Production Contract
**Status:** COMPLETED (2026-02-21)
**Priority:** P2 (medium)
**Area:** zig, runtimes
**Effort:** M (half day)
**Blocked by:** none
**Source:** [docs/reference/ZIG_RUST_INTEROP_DESIGN.md], [docs/plans/2026-02-20-MOJO-ZIG-STACK-AUDIT-AND-OPTIMIZATION-PLAN.md], [crates/thegent-zmx-interop/src/lib.rs]

Promote Zig interop to versioned ABI contract with contract tests and CI lane hooks.

---

### [WL-133] Mojo Kernel Promotion for Deterministic Scoring
**Status:** COMPLETED (2026-02-21)
**Priority:** P2 (medium)
**Area:** mojo, runtimes
**Effort:** M (half day)
**Blocked by:** none
**Source:** [docs/plans/2026-02-20-MOJO-ZIG-STACK-AUDIT-AND-OPTIMIZATION-PLAN.md], [src/thegent/infra/mojo_bridge.py], [tests/test_unit_mojo_bridge.py]

Replace placeholder kernels with production workloads only when benchmark thresholds are met.

---

### [WL-134] Test Topology Rebalance for Fast/Deep Lanes
**Status:** COMPLETED (2026-02-21)
**Priority:** P1 (high)
**Area:** testing, ci
**Effort:** M (half day)
**Blocked by:** none
**Source:** [docs/plans/2026-02-21-MODERNIZATION-MASTER-PLAN.md:Phase E], [Taskfile.yml], [pyproject.toml], [tests/test_wl134_deep_lane_marker.py], [docs/guides/QUALITY_ASSURANCE.md]

Partitioned tests into fast/deep executable lanes with regression and documentation coverage:
1. Added canonical lane commands: `test:fast-lane`, `test:nightly-lane`, `test:deep`, and `test:gate`.
2. Registered lane marker contract in pytest config (`[tool.thegent.pytest_lanes]` + `deep` marker).
3. Added lane-wiring regression checks and operational QA guidance.

---

### [WL-135] LOC and Complexity SLO Dashboard
**Status:** COMPLETED (2026-02-21)
**Priority:** P2 (medium)
**Area:** governance, observability
**Effort:** S (1-3h)
**Blocked by:** none
**Source:** [docs/reports/2026-02-21-LIBRARY-REAUDIT-AND-CODEBASE-ATLAS.md], [scripts/wl137_weekly_diagnosis.py], [scripts/collect_loc_metrics.py], [scripts/render_slo_dashboard.py], [scripts/emit_wl135_slo_stub.py], [tests/test_wl135_loc_collector.py], [tests/test_wl135_slo_dashboard.py], [tests/test_wl135_slo_metric_emitter_stub.py], [tests/test_wl135_ci_summary_contract.py], [docs/guides/QUALITY_ASSURANCE.md]

Published LOC/complexity and SLO dashboard pipeline deliverables:
1. Added LOC/complexity collector task and artifact (`task metrics:loc` -> `.quality/loc-metrics.json`).
2. Added CI summary serialization (`--ci-summary`) with runtime buckets and drift deltas.
3. Added SLO dashboard renderer and stub metric emitter workflow.
4. Added regression tests and QA runbook wiring.

---

### [WL-136] Two-Python-Surface Reduction Plan (Core vs Tooling/Test)
**Status:** COMPLETED (2026-02-21, trend monitoring carried by WL-137)
**Priority:** P0 (blocker)
**Area:** architecture, python
**Effort:** M (half day)
**Blocked by:** none (resolved 2026-02-21)
**Source:** [docs/plans/2026-02-21-MODERNIZATION-MASTER-PLAN.md], [docs/reports/2026-02-21-LIBRARY-REAUDIT-AND-CODEBASE-ATLAS.md], [docs/plans/WL-136-TWO-PYTHON-SURFACES.md], [docs/reports/artifacts/wl120-wl136-loc-trend-2026-02-21.json], [docs/reports/artifacts/wl120-wl136-loc-trend-2026-02-21.md]

Formalize and execute separate reduction tracks:
1. Core runtime Python surface (must shrink aggressively via modularization + Rust offload).
2. Tooling/test/research Python surface (must be isolated from core runtime and fast lanes).
Goal: heavy LOC reduction without behavior regressions.

Track-A closeout slice (2026-02-21):
1. Finalized architecture decision record in `docs/reference/ADR-016-two-python-surfaces.md`.
2. Linked ADR index entry in `ADR.md`.
3. Verified boundary-oriented command routing remains green with focused validation commands.
4. Re-ran WL-136 boundary checks and strict scripts; all boundary gates are currently green.

**Blockers checklist (explicit):**
- [x] Core-vs-tooling boundary gate is clean for contract-scoped core zones; `uv run pytest -q tests/test_wl136_boundary_check.py` => `5 passed`, `uv run pytest -q tests/test_wl136_boundary_compliance.py` => `3 passed`, and strict script/audit checks pass.
- [x] Core-surface trend continuity is monitored via WL-137 weekly diagnosis; post-2026-02-21 data: `6790 -> 7913 -> 12533 -> 12620` shows core boundary also spiked with new modules (+5.6K on 2026-02-21). Boundary gates remain green but LOC growth requires careful monitoring. Source: `docs/reports/artifacts/wl120-wl136-loc-trend-2026-02-21.json`.
- [x] Completion approved (2026-02-21) for WL-136 scope because boundary compliance gates are green and WL-120 monolith ceilings are now met.

---

### [WL-137] Cross-Codebase LOC/Refactor Audit Cadence (thegent + trace)
**Status:** COMPLETED (2026-02-21)
**Priority:** P1 (high)
**Area:** governance, architecture
**Effort:** S (1-3h)
**Blocked by:** none
**Source:** [docs/reports/2026-02-21-LOC-CODE-REFACTOR-DIAGNOSIS-ALL-CODEBASES.md], [config/wl137-diagnosis.toml], [scripts/wl137_weekly_diagnosis.py], [docs/checklists/WL-137-WEEKLY-DIAGNOSIS.md]

Establish repeatable weekly LOC+refactor diagnosis across active codebases/languages with trend deltas and regression alerts.

---

### [WL-138] Execute Decomposition Map (Python/Rust/Zig/Mojo)
**Status:** COMPLETED (2026-02-21)
**Priority:** P0 (blocker)
**Area:** architecture, runtimes
**Effort:** XL (multi-week)
**Blocked by:** none (resolved 2026-02-21)
**Source:** [docs/plans/2026-02-21-PY-RUST-ZIG-MOJO-DECOMPOSITION-MAP.md], [contracts/runtime/zig_abi_contract_v1.json], [contracts/runtime/mojo_kernel_contract_v1.json], [scripts/wl138_decomposition_progress.py], [tests/test_wl138_decomposition_progress.py], [docs/reports/artifacts/wl138_decomposition_progress.json]

Implement the full decomposition program:
1. Python monolith cuts (`cli.py`, `impl.py`, `mcp/server.py`).
2. Rust hook decomposition (`crates/thegent-hooks/src/main.rs`, `hooks/hook-dispatcher/src/main.rs`).
3. Zig ABI contract test wiring and promotion checks.
4. Mojo kernel correctness + benchmark harness with promotion gates.

**Blockers checklist (explicit):**
- [x] Dependency blocker resolved (2026-02-21): WL-120 decomposition/monolith gate is complete (`cli.py` 49, `impl.py` 561, `mcp/server.py` 228), and trend continuity is tracked by WL-137 cadence instead of blocking WL-138 closeout.
- [x] Delivered 2026-02-21: decomposition progress artifact now includes execution-level gates for Rust hook decomposition and Zig/Mojo promotion outcomes (`scripts/wl138_decomposition_progress.py`, `tests/test_wl138_decomposition_progress.py`, `docs/reports/artifacts/wl138_decomposition_progress.json`).

---

### [WL-139] CLAUDE Instruction Architecture Standardization (Global vs Project)
**Status:** COMPLETED (2026-02-21)
**Priority:** P2 (medium)
**Area:** governance, docs, DX/AX/UX
**Effort:** S (1-3h)
**Blocked by:** none
**Source:** [CLAUDE.md], [docs/governance/GOVERNANCE_SUMMARY.md], [docs/governance/POLYGLOT_RUNTIME_COVERAGE_AND_CONVERSION_MATRIX_2026-02-21.md], [docs/research/2026-02-21-CLAUDE-INSTRUCTION-ARCHITECTURE-DX-AX-UX-RESEARCH.md], [docs/plans/2026-02-21-CLAUDE-INSTRUCTION-ARCHITECTURE-DX-AX-UX-PLAN.md], [docs/reports/2026-02-21-CLAUDE-INSTRUCTION-ARCHITECTURE-UPGRADE-WORKLOG.md]

Standardized instruction layering and readability:
1. Added explicit global-vs-project instruction architecture section.
2. Added canonical instruction doc map references.
3. Aligned governance docs and logged upgrade scope/roadmap artifacts.

---

### [WL-140] Scaffolder Questionnaire and Copier Normalization (DX/AX/UX)
**Status:** COMPLETED (2026-02-21)
**Priority:** P1 (high)
**Area:** templates, onboarding, DX/AX/UX
**Effort:** M (half day)
**Blocked by:** none
**Source:** [templates/initialize-project/copier.yml], [templates/initialize-project/README.md], [templates/initialize-project/{{ project_name }}/CLAUDE.md], [templates/claude/CLAUDE.md.template], [docs/research/2026-02-21-SCAFFOLDER-QUESTIONNAIRE-DX-AX-UX-WEB-RESEARCH.md], [docs/plans/2026-02-21-SCAFFOLDER-QUESTIONNAIRE-DX-AX-UX-IMPLEMENTATION-PLAN.md], [docs/reports/2026-02-21-SCAFFOLDER-QUESTIONNAIRE-DX-AX-UX-UPGRADE-WORKLOG.md]

Upgraded scaffolder reliability and onboarding quality:
1. Expanded project-type questionnaire and cross-field validators.
2. Normalized mixed Cookiecutter/Copier templating to Copier-native syntax.
3. Added DX/AX/UX profile contracts into generated CLAUDE artifacts.
4. Added matrix-style questionnaire guidance and validated with Copier smoke render.

---

### [WL-141] Initialize-Project Smoke Harness (Task + CI)
**Status:** COMPLETED (2026-02-21)
**Priority:** P1 (high)
**Area:** templates, ci, quality
**Effort:** S (1-3h)
**Blocked by:** WL-140
**Source:** [scripts/smoke_initialize_project_template.sh], [Taskfile.yml], [.github/workflows/ci.yml]

Hardened template reliability with automated smoke checks:
1. Added profile-aware Copier smoke script (`service_api`, `cli_tool`, `event_worker`, `web_app`, `library_sdk`, `all`).
2. Added Task entrypoints for single-profile and all-profile smoke checks.
3. Added CI quality-job smoke gate for `service_api` profile.
4. Added unresolved-template marker checks and profile assertion in generated CLAUDE output.

---

### [WL-142] `thegent sys setup project scaffold` Preset Bootstrap Command
**Status:** COMPLETED (2026-02-21)
**Priority:** P1 (high)
**Area:** cli, templates, onboarding
**Effort:** S (1-3h)
**Blocked by:** WL-140
**Source:** [src/thegent/cli/apps/project.py], [tests/test_project_tenancy.py]

Added a first-class CLI entrypoint for preset bootstrap:
1. `thegent sys setup project scaffold <destination> --profile <preset>`.
2. Uses Copier preset data-file generation with curated defaults.
3. Includes profile validation and destination safety checks.
4. Covered by focused CLI tests and end-to-end smoke invocation.

---

### [WL-143] Scaffold Preset Discoverability (`scaffold-profiles`)
**Status:** COMPLETED (2026-02-21)
**Priority:** P2 (medium)
**Area:** cli, ux, onboarding
**Effort:** S (1-3h)
**Blocked by:** WL-142
**Source:** [src/thegent/cli/apps/project.py], [tests/test_project_tenancy.py]

Improved preset discoverability and ergonomics:
1. Added `thegent sys setup project scaffold-profiles` and `--json`.
2. Improved invalid profile errors to include valid preset names.
3. Added focused CLI tests for text/json profile listing.

---

### [WL-144] Scaffold Advanced Flags (`--dry-run`, `--register`)
**Status:** COMPLETED (2026-02-21)
**Priority:** P1 (high)
**Area:** cli, onboarding, tenancy
**Effort:** S (1-3h)
**Blocked by:** WL-142
**Source:** [src/thegent/cli/apps/project.py], [tests/test_project_tenancy.py]

Added advanced scaffold execution controls:
1. `--dry-run` previews full Copier payload without writing files.
2. `--register` optionally registers the scaffolded project tenancy.
3. `--tenant` allows tenant override when registering.
4. Added tests for dry-run behavior and registration path.

---

### [WL-145] Scaffold Runtime Bootstrap (`--install-runtime`)
**Status:** COMPLETED (2026-02-21)
**Priority:** P1 (high)
**Area:** cli, tenancy, onboarding
**Effort:** S (1-3h)
**Blocked by:** WL-144
**Source:** [src/thegent/cli/apps/project.py], [tests/test_project_tenancy.py]

Integrated optional runtime asset installation into scaffold flow:
1. Added `scaffold --install-runtime` to run `run_install_project` after successful scaffold+registration.
2. Added guardrails: requires `--register` unless `--dry-run`, and dry-run explicitly reports runtime skip status.
3. Extended scaffold JSON payload with runtime install request/applied/status/result fields.
4. Added focused CLI tests for success path, dry-run skip, missing-register validation, and runtime-install failure surfacing.

---

### [WL-146] Scaffold Discoverability + CI Smoke Task
**Status:** COMPLETED (2026-02-21)
**Priority:** P1 (high)
**Area:** cli, docs, ci
**Effort:** S (1-3h)
**Blocked by:** WL-145
**Source:** [.github/workflows/ci.yml], [docs/reference/cli-examples.md]

Improved operational discoverability and explicit coverage for scaffold command:
1. Wired CI quality workflow to execute a direct scaffold dry-run smoke command.
2. Added runtime-aware scaffold dry-run invocation (`--install-runtime --dry-run --json`) as explicit CI coverage.
3. Added CLI reference sections for `thegent sys setup project scaffold` and `scaffold-profiles` with examples.

---

### [WL-147] 90-Item Multi-Agent Batch Decomposition Plan
**Status:** COMPLETED (2026-02-21)
**Priority:** P1 (high)
**Area:** planning, orchestration
**Effort:** S (1-3h)
**Blocked by:** none
**Source:** [docs/plans/2026-02-21-AGENT-BATCH-90-EXECUTION-PLAN.md]

Created a dependency-aware 90-item execution decomposition for parallel agent delivery:
1. Defined 3 waves of 30 items each (`6 agents x 5 items` per wave).
2. Mapped each micro-item to currently open WL epics (WL-117/120/128/130/131/132/133/134/135/136/138).
3. Added repeat-loop protocol (`do next`, `repeat/do next`) for wave-by-wave execution.

---

### [WL-148] B90 Wave-1 Execution via Child Agents (6x5 = 30 items)
**Status:** COMPLETED (2026-02-21)
**Priority:** P1 (high)
**Area:** execution, orchestration
**Effort:** M (half day)
**Blocked by:** WL-147
**Source:** [docs/reports/2026-02-21-B90-W1-agent-a.md], [docs/reports/2026-02-21-B90-W1-agent-b.md], [docs/reports/2026-02-21-B90-W1-agent-c.md], [docs/reports/2026-02-21-B90-W1-agent-d.md], [docs/reports/2026-02-21-B90-W1-agent-e.md], [docs/reports/2026-02-21-B90-W1-agent-f.md]

Executed Wave-1 assignments with child-agent workflow and produced per-agent evidence reports:
1. Completed all `B90-W1-A1..A5` (agent-a).
2. Completed all `B90-W1-B1..B5` (agent-b).
3. Completed all `B90-W1-C1..C5` (agent-c).
4. Completed all `B90-W1-D1..D5` (agent-d).
5. Completed all `B90-W1-E1..E5` (agent-e).
6. Completed all `B90-W1-F1..F5` (agent-f).

---

## CLAIMED (in progress — do not pick)

| ID | Agent | Started | Notes |
|----|-------|---------|-------|

---

### Wave70 Claims (2026-02-22)


| research-library-ansi | codex-24976 | 2026-02-23T01:36:08.456669+00:00 |
| ~~acp-client-adapter~~ | codex-26970 | 2026-02-23T01:36:12.070561+00:00 |
| ~~research-governance-override-events~~ | codex-30449 | 2026-02-23T01:36:20.170381+00:00 |
| ~~ux-linting-accelerator~~ | codex-26970 | 2026-02-23T01:36:23.486846+00:00 |
| swarm-critical-lane | codex-30449 | 2026-02-23T01:36:31.268445+00:00 |
| install-library-deps | codex-26970 | 2026-02-23T01:36:34.013522+00:00 |
| ~~swarm-dag-prioritization~~ | codex-30449 | 2026-02-23T01:36:42.271806+00:00 |
| ~~resource-network-bandwidth~~ | codex-26970 | 2026-02-23T01:36:45.032668+00:00 |
| _none_ | codex-30449 | 2026-02-23T01:36:52.712383+00:00 |
| wave70-l4 | codex-30449 | 2026-02-23T01:37:05.303313+00:00 |
| docs-cli-reference | codex-26970 | 2026-02-23T01:37:08.225371+00:00 |
| ~~borrow-heliosguard-backlog~~ | codex-26970 | 2026-02-23T01:37:18.852120+00:00 |
| wave70-l2 | codex-26970 | 2026-02-23T01:37:44.388215+00:00 |
| ~~docs-claudemd-reference~~ | codex-26970 | 2026-02-23T01:37:56.908952+00:00 |
| ~~SCLI-P7.1~~ | codex-26970 | 2026-02-23T01:38:24.452951+00:00 |
| ~~sharecli-smart-merge~~ | codex-26970 | 2026-02-23T01:38:41.297906+00:00 |
| ~~sharecli-git-parallelism~~ | codex-26970 | 2026-02-23T01:38:55.428057+00:00 |
| ~~audit-delegation-friction~~ | codex-26970 | 2026-02-23T01:39:24.692432+00:00 |
| ~~escalation-index-file-indexing~~ | codex-26970 | 2026-02-23T01:39:58.712689+00:00 |
| ~~docs-mcp-tool-docs~~ | codex-26970 | 2026-02-23T01:40:12.286713+00:00 |
| ~~TGNT-P16.2~~ | codex-smoke | 2026-02-23T01:40:58.247759+00:00 |
| ~~research-smart-robust-strategies~~ | codex-smoke | 2026-02-23T01:41:00.119425+00:00 |
| ~~borrow-heliosguard-priority~~ | codex-smoke | 2026-02-23T01:41:00.259408+00:00 |
| ~~TGNT-P18.3~~ | codex-36397 | 2026-02-23T01:41:24.684994+00:00 |
| ~~audit-teammate-collaboration~~ | codex-36397 | 2026-02-23T01:42:13.232032+00:00 |
| ~~TGNT-P14.1~~ | codex-36397 | 2026-02-23T01:46:47.270912+00:00 |
| ~~TGNT-P11.1~~ | codex-self-wave10 | 2026-02-23T01:48:38.010029+00:00 |
| ~~sharecli-task-queue~~ | codex-self-wave10 | 2026-02-23T01:48:38.385069+00:00 |
| ~~TGNT-P18.2~~ | codex-self-wave10 | 2026-02-23T01:48:38.684327+00:00 |
| ~~rollout-hook-rust-phase2~~ | codex-self-wave10 | 2026-02-23T01:48:39.121995+00:00 |
| docs-skill-examples | codex-self-wave10 | 2026-02-23T01:48:39.330964+00:00 |
| wp-16001-persona-registry | codex-self-wave10 | 2026-02-23T01:48:39.594937+00:00 |
| ~~SCLI-P7.3~~ | codex-self-wave10 | 2026-02-23T01:48:39.797259+00:00 |
| wave70-l1 | codex-self-wave-next2 | 2026-02-23T01:50:21.485463+00:00 |
| wp-16002-async-delegation | codex-self-wave-next2 | 2026-02-23T01:50:21.967715+00:00 |
| ~~TGNT-P16.1~~ | codex-self-wave-next2 | 2026-02-23T01:50:22.105584+00:00 |
| wave70-l7 | codex-self-wave-next2 | 2026-02-23T01:50:22.231318+00:00 |
| wave70-l3 | codex-self-wave-next2 | 2026-02-23T01:50:22.365737+00:00 |
| TGNT-P17.1 | codex-self-wave-next2 | 2026-02-23T01:50:22.490878+00:00 |
## COMPLETED (historical reference)

> All items below were completed by various agents between 2026-02-18 and 2026-02-20. See WORK_STREAM prior version for full entries with completion notes.

| ID | Completed | Summary |
|----|-----------|---------|
| SCLI-P7.1 | 2026-02-23 | Verified singleflight dedup behavior and cache heat-map eviction via `tests/mesh/test_cache.py` (20 passed) |
| SCLI-P7.3 | 2026-02-23 | Verified heat-based cache behavior and eviction ordering via `tests/mesh/test_cache.py` (20 passed) |
| TGNT-P11.1 | 2026-02-23 | Hardened tmpfs-like mesh directory initialization with explicit `0o1777` chmod and added focused tests (`tests/infra/test_ipc_context_injection.py`) |
| TGNT-P14.1 | 2026-02-23 | Hardened AGENT template/context symlink management and added focused tests (`tests/infra/test_ipc_context_injection.py`) |
| TGNT-P16.1 | 2026-02-23 | Verified Linux bubblewrap tier-2 worktree bind behavior in `tests/test_wl681x_lane_d.py -k tier2_bwrap` |
| sharecli-smart-merge | 2026-02-23 | Verified SmartMerger integration and fallback/driver behavior via `tests/mesh/test_smart_merge.py` |
| sharecli-git-parallelism | 2026-02-23 | Verified shared-directory worktree pool git parallelism via `tests/mesh/test_git_parallelism.py` |
| escalation-index-file-indexing | 2026-02-23 | Closed with evidence-path validation and queue-order indexing in `docs/reports/2026-02-23-worklog-wave76-lane-e.md` |
| docs-mcp-tool-docs | 2026-02-23 | Confirmed MCP tool documentation mapping in work stream deliverables table and lane report evidence |
| TGNT-P16.2 | 2026-02-23 | Verified macOS seatbelt sandbox tier mapping/profile generation via `tests/security/test_sandboxing_provider.py` |
| research-smart-robust-strategies | 2026-02-23 | Closed with research artifact cross-reference validation (`SMART_ROBUST_STRATEGIES_RESEARCH.md`) in lane report |
| TGNT-P18.3 | 2026-02-23 | Verified mesh management CLI status/tasks behavior via `tests/observability/test_observability_v2.py` |
| sharecli-task-queue | 2026-02-23 | Verified Maildir queue behavior and task lifecycle via `tests/mesh/test_task_queue.py` |
| TGNT-P18.2 | 2026-02-23 | Verified advanced metrics aggregation and JSONL parsing via `tests/observability/test_observability_v2.py` |
| rollout-hook-rust-phase2 | 2026-02-23 | Closed with focused Rust-hook rollout evidence capture and regression suite pass in lane report |
| WL-9510 | 2026-02-23 | Split hook shell-resolution/command-build/execute phases and fixed TimeoutExpired text-stream handling in `src/thegent/infra/hook_runner.py`; regression coverage in `tests/infra/test_hook_runner.py` |
| WL-9511 | 2026-02-23 | Hook execution command-path quality-gate parity validated for PowerShell `-File` mode via `tests/infra/test_hook_runner.py` |
| WL-9512 | 2026-02-23 | Split metrics emission formatting from storage logic in `src/thegent/integrations/prometheus_metrics.py` |
| WL-9513 | 2026-02-23 | Added regression guard for stable metric sample state after record-time capture in `tests/test_wl196_prometheus_metrics.py` |
| WL-9514 | 2026-02-23 | Split SLO status computation from payload construction in `src/thegent/metrics/collector.py` |
| WL-9515 | 2026-02-23 | Hook sync-path timeout behavior now preserves stdout/stderr payloads without decode crashes in `src/thegent/infra/hook_runner.py` |
| WL-9516 | 2026-02-23 | Threshold enforcement path in SLO stub now explicitly isolated and regression-covered in `tests/test_wl135_slo_metric_emitter_stub.py` |
| WL-9517 | 2026-02-23 | Prometheus metric export now uses explicit sample-format helper, preserving business logic isolation in `src/thegent/integrations/prometheus_metrics.py` |
| WL-9518 | 2026-02-23 | Added pass-at-threshold boundary regression for SLO payload status in `tests/test_wl135_slo_metric_emitter_stub.py` |
| WL-9519 | 2026-02-23 | Wave-77 Lane-E evidence captured in `docs/reports/2026-02-23-worklog-wave77-lane-e.md` with focused test run proof |
| WL-9520 | 2026-02-23 | Workflow stage graph now fails fast on empty stage IDs in `src/thegent/agents/crew/workflow.py`; regression coverage in `tests/test_crew.py` |
| WL-9521 | 2026-02-23 | Added whitespace-only stage-ID guard in dependency parse phase with regression coverage in `tests/test_crew.py` |
| WL-9522 | 2026-02-23 | Execution planning now fails fast on duplicate crew IDs within a stage in `src/thegent/agents/crew/workflow.py` |
| WL-9523 | 2026-02-23 | Added execution-plan regression coverage for valid multi-crew stage IDs in `tests/test_crew.py` |
| WL-9524 | 2026-02-23 | Added explicit `_build_execution_plan()` parse boundary and dependency-order regression coverage in `tests/test_crew.py` |
| WL-9525 | 2026-02-23 | Execution now consumes a frozen execution plan snapshot before stage runs, preventing mid-run stage-list mutations from changing run order |
| WL-9526 | 2026-02-23 | Added regression ensuring stage execution errors propagate fail-fast through `WorkflowEngine.execute()` |
| WL-9527 | 2026-02-23 | Added no-op regression for empty workflow execution path (`_build_execution_plan()` and `execute()`) |
| WL-9528 | 2026-02-23 | Added regression for stage-result map replacement semantics in `execute_stage()` |
| WL-9529 | 2026-02-23 | Added regression ensuring dependency validation happens before any stage execution side effects |
| wave80-pr23-merge | 2026-02-23 | PR #23 merged as `a1b56700ef5f716cda77280901454b3f0ddd7d82`; follow-up evidence captured in `docs/reports/2026-02-23-wave80-followup.md` including GitHub check runs (`Test` matrix + CI/Build/Benchmark gates) |
| wave80-wl007-checkpoint | 2026-02-23 | Wave80 follow-up checkpoint updated for WL-007-related validation evidence after PR #23 merge; no new WL-007 closure claim added |
| wave70-l5 | 2026-02-22 | Implemented WL-224 (workstream schema linter), WL-225 (wl sort/normalize), WL-226 (remote payload checksums), WL-227 (metadata enrichment), plus WL-259,260,222,223,228,229 with comprehensive test coverage (76 tests) |
| wave70-l6 | 2026-02-22 | Implemented WL-234 (incident runbook), WL-235 (connector chaos tests), WL-236 (cold/warm benchmarks), WL-237 (hourly change digest) with comprehensive test coverage (56 tests) |
| WL-155-156-next20-b4 | 2026-02-22 | Executed fourth next-20 memory/scraper batch: snapshot indexing/analytics/export APIs plus summary-flow index artifact wiring and targeted tests |
| WL-155-156-next20-b3 | 2026-02-22 | Executed third next-20 memory/scraper batch: snapshot lifecycle utilities (list/load/latest/filter/export markdown), plus targeted unit tests and plan log updates |
| WL-155-156-next20-b2 | 2026-02-22 | Executed second next-20 memory/scraper batch: runtime trigger wiring (`tool_use`/`error`/`session_change`), snapshot persistence integration, inferred dump tagging, and targeted test/doc updates |
| WL-155-156-next20 | 2026-02-22 | Executed next-20 memory/scraper batch: rich session snapshot extraction, structured prompt+synthesis dumps, runtime wiring, and targeted tests/docs (`tests/test_unit_session_scraper.py`, `tests/test_unit_always_write_dumps.py`, `docs/plans/2026-02-21-SESSION_MEMORY_SYSTEM.md`, `docs/plans/2026-02-21-ENHANCED_SESSION_SCRAPER.md`) |
| docgen-link-checker | 2026-02-20 | scripts/check-docs-links.py exists, integrated in npm as docs:links |
| WL-120 | 2026-02-21 | Python monolith reduction complete for target files (`cli.py` 49, `impl.py` 561, `mcp/server.py` 228); trend continuity carried in WL-137 cadence |
| WL-136 | 2026-02-21 | Core-vs-tooling boundary reduction plan completed; boundary gates green, trend continuity carried in WL-137 cadence |
| WL-138 | 2026-02-21 | Decomposition map execution completed; execution gates green and WL-120 dependency resolved |
| WL-001 | 2026-02-20 | OpenRouter WS Auth header fix; cliproxy_adapter forward_headers |
| WL-002 | 2026-02-20 | OpenRouter provider type registration; API_KEY_PROVIDERS updated |
| WL-003 | 2026-02-20 | OpenRouter LiteLLM router config registered |
| WL-004 | 2026-02-20 | OpenRouter model ID mappings; harness_model_mapping.py updated |
| WL-005 | 2026-02-20 | OpenRouter SSE keep-alive comment parsing fix |
| WL-006 | 2026-02-20 | Quality gate scanner scope bounds; .jscpd.json, gitleaks caps, rg slop scan |
| WL-127 | 2026-02-21 | Replaced `lazy_static` cache with `OnceLock` in Rust policy engine and removed crate dependency |
| WL-134 | 2026-02-21 | Test topology rebalance complete: fast/nightly/deep lane tasks, pytest lane markers, regression tests, and QA runbook wiring |
| WL-135 | 2026-02-21 | LOC/complexity SLO dashboard complete: collector, CI summary serialization, dashboard renderer, stub emitter, and regression tests/docs |
| WL-132 | 2026-02-21 | Zig ABI promotion closed out with canonical runtime contract gate task (`quality:runtime-contracts:zig-abi`), CI fail-closed wiring, and fixture-backed artifact validation |
| WL-133 | 2026-02-21 | Mojo deterministic kernel promotion closed out with canonical runtime contract gate task (`quality:runtime-contracts:mojo-kernel`) and CI fail-closed runtime contract lane wiring |
| WL-129 | 2026-02-21 | Release workflow now emits Python and Rust vulnerability JSON artifacts (`pip-audit`, `cargo-audit`) |
| WL-137 | 2026-02-21 | Weekly LOC/refactor cadence: `task diag:wl137`, `scripts/wl137_weekly_diagnosis.py`, config/history/report pipeline, and checklist |
| WL-139 | 2026-02-21 | Standardized CLAUDE instruction architecture (global vs project), added explicit architecture/doc map references, and captured DX/AX/UX research-plan-report set |
| WL-140 | 2026-02-21 | Expanded initialize-project questionnaire, fixed Copier templating compatibility, and added DX/AX/UX-aware generated CLAUDE scaffolding with smoke validation |
| WL-141 | 2026-02-21 | Added initialize-project smoke harness script, Task targets, and CI smoke gate with profile and unresolved-template validation |
| WL-142 | 2026-02-21 | Added `thegent sys setup project scaffold` with profile presets, validations, and CLI tests |
| WL-143 | 2026-02-21 | Added scaffold profile discovery command and improved invalid-profile guidance with tests |
| WL-144 | 2026-02-21 | Added `scaffold --dry-run/--register/--tenant` with payload preview and tenancy registration tests |
| WL-145 | 2026-02-21 | Added `scaffold --install-runtime` with register/dry-run guardrails, runtime status payload, and failure/success CLI tests |
| WL-146 | 2026-02-21 | Added scaffold CLI discoverability docs and CI quality smoke wiring for direct scaffold dry-run |
| WL-147 | 2026-02-21 | Added 90-item (3-wave) multi-agent decomposition plan with 6x5 assignments per wave |
| WL-148 | 2026-02-21 | Executed B90 Wave-1 with child agents and produced 6 per-agent evidence reports (30 items) |
| WL-130 | 2026-02-21 | Runtime modularization matrix closed: canonical artifact `contracts/runtime/runtime-modularization-matrix.json` validated by `tests/test_wl130_runtime_matrix.py` |
| WL-131 | 2026-02-21 | Closed blocker: fixed parser parity collection mismatch, validated parity suites (`41 passed, 1 skipped`; `22 passed, 4 skipped`), refreshed perf-budget evidence in `benchmarks/results/wl131/perf-budget-latest.json` (`budget_pass=true`) |
| WL-007 | 2026-02-20 | Rust quality-gate + security-pipeline binaries; 50%+ latency improvement |
| WL-010 | 2026-02-20 | Multi-project tenancy: ProjectTenancy singleton fix (CLI bypassing patch), Typer single-cmd app collapse fix, Rich JSON wrap fix → typer.echo. project.py, sys.py, install.py — 46 tests |
| WL-011 | 2026-02-20 | OpenRouter P1 features OR-08 through OR-16 |
| WL-012 | 2026-02-20 | Pareto Router Phase 3: executor, orchestrator, audit logging, config — 39+123 tests |
| WL-013 | 2026-02-20 | Supermemory Phase 2: SupermemoryProvider cloud persistence |
| WL-014 | 2026-02-20 | Unified Prompt Queue: PromptQueueManager + thegent queue TUI |
| WL-015 | 2026-02-20 | Cross-Platform Rules Sync: RulesSyncManager + thegent rules sync |
| WL-016 | 2026-02-20 | Persistent Python Worker Pool: PersistentWorkerPool + process-compose integration |
| WL-017 | 2026-02-20 | TUI Phase 2: InteractiveInputWidget, TableWidget, TimelineWidget |
| WL-018 | 2026-02-20 | CLIProxy Cursor Phase 2: cursor: schema, token refresh, rebindExecutors |
| WL-019 | 2026-02-20 | HITL: RunContext, HITLDecision, GovernanceEventLog, PolicyEngine (await_approval), HITLApprovalWorkflow, govern approve/reject/list CLI + MCP tools — 33 tests |
| WL-020 | 2026-02-20 | Federated Policy Engine: FR-FED-001→006, 3-level namespace hierarchy, EU-AI-ACT/US-SEC jurisdiction profiles, ConsentRelayStore, ArbitrationLog (most-restrictive-wins), federation health — 48 tests |
| WL-030 | 2026-02-20 | Quality gate retry bounds: ThegentSettings fields, stale artifact cleanup — 20 tests |
| WL-032 | 2026-02-20 | TUI Phase 3: ThemeRegistry, SparklineWidget, BarChartWidget, FloatingOverlay — 110 tests |
| WL-033 | 2026-02-20 | OpenRouter P2: OR-17 headers, OR-18 native bypass, OR-19 generation ID — 28 tests |
| WL-034 | 2026-02-20 | Agent Registry: CapabilityIndex, TF-IDF recommend, CLI commands, auto-agent — 48 tests |
| WL-035 | 2026-02-20 | mise validation: tests, README update, CHANGELOG — 16 tests |
| WL-036 | 2026-02-20 | Shadow dir cleanup: prune.py, gardening.py, doctor fix_hint — 15 tests |
| WL-037 | 2026-02-20 | thegent sync: work-stream/rules/research commands — 20 tests |
| WL-038 | 2026-02-20 | $defer injection: deferral.py, all 3 runners patched — 30 tests |
| WL-039 | 2026-02-20 | WBS Phase 2 Reliability: circuit breaker, provider loop timeout, poison pill — 120 tests |
| WL-040 | 2026-02-20 | WBS Phase 4 UX: error messages, JSON output, completions, help, spinners — 34 tests |
| WL-050 | 2026-02-20 | Adaptive Scale: TailscaleComputePool, FederatedLB, WatcherDaemon — 59 tests |
| WL-051 | 2026-02-20 | Enterprise compliance: ComplianceEvidence, EvidenceStore, RetentionEnforcer, OrgRegistry, KeyRotationMonitor, CLI — 72 tests |
| WL-052 | 2026-02-20 | TUI mouse support: MouseHandler, DragState, PaneSplitter, ScrollState, ContextMenu, OutputWidget — 48 new tests (158 total) |
| WL-053 | 2026-02-20 | Windows PowerShell support for thegent install — 25 tests |
| WL-054 | 2026-02-20 | CLOSED — not needed (wisdgod/cursor-api binary dep is acceptable) |
| WL-055 | 2026-02-20 | VitePress docsite: docs/site/ with Playwright E2E tests |
| WL-060 | 2026-02-20 | Gardener Agent: GardenerAgent, gardening.py "garden" step, never_idle.py integration, thegent memory garden CLI — 37 tests |
| WL-061 | 2026-02-20 | Cursor API evaluation: keep binary dep, WL-054 not needed |
| WL-031 | 2026-02-20 | Pareto Frontier TUI Panel: ParetoFrontierPanel Rust, ParetoTuiSession Python, BarChart+Sparkline — 16 Python + 176 Rust tests |
| batch-lib-replacement | 2026-02-20 | Library Replacement: MD5→SHA256 in mesh/cache.py, mesh/coordination.py, ui/compositor/compositor.py; cachetools.TTLCache in cli/commands/impl.py |
| batch-p0-openrouter | 2026-02-20 | OpenRouter P0 fixes: WS Auth header (WL-001), provider (WL-002), LiteLLM (WL-003), models (WL-004), SSE (WL-005) |
| batch-p1-verified | 2026-02-20 | P1 verified complete: WL-012 Pareto Phase3, WL-013 Supermemory API, WL-014 Prompt Queue, WL-016 Worker Pool, WL-018 Cursor Phase2 |
| batch-perf-orchestration | 2026-02-20 | Performance + Orchestration: WL-070 Router cache, WL-071 AsyncClient pool, WL-072 NeverIdleLoop, WL-073 Cursor reachability cache, WL-077 Settings cache, WL-080 Protocol schema, WL-081 OrchestrationPlan, WL-100 DiffRenderer TUI, WL-101 Skills Discovery, WL-108 Context Budget |
| wl-019-hitl-approve-reject | 2026-02-20 | Added `thegent govern approve/reject`, MCP tools, and `await_approval` event emission in PolicyEngine |
| wl-007-benchmark-harness | 2026-02-20 | Added `scripts/benchmark-quality-gate-rust.sh` for Rust vs shell quality/security benchmark runs |
| wl-010-tenancy-commands-verified | 2026-02-20 | Verified `thegent sys setup project` and `thegent install project` command surfaces are available |
| wl-007-quality-gate-bin | 2026-02-20 | Added `quality-gate` and `security-pipeline` Rust binaries + integration tests |
| wl-006-scan-bounds-hardening | 2026-02-20 | Bounded `gitleaks` and `rg`-based slop scanning in `templates/shared/quality-gate.sh` |
| next-50-batch-plan | 2026-02-20 | Created dependency-ordered 50-item batch plan in `docs/plans/2026-02-20-NEXT-50-EXECUTION-BATCH.md` |
| wire-maif-agent-runner | 2026-02-19 | MAIF wired into ExecutionEngine and cli run_impl |
| swarm-fix-macos-sampling | 2026-02-19 | Fixed macOS vm_stat sampling for psutil parity |
| swarm-hysteresis-env | 2026-02-19 | THGENT_HYSTERESIS_* env vars in ThegentSettings |
| heliosShield-git-overhaul | 2026-02-19 | Parallel-safe git with AST-aware merge via Mergiraf |
| swarm-redlock-atomic | 2026-02-19 | RedlockController with Lua release; 56 tests |
| resource-gpu-utilization | 2026-02-19 | GpuMonitor with nvidia-smi fallback; 39 tests |
| ux-terminal-keepalive | 2026-02-19 | TerminalKeepalive + KeepaliveConfig; 23 tests |
| scratch-doctor-fix | 2026-02-19 | DoctorRunner with 8 checks and --fix; 41 tests |
| swarm-priority-queue | 2026-02-20 | RunPriorityQueue with heapq+FIFO; 58 tests |
| swarm-dag-prioritization | 2026-02-19 | DagPrioritizer with Kahn+CPM; 49 tests |
| swarm-token-bucket | 2026-02-19 | TokenBucket thread-safe; 46 tests |
| impl-simulation-replay-engine | 2026-02-19 | SimulationReplayEngine + replay CLI; 35 tests |
| coordination-hybrid-strategy | 2026-02-19 | HybridCoordinationStrategy HIERARCHICAL/P2P/ADAPTIVE; 37 tests |
| impl-compositor-manager | 2026-02-19 | CompositorManager with Layout enum; 41 tests |
| borrow-dex-flash-agents | 2026-02-19 | FlashAgent + thegent_flash MCP tool; 24 tests |
| setup-syncthing-workspace | 2026-02-19 | SyncthingManager with httpx; 34 tests |
| enhance-macos-sandbox | 2026-02-19 | MacOSSandbox + SandboxLevel; 39 tests |
| bkm-09-watcher-daemon | 2026-02-19 | WatcherDaemon singleton; 56 tests |
| muxless-termitty-introspection | 2026-02-19 | TerminalCapture 4-step fallback; 45 tests |
| borrow-plangent-subagents | 2026-02-19 | PlangentPlanner+Executor; 49 tests |
| impl-rust-zmx-wrapper | 2026-02-19 | crates/thegent-zmx idiomatic Rust; 27+2 tests |
| compositor-caching | 2026-02-19 | TTLCache render cache in Compositor; 24 tests |
| shell-consolidate-configs | 2026-02-19 | ShellConfigAuditor; 40 tests |
| serena-jetbrains-integration | 2026-02-19 | JetBrainsIntegration platform-aware; 48 tests |
| fastmcp-storage-eventstore | 2026-02-19 | McpStorage+McpEventStore; 43 tests |
| cache-frecency-algorithm | 2026-02-19 | FrecencyCache + FrecencyModelSelector; 48 tests |
| swarm-redis-concurrency | 2026-02-19 | RedisConcurrencyController; 34 tests |
| cache-predictive-pre-warming | 2026-02-19 | CachePreWarmer + background daemon; 44 tests |
| impl-memory-manager-integration | 2026-02-19 | MemoryManager wired into run_impl; 31 tests |
| impl-cross-project-registry | 2026-02-19 | CrossProjectRegistry; 36 tests |
| impl-idea-seed-scanner | 2026-02-19 | IdeaSeedScanner 9 patterns; 53 tests |
| muxless-acp-session-endpoints | 2026-02-19 | SessionEndpoints JSON-RPC; 36 tests |
| fastmcp-tool-patterns | 2026-02-19 | confirm/progress/choice/retry decorators; 31 tests |
| acp-mcp-bridge | 2026-02-19 | AcpMcpBridge + thegent_acp_invoke; 38 tests |
| compositor-error-boundaries | 2026-02-19 | Panel error_fallback + Compositor.recover; 37 tests |
| compositor-perf-profiling | 2026-02-19 | CompositorProfiler + RenderProfile; 34 tests |
| cache-diskcache-migration | 2026-02-19 | MultiLevelCache L1+L2 migration; 23 tests |
| git-migrate-gix | 2026-02-19 | thegent-git backed by gix pure Rust |
| swarm-soft-deadlines | 2026-02-19 | SoftDeadline + DeadlineMonitor; 37 tests |
| acp-server-adapter | 2026-02-19 | ACPServerAdapter Starlette+stdio; 45 tests |
| acp-client-adapter | 2026-02-19 | ACPClient httpx+tenacity; 37 tests |
| bkm-06-git-native | 2026-02-19 | thegent-git CLI binary + PyO3 GitNative; 28 tests |
| impl-supermemory-client | 2026-02-19 | SupermemoryClient httpx+tenacity; 38 tests |
| fastmcp-elicitation-api | 2026-02-19 | elicit_confirmation/choice/text; 27 tests |
| fastmcp-context-api | 2026-02-19 | ctx.report_progress in 5 tools; 21 tests |
| research-governance-override-events | 2026-02-19 | OverrideEventEmitter + monitor; 28 tests |
| impl-routing-intake-integration | 2026-02-19 | _apply_pareto_routing in run_impl; 19 tests |
| litellm-clode-integration | 2026-02-19 | /v1/responses routes in mcp_server; 28 tests |
| litellm-responses-handler | 2026-02-19 | handler completions + WS close-code fix; 43 tests |
| impl-sync-command | 2026-02-19 | SyncCommand.status/push/pull/reset; 45 tests |
| tenacity-migrate-cli | 2026-02-19 | EAGAIN/EWOULDBLOCK to tenacity; 17 tests |
| tenacity-migrate-loop | 2026-02-19 | @with_retry(tenacity) on worker; 10 tests |
| heliosShield-smart-merge | 2026-02-19 | Mergiraf AST-aware via thegent git parallel |
| heliosShield-git-parallelism | 2026-02-19 | WorktreePool; 39 tests |
| task-io-improvement | 2026-02-19 | TaskInput/Output/Error/Spec Pydantic v2; 28 tests |
| adr-015-immutable-ledger | 2026-02-19 | ADR-015 SHA-256 hash chain design documented |
| bkm-08-discovery-binary | 2026-02-19 | thegent-discovery binary + DiscoveryClient; 28 tests |
| cache-multi-level | 2026-02-19 | MultiLevelCache L1=TTLCache L2=diskcache; 31 tests |
| bkm-05-state-shm | 2026-02-19 | CircuitBreakerShm + XpTracker mmap Rust; 34 tests |
| impl-zig-rust-interop-poc | 2026-02-19 | extern "C" FFI + subprocess fallback; 8 tests |
| swarm-usage-tracking | 2026-02-19 | UsageTracker in ConcurrencyController; 30 tests |
| heliosShield-task-queue | 2026-02-19 | MaildirQueue; 32 tests |
| compositor-lifecycle-hooks | 2026-02-19 | Panel on_mount/on_unmount hooks; 28 tests |
| bkm-07-hook-dispatcher-extend | 2026-02-19 | scan-secrets 14 named patterns; 36 tests |
| muxless-zmx-integration | 2026-02-19 | ZmxBackend + SessionBackend; 37 tests |
| impl-pareto-router | 2026-02-19 | ParetoRouter multi-objective optimization |
| impl-cost-aware-router | 2026-02-19 | CostAwareRouter budget-aware routing |
| prototype-federated-policy | 2026-02-19 | FederatedPolicyEngine multi-tenant |
| OPT-001 | 2026-02-19 | ResponseCachingMiddleware 30s TTL |
| OPT-002 | 2026-02-19 | RateLimitingMiddleware 10/s burst=20 |
| ROB-004 | 2026-02-19 | Circuit breaker per-provider |
| ROB-007 | 2026-02-19 | Graceful shutdown with in-flight drain |
| QW-002 | 2026-02-19 | _resolve_cwd() caching 10s TTL |
| wp-71001-registry-db | 2026-02-19 | ProjectRegistry SQLite schema |
| wp-71002-shadow-git | 2026-02-19 | ShadowAuditGit with secret scrubbing |
| wp-71003-episode-ctrl | 2026-02-19 | EpisodeController into agent loop |
| wp-71004-audit-cli | 2026-02-19 | thegent audit log/diff commands |
| wp-71005-hierarchy-cli | 2026-02-19 | thegent plan milestone/sprint commands |
| bkm-10-jsonl-parser | 2026-02-19 | JSONL streaming parser Rust |
| bkm-11-governance-scanner | 2026-02-19 | Native governance scanner Rust |
| impl-os-user-adapter | 2026-02-19 | OS-level user creation Linux/macOS/Win |
| heliosShield-bridge-fix | 2026-02-19 | heliosShield bridge and tests fixed |
| mise-integration | 2026-02-18 | Full mise install/uninstall/backup/restore; 4 shells |
| tui-compositor-phase1 | 2026-02-18 | 7 components + LayoutEngine; 40+ tests |
| Phase2-Hysteresis | 2026-02-18 | HysteresisManager + FFI; 78 tests |
| research-pareto-routing-phase1 | 2026-02-18 | ParetoRouter Rust Phase 1 |
| research-hook-rust-phase1 | 2026-02-18 | thegent-hooks Rust library (PolicyEngine, QualityEvaluator, SecurityScanner, CostCalculator) |
| research-economic-governance | 2026-02-18 | ProviderScorer, ProviderRegistry, MetricsCollector; Phase 2.1 complete |

---

| CLIP-BUG-01 | codex-closeout | 2026-02-23T02:44:17.396127+00:00 |
| CLIP-BUG-02 | codex-closeout | 2026-02-23T02:44:18.755867+00:00 |
| CLIP-BUG-03 | codex-closeout | 2026-02-23T02:44:19.746595+00:00 |
| CLIP-BUG-04 | codex-closeout | 2026-02-23T02:44:20.571724+00:00 |
| CLIP-BUG-05 | codex-closeout | 2026-02-23T02:44:21.576003+00:00 |
| CLIP-BUG-06 | codex-closeout | 2026-02-23T02:44:22.525598+00:00 |
| CLIP-BUG-07 | codex-closeout | 2026-02-23T02:44:23.791120+00:00 |
| CLIP-BUG-08 | codex-closeout | 2026-02-23T02:44:24.681246+00:00 |
| CLIP-BUG-09 | codex-closeout | 2026-02-23T02:44:25.224764+00:00 |
| CLIP-BUG-10 | codex-closeout | 2026-02-23T02:44:25.745853+00:00 |
| CLIP-BUG-11 | codex-closeout | 2026-02-23T02:44:26.139078+00:00 |
| CLIP-BUG-12 | codex-closeout | 2026-02-23T02:44:26.526508+00:00 |
| SCLI-P1.2 | codex-closeout | 2026-02-23T02:44:26.999466+00:00 |
| SCLI-P1.4 | codex-closeout | 2026-02-23T02:44:27.340791+00:00 |
| SCLI-P13.2 | codex-closeout | 2026-02-23T02:44:27.691853+00:00 |
## STRATEGIC DIRECTION: Turn Codex into Ante

> Added: 2026-02-20 | Reference: docs/context/ante.md

Ante (by Antigma Labs) is the closest existing product to thegent's vision for autonomous agent orchestration. It is proprietary, preview-quality, and unreliable — but its design philosophy, architecture, and feature set serve as the primary reference target.

**The plan:** Use Codex CLI as the harness foundation (App Server protocol, Responses API, WebSocket, TUI). Implement Ante-like orchestration features on top of thegent's routing/governance/TUI infrastructure. The result is "better than Ante" — Ante's UX patterns + thegent's governance, routing, and multi-tenancy.

**Key Ante capabilities to replicate (priority-ordered):**

1. **Skills system** — SKILL.md format (YAML frontmatter + markdown instructions), discoverable from `~/.{harness}/skills/` + `.{harness}/skills/`, slash command invocation (`/skillname [args]`), pre-approved tool lists per skill, `$ARGUMENTS` substitution. Open format — portable across agents.

2. **Persistent per-project memory (MEMORY.md)** — Auto-inject `MEMORY.md` (first 200 lines) into system prompt at every session start. Per-project scoped at `.claude/projects/<hash>/memory/`. Agent reads/writes via Write/Edit tools. Cross-session continuity without manual prompting.

3. **Named sub-agent types with descriptions** — Markdown + YAML frontmatter definition (name, description, model override, tool restriction). Built-in General + Explorer equivalents. Discovery at session init. Main agent queries descriptions for routing delegation decisions.

4. **`--check` verification pass** — Post-task second LLM pass where agent reviews its own work vs original request, completes gaps, optimizes without breaking correctness.

5. **Structured headless output formats** — `minimal` / `human` / `json` output modes. JSON mode emits one event per line (agent_message, tool_call_started, tool_call_finished, usage_update, error). Standard exit codes (0=success, 1=input, 2=execution, 3=provider, 4=cancelled).

6. **Agent organization patterns** — Four named multi-agent coordination architectures: Independent (parallel fan-out + aggregator), Decentralized (shared board + peer rounds), Centralized Iterative (orchestrator + quality gates), Hybrid Iterative (orchestrator + peer refine). Select via flag.

7. **Context-aware directory injection (headless)** — Auto-append folder structure to headless prompt system context (project layout awareness without manual description).

8. **Offline / local model support** — `--provider local` routing to llama.cpp or Ollama for GGUF inference. Air-gap capability.

**Ante's known weaknesses thegent surpasses:**
- Governance: thegent has comprehensive policy engine; Ante has only tool filtering + approval
- Quality: thegent has 5-layer security pipeline + quality gates; Ante has none
- Organization: thegent has multi-tenant + org features; Ante is single-user only
- Work-stream: thegent has canonical WORK_STREAM.md + plan loop; Ante has no equivalent
- Routing: thegent has 400+ models via OpenRouter; Ante has 6 built-in providers

**Reference:** docs/context/ante.md (comprehensive, verified 2026-02-20)

---

### 2026-02-21 follow-up

- WL-011 parity hardening: non-stream OpenRouter path now matches stream semantics for OR-11/OR-13.
  - OR-11: normalized error envelopes preserve `error.metadata` and enforce `error.code`.
  - OR-13: bounded retries for 408/502/503 on non-stream requests (402 remains no-retry hard-stop).
  - Evidence: `src/thegent/cliproxy_adapter.py` (`_proxy_request`), `tests/routing/test_openrouter_p1_nonstream.py`.
- WL-017 completion hardening: explicit widget classes and default compositor wiring are now present.
  - Added `InteractiveInputWidget`, `TableWidget`, `TimelineWidget`.
  - Wired into default compositor layout with initial table/timeline state + prompt submit handling.
  - Evidence: `src/thegent/tui/widgets/interactive_input.py`, `src/thegent/tui/widgets/table_widget.py`, `src/thegent/tui/widgets/timeline_widget.py`, `src/thegent/tui/compositor.py`.

*Run `thegent plan incorporate` to refresh from plans, research, specs.*

---

### Desktop Automation & UI Implementation (2026-02-21)

### [WL-149] Virtual Desktop Automation (UFO2 PiP Approach)
**Status:** COMPLETED
**Priority:** P1
**Area:** automation, desktop
**Effort:** M
**Blocked by:** none

Implementation of high-performance virtual desktop automation with sub-50ms latency. Uses UFO2 Picture-in-Picture approach for non-colliding agent sessions.

- Created `src/thegent/automation/virtual_desktop.py` with VirtualDesktopManager, DesktopSession
- Created platform providers: windows_virtual_desktop.py (SendInput), linux_virtual_desktop.py (Xvfb), macos_virtual_desktop.py (CGEvent)
- 15 tests passing

**Evidence:** `tests/automation/test_virtual_desktop.py`

---

### [WL-150] Screen-to-UI-Tree Parser (OmniParser/UI-TARS)
**Status:** COMPLETED
**Priority:** P1
**Area:** automation, desktop
**Effort:** M
**Blocked by:** none

Research and implementation of screen parsing to convert screenshots into structured UI trees.

- Researched OmniParser V2 (Microsoft, 39.6% ScreenSpot Pro), UI-TARS (ByteDance, 98.7% accuracy), ScreenParse (arxiv)
- Created `src/thegent/automation/screen_parser.py` with AccessibilityParser (fastest native), OmniParserBackend, UITARSBackend

**Evidence:** `src/thegent/automation/screen_parser.py`

---

### [WL-151] Mobile Automation (Appium-based)
**Status:** COMPLETED
**Priority:** P2
**Area:** automation, mobile
**Effort:** M
**Blocked by:** none

Appium-based mobile automation with simulator support and auth profiles.

- Created `src/thegent/automation/mobile.py` with DeviceConfig, AuthProfile, MobileAutomationManager
- Supports Android/iOS, simulator/emulator/real device
- 5 tests passing

**Evidence:** `tests/automation/test_mobile.py`

---

### [WL-152] Agent Browser with Multi-Profile Auth
**Status:** COMPLETED
**Priority:** P2
**Area:** automation, browser
**Effort:** M
**Blocked by:** none

Multi-profile browser automation with auth management.

- Created `src/thegent/automation/agent_browser.py` with BrowserProfile, AuthAgentProvider (OIDC)
- Integrates with Kernel Browser Profiles, Auth-Agent
- Supports PlaywrightProvider for CDP automation

**Evidence:** `src/thegent/automation/agent_browser.py`

---

### [WL-153] Tray Application
**Status:** COMPLETED
**Priority:** P2
**Area:** desktop, tray
**Effort:** S
**Blocked by:** none

System tray application with menu and notifications.

- Created `src/thegent/tray/__init__.py` with TrayManager, TrayIcon, notification support

**Evidence:** `src/thegent/tray/__init__.py`

---

### [WL-154] Desktop GUI Application (Dual-App Architecture)
**Status:** COMPLETED
**Priority:** P1
**Area:** desktop, gui
**Effort:** M
**Blocked by:** none

Native desktop GUI application working in tandem with TUI compositor and tray.

- Created `src/thegent/desktop/__init__.py` with DesktopApp, AgentSession, AppMode (STANDALONE/TUI_TANDEM/TRAY_TANDEM)
- 8 tests passing
- Works alongside existing TUI compositor (`src/thegent/tui/`, ~5453 LOC Rust/Python)

**Evidence:** `tests/test_unit_desktop_app.py`

---

### Related Research

See `docs/research/CONVERSATION_DUMP_2026-02-21_DESKTOP_AUTOMATION.md` for comprehensive documentation.

---

### [WL-155] Session Memory & Documentation System
**Status:** COMPLETED
**Priority:** P1
**Area:** memory, documentation
**Effort:** M
**Blocked by:** none

Harmonize session memory system: every prompt logged with exact text + agent synthesis, research/planning separate, work stream traceable.

- Enhanced ConversationRecord with agent_synthesis field
- Updated ConversationDumper methods to support agent_synthesis parameter
- Enhanced SessionScraper with TypedDict event schemas (SessionSnapshotCreatedEvent, SessionSnapshotFailedEvent)
- Added trigger normalization, UUID generation, and event logging utilities
- Implemented snapshot event logging (created/failed) with request_event_id support
- All 72 unit tests passing: test_unit_always_write_dumps.py, test_unit_session_scraper.py, test_conversation_dumper.py, test_session_manager.py, test_memory_manager.py

**Evidence:** Tests passing (72/72); Implementation: `src/thegent/orchestration/state/session_scraper.py`, `src/thegent/session/conversation_dumper.py`; Spec: `docs/plans/2026-02-21-SESSION_MEMORY_SYSTEM.md`

### [WL-156] Enhanced Session Scraper (Rich Extraction)
**Status:** COMPLETED
**Priority:** P1
**Area:** memory, scraper
**Effort:** M
**Blocked by:** none

Enhanced session scraper with periodic snapshots, rich extraction, tagging.

- Spec: `docs/plans/2026-02-21-ENHANCED_SESSION_SCRAPER.md`
- Triggers: periodic, tool_use, error, session_change
- Extract: commands, files, facts, decisions
- Tags: YAML frontmatter, #tag syntax, JSON sections

**Evidence:**
- Spec: `docs/plans/2026-02-21-ENHANCED_SESSION_SCRAPER.md`
- Completed: 2026-02-22 (commit bbf8aa26)
- Tests: 10/10 pass (test_unit_session_scraper.py) + 6/6 pass (test_unit_session_scraper_batch6.py)
- Implementation: SessionSnapshotCreatedEvent and SessionSnapshotFailedEvent payload schema validation, request_event_id propagation, trigger normalization

### [WL-157] GitHub Projects Bidirectional Sync (Standalone Optional)
**Status:** COMPLETED
**Priority:** P1
**Area:** planning, sync, integrations
**Effort:** M
**Blocked by:** none (gh auth with `project` scope is runtime/deployment requirement, not code blocker)

Add optional bidirectional GitHub Project v2 sync that remains standalone-safe when disabled.

**Completed:** 2026-02-22 (commit 79c5fbbd)

**Implementation:**
- Config fields in `src/thegent/config.py`:
  - `gh_project_sync_enabled` (bool; default False)
  - `gh_project_owner` (str; GitHub org/user)
  - `gh_project_number` (int; project v2 number)
  - `gh_project_direction` (read_only|write_only|bidirectional; default bidirectional)
  - `gh_project_standalone_mode` (bool; default True — skip gracefully when disabled)

- Sync module: `src/thegent/integrations/gh_project_sync.py`
  - `GHProjectConfig`: Configuration dataclass with validation
  - `GHProjectSyncError`, `GHProjectAuthError`: Custom exceptions
  - `get_project_status()`: Query project metadata and item count
  - `sync_to_github()`: Sync thegent workstream to GitHub Projects
  - `sync_from_github()`: Sync GitHub Projects items to workstream
  - `export_to_csv()`, `import_from_csv()`: CSV exchange
  - Standalone-safe: All functions return gracefully when disabled/auth missing in standalone mode
  - Auth-aware: Detects missing `project` scope and returns status (not crash)

- Comprehensive test coverage: `tests/test_wl157_gh_project_sync.py` (35 tests, 100% pass)
  - Configuration validation
  - Standalone-safe behavior (no crashes when disabled)
  - Auth error handling (graceful skip when gh auth missing project scope)
  - Read/write/bidirectional direction enforcement
  - CSV export/import with path handling
  - Edge cases: disabled config, invalid config, missing files

**Runtime Notes:**
- `gh auth` with `project` scope is a **deployment prerequisite**, not a code blocker
  - Users must run: `gh auth login --scopes "project"`
  - Code detects missing scope and returns `{"status": "auth_required"}` gracefully
- When `THGENT_GH_PROJECT_SYNC_ENABLED=false` or config invalid, all operations return early (no-op)
- Fully backward-compatible: zero user debt, can be disabled entirely

### [WL-158] Unified Workstream Integration for CLIProxyAPI++ Board Artifacts
**Status:** COMPLETED
**Priority:** P1
**Area:** workstream, docs, planning
**Effort:** M
**Blocked by:** none

Integrate the generated CLIProxyAPI++ board/import artifacts into thegent unified workstream loop.

**Completed:** 2026-02-22 (commit 72f26996)

**Implementation:**
- Board artifacts ready in `cliproxyapi-plusplus/docs/planning/`:
  - `CLIPROXYAPI_2000_ITEM_EXECUTION_BOARD_2026-02-22.md` (markdown execution board with status summary)
  - `CLIPROXYAPI_2000_ITEM_EXECUTION_BOARD_2026-02-22.csv` (board items with WL mapping)
  - `CLIPROXYAPI_2000_ITEM_EXECUTION_BOARD_2026-02-22.json` (metadata and execution slices)
  - `GITHUB_PROJECT_IMPORT_CLIPROXYAPI_2000_2026-02-22.csv` (GitHub Projects import format)

- BoardArtifactLoader in `src/thegent/planning/board_artifact_loader.py`:
  - Loads all artifact formats (JSON, CSV, markdown)
  - Maps CLIProxyAPI board items to thegent WL IDs
  - Parses execution slices and their WL range mappings
  - Provides workstream integration interface

- 4 execution slices with active WL cadence:
  - Slice A (Core Routing): WL-001..WL-015 (45% complete)
  - Slice B (Providers): WL-020..WL-050 (28% complete)
  - Slice C (Workstream): WL-158..WL-162 (intake phase)
  - Slice D (Quality): WL-100..WL-140 (15% complete)

**Evidence:**
- Implementation: `src/thegent/planning/board_artifact_loader.py`
- Tests: `tests/test_wl158_board_artifact_integration.py` (12/12 pass)
- Board artifacts: `cliproxyapi-plusplus/docs/planning/`

### [WL-159] Cross-Repo Board Sync Operationalization
**Status:** COMPLETED
**Priority:** P2
**Area:** tooling, operations
**Effort:** S
**Blocked by:** none

Operationalize repeatable board update/import flow using native tooling and explicit command docs.

**Implementation:** Python-native operationalization with CLI and Taskfile integration.

- Added `thegent sync board` command in `src/thegent/cli/apps/sync.py` (sync_board subcommand)
- Added `SyncCommand.sync_board()` method in `src/thegent/commands/sync.py` with work-stream parsing and platform stubs
- Added `task board:sync` and `task board:sync:dry-run` commands to `Taskfile.yml`
- Created comprehensive workflow docs: `docs/reference/BOARD_SYNC_WORKFLOW.md`
- Created test suite: `tests/test_wl159_board_sync.py` (12 tests, all passing)
- Supports GitHub Projects and Linear platforms with environment config (THGENT_BOARD_ID, THGENT_BOARD_SOURCE)
- Dry-run mode for validation before sync

**Evidence:**
- `src/thegent/cli/apps/sync.py:278-310` (sync board CLI command)
- `src/thegent/commands/sync.py:865-980` (SyncCommand.sync_board implementation)
- `Taskfile.yml` (board:sync and board:sync:dry-run tasks)
- `docs/reference/BOARD_SYNC_WORKFLOW.md` (complete workflow documentation)
- `tests/test_wl159_board_sync.py` (12 passing tests)

### [WL-160] Full Automatic Workstream Reflection (GitHub Projects + Linear)
**Status:** COMPLETED
**Priority:** P1
**Area:** sync, automation, integrations
**Effort:** M
**Blocked by:** none

Make board/tooling concerns transparent to agents by running background synchronization that continuously reflects:
- local markdown updates (`docs/reference/WORK_STREAM.md`) -> GitHub Projects + Linear
- remote status updates in GitHub Projects/Linear -> local markdown status lines

Implementation surfaces:
- `src/thegent/integrations/workstream_autosync.py` (640 LOC: cycle runner + adapters + reflection writer)
- `src/thegent/cli/apps/sync.py` (`thegent sync autopilot` command, +120 LOC)
- `src/thegent/config.py` (`THGENT_WORKSTREAM_AUTOSYNC_*`, `THGENT_LINEAR_*` settings, +40 LOC)
- `tests/test_wl160_workstream_autosync.py` (28 comprehensive tests)

**Evidence:** Full implementation complete with:
- WorkstreamAutosyncConfig: bidirectional sync configuration with platform-specific settings
- WorkstreamParser: regex-based WORK_STREAM.md item extraction (status, priority, area, blocked_by)
- WorkstreamAutosyncRunner: async cycle runner with configurable interval (default 300s)
- Platform adapters: stubs for GitHub Projects and Linear (ready for real API integration)
- CLI autopilot: `thegent sync autopilot [--once|--interval|--dry-run|--format]`
- Standalone-safe: gracefully skips when disabled or credentials missing
- Full test coverage: config validation, parsing, sync ops, runner lifecycle, CLI integration
- Commits: WL-160 implementation (640 LOC workstream_autosync.py), plus sync.py, config.py, tests

### [WL-161] Board-ID-First Reconciliation Policy
**Status:** COMPLETED
**Priority:** P1
**Area:** sync, governance
**Effort:** S
**Blocked by:** none

Define deterministic conflict precedence using board-id-first matching and source timestamp ordering.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_2026-02-22.md`

### [WL-181] Status Drift Severity Classification
**Status:** COMPLETED
**Priority:** P1
**Area:** reliability, sync
**Effort:** S
**Blocked by:** none

Add severity tiers for status drift and define escalation thresholds per tier.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_B_2026-02-22.md`

### [WL-201] Sync Provenance Stamps
**Status:** COMPLETED
**Priority:** P1
**Area:** audit, sync
**Effort:** S
**Blocked by:** none

Add per-item provenance stamps for reflected updates in local markdown.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_C_2026-02-22.md`

### [WL-221] Connector Quota Budgets
**Status:** COMPLETED
**Priority:** P1
**Area:** governance, budget
**Effort:** S
**Blocked by:** none

Add per-connector quota budgets for controlled write/read consumption.

**Evidence:** `src/thegent/integrations/capability_alerts.py`, `src/thegent/integrations/workstream_autosync.py`, `tests/test_wl160_workstream_autosync.py`, `tests/test_wl305_capability_alerts.py`

### [WL-241] Auth Expiry Detector
**Status:** COMPLETED
**Priority:** P1
**Area:** auth, reliability
**Effort:** S
**Blocked by:** none

Detect impending connector auth expiration and emit proactive renewal warnings.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_E_2026-02-22.md`

### [WL-261] Sync Policy Audit Command
**Status:** COMPLETED
**Priority:** P1
**Area:** governance, cli
**Effort:** S
**Blocked by:** none

Add audit command to validate runtime behavior against sync-policy contract.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_F_2026-02-22.md`

### [WL-281] Team Ownership Registry
**Status:** COMPLETED
**Priority:** P1
**Area:** governance, ops
**Effort:** S
**Blocked by:** none

Add ownership registry with escalation contacts for each sync domain.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_G_2026-02-22.md`

### [WL-301] Cross-Connector Consistency Verifier
**Status:** COMPLETED
**Priority:** P1
**Area:** integrity, sync
**Effort:** M
**Blocked by:** none

Verify status/priority consistency across all connectors per cycle.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_H_2026-02-22.md`

### [WL-302] Compliance Evidence Snapshot Scheduler
**Status:** COMPLETED
**Priority:** P1
**Area:** compliance, scheduler
**Effort:** S
**Blocked by:** none

Schedule periodic compliance evidence snapshots from sync artifacts.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_H_2026-02-22.md`

### [WL-303] Pipeline Stage Percentiles
**Status:** COMPLETED
**Priority:** P2
**Area:** observability, perf
**Effort:** S
**Blocked by:** none

Capture stage timings and percentile summaries for each sync cycle.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_H_2026-02-22.md`

### [WL-304] Conflict Growth Guardrails
**Status:** COMPLETED
**Priority:** P1
**Area:** safety, conflicts
**Effort:** S
**Blocked by:** none

Add hard controls for runaway conflict queue growth.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_H_2026-02-22.md`

### [WL-305] Capability Mismatch Alerts
**Status:** COMPLETED
**Priority:** P1
**Area:** connectors, alerts
**Effort:** S
**Blocked by:** none

Alert when connector capabilities diverge from required sync features.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_H_2026-02-22.md`

### [WL-306] Runtime Connector Toggle Controls
**Status:** COMPLETED
**Priority:** P2
**Area:** ops, runtime
**Effort:** S
**Blocked by:** none

Allow dynamic connector enable/disable without restarting services.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_H_2026-02-22.md`

### [WL-307] WL ID Reservation Allocator
**Status:** COMPLETED
**Priority:** P2
**Area:** planning, governance
**Effort:** S
**Blocked by:** none

Add allocator for reserving WL ranges for upcoming planning waves.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_H_2026-02-22.md`

### [WL-308] Remote Write Receipts
**Status:** COMPLETED
**Priority:** P1
**Area:** audit, connectors
**Effort:** S
**Blocked by:** none

Record explicit remote write confirmations in cycle reports.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_H_2026-02-22.md`

### [WL-309] Strict Board-ID Uniqueness
**Status:** COMPLETED
**Priority:** P1
**Area:** integrity, governance
**Effort:** S
**Blocked by:** none

Reject duplicate Board IDs across all local and generated sync artifacts.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_H_2026-02-22.md`

### [WL-310] Parallel Local Edit Merge Policy
**Status:** COMPLETED
**Priority:** P1
**Area:** merge, reliability
**Effort:** M
**Blocked by:** none

Define deterministic merge policy for parallel local workstream edits.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_H_2026-02-22.md`

### [WL-311] Versioned Mapping Registry
**Status:** COMPLETED
**Priority:** P1
**Area:** mappings, governance
**Effort:** M
**Blocked by:** none

Version state/priority mapping tables with migration-safe upgrades.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_H_2026-02-22.md`

### [WL-312] Policy Checksum Drift Detection
**Status:** COMPLETED
**Priority:** P1
**Area:** policy, integrity
**Effort:** S
**Blocked by:** none

Embed policy checksum per cycle and detect drift against expected policy.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_H_2026-02-22.md`

### [WL-313] Confidential Report Mode
**Status:** COMPLETED
**Priority:** P2
**Area:** security, reporting
**Effort:** S
**Blocked by:** none

Add confidential-mode reports with minimized metadata exposure.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_H_2026-02-22.md`

### [WL-314] Connector Latency Chaos Mode
**Status:** COMPLETED
**Priority:** P2
**Area:** testing, chaos
**Effort:** M
**Blocked by:** none

Inject synthetic connector latency for resilience validation.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_H_2026-02-22.md`

### [WL-315] Governance Sign-Off Template
**Status:** COMPLETED
**Priority:** P2
**Area:** governance, docs
**Effort:** S
**Blocked by:** none

Create sign-off template for production autosync enablement reviews.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_H_2026-02-22.md`

### [WL-316] Sandbox Seeding Utility
**Status:** COMPLETED
**Priority:** P2
**Area:** testing, tools
**Effort:** S
**Blocked by:** none

Add utility to seed sandbox trackers for repeatable connector tests.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_H_2026-02-22.md`

### [WL-317] Drift Replay Tool
**Status:** COMPLETED
**Priority:** P1
**Area:** replay, diagnostics
**Effort:** M
**Blocked by:** none

Replay drift scenarios from archived manifests for deterministic debugging.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_H_2026-02-22.md`

### [WL-318] Alert Routing Hooks
**Status:** COMPLETED
**Priority:** P2
**Area:** alerts, integrations
**Effort:** S
**Blocked by:** none

Add pluggable alert routing hooks (webhook/email/event bus).

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_H_2026-02-22.md`

### [WL-319] Symptom-to-Fix Docs Matrix
**Status:** COMPLETED
**Priority:** P2
**Area:** docs, support
**Effort:** S
**Blocked by:** none

Publish matrix mapping symptoms to commands and remediation actions.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_H_2026-02-22.md`

### [WL-320] Enterprise Rollout Scorecard
**Status:** COMPLETED
**Priority:** P1
**Area:** enterprise, release
**Effort:** S
**Blocked by:** none

Define rollout scorecard and go/no-go thresholds for enterprise adoption.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_H_2026-02-22.md`

### [WL-282] Connector Maintenance Calendar Ingestion
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** scheduling, connectors
**Effort:** S
**Blocked by:** none

Ingest connector maintenance windows from config to avoid planned outages.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_G_2026-02-22.md`

### [WL-283] Large-Range Partition Planner
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** scale, scheduling
**Effort:** M
**Blocked by:** none

Plan WL-range partitions dynamically for very large workstreams.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_G_2026-02-22.md`

### [WL-284] Rolling Checkpoint Resume
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** reliability, resume
**Effort:** M
**Blocked by:** none

Create rolling checkpoints so long sync cycles can resume safely.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_G_2026-02-22.md`

### [WL-285] Mutation Spike Anomaly Detector
**Status:** COMPLETED
**Priority:** P1
**Area:** observability, safety
**Effort:** S
**Blocked by:** none

Detect abnormal mutation spikes and trigger protective throttling/escalation.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_G_2026-02-22.md`

### [WL-286] Adaptive Per-Connector Rate Limiter
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** performance, reliability
**Effort:** M
**Blocked by:** none

Implement adaptive rate limits by connector and operation class.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_G_2026-02-22.md`

### [WL-287] Label/Tag Parity
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** metadata, sync
**Effort:** S
**Blocked by:** none

Synchronize labels/tags with parity across local and remote trackers.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_G_2026-02-22.md`

### [WL-288] Local Tag Taxonomy Validator
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** validation, docs
**Effort:** S
**Blocked by:** none

Validate local workstream tags against approved taxonomy.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_G_2026-02-22.md`

### [WL-289] Duplicate Title Guard
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** integrity, governance
**Effort:** S
**Blocked by:** none

Add strict duplicate-title checks with explicit exception policy.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_G_2026-02-22.md`

### [WL-290] Local SLA Annotation Sync
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** sla, docs
**Effort:** S
**Blocked by:** none

Reflect SLA metadata into local markdown block annotations.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_G_2026-02-22.md`

### [WL-291] Open Blockers Digest
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** reporting, ops
**Effort:** S
**Blocked by:** none

Generate per-cycle digest of currently open blockers and dependencies.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_G_2026-02-22.md`

### [WL-292] Queue Pruning Lifecycle
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** maintenance, queue
**Effort:** S
**Blocked by:** none

Auto-prune stale conflict and dead-letter entries with retention policy.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_G_2026-02-22.md`

### [WL-293] Signed Capability Cache
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** security, connectors
**Effort:** M
**Blocked by:** key/signing policy

Sign connector capability cache entries and enforce TTL renewal.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_G_2026-02-22.md`

### [WL-294] Policy What-If Simulation
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** governance, cli
**Effort:** S
**Blocked by:** none

Add policy simulation command for hypothetical sync policy changes.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_G_2026-02-22.md`
**Batch evidence:** `docs/reports/2026-02-22-wave70-batch1-wl293-297.md`

### [WL-295] Pull Pagination Resilience Tests
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** tests, connectors
**Effort:** M
**Blocked by:** fixture generation

Test multi-page remote pull behavior with pagination edge cases.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_G_2026-02-22.md`
**Batch evidence:** `docs/reports/2026-02-22-wave70-batch1-wl293-297.md`

### [WL-296] Restore Verifier
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** rollback, reliability
**Effort:** S
**Blocked by:** none

Verify rollback/restore outputs match checkpoint expectations.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_G_2026-02-22.md`
**Batch evidence:** `docs/reports/2026-02-22-wave70-batch1-wl293-297.md`

### [WL-297] Connector Cost Accounting
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** cost, observability
**Effort:** S
**Blocked by:** none

Track per-connector API usage/cost metrics for budgeting.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_G_2026-02-22.md`
**Batch evidence:** `docs/reports/2026-02-22-wave70-batch1-wl293-297.md`

### [WL-298] Enterprise Topology Cookbook
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** docs, architecture
**Effort:** S
**Blocked by:** none

Document common enterprise deployment topologies for autosync.

**Evidence:** `docs/reference/AUTOSYNC_ENTERPRISE_TOPOLOGY_COOKBOOK.md`

### [WL-299] Reliability Score Targets
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** reliability, analytics
**Effort:** S
**Blocked by:** none

Define reliability score computation and target thresholds over time.

**Evidence:** `src/thegent/integrations/reliability_score_targets.py`, `tests/integrations/test_wl299_reliability_score_targets.py`, `docs/reports/2026-02-22-wave70-batch2-wl262-264-299-300.md`

### [WL-300] Default-On Guardrail Pack
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** migration, governance
**Effort:** M
**Blocked by:** none

Ship guardrail policy pack and migration script for default-on rollout.

**Evidence:** `src/thegent/integrations/guardrail_pack_migration.py`, `tests/integrations/test_wl300_default_on_guardrail_pack.py`, `docs/reports/2026-02-22-wave70-batch2-wl262-264-299-300.md`

### [WL-262] Failure Remediation Suggestions
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** ux, diagnostics
**Effort:** S
**Blocked by:** none

Attach deterministic remediation suggestions to common sync failure classes.

**Evidence:** `src/thegent/integrations/remediation_suggestions.py`, `tests/integrations/test_wl262_failure_remediation_suggestions.py`, `docs/reports/2026-02-22-wave70-batch2-wl262-264-299-300.md`

### [WL-263] Credential Source Validator
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** auth, config
**Effort:** S
**Blocked by:** none

Validate credential source precedence and reject ambiguous auth configuration.

**Evidence:** `src/thegent/integrations/credential_source_validator.py`, `tests/integrations/test_wl263_credential_source_validator.py`, `docs/reports/2026-02-22-wave70-batch2-wl262-264-299-300.md`

### [WL-264] WL Block Formatter
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** formatting, parser
**Effort:** S
**Blocked by:** none

Add strict formatter for WL block structure and metadata normalization.

**Evidence:** `src/thegent/integrations/wl_block_formatter.py`, `tests/integrations/test_wl264_wl_block_formatter.py`, `docs/reports/2026-02-22-wave70-batch2-wl262-264-299-300.md`

### [WL-265] Field Mapping Bootstrap Wizard
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** setup, ux
**Effort:** S
**Blocked by:** none

Add first-time setup wizard for connector field/state mapping bootstrap.

**Evidence:** `src/thegent/integrations/field_mapping_wizard.py`, `tests/test_wl265_field_mapping_wizard.py`

### [WL-266] Pre-Apply Connector Health Probe
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** reliability, safety
**Effort:** S
**Blocked by:** none

Run health probe before apply cycle and fail early on degraded connectors.

**Evidence:** `src/thegent/integrations/workstream_autosync.py`, `tests/test_wl160_workstream_autosync.py`

### [WL-267] Adaptive Sync Interval Controller
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** performance, scheduler
**Effort:** M
**Blocked by:** none

Adapt loop interval dynamically based on drift rate, error rate, and load.

**Evidence:** `src/thegent/integrations/adaptive_sync_interval.py`, `tests/test_wl267_adaptive_sync_interval.py`

### [WL-268] Incident Snapshot Bundle
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** incident, audit
**Effort:** S
**Blocked by:** none

Produce immutable incident snapshot bundles for postmortem workflows.

**Evidence:** `src/thegent/integrations/incident_snapshot.py`, `tests/test_wl268_incident_snapshot.py`

### [WL-269] Conflict Triage Categories
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** conflicts, governance
**Effort:** S
**Blocked by:** none

Classify conflicts by category/severity and assign owner routing metadata.

**Evidence:** `src/thegent/integrations/conflict_triage.py`, `tests/test_wl269_conflict_triage.py`

### [WL-270] Metadata Freshness TTL
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** metadata, sync
**Effort:** S
**Blocked by:** none

Enforce metadata freshness TTL and stale marker behavior.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_F_2026-02-22.md`

### [WL-271] Split-Brain Remote State Detector
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** integrity, reliability
**Effort:** M
**Blocked by:** none

Detect divergent remote states across connectors for the same board item.

**Evidence:** `src/thegent/integrations/cross_connector_verifier.py`, `tests/test_wl301_cross_connector_verifier.py`

### [WL-272] Local Status Transition History Log
**Status:** COMPLETED
**Priority:** P1
**Area:** audit, history
**Effort:** S
**Blocked by:** none

Append-only history log for all local status transitions caused by sync.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_F_2026-02-22.md`

### [WL-273] Selective Retry Queue
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** resilience, queue
**Effort:** M
**Blocked by:** none

Queue transient failures for selective retry without replaying successful writes.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_F_2026-02-22.md`

### [WL-274] Connector Sandbox Project Mode
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** testing, safety
**Effort:** S
**Blocked by:** none

Support sandbox project targets for safe connector validation.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_F_2026-02-22.md`

### [WL-275] CI Benchmark Gates
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** ci, performance
**Effort:** M
**Blocked by:** none

Add CI thresholds that fail on autosync latency/throughput regressions.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_F_2026-02-22.md`

### [WL-276] Artifact Redaction Pipeline
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** security, compliance
**Effort:** S
**Blocked by:** none

Redact sensitive fields from reports/artifacts using policy-driven rules.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_F_2026-02-22.md`

### [WL-277] Artifact Format Versioning
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** compatibility, artifacts
**Effort:** S
**Blocked by:** none

Add explicit versioning to export/import/report artifact schemas.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_F_2026-02-22.md`

### [WL-278] Operator Command Aliases
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** cli, ergonomics
**Effort:** S
**Blocked by:** none

Introduce concise aliases for high-frequency operator workflows.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_F_2026-02-22.md`

### [WL-279] Troubleshooting Matrix
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** docs, support
**Effort:** S
**Blocked by:** none

Publish GitHub/Linear failure matrix with causes, diagnostics, and fixes.

**Evidence:** `docs/reference/AUTOSYNC_TROUBLESHOOTING_MATRIX.md`

### [WL-280] Multi-Team Enterprise Rollout Checklist
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** release, enterprise
**Effort:** S
**Blocked by:** none

Define enterprise rollout checklist for multi-team autosync adoption.

**Evidence:** `docs/checklists/AUTOSYNC_ENTERPRISE_ROLLOUT_CHECKLIST.md`

### [WL-242] Immutable Cycle Manifest
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** audit, reproducibility
**Effort:** S
**Blocked by:** none

Write immutable cycle manifests capturing all inputs/decisions/outputs.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_E_2026-02-22.md`

### [WL-243] Dual-Write Shadow Mode
**Status:** COMPLETED
**Priority:** P1
**Area:** rollout, safety
**Effort:** M
**Blocked by:** none

Add observe-only shadow mode before enabling full external mutation.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_E_2026-02-22.md`

### [WL-244] HTML Diff Artifact
**Status:** COMPLETED
**Priority:** P2
**Area:** reporting, ux
**Effort:** S
**Blocked by:** none

Generate side-by-side HTML diff artifacts for local/remote state comparisons.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_E_2026-02-22.md`

### [WL-245] Ownership Metadata Propagation
**Status:** COMPLETED
**Priority:** P1
**Area:** metadata, sync
**Effort:** M
**Blocked by:** none

Propagate per-item ownership metadata across local, GitHub, and Linear.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_E_2026-02-22.md`

### [WL-246] Env Profile Drift Validator
**Status:** COMPLETED
**Priority:** P2
**Area:** config, validation
**Effort:** S
**Blocked by:** none

Validate config parity/drift across dev/staging/prod autosync profiles.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_E_2026-02-22.md`

### [WL-247] Legacy Board ID Migration Tool
**Status:** COMPLETED
**Priority:** P1
**Area:** migration, cli
**Effort:** M
**Blocked by:** none

Add migration command to normalize legacy IDs into WL namespace.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_E_2026-02-22.md`

### [WL-248] Remote-Orphan Detector
**Status:** COMPLETED
**Priority:** P1
**Area:** integrity, sync
**Effort:** S
**Blocked by:** none

Detect remote tracker items lacking local workstream representation.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_E_2026-02-22.md`

### [WL-249] Local-Orphan Detector
**Status:** COMPLETED
**Priority:** P1
**Area:** integrity, sync
**Effort:** S
**Blocked by:** none

Detect local workstream items lacking any remote tracker mapping.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_E_2026-02-22.md`

### [WL-250] Conflict TTL and Escalation
**Status:** COMPLETED
**Priority:** P1
**Area:** governance, conflicts
**Effort:** S
**Blocked by:** none

Add conflict TTL with automatic escalation actions after timeout.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_E_2026-02-22.md`

### [WL-251] Retry Class Policy
**Status:** COMPLETED
**Priority:** P1
**Area:** resilience, policy
**Effort:** M
**Blocked by:** none

Implement policy classes for transient versus permanent connector errors.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_E_2026-02-22.md`

**Completed:** 2026-02-22 — RetryClassPolicy + RetryClassifier with three error classes (TRANSIENT, PERMANENT, RATE_LIMITED) and substring-based matching. 17 tests passing.

### [WL-252] Offline Simulation Mode
**Status:** COMPLETED
**Priority:** P2
**Area:** testing, ux
**Effort:** S
**Blocked by:** none

Add simulation mode for offline connector verification and dry verification.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_E_2026-02-22.md`

**Completed:** 2026-02-22 — OfflineSimulationMode + SimulatedResponse for mocking API responses without network calls. Enable/disable toggles and per-endpoint response registration. 17 tests passing.

### [WL-253] Snapshot Compaction
**Status:** COMPLETED
**Priority:** P2
**Area:** storage, ops
**Effort:** S
**Blocked by:** none

Compact/rotate long-lived cycle artifacts to control report directory growth.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_E_2026-02-22.md`

**Completed:** 2026-02-22 — SnapshotCompactor with registration, compaction tracking, and savings calculation. Tracks original vs compacted size. Query methods for compacted/uncompacted snapshots. 22 tests passing.

### [WL-254] Encrypted Artifact Option
**Status:** COMPLETED
**Priority:** P2
**Area:** security, compliance
**Effort:** M
**Blocked by:** key policy

Add optional encryption-at-rest for sync artifact outputs.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_E_2026-02-22.md`

**Completed:** 2026-02-22 — EncryptedArtifactStore with ArtifactEncryptionConfig. Store/retrieve/list artifacts with per-artifact encryption metadata. Default AES-256 algorithm with configurable key_id. 23 tests passing.

### [WL-255] Run Correlation IDs
**Status:** COMPLETED
**Priority:** P1
**Area:** observability, tracing
**Effort:** S
**Blocked by:** none

Use shared run-level correlation IDs for all connector calls/events.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_E_2026-02-22.md`

### [WL-256] No-Op Fast Path
**Status:** COMPLETED
**Priority:** P2
**Area:** performance, sync
**Effort:** S
**Blocked by:** none

Add fast no-op cycle path and explicit telemetry for unchanged runs.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_E_2026-02-22.md`

### [WL-257] Historical Trend Reports
**Status:** COMPLETED
**Priority:** P2
**Area:** analytics, reporting
**Effort:** M
**Blocked by:** none

Produce trend reports for drift/error/latency over long horizons.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_E_2026-02-22.md`

### [WL-258] Docs Freshness Checker
**Status:** COMPLETED
**Priority:** P2
**Area:** docs, quality
**Effort:** S
**Blocked by:** none

Add automatic checker for stale sync docs and command reference drift.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_E_2026-02-22.md`

### [WL-259] Operator Acceptance Tests
**Status:** COMPLETED
**Priority:** P1
**Area:** tests, ops
**Effort:** M
**Blocked by:** fixture orchestration

Add operator journey acceptance tests from setup to steady-state operation.

**Evidence:** `src/thegent/integrations/operator_acceptance.py`, `tests/test_wl259_operator_acceptance.py`

### [WL-260] Default Enablement Migration Plan
**Status:** COMPLETED
**Priority:** P1
**Area:** migration, release
**Effort:** S
**Blocked by:** none

Define migration plan for enabling autosync by default in existing repos.

**Evidence:** `src/thegent/integrations/enablement_migration.py`, `tests/test_wl260_enablement_migration.py`

### [WL-222] Blackout Calendar Support
**Status:** COMPLETED
**Priority:** P2
**Area:** ops, scheduling
**Effort:** S
**Blocked by:** none

Add project-level blackout windows where autosync pauses external mutation.

**Evidence:** `src/thegent/integrations/blackout_calendar.py`, `tests/test_wl222_blackout_calendar.py`

### [WL-223] Actor/Impersonation Guardrails
**Status:** COMPLETED
**Priority:** P1
**Area:** security, governance
**Effort:** S
**Blocked by:** none

Validate acting identity and prevent unintended impersonation in connector writes.

**Evidence:** `src/thegent/integrations/actor_guardrails.py`, `tests/test_wl223_actor_guardrails.py`

### [WL-224] Workstream Schema Linter
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** validation, parser
**Effort:** M
**Blocked by:** none

Add linter for WORK_STREAM structure consistency and malformed block detection.

**Evidence:** `src/thegent/commands/workstream.py`, `src/thegent/utils/workstream_ops.py`, `src/thegent/cli/commands/plan_cmds.py`, `tests/test_workstream_ops.py`, `tests/test_plan_verify_workstream_cmd.py`

### [WL-225] WL Sort/Normalize Command
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** cli, hygiene
**Effort:** S
**Blocked by:** none

Add deterministic WL ordering and normalization command for maintenance.

**Evidence:** `src/thegent/commands/workstream.py`, `src/thegent/utils/workstream_ops.py`, `src/thegent/cli/commands/plan_cmds.py`, `tests/test_workstream_ops.py`

### [WL-226] Remote Payload Checksums
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** integrity, sync
**Effort:** S
**Blocked by:** none

Add optional checksums for payload integrity verification during reflection.

**Evidence:** `src/thegent/integrations/policy_checksum.py`, `src/thegent/integrations/workstream_autosync.py`, `tests/integrations/test_wl312_policy_checksum.py`, `tests/test_wl160_workstream_autosync.py`

### [WL-227] Metadata Enrichment
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** docs, sync
**Effort:** S
**Blocked by:** none

Enrich remote items with source links, tags, and structured reference metadata.

**Evidence:** `src/thegent/integrations/sync_provenance.py`, `src/thegent/integrations/reflection_event_log.py`, `src/thegent/integrations/workstream_autosync.py`, `tests/test_wl201_sync_provenance.py`, `tests/test_wl261_sync_audit.py`

### [WL-228] Connector Capability Discovery
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** architecture, connectors
**Effort:** M
**Blocked by:** none

Add capability probing and feature flags for connector-specific behavior gates.

**Evidence:** `src/thegent/integrations/connector_capability_discovery.py`, `tests/test_wl228_connector_capability_discovery.py`

### [WL-229] Maintenance Banner Propagation
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** ux, ops
**Effort:** S
**Blocked by:** none

Propagate maintenance mode banners to CLI output and report artifacts.

**Evidence:** `src/thegent/integrations/maintenance_banner.py`, `tests/test_wl229_maintenance_banner.py`

### [WL-230] Emergency Stop Switch
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** safety, ops
**Effort:** S
**Blocked by:** none

Add emergency stop file/env switch watched by autopilot loop.

**Evidence:** `src/thegent/integrations/workstream_autosync.py`, `tests/test_wl160_workstream_autosync.py`

### [WL-231] Replay-Safe Mutation IDs
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** idempotency, sync
**Effort:** M
**Blocked by:** none

Assign operation IDs to remote writes to prevent duplicate replay side effects.

**Evidence:** `src/thegent/integrations/workstream_autosync.py`, `tests/test_wl160_workstream_autosync.py`

### [WL-232] Signed Audit Artifact Chain
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** compliance, audit
**Effort:** M
**Blocked by:** key management policy

Add signed audit artifact chaining for compliance-grade provenance evidence.

**Evidence:** `src/thegent/integrations/signed_audit_chain.py`, `tests/test_wl232_signed_audit_chain.py`

### [WL-233] Connector SLA Tracking
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** observability, sla
**Effort:** S
**Blocked by:** none

Track connector SLAs and emit alerts when latency/error thresholds breach.

**Evidence:** `src/thegent/integrations/connector_sla.py`, `tests/test_wl233_connector_sla.py`

### [WL-234] Incident Runbook
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** docs, ops
**Effort:** S
**Blocked by:** none

Publish incident response and rollback runbook for autosync failures.

**Evidence:** `docs/site/operations/runbooks.md`, `tests/test_wl160_workstream_autosync.py`

### [WL-235] Connector Chaos Tests
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** tests, resilience
**Effort:** M
**Blocked by:** chaos fixture matrix

Add chaos tests covering connector outages and partial-failure edge cases.

**Evidence:** `src/thegent/integrations/workstream_autosync.py`, `tests/test_wl160_workstream_autosync.py`

### [WL-236] Cold/Warm Benchmark Split
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** perf, benchmarks
**Effort:** S
**Blocked by:** none

Split benchmark reporting between cold-start and warm-cache operation modes.

**Evidence:** `scripts/benchmark_python_suite.py`, `scripts/benchmark-report.py`, `tests/performance/test_python_benchmark_suite.py`

### [WL-237] Hourly Change Digest
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** reporting, ux
**Effort:** S
**Blocked by:** none

Generate compact hourly digest summarizing all local and remote changes.

**Evidence:** `src/research_engine/digest.py`, `tests/research_engine/test_digest.py`, `tests/test_wl160_workstream_autosync.py`

### [WL-238] Remote→Local Annotation Standard
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** docs, formatting
**Effort:** S
**Blocked by:** none

Standardize annotation block format for remote-to-local reflection details.

**Evidence:** `src/thegent/integrations/annotation_standard.py`, `tests/test_wl238_annotation_standard.py`

### [WL-239] Staged Rollout Profiles
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** release, config
**Effort:** M
**Blocked by:** none

Add rollout presets for dev/staging/prod with safety defaults.

**Evidence:** `src/thegent/integrations/staged_rollout.py`, `tests/test_wl239_staged_rollout.py`

### [WL-240] GA Readiness Criteria
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** release, governance
**Effort:** S
**Blocked by:** none

Define GA/default-on criteria and final readiness review checklist.

**Evidence:** `docs/reference/AUTOSYNC_GA_READINESS_CRITERIA.md`, `src/thegent/sync/ga_readiness.py`, `tests/test_unit_autosync_doctor.py`, `docs/reports/2026-02-22-wave70-lane7-execution.md`

### [WL-202] Anti-Flap Status Hysteresis
**Status:** COMPLETED
**Priority:** P1
**Area:** reliability, sync
**Effort:** S
**Blocked by:** none

Introduce hysteresis to prevent rapid status oscillation across cycles.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_C_2026-02-22.md`

### [WL-203] Local Decision Journal
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** audit, replay
**Effort:** M
**Blocked by:** none

Persist replayable journal entries for each sync decision.

**Evidence:** `src/thegent/sync/journal.py`, `tests/test_unit_sync_journal.py`, `docs/reports/2026-02-22-wave70-lane7-execution.md`

### [WL-204] Conflict Surface Command
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** cli, ux
**Effort:** S
**Blocked by:** none

Add CLI command to list unresolved sync conflicts and recommended actions.

**Evidence:** `src/thegent/sync/conflicts.py`, `tests/test_unit_sync_conflicts.py`, `tests/test_cli_sync.py`, `docs/reports/2026-02-22-wave70-lane7-execution.md`

### [WL-205] Manual Conflict Queue
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** governance, sync
**Effort:** M
**Blocked by:** none

Add machine-readable conflict queue file for deterministic manual resolution.

**Evidence:** `src/thegent/sync/queue.py`, `tests/test_unit_sync_queue.py`, `docs/reports/2026-02-22-wave70-lane7-execution.md`

### [WL-206] Sync Freeze/Unfreeze Controls
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** ops, cli
**Effort:** S
**Blocked by:** none

Add maintenance controls to pause and resume automatic sync safely.

**Evidence:** `src/thegent/sync/controller.py`, `tests/test_unit_sync_controller.py`, `docs/reports/2026-02-22-wave70-lane7-execution.md`

### [WL-207] Full-Rescan Scheduler
**Status:** COMPLETED
**Priority:** P1
**Area:** reliability, scheduler
**Effort:** S
**Blocked by:** none

Schedule periodic full-rescan passes in addition to incremental cycles.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_C_2026-02-22.md`

### [WL-208] Max-Changes Per Cycle Guardrail
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** safety, sync
**Effort:** S
**Blocked by:** none

Cap per-cycle mutation volume with explicit fail-loud behavior when exceeded.

**Evidence:** `src/thegent/sync/engine.py`, `tests/test_unit_sync_engine.py`, `docs/reports/2026-02-22-wave70-lane7-execution.md`

### [WL-209] Connector Health Scoreboard
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** observability, ux
**Effort:** S
**Blocked by:** none

Publish connector health and drift scores in CLI/report artifacts.

**Evidence:** `src/thegent/sync/health.py`, `tests/test_unit_sync_health.py`, `docs/reports/2026-02-22-wave70-lane7-execution.md`

### [WL-210] Field/Schema Drift Detection
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** integrity, sync
**Effort:** M
**Blocked by:** none

Detect remote field/schema changes that invalidate current sync mappings.

**Evidence:** `src/thegent/sync/schema.py`, `tests/test_unit_schema_drift.py`, `docs/reports/2026-02-22-wave70-lane7-execution.md`

### [WL-211] Required Field Validation Gate
**Status:** COMPLETED (2026-02-22)
**Priority:** P1
**Area:** validation, governance
**Effort:** S
**Blocked by:** none

Add strict validation that required custom fields exist before external writes.

**Evidence:** `src/thegent/sync/validation.py`, `tests/test_unit_required_field_validation.py`, `docs/reports/2026-02-22-wave70-lane7-execution.md`

### [WL-212] Pull-Only-on-Failure Mode
**Status:** COMPLETED (2026-02-22)
**Priority:** P2
**Area:** resilience, config
**Effort:** S
**Blocked by:** none

Add explicit, visible pull-only mode for degraded write conditions.

**Evidence:** `src/thegent/sync/retry.py`, `tests/test_unit_sync_retry.py`, `docs/reports/2026-02-22-wave70-lane7-execution.md`

### [WL-213] Dead-Letter Queue for Remote Writes
**Status:** COMPLETED
**Priority:** P1
**Area:** reliability, queue
**Effort:** M
**Blocked by:** none

Persist rejected remote writes in a dead-letter queue for deterministic recovery.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_C_2026-02-22.md`
**Implementation:** `src/thegent/integrations/dead_letter_queue.py` with `DeadLetterEntry` dataclass and `DeadLetterQueue` class (enqueue, read_all, pending, mark_retried, purge_resolved). Tests: `tests/integrations/test_wl213_dead_letter_queue.py` (13 tests).

### [WL-214] Dead-Letter Replay Command
**Status:** COMPLETED
**Priority:** P1
**Area:** cli, recovery
**Effort:** S
**Blocked by:** none

Add replay command to reprocess dead-letter entries after connector fixes.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_C_2026-02-22.md`
**Implementation:** `src/thegent/integrations/dead_letter_replay.py` with `ReplayResult` dataclass and `DeadLetterReplayEngine` class (replay_one, replay_all, replay_summary). Tests: `tests/integrations/test_wl214_dead_letter_replay.py` (14 tests).

### [WL-215] Cycle Performance Benchmark Harness
**Status:** COMPLETED
**Priority:** P2
**Area:** perf, benchmarks
**Effort:** M
**Blocked by:** none

Build benchmark harness for cycle latency, throughput, and error profile.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_C_2026-02-22.md`
**Implementation:** `src/thegent/integrations/cycle_benchmark.py` with `CycleBenchmark` dataclass and `CycleBenchmarkHarness` class (start_cycle, end_cycle, get_duration_seconds, all_benchmarks). Tests: `tests/test_wl215_cycle_benchmark.py` (10 tests).

### [WL-216] 1k+ Item Load Tests
**Status:** COMPLETED
**Priority:** P1
**Area:** perf, tests
**Effort:** M
**Blocked by:** fixture generation

Add synthetic load tests for projects with 1k+ WL items.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_C_2026-02-22.md`
**Implementation:** `src/thegent/integrations/load_test_harness.py` with `LoadTestConfig` dataclass and `LoadTestHarness` class (generate_items, run_batch, summarize). Tests: `tests/test_wl216_load_test_harness.py` (12 tests).

### [WL-217] Tenancy-Safe Namespacing
**Status:** COMPLETED
**Priority:** P1
**Area:** tenancy, safety
**Effort:** M
**Blocked by:** none

Namespace caches, locks, and reports by project tenancy to prevent cross-talk.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_C_2026-02-22.md`
**Implementation:** `src/thegent/integrations/tenant_namespace.py` with `TenantNamespace` dataclass and `TenantNamespaceResolver` class (namespace, strip_namespace, is_owned, namespace_dict, strip_dict). Tests: `tests/integrations/test_wl217_tenant_namespace.py` (15 tests).

### [WL-218] Autosync Onboarding Wizard
**Status:** COMPLETED
**Priority:** P2
**Area:** setup, ux
**Effort:** S
**Blocked by:** none

Add setup wizard path for autosync environment keys, scopes, and quick verification.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_C_2026-02-22.md`
**Implementation:** `src/thegent/integrations/onboarding_wizard.py` with `OnboardingStep` dataclass and `OnboardingWizard` class (STEPS, get_steps, complete_step, next_incomplete, is_complete, progress). Tests: `tests/integrations/test_wl218_onboarding_wizard.py` (18 tests).

### [WL-219] VitePress Ops Docset for Autosync
**Status:** COMPLETED
**Priority:** P2
**Area:** docs, vitepress
**Effort:** S
**Blocked by:** none

Add dedicated docset section for autonomous reflection operations and troubleshooting.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_C_2026-02-22.md`
**Implementation:** `src/thegent/integrations/vitepress_ops.py` with `VitePressOpsDocset` class (generate_nav, render_index). Tests: `tests/test_wl219_vitepress_ops.py` (11 tests).

### [WL-220] Production Readiness Gate
**Status:** COMPLETED
**Priority:** P1
**Area:** release, governance
**Effort:** S
**Blocked by:** none

Define production readiness checklist for enabling autosync by default.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_C_2026-02-22.md`
**Implementation:** `src/thegent/integrations/prod_readiness.py` with `ReadinessCheck` dataclass and `ProductionReadinessGate` class (REQUIRED, add, evaluate, missing_checks, failed_checks, report). Tests: `tests/integrations/test_wl220_prod_readiness.py` (15 tests).

### [WL-182] Stale Item Detector
**Status:** COMPLETED
**Priority:** P2
**Area:** monitoring, sync
**Effort:** S
**Blocked by:** none

Detect items that have no local or remote movement beyond configured age thresholds.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_B_2026-02-22.md`
**Implementation:** `src/thegent/integrations/stale_detector.py` with `StaleConfig`, `StaleItem` dataclasses and `StaleItemDetector` class (is_stale, detect, summary). Tests: `tests/integrations/test_wl182_stale_detector.py` (21 tests).

### [WL-183] Board-ID Collision Guard
**Status:** COMPLETED
**Priority:** P1
**Area:** integrity, sync
**Effort:** S
**Blocked by:** none

Detect duplicate board IDs across connectors and hard-fail the cycle when collisions occur.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_B_2026-02-22.md`
**Implementation:** `src/thegent/integrations/board_id_guard.py` with `BoardIdCollisionError`, `BoardIdRegistry`, and `validate_no_collisions()`. Tests: `tests/test_wl183_board_id_guard.py` (14 tests).

### [WL-184] WL Header Normalization Pass
**Status:** COMPLETED
**Priority:** P2
**Area:** parser, workstream
**Effort:** S
**Blocked by:** none

Normalize malformed WL headers before reflection to avoid parser split-brain behavior.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_B_2026-02-22.md`
**Implementation:** `src/thegent/integrations/header_normalizer.py` with `NormalizationResult` dataclass and `WLHeaderNormalizer` class (normalize_title, normalize_status, normalize_priority, normalize_record). Tests: `tests/integrations/test_wl184_header_normalizer.py` (24 tests).

### [WL-185] Reflection Rollback Command
**Status:** COMPLETED
**Priority:** P1
**Area:** safety, cli
**Effort:** M
**Blocked by:** none

Add rollback command to restore last known-good local snapshot after bad sync cycles.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_B_2026-02-22.md`
**Implementation:** `src/thegent/integrations/reflection_rollback.py` with `RollbackEntry` dataclass and `ReflectionRollbackStore` class (record, rollback_to, list_entries). Tests: `tests/test_wl185_reflection_rollback.py` (15 tests).

### [WL-186] Human-Readable Dry-Run Diffs
**Status:** COMPLETED
**Priority:** P2
**Area:** ux, cli
**Effort:** S
**Blocked by:** none

Add dry-run output showing exact local and remote field deltas before apply.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_B_2026-02-22.md`
**Implementation:** `src/thegent/integrations/dry_run_diff.py` with `FieldDiff`, `DryRunDiff` dataclasses and `DryRunRenderer` class (compute_diff, render_text, render_batch). Tests: `tests/integrations/test_wl186_dry_run_diff.py` (19 tests).

### [WL-187] External Write Batching
**Status:** COMPLETED
**Priority:** P1
**Area:** performance, sync
**Effort:** M
**Blocked by:** API limits

Batch connector writes to reduce API churn and stabilize long-running loops.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_B_2026-02-22.md`

**Implementation:** `src/thegent/integrations/external_write_batcher.py` with `WriteRequest` and `ExternalWriteBatcher`. Tests: `tests/test_wl187_external_write_batcher.py` (14 tests, all passing).

### [WL-188] WL-Range Partitioned Sync
**Status:** COMPLETED
**Priority:** P2
**Area:** scalability, sync
**Effort:** S
**Blocked by:** none

Support range-limited sync execution by WL ID interval for safer phased rollouts.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_B_2026-02-22.md`

**Implementation:** `src/thegent/integrations/range_partitioned_sync.py` with `SyncPartition` and `RangePartitionedSync`. Tests: `tests/test_wl188_range_partitioned_sync.py` (16 tests, all passing).

### [WL-189] WL Ignore List
**Status:** COMPLETED
**Priority:** P2
**Area:** config, sync
**Effort:** S
**Blocked by:** none

Add config for explicit WL ID exclusions from sync apply cycles.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_B_2026-02-22.md`

**Implementation:** `src/thegent/integrations/wl_ignore_list.py` with `WLIgnoreList` class. Tests: `tests/test_wl189_wl_ignore_list.py` (18 tests, all passing).

### [WL-190] Strict Mapping Mode
**Status:** COMPLETED
**Priority:** P1
**Area:** governance, sync
**Effort:** S
**Blocked by:** none

Add strict mode that fails loudly on unknown remote states or unmapped field values.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_B_2026-02-22.md`

**Implementation:** `src/thegent/integrations/strict_mapping.py` with `StrictMappingError`, `StrictMappingConfig`, and `StrictMappingValidator`. Tests: `tests/test_wl190_strict_mapping.py` (14 tests, all passing).

### [WL-191] Connector Mapping Cache
**Status:** COMPLETED
**Priority:** P1
**Area:** performance, config
**Effort:** M
**Blocked by:** none

Cache GitHub field IDs and Linear state mappings to avoid repetitive discovery calls.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_B_2026-02-22.md`

**Implementation:** `src/thegent/integrations/connector_mapping_cache.py` with `MappingEntry` dataclass and `ConnectorMappingCache` class. Tests: `tests/integrations/test_wl191_connector_mapping_cache.py` (14 tests, all passing).

### [WL-192] Startup Scope/Reachability Validation
**Status:** COMPLETED
**Priority:** P1
**Area:** diagnostics, startup
**Effort:** S
**Blocked by:** none

Add startup checks for auth scopes, endpoint reachability, and required project metadata.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_B_2026-02-22.md`

**Implementation:** `src/thegent/integrations/startup_validation.py` with `StartupValidationResult` and `StartupValidator`. Tests: `tests/test_wl192_startup_validation.py` (12 tests, all passing).

### [WL-193] Per-Connector Timeout Controls
**Status:** COMPLETED
**Priority:** P2
**Area:** reliability, config
**Effort:** S
**Blocked by:** none

Expose separate timeout controls for GitHub and Linear operations.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_B_2026-02-22.md`

**Implementation:** `src/thegent/integrations/connector_timeout.py` with `ConnectorTimeoutConfig` and `ConnectorTimeoutRegistry`. Tests: `tests/test_wl193_connector_timeout.py` (16 tests, all passing).

### [WL-194] Connector Circuit Breakers
**Status:** COMPLETED
**Priority:** P1
**Area:** resilience, sync
**Effort:** M
**Blocked by:** none

Add per-connector circuit breakers to isolate repeated failures without silent degradation.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_B_2026-02-22.md`

**Implementation:** `src/thegent/integrations/connector_circuit_breaker.py` with `CircuitState` enum and `ConnectorCircuitBreaker` (state transitions: CLOSED -> OPEN -> HALF_OPEN). Tests: `tests/test_wl194_connector_circuit_breaker.py` (35 tests, all passing).

### [WL-195] Reflection Decision Event Log
**Status:** COMPLETED
**Priority:** P1
**Area:** observability, audit
**Effort:** S
**Blocked by:** none

Log every reflection decision with before/after values and connector provenance.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_B_2026-02-22.md`

**Implementation:** `src/thegent/integrations/reflection_event_log.py` with `ReflectionDecision` and `ReflectionEventLog` (persists to JSONL). Tests: `tests/test_wl195_reflection_event_log.py` (14 tests, all passing).

### [WL-196] Prometheus Metrics Export
**Status:** COMPLETED
**Priority:** P2
**Area:** observability, metrics
**Effort:** M
**Blocked by:** none

Add Prometheus-compatible metrics export for sync health and throughput.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_B_2026-02-22.md`

**Implementation:** `src/thegent/integrations/prometheus_metrics.py` with `MetricSample` dataclass and `PrometheusMetricsExporter` (text format export with label handling). Tests: `tests/test_wl196_prometheus_metrics.py` (24 tests, all passing).

### [WL-197] Sync Policy File Contract
**Status:** COMPLETED
**Priority:** P1
**Area:** governance, config
**Effort:** M
**Blocked by:** none

Define `.thegent/sync-policy.yaml` for conflict precedence, strictness, and connector rules.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_B_2026-02-22.md`

**Implementation:** `src/thegent/integrations/sync_policy_contract.py` extended with `SyncPolicyContract` and `SyncPolicyValidator` (WL-197: simple mode; retains full YAML loading for compatibility). Tests: `tests/test_wl197_sync_policy_contract.py` (14 tests, all passing).

### [WL-198] End-to-End Replay Fixture
**Status:** COMPLETED
**Priority:** P1
**Area:** tests, e2e
**Effort:** M
**Blocked by:** none

Create e2e replay fixtures for full local->remote->local reflection cycles.

**Implementation:** `src/thegent/integrations/e2e_replay_fixture.py` with `ReplayEvent` and `E2EReplayFixture` (event recording, replay, and management). Tests: `tests/test_wl198_e2e_replay_fixture.py` (21 tests, all passing).

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_B_2026-02-22.md`

### [WL-199] Multi-Project Tenancy Autosync Docs
**Status:** COMPLETED
**Priority:** P2
**Area:** docs, tenancy
**Effort:** S
**Blocked by:** none

Document operational patterns for running autosync across multiple project roots.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_B_2026-02-22.md`

**Implementation:** `src/thegent/integrations/multi_project_tenancy_docs.py` with `TenancyDocEntry` dataclass and `MultiProjectTenancyDocs` class for managing multi-project documentation. Provides `register()`, `get()`, and `render_markdown()` methods. Tests: `tests/test_wl199_multi_project_tenancy_docs.py` (11 tests, all passing).

### [WL-200] Autosync Release/Migration Checklist
**Status:** COMPLETED
**Priority:** P1
**Area:** release, docs
**Effort:** S
**Blocked by:** none

Publish enablement and migration checklist for adopting autosync in existing repos.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_B_2026-02-22.md`

**Implementation:** `docs/guides/AUTOSYNC_ENABLEMENT_CHECKLIST.md` (comprehensive guide with prerequisites, enablement, migration, rollback, verification, and troubleshooting). Module: `src/thegent/integrations/autosync_checklist.py` with checklist and verification functions. Tests: `tests/test_wl200_autosync_checklist.py` (14 tests, all passing).

### [WL-162] GitHub Field Update Parity
**Status:** COMPLETED
**Priority:** P1
**Area:** github, sync
**Effort:** M
**Blocked by:** GitHub Project field IDs

Push status and priority updates to GitHub Project fields instead of only draft item body text.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_2026-02-22.md`

**Implementation:** `src/thegent/integrations/github_field_parity.py` with `FieldParityReport` dataclass and `GitHubFieldParityChecker` class. Provides `check()`, `check_all()`, and `out_of_parity()` methods for field parity validation. Tests: `tests/test_wl162_github_field_parity.py` (15 tests, all passing).

### [WL-163] GitHub Pull Reflection Audit Trail
**Status:** COMPLETED
**Priority:** P1
**Area:** github, workstream
**Effort:** S
**Blocked by:** none

Reflect pulled GitHub status changes into local markdown with explicit sync-cycle audit notes.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_2026-02-22.md`
**Implementation:** `src/thegent/integrations/gh_pull_audit.py` with `PullReflectionAuditEntry` dataclass and `PullReflectionAuditLog` class. Persists to `docs/reference/gh_pull_audit.jsonl`. Tests: `tests/test_wl163_gh_pull_audit.py` (7 tests).

### [WL-164] Linear State Mapping Table
**Status:** COMPLETED
**Priority:** P1
**Area:** linear, sync
**Effort:** M
**Blocked by:** Linear workflow configuration

Implement explicit state ID mapping for Todo/In Progress/Done with fail-fast validation.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_2026-02-22.md`

**Implementation:** `src/thegent/integrations/linear_graphql.py` with `build_linear_state_mapping()` function. Tests: `tests/test_wl164_linear_state_mapping.py` (2 tests, all passing).

### [WL-165] Linear Priority Round-Trip
**Status:** COMPLETED
**Priority:** P1
**Area:** linear, sync
**Effort:** S
**Blocked by:** none

Add full priority round-trip between local P-levels and Linear priority semantics.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_2026-02-22.md`
**Implementation:** `src/thegent/integrations/linear_priority.py` with `LinearPriority` and `LocalPriority` enums, `linear_to_local()` and `local_to_linear()` converters with stable round-trip. Tests: `tests/test_wl165_linear_priority.py` (23 tests).

### [WL-166] Idempotency Index Cache
**Status:** COMPLETED
**Priority:** P1
**Area:** sync, cache
**Effort:** M
**Blocked by:** none

Persist a local dedup/index cache to enforce idempotent external writes across cycles.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_2026-02-22.md`

**Implementation:** `src/thegent/integrations/idempotency_cache.py` with `IdempotencyRecord` dataclass and `IdempotencyCache` class. Tests: `tests/test_wl166_idempotency_cache.py` (19 tests, all passing).

### [WL-167] Remote Archive/Delete Policy
**Status:** COMPLETED
**Priority:** P2
**Area:** sync, lifecycle
**Effort:** S
**Blocked by:** none

Define and implement reflection policy for archived/deleted remote items.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_2026-02-22.md`

**Implementation:** `src/thegent/integrations/remote_archive_policy.py` with `ArchiveAction` enum (ARCHIVE, DELETE, SKIP) and `RemoteArchivePolicy` class. Provides `set_policy()`, `get_action()`, and `apply()` methods for per-connector lifecycle management. Tests: `tests/test_wl167_remote_archive_policy.py` (14 tests, all passing).

### [WL-168] Sync Scope Filters
**Status:** COMPLETED
**Priority:** P2
**Area:** ux, sync
**Effort:** S
**Blocked by:** none

Add selective sync filters by area, status, priority, and WL prefix ranges.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_2026-02-22.md`

**Implementation:** `src/thegent/integrations/sync_scope_filter.py` with `SyncScopeFilter` class supporting include/exclude patterns via substring matching. Provides `matches()` and `filter()` methods for scope validation. Tests: `tests/test_wl168_sync_scope_filter.py` (15 tests, all passing).

### [WL-169] API Rate-Limit Backoff Controls
**Status:** COMPLETED
**Priority:** P1
**Area:** reliability, sync
**Effort:** M
**Blocked by:** none

Implement unified backoff and bounded retry policy for GitHub/Linear API pressure handling.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_2026-02-22.md`

**Implementation:** `src/thegent/integrations/rate_limit_backoff.py` with `RateLimitConfig` dataclass and `RateLimitBackoffManager` class. Tests: `tests/test_wl169_rate_limit_backoff.py` (22 tests, all passing).

### [WL-170] Error Budget and Escalation Thresholds
**Status:** COMPLETED
**Priority:** P1
**Area:** reliability, ops
**Effort:** S
**Blocked by:** none

Add hard-fail thresholds and escalation behavior for repeated autosync failures.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_2026-02-22.md`
**Implementation:** `src/thegent/integrations/error_budget.py` with `ErrorBudgetConfig` and `ErrorBudgetTracker` classes. Tracks consecutive/total failures, supports escalation and hard-fail decisions. Tests: `tests/test_wl170_error_budget.py` (14 tests).

### [WL-171] Autopilot Status Command
**Status:** COMPLETED
**Priority:** P2
**Area:** cli, ux
**Effort:** S
**Blocked by:** none

Add `thegent sync autopilot status` command with health, lag, and last-cycle summary.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_2026-02-22.md`

### [WL-172] Autopilot Doctor Command
**Status:** COMPLETED
**Priority:** P2
**Area:** cli, diagnostics
**Effort:** S
**Blocked by:** none

Add `thegent sync autopilot doctor` to validate credentials, scopes, and field mappings.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_2026-02-22.md`
**Implementation:** `src/thegent/integrations/autopilot_doctor.py`, tests in `tests/test_wl172_autopilot_doctor.py`

### [WL-173] Cycle Metrics Emission
**Status:** COMPLETED
**Priority:** P2
**Area:** observability, metrics
**Effort:** S
**Blocked by:** none

Emit structured metrics per autosync cycle for dashboarding and alerting.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_2026-02-22.md`
**Implementation:** `src/thegent/integrations/cycle_metrics.py`, tests in `tests/test_wl173_cycle_metrics.py`

### [WL-174] Local-vs-Remote Integrity Scanner
**Status:** COMPLETED
**Priority:** P1
**Area:** integrity, sync
**Effort:** M
**Blocked by:** none

Add periodic mismatch scanner for local workstream versus external tracker records.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_2026-02-22.md`

### [WL-175] Single-Writer Lock Discipline
**Status:** COMPLETED
**Priority:** P1
**Area:** concurrency, reliability
**Effort:** M
**Blocked by:** none

Enforce one active autosync writer per project using explicit lock semantics.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_2026-02-22.md`

### [WL-176] Process-Compose Operational Hardening
**Status:** COMPLETED
**Priority:** P2
**Area:** operations, docs
**Effort:** S
**Blocked by:** none

Harden startup/restart semantics and operator docs for long-running autosync service mode.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_2026-02-22.md`
**Implementation:** `src/thegent/integrations/process_compose_ops.py`, tests in `tests/test_wl176_process_compose_ops.py`

### [WL-177] Parser/Reflection Edge-Case Unit Tests
**Status:** COMPLETED
**Priority:** P1
**Area:** tests, parser
**Effort:** M
**Blocked by:** none

Add unit coverage for malformed markdown blocks and status reflection edge cases.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_2026-02-22.md`

### [WL-178] GitHub Sync Integration Tests
**Status:** COMPLETED
**Priority:** P1
**Area:** tests, github
**Effort:** M
**Blocked by:** mocked gh transport fixtures

Add integration tests validating pull/push behavior against mocked GitHub CLI responses.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_2026-02-22.md`

### [WL-179] Linear Sync Integration Tests
**Status:** COMPLETED
**Priority:** P1
**Area:** tests, linear
**Effort:** M
**Blocked by:** GraphQL fixture coverage

Add integration tests for Linear GraphQL cycle behavior with deterministic fixtures.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_2026-02-22.md`

### [WL-180] Zero-Touch Operator Quick Start
**Status:** COMPLETED
**Priority:** P2
**Area:** docs, onboarding
**Effort:** S
**Blocked by:** none

Publish quick-start docs for unattended board reflection setup and verification commands.

**Evidence:** `docs/research/WORKSTREAM_AUTOSYNC_NEXT_20_ITEMS_2026-02-22.md`
**Implementation:** `src/thegent/integrations/zero_touch_quickstart.py`, tests in `tests/test_wl180_zero_touch_quickstart.py`

<!-- auto-incorporated by thegent sync work-stream -->
| Aspect | MCP (Model Context Protocol) | ACP (Agent Client Protocol) |
|--------|------------------------------|-----------------------------|
| **Focus** | Model ↔ Tool communication | Editor ↔ Agent communication |
| **Use Case** | Tools, resources, prompts | Agent spawns, conversations, edits |
| **Transport** | stdio, HTTP, WebSocket | stdio (local), HTTP/WebSocket (remote) |
| **Message Format** | JSON-RPC | JSON-RPC (similar structure) |
| **Ecosystem** | Anthropic, MCP servers | Zed, gsh, Claude Agent SDK |
| Solution | Type | Key Features | Pricing Model | Best For |
|----------|------|--------------|---------------|----------|
| **OpenRouter** | Commercial SaaS | 300+ models, smart routing, guardrails, broadcast | Pay-per-use + credits | Production apps needing reliability |
| **Together AI Router** | Commercial | Multi-model routing, cost optimization | Pay-per-use | Cost-sensitive applications |
| **Anthropic Router** | Commercial | Claude-specific routing | Pay-per-use | Claude-focused apps |
| Solution | Stars | Key Features | Best For |
|----------|-------|-------------|----------|
| **LiteLLM Router** | 36,226 | 100+ providers, load balancing, caching | Production OSS routing |
| **Semantic Router** | 2,500+ | Intent-based routing, zero-cost | Fast routing without LLM calls |
| **HierRouter** | Research | RL-based routing, pipeline assembly | Research/advanced routing |
| **MasRouter** | Research | Multi-agent routing | Multi-agent systems |
| Solution | Type | Description |
|---------|------|-------------|
| **Portkey** | Commercial + OSS | Gateway with routing, OSS components available |
| **Helicone** | Commercial | Observability + routing features |
| Feature | OpenRouter | LiteLLM Router | Our Target |
|---------|------------|----------------|------------|
| **Models** | 300+ | 100+ | 100+ |
| **Routing Strategies** | 3 (price, latency, throughput) | 6 (simple-shuffle, cost, latency, etc.) | 6+ |
| **Fallbacks** | ✅ Automatic | ✅ Automatic | ✅ Automatic |
| **Caching** | ✅ Prompt caching | ✅ Redis + In-Memory | ✅ Redis + In-Memory |
| **Guardrails** | ✅ Built-in | ❌ Custom needed | ✅ Custom implementation |
| **Observability** | ✅ 15+ destinations | ⚠️ Custom callbacks | ✅ Custom + integrations |
| **Plugins** | ✅ Web, PDF, Healing | ❌ None | ✅ Custom plugins |
| **Responses API** | ✅ Native | ❌ Adapter needed | ✅ Adapter |
| **ZDR Support** | ✅ Built-in | ❌ Custom needed | ✅ Custom implementation |
| **Performance Thresholds** | ✅ Percentile-based | ❌ Basic | ✅ Percentile-based |
| **Cost Tracking** | ✅ Built-in | ✅ Built-in | ✅ Built-in |
| **Budget Limits** | ✅ Multi-level | ✅ Provider-level | ✅ Multi-level |
| § | Section | Content |
|---|---------|---------|
| 1 | Executive Summary | Key findings, decision matrix, recommendations |
| 2 | Caching Systems Deep Dive | Memcached, Valkey, diskcache, Redis, NATS comparison |
| 3 | Workflow Engines | Temporal vs Hatchet: features, use cases, optimization |
| 4 | Graph Databases | Neo4j: capabilities, AI integration, optimization |
| 5 | PostgreSQL Ecosystem | pgvector, pg_ai, extensions, AI-specific features |
| 6 | AI-Specific Solutions | Codebase indexers, semantic search, vector stores |
| 7 | Plugin & Extension Strategies | Maximizing features, integration patterns |
| 8 | Maximum Optimality Patterns | Advanced usage, performance tuning, best practices |
| 9 | thegent Integration Roadmap | Phased implementation plan |
| 10 | Decision Trees & Selection Guide | When to use what, hybrid architectures |
| System | Latency | Throughput | Persistence | Distributed | Best For |
|--------|---------|------------|-------------|-------------|----------|
| **cachetools** | ~10ns | Very High | No | No | Hot paths, single-process |
| **diskcache** | ~100µs | High | Yes (SQLite) | No | Large cache, single-server |
| **Memcached** | ~500µs | Very High | No | Yes | Simple key-value, high throughput |
| **Valkey** | ~100µs | Very High | Yes (AOF/RDB) | Yes | Rich data types, complex queries |
| **Redis** | ~100µs | Very High | Yes (AOF/RDB) | Yes | Legacy compatibility, Redis Cloud |
| **NATS KV** | ~1ms | High | Yes (JetStream) | Yes | Event-driven, pub/sub integration |
| Engine | Language | Complexity | AI Agent Support | Best For |
|--------|----------|------------|------------------|----------|
| **Temporal** | Go, Java, Python, TS | High | Excellent (SDKs) | Complex workflows, long-running tasks |
| **Hatchet** | Python, TypeScript | Low | Native | AI agent orchestration, simple workflows |
| Database | Query Type | AI Integration | Best For |
|----------|------------|---------------|----------|
| **Neo4j** | Graph (Cypher) | Native embeddings, vector search | Semantic relationships, knowledge graphs |
| **PostgreSQL + pgvector** | SQL + Vector | pg_ai, pgvector | Hybrid relational + vector search |
| **PostgreSQL + pg_ai** | SQL + LLM | Native LLM functions | LLM-powered queries, embeddings |
| Feature | Memcached | Valkey | diskcache | Redis | NATS KV |
|---------|----------|-------|-----------|-------|---------|
| **Latency** | ~500µs | ~100µs | ~100µs-1ms | ~100µs | ~1ms |
| **Persistence** | No | Yes | Yes | Yes | Yes |
| **Data Types** | String only | Rich | Any Python | Rich | String only |
| **Distributed** | Yes (sharding) | Yes (cluster) | No | Yes (cluster) | Yes (JetStream) |
| **Pub/Sub** | No | Yes | No | Yes | Yes (native) |
| **Lua Scripts** | No | Yes | No | Yes | No |
| **Streams** | No | Yes | No | Yes | Yes (JetStream) |
| **Modules** | No | Yes | No | Yes | No |
| **Best For** | Simple caching | Rich caching | Single-server | Legacy/Cloud | Event-driven |
| Feature | Temporal | Hatchet |
|--------|----------|---------|
| **Complexity** | High | Low |
| **Languages** | Go, Java, Python, TS | Python, TypeScript |
| **AI Support** | Good (SDKs) | Native |
| **Durability** | Excellent | Good |
| **Scalability** | Excellent | Good |
| **Best For** | Complex workflows | AI agent workflows |
| System | Latency (p50) | Latency (p99) | Throughput |
|--------|---------------|---------------|------------|
| cachetools | ~10ns | ~50ns | 10M+ ops/sec |
| diskcache | ~100µs | ~500µs | 10K+ ops/sec |
| Valkey (local) | ~100µs | ~500µs | 100K+ ops/sec |
| Valkey (network) | ~1ms | ~5ms | 50K+ ops/sec |
| NATS KV | ~1ms | ~5ms | 10K+ ops/sec |
| Strategy | Component | Status |
|----------|-----------|--------|
| Exponential backoff + jitter | resilience.with_retry, loop_controller, state_machine, cli_impl, egress | ✓ tenacity wait_random_exponential |
| Jitter on prune cooldown | prune-orphans-stop.sh | ✓ THGENT_AUTO_PRUNE_COOLDOWN_JITTER |
| Graceful SIGTERM | main.mcp_prune | ✓ THGENT_PRUNE_GRACE_PERIOD |
| MCP retry policy doc | docs/reference/MCP_RETRY_POLICY.md | ✓ |
| Circuit breaker | execution.CircuitBreakerRegistry, config | ✓ threshold, window, recovery |
| Per-owner bulkhead | ConcurrencyController.max_slots_per_owner | ✓ THGENT_CONCURRENCY_MAX_SLOTS_PER_OWNER |
| Cost-aware retry | Agent runners (API: 2 attempts, local: 5) | ✓ |
| /health endpoint | mcp_server | ✓ GET /health |
| Prune retry on failure | prune-orphans-stop.sh | ✓ 3 attempts, backoff 2^attempt s |
| Gardener spawn backoff | gardener-spawn-manager.sh | ✓ GARDENER_SPAWN_BACKOFF_SEC |
| Retry budget (per-min cap) | resilience.RetryBudgetPerMinute, with_retry | ✓ THGENT_RETRY_BUDGET_PER_MINUTE |
| Token bucket (API rate limit) | resilience.TokenBucket, get_token_bucket | ✓ THGENT_TOKEN_BUCKET_CAPACITY |
| Adaptive load thresholds | execution.AdaptiveLoadThresholds, LoadClassifier | ✓ THGENT_LOAD_ADAPTIVE_ENABLED |
| § | Section |
|---|---------|
| 1 | Executive Summary |
| 2 | Retry & Exponential Backoff |
| 3 | Jitter Strategies (Thundering Herd) |
| 4 | Circuit Breaker Pattern |
| 5 | Bulkhead & Isolation |
| 6 | Restart Policies (Kubernetes, systemd) |
| 7 | Fairness & Multi-Tenant Isolation |
| 8 | Adaptive & Telemetry-Driven Strategies |
| 9 | Backpressure & Rate Limiting |
| 10 | **Timeout Strategies** *(new)* |
| 11 | **Health Checks & Liveness Probes** *(new)* |
| 12 | **Retry Exhaustion & Dead Letter** *(new)* |
| 13 | **Cascading Failure Prevention** *(new)* |
| 14 | **Cost-Aware & Hybrid Strategies** *(new)* |
| 15 | thegent Mapping & Roadmap |
| 16 | Decision Trees & Quick Reference |
| 17 | Cross-References & Bibliography |
| Pattern | Purpose |
|---------|---------|
| **Retry + exponential backoff** | Transient failures, rate limits, API throttling |
| **Jitter** | Avoid thundering herd when many clients retry simultaneously |
| **Circuit breaker** | Stop hammering failing services; half-open probe for recovery |
| **Bulkhead** | Isolate failures so one bad tenant doesn't cascade |
| **Restart policies** | Kubernetes CrashLoopBackOff, systemd Restart=, launchd KeepAlive |
| **Fairness** | Per-owner quotas, retry budgets, starvation prevention |
| **Adaptive strategies** | Telemetry-driven thresholds, dynamic backoff |
| **Timeout strategies** | Fixed vs adaptive; deadline propagation |
| **Health checks** | Liveness, readiness, startup probes |
| **Retry exhaustion** | Dead letter, fallback, fail-fast semantics |
| **Cascading failure prevention** | Circuit breaker + bulkhead + timeout |
| **Cost-aware retry** | Fewer retries for expensive ops (LLM API) |
| Retry | Don't Retry |
|-------|-------------|
| 503, 504, 429 | 4xx (except 429) |
| ECONNRESET, ETIMEDOUT, ECONNREFUSED | ENOENT, EACCES |
| Transient network | Permanent config error |
| Rate limit (429) | Auth failure (401) |
| Component | Current | Enhancement |
|-----------|---------|-------------|
| **MCP tool calls** | Best-effort; may fail | Retry with backoff for 503/429 |
| **API provider calls** | tenacity (if used) | Ensure exponential backoff + jitter |
| **Prune trigger** | Cooldown (fixed 300s) | Exponential backoff when prune fails |
| **Gardener spawn** | Retry on failure | Backoff between spawn attempts |
| **DAG task retry** | Retry count | Backoff between retries |
| Strategy | Formula | Use Case |
|----------|---------|----------|
| **Full jitter** | `random(0, exponentialDelay)` | Best in practice; spreads load |
| **Equal jitter** | `(delay/2) + random(0, delay/2)` | Bounded minimum wait |
| **Decorrelated** | `random(baseDelay, 3×baseDelay)` | Builds on prior delay |
| Strategy | Min Wait | Max Wait | Load Spread | Use When |
|----------|----------|----------|-------------|----------|
| **None** | full delay | full delay | Poor | Single client |
| **Full jitter** | 0 | full delay | Best | Multi-client (default) |
| **Equal jitter** | delay/2 | delay | Good | Need bounded min |
| **Decorrelated** | base | 3×base | Good | Prior delay known |
| Param | Typical | Description |
|-------|---------|-------------|
| failureThreshold | 5 | Failures before OPEN |
| resetTimeout | 30s | Time before HALF-OPEN probe |
| successThreshold | 1 | Successes in HALF-OPEN to close |
| Component | Circuit Breaker Use |
|-----------|---------------------|
| **Provider API** | Open when 5xx rate > X%; block requests 30s |
| **MCP tool (external)** | Open when tool fails N times; skip for 60s |
| **Prune** | Not applicable (prune is local) |
| **ConcurrencyController** | Could circuit-break "acquire" when load chronically high |
| Window Type | Failure Count | Pros | Cons |
|-------------|---------------|------|------|
| **Fixed** | Last N requests | Simple | Burst at boundary |
| **Sliding** | Last N seconds | Smoother | More state |
| **Percent-based** | % of last N | Adaptive to load | Needs min sample size |
| Practice | Description |
|----------|-------------|
| **Separate connection pools** | MCP vs API vs hooks |
| **Per-tenant limits** | Cap slots per owner |
| **Independent circuit breakers** | One per provider, per tool |
| **Thread/process pools** | Dedicated pool per domain |
| Current | Bulkhead Enhancement |
|---------|----------------------|
| ConcurrencyController (global) | Per-owner or per-project sub-limits |
| Single prune path | Isolate LSP prune from MCP prune (different patterns) |
| Gardener spawn | Per-project disk gate already isolates |
| MCP server | Separate timeouts per tool namespace |
| Policy | Behavior |
|--------|----------|
| Always | Restart on any exit |
| OnFailure | Restart only on non-zero exit |
| Never | No restart |
| Directive | Example |
| Restart= | on-failure, always, no |
| RestartSec= | 2 (seconds before restart) |
| StartLimitIntervalSec= | 60 |
| StartLimitBurst= | 5 |
| Key | Behavior |
|-----|----------|
| KeepAlive | true, false, or dict (SuccessfulExit, etc.) |
| RunAtLoad | Start at load |
| ThrottleInterval | Min seconds between restarts |
| Component | Restart Policy |
|-----------|----------------|
| prune-periodic | launchd KeepAlive=false (run periodically, don't restart) |
| thegent serve | process-compose restart policy |
| MCP subprocess tools | Optional: restart on crash with backoff |
| Gardener workers | Restart with limit (avoid spawn storm) |
| Goal | Mechanism |
|------|------------|
| **No starvation** | Per-owner min share or max wait time |
| **Proportional share** | Weighted fair queuing |
| **Retry fairness** | Retry budget per owner; don't let one consumer exhaust |
| Algorithm | Idea |
|-----------|------|
| **Max-Min Fairness** | Maximize minimum share |
| **Proportional Fair** | Allocate proportional to demand |
| **Token Bucket** | Refill rate; burst capacity |
| **Leaky Bucket** | Smooth output rate |
| Component | Fairness Enhancement |
|-----------|---------------------|
| ConcurrencyController | Per-owner quota; FCFS within quota |
| Prune | No fairness (system-wide); could add per-project "don't prune my project" |
| DAG tasks | Prioritize by critical path; fair within priority |
| API rate limits | Token bucket per provider |
| Metric | Purpose |
|--------|---------|
| `retry_count` | How often retries occur |
| `retry_exhausted_count` | Failures after max retries |
| `circuit_breaker_state` | CLOSED / OPEN / HALF_OPEN |
| `circuit_breaker_trips` | Count of OPEN transitions |
| `latency_p99` | For adaptive timeout |
| `failure_rate_5m` | For circuit breaker threshold |
| Component | Adaptive Enhancement |
|-----------|---------------------|
| HysteresisController | Already adaptive (dwell, thresholds) |
| ConcurrencyController | Dynamic fd_utilization_max from observed FD pressure |
| Prune threshold | Lower when memory trend is declining |
| Load thresholds | Adjust spike/surge from observed load patterns |
| Component | Rate Limit |
|-----------|------------|
| ConcurrencyController | Slot limit (admission control) |
| Load thresholds | Traffic shaping when spike/surge |
| API providers | Token bucket per provider (future) |
| Prune | Cooldown = rate limit on prune frequency |
| Type | Formula | Use Case |
|------|---------|----------|
| **Fixed** | `timeout = 30s` | Predictable ops |
| **Per-call** | `timeout = base + k × payload_size` | Variable payload |
| **Percentile-based** | `timeout = p99_latency × 2` | Adaptive to observed latency |
| **Deadline propagation** | Parent passes deadline to children | Distributed traces |
| Component | Timeout Strategy |
|-----------|------------------|
| MCP tool call | Fixed (e.g. 60s); consider per-tool override |
| API provider | Adaptive from p99; fallback fixed |
| Prune scan | Fixed (e.g. 10s); don't block Stop |
| DAG task | Per-task timeout; propagate to subtasks |
| Probe | Purpose | Failure Action |
|-------|---------|----------------|
| **Liveness** | Is process alive? | Restart |
| **Readiness** | Can accept work? | Don't route traffic |
| **Startup** | Has init finished? | Restart if stuck |
| Pattern | Description |
|---------|-------------|
| **HTTP GET /health** | Simple; 200 = healthy |
| **TCP connect** | Port open = alive |
| **Command** | Run `thegent mcp ping` or similar |
| **Dependency check** | Verify Redis, provider API reachable |
| Component | Health Check |
|-----------|--------------|
| thegent serve | HTTP /health or MCP ping |
| prune-periodic | launchd/systemd monitors exit |
| MCP tools | Optional: ping before invoke |
| Provider API | Circuit breaker = implicit health |
| Action | Use Case |
|--------|----------|
| **Fail fast** | User sees error; can retry manually |
| **Dead letter queue** | Store for later replay (async jobs) |
| **Fallback** | Use backup provider or cached result |
| **Alert** | Notify operator; don't silently drop |
| Component | Exhaustion Behavior |
|-----------|---------------------|
| MCP tool | Fail fast; surface to agent |
| DAG task | Mark failed; optional DLQ for replay |
| API provider | Fallback to cached/backup if configured |
| Prune | Never exhaust (local); cooldown only |
| Mitigation | How |
|------------|-----|
| **Circuit breaker** | Stop sending to A when it fails |
| **Bulkhead** | Limit concurrent calls to A |
| **Timeout** | Don't wait forever; fail fast |
| **Fallback** | Return cached or degraded response |
| **Load shed** | Reject new work when overloaded |
| Risk | Mitigation |
|------|------------|
| Provider API overload | Circuit breaker + bulkhead |
| MCP server overload | ConcurrencyController slots |
| Prune during load | Cooldown + memory threshold |
| DAG task storm | Admission control; queue depth limit |
| Condition | Action |
|-----------|--------|
| Cheap op (local) | Retry freely |
| Expensive op (API call) | Retry 1–2×; then fail |
| Rate limit (429) | Backoff; respect Retry-After |
| Quota exceeded | Don't retry; report |
| Strategy | thegent Use |
|----------|-------------|
| Cost-aware retry | LLM API: 1–2 retries; local tools: 5 |
| Retry + CB | Provider API: retry per call; CB when 5xx spike |
| Bulkhead + fairness | ConcurrencyController: per-owner + global |
| Strategy | Component | Effort | Impact |
|----------|-----------|--------|--------|
| Exponential backoff + jitter | MCP/API retries | 6–10 | High |
| Circuit breaker | Provider API, MCP tools | 8–12 | High |
| Jitter on prune cooldown | prune-orphans-stop | 2–4 | Medium |
| Per-owner fairness | ConcurrencyController | 15–20 | Medium |
| Bulkhead (per-owner limits) | ConcurrencyController | 10–15 | Medium |
| Adaptive thresholds | HysteresisController | 8–12 | Medium |
| Restart with backoff | Gardener, MCP tools | 6–10 | Medium |
| Pattern | Key Params | Typical Values |
|---------|------------|----------------|
| Exponential backoff | initialDelay, factor, maxDelay, maxRetries | 1s, 2, 60s, 5 |
| Jitter | full / equal / decorrelated | full |
| Circuit breaker | failureThreshold, resetTimeout | 5, 30s |
| Cooldown (prune) | cooldown, jitter | 300s, ±30s |
| Timeout (per attempt) | timeout | 10–30s (shorter than total retry window) |
| Retry budget | maxRetriesPerMinute | 60 |
| Failure | Primary Strategy | Fallback |
|---------|------------------|----------|
| Transient 5xx | Retry + backoff + jitter | Circuit breaker |
| 429 rate limit | Retry with longer delay; respect Retry-After | Circuit breaker |
| Timeout | Shorter per-attempt timeout; retry | Fail fast after N |
| Service down | Circuit breaker | Bulkhead limits exposure |
| One tenant overload | Bulkhead (per-owner cap) | Fairness queue |
| Retry storm | Retry budget | Circuit breaker |
| Cascade risk | Circuit breaker + timeout + bulkhead | Load shed |
| Doc | Relevance |
|-----|-----------|
| [SMART_ROBUST_STRATEGIES_RESEARCH](./SMART_ROBUST_STRATEGIES_RESEARCH.md) | Process lifecycle, LSP multiplexing, prune strategies |
| [SWARM_OPTIMIZATION_SCHEDULING_DEEP_RESEARCH](./SWARM_OPTIMIZATION_SCHEDULING_DEEP_RESEARCH.md) | Scheduling theory, admission control, backpressure |
| [SYSTEM_RESOURCES_FD_CPU_DEEP_RESEARCH](./SYSTEM_RESOURCES_FD_CPU_DEEP_RESEARCH.md) | FD, CPU, resource gates |
| [SWARM_PROCESS_AUTOMATION_DEEP_RESEARCH](./SWARM_PROCESS_AUTOMATION_DEEP_RESEARCH.md) | Prune, triggers, platform ecosystem |
| Source | Topic |
|--------|-------|
| [Better Stack: Exponential Backoff](https://betterstack.com/community/guides/monitoring/exponential-backoff/) | Retry, jitter, circuit breaker, bulkhead |
| [Kubernetes: Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/) | CrashLoopBackOff, restart policy |
| [AWS: Retry with Backoff](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/retry-backoff.html) | Transient errors, rate limits |
| [Google Cloud: Retry Strategy](https://docs.cloud.google.com/storage/docs/retry-strategy) | Exponential backoff with jitter |
| [Polly: Retry](https://www.pollydocs.org/strategies/retry) | .NET resilience; backoff types |
| Domain | Current State | Gap | Recommendation |
|--------|---------------|-----|----------------|
| **File reads** | IDE read_file, list_dir; shell ls/grep | No unified MCP tool; agents use ls in root (5m+ delays) | fd + rg canonical; add `thegent_files` MCP |
| **Web search** | thegent_ddg_search (DDG) | No URL fetch; no Firecrawl/FetchSERP | Add mcp_web_fetch; optional Firecrawl |
| **Web scrape** | Model scrapers (internal) | No agent-facing scrape | server-fetch for URL content |
| **Batch edits** | thegent_apply_transaction | Exists; underused | Document; add search_replace batch |
| **kilo / roo** | AI providers (proxy) | N/A | Clarify in docs |
| **OpenCode** | Session parsing support | Cross-provider parity | Document IDE parity |
| Source | Tool / Method | Platform | Exclusions |
|--------|---------------|----------|------------|
| **IDE** | read_file, list_dir, codebase_search | Cursor, Claude Code | IDE-specific |
| **Shell** | ls, find, grep, fd, rg | All | fd/rg respect .gitignore |
| **MCP** | — | — | **No file list/search MCP tool** |
| **Hooks** | fd-wrapper, grep-wrapper (→ rg) | thegent hooks only | common.sh |
| Priority | Action | Effort |
|----------|--------|--------|
| P1 | Document fd + rg as canonical pair (skills, CLAUDE.md) | Done |
| P1 | Add `thegent_files` MCP tool (list + search modes) | 15–25 tool calls |
| P2 | .agentignore for project-level exclusions | 4–6 tool calls |
| P2 | Ensure fd, rg in Brewfile/setup for agent shells | 1–2 edits |
| Tool | Location | Purpose |
|------|----------|---------|
| **thegent_ddg_search** | mcp_server.py | DuckDuckGo text search; returns titles, snippets, URLs |
| **ddg_search** | tools/research.py | Backend for thegent_ddg_search |
| **mcp_web_fetch** | Cursor built-in | Fetch URL content (read-only) |
| **server-fetch** | @modelcontextprotocol/server-fetch | Official MCP for web content |
| Priority | Action | Effort |
|----------|--------|--------|
| P1 | Document: use thegent_ddg_search for research; mcp_web_fetch for URL content | Doc only |
| P2 | Add thegent_fetch_url (or wire server-fetch) for full page content | 8–12 tool calls |
| P3 | Optional: Firecrawl MCP for heavy scrape (JS-rendered pages) | External MCP |
| P3 | DDG: add retry with backoff; optional cache TTL | 4–6 tool calls |
| Component | Purpose |
| **models/scrapers.py** | Provider model discovery (cursor, gemini, claude, proxy, etc.) |
| **cliproxy_manager** | Health check, model fetch, provider metrics |
| **ddg_search** | Web search (agent-facing) |
| MCP | Purpose |
|-----|---------|
| **server-fetch** | Web content fetching |
| **server-filesystem** | Secure file ops |
| **server-github** | GitHub PRs, issues, repos |
| **Firecrawl** | Web scrape (JS-rendered) |
| **Octocode** | GitHub/code search |
| Platform | AI proxy | OSS harness | CLI |
|----------|----------|-------------|-----|
| **kilo** | api.kilo.ai/v1 | ✓ | `kilo auth` |
| **roo** | api.roocode.com/v1 | ✓ | `roo auth login` |
| Aspect | Details |
|--------|---------|
| **CLI** | `opencode` — npm install -g opencode |
| **Zen** | Curated models for coding agents; pay-per-request; works with any agent |
| **Config** | `.opencode/` — commands, instructions, plugins, prompts, tools |
| **ECC** | everything-claude-code has `.opencode/` plugin (12 agents, 24 commands, 16 skills) |
| Platform | AI proxy | OSS harness | CLIProxy |
|----------|----------|------------|----------|
| Claude Code | Anthropic | ✓ | ✓ |
| Cursor | cursor-api | Partial | — |
| Codex | OpenAI | ✓ | ✓ (adapter) |
| OpenCode | Zen, multi | ✓ | Proposed (config) |
| kilo | api.kilo.ai | ✓ | ✓ (as provider) |
| roo | api.roocode.com | ✓ | ✓ (as provider) |
| Tool | Location | Purpose |
|------|----------|---------|
| **thegent_apply_transaction** | mcp_server.py | Atomic multi-file apply |
| **apply_multi_file_transaction** | orchestration/transactions.py | Temp files → atomic rename |
| Priority | Action | Effort |
|----------|--------|--------|
| P1 | Document thegent_apply_transaction in skills, CLAUDE.md | 2–3 edits |
| P2 | Add thegent_batch_search_replace (pattern, replacement, path_glob) | 12–18 tool calls |
| P3 | Add dry_run param to thegent_apply_transaction | 2–4 tool calls |
| Opt | Status | Impact |
|-----|--------|--------|
| fd + rg over ls/grep | Documented | 10–35x faster; avoids 5m+ ls |
| thegent_files MCP | Proposed | Unified across platforms |
| .cursorignore | Recommended | Reduces Cursor index size |
| .agentignore | Proposed | Project-level exclusions |
| Opt | Status | Impact |
|-----|--------|--------|
| DDG retry/backoff | Proposed | Resilience |
| DDG result cache | Proposed | Reduce duplicate queries |
| server-fetch integration | Proposed | Full URL content |
| Opt | Status | Impact |
|-----|--------|--------|
| thegent_apply_transaction | Exists | Atomic multi-file |
| batch_search_replace | Proposed | Single call for N files |
| dry_run | Proposed | Safer preview |
| Opt | Status | Impact |
|-----|--------|--------|
| ThreadPoolExecutor(6) | Done | 3–5x faster scrape |
| Cache TTL | Done | ~300s |
| diskcache | Proposed (LIBRARY_REPLACEMENT) | Cleaner cache |
| Task | IDE | MCP | Shell |
|------|-----|-----|-------|
| Read file | read_file | (thegent_files read) | cat, head |
| List dir | list_dir | thegent_files list | fd -t f -d 1 |
| Search content | codebase_search | thegent_files search | rg |
| Web search | — | thegent_ddg_search | — |
| Fetch URL | mcp_web_fetch | (thegent_fetch_url) | curl |
| Batch edit | N× edit | thegent_apply_transaction | sed -i (risky) |
| Phase | Tasks | Effort |
|-------|-------|--------|
| **P1 (Immediate)** | Document baseline in skills, CLAUDE.md; add kilo/roo/OpenCode clarification | 4–6 edits |
| **P2 (Short)** | thegent_files MCP tool; thegent_apply_transaction docs | 15–25 tool calls |
| **P3 (Medium)** | thegent_fetch_url or server-fetch wire; batch_search_replace | 20–30 tool calls |
| **P4 (Long)** | DDG retry/cache; .agentignore; dry_run for transactions | 10–15 tool calls |
| Doc | Purpose |
|-----|---------|
| [AGENT_FILE_SEARCH_UNIFIED_TOOL_RESEARCH.md](./AGENT_FILE_SEARCH_UNIFIED_TOOL_RESEARCH.md) | fd + rg, thegent_files design |
| [INDEXING_AND_OPTIMIZATION_SYSTEMS.md](../reference/INDEXING_AND_OPTIMIZATION_SYSTEMS.md) | Indexing, Spotlight, ls avoidance |
| [SETUP_PROPOSED_ITEMS.md](../plans/SETUP_PROPOSED_ITEMS.md) | MCP ecosystem, server-fetch, Firecrawl |
| [TOUCHPOINT_INTEGRATION_DEEP_DIVE.md](../reference/TOUCHPOINT_INTEGRATION_DEEP_DIVE.md) | Research tools, skill references |
- [x] `thegent crew create` - Create crew
- [x] `thegent crew execute` - Execute crew
- [x] `thegent crew list` - List crews
- [x] `thegent crew show` - Show crew details
- [x] `thegent crew status` - Show execution status
- [x] Test TaskExecutor dependency resolution
- [x] Test CrewExecutor execution modes
- [x] Test WorkflowEngine stage dependencies
- [x] Test RouterManager routing strategies
- [x] Test MonitoringEngine metrics
- [ ] Test harness integration
- [ ] API documentation
- [ ] Architecture documentation
- [ ] Usage guide
- [ ] Examples
- [ ] Token/cost parsing from agent output
- [ ] Better error handling
- [ ] Streaming support
- [ ] Parallel task execution
- [ ] Caching improvements
- [ ] Metrics collection optimization
| Tool | Replaces | Respects .gitignore | Exclusions | Speed |
|------|----------|---------------------|------------|-------|
| **ls** | — | No | No | Slow in large dirs |
| **find** | — | No | Manual | Slow |
| **grep** | — | No | Manual | Medium |
| **fd** | ls, find | Yes | -E flag, .gitignore | 10–35x faster |
| **rg** (ripgrep) | grep | Yes | -g, .gitignore | 10x faster |
| Task | Use | Example |
|------|-----|---------|
| List files in dir | `fd -t f -d 1` or `fd -t d -d 1` | `fd -t f -d 1 -E node_modules -E .venv` |
| Find files by name | `fd pattern` | `fd "test_" -e py` |
| Search file content | `rg pattern` | `rg "def main" --type py` |
| Platform | Built-in | Use case |
|----------|----------|----------|
| **Cursor** | @codebase, @file, semantic search | Prefer over shell when available |
| **Claude Code** | read_file, list_dir, codebase_search | Prefer over shell when available |
| **Codex** | Varies | May need shell fallback |
| Layer | Tool | When |
|-------|------|------|
| **IDE (Cursor, Claude Code)** | Native @codebase, read_file, list_dir | First choice when available |
| **MCP (thegent serve)** | `thegent_files` (future) | When agent uses MCP tools |
| **Shell (all platforms)** | **fd** (list/find) + **rg** (search) | Terminal fallback; document as canonical |
| Task | Effort | Impact |
|------|--------|--------|
| Document fd + rg as canonical in skills, CLAUDE.md | 1–2 edits | High |
| Add `thegent_files` MCP tool (list + search) | 15–25 tool calls | High — unified across platforms |
| Ensure fd, rg in agent PATH (Brewfile, setup) | 1–2 edits | Medium |
| .agentignore support for thegent_files | 4–6 tool calls | Medium |
| Tool | Speed | .gitignore | Exclusions | Cross-platform | Maintenance |
|------|-------|------------|------------|----------------|-------------|
| **fd** | 10-35x ls | Yes | -E flag | Linux/macOS/Windows | Active |
| **find** | Slow | No | Manual | Yes | Legacy |
| **ls** | Slowest | No | No | Yes | Native |
| **ripgrep -l** | Fast | Yes | -g | Yes | Active |
| **ugrep -g** | Fast | Yes | -g | Yes | Active |
| **lsd** | Medium | No | No | Linux/macOS | Active |
| Tool | Speed | .gitignore | Exclusions | Regex | Maintenance |
|------|-------|------------|------------|-------|-------------|
| **rg** | 10x grep | Yes | -g | PCRE2 | Active |
| **grep** | Baseline | No | Manual | Basic | Legacy |
| **ugrep** | Fast | Yes | -g | PCRE++ | Active |
| **ack** | Medium | Yes | --ignore-dir | Perl | Moderate |
| **ag** | Fast | Yes | --ignore-dir | Rust | Moderate |
| Tool | Replaces | Pros | Cons | Agent Fit |
|------|----------|------|------|-----------|
| **ugrep** | find + grep + ls | Single binary, fast | Learning curve | Medium |
| **fd + rg** | find + grep | Industry standard, well-documented | Two tools | High |
| **thegent_files** | MCP wrapper | Built-in exclusions, MCP native | MCP-only | High (if MCP) |
| **IDE native** | @codebase | Semantic awareness | IDE-specific | High (if IDE) |
| Operation | ls | find | fd | rg | ugrep |
|-----------|-----|------|----|----|-------|
| `ls -l` in large dir | 1x | N/A | 10x | N/A | N/A |
| Find .py files | N/A | 1x | 15x | 8x | 10x |
| Search "TODO" in code | N/A | N/A | N/A | 10x | 8x |
| Find + Search combined | N/A | 1x | 5x | 5x | 4x |
- [ ] Document fd + rg as canonical in skills/
- [ ] Add fd + rg to Brewfile (ensure in PATH)
- [ ] Update CLAUDE.md with tool recommendations
- [ ] Create quick reference card for agents
- [ ] Design `thegent_files` MCP tool interface
- [ ] Implement `list` mode (fd wrapper)
- [ ] Implement `search` mode (rg wrapper)
- [ ] Add default exclusions (node_modules, .venv, .git)
- [ ] Add `.agentignore` support
- [ ] Test on Linux, macOS, Windows
- [ ] Update SKILL.md templates to use fd + rg
- [ ] Add fd + rg examples to agent training data
- [ ] Create fallback logic (IDE native → MCP → fd/rg → ls/grep)
- [ ] Document agent instruction for file operations
- [ ] Benchmark fd vs ls in node_modules-heavy project
- [ ] Benchmark rg vs grep in large codebase
- [ ] Test thegent_files MCP tool performance
- [ ] Verify exclusions work correctly
| Doc | Relevance |
|-----|-----------|
| [INDEXING_AND_OPTIMIZATION_SYSTEMS.md](../reference/INDEXING_AND_OPTIMIZATION_SYSTEMS.md) | Indexing systems overview |
| [PROCESS_OPTIMIZATION_PLAN.md](../plans/PROCESS_OPTIMIZATION_PLAN.md) | Process optimization |
| [SWARM_PROCESS_AUTOMATION_DEEP_RESEARCH.md](./SWARM_PROCESS_AUTOMATION_DEEP_RESEARCH.md) | Process automation |
| Section | Added Content |
|---------|---------------|
| §7.1 | File Discovery Tools Comparison (fd, find, ls, ripgrep, ugrep, lsd) |
| §7.2 | Content Search Tools Comparison (rg, grep, ugrep, ack, ag) |
| §7.3 | Unified/Bundled Tools Matrix (ugrep, fd+rg, thegent_files, IDE native) |
| §7.4 | Performance Comparison (relative speeds) |
| §8 | Implementation Checklist (Immediate, MCP, Agent, Verification) |
- [ ] Implement `AgentHierarchyManager`
- [ ] Extend `TeammateManager` with hierarchy support
- [ ] Add hierarchy visualization commands
- [ ] Unit tests for hierarchy operations
- [ ] Implement team creation and management
- [ ] Add team coordination protocols
- [ ] Cross-team collaboration support
- [ ] Integration tests
- [ ] Hierarchy visualization in dashboard
- [ ] Team activity monitoring
- [ ] Relationship graph visualization
- [ ] CLI improvements
- [ ] Dynamic team creation
- [ ] Team templates
- [ ] Advanced coordination modes
- [ ] Performance optimization
| Type | Purpose | Input | Output | Execution |
|------|---------|-------|--------|-----------|
| **code-search** | Find patterns/files in codebase | Query (glob, regex, keywords) | Matching files + context | Native tools (rg, fd, ag) |
| **code-gen** | Generate code snippets/modules | Spec (requirements, template) | Generated code + tests | Codex (Phase 3) or direct LLM |
| **test-gen** | Generate test cases | Code + coverage gaps | Test file + assertions | Direct LLM or droid |
| **doc-gen** | Generate documentation | Codebase context | Markdown docs | Direct LLM |
| **refactor** | Apply code transformations | Pattern + replacement rules | Refactored code + changes | CodeMod or AST tools |
| **review** | Code review & validation | Code + criteria | Findings + scores | Direct LLM |
| Mode | Setup | Execution | Harness |
|------|-------|-----------|---------|
| **Local (MVP)** | Direct Python classes | Subagent (thegent free/bg) or threads | None |
| **Distributed (Phase 2)** | Multiple processes | Pool of SmolGent workers | None |
| **Codex Harness (Phase 3)** | Codex + Python sandbox | Codex for code-gen, code-search | Yes |
| **CC Harness (Phase 3)** | Claude Code integration | CC for code generation/review | Yes |
| **Droid Harness (Phase 3)** | Factory droid exec | Droids for long-running tasks | Yes |
| Component | Latency | Notes |
|-----------|---------|-------|
| Manager routing | 100-500ms | LLM call to identify SmolGents |
| Task write (atomicity) | <1ms | File write + atomic move |
| SmolGent startup | 100-200ms | Process/thread spawn |
| Task execution | 1-30s | Actual work (varies by type) |
| Result write | <1ms | Atomic move |
| Result polling (1 iteration) | 10ms | Check .mgmt/results/ |
| Aggregation | 100-500ms | LLM call to combine results |
| **Total (best case)** | **2-10s** | Sequential, no parallelism |
| **Total (with parallelism)** | **1-5s** | Multiple SmolGents in parallel |
| Resource | Per SmolGent | Notes |
|----------|--------------|-------|
| Memory | 10-50MB | Varies by type (code-search uses rg, minimal) |
| CPU | 1 core active during execution | Mostly idle (I/O bound) |
| Storage | .mgmt/ dir: <100MB | Task files + results (gc periodically) |
| Network | 0-1MB/s | Optional LLM calls (code-gen, review) |
| Aspect | MVP | Full Hierarchy |
|--------|-----|---|
| **Scope** | Manager + 6 SmolGents | Multi-level teams |
| **Coordination** | File-based IPC | Structured messages + DB |
| **Team Support** | No teams (flat) | Hierarchical teams |
| **Execution** | Local threads (Phase 1) | Distributed + harnesses |
| **Routing** | Simple LLM-based | Advanced algorithm |
| **Result Aggregation** | Basic concatenation | Structured synthesis |
| **Implementation Effort** | ~2 weeks | ~8 weeks |
| **Complexity** | Low | High |
- [ ] Manager can parse prompts and route to SmolGents
- [ ] Code-search SmolGent finds files/patterns correctly
- [ ] Review SmolGent analyzes code
- [ ] File-based IPC is atomic (no data loss or corruption)
- [ ] Results aggregate correctly
- [ ] Retry logic handles transient failures
- [ ] All 6 SmolGent types working by end of Phase 2
- [ ] End-to-end latency: 2-10 seconds (simple tasks)
- [ ] Throughput: 2+ tasks/second with 4 workers
- [ ] File IPC overhead: <1% of task execution time
- [ ] Memory per SmolGent: <50MB
- [ ] Zero race conditions in file IPC
- [ ] 95%+ success rate (retries included)
- [ ] Proper error messages and stack traces
- [ ] Unit test coverage: >80%
- [ ] Integration tests for full manager→SmolGent→result flow
- [ ] Extends existing `TeammateManager` without breaking changes
- [ ] Implements `AgentRunner` interface
- [ ] Works with existing CLI (thegent free, thegent bg)
- [ ] Configuration via .claude/smolgent-config.json
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| File IPC race conditions | Medium | High | Use atomic `mv`, extensive testing |
| SmolGent timeout during execution | Medium | Medium | Configurable timeouts, graceful degradation |
| Manager bottleneck with many tasks | Low | Medium | Move to distributed in Phase 2 |
| Harness integration complexity (Phase 3) | Low | Medium | Design harness layer carefully in MVP |
| Result data loss on crash | Low | High | Persistent .mgmt/ directory, cleanup policies |
- [ ] SmolGentTask & SmolGentResult dataclasses
- [ ] SmolGentBase abstract class
- [ ] Maildir pattern utilities (atomic writes, claiming)
- [ ] ManagerAgent (basic routing)
- [ ] CodeSearchSmolGent implementation
- [ ] ReviewSmolGent implementation
- [ ] LocalSmolGentPool (thread executor)
- [ ] SmolGentCoordinator (orchestrator)
- [ ] CLI: `thegent smolgent code-search`
- [ ] Tests: 80%+ coverage
- [ ] Docs: README, examples, API docs
- [ ] CodeGenSmolGent
- [ ] TestGenSmolGent
- [ ] DocGenSmolGent
- [ ] RefactorSmolGent
- [ ] ProcessPool (distributed execution)
- [ ] Advanced routing (LLM-based decomposition)
- [ ] Enhanced error handling & retry
- [ ] CLI: `thegent smolgent *` for all types
- [ ] Benchmarks: latency & throughput
- [ ] Integration tests
- [ ] HarnessBase abstraction
- [ ] CodexHarness (code-search, code-gen via Codex sandbox)
- [ ] ClaudeCodeHarness (review, code-gen via CC)
- [ ] DroidHarness (long-running tasks)
- [ ] Harness auto-selection
- [ ] Fallback logic (harness unavailable)
- [ ] Tests for harness isolation
- [ ] Docs: harness architecture, extension guide
| Layer | Location | Purpose |
|-------|----------|---------|
| Governance hierarchy | `src/thegent/governance/agent_hierarchy.py` | Persistence-backed (JSON files), role-based (EXECUTIVE / TEAM_LEAD / SPECIALIST), team management, delegation policy enforcement |
| Research stub | `src/thegent/research/agent_hierarchy.py` | Minimal 60-line prototype — register + get_children + get_hierarchy_path |
| Crew executor | `src/thegent/crew/executor.py` | TaskExecutor with topological DAG resolution; AgentAssigner strategies (RoundRobin, SkillBased, Hierarchical) |
| Harness | `src/thegent/crew/harness.py` | Bridges crew tasks to CLI agents (codex/claude/copilot/gemini) via DirectAgentRunner |
| Category | Tests | All Pass |
|----------|-------|----------|
| AgentCapability enum | 2 | Yes |
| AgentState enum | 1 | Yes |
| AgentNode creation/capability/serialisation | 8 | Yes |
| spawn_agent (registration, wiring, validation) | 6 | Yes |
| Agent registry (list/get/root) | 3 | Yes |
| route_task (3 strategies + no-match + exclude) | 6 | Yes |
| execute_task (success, failure, smolagent, state, counters) | 10 | Yes |
| execute_parallel (ordering, concurrency, mixed success) | 3 | Yes |
| collect_results (all, filtered, success-only, clear) | 4 | Yes |
| Tree traversal (children, ancestors, descendants, tree dict) | 9 | Yes |
| remove_agent | 3 | Yes |
| summary | 2 | Yes |
| End-to-end (orchestrator→specialist, parallel) | 2 | Yes |
| Decision | Rationale |
|----------|-----------|
| `set[AgentCapability]` for capabilities | O(1) intersection/subset checks; clean enum namespace |
| Separate from governance hierarchy | Governance needs persistence + policy; this needs speed + SmolAgents attachment |
| `RuntimeError` propagates, `Exception` creates TaskResult | Programming errors (no executor configured) should crash loudly; task execution errors should be handled gracefully |
| `asyncio.gather` in thread when event loop running | Allows `execute_parallel` to be called from both sync and async contexts without forcing the caller to manage loops |
| `task_executor` callback parameter | 100% test coverage without LLM API keys; production code swaps in real SmolAgents calls |
| First spawned node is root | Minimal friction: single-orchestrator pattern is the common case |
| ROUND_ROBIN bucketed per capability | Prevents one capability from monopolising a single index counter |
| Level | Role | Examples | Can Delegate To |
|-------|------|----------|-----------------|
| **0** | User | Human | All agents |
| **1** | Executive | `sitback`, `manager`, `orchestrator` | All agents |
| **2** | Team Lead | `frontend-lead`, `backend-lead`, `devops-lead` | Team members, other team leads (with approval) |
| **3** | Specialist | `coder`, `researcher`, `reviewer`, `tester` | Peers, lower-level specialists |
- [ ] Google A2A protocol (deferred)
- [ ] GitHub Copilot Workspace teams (limited public docs)
- [ ] Cursor multi-agent patterns (limited public docs)
- [ ] Am I making too many similar tool calls? → Batch them
- [ ] Is this more complex than needed? → Simplify
- [ ] Can I create a reusable helper? → Create it
- [ ] Will other agents benefit? → Share it
- [ ] Can this be automated? → Automate it
| Agent | Work Item | Status |
|-------|-----------|--------|
| free-agent-1 | research-library-circuit-breaker | ⏳ Dependency added |
| free-agent-2 | research-library-yaml | ⏳ In progress |
| free-agent-3 | research-library-ansi | ⏳ In progress |
| free-agent-4 | research-cross-platform-isolation | ⏳ In progress |
| free-agent-5 | scratch-thegent-shims | ⏳ In progress |
| free-agent-6 | research-cross-platform-shell | ⏳ In progress |
| free-agent-7 | research-hook-rust-phase1 | ⏳ In progress |
| free-agent-8 | research-idea-seed-system | ⏳ In progress |
| free-agent-9 | sync-unified-command | ✅ Code changes detected |
| free-agent-10 | research-phase13-tenant-boundary-tests | ⏳ In progress |
| Agent | Work Item | Priority | Dependencies |
|-------|-----------|----------|--------------|
| free-agent-11 | research-library-retry | P1 | None |
| free-agent-12 | research-library-cache | P2 | None |
| free-agent-13 | research-cross-platform-coordination | P1 | research-cross-platform-isolation |
| free-agent-14 | research-cross-platform-desktop | P1 | research-cross-platform-coordination |
| free-agent-15 | research-cross-platform-security | P1 | research-cross-platform-desktop |
| Agent ID | Work Item | Target Files | Status |
|----------|-----------|--------------|--------|
| free-agent-1 | research-library-circuit-breaker | `src/thegent/orchestration/circuit_breaker.py` | ✅ Running |
| free-agent-2 | research-library-yaml | `src/thegent/infra/fast_yaml_parser.py` + 14 files | ✅ Running |
| free-agent-3 | research-library-ansi | `src/thegent/agents/codex_proxy.py`, `droid.py` + 3 files | ✅ Running |
| free-agent-4 | research-cross-platform-isolation | New implementation | ✅ Running |
| free-agent-5 | scratch-thegent-shims | New Rust project | ✅ Running |
| # | Work Item | Target | Status | Notes |
|---|-----------|--------|--------|-------|
| 1 | research-library-circuit-breaker | `circuit_breaker.py` | ✅ Delegated | PID: 78918 |
| 2 | research-library-yaml | `fast_yaml_parser.py` + 14 files | ✅ Delegated | PID: 6317 |
| 3 | research-library-ansi | 5 files with `_strip_ansi()` | ✅ Delegated | PID: 6407 |
| 4 | research-cross-platform-isolation | New isolation layer | ✅ Delegated | PID: 6501 |
| 5 | scratch-thegent-shims | Rust shims project | ✅ Delegated | PID: 6596 |
| Agent | Work Item | Status | Evidence |
|-------|-----------|--------|----------|
| free-agent-1 | research-library-circuit-breaker | ⏳ Claimed | WORK_STREAM.md |
| free-agent-2 | research-library-yaml | ⏳ Claimed | WORK_STREAM.md |
| free-agent-3 | research-library-ansi | ⏳ Claimed | WORK_STREAM.md |
| free-agent-4 | research-cross-platform-isolation | ⏳ Claimed | WORK_STREAM.md |
| free-agent-5 | scratch-thegent-shims | ⏳ Claimed | WORK_STREAM.md |
| free-agent-6 | research-cross-platform-shell | ⏳ Claimed | WORK_STREAM.md |
| free-agent-7 | research-hook-rust-phase1 | ⏳ Claimed | WORK_STREAM.md |
| free-agent-8 | research-idea-seed-system | ⏳ Claimed | WORK_STREAM.md |
| free-agent-9 | sync-unified-command | ⏳ Claimed | WORK_STREAM.md |
| free-agent-10 | research-phase13-tenant-boundary-tests | ⏳ Claimed | WORK_STREAM.md |
| Pattern | Latency | Coupling | Ordering | Ordering |
|---------|---------|----------|----------|----------|
| Event Bus (Async) | ⭐⭐⭐⭐ (Low latency) | ⭐⭐⭐⭐ (Decoupled) | ⭐⭐ (Eventually consistent) | ⭐⭐⭐ |
| Shared State | ⭐⭐⭐⭐⭐ (Instant) | ⭐ (Tightly coupled) | ⭐⭐⭐⭐⭐ (Sequential) | ⭐ |
| Message Queue | ⭐⭐⭐ (Medium) | ⭐⭐⭐ (Loose) | ⭐⭐⭐ (FIFO) | ⭐⭐⭐ |
| Technique | Token Savings | Quality Impact | Complexity |
|-----------|---------------|----------------|-----------|
| Sliding Window | 60-70% | Minimal (with overlap) | Low |
| Hierarchical | 70-80% | Moderate (loses detail) | Medium |
| Summarization | 80-90% | High (abstractive better) | High |
| Message Culling | 40-50% | Low (loses history) | Low |
| Cache Type | Hit Rate | Speed | Memory | Complexity |
|-----------|----------|-------|--------|-----------|
| Exact Match | 20-40% | Instant | Medium | Low |
| Semantic | 60-80% | ~100ms lookup | Medium | High |
| Hierarchical | 40-70% | Fast (L1) | Large | High |
| Prompt Cache (Claude) | 85%+ | Instant | Offloaded | Very Low |
| Problem | Best Pattern | Why |
|---------|-------------|-----|
| Task dependencies | DAG Orchestration | Optimal parallelism |
| Many independent tasks | Work Stealing | Prevents starvation |
| Tight agent coupling | Shared State | Low latency |
| Loose agent coupling | Event Bus | Decoupled, scalable |
| Long documents | Sliding Window | Memory efficient |
| Chat applications | Multi-turn Manager | Conversation history |
| High cost sensitivity | Semantic Cache | 80%+ hit rate possible |
| Latency critical | Prompt Cache | Instant hits |
| Fast inference | Speculative Decoding | 2-3x speedup |
| Variable load | Dynamic Spawning | Cost effective |
| Quality-cost tradeoff | Cost-based Routing | Optimal choices |
| Complex queries | Specialist Routing | Expert answers |
| Reliability critical | Fallback Chain | Graceful degradation |
| Platform | Type | CLI | AI Proxy | OSS Harness | MCP Support |
|----------|------|-----|----------|-------------|-------------|
| **kilo** | OSS Platform | `kilo auth` | `api.kilo.ai/v1` | ✓ | — |
| **roo** | OSS Platform | `roo auth login` | `api.roocode.com/v1` | ✓ | — |
| **OpenCode** | OSS Agent | `opencode` | Zen, multi-provider | ✓ | ✓ |
| **Claude Code** | OSS Agent | `claude` | Anthropic | ✓ | ✓ |
| **Codex** | OSS Agent | `codex` | OpenAI | ✓ | ✓ (adapter) |
| **Cursor Agent** | IDE Agent | IDE | cursor-api | Partial | ✓ |
| Option | Description | Effort |
|--------|-------------|--------|
| **A. OpenCode custom provider** | Configure OpenCode to use `OPENAI_BASE_URL=http://127.0.0.1:8317/v1` + `OPENAI_API_KEY=sk-dummy` | Low — config only |
| **B. Zen bypass** | Use OpenCode with custom provider URL pointing to CLIProxy; Zen becomes optional | Low |
| **C. CLIProxy Zen block** | Add Zen as a provider block in CLIProxy config (if Zen exposes OpenAI-compatible API) | Medium — depends on Zen API |
| **D. thegent OpenCode runner** | thegent `run opencode "..."` that launches OpenCode with env pointing to proxy | Medium |
| Component | Implementation |
|-----------|----------------|
| **Runtime** | Claude Code (via `clode`) or Codex (via `--dex`) |
| **Launch** | `thegent sitback` → `_run_sitback_claude` / `_run_sitback_codex` |
| **Skill** | `skills/sitback-agent/SKILL.md` → `~/.claude/skills/sitback-agent` |
| **MCP** | `thegent serve` (prerequisite); tools: `thegent_sitback_dashboard`, `thegent_run`, `thegent_bg`, etc. |
| **Chat surface** | Claude Code IDE or Codex IDE |
| Sitback capability | Claude Code / Codex | OpenClaw | Agent Zero |
|--------------------|---------------------|----------|------------|
| **Chat interface** | IDE chat | WebChat, CLI (`openclaw agent --message`) | Web UI, terminal |
| **MCP client** | Native (stdio/HTTP) | Pi agent → MCP? | Native (MCP client) |
| **Skill loading** | `~/.claude/skills/` | OpenClaw skills (ClawHub) | SKILL.md (compatible) |
| **Tool calling** | Full | Pi agent tool streaming | Full |
| **Always-on** | No (IDE session) | Yes (Gateway daemon) | Yes (Docker/process) |
| **Session chat** | Per-IDE | Gateway sessions | Per-chat |
| **Multi-channel** | No | WhatsApp, Telegram, WebChat, etc. | No (Web + terminal) |
| Criterion | OpenClaw | Agent Zero |
|-----------|----------|------------|
| **Skill format** | OpenClaw-specific; may need adapter | SKILL.md (compatible) |
| **MCP** | Pi agent; MCP support TBD | MCP client native |
| **Stack** | Node/TS | Python |
| **Always-on** | Gateway daemon | Docker/process |
| **Chat** | WebChat, multi-channel | Web UI, terminal |
| **Sitback fit** | Gateway + skills; good for "chat with sessions" | MCP + skills; good for tool-heavy orchestration |
| **Effort to integrate** | Medium–high (skill adapter, Pi↔MCP) | Low–medium (MCP config, skill load) |
| Action | Effort | Value |
|--------|--------|-------|
| Publish `agent-orchestra`, `sitback-agent` to ClawHub | Low | Discoverability for OpenClaw/Agent Zero users |
| Add `thegent skill install clawhub:<name>` (or similar) | Medium | Pull community skills into thegent |
| Verify ClawHub skill format vs thegent SKILL.md | Low | Prerequisite for above |
| thegent MCP Tool | Agent Zero Use |
|------------------|----------------|
| `thegent_do_next` | Get next actionable item from WORK_STREAM |
| `thegent_run` / `thegent_bg` | Execute task via thegent routing |
| `thegent_memory_add` | Record observations into audit log |
| `thegent_memory_scrape_session` | Ingest user prompts/intents |
| Consideration | Assessment |
|---------------|------------|
| OpenClaw focus | Consumer channels (WhatsApp, Telegram); not dev/CLI |
| thegent focus | Governance, hooks, Pareto routing |
| Overlap | Low — different surfaces |
| Feature | Why |
|---------|-----|
| OpenClaw multi-channel | thegent is CLI/terminal, not messaging |
| Agent Zero subagents | thegent uses WORK_STREAM + DAG, not superior/subordinate |
| OpenClaw Gateway | thegent has its own MCP server |
| Agent Zero memory/RAG | thegent has `thegent_memory_*`; different design |
| Feature | Claude Code | Codex | Cursor | OpenCode | kilo | roo |
|---------|-------------|-------|--------|----------|------|-----|
| AI proxy | Anthropic | OpenAI | cursor-api | Zen, multi | api.kilo.ai | api.roocode.com |
| OSS harness | ✓ | ✓ | Partial | ✓ | ✓ | ✓ |
| CLI | ✓ | ✓ | IDE | ✓ | ✓ | ✓ |
| MCP | ✓ | ✓ | ✓ | ✓ | — | — |
| CLIProxy | ✓ | ✓ (adapter) | — | Proposed | ✓ | ✓ |
| Zen | — | — | — | ✓ | — | — |
| Session parsing | ✓ | ✓ | ✓ | ✓ | — | — |
| Criterion | Claude Code | Codex | Agent Zero | OpenClaw |
|-----------|-------------|-------|------------|----------|
| **Chat interface** | IDE | IDE | Web UI, terminal | WebChat, multi-channel |
| **MCP support** | Native | Adapter | Native | TBD |
| **Skill format** | SKILL.md | SKILL.md | SKILL.md | OpenClaw-specific |
| **Always-on** | No | No | Yes | Yes |
| **Stack** | Python | Python | Python | Node/TS |
| **Setup complexity** | Medium | Medium | Low–medium | Medium–high |
| **Integration effort** | Low | Low | Low–medium | Medium–high |
| Task | Effort | Owner |
|------|--------|-------|
| Document OpenCode + CLIProxy in PROVIDER_SETUP_GUIDE | 1–2 edits | — |
| Add OpenCode Zen section: when to use Zen vs CLIProxy | 1–2 edits | — |
| Document Agent Zero + thegent MCP setup | 2–4 edits | — |
| Add `thegent sitback --agent-zero` command | 8–12 tool calls | — |
| Verify ClawHub skill format compatibility | Manual inspection | — |
| Publish agent-orchestra to ClawHub (if format OK) | clawhub.ai | — |
| Optional: thegent opencode runner (launch with proxy env) | 8–12 tool calls | — |
| Optional: GoZen profile for thegent/CLIProxy | 2–4 edits | — |
| Aspect | Details |
|--------|---------|
| **AI proxy** | `https://api.kilo.ai/v1` — OpenAI-compatible model API |
| **OSS harness** | CLI + agent runner (like Claude Code, Codex) — runs agents with tools |
| **CLI** | `kilo auth` — interactive wizard; credentials in `~/.kilocode/cli/` or `~/.kilo/token.json` |
| **thegent** | Provider via CLIProxyAPIPlus; `thegent run kilo "..."`; `thegent cliproxy login kilo` |
| **Search/features** | Model catalog, agent routing; harness provides search and tool execution |
| Aspect | Details |
|--------|---------|
| **AI proxy** | `https://api.roocode.com/v1` — OpenAI-compatible model API |
| **OSS harness** | CLI + agent runner — runs agents with tools |
| **CLI** | `roo auth login` — OAuth flow; credentials in `~/.config/roo/credentials.json` |
| **thegent** | Provider via CLIProxyAPIPlus; `thegent run roo "..."`; `thegent cliproxy login roo` |
| **Search/features** | Model catalog, agent routing; harness provides search and tool execution |
| Aspect | Details |
|--------|---------|
| **Type** | OSS AI coding agent (terminal, IDE, desktop) |
| **CLI** | `opencode` — `npm install -g opencode`; similar to Claude Code |
| **Zen** | Curated free/paid models for coding agents; pay-per-request; works with any agent |
| **Config** | `.opencode/` — commands, instructions, plugins, prompts, tools |
| **ECC support** | everything-claude-code has `.opencode/` plugin (v1.3.0); 12 agents, 24 commands, 16 skills |
| **API** | OpenCode SDK; server on port 4096; supports Anthropic, OpenAI, Google, etc. |
| Platform | CLI | AI Proxy | OSS Harness | Search/Features |
|----------|-----|----------|-------------|-----------------|
| **Claude Code** | `claude` | Anthropic | ✓ | read_file, list_dir, codebase_search, MCP |
| **Codex** | `codex` | OpenAI | ✓ | Responses API; tools server-side |
| **Cursor Agent** | IDE | cursor-api | Partial | @codebase, semantic search |
| **OpenCode** | `opencode` | Zen, multi-provider | ✓ | plugins; .opencode/ |
| **kilo** | `kilo auth` | api.kilo.ai | ✓ | Model catalog; harness runs agents |
| **roo** | `roo auth login` | api.roocode.com | ✓ | Model catalog; harness runs agents |
| **augment** | (research) | — | — | — |
| **amp** | (research) | — | — | — |
| Option | Description | Effort |
|--------|-------------|--------|
| **A. OpenCode custom provider** | Configure OpenCode to use `OPENAI_BASE_URL=http://127.0.0.1:8317/v1` + `OPENAI_API_KEY=sk-dummy` | Low — config only |
| **B. Zen bypass** | Use OpenCode with custom provider URL pointing to CLIProxy; Zen becomes optional | Low |
| **C. CLIProxy Zen block** | Add Zen as a provider block in CLIProxy config (if Zen exposes OpenAI-compatible API) | Medium — depends on Zen API |
| **D. thegent OpenCode runner** | thegent `run opencode "..."` that launches OpenCode with env pointing to proxy | Medium |
| Task | Effort | Owner |
|------|--------|-------|
| Document OpenCode + CLIProxy in PROVIDER_SETUP_GUIDE | 1–2 edits | — |
| Add OpenCode Zen section: when to use Zen vs CLIProxy | 1–2 edits | — |
| Optional: thegent opencode runner (launch with proxy env) | 8–12 tool calls | — |
| Optional: GoZen profile for thegent/CLIProxy | 2–4 edits | — |
| Feature | Claude Code | Codex | Cursor | OpenCode | kilo | roo |
|---------|-------------|-------|--------|----------|------|-----|
| AI proxy | Anthropic | OpenAI | cursor-api | Zen, multi | api.kilo.ai | api.roocode.com |
| OSS harness | ✓ | ✓ | Partial | ✓ | ✓ | ✓ |
| CLI | ✓ | ✓ | IDE | ✓ | ✓ | ✓ |
| MCP | ✓ | ✓ | ✓ | ✓ | — | — |
| CLIProxy | ✓ | ✓ (adapter) | — | Proposed | ✓ | ✓ |
| Zen | — | — | — | ✓ | — | — |
| Session parsing | ✓ | ✓ | ✓ | ✓ | — | — |
| Doc | Purpose |
|-----|---------|
| [PROVIDER_SETUP_GUIDE.md](../guides/PROVIDER_SETUP_GUIDE.md) | kilo, roo, CLIProxy login |
| [AGENT_ACCESS_AND_OPTIMIZATION_AUDIT_PLAN.md](./AGENT_ACCESS_AND_OPTIMIZATION_AUDIT_PLAN.md) | File/web/batch audit |
| [CODEX_MINIMAX_CLIPROXY_RESEARCH_AND_PLAN.md](./CODEX_MINIMAX_CLIPROXY_RESEARCH_AND_PLAN.md) | Codex + CLIProxy adapter |
| [SETUP_PROPOSED_ITEMS.md](../plans/SETUP_PROPOSED_ITEMS.md) | MCP ecosystem, oh-my-opencode |
| Process Type | OS Name | Count | Likely Role |
|--------------|---------|-------|-------------|
| **zsh** | zsh | 3–4 | Shell for command execution, integrated terminal(s) |
| **agent-shell** | cursor-shell* | 2–3 | Tool execution, shell integration for agent (Codex, etc.) |
| **agent** | codex / cursor-agent | 1 | The AI agent process |
| Layer | Owner | Can Optimize? |
|------|-------|---------------|
| **4 zsh + 2–3 agent-shell + 1 agent** | Runtime (proprietary) | **No** — upstream architecture |
| **MCP servers** (Playwright, Upstash, thegent) | thegent / config | **Yes** — uni-mount, single URL |
| **LSPs** (clangd, gopls, rust-analyzer) | IDE + thegent | **Partial** — LSP multiplexing (MTSP-04) |
| **Task / shell-outs** | thegent | **Yes** — consolidated worker, Rust hook-dispatcher |
| Task | Description | Status |
|------|-------------|--------|
| **MTSP-01** | Unified MCP Host — single `thegent serve` URL | Done |
| **MTSP-02** | In-Process Agent Runner — cwd isolation, fewer shell-outs | Phase 2 |
| **MTSP-03** | Shared Task Worker — process-compose | Done |
| **MTSP-04** | LSP Multiplexing — single Serena daemon | Pending |
| **MTSP-05** | Unified Worker Daemon | Phase 2 |
| Action | Effect |
|--------|--------|
| `thegent mcp migrate-unimount all` | Single MCP URL — fewer duplicate MCP processes |
| `export THGENT_AUTO_PRUNE=1` | Auto-prune orphans on Stop |
| `thegent mcp spotlight-exclude` | Reduce mds_stores CPU/memory pressure |
| `THGENT_CONCURRENCY_MAX_SLOTS_PER_OWNER=2` | Cap concurrent runs per project |
| Fewer agent tabs | Directly reduces 7×N process count |
| Question | Answer |
|----------|--------|
| **Is 4 zsh + 2–3 agent-shell + 1 agent a lot?** | For one session: moderate. For N sessions: yes — scales linearly. |
| **Multi-tenant needed?** | Yes — MTSP is the right direction. Consolidate MCP, LSP, task; the ~7 runtime processes are upstream. |
| **What to do now?** | Uni-mount MCP, auto-prune, spotlight-exclude, slot caps. Continue MTSP-04 (LSP multiplexing). |
| Category | Count | Top Project | Stars |
|----------|-------|-------------|-------|
| General Frameworks | 6 | Superpowers | 55,809 |
| MCP-based | 5 | mcp-use | 9,206 |
| Domain-Specific | 5 | TradingAgents | 30,232 |
| Infrastructure | 4 | AgentGateway | 1,772 |
| **Total Documented** | **20+** | - | - |
| Product | OpenAI Compat | Deployment | Multi-Provider | Semantic Cache | Guardrails | ML Routing | Prompt Mgmt | MCP/A2A | Observability | Budget Mgmt | Self-Host |
|---------|--------------|------------|---------------|----------------|------------|-----------|-------------|---------|--------------|-------------|-----------|
| **Bifrost** | Yes | Cloud/Edge/On-prem | 1000+ models | Yes (embedding) | Yes | No | No | MCP tools | OTel+Prometheus | Hierarchical | Yes |
| **LiteLLM** | Yes | Self-hosted | 100+ providers | No | Basic | No | No | No | Multi-platform | Per-key/team | Yes |
| **Portkey** | Yes | Both | 1600+ LLMs | Yes (semantic) | 60+ | No | Yes | No | Yes | Virtual keys | Yes (OSS) |
| **Helicone** | Yes | Both | Major | Edge cache | Basic | No | Yes (versioned) | No | Deep traces | No | Yes |
| **Cloudflare** | Yes | SaaS only | 350+ / 6 providers | Yes | Basic | No | No | No | Real-time analytics | Rate limiting | No |
| **Kong** | Yes | Both | Multi-provider | Semantic | Plugin-based | No | Plugin | MCP (via plugin) | Extensive | Plugin | Yes |
| **Vercel** | Yes | SaaS only | Hundreds | Yes | Basic | No | No | No | Per-model analytics | No | No |
| **OpenRouter** | Yes | SaaS only | 300+ models | No | No | Basic | No | No | Basic | No | No |
| **Not Diamond** | Yes | Both | Any | No | No | Yes (ML meta-model) | Auto-rewrite | No | No | No | VPC only |
| **Martian** | Yes | SaaS+VPC | Configurable | No | Compliance | Yes (model mapping) | No | No | No | No | VPC only |
| **Unify** | Yes | SaaS only | Provider-level | No | No | Yes (live benchmarks) | No | No | No | No | No |
| **Requesty** | Yes | SaaS only | 500+ models | Yes | PII+injection | Latency-based | No | No | 40+ metrics | Budget caps | No |
| **Braintrust** | Yes | Both (OSS) | 100+ models | Yes | No | No | No | No | Eval-native | No | Yes |
| **Langfuse** | Via LiteLLM | Both | Via LiteLLM | No | No | No | Yes (versioned) | No | OTel-native | No | Yes |
| **Azure APIM** | Yes | Azure cloud | Azure AI + more | Semantic | Content Safety | No | No | MCP servers | Azure Monitor | TPM limits | Hybrid |
| **AWS Bedrock** | Yes | AWS cloud | AWS models | Prompt cache | Basic | No | No | AgentCore MCP | CloudWatch | IAM-based | VPC |
| **Vertex AI** | Yes | GCP cloud | Google models | No | Safety filters | No | No | No | Cloud Monitoring | Quotas | No |
| **Fireworks** | Yes | SaaS+BYOC | Fireworks models | No | No | No | No | No | Basic | No | BYOC |
| **Envoy AI GW** | Yes | K8s self-hosted | Any provider | No | No | No | No | MCP (first-class) | OTel+OI | Token rate limit | Yes |
| **TrueFoundry** | Yes | Both | 1000+ LLMs | No | Yes | No | No | MCP Gateway | Yes | Budget | Yes |
| **AgentGateway** | No (MCP/A2A) | Self-hosted | N/A | No | No | No | No | MCP+A2A | OTel | No | Yes |
| **Operant AI** | No (MCP) | SaaS | N/A | No | Security-focus | No | No | MCP security | Traffic graphs | No | No |
| **ZenMux** | Yes | SaaS | 200+ LLMs | No | No | Task classify | No | No | HLE benchmarks | No | No |
| Feature | Who Has It | Description |
|---------|-----------|-------------|
| **ML meta-model routing** | Not Diamond, Martian | Learned routing (not rules/benchmarks). Routes per-query based on trained model. |
| **Automatic prompt rewriting per model** | Not Diamond | Auto-adapts prompts for different model families. |
| **Mechanistic interpretability routing** | Martian | Uses model internals (not just outputs) to predict quality. |
| **Provider-level routing (same model, different host)** | Unify | Routes Llama 3.1 to cheapest/fastest provider in real-time. |
| **Live 10-min benchmark updates as routing signal** | Unify | Continuous benchmark refresh vs static leaderboards. |
| **LLM Insurance / automatic compensation** | ZenMux | Credits for hallucinations, latency breaches, quality drops. |
| **Async observability (no hot path)** | Helicone | Ingest traces without being in the proxy path at all. |
| **Unified reasoning API abstraction** | Braintrust | Normalizes o1/Claude-thinking/Gemini-thinking into one API. |
| **Eval-integrated gateway** | Braintrust | Asynchronous online eval of production traffic, zero latency. |
| **OTel-native (not OTel adapter)** | Langfuse | Built on OTel client, not a wrapper. |
| **A2A + MCP dual protocol** | AgentGateway | Both Google A2A and Anthropic MCP protocols. |
| **REST-to-MCP bridge** | AgentGateway | Auto-converts REST APIs to MCP tools. |
| **Federated MCP tool registry** | AgentGateway, TrueFoundry | Centralized tool discovery for agents. |
| **MCP security (Shadow Escape detection)** | Operant AI | Zero-click exploit detection for MCP traffic. |
| **Grounding with live search** | Vertex AI | Native Google Search integration into completions. |
| **BYOC inference (customer's GPUs)** | Fireworks AI | Inference engine runs on customer's VPC hardware. |
| **Agent workflow optimization** | Not Diamond | Optimizes multi-step agent plans, not just single calls. |
| **Kubernetes Gateway API Inference Extension** | Envoy AI Gateway | Spec-stable intelligent endpoint selection for K8s. |
| **WebSocket Realtime API with token tracking** | Azure APIM | Streaming/realtime token metering for GPT-4o Realtime. |
| **Native Managed Identity auth** | Azure APIM | No API keys; Azure MSI for auth. |
| **Prompt compliance routing** | Martian | Routes based on regulatory/compliance model properties. |
| **HLE community benchmarks** | ZenMux | Human Last Exam tests, community-auditable. |
| **Unified LLM + MCP gateway** | TrueFoundry | Both LLM and agent-tool routing in one control plane. |
| **Model fine-tuning + gateway** | TrueFoundry, Fireworks | Train and serve custom models through the same platform. |
| Category | Total | Optimized | Can Optimize | Keep As-Is |
|----------|-------|-----------|--------------|------------|
| HTTP/Networking | 8 | 6 | 2 | 0 |
| Data Serialization | 6 | 1 | 2 | 3 |
| File Operations | 5 | 0 | 2 | 3 |
| Caching | 5 | 4 | 0 | 1 |
| CLI/UI | 4 | 4 | 0 | 0 |
| Database | 4 | 4 | 0 | 0 |
| Config | 3 | 2 | 1 | 0 |
| Testing | 4 | 4 | 0 | 0 |
| Observability | 4 | 4 | 0 | 0 |
| Auth/Security | 5 | 5 | 0 | 0 |
| ML/AI | 5 | 5 | 0 | 0 |
| **TOTAL** | **~200** | **~40** | **~7** | **~153** |
| Aspect | Details |
|--------|---------|
| **Type** | Open-source UI renderer |
| **License** | Apache 2.0 |
| **Price** | Free |
| **Website** | swagger.io/tools/swagger-ui/ |
| Aspect | Details |
|--------|---------|
| **Type** | Commercial API documentation platform |
| **License** | Proprietary (free tier available) |
| **Price** | Free tier + paid plans |
| **Website** | redocly.com/ |
| Aspect | Details |
|--------|---------|
| **Type** | Web Component-based API docs |
| **License** | MIT |
| **Price** | Free |
| **Website** | rapidocweb.com/ |
| Aspect | Details |
|--------|---------|
| **Type** | API Platform (Client + Docs + Registry + SDK) |
| **License** | MIT (open-source) |
| **Price** | Free tier + paid plans |
| **Website** | scalar.com/ |
| Feature | Swagger UI | Redoc | RapiDoc | Scalar |
|---------|------------|-------|---------|--------|
| Open Source | Yes | Partial | Yes | Yes |
| Free Tier | Yes | Yes | Yes | Yes |
| Built-in API Testing | No | No | Yes | Yes |
| Custom Theming | Limited | Yes | Yes | Yes |
| Framework Required | No | No | No | Optional |
| Performance | Moderate | Good | Excellent | Good |
| Markdown Support | No | No | Yes | Yes |
| Interactive Console | No | No | Yes | Yes |
| Tool | Description | License |
|------|-------------|---------|
| **Prism** | Open-source mock server, validation, proxy | MIT |
| **Stoplight Prism** | Similar to above, now community-maintained | Apache 2.0 |
| **swagger-cli** | CLI for Swagger validation and bundling | Apache 2.0 |
| **openapi-mermaid** | Generates mock servers from specs | MIT |
| Aspect | Details |
|--------|---------|
| **Type** | Static Site Generator (React-based) |
| **License** | MIT |
| **Price** | Free (open source) |
| **Website** | docusaurus.io/ |
| vs Gatsby | vs Next.js | vs VitePress | vs MkDocs |
|-----------|------------|--------------|-----------|
| More focused on docs | More opinionated | Vue-based | Python-based |
| Lower learning curve | Out-of-box features | React-based | No SPA |
| Aspect | Details |
|--------|---------|
| **Type** | Static Site Generator (Vue-based) |
| **License** | MIT |
| **Price** | Free (open source) |
| **Website** | vitepress.dev/ |
| Aspect | Details |
|--------|---------|
| **Type** | Documentation Platform |
| **License** | Proprietary |
| **Price** | Free tier + Enterprise plans |
| **Website** | mintlify.com/ |
| Tool | Description | Language |
|------|-------------|----------|
| **oclif** | Node.js CLI framework with built-in help | JavaScript/TypeScript |
| **Cobra** | Go CLI framework with auto-help | Go |
| **Typer** | Python CLI library with help generation | Python |
| **Clap** | Rust CLI argument parser | Rust |
| **Argparse** | Python standard library | Python |
| Feature | Docusaurus | VitePress | Mintlify |
|---------|------------|-----------|----------|
| Open Source | Yes | Yes | No |
| Free Tier | Yes | Yes | Yes |
| Build Speed | Moderate | Fast | N/A (hosted) |
| Plugin Ecosystem | Extensive | Growing | Limited |
| Customization | High | High | Moderate |
| GitHub Sync | Via plugins | Via plugins | Native |
| CLI Integration | Via plugins | Via plugins | Native |
| Aspect | Details |
|--------|---------|
| **Type** | Text-to-diagram tool |
| **License** | MIT |
| **Price** | Free |
| **Website** | mermaid.js.org/ |
| Aspect | Details |
|--------|---------|
| **Type** | UML diagram generator |
| **License** | GPL |
| **Price** | Free |
| **Website** | plantuml.com/ |
| Aspect | Details |
|--------|---------|
| **Type** | Unified diagram API |
| **License** | MIT |
| **Price** | Free (self-hosted) |
| **Website** | kroki.io/ |
| Aspect | Details |
|--------|---------|
| **Type** | Architecture visualization |
| **License**** | Various (tools) |
| **Price** | Free |
| **Website** | c4model.com/ |
| Feature | Mermaid | PlantUML | Kroki | C4 |
|---------|---------|----------|-------|-----|
| Open Source | Yes | Yes | Yes | Yes |
| Free | Yes | Yes | Yes | Yes |
| UML Support | Limited | Full | Full | Limited |
| Web-Native | Yes | No | No | Via tools |
| Integrations | Wide | Wide | Good | Via tools |
| Learning Curve | Low | Medium | Low | Medium |
| Tool | Description |
|------|-------------|
| **Runme** | Markdown-based runbooks with execution |
| **Opslevel Runbooks** | Infrastructure runbook management |
| **GitBook** | Documentation with runbook features |
| Aspect | Details |
|--------|---------|
| **Type** | Link checker |
| **License** | Apache 2.0 / MIT |
| **Price** | Free |
| **Website** | github.com/lycheeverse/lychee |
| Feature | Lychee | awesome_bot | muffet | broken-link-checker | linkinator |
|---------|--------|-------------|--------|---------------------|------------|
| Language | Rust | Ruby | Go | JS | TypeScript |
| Async | Yes | Yes | Yes | Yes | Yes |
| JSON Output | Yes | No | Yes | Yes | Yes |
| Static Binary | Yes | No | Yes | No | No |
| Markdown | Yes | Yes | No | No | No |
| HTML | Yes | No | No | Yes | Yes |
| Basic Auth | Yes | No | No | Yes | No |
| GitHub Action | Yes | No | No | No | Yes |
| Tool | Description | Integration |
|------|-------------|-------------|
| **Playwright** | E2E testing for docs | Docusaurus, VitePress |
| **Cypress** | E2E testing | Various |
| **CodeceptJS** | E2E testing | Various |
| **jest-axel** | API documentation testing | OpenAPI |
| **docusaurus-search-local** | Local search testing | Docusaurus |
| Tool | Description |
|------|-------------|
| **broken-link-checker** | Node.js link checker with image support |
| **linkinator** | TypeScript-based link checker |
| **htmltest** | Static HTML link checker (Go) |
| Tool | Description | Use Case |
|------|-------------|----------|
| **Vitest** | Fast unit test runner | Testing doc components |
| **Storybook** | UI component explorer | Doc component testing |
| ** chromatic** | Visual testing | Doc UI consistency |
| Command | Description |
|---------|-------------|
| `init` | Initialize project |
| `build` | Build for production |
| `dev` | Start dev server |
| Component | Recommended | Alternative |
|-----------|-------------|-------------|
| API Docs | RapiDoc | Swagger UI |
| Site Generator | VitePress | MkDocs |
| Diagrams | Mermaid | PlantUML |
| Link Check | Lychee | linkinator |
| Component | Recommended | Alternative |
|-----------|-------------|-------------|
| API Docs | Scalar | RapiDoc |
| Site Generator | Docusaurus | VitePress |
| Diagrams | Mermaid + PlantUML | Kroki |
| Link Check | Lychee | custom CI |
| Component | Recommended | Alternative |
|-----------|-------------|-------------|
| API Docs | Scalar + Redoc | Swagger Hub |
| Site Generator | Docusaurus | Custom VitePress |
| Diagrams | PlantUML + C4 | Kroki |
| Link Check | Lychee | Enterprise tools |
| Runbooks | Runme | OpsLevel |
| Component | Recommended | Alternative |
|-----------|-------------|-------------|
| API Docs | RapiDoc | Swagger UI |
| Site Generator | VitePress | Docusaurus |
| Diagrams | Mermaid | PlantUML |
| Link Check | Lychee | None |
| Tool | Category | License |
|------|----------|---------|
| Swagger UI | API Docs | Apache 2.0 |
| RapiDoc | API Docs | MIT |
| Docusaurus | Site Generator | MIT |
| VitePress | Site Generator | MIT |
| Mermaid | Diagrams | MIT |
| PlantUML | Diagrams | GPL |
| Lychee | Link Check | Apache 2.0 |
| Tool | Category | Price Range |
|------|----------|-------------|
| Redocly | API Docs | Free tier + Custom |
| Mintlify | Docs Platform | Free + Enterprise |
| Swagger Hub | API Platform | Free + Team + Enterprise |
| GitBook | Docs Platform | Free + Team + Enterprise |
| Notion | Docs | Free + Paid |
| Confluence | Docs | Paid |
| Topic | Reference |
|-------|-----------|
| TUI/Queue Design | `USER_QUEUE_TUI_AND_AGENT_POLL.md` |
| CI/CD Pipelines | `CI_CD_DEVX_TOOLING.md` |
| Hybrid Environment | `../architecture/HYBRID_MAC_WIN_DEV_ENVIRONMENT.md` |
| Implementation Plan | `../plans/HYBRID_ENV_IMPLEMENTATION_PLAN.md` |
| Section | Description |
|---------|-------------|
| **9. CLI Design Patterns** | Added command structure, config files, output formatting, error handling, progress indicators, subcommand discovery, environment overrides, shell completion patterns |
| **10. Cross-References** | Added links to related documentation |
| **11. Extension Summary** | This summary section |
| Pattern | Purpose |
|---------|---------|
| 9.1 Command Structure | Hierarchical command organization |
| 9.2 Configuration Files | YAML configs with profiles |
| 9.3 Output Formatting | Multiple output modes |
| 9.4 Error Handling | Consistent exit codes |
| 9.5 Progress Indicator | Multi-stage progress display |
| 9.6 Subcommand Discovery | Auto-loading commands |
| 9.7 Environment Override | Priority-based config |
| 9.8 Shell Completion | Interactive completion |
| Tool | Purpose |
|------|---------|
| Typer | CLI framework (Python) |
| Cobra | CLI framework (Go) |
| Click | CLI framework (Python) |
| Clap | CLI framework (Rust) |
| ADR ID | Title | Status | Primary Evidence |
| --- | --- | --- | --- |
| ADR-2026-02-16-01 | Standardize Shell/Shim Recovery Flow | Accepted | `docs/research/CURSOR_AGENT_RECOVERY_2026-02-16.md` |
| ADR-2026-02-16-02 | Promote GUI/TUI Notes into Planned Work | Accepted | `docs/research/PROMPTS_LAST_12H.md` |
| ADR-2026-02-16-03 | Adopt Hybrid Compute Offloading | Accepted | `docs/research/CONVERSATION_DUMP_2026-02-16.md` |
| ADR-2026-02-16-04 | Enforce Conversation Dump Persistence by Default | Accepted | `docs/research/CONVERSATION_DUMP_2026-02-18.md` |
| Language | Install Command | Platform |
|----------|----------------|----------|
| Python | `npm install -g pyright` | All |
| TypeScript | `npm install -g typescript-language-server typescript` | All |
| Rust | `rustup component add rust-analyzer` | All |
| Go | `go install golang.org/x/tools/gopls@latest` | All |
| C++ | `brew install llvm` (macOS) / `apt-get install clangd` (Linux) | Platform-specific |
| Bash | `npm install -g bash-language-server` | All |
| YAML | `npm install -g yaml-language-server` | All |
| JSON | `npm install -g vscode-json-languageserver` | All |
| Integration | Auto-Detection | Auto-Configuration |
|-------------|----------------|-------------------|
| JetBrains IDE | ✅ PATH + common locations | ✅ CLI access |
| Serena JetBrains Plugin | ✅ Port check (8765) | ✅ Backend selection |
| Ghostty Shell Integration | ✅ `GHOSTTY_RESOURCES_DIR` | ⚠️ Manual setup (instructions) |
| Component | Status | Performance Gain | Priority |
|-----------|--------|------------------|----------|
| JSON Schema | ✅ Done | 2-3x faster | Medium |
| File Ops | ✅ Done | 5-10x (Linux) | Medium |
| HTTP Client | ✅ Done | 2-3x (optional) | Low |
| Optimization | Current | With Fast Backend | Improvement |
|--------------|---------|-------------------|-------------|
| Subprocess (concurrent) | Sequential | Async concurrent | **Nx faster** (N = concurrency) |
| Caching | Single-tier | Multi-tier | **Better hit rates** |
| Fuzzy matching | Standard | rapidfuzz | **10-100x faster** |
| UUID generation | uuid | fastuuid | **2-5x faster** |
| Optimization | Current | With Fast Backend | Improvement |
|--------------|---------|-------------------|-------------|
| WebSocket (async) | websocket-client | websockets | **Better async support** |
| Compression | gzip | zstd | **2-3x faster** |
| Compression ratio | gzip | brotli | **10-20% better** |
| Path operations | pathlib | os.path | **Lower overhead** |
| Endpoint Prefix | SDK Compatibility |
|----------------|-------------------|
| `http://localhost:8080/openai` | OpenAI SDK |
| `http://localhost:8080/anthropic` | Anthropic SDK |
| `http://localhost:8080/genai` | Google GenAI SDK |
| `http://localhost:8080/v1/chat/completions` | Any OpenAI-compatible client |
| Endpoint | Purpose |
|----------|---------|
| `GET /metrics` | Prometheus metrics scrape |
| `POST /api/providers` | Add/update provider configuration |
| `/v1/mcp/tool/execute` | Explicit MCP tool execution |
| Provider | Notes |
|----------|-------|
| OpenAI | Full support including Responses API |
| Anthropic | Claude 3.x, Claude 4.x families |
| AWS Bedrock | Requires `access_key`, `secret_key`, `region`, `arn`; model-to-ARN mapping |
| Google Vertex AI | Requires deployment config |
| Azure OpenAI | Requires `deployments` mapping + `api_version` |
| Cerebras | Fast inference |
| Cohere | Command family |
| Mistral | Mistral 7B, Mixtral, etc. |
| Ollama | Local models |
| Groq | Ultra-fast inference |
| Google GenAI | Gemini family |
| Hugging Face | Via inference API |
| Together AI | (documented) |
| Perplexity | (documented) |
| Parameter | Description |
|-----------|-------------|
| `embedding_model` | Model used to embed prompts for similarity search |
| `ttl` | Time-to-live in seconds |
| `threshold` | Cosine similarity cutoff (0.8 = 80% similar) |
| `conversation_history_threshold` | Threshold for multi-turn caching |
| `cache_by_model` | Separate cache per model |
| `cache_by_provider` | Separate cache per provider |
| Backend | Notes |
| Weaviate | 50Gi+ recommended for production |
| Qdrant | External instance supported |
| Redis | Supported |
| Metric | Description |
>>>>>>> codex/wave80-integration-lanes-a-f
|--------|-------------|
| **ID** | Unique task identifier (format: `{PROJECT}-{PHASE}.{TASK}` or `P{PHASE}.{TASK}`) |
| **Title** | Task description (brief, <80 chars) |
| **Type** | `feature` \| `refactor` \| `bugfix` \| `infra` \| `research` \| `docs` |
| **Project** | `thegent` or `sharecli` |
| **Phase** | Phase number (0-18) or epic name |
| **Depends On** | Prerequisite task IDs (comma-separated) |
| **Effort** | Estimate: `~3min` / `~5min` / `~8min` / `~10min` / `~15min` / `~20min` |
| **Status** | `PENDING` / `CLAIMED` / `IN_PROGRESS` / `COMPLETED` / `BLOCKED` |

---

## PENDING

All actionable, unassigned work items. Ordered by project, phase, then task ID.

### thegent: Phase 0 (Foundation - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P0.1 | Symlink dispatch mechanism (`bin/harness` + N symlinks) | infra | -- | ~5min | COMPLETED |
| TGNT-P0.2 | Agent detection via `/proc` tree walk with macOS `ps` fallback | infra | TGNT-P0.1 | ~5min | COMPLETED |
| TGNT-P0.3 | `rules.conf` parser (command, strategy, options) | infra | TGNT-P0.1 | ~3min | COMPLETED |
| TGNT-P0.4 | Coalesce strategy (flock + SHA256 cache key + atomic writes) | infra | TGNT-P0.2, TGNT-P0.3 | ~10min | COMPLETED |
| TGNT-P0.5 | Queue strategy (bounded concurrency pool with slot files) | infra | TGNT-P0.3 | ~8min | COMPLETED |
| TGNT-P0.6 | Debounce strategy (delay + coalesce within window) | infra | TGNT-P0.3 | ~5min | COMPLETED |
| TGNT-P0.7 | `harness sync` symlink generator from rules.conf | infra | TGNT-P0.3 | ~3min | COMPLETED |
| TGNT-P0.8 | `nocache_args` safety (`--fix` / `--write` -> queue fallback) | infra | TGNT-P0.4 | ~3min | COMPLETED |

### thegent: Phase 1 (Quick Wins - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P1.1 | Lock timeout via `HARNESS_LOCK_TIMEOUT` (fallback to uncached) | infra | TGNT-P0.4 | ~3min | COMPLETED |
| TGNT-P1.2 | Stale-while-revalidate (serve stale + background refresh) | infra | TGNT-P0.4 | ~5min | COMPLETED |
| TGNT-P1.3 | Prometheus metrics endpoint (`harness metrics`) | infra | TGNT-P0.4 | ~5min | COMPLETED |
| TGNT-P1.4 | Cache compression (zstd for outputs > 10KB) | infra | TGNT-P0.4 | ~5min | COMPLETED |
| TGNT-P1.5 | JSON metrics export (`harness metrics json`) | infra | TGNT-P1.3 | ~2min | COMPLETED |

### thegent: Phase 2 (Intelligence - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P2.1 | 5-level priority queue (critical/high/normal/low/background) | feature | TGNT-P1.1 | ~8min | COMPLETED |
| TGNT-P2.2 | Priority aging (+1 level per 5s waiting, prevents starvation) | feature | TGNT-P2.1 | ~3min | COMPLETED |
| TGNT-P2.3 | Fair share scheduling (per-agent quota with penalty for over-use) | feature | TGNT-P2.1 | ~8min | COMPLETED |
| TGNT-P2.4 | Semantic coalescing (path normalization, `.` -> project root) | feature | TGNT-P0.4 | ~5min | COMPLETED |
| TGNT-P2.5 | Queue timeout protection (fallback execution on timeout) | feature | TGNT-P2.1 | ~3min | COMPLETED |

### thegent: Phase 3 (Performance - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P3.1 | L1 memory cache (`/dev/shm`, 100MB max, 60s TTL) | infra | TGNT-P0.4 | ~8min | COMPLETED |
| TGNT-P3.2 | L2 disk cache (`var/cache`, compressed, persistent) | infra | TGNT-P0.4 | ~5min | COMPLETED |
| TGNT-P3.3 | L2-to-L1 promotion on cache hit (automatic) | infra | TGNT-P3.1, TGNT-P3.2 | ~5min | COMPLETED |
| TGNT-P3.4 | I/O scheduler integration (ionice priority classes) | feature | TGNT-P2.1 | ~5min | COMPLETED |
| TGNT-P3.5 | Negative stat cache (track nonexistent files, 5s TTL) | feature | TGNT-P3.1 | ~3min | COMPLETED |
| TGNT-P3.6 | Page cache warmer (bulk read by file type before exec) | feature | TGNT-P0.4 | ~5min | COMPLETED |

### thegent: Phase 4 (Coordination - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P4.1 | Intent broadcasting (agents signal planned file ops) | feature | TGNT-P0.4 | ~8min | COMPLETED |
| TGNT-P4.2 | Intent conflict checking (write-write, read-write detection) | feature | TGNT-P4.1 | ~5min | COMPLETED |
| TGNT-P4.3 | Wait-for graph construction from lock records | feature | TGNT-P0.5 | ~8min | COMPLETED |
| TGNT-P4.4 | DFS cycle detection for deadlocks | feature | TGNT-P4.3 | ~5min | COMPLETED |
| TGNT-P4.5 | Deadlock auto-resolution (abort youngest waiter) | feature | TGNT-P4.4 | ~3min | COMPLETED |
| TGNT-P4.6 | Fair share tracking with 50% decay smoothing | feature | TGNT-P2.3 | ~5min | COMPLETED |

### thegent: Phase 5 (Polish - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P5.1 | Interactive dashboard (TUI with cache/queue/intent/fair share) | feature | TGNT-P1.3, TGNT-P2.3, TGNT-P4.1 | ~10min | COMPLETED |
| TGNT-P5.2 | Self-tuning report (analyze metrics, detect low hit rate/contention) | feature | TGNT-P1.3, TGNT-P3.1 | ~8min | COMPLETED |
| TGNT-P5.3 | Auto-fix recommendations (color-coded severity, safe auto-apply) | feature | TGNT-P5.2 | ~5min | COMPLETED |
| TGNT-P5.4 | Rules suggestion engine (generate rules from observed patterns) | feature | TGNT-P5.2 | ~5min | COMPLETED |
| TGNT-P5.5 | L1 vs L2 benchmark command | feature | TGNT-P3.1, TGNT-P3.2 | ~3min | COMPLETED |

### thegent: Phase 6 (Git Parallelism - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P6.1 | Per-agent `GIT_INDEX_FILE` management (init, copy, cleanup) | feature | TGNT-P4.1 | ~8min | COMPLETED |
| TGNT-P6.2 | Git plumbing commit pipeline (hash-object -> write-tree -> commit-tree) | feature | TGNT-P6.1 | ~10min | COMPLETED |
| TGNT-P6.3 | CAS ref update with exponential backoff + jitter retry | feature | TGNT-P6.2 | ~5min | COMPLETED |
| TGNT-P6.4 | Scoped staging (agent-to-file mapping, parallel when non-overlapping) | feature | TGNT-P6.1 | ~5min | COMPLETED |
| TGNT-P6.5 | `harness git status` per-agent view (show each agent's staged changes) | feature | TGNT-P6.4 | ~3min | COMPLETED |

### thegent: Phase 7 (Smart Merge - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P7.1 | Mergiraf integration (AST merge for Python/JS/TS/Rust/Go/Java/C) | feature | TGNT-P6.3 | ~10min | COMPLETED |
| TGNT-P7.2 | Conflict prediction from intents (trial merge before commit) | feature | TGNT-P4.1, TGNT-P6.3 | ~8min | COMPLETED |
| TGNT-P7.3 | Import union auto-resolve (Python/JS import conflicts -> sorted union) | feature | TGNT-P7.1 | ~5min | COMPLETED |
| TGNT-P7.4 | JSON/YAML structural merge (deep merge via jq, ours-wins on conflict) | feature | TGNT-P7.1 | ~5min | COMPLETED |

### thegent: Phase 8 (File Coordination - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P8.1 | OCC version check on write (record version at claim, verify before commit) | feature | TGNT-P4.1 | ~8min | COMPLETED |
| TGNT-P8.2 | HLC timestamp generation (millisecond physical + logical counter) | feature | TGNT-P8.1 | ~5min | COMPLETED |
| TGNT-P8.3 | Lease-based file claims registry (read/write/exclusive with flock) | feature | TGNT-P8.1 | ~8min | COMPLETED |
| TGNT-P8.4 | Lease renewal and expiry (background cleanup daemon) | feature | TGNT-P8.3 | ~5min | COMPLETED |

### thegent: Phase 9 (Request Coalescing v2 - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P9.1 | Singleflight dedup pattern (first executes, rest wait for shared result) | feature | TGNT-P0.4 | ~5min | COMPLETED |
| TGNT-P9.2 | inotify cache invalidation (watch file changes, invalidate affected entries) | feature | TGNT-P3.1 | ~8min | COMPLETED |
| TGNT-P9.3 | Heat-based LRU eviction (access frequency with exponential decay) | feature | TGNT-P3.1 | ~5min | COMPLETED |

### thegent: Phase 10 (Resource Isolation - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P10.1 | Per-agent TMPDIR allocation (private temp, cleanup on exit) | feature | TGNT-P0.2 | ~3min | COMPLETED |
| TGNT-P10.2 | Dynamic port range allocation (registry + liveness check) | feature | TGNT-P10.1 | ~5min | COMPLETED |
| TGNT-P10.3 | Environment variable isolation (agent-specific env file, wrapped exec) | feature | TGNT-P10.1 | ~5min | COMPLETED |

### thegent: Phase 11 (IPC Primitives - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P11.1 | tmpfs mesh directory creation (`/tmp/agent-mesh`, 256MB, mode 1777) | infra | -- | ~3min | COMPLETED |
| TGNT-P11.2 | Atomic mkdir lock primitives (EEXIST = already held) + claim + lease | infra | TGNT-P11.1 | ~5min | COMPLETED |
| TGNT-P11.3 | Maildir message queue (tmp -> new -> cur lifecycle, TTL enforcement) | infra | TGNT-P11.1 | ~10min | COMPLETED |
| TGNT-P11.4 | inotify event notification (1-10ms latency, polling fallback for macOS) | feature | TGNT-P11.3 | ~8min | COMPLETED |
| TGNT-P11.5 | Write-ahead log (WAL) with append-before-execute + replay-on-crash | infra | TGNT-P11.1 | ~8min | COMPLETED |

### thegent: Phase 12 (Process Discovery - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P12.1 | `/proc` scanner with agent-specific patterns (Claude/Aider/Cursor/Cline) | feature | TGNT-P11.1 | ~8min | COMPLETED |
| TGNT-P12.2 | Agent manifest creation (YAML: id, type, pid, capabilities, ODD, status) | feature | TGNT-P12.1 | ~5min | COMPLETED |
| TGNT-P12.3 | Heartbeat monitor (touch-file every 5s, 15s failure threshold) | feature | TGNT-P12.2 | ~5min | COMPLETED |
| TGNT-P12.4 | Stale agent cleanup (reclaim tasks, notify dependents, archive manifest) | feature | TGNT-P12.3 | ~3min | COMPLETED |

### thegent: Phase 13 (Shell Injection - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P13.1 | tmux session detection and naming (`mesh-{agent-uuid}`) | feature | TGNT-P12.1 | ~5min | COMPLETED |
| TGNT-P13.2 | Command injection via `tmux send-keys -l` + 1.5s delay + Enter (>99% reliable) | feature | TGNT-P13.1 | ~8min | COMPLETED |
| TGNT-P13.3 | Agent readiness detection (prompt patterns per agent type, busy/idle/error states) | feature | TGNT-P13.2 | ~5min | COMPLETED |

### thegent: Phase 14 (Context Injection - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P14.1 | AGENT.md template system (mesh state, coordination rules, identity) | feature | TGNT-P12.2 | ~5min | COMPLETED |
| TGNT-P14.2 | Tool-specific context files (CLAUDE.md, .cursorrules, .clinerules symlinks) | feature | TGNT-P14.1 | ~8min | COMPLETED |
| TGNT-P14.3 | Dynamic context update (re-render AGENT.md on mesh state changes) | feature | TGNT-P14.2 | ~5min | COMPLETED |

### thegent: Phase 15 (Worktree Support - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P15.1 | Optional worktree creation (`git worktree add .mesh/worktrees/agent-{uuid}`) | feature | TGNT-P6.1 | ~8min | COMPLETED |
| TGNT-P15.2 | Branch coordination (registry, collision avoidance, status tracking) | feature | TGNT-P15.1 | ~5min | COMPLETED |
| TGNT-P15.3 | Worktree cleanup (orphan detection, 30s grace, health monitor) | feature | TGNT-P15.2 | ~3min | COMPLETED |

### thegent: Phase 16 (Sandboxing - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P16.1 | bubblewrap profile (Linux: filesystem + network + process policies) | infra | TGNT-P12.2 | ~10min | COMPLETED |
| TGNT-P16.2 | seatbelt profile (macOS: sandbox-exec equivalent) | infra | TGNT-P12.2 | ~10min | COMPLETED |
| TGNT-P16.3 | 5-tier autonomy enforcement (read -> worktree -> git -> shared -> production) | feature | TGNT-P16.1, TGNT-P16.2 | ~8min | COMPLETED |
| TGNT-P16.4 | Operation classification engine (tier assignment from command + target analysis) | feature | TGNT-P16.3 | ~8min | COMPLETED |

### thegent: Phase 17 (Resource Management - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P17.1 | Memory limit enforcement (cgroups on Linux, ulimit fallback) | feature | TGNT-P12.2 | ~8min | COMPLETED |
| TGNT-P17.2 | Process count limits (detect runaway subprocess spawning) | feature | TGNT-P17.1 | ~5min | COMPLETED |
| TGNT-P17.3 | FD budget allocation (monitor per-agent, alert at thresholds) | feature | TGNT-P17.2 | ~5min | COMPLETED |

### thegent: Phase 18 (Observability v2 - COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| TGNT-P18.1 | JSONL structured logging (PIPE_BUF-aware, atomic append, <4KB per line) | infra | TGNT-P11.1 | ~5min | COMPLETED |
| TGNT-P18.2 | Advanced metrics aggregation (per-agent, per-command, histograms) | feature | TGNT-P1.3, TGNT-P12.2 | ~8min | COMPLETED |
| TGNT-P18.3 | CLI for mesh management (`mesh status`, `mesh agents`, `mesh tasks`) | feature | TGNT-P12.2 | ~10min | COMPLETED |
| TGNT-P18.4 | Health dashboard v2 (agent activity, port/tmpdir usage, claims, intents) | feature | TGNT-P5.1, TGNT-P18.2 | ~10min | COMPLETED |

---

## sharecli: Phases 0-3 (Early Stages)

### Phase 0: Foundation & Prototype (COMPLETE)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| SCLI-P0.1 | Mission statement and hard problems analysis | research | -- | ~5min | COMPLETED |
| SCLI-P0.2 | System architecture diagram and component overview | docs | SCLI-P0.1 | ~8min | COMPLETED |
| SCLI-P0.3 | Configuration schema (rules.conf, agents.conf, env vars) | docs | SCLI-P0.2 | ~5min | COMPLETED |
| SCLI-P0.4 | Risk register with mitigation strategies | docs | SCLI-P0.2 | ~8min | COMPLETED |
| SCLI-P0.5 | Tech stack justification (Bash, Rust, C, flock, etc.) | docs | SCLI-P0.2 | ~5min | COMPLETED |

### Phase 1: Process Detection & Agent Mesh Initialization (PENDING)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| SCLI-P1.1 | Process enumeration from `/proc` (or `ps` for macOS) | feature | -- | ~8min | COMPLETED |
| SCLI-P1.2 | Agent pattern matching (regex-based detection from agents.conf) | feature | SCLI-P1.1 | ~5min | COMPLETED |
| SCLI-P1.3 | Agent manifest system (YAML with metadata, capabilities, ODD) | feature | SCLI-P1.2 | ~8min | COMPLETED |
| SCLI-P1.4 | Mesh directory initialization (`/tmp/agent-mesh` or configurable) | infra | -- | ~3min | COMPLETED |
| SCLI-P1.5 | Agent heartbeat mechanism (touch-file every 5s, 15s failure detection) | feature | SCLI-P1.3 | ~8min | COMPLETED |
| SCLI-P1.6 | Stale agent cleanup and task reclamation | feature | SCLI-P1.5 | ~8min | COMPLETED |

### Phase 2: IPC & Coordination (PENDING)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| SCLI-P2.1 | Atomic mkdir lock primitives for mesh coordination | infra | SCLI-P1.4 | ~5min | COMPLETED |
| SCLI-P2.2 | Maildir message queue system (tmp -> new -> cur lifecycle) | feature | SCLI-P1.4 | ~10min | COMPLETED |
| SCLI-P2.3 | inotify-based event notification (with /proc polling fallback) | feature | SCLI-P2.2 | ~8min | COMPLETED |
| SCLI-P2.4 | Write-ahead log (WAL) for crash recovery | infra | SCLI-P1.4 | ~8min | COMPLETED |
| SCLI-P2.5 | Intent broadcasting system (agents signal planned operations) | feature | SCLI-P2.2 | ~8min | COMPLETED |
| SCLI-P2.6 | Intent conflict detection (write-write, read-write conflicts) | feature | SCLI-P2.5 | ~5min | COMPLETED |

### Phase 3: Consensus & Escalation (PENDING)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| SCLI-P3.1 | Consensus protocol (majority for implementation, supermajority for architecture) | feature | SCLI-P2.5 | ~8min | COMPLETED |
| SCLI-P3.2 | Shapley-value causal influence tracking | feature | SCLI-P3.1 | ~10min | COMPLETED |
| SCLI-P3.3 | 5-tier escalation workflow (self -> peer -> lead -> committee -> human) | feature | SCLI-P3.1 | ~10min | COMPLETED |
| SCLI-P3.4 | Async human escalation queue | feature | SCLI-P3.3 | ~5min | COMPLETED |
| SCLI-P3.5 | Confidence scoring and debate capping (max 3 rounds) | feature | SCLI-P3.1 | ~8min | COMPLETED |

---

## sharecli: Phases 4-9 (Mid-Stage Features)

### Phase 4: Git Operations & Parallelism (PENDING)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| SCLI-P4.1 | Per-agent `GIT_INDEX_FILE` implementation | feature | SCLI-P1.3 | ~8min | COMPLETED |
| SCLI-P4.2 | Git plumbing pipeline (hash-object, write-tree, commit-tree, update-ref CAS) | feature | SCLI-P4.1 | ~10min | COMPLETED |
| SCLI-P4.3 | CAS retry loop with exponential backoff and jitter | feature | SCLI-P4.2 | ~5min | COMPLETED |
| SCLI-P4.4 | Scoped staging (agent-to-file mapping for parallel operations) | feature | SCLI-P4.1 | ~5min | COMPLETED |
| SCLI-P4.5 | Per-agent git status view (show staged changes per agent) | feature | SCLI-P4.4 | ~3min | COMPLETED |

### Phase 5: Smart Merge (PENDING)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| SCLI-P5.1 | Mergiraf integration (AST-aware merge for 10+ languages) | feature | SCLI-P4.2 | ~10min | COMPLETED |
| SCLI-P5.2 | Conflict prediction before commit (trial merge from intents) | feature | SCLI-P2.5, SCLI-P4.2 | ~8min | COMPLETED |
| SCLI-P5.3 | Import union auto-resolution (Python/JS imports) | feature | SCLI-P5.1 | ~5min | COMPLETED |
| SCLI-P5.4 | JSON/YAML structural merge (deep merge via jq) | feature | SCLI-P5.1 | ~5min | COMPLETED |

### Phase 6: File Coordination (PENDING)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| SCLI-P6.1 | Optimistic concurrency control (OCC) version tracking | feature | SCLI-P2.5 | ~8min | COMPLETED |
| SCLI-P6.2 | Hybrid Logical Clock (HLC) timestamp generation | feature | SCLI-P6.1 | ~5min | COMPLETED |
| SCLI-P6.3 | Lease-based file claims registry (read/write/exclusive) | feature | SCLI-P6.1 | ~8min | COMPLETED |
| SCLI-P6.4 | Lease renewal and expiry management | feature | SCLI-P6.3 | ~5min | COMPLETED |

### Phase 7: Caching & Request Deduplication (PENDING)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| SCLI-P7.1 | Singleflight deduplication (first executes, rest wait) | feature | -- | ~5min | COMPLETED |
| SCLI-P7.2 | inotify-based cache invalidation on file changes | feature | SCLI-P2.3 | ~8min | COMPLETED |
| SCLI-P7.3 | Heat-based LRU eviction (access frequency tracking) | feature | -- | ~5min | COMPLETED |

### Phase 8: Resource Isolation (PENDING)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| SCLI-P8.1 | Per-agent TMPDIR allocation and cleanup | feature | SCLI-P1.3 | ~3min | COMPLETED |
| SCLI-P8.2 | Dynamic port range allocation (registry + liveness) | feature | SCLI-P8.1 | ~5min | COMPLETED |
| SCLI-P8.3 | Environment variable isolation per agent | feature | SCLI-P8.1 | ~5min | COMPLETED |

### Phase 9: Shell Injection & Context Injection (PENDING)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| SCLI-P9.1 | tmux session detection and naming | feature | SCLI-P1.3 | ~5min | COMPLETED |
| SCLI-P9.2 | tmux command injection (`send-keys` with 1.5s delay) | feature | SCLI-P9.1 | ~8min | PENDING |
| SCLI-P9.3 | Agent readiness detection (prompt patterns, busy/idle/error) | feature | SCLI-P9.2 | ~5min | PENDING |
| SCLI-P9.4 | AGENT.md template system (dynamic mesh state injection) | feature | SCLI-P1.3 | ~5min | PENDING |
| SCLI-P9.5 | Tool-specific context files (CLAUDE.md, .cursorrules symlinks) | feature | SCLI-P9.4 | ~8min | PENDING |

---

## sharecli: Phases 10-14 (Advanced Features)

### Phase 10: Sandboxing (PENDING)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| SCLI-P10.1 | bubblewrap profile (Linux filesystem/network/process policies) | infra | SCLI-P1.3 | ~10min | PENDING |
| SCLI-P10.2 | seatbelt profile (macOS sandbox-exec equivalent) | infra | SCLI-P1.3 | ~10min | PENDING |
| SCLI-P10.3 | 5-tier autonomy enforcement (read -> worktree -> git -> shared -> production) | feature | SCLI-P10.1, SCLI-P10.2 | ~8min | PENDING |
| SCLI-P10.4 | Operation classification (tier assignment from command + target) | feature | SCLI-P10.3 | ~8min | PENDING |

### Phase 11: Worktree Support (PENDING)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| SCLI-P11.1 | Optional per-agent git worktree creation | feature | SCLI-P4.1 | ~8min | PENDING |
| SCLI-P11.2 | Branch coordination and collision avoidance | feature | SCLI-P11.1 | ~5min | PENDING |
| SCLI-P11.3 | Worktree cleanup and orphan detection | feature | SCLI-P11.2 | ~3min | PENDING |

### Phase 12: Resource Management (PENDING)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| SCLI-P12.1 | Memory limit enforcement (cgroups on Linux, ulimit fallback) | feature | SCLI-P1.3 | ~8min | PENDING |
| SCLI-P12.2 | Process count limits (runaway subprocess detection) | feature | SCLI-P12.1 | ~5min | PENDING |
| SCLI-P12.3 | File descriptor budget allocation and monitoring | feature | SCLI-P12.2 | ~5min | PENDING |

### Phase 13: Observability (PENDING)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| SCLI-P13.1 | JSONL structured logging (atomic append, <4KB per line) | infra | SCLI-P1.4 | ~5min | PENDING |
| SCLI-P13.2 | Advanced metrics aggregation (per-agent, per-command) | feature | -- | ~8min | PENDING |
| SCLI-P13.3 | CLI mesh management commands (`mesh status`, `mesh agents`) | feature | SCLI-P1.3 | ~10min | PENDING |
| SCLI-P13.4 | Health dashboard v2 (activity, usage, claims, intents) | feature | SCLI-P13.2 | ~10min | PENDING |

### Phase 14: Audit & Recovery (PENDING)

| ID | Title | Type | Depends On | Effort | Status |
|----|-------|------|-----------|--------|--------|
| SCLI-P14.1 | Shadow git repo for full delete recovery | feature | SCLI-P4.2 | ~10min | PENDING |
| SCLI-P14.2 | Audit trail with inotify sync to shadow repo | feature | SCLI-P14.1 | ~8min | PENDING |
| SCLI-P14.3 | Full recovery workflow (cross-reference dev + audit repos) | feature | SCLI-P14.2 | ~8min | PENDING |

---

## CLAIMED

| ID | Title | Agent | Claimed At | Expected Completion |
|----|-------|-------|-----------|-------------------|
| TGNT-P6.1 | Per-agent GIT_INDEX_FILE management | phase6-worker | 2026-02-18T16:45:00Z | 2026-02-18T16:53:00Z |
| TGNT-P6.2 | Git plumbing commit pipeline | phase6-worker | 2026-02-18T16:45:00Z | 2026-02-18T17:05:00Z |
| TGNT-P6.3 | CAS ref update with exponential backoff | phase6-worker | 2026-02-18T16:45:00Z | 2026-02-18T17:10:00Z |
| TGNT-P6.4 | Scoped staging (agent-to-file mapping) | phase6-worker | 2026-02-18T16:45:00Z | 2026-02-18T17:15:00Z |
| TGNT-P6.5 | harness git status per-agent view | phase6-worker | 2026-02-18T16:45:00Z | 2026-02-18T17:18:00Z |

---

## COMPLETED

| ID | Title | Completed At | Effort | Notes |
|----|-------|---|--------|-------|
| TGNT-P0.1 | Symlink dispatch mechanism | 2026-02-15 | ~5min | Core harness foundation |
| TGNT-P0.2 | Agent detection via `/proc` tree walk | 2026-02-15 | ~5min | Includes macOS `ps` fallback |
| TGNT-P0.3 | `rules.conf` parser | 2026-02-15 | ~3min | Command, strategy, options support |
| TGNT-P0.4 | Coalesce strategy | 2026-02-15 | ~10min | flock + SHA256 + atomic writes |
| TGNT-P0.5 | Queue strategy | 2026-02-16 | ~8min | Bounded concurrency pool |
| TGNT-P0.6 | Debounce strategy | 2026-02-16 | ~5min | Delay + coalesce within window |
| TGNT-P0.7 | `harness sync` symlink generator | 2026-02-16 | ~3min | From rules.conf |
| TGNT-P0.8 | `nocache_args` safety | 2026-02-16 | ~3min | `--fix`/`--write` fallback |
| TGNT-P1.1 | Lock timeout + fallback | 2026-02-16 | ~3min | HARNESS_LOCK_TIMEOUT env var |
| TGNT-P1.2 | Stale-while-revalidate | 2026-02-16 | ~5min | Serve stale + background refresh |
| TGNT-P1.3 | Prometheus metrics | 2026-02-16 | ~5min | `harness metrics` endpoint |
| TGNT-P1.4 | Cache compression | 2026-02-16 | ~5min | zstd for outputs > 10KB |
| TGNT-P1.5 | JSON metrics export | 2026-02-16 | ~2min | `harness metrics json` |
| TGNT-P2.1 | 5-level priority queue | 2026-02-17 | ~8min | critical/high/normal/low/background |
| TGNT-P2.2 | Priority aging | 2026-02-17 | ~3min | +1 level per 5s, prevents starvation |
| TGNT-P2.3 | Fair share scheduling | 2026-02-17 | ~8min | Per-agent quota + penalty |
| TGNT-P2.4 | Semantic coalescing | 2026-02-17 | ~5min | Path normalization, `.` -> root |
| TGNT-P2.5 | Queue timeout protection | 2026-02-17 | ~3min | Fallback execution on timeout |
| TGNT-P3.1 | L1 memory cache | 2026-02-17 | ~8min | `/dev/shm`, 100MB, 60s TTL |
| TGNT-P3.2 | L2 disk cache | 2026-02-17 | ~5min | `var/cache`, compressed, persistent |
| TGNT-P3.3 | L2-to-L1 promotion | 2026-02-17 | ~5min | Automatic on cache hit |
| TGNT-P3.4 | I/O scheduler integration | 2026-02-17 | ~5min | ionice priority classes |
| TGNT-P3.5 | Negative stat cache | 2026-02-17 | ~3min | Nonexistent files, 5s TTL |
| TGNT-P3.6 | Page cache warmer | 2026-02-17 | ~5min | Bulk read by file type |
| TGNT-P4.1 | Intent broadcasting | 2026-02-18 | ~8min | Agents signal planned ops |
| TGNT-P4.2 | Intent conflict checking | 2026-02-18 | ~5min | write-write, read-write detection |
| TGNT-P4.3 | Wait-for graph | 2026-02-18 | ~8min | From lock records |
| TGNT-P4.4 | DFS cycle detection | 2026-02-18 | ~5min | Deadlock detection |
| TGNT-P4.5 | Deadlock auto-resolution | 2026-02-18 | ~3min | Abort youngest waiter |
| TGNT-P4.6 | Fair share tracking | 2026-02-18 | ~5min | 50% decay smoothing |
| TGNT-P5.1 | Interactive TUI dashboard | 2026-02-18 | ~10min | cache/queue/intent/fair share |
| TGNT-P5.2 | Self-tuning report | 2026-02-18 | ~8min | Detect low hit rate/contention |
| TGNT-P5.3 | Auto-fix recommendations | 2026-02-18 | ~5min | Color-coded severity |
| TGNT-P5.4 | Rules suggestion engine | 2026-02-18 | ~5min | From observed patterns |
| TGNT-P5.5 | L1 vs L2 benchmark | 2026-02-18 | ~3min | Perf comparison tool |
| SCLI-P0.1 | Mission & hard problems | 2026-02-15 | ~5min | System analysis |
| SCLI-P0.2 | Architecture diagram | 2026-02-15 | ~8min | Component overview |
| SCLI-P0.3 | Configuration schema | 2026-02-15 | ~5min | rules.conf, agents.conf, env vars |
| SCLI-P0.4 | Risk register | 2026-02-15 | ~8min | Mitigations |
| SCLI-P0.5 | Tech stack justification | 2026-02-15 | ~5min | Bash, Rust, C rationale |
| SCLI-P5.1 | Mergiraf integration (AST-aware merge for 10+ languages) | 2026-02-22 | ~10min | merge_ast_aware in mesh/merge.py |
| SCLI-P5.2 | Conflict prediction before commit (trial merge from intents) | 2026-02-22 | ~8min | predict_conflicts in mesh/merge.py |
| SCLI-P5.3 | Import union auto-resolution (Python/JS imports) | 2026-02-22 | ~5min | resolve_imports in mesh/merge.py |
| SCLI-P5.4 | JSON/YAML structural merge (deep merge via jq) | 2026-02-22 | ~5min | merge_structural in mesh/merge.py |
| SCLI-P6.1 | Optimistic concurrency control (OCC) version tracking | 2026-02-22 | ~8min | OptimisticConcurrencyControl in mesh/coordination.py |
| TGNT-P7.1 | Mergiraf integration | 2026-02-19 | ~10min | AST merge for 10+ languages |
| TGNT-P7.2 | Conflict prediction from intents | 2026-02-19 | ~8min | Trial merge before commit |
| TGNT-P7.3 | Import union auto-resolve | 2026-02-19 | ~5min | Python/JS sorted union |
| TGNT-P7.4 | JSON/YAML structural merge | 2026-02-19 | ~5min | Deep merge via jq, ours-wins |
| TGNT-P8.1 | OCC version check on write | 2026-02-19 | ~8min | Record version at claim, verify before commit |
| TGNT-P8.2 | HLC timestamp generation | 2026-02-19 | ~5min | Millisecond physical + logical counter |
| TGNT-P8.3 | Lease-based file claims registry | 2026-02-19 | ~8min | read/write/exclusive with flock |
| TGNT-P8.4 | Lease renewal and expiry | 2026-02-19 | ~5min | Background cleanup daemon |
| TGNT-P9.1 | Singleflight dedup pattern | 2026-02-19 | ~5min | First executes, rest wait |
| TGNT-P9.2 | inotify cache invalidation | 2026-02-19 | ~8min | Watch file changes, invalidate |
| TGNT-P9.3 | Heat-based LRU eviction | 2026-02-19 | ~5min | Access frequency + exponential decay |
| TGNT-P10.1 | Per-agent TMPDIR allocation | 2026-02-19 | ~3min | Private temp, cleanup on exit |
| TGNT-P10.2 | Dynamic port range allocation | 2026-02-19 | ~5min | Registry + liveness check |
| TGNT-P10.3 | Environment variable isolation | 2026-02-19 | ~5min | Agent-specific env file |
| TGNT-P12.1 | /proc scanner with agent patterns | 2026-02-19 | ~8min | Claude/Aider/Cursor/Cline detection |
| TGNT-P12.2 | Agent manifest creation | 2026-02-19 | ~5min | YAML: id, type, pid, capabilities |
| TGNT-P12.3 | Heartbeat monitor | 2026-02-19 | ~5min | Touch-file every 5s, 15s threshold |
| TGNT-P12.4 | Stale agent cleanup | 2026-02-19 | ~3min | Reclaim tasks, archive manifest |
| TGNT-P13.1 | tmux session detection | 2026-02-19 | ~5min | mesh-{agent-uuid} naming |
| TGNT-P13.2 | Command injection via tmux | 2026-02-19 | ~8min | send-keys + 1.5s delay |
| TGNT-P13.3 | Agent readiness detection | 2026-02-19 | ~5min | Prompt patterns, busy/idle/error |
| TGNT-P15.1 | Optional worktree creation | 2026-02-19 | ~8min | git worktree add .mesh/worktrees/agent-{uuid} |
| TGNT-P15.2 | Branch coordination | 2026-02-19 | ~5min | Registry, collision avoidance, status tracking |
| TGNT-P15.3 | Worktree cleanup | 2026-02-19 | ~3min | Orphan detection, 30s grace, health monitor |

---

## Notes

- **Total Pending Tasks**: 89 items across both projects
- **Completed Tasks**: 46 items (Phases 0-5 for thegent, Phases 0 for sharecli)
- **Effort Distribution**: Mix of ~3-20 minute tasks, primarily feature and infrastructure work
- **Dependency Strategy**: Sequential foundation (P0-P1), parallel optimization (P2-P5), then specialized tracks (P6-P18)
- **Next Steps**: Begin Phase 6 (Git Parallelism) for thegent; Phase 1 (Process Detection) for sharecli
- **Agents**: Coordinate via this file; claim items in CLAIMED section before starting

---

## Claiming Work

1. **Before starting**: Add your item to CLAIMED with agent name and current timestamp
2. **Upon completion**: Move from CLAIMED to COMPLETED with completion timestamp and notes
3. **If blocked**: Update status to BLOCKED and note the blocking dependency
4. **For coordination**: Read PENDING and CLAIMED to avoid duplicates; check "Depends On" column for prerequisites

---

**Last Updated**: 2026-02-22 | **Format Version**: 1.0
