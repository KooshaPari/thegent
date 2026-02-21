# Unified Work Stream — Canonical

> **Purpose**: Single source of truth for all project work. All agents read this file before picking work.
> **Claim before starting**: Append to CLAIMED. Move to COMPLETED when done.
> **Incorporator**: Run `thegent plan incorporate` to merge new fragments from plans, research, specs.
> **Last Audited**: 2026-02-21

---

## Instructions for Agents

1. **Before picking work**: Read BACKLOG; filter out items in CLAIMED; pick items whose Depends are satisfied.
2. **When starting**: Append to CLAIMED (ID, Agent, Started). Use unique agent_id.
3. **When completing**: Remove from CLAIMED; add to COMPLETED; update source plan if applicable.
4. **Incorporator**: Run `thegent plan incorporate` to merge new fragments from plans, research, specs.

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
**Completed:** 2026-02-20 — 13 Python perf tests. TTLCache(maxsize=1, ttl=300) was already implemented; added public invalidate_router_cache() for external callers.
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
**Status:** in_progress
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
2. Reduced `impl.py` line count in baseline from `3776` to `3706` (current baseline artifact refresh below).
3. Extracted MCP tool icon map from `src/thegent/mcp/server.py` into `src/thegent/mcp/server_tool_icons.py` and kept server wiring through a single import (`from thegent.mcp.server_tool_icons import TOOL_ICONS`).
4. Refreshed monolith baseline evidence (`docs/reports/artifacts/wl120-monolith-baseline-2026-02-21.{json,txt}`) and LOC metrics (`.quality/loc-metrics.json`) after the extraction pass.
5. Extracted duplicated pre-work governance hard-gate logic from both `src/thegent/cli/commands/impl.py` and `src/thegent/cli/commands/work_stream_impl.py` into shared `src/thegent/cli/services/pre_work_gate_helpers.py`, preserving both command modules via wrapper functions for contract stability.
6. Added parity coverage for extracted gate wrappers in `tests/test_wl125_pre_work_gate_helpers_parity.py`.
7. Extracted shared work-stream orchestration surface (`do_next`, `wait_next`, `spawn_next`, `claim`, `complete`, `incorporate`) into `src/thegent/cli/services/work_stream_orchestration.py`; both `impl.py` and `work_stream_impl.py` now delegate through thin wrappers.
8. Added governance regression gate in `scripts/check_instruction_architecture.py` to enforce pre-work hard-gate single-source ownership and wrapper-only command modules.

**Blockers checklist (explicit):**
- [ ] Missing deliverable (as of 2026-02-21): monolith ceilings are only partially met in refreshed baseline collector output (`cli.py` 49 LOC vs `<2000` target met; `impl.py` 1268 LOC vs `<2000` target met; `mcp/server.py` 952 LOC vs `<500` target unmet; source: `docs/reports/artifacts/wl120-monolith-baseline-2026-02-21.json` + `.txt`). Next step: continue Wave-3+ extractions in `docs/changes/cli-dag-extraction/tasks.md` and `docs/changes/mcp-server-extraction/tasks.md` until all three ceilings are satisfied.
- [ ] Missing deliverable: WL-120 acceptance trend ("declining `src/thegent/*.py` LOC for 3 consecutive daily snapshots") is still not met; day-end commit evidence remains `122545 -> 117587 -> 117587` (`2026-02-19` through `2026-02-21`, source: `docs/reports/artifacts/wl120-wl136-loc-trend-2026-02-21.md`). Next step: record a lower 2026-02-22 day-end snapshot after additional cuts.
- [ ] Completion criteria status (objective): **NOT MET** as of 2026-02-21 because both required gates are still open (full monolith-ceiling compliance and 3-day declining LOC trend).

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
**Status:** in_progress (2026-02-21 boundary-refresh slice)
**Priority:** P0 (blocker)
**Area:** architecture, python
**Effort:** M (half day)
**Blocked by:** WL-120 LOC-trend and monolith reduction still open
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
- [ ] Missing deliverable (as of 2026-02-21): WL-136 exit criterion requiring a decreasing core LOC trend is still not met; attached evidence `docs/reports/artifacts/wl120-wl136-loc-trend-2026-02-21.md` shows `1267 -> 1464 -> 1464` for core-boundary LOC.
- [ ] Exact blocker (as of 2026-02-21): no newer day-end snapshot (2026-02-22) is available yet to prove a strict decline below `1464`; owner/date mapping for remaining mixed-surface reductions is still pending.

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
**Status:** in_progress (2026-02-21 closeout slice)
**Priority:** P0 (blocker)
**Area:** architecture, runtimes
**Effort:** XL (multi-week)
**Blocked by:** WL-120
**Source:** [docs/plans/2026-02-21-PY-RUST-ZIG-MOJO-DECOMPOSITION-MAP.md], [contracts/runtime/zig_abi_contract_v1.json], [contracts/runtime/mojo_kernel_contract_v1.json], [scripts/wl138_decomposition_progress.py], [tests/test_wl138_decomposition_progress.py], [docs/reports/artifacts/wl138_decomposition_progress.json]

Implement the full decomposition program:
1. Python monolith cuts (`cli.py`, `impl.py`, `mcp/server.py`).
2. Rust hook decomposition (`crates/thegent-hooks/src/main.rs`, `hooks/hook-dispatcher/src/main.rs`).
3. Zig ABI contract test wiring and promotion checks.
4. Mojo kernel correctness + benchmark harness with promotion gates.

**Blockers checklist (explicit):**
- [ ] Dependency blocker (precise, as of 2026-02-21): WL-120 remains `in_progress` with unresolved acceptance criteria in this file (revalidated monolith ceiling gate is still open: `cli.py` 49 vs `<2000` met, `impl.py` 1268 vs `<2000` met, `mcp/server.py` 952 vs `<500` unmet; and 3-day LOC decline gate still open: `122545 -> 117587 -> 117587`), so WL-138 cannot be promoted to `COMPLETED` yet.
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
| WL-136 | codex-batch-20260221 | 2026-02-21 | Boundary refresh complete (tests/scripts green); still blocked on 3-day core LOC decline evidence |
| WL-078 | agent-a | 2026-02-21 | Batch wave-1 (5x6): execute do-next + report |
| WL-101 | agent-a | 2026-02-21 | Batch wave-1 (5x6): execute do-next + report |
| WL-102 | agent-a | 2026-02-21 | Batch wave-1 (5x6): execute do-next + report |
| WL-103 | agent-a | 2026-02-21 | Batch wave-1 (5x6): execute do-next + report |
| WL-105 | agent-a | 2026-02-21 | Batch wave-1 (5x6): execute do-next + report |
| WL-107 | agent-b | 2026-02-21 | Batch wave-1 (5x6): execute do-next + report |
| WL-108 | agent-b | 2026-02-21 | Batch wave-1 (5x6): execute do-next + report |
| WL-109 | agent-b | 2026-02-21 | Batch wave-1 (5x6): execute do-next + report |
| WL-110 | agent-b | 2026-02-21 | Batch wave-1 (5x6): execute do-next + report |
| WL-114 | agent-b | 2026-02-21 | Batch wave-1 (5x6): execute do-next + report |
| WL-115 | agent-c | 2026-02-21 | Batch wave-1 (5x6): execute do-next + report |
| WL-116 | agent-c | 2026-02-21 | Batch wave-1 (5x6): execute do-next + report |
| WL-118 | agent-c | 2026-02-21 | Batch wave-1 (5x6): execute do-next + report |
| WL-119 | agent-c | 2026-02-21 | Batch wave-1 (5x6): execute do-next + report |
| WL-120 | agent-c | 2026-02-21 | Batch wave-1 (5x6) + extraction waves: moved run pre-flight guard/concurrency block to `run_guard_helpers.py`, moved MCP tool icon map to `server_tool_icons.py`, extracted shared pre-work gate helpers to `pre_work_gate_helpers.py`, extracted shared work-stream orchestration to `work_stream_orchestration.py`, added instruction-architecture regression gate for pre-work helper ownership, refreshed baseline (`impl.py` 1268, `mcp/server.py` 952) |
| WL-122 | agent-d | 2026-02-21 | Batch wave-1 (5x6): execute do-next + report |
| WL-104 | agent-d | 2026-02-21 | Batch wave-1 (5x6): dependency prep + report |
| WL-106 | agent-d | 2026-02-21 | Batch wave-1 (5x6): dependency prep + report |
| WL-111 | agent-d | 2026-02-21 | Batch wave-1 (5x6): dependency prep + report |
| WL-117 | claude-sonnet-4-6 | 2026-02-20 | COMPLETED: VS Code extension — agentServerClient, sessionListProvider, contextBudgetStatusBar, approvalWebviewPanel, extension.ts; 31 tests passing; tsc --noEmit clean |
| WL-121 | agent-e | 2026-02-21 | Batch wave-1 (5x6): dependency chain execution + report |
| WL-123 | agent-e | 2026-02-21 | Batch wave-1 (5x6): dependency prep + report |
| WL-124 | agent-e | 2026-02-21 | Batch wave-1 (5x6): dependency prep + report |
| WL-125 | agent-e | 2026-02-21 | Batch wave-1 (5x6): dependency prep + report |
| WL-126 | agent-e | 2026-02-21 | Batch wave-1 (5x6): dependency prep + report |
| WL-079 | agent-f | 2026-02-21 | Batch wave-1 (5x6): dependency prep + report |
| WL-093 | agent-f | 2026-02-21 | Batch wave-1 (5x6): dependency prep + report |
| WL-094 | agent-f | 2026-02-21 | Batch wave-1 (5x6): dependency prep + report |
| WL-095 | agent-f | 2026-02-21 | Batch wave-1 (5x6): dependency prep + report |
| WL-096 | claude-sonnet-4-6 | 2026-02-20 | COMPLETED: revision queue wired in VetterOrchestrator; 30 tests in test_wl096_vetter_revision_queue.py |
| WL-138 | codex-orchestrator-20260221 | 2026-02-21 | In progress: execution-level decomposition gates are green (`5/5` checkpoints, `4/4` gates), but dependency blocker remains open in WL-120 (monolith ceilings + LOC-trend acceptance unresolved) |
| WL-078 | codex-orchestrator-20260221 | 2026-02-21 | Claimed next: implement Python benchmark suite (initial runnable lane + docs + smoke validation) |

---

## COMPLETED (historical reference)

> All items below were completed by various agents between 2026-02-18 and 2026-02-20. See WORK_STREAM prior version for full entries with completion notes.

| ID | Completed | Summary |
|----|-----------|---------|
| docgen-link-checker | 2026-02-20 | scripts/check-docs-links.py exists, integrated in npm as docs:links |
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
