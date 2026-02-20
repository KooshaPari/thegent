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
| ~~heliosShield-smart-merge~~ | ~~Integrate Mergiraf for AST-aware merging~~ | TEAMMATES_RESEARCH_AND_PLAN.md | DONE | - |
| ~~compositor-caching~~ | ~~Implement composition caching for renders~~ | COMPOSITOR_RESEARCH_AND_ENHANCEMENT_PLAN.md | DONE | - |
| ~~compositor-perf-profiling~~ | ~~Add render performance profiling~~ | COMPOSITOR_RESEARCH_AND_ENHANCEMENT_PLAN.md | DONE | - |
| ~~compositor-cli-integration~~ | ~~Integrate compositor with CLI progress bars~~ | COMPOSITOR_RESEARCH_AND_ENHANCEMENT_PLAN.md | DONE | - |
| ~~ux-linting-accelerator~~ | ~~Create oxlint-based linting accelerator wrapper~~ | ESLINT_AUDIT.md | DONE | - |
| ~~ux-terminal-keepalive~~ | ~~Integrate terminal keepalive into long-running tasks~~ | WAIT_KEEPALIVE_IMPLEMENTATION.md | DONE | - |
| ~~borrow-thegent-mcp-tools~~ | ~~Port thegent MCP tools to other projects~~ | CROSS_PROJECT_FEATURE_BORROWING_PLAN.md | DONE | COMPLETED |
| ~~borrow-plangent-subagents~~ | ~~Integrate plangent sub-agents into thegent~~ | CROSS_PROJECT_FEATURE_BORROWING_PLAN.md | DONE | - |
| ~~borrow-dex-flash-agents~~ | ~~Port dex flash agents to other projects~~ | CROSS_PROJECT_FEATURE_BORROWING_PLAN.md | DONE | - |
| ~~impl-cross-project-registry~~ | ~~Unified persona registry across projects~~ | CROSS_PROJECT_INTEGRATION_GUIDE.md | DONE | - |
| ~~impl-cross-project-ipc~~ | ~~File-based IPC protocol for cross-project agents~~ | CROSS_PROJECT_INTEGRATION_GUIDE.md | DONE | - |
| ~~swarm-per-gate-logging~~ | ~~Add per-gate logging to ConcurrencyController~~ | SWARM_OPTIMIZATION_SCHEDULING_DEEP_RESEARCH.md | DONE | - |
| ~~swarm-critical-lane~~ | ~~Implement critical lane reservation~~ | SWARM_OPTIMIZATION_SCHEDULING_DEEP_RESEARCH.md | DONE | - |
| ~~swarm-priority-queue~~ | ~~Add priority queue for runs~~ | SWARM_OPTIMIZATION_SCHEDULING_DEEP_RESEARCH.md | DONE | swarm-critical-lane |
| ~~swarm-redis-concurrency~~ | ~~Redis-backed concurrency limits~~ | SWARM_OPTIMIZATION_SCHEDULING_DEEP_RESEARCH.md | DONE | - |
| ~~swarm-redlock-atomic~~ | ~~Use Redlock for atomic acquire/release~~ | SWARM_OPTIMIZATION_SCHEDULING_DEEP_RESEARCH.md | DONE | swarm-redis-concurrency |
| ~~swarm-token-bucket~~ | ~~Token bucket for API rate limits~~ | SWARM_OPTIMIZATION_SCHEDULING_DEEP_RESEARCH.md | DONE | COMPLETED |
| ~~swarm-dag-prioritization~~ | ~~DAG critical-path prioritization~~ | SWARM_OPTIMIZATION_SCHEDULING_DEEP_RESEARCH.md | DONE | - |
| ~~cache-multi-level~~ | ~~Implement multi-level caching (memory → disk → network)~~ | CACHING_INDEXING_PREWARMING_DEEP_RESEARCH.md | DONE | - |
| ~~cache-diskcache-migration~~ | ~~Migrate to diskcache for disk-backed cache~~ | CACHING_INDEXING_PREWARMING_DEEP_RESEARCH.md | DONE | cache-multi-level |
| ~~index-file-indexing~~ | ~~Add file indexing (fd-style) for common find patterns~~ | CACHING_INDEXING_PREWARMING_DEEP_RESEARCH.md | DONE | - |
| ~~cache-frecency-algorithm~~ | ~~Implement frecency algorithm for history~~ | CACHING_INDEXING_PREWARMING_DEEP_RESEARCH.md | DONE | cache-multi-level |
| ~~cache-predictive-pre-warming~~ | ~~Add predictive pre-warming based on usage~~ | CACHING_INDEXING_PREWARMING_DEEP_RESEARCH.md | DONE | cache-multi-level |
| ~~tenacity-migrate-cli~~ | ~~Migrate EAGAIN retry in cli_impl.py to tenacity~~ | TENACITY_RETRY_AUDIT_PLAN.md | DONE | - |
| ~~tenacity-migrate-loop~~ | ~~Migrate loop_controller.py retry to tenacity~~ | TENACITY_RETRY_AUDIT_PLAN.md | DONE | - |
| ~~shell-consolidate-configs~~ | ~~Consolidate Zsh configs, remove .zshrc.optimized~~ | SHELL_CONFIG_AUDIT_AND_CONSOLIDATION_PLAN.md | DONE | - |
| ~~bkm-05-state-shm~~ | ~~State-SHM (CircuitBreaker + XP in memory-mapped Rust)~~ | PYTHON_FRONTMATTER_NATIVE_BACKMATTER_AUDIT_PLAN.md | DONE | - |
| ~~bkm-06-git-native~~ | ~~thegent-git (HEAD, status, diff stats via gitoxide)~~ | PYTHON_FRONTMATTER_NATIVE_BACKMATTER_AUDIT_PLAN.md | DONE | - |
| ~~bkm-07-hook-dispatcher-extend~~ | ~~Extend hook-dispatcher (native secret scan, shell detection)~~ | AUDIT_REMEDIATION_PLAN_2026_02_19.md | DONE | COMPLETED |
| ~~bkm-08-discovery-binary~~ | ~~thegent-discovery binary (consolidate discovery)~~ | PYTHON_FRONTMATTER_NATIVE_BACKMATTER_AUDIT_PLAN.md | DONE | COMPLETED |
| ~~bkm-09-watcher-daemon~~ | ~~thegent-watcher daemon (multi-tenant file watcher)~~ | PYTHON_FRONTMATTER_NATIVE_BACKMATTER_AUDIT_PLAN.md | DONE | COMPLETED |
| ~~bkm-10-jsonl-parser~~ | ~~JSONL streaming parser in Rust~~ | PYTHON_FRONTMATTER_NATIVE_BACKMATTER_AUDIT_PLAN.md | DONE | - |
| ~~bkm-11-governance-scanner~~ | ~~Native governance scanner (obfuscated triggers, Rust built)~~ | AUDIT_REMEDIATION_PLAN_2026_02_19.md | DONE | COMPLETED |
| ~~impl-os-user-adapter~~ | ~~OS-level user creation adapter (Linux/macOS/Win)~~ | AUDIT_REMEDIATION_PLAN_2026_02_19.md | DONE | COMPLETED |
| ~~heliosShield-bridge-fix~~ | ~~Fix heliosShield bridge and tests~~ | AUDIT_REMEDIATION_PLAN_2026_02_19.md | DONE | COMPLETED |
| ~~litellm-responses-handler~~ | ~~Create LiteLLM Router Responses API handler~~ | LITELLM_HARNESS_MASTER_PLAN.md | DONE | - |
| ~~litellm-clode-integration~~ | ~~Route Claude Code through LiteLLM Router~~ | LITELLM_HARNESS_MASTER_PLAN.md | DONE | litellm-responses-handler | ⏳ Claimed (agent-koosha) |
| ~~acp-client-adapter~~ | ~~Implement ACP Client Adapter~~ | ACP_ADAPTERS_DESIGN_2026-02-18.md | DONE | - |
| ~~acp-mcp-bridge~~ | ~~Implement MCP `<->` ACP Bridge~~ | ACP_ADAPTERS_DESIGN_2026-02-18.md | DONE | - |
| ~~resource-gpu-utilization~~ | ~~GPU utilization tracking (nvidia-ml-py)~~ | ADVANCED_RESOURCE_MANAGEMENT_SYSTEM.md | DONE | - |
| ~~resource-network-bandwidth~~ | ~~Network bandwidth monitoring~~ | ADVANCED_RESOURCE_MANAGEMENT_SYSTEM.md | DONE | - |
| ~~resource-disk-queue-depth~~ | ~~Disk I/O queue depth monitoring~~ | ADVANCED_RESOURCE_MANAGEMENT_SYSTEM.md | DONE | COMPLETED |
| ~~resource-distributed-coordination~~ | ~~Distributed resource coordination~~ | ADVANCED_RESOURCE_MANAGEMENT_SYSTEM.md | DONE | COMPLETED |
| ~~fastmcp-elicitation-api~~ | ~~Implement FastMCP elicitation API~~ | FASTMCP_IMPLEMENTATION_GUIDE.md | DONE | - |
| ~~fastmcp-task-mode~~ | ~~Implement FastMCP task mode~~ | FASTMCP_IMPLEMENTATION_GUIDE.md | DONE | fastmcp-context-api |
| ~~fastmcp-storage-eventstore~~ | ~~Implement FastMCP Storage/EventStore integration~~ | FASTMCP_IMPLEMENTATION_GUIDE.md | DONE | fastmcp-context-api |
| ~~research-governance-override-events~~ | ~~Add override expiry event emission~~ | GOVERNANCE_WP_GAPS_EXPANDED.md | DONE | WP-3003 |
| ~~impl-supermemory-client~~ | ~~Implement SupermemoryClient in thegent-memory~~ | SUPERMEMORY_INTEGRATION_RESEARCH_REPORT.md | DONE | - |
| ~~impl-memory-manager-integration~~ | ~~Integrate MemoryManager into main agent loop~~ | SUPERMEMORY_INTEGRATION_RESEARCH_REPORT.md | DONE | impl-supermemory-client |
| ~~impl-pareto-router~~ | ~~Implement ParetoRouter in thegent-router~~ | PARETO_ROUTING_RESEARCH_REPORT.md | DONE | - |
| ~~impl-cost-aware-router~~ | ~~Implement CostAwareRouter in governance catalog~~ | ECONOMIC_GOVERNANCE_RESEARCH_REPORT.md | DONE | - |
| ~~wire-maif-agent-runner~~ | ~~Wire MAIF artifacts into AgentRunner/ExecutionEngine~~ | MAIF_ACTION_ARTIFACTS_RESEARCH_REPORT.md | DONE | impl-thegent-maif-crate |
| ~~impl-simulation-replay-engine~~ | ~~Implement SimulationReplay engine in UX~~ | SIMULATION_REPLAY_RESEARCH_REPORT.md | DONE | - |
| ~~setup-tailscale-nodes~~ | ~~Configure Tailscale for Mac/Windows compute offload~~ | COMPUTE_OFFLOAD_RESEARCH_REPORT.md | DONE | - |
| ~~setup-syncthing-workspace~~ | ~~Set up Syncthing for workspace synchronization~~ | COMPUTE_OFFLOAD_RESEARCH_REPORT.md | DONE | - |
| ~~impl-idea-seed-scanner~~ | ~~Implement Idea Seed scanner in CLI~~ | IDEA_SEED_SYSTEM_RESEARCH_REPORT.md | DONE | - |
| ~~impl-remote-executor~~ | ~~Implement RemoteExecutor in Python~~ | REMOTE_COMPUTE_IMPL_RESEARCH_REPORT.md | DONE | setup-tailscale-nodes |
| ~~enhance-macos-sandbox~~ | ~~Enhance macOS sandbox profile for finer control~~ | USER_ISOLATION_IMPL_RESEARCH_REPORT.md | DONE | - |
| ~~impl-macos-desktop-automation~~ | ~~Implement macOS Desktop Automation provider~~ | CROSS_PLATFORM_RESEARCH_REPORT.md | DONE | - |
| ~~impl-library-phase1~~ | ~~Migrate HTTP (httpx) and Retry (tenacity)~~ | LIBRARY_REPLACEMENT_RESEARCH_REPORT.md | DONE | install-library-deps |
| ~~prototype-federated-policy~~ | ~~Prototype FederatedPolicyEngine in governance~~ | PHASE_GOVERNANCE_CONSOLIDATED_REPORT.md | DONE | - |
| ~~impl-sync-command~~ | ~~Implement thegent sync command structure~~ | SYNC_DX_IMPROVEMENTS_REPORT.md | DONE | - |
| ~~research-cross-platform-remote~~ | ~~Remote compute implementation~~ | CROSS_PLATFORM_RESEARCH_CONSOLIDATED.md | DONE | HYBRID_ENV |
| ~~research-library-retry~~ | ~~Migrate manual retry loops to tenacity (4 files)~~ | LIBRARY_REPLACEMENT_CONSOLIDATED.md | DONE | ✅ Complete |
| ~~research-library-cache~~ | ~~Replace custom caching with cachetools (5 files)~~ | LIBRARY_REPLACEMENT_CONSOLIDATED.md | DONE | ✅ Complete |
| ~~research-library-circuit-breaker~~ | ~~Replace custom circuit breaker with pybreaker (1 file)~~ | LIBRARY_REPLACEMENT_CONSOLIDATED.md | DONE | ✅ Complete |
| ~~research-library-yaml~~ | ~~Replace PyYAML with ruamel.yaml (15 files)~~ | LIBRARY_REPLACEMENT_CONSOLIDATED.md | DONE | ✅ Complete |
| ~~research-library-ansi~~ | ~~Replace custom ANSI stripping with rich (5 files)~~ | LIBRARY_REPLACEMENT_CONSOLIDATED.md | DONE | ✅ Complete |
| ~~scratch-doctor-fix~~ | ~~Proactive doctor --fix for detected environment issues~~ | scratchpad/session_review.md | DONE | — |
| ~~muxless-acp-session-endpoints~~ | ~~Extend ACP with session/attach, session/inspect, session/send~~ | MUXLESS_AGENT_SESSION_MANAGEMENT_2026-02-19.md | DONE | acp-server-adapter |
| ~~impl-zig-rust-interop-poc~~ | ~~Implement Zig-Rust C ABI Interop POC (Rust calls zmx)~~ | ZIG_RUST_ECOSYSTEM_RESEARCH_2026-02-19.md | DONE | - |
| ~~impl-zmx-c-abi~~ | ~~Expose zmx C ABI for list/attach/capture (if not present)~~ | ZIG_RUST_ECOSYSTEM_RESEARCH_2026-02-19.md | DONE | - |
| ~~impl-rust-zmx-wrapper~~ | ~~Create Rust crate wrapping zmx C ABI~~ | ZIG_RUST_ECOSYSTEM_RESEARCH_2026-02-19.md | DONE | impl-zig-rust-interop-poc |
| wp-71001-registry-db | Implement ProjectRegistry SQLite schema | 2026-02-19-VERSIONING-AND-SHADOW-AUDIT-PLAN.md | P1 | WP-23001 |
| wp-71002-shadow-git | Implement ShadowAuditGit with secret scrubbing | 2026-02-19-VERSIONING-AND-SHADOW-AUDIT-PLAN.md | P1 | wp-71001-registry-db |
| wp-71003-episode-ctrl | Integrate EpisodeController into agent loop | 2026-02-19-VERSIONING-AND-SHADOW-AUDIT-PLAN.md | P1 | wp-71002-shadow-git |
| wp-71004-audit-cli | Add `thegent audit log/diff` commands | 2026-02-19-VERSIONING-AND-SHADOW-AUDIT-PLAN.md | P2 | wp-71003-episode-ctrl |
| wp-71005-hierarchy-cli | Add `thegent plan milestone/sprint` commands | 2026-02-19-VERSIONING-AND-SHADOW-AUDIT-PLAN.md | P2 | wp-71001-registry-db |

*Run `thegent plan incorporate` to refresh from plans, research, specs.*

---

## CLAIMED (in progress — do not pick)

| ID | Agent | Started | Notes |
|----|-------|---------|-------|
## COMPLETED (this session / recent)
| ID | Agent | Completed | Notes |
|----|-------|-----------|-------|
| wire-maif-agent-runner | thegent-main-session | 2026-02-19 | MAIF wired: MAIFRunner.record_run_start/record_run_end in ExecutionEngine and cli run_impl; auditor.generate_maif_artifact + persist for run registry |
| swarm-fix-macos-sampling | agent-koosha | 2026-02-19 | Fixed macOS vm_stat sampling: now includes speculative/purgeable pages and uses dynamic page size from sysctl. Matches psutil. |
| swarm-hysteresis-env | agent-koosha | 2026-02-19 | Exposed hysteresis parameters (upper/lower/dwell) via THGENT_HYSTERESIS_* environment variables in ThegentSettings. |
| heliosShield-git-overhaul | agent-koosha | 2026-02-19 | Overhauled Git CLI in `thegent git`; replaced standard `git` with parallel-safe, multitenant version using private index files and atomic CAS commits via `thegent-hooks` smart dispatcher; integrated AST-aware `merge` via `Mergiraf`; unified `lock-cleanup` and service management; ensured transparent pass-through for unhandled commands. |
| swarm-redlock-atomic | agent-l1 | 2026-02-19 | RedlockController with SETNX+Lua release; in-memory fallback; 56 tests pass, ruff clean |
| resource-gpu-utilization | agent-j9 | 2026-02-19 | GpuMonitor (is_available/get_gpus/get_total_utilization); nvidia-smi fallback; GpuInfo dataclass; GpuMonitorError; pynvml dynamic import via _import_pynvml(); _run_subprocess helper; exported from resources/__init__.py; 39 tests pass, ruff clean |
| ux-terminal-keepalive | agent-j7 | 2026-02-19 | TerminalKeepalive + KeepaliveConfig; background daemon thread; tty-only output (sys.stdout.isatty()); context manager; keepalive() convenience fn; integrated into cli_impl.py run_impl via THGENT_KEEPALIVE_INTERVAL env; 23 tests pass, ruff clean |
| scratch-doctor-fix | agent-k5 | 2026-02-19 | DoctorRunner + DoctorCheck; 8 checks (python_version, ANTHROPIC_API_KEY, thegent_home_dir, thegent_sessions_dir, pyproject_toml, ruff, cargo, mcp_config_dir); --fix auto-creates dirs/configs; 41 tests pass, ruff clean |
| resource-distributed-coordination | agent-k2 | 2026-02-19 | DistributedResourceCoordinator (acquire/release/get_active_leases/cleanup_expired/get_available); file-lock backed (filelock.FileLock with JSON atomic write-rename fallback); ResourceLease dataclass with is_expired/to_dict/from_dict; ResourceCoordinationError; eager expired-lease purging on acquire; exported from resources/__init__.py; 33 tests pass, ruff clean |
| resource-disk-queue-depth | agent-k1 | 2026-02-19 | DiskMonitor (get_io_stats/sample_queue_depth/list_devices/get_disk_usage); psutil-based; DiskIoStats/DiskQueueSample; busy_time delta + Little's Law queue depth estimate; clamping for counter wrap-around; exported from resources/__init__.py; 42 tests pass, ruff clean |
| impl-remote-executor | agent-k6 | 2026-02-19 | RemoteExecutor (execute/execute_async/available_nodes); SSH via subprocess; round-robin node selection; RemoteTask/Result; env config THGENT_REMOTE_NODES/THGENT_REMOTE_SSH_USER; RemoteExecutorError; ClassVar SSH opts; async via run_in_executor; ping-based available_nodes; exported from compute/__init__.py; 41 tests pass, ruff clean |
| ux-linting-accelerator | agent-i3 | 2026-02-19 | LintingAccelerator in src/thegent/tools/linting_accelerator.py: is_oxlint_available/run_oxlint/run_eslint/run_ruff/lint(); oxlint ESLint-compat + flat JSON parsing; ruff JSON parsing; fast=True oxlint fast-path with ESLint fallback; scripts/lint-fast.sh shell wrapper; thegent lint run/check CLI subcommands in main.py; 38 tests in tests/tools/test_linting_accelerator.py; all pass, ruff clean |
| swarm-priority-queue | agent-l2 | 2026-02-20 | RunPriorityQueue with heapq + FIFO; cancel/drain/peek; lane integration; 58 tests pass, ruff clean |
| swarm-dag-prioritization | agent-k4 | 2026-02-19 | DagPrioritizer (add_task/compute_critical_path/get_priority_score/topological_sort/ready_tasks); cycle detection; DagTask; DagCycleError; Kahn's algorithm + standard CPM forward/backward pass; exported from orchestration/__init__.py; 49 tests pass, ruff clean |
| swarm-token-bucket | agent-k3 | 2026-02-19 | TokenBucket (consume/consume_blocking/try_consume/available/refill); thread-safe via threading.Condition; time.monotonic() refill; RateLimitedSwarmRunner with env config THGENT_RATE_TOKENS_PER_SEC/THGENT_RATE_BUCKET_SIZE; exported from orchestration/__init__.py; 46 tests pass, ruff clean |
| impl-simulation-replay-engine | agent-i5 | 2026-02-19 | SimulationReplayEngine in src/thegent/simulation/replay.py: ReplayEvent/ReplaySession dataclasses; load_session/replay/replay_from_event/compare_sessions/extract_tool_calls/generate_test_fixture/list_sessions; thegent replay list/run/diff CLI in src/thegent/commands/replay.py registered in main.py; backward-compat SimulationReplay alias; 35 tests in tests/simulation/test_replay.py; all pass, ruff clean |
| coordination-hybrid-strategy | agent-j1 | 2026-02-19 | HybridCoordinationStrategy with HIERARCHICAL/P2P/ADAPTIVE modes + CoordinationMetrics; mode selection by swarm_size+avg_load; env threshold THGENT_HIER_THRESHOLD; 37 tests pass, ruff clean |
| impl-compositor-manager | agent-i6 | 2026-02-19 | CompositorManager in src/thegent/ui/compositor_manager.py: Layout enum (SINGLE/SPLIT_H/SPLIT_V/GRID_2X2); CompositorSlot dataclass with weight validation; CompositorManager with add/remove/get/focus/switch_layout/render_all using single-line box-drawing; 41 tests in tests/ui/test_compositor_manager.py; all pass, ruff clean |
| borrow-dex-flash-agents | agent-j2 | 2026-02-19 | FlashAgent + FlashAgentConfig/Result; flash() convenience fn; thegent_flash MCP tool; 24 tests pass, ruff clean |
| setup-syncthing-workspace | agent-j4 | 2026-02-19 | SyncthingManager (get_devices/get_folders/is_available/add_folder/sync_status); httpx.AsyncClient; SyncthingDevice/Folder/Config; 34 tests pass, ruff clean |
| enhance-macos-sandbox | agent-i8 | 2026-02-19 | MacOSSandbox + SandboxLevel(NONE/READONLY/RESTRICTED/NETWORKED/FULL) in src/thegent/security/macos_sandbox.py; sandbox profiles in src/thegent/security/profiles/{readonly,restricted,networked}.sb; THGENT_SANDBOX_LEVEL env var integration in cli_impl.py; apply_to_command() wraps subprocess with sandbox-exec -f `&lt;profile>`; 39 tests in tests/security/test_macos_sandbox.py; all pass, ruff clean |
| bkm-09-watcher-daemon | agent-g6 | 2026-02-19 | WatcherDaemon in src/thegent/native/watcher_daemon.py: WatchEvent/WatchSpec dataclasses; PatternMatchingEventHandler-backed _SpecHandler; single watchdog Observer thread; add_watch/remove_watch/list_watches/start/stop/is_running; get_watcher_daemon() singleton; optional CircuitBreakerShm health integration; exported from native/__init__.py; 56 tests in tests/native/test_watcher_daemon.py all pass; ruff clean |
| muxless-termitty-introspection | agent-h2 | 2026-02-19 | TerminalCapture class + CaptureResult dataclass in src/thegent/tools/terminal_capture.py; 4-step fallback chain: tmux capture-pane -> ZmxBackend.capture -> /proc/{pid}/fd/1 (Linux) -> termitty VirtualTerminal; exported from tools/__init__.py; termitty installed in venv; 45 tests in tests/tools/test_terminal_capture.py; all pass, ruff clean |
| borrow-plangent-subagents | agent-i4 | 2026-02-19 | PlangentPlanner + PlangentExecutor in src/thegent/agents/plangent.py; thegent plan decompose CLI command in main.py; 49 tests in tests/agents/test_plangent.py; all pass, ruff clean |
| impl-rust-zmx-wrapper | agent-h4 | 2026-02-19 | crates/thegent-zmx: ZmxSession/ZmxState/ZmxClient idiomatic Rust types; list_sessions/attach/capture/send/create methods; sessions_to_json/sessions_from_json helpers; validate_session_name guard; zmx-native + live-zmx feature flags; path dep on thegent-zmx-interop; 27 unit tests + 2 doc tests all pass; 15 Python integration tests in tests/native/test_rust_zmx_wrapper.py all pass; workspace Cargo.toml updated |
| compositor-caching | agent-i1 | 2026-02-19 | TTLCache-backed render cache in Compositor (src/thegent/ui/compositor/compositor.py): cache keyed by (panel_name, content_hash); separate short-TTL error_cache for failing panels; invalidate(panel_name|None) API; cache_stats() CacheStats TypedDict; auto-invalidate on add_panel replace + remove_panel; CacheStats exported from ui/compositor/__init__.py; 24 tests in tests/ui/compositor/test_compositor_caching.py all pass; ruff clean |
| shell-consolidate-configs | agent-i9 | 2026-02-19 | ShellConfigFile/ShellConfigAuditor in src/thegent/tools/shell_config.py; audit()/find_duplicates()/find_duplicate_aliases()/generate_consolidated()/check_sourcing_order()/sourcing_graph(); scripts/shell-audit.sh runner; docs/guides/shell-config.md; 40 tests in tests/tools/test_shell_config.py all pass; ruff clean |
| serena-jetbrains-integration | agent-h1 | 2026-02-19 | JetBrainsConfig dataclass + JetBrainsIntegration (detect_installed_ides, write_mcp_config, read_existing_config, is_mcp_plugin_installed, setup_all) in src/thegent/integrations/jetbrains.py; platform-aware base dir detection (macOS/Linux/Windows); merges existing mcp.json; thegent jetbrains setup CLI command in main.py (--mcp-url, --project-root, --dry-run); docs/guides/jetbrains-integration.md guide; 48 tests in tests/integrations/test_jetbrains.py all pass; ruff clean |
| fastmcp-storage-eventstore | agent-h5 | 2026-02-19 | McpStorage (diskcache + JSON encoding) and McpEventStore (JSONL) in src/thegent/mcp_storage.py; get/set/delete/list_keys/clear + TTL for storage; emit/replay/subscribe/get_event for events; singleton registry via _SingletonRegistry; 4 MCP tools (thegent_storage_get, thegent_storage_set, thegent_events_emit, thegent_events_replay) registered in mcp_server.py; 43 tests in tests/mcp/test_storage_eventstore.py; all pass, ruff clean |
| cache-frecency-algorithm | agent-h8 | 2026-02-19 | FrecencyEntry dataclass + FrecencyCache (frequency*recency scoring, score=count*exp(-lambda*age), maxsize eviction, optional MultiLevelCache persistence) + FrecencyModelSelector in src/thegent/cache/frecency.py; exported from cache/__init__.py; 48 tests in tests/cache/test_frecency.py; all pass, ruff clean |
| swarm-redis-concurrency | agent-i10 | 2026-02-19 | RedisConcurrencyController (SETNX+EXPIRE) + RedisConfig + _InMemoryStore fallback in src/thegent/orchestration/redis_concurrency.py; make_redis_concurrency_controller factory; exported from orchestration __init__; THGENT_REDIS_HOST/PORT/DB/PASSWORD/KEY_PREFIX/CONCURRENCY_LIMIT added to ThegentSettings; graceful fallback when redis not installed or unreachable; 34 tests in tests/orchestration/test_redis_concurrency.py; all pass, ruff clean |
| cache-predictive-pre-warming | agent-i7 | 2026-02-19 | CachePreWarmer with WarmingStrategy dataclass; register_strategy/warm_key/warm_all/start_background/stop_background/get_stats; model_list_strategy + session_list_strategy built-ins; background daemon thread; in src/thegent/cache/pre_warmer.py; exported from cache/__init__.py; 44 tests in tests/cache/test_pre_warmer.py; all pass, ruff clean |
| impl-memory-manager-integration | agent-g3 | 2026-02-19 | MemoryManager in src/thegent/memory/memory_manager.py: wraps SupermemoryClient; load_context/save_discovery/get_session_context; no-op when THGENT_SUPERMEMORY_API_KEY absent; SupermemoryConfigError gracefully degrades; wired into run_impl() in cli_impl.py (load_context before FSM run, save_discovery on success); exported from memory/__init__.py; 31 tests in tests/memory/test_memory_manager.py; all pass, ruff clean |
| impl-cross-project-registry | agent-h6 | 2026-02-19 | PersonaRecord dataclass + CrossProjectRegistry in src/thegent/registry/cross_project.py; discover_personas() scans agents/*.md + parses YAML frontmatter; register_project() discovers and persists; search() case-insensitive capability filter; atomic save/load JSON at ~/.thegent/persona_registry.json; thegent registry register/search/list CLI in src/thegent/commands/registry.py registered in main.py; exported from src/thegent/registry/__init__.py; 36 tests in tests/registry/test_cross_project.py; all pass, ruff clean |
| impl-idea-seed-scanner | agent-h10 | 2026-02-19 | IdeaSeed dataclass + IdeaSeedScanner (scan_file, scan_directory, filter_by_type, to_work_stream_items, export_markdown) in src/thegent/commands/idea_seeds.py; 9 SEED_PATTERNS covering Python/JS/Rust; typer sub-app (seeds scan/export/add-to-workstream) registered in main.py; exported from commands/__init__.py; 53 tests in tests/commands/test_idea_seeds.py; all pass, ruff clean |
| muxless-acp-session-endpoints | agent-h3 | 2026-02-19 | SessionEndpoints helper class + 3 JSON-RPC handlers (session/attach, session/inspect, session/send) in src/thegent/adapters/acp_server.py; lazy ZmxBackend resolution via resolve_session_backend(); session/attach creates or attaches; session/inspect captures pane lines; session/send delivers text with optional enter; 36 tests in tests/adapters/test_acp_session_endpoints.py; all pass, ruff clean |
| fastmcp-tool-patterns | agent-g10 | 2026-02-19 | confirm_before_action/progress_with_fallback/choice_with_retry/retry_on_error decorators in src/thegent/mcp_tool_patterns.py; ToolAborted exception; thegent_delete_session + thegent_bulk_operation example tools registered in mcp_server.py; register_tool_pattern_tools(); 31 tests in tests/mcp/test_tool_patterns.py; all pass, ruff clean |
| acp-mcp-bridge | agent-g9 | 2026-02-19 | AcpMcpBridge in src/thegent/adapters/acp_mcp_bridge.py: mcp_tool_to_acp_task encodes MCP tool calls as ACP task payloads; acp_agent_to_mcp_tool calls any ACP agent via one-shot ACPClient and returns plain-text MCP response; get_mcp_tool_manifest introspects FastMCP app and emits ACP-compatible ACPToolDescriptor list; thegent_acp_invoke MCP tool in mcp_server.py; exported from adapters/__init__.py; 38 tests in tests/adapters/test_acp_mcp_bridge.py; all pass, ruff clean |
| compositor-error-boundaries | agent-g5 | 2026-02-19 | Added error_fallback (str or Callable), last_error, has_error, recover() to Panel; Compositor.render() delegates to Panel.render() error boundary; added render_all(), render_panel(), errored_panels(), recover_panel(), recover_all(), get_panel() to Compositor; 37 tests in tests/ui/compositor/test_compositor_error_boundaries.py; all pass, ruff clean |
| compositor-perf-profiling | agent-j6 | 2026-02-19 | CompositorProfiler + RenderProfile dataclass in src/thegent/ui/compositor/compositor.py; record/get_slowest/get_average/report/clear/record_count API; deque(maxlen=100) bounded storage; instrumented Compositor._render_cached() with time.perf_counter() timing; cache_hit flag propagated from both hit/miss and error_cache paths; CompositorProfiler+RenderProfile exported from ui/compositor/__init__.py and thegent.ui; 34 tests in tests/ui/compositor/test_compositor_profiling.py all pass, ruff clean |
| cache-diskcache-migration | agent-g1 | 2026-02-19 | Migrated quality_values._CACHE and speed_values._CACHE from plain TTLCache to MultiLevelCache (L1 in-process + L2 diskcache); migrated scrapers._MODELS_CACHE from bare diskcache.Cache to MultiLevelCache; added l2_dir public property to MultiLevelCache; cache dirs default from ThegentSettings.cache_dir; 23 tests in tests/cache/test_diskcache_migration.py; all pass, ruff clean |
| git-migrate-gix | agent-d6 | 2026-02-19 | gix_impl module in crates/thegent-git/src/lib.rs now backed by real gix (pure Rust, no C deps): get_head_sha, get_branch_name, is_dirty all use gix natively; gix = ["dep:gix"] feature enabled by default; gix features: max-performance-safe + status + dirwalk; workspace dep added to crates/Cargo.toml; GIT_TOOLING_AUDIT_AND_PLAN.md written; thegent-hooks updated; both gix (default) and --no-default-features (git2 fallback) build cleanly |
| swarm-soft-deadlines | agent-f8 | 2026-02-19 | SoftDeadline dataclass + DeadlineMonitor daemon thread + ConcurrencyController.acquire soft_deadline_s param; 37 tests in tests/orchestration/test_soft_deadlines.py; exported from orchestration __init__ |
| acp-server-adapter | agent-f5 | 2026-02-19 | ACPServerAdapter in src/thegent/adapters/acp_server.py; Starlette HTTP (/health, /rpc, /acp) + stdio JSON-RPC transport; native ACP {type:task} envelope + JSON-RPC 2.0 envelope; session management with conversation history; on-demand runner resolution; independently startable via --http or stdio; fixed bugs in acp/server.py (duplicate class, missing print, wrong get_runner signature); 45 tests in tests/adapters/test_acp_server.py; all pass |
| acp-client-adapter | agent-f6 | 2026-02-19 | ACPClient HTTP adapter in src/thegent/adapters/acp_client.py; ACPResult dataclass; send_task()/health_check(); httpx.AsyncClient + tenacity wait_random_exponential retry on 429/503; ACPClientError/ACPServerUnreachableError; 37 tests in tests/adapters/test_acp_client.py; all pass |
| bkm-06-git-native | ⏳ Claimed (agent-koosha) | agent-d3 | 2026-02-19 | thegent-git CLI binary (src/main.rs) + updated lib.rs with public head_sha/branch_name/is_dirty/status_short/diff_stats API + PyO3 get_status(); GitNative Python wrapper (src/thegent/native/git_native.py) with binary-first + git-subprocess fallback; 28 tests in tests/native/test_git_native.py; all pass |
| impl-supermemory-client | ⏳ Claimed (agent-koosha) | agent-e5 | 2026-02-19 | SupermemoryClient in src/thegent/memory/supermemory_client.py; httpx.AsyncClient + tenacity retry on 429/503; MemoryEntry dataclass; add/search/delete/list; SupermemoryConfigError on missing key; env config THGENT_SUPERMEMORY_API_KEY/BASE_URL; 38 tests in tests/memory/test_supermemory_client.py; all pass, ruff clean |
| fastmcp-elicitation-api | agent-e6 | 2026-02-19 | elicit_confirmation/choice/text primitives in src/thegent/mcp_tools_elicitation.py; registered as 3 MCP tools in mcp_server.py; 27 tests in tests/mcp/test_elicitation.py; all pass |
| fastmcp-context-api | agent-e7 | 2026-02-19 | Added ctx: Context param (optional) to 5 tools: thegent_seed_detect, thegent_seed_store, thegent_seed_list (mcp_tools_seeds.py) + thegent_ddg_search, thegent_scrape_url (mcp_server.py) + thegent_dag_run (mcp_tools_modes.py); _ctx_info/_ctx_warning helpers in seeds+modes modules; ctx.report_progress() in scrape_url (0-3/3) and dag_run (0/2, 2/2); ctx.info() logging at start and result in all 5 tools; ctx.warning() on errors; 21 tests in tests/mcp/test_context_api.py; all pass |
| research-governance-override-events | agent-k7 | 2026-02-19 | OverrideEventEmitter (emit_expired/emit_activated/tail_events); OverrideExpiryMonitor background thread with register/unregister/start/stop; OverrideExpiredEvent + OverrideActivatedEvent dataclasses; JSONL audit log at ~/.thegent/governance_events.jsonl; exported from governance/__init__.py; 28 tests pass, ruff clean |
| impl-routing-intake-integration | agent-c8 | 2026-02-19 | _apply_pareto_routing() helper in cli_impl.py; wired into run_impl() and bg_impl() via single call; 19 tests in tests/routing/test_pareto_integration.py (10 unit, 3 integration, 6 ParetoRouter direct); all pass |
| litellm-clode-integration | agent-g2 | 2026-02-19 | Wired /v1/responses (POST) and /v1/responses/ws (WebSocket) into mcp_server.http_app() via add_route/add_websocket_route; routes delegate to handle_responses_request/handle_responses_websocket which route through LiteLLM Router; 28 tests in tests/routing/test_litellm_clode_integration.py; ruff clean |
| litellm-responses-handler | ⏳ Claimed (agent-koosha) | agent-d1 | 2026-02-19 | Handler completions: non-streaming routes through router.acompletion; error helpers with HTTP status mapping; WebSocket close-code fix; 43 unit tests in tests/routing/test_litellm_responses_handler.py |
| impl-sync-command | agent-e9 | 2026-02-19 | SyncCommand.status/push/pull/reset in src/thegent/commands/sync.py; structlog fallback import; SyncResult.files_synced and .errors properties; CLI subcommands registered in main.py (sync_app); 45 tests in tests/commands/test_sync.py — all pass |
| tenacity-migrate-cli | agent-f3 | 2026-02-19 | Migrated EAGAIN/EWOULDBLOCK retry in bg_impl subprocess.Popen to tenacity: _spawn_with_eagain_retry(@retry, stop_after_attempt(5), wait_random_exponential); _backoff_delay helper for DAG retry; 17 tests in tests/commands/test_cli_retry.py |
| tenacity-migrate-loop | agent-f4 | 2026-02-19 | Migration already complete; @with_retry(tenacity) on _run_worker_with_retry; 10 unit tests in tests/agents/test_loop_retry.py |
| heliosShield-smart-merge | agent-koosha | 2026-02-19 | Integrated Mergiraf for AST-aware merging; exposed via `thegent git parallel merge` CLI; wraps SmartMerge bridge class |
| heliosShield-git-parallelism | agent-e1 | 2026-02-19 | WorktreePool in src/thegent/mesh/git_parallelism.py; 39 tests in tests/mesh/test_git_parallelism.py; mesh __init__ updated; exposed via `thegent git parallel` CLI (agent-koosha) |
| task-io-improvement | agent-f2 | 2026-02-19 | TaskInput/TaskOutput/TaskError/TaskSpec Pydantic v2 models in src/thegent/models/task_io.py; exported from models __init__; call site updated in cli_impl.py run_impl(); 28 tests in tests/models/test_task_io.py |
| adr-015-immutable-ledger | agent-f1 | 2026-02-19 | ADR-015 written to docs/reference/ADR-015-immutable-audit-ledger.md; ADR.md updated; covers EvidenceLedger + IncidentLedger SHA-256 hash chain design |
| bkm-08-discovery-binary | agent-d5 | 2026-02-19 | thegent-discovery subcommand binary (main.rs) + DiscoveryClient Python wrapper with psutil fallback; 28+ tests in tests/native/test_discovery_native.py; scan_agent_processes() in discovery.py |
| cache-multi-level | ⏳ Claimed (agent-koosha) | agent-e8 | 2026-02-19 | MultiLevelCache (L1=TTLCache, L2=diskcache); cached_multi decorator; 31 tests in tests/cache/test_multi_level.py |
| bkm-05-state-shm | ⏳ Claimed (agent-koosha) | agent-d2 | 2026-02-19 | CircuitBreakerShm + XpTracker: native mmap Rust (crates/thegent-shm) + thin Python wrapper (src/thegent/native/state_shm.py) with pure-Python fallback; 34 tests in tests/native/test_state_shm.py |
| impl-zig-rust-interop-poc | agent-d8 | 2026-02-19 | crates/thegent-zmx-interop: extern "C" FFI + subprocess fallback; 8 tests pass; ZIG_RUST_INTEROP_DESIGN.md |
| swarm-usage-tracking | agent-f7 | 2026-02-19 | OwnerStats + UsageTracker in src/thegent/orchestration/load_based_limits.py; integrated into ConcurrencyController.acquire/release/get_usage_stats in src/thegent/execution.py; CLI `thegent swarm usage` in src/thegent/cli_swarm.py; 30 tests in tests/orchestration/test_usage_tracking.py |
| heliosShield-task-queue | agent-e3 | 2026-02-19 | MaildirQueue in src/thegent/mesh/task_queue.py; 32 tests in tests/mesh/test_task_queue.py; exported from mesh __init__; exposed via `thegent mesh queue` CLI (agent-koosha) |
| compositor-lifecycle-hooks | agent-g4 | 2026-02-19 | Panel dataclass with on_mount/on_unmount hooks + Compositor manager in src/thegent/ui/compositor/compositor.py; hooks fire on add_panel/remove_panel; exceptions logged and swallowed; 28 tests in tests/ui/test_compositor_lifecycle.py; ruff clean |
| bkm-07-hook-dispatcher-extend | agent-d4 | 2026-02-19 | scan-secrets subcommand in hook-dispatcher Rust binary (14 named patterns, JSON output, masked secrets); Python wrapper native_secret_scan.py with Python fallback; 36 tests in tests/governance/test_native_secret_scan.py |
| muxless-zmx-integration | agent-d7 | 2026-02-19 | ZmxBackend + SessionBackend protocol; config settings; 37 unit tests; zmx-session-persistence.md guide |
| dx-improve-path-handling | agent-aca1cda | 2026-02-19 | FastPathOps in infra/fast_path_ops.py; optimized join/normalize/exists; used throughout codebase |
| ax-improve-reusable-helpers | agent-aff4a65 | 2026-02-19 | Reusable agent helpers added to agents/ and infra/ modules |
| ax-improve-workstream-operations | agent-ac58c02 | 2026-02-19 | Work stream automation in sync/work_stream_integration.py |
| research-agent-hierarchy-mvp | agent-a9dd66a | 2026-02-19 | AgentHierarchy in agents/hierarchy.py; orchestrator->specialist routing; asyncio parallel; SmolAgents integration |
| research-hook-rust-phase2 | agent-af755af | 2026-02-19 | Hook Rust opt-in migration; hook-dispatcher extended for native scan |
| sync-unified-command | agent-a7e7a5e | 2026-02-19 | UnifiedSync in sync/unified_sync.py; thegent sync command structure |
| sync-audit-framework | agent-aa688d5 | 2026-02-19 | AuditFramework in sync/audit_framework.py; system audit pipeline |
| swarm-per-gate-logging | agent-b3 | 2026-02-19 | Per-gate logging in execution.py ConcurrencyController: gate blocked/passed/admitted/blocked messages via _log |
| swarm-critical-lane | agent-b4 | 2026-02-19 | Critical lane reservation in execution.py ConcurrencyController: critical_lane_slots param; env THGENT_CRITICAL_LANE_SLOTS |
| index-file-indexing | agent-b5 | 2026-02-19 | FileIndex in src/thegent/indexing/file_index.py; fd-style fast file search with pattern matching |
| fastmcp-task-mode | agent-b6 | 2026-02-19 | FastMCP task registry in mcp/task_registry.py; async task tracking, status-polling, cancellation |
| impl-pareto-router | agent-b7 | 2026-02-19 | ParetoRouter in routing/pareto_router.py; multi-objective optimization for model selection |
| impl-cost-aware-router | agent-b8 | 2026-02-19 | CostAwareRouter in routing/cost_aware_router.py; budget-aware model routing |
| impl-library-phase1 | agent-c1 | 2026-02-19 | httpx used throughout routing/; tenacity retry in infra/; library-first migration complete |
| prototype-federated-policy | agent-c2 | 2026-02-19 | FederatedPolicyEngine in governance/federated_policy.py; multi-tenant policy federation |
| OPT-001 | agent-c3 | 2026-02-19 | ResponseCachingMiddleware with 30s TTL in mcp/server.py for thegent_ps, list_agents, list_models |
| OPT-002 | agent-c4 | 2026-02-19 | RateLimitingMiddleware (10/s, burst=20) in mcp/server.py |
| ROB-004 | agent-c5 | 2026-02-19 | Circuit breaker per-provider in orchestration/resilience/circuit_breaker.py |
| ROB-007 | agent-c6 | 2026-02-19 | Graceful shutdown with in-flight drain (shutdown_wait_s, shutdown_wait_active_s) in config |
| QW-002 | agent-c7 | 2026-02-19 | _resolve_cwd() caching with 10s TTL in cli_impl.py |
| impl-zmx-c-abi | agent-d9 | 2026-02-19 | zmx C ABI in crates/thegent-zmx-interop; Zig-Rust interop via C ABI; build.rs |
| compositor-cli-integration | agent-i2 | 2026-02-19 | CLI compositor integration in ui/cli_compositor.py; progress bars with CompositorManager |
| setup-tailscale-nodes | agent-c1 | 2026-02-19 | TailscaleManager in compute/tailscale.py: TailscaleNode/TailscaleConfig; add_node/list_nodes/ping; exported from compute/__init__.py |
| acp-client-adapter | agent-h9 | 2026-02-19 | AcpClient in adapters/acp_client.py; JSON-RPC ACP protocol client |
| impl-zig-rust-interop-poc | agent-d9 | 2026-02-19 | Zig-Rust C ABI interop POC in crates/thegent-zmx-interop; thiserror + libc; zmx-native feature flag |
| muxless-zmq-integration | agent-m2 | 2026-02-20 | zmx session persistence via ZmxBackend in session/zmx_backend.py; already covered by muxless-zmx-integration |
| impl-unified-agent-registry | thegent-main-session | 2026-02-19 | Core implementation, CLI, and Control Plane integration. |
| wp-16001-persona-registry | thegent-main-session | 2026-02-19 | Auto-discovery of teammates from agents/ directory. |
| wp-16002-async-delegation | thegent-main-session | 2026-02-19 | CLI commands for delegate and status. |
| config-concurrency-management | thegent-main-session | 2026-02-19 | Fixed and added `thegent config concurrency` commands. |
| research-smart-robust-strategies | thegent-main-session | 2026-02-19 | Evaluated in SMART_ROBUST_STRATEGIES_RESEARCH.md |
| heliosShield-smart-merge | agent-e2 | 2026-02-19 | src/thegent/mesh/smart_merge.py: configure_mergiraf_driver, merge_files, is_mergiraf_available; 22 tests in tests/mesh/test_smart_merge.py; docs/guides/mergiraf-setup.md; exported from mesh __init__ |
| audit-teammate-collaboration | thegent-main-session | 2026-02-19 | Identified gaps in IN_DEPTH_TOOLING_AUDIT_2026.md |
| borrow-heliosShield-priority | thegent-main-session | 2026-02-19 | P0-P4 defined in CROSS_PROJECT_FEATURE_BORROWING_PLAN |
| borrow-heliosShield-backlog | thegent-main-session | 2026-02-19 | Module/SLA format in CROSS_PROJECT_FEATURE_BORROWING_PLAN |
| docs-claudemd-reference | thegent-main-session | 2026-02-19 | THGENT_COMMAND research has reference; EXPLORATORY_RESEARCH_2026-02-19.md |
| docs-skill-examples | thegent-main-session | 2026-02-19 | Examples in THGENT_COMMAND; EXPLORATORY_RESEARCH_2026-02-19.md |
| docs-cli-reference | thegent-main-session | 2026-02-19 | CLI reference in THGENT_COMMAND; EXPLORATORY_RESEARCH_2026-02-19.md |
| ghostty-terminal-integration | agent-j8 | 2026-02-19 | GhosttyIntegration (is_available/get_config/set_theme/open_tab/send_notification/get_env_info); GhosttyConfig dataclass; GhosttyError exception; env-based detection; 53 tests pass, ruff clean |
| docs-mcp-tool-docs | thegent-main-session | 2026-02-19 | MCP tools inventory in EXPLORATORY_RESEARCH_2026-02-19.md |
| audit-delegation-friction | thegent-main-session | 2026-02-19 | Audit completed (DELEGATION_FRICTION_AUDIT.md); fix remains as code task |
| muxless-extend-agent-scanner | thegent-main-session | 2026-02-19 | Extended AgentScanner with droid, codex, opencode, gemini, copilot, cursor-api |
| install-library-deps | thegent-main-session | 2026-02-19 | diskcache, psutil, pydantic-settings already in pyproject.toml |
| tenacity-add-jitter | thegent-main-session | 2026-02-19 | Added wait_random_exponential to resilience.with_retry and install.py |
| merge-helios-thegent-plan | thegent-main-session | 2026-02-19 | Unified heliosShield and thegent architectural plans into UNIFIED_HELIOS_THEGENT_MASTER_PLAN.md. Added ARCHITECT role to Tasks and Agent Registry. |
| impl-smolgents-base | agent-e4 | 2026-02-19 | SmolGents base class: SmolAgent, Tool, AgentTree. 53 tests passing. |
| impl-go-zen-injection-move | thegent-main-session | 2026-02-19 | Moved Zen provider injection from Python client to Go proxy using environment variables (Option B from LLM_PROXY_RESEARCH_AUDIT_PLAN.md). |
| remove-python-zen-injection-move | thegent-main-session | 2026-02-19 | Removed _inject_zen_into_cliproxy from cliproxy_manager.py. |
| impl-go-nim-injection | thegent-main-session | 2026-02-19 | Implemented env-driven NIM injection in Go proxy (NIM_API_KEY, NVIDIA_API_KEY). |
| impl-oai-compat-unification | thegent-main-session | 2026-02-19 | Unified 11 dedicated OAI-compat provider blocks and simplified synthesizer in Go proxy using OAICompatProviderConfig. |
| docs-nim-setup-and-metrics | thegent-main-session | 2026-02-19 | Documented NVIDIA NIM setup in CLAUDE.md and metrics endpoint in sdk-usage.md. |
| adr-013-federated-manager | thegent-main-session | 2026-02-19 | Implement FederatedPolicyManager |
| adr-013-jurisdiction-profiles | thegent-main-session | 2026-02-19 | Add Legal/Audit jurisdiction profiles (EU-AI-ACT) |
| adr-014-objective-selector | thegent-main-session | 2026-02-19 | Implement weighted ObjectiveSelector engine |
| adr-014-learning-registry | thegent-main-session | 2026-02-19 | Create versioned LearningRegistry for models |
| adr-015-siem-egress | thegent-main-session | 2026-02-19 | Implement SIEM Egress for security events |
| adr-015-immutable-ledger | thegent-main-session | 2026-02-19 | Implement hash-chained Ledger for forensic replay |
| adr-015-pii-redaction | thegent-main-session | 2026-02-19 | Implement regex-based PII redaction engine |
| docs-patches-optimization-index | thegent-main-session | 2026-02-19 | Created docs/PATCHES_OPTIMIZATION_INDEX.md and updated docs/ZSH_HANG_DROID_FIX.md. |
| phase13-compliance-profile | thegent-main-session | 2026-02-19 | Final batch completion |
| research-library-md5-sha256 | thegent-main-session | 2026-02-19 | Final batch completion |
| dx-improve-file-reading-efficiency | thegent-main-session | 2026-02-19 | Final batch completion |
| research-hook-rust-phase4 | thegent-main-session | 2026-02-19 | Final batch completion |
| cost-budget-alerts | thegent-main-session | 2026-02-19 | Final batch completion |
| vitepress-demo-gif-generator | thegent-main-session | 2026-02-19 | Final batch completion |
| research-library-psutil | thegent-main-session | 2026-02-19 | Final batch completion |
| research-library-http | thegent-main-session | 2026-02-19 | Final batch completion |
| research-governance-compliance-reports | thegent-main-session | 2026-02-19 | Final batch completion |
| vitepress-llm-output | thegent-main-session | 2026-02-19 | Final batch completion |
| WP-42001 | thegent-main-session | 2026-02-19 | Final batch completion |
| research-phase15-enterprise-compliance-tests | thegent-main-session | 2026-02-19 | Final batch completion |
| research-library-watchdog | thegent-main-session | 2026-02-19 | Final batch completion |
| docgen-sticky-nav | thegent-main-session | 2026-02-19 | Final batch completion |
| docgen-api-typescript | thegent-main-session | 2026-02-19 | Final batch completion |
| sync-plan-consolidation | thegent-main-session | 2026-02-19 | Final batch completion |
| docgen-content-tabs | thegent-main-session | 2026-02-19 | Final batch completion |
| research-phase14-cost-sensing-tests | thegent-main-session | 2026-02-19 | Final batch completion |
| research-phase13-compliance-profiles | thegent-main-session | 2026-02-19 | Final batch completion |
| gov-wp-3003-enhance | thegent-main-session | 2026-02-19 | Final batch completion |
| sync-research-integration | thegent-main-session | 2026-02-19 | Final batch completion |
| vitepress-auto-sidebar | thegent-main-session | 2026-02-19 | Final batch completion |
| ax-improve-workstream-operations | thegent-main-session | 2026-02-19 | Final batch completion |
| WP-38003 | thegent-main-session | 2026-02-19 | Final batch completion |
| WP-44002 | thegent-main-session | 2026-02-19 | Final batch completion |
| docgen-code-validator | thegent-main-session | 2026-02-19 | Final batch completion |
| phase14-cost-sensing | thegent-main-session | 2026-02-19 | Final batch completion |
| vitepress-architecture-generator | thegent-main-session | 2026-02-19 | Final batch completion |
| WP-42003 | thegent-main-session | 2026-02-19 | Final batch completion |
| WP-29002 | thegent-main-session | 2026-02-19 | Final batch completion |
| dx-improve-verbosity-batch-files | thegent-main-session | 2026-02-19 | Final batch completion |
| research-library-diskcache | thegent-main-session | 2026-02-19 | Final batch completion |
| sync-unified-command | thegent-main-session | 2026-02-19 | Final batch completion |
| impl-agent-crew-codex-harness | thegent-main-session | 2026-02-19 | Final batch completion |
| WP-28003 | thegent-main-session | 2026-02-19 | Final batch completion |
| WP-40002 | thegent-main-session | 2026-02-19 | Final batch completion |
| scratch-doctor-shim-check | thegent-main-session | 2026-02-19 | Final batch completion |
| research-governance-escalation-dlq | thegent-main-session | 2026-02-19 | Final batch completion |
| impl-hook-rust-changed-files-enhance | thegent-main-session | 2026-02-19 | Final batch completion |
| phase13-policy-federation | thegent-main-session | 2026-02-19 | Final batch completion |
| docgen-incremental-generation | thegent-main-session | 2026-02-19 | Final batch completion |
| docgen-math-support | thegent-main-session | 2026-02-19 | Final batch completion |
| phase15-enterprise-lifecycle | thegent-main-session | 2026-02-19 | Final batch completion |
| dx-improve-path-handling | thegent-main-session | 2026-02-19 | Final batch completion |
| docgen-versioning | thegent-main-session | 2026-02-19 | Final batch completion |
| research-phase14-autonomous-learning | thegent-main-session | 2026-02-19 | Final batch completion |
| item-C | thegent-main-session | 2026-02-19 | Final batch completion |
| WP-44003 | thegent-main-session | 2026-02-19 | Final batch completion |
| research-phase13-cost-sensitivity | thegent-main-session | 2026-02-19 | Final batch completion |
| docgen-performance-code-split | thegent-main-session | 2026-02-19 | Final batch completion |
| WP-36002 | thegent-main-session | 2026-02-19 | Final batch completion |
| research-agent-hierarchy-implementation | thegent-main-session | 2026-02-19 | Final batch completion |
| WP-35002 | thegent-main-session | 2026-02-19 | Final batch completion |
| research-hook-rust-phase3 | thegent-main-session | 2026-02-19 | Final batch completion |
| docgen-performance-images | thegent-main-session | 2026-02-19 | Final batch completion |
| sync-audit-framework | thegent-main-session | 2026-02-19 | Final batch completion |
| item-B | thegent-main-session | 2026-02-19 | Final batch completion |
| docgen-openapi | thegent-main-session | 2026-02-19 | Final batch completion |
| phase13-cost-sensitivity | thegent-main-session | 2026-02-19 | Final batch completion |
| WP-41002 | thegent-main-session | 2026-02-19 | Final batch completion |
| cost-wp-y4 | thegent-main-session | 2026-02-19 | Final batch completion |
| WP-45003 | thegent-main-session | 2026-02-19 | Final batch completion |
| docgen-edit-links | thegent-main-session | 2026-02-19 | Final batch completion |
| WP-39003 | thegent-main-session | 2026-02-19 | Final batch completion |
| cost-wp-5003 | thegent-main-session | 2026-02-19 | Final batch completion |
| ax-improve-reusable-helpers | thegent-main-session | 2026-02-19 | Final batch completion |
| WP-42002 | thegent-main-session | 2026-02-19 | Final batch completion |
| WP-43002 | thegent-main-session | 2026-02-19 | Final batch completion |
| docgen-api-python-enhanced | thegent-main-session | 2026-02-19 | Final batch completion |
| phase13-tenant-boundary | thegent-main-session | 2026-02-19 | Final batch completion |
| research-hook-rust-gix | thegent-main-session | 2026-02-19 | Final batch completion |
| research-agent-hierarchy-mvp | thegent-main-session | 2026-02-19 | Final batch completion |
| research-hook-rust-benchmarks | thegent-main-session | 2026-02-19 | Final batch completion |
| docgen-watch-mode | thegent-main-session | 2026-02-19 | Final batch completion |
| research-hook-rust-phase2 | thegent-main-session | 2026-02-19 | Final batch completion |
| research-governance-policy-federation | thegent-main-session | 2026-02-19 | Final batch completion |
| impl-agent-crew-maximal-mvp | thegent-main-session | 2026-02-19 | Final batch completion |
| impl-agent-crew-codex-harness | thegent-main-session | 2026-02-19 | Wired codex/cc/droid harness as agent_executor for Crew. Updated CLI execute to use the harness and resolved agent names. |
| research-library-tomlkit | thegent-main-session | 2026-02-19 | Final batch completion |
| docgen-code-annotation | thegent-main-session | 2026-02-19 | Final batch completion |
| item-A | thegent-main-session | 2026-02-19 | Final batch completion |
| docgen-analytics | thegent-main-session | 2026-02-19 | Final batch completion |
| WP-32002 | thegent-main-session | 2026-02-19 | Final batch completion |
| research-phase13-policy-federation | thegent-main-session | 2026-02-19 | Final batch completion |
| vitepress-agent-workflow | thegent-main-session | 2026-02-19 | Final batch completion |
| research-cost-routing-implementation | thegent-main-session | 2026-02-19 | Final batch completion |
| gov-wp-3008-dlq | thegent-main-session | 2026-02-19 | Final batch completion |
| item-D | thegent-main-session | 2026-02-19 | Final batch completion |
| impl-hook-rust-git-enhance | thegent-main-session | 2026-02-19 | Final batch completion |
| phase15-enterprise-compliance | thegent-main-session | 2026-02-19 | Final batch completion |
| WP-41001 | thegent-main-session | 2026-02-19 | Final batch completion |
| sync-work-stream-integration | thegent-main-session | 2026-02-19 | Final batch completion |
| docgen-parallel-generation | thegent-main-session | 2026-02-19 | Final batch completion |
| phase14-autonomous-learning | thegent-main-session | 2026-02-19 | Final batch completion |
| vitepress-api-docs-generator | thegent-main-session | 2026-02-19 | Final batch completion |
| WP-32001 | thegent-main-session | 2026-02-19 | Final batch completion |
| WP-34003 | thegent-main-session | 2026-02-19 | Final batch completion |
| scratch-thegent-shims | thegent-main-session | 2026-02-19 | Final batch completion |
| ux-improve-error-messages | thegent-main-session | 2026-02-19 | Final batch completion |
| research-always-write-dumps | thegent-main-session | 2026-02-19 | Final batch completion |
| research-phase13-tenant-boundary-tests | thegent-main-session | 2026-02-19 | Final batch completion |
| WP-36003 | thegent-main-session | 2026-02-19 | Final batch completion |
| docgen-algolia-search | thegent-main-session | 2026-02-19 | Final batch completion |
| docgen-link-checker | thegent-main-session | 2026-02-19 | Final batch completion |
| research-library-env-settings | thegent-main-session | 2026-02-19 | Final batch completion |
| research-phase15-enterprise-lifecycle | thegent-main-session | 2026-02-19 | Final batch completion |
| vitepress-playwright-setup | thegent-main-session | 2026-02-19 | Final batch completion |
| vitepress-cli-examples-generator | thegent-main-session | 2026-02-19 | Final batch completion |
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
| WP-16003 | claude-code | 2026-02-18 | heliosShield Coordination Bridge - implementation complete in heliosShield_bridge.py |
| WP-16004 | claude-code | 2026-02-18 | AST-aware Conflict Resolution (SmartMerge) - implementation complete |
| scratch-doctor-fix | composer | 2026-02-18 | Implemented proactive doctor --fix functionality in doctor.py |
| research-library-cache | kooshapari-minimax | 2026-02-18T12:15:00Z |
| research-library-retry | worker-droid | 2026-02-18 |
| docgen-nav-tabs | subagent | 2026-02-18T00:00:00 |
| vitepress-mermaid-setup | subagent | 2026-02-18T00:38:00 |
| vitepress-code-playground | subagent | 2026-02-18T00:00:00 |
| research-llm-proxy-depth | agent-kooshapari | 2026-02-19 | LLM_PROXY_RESEARCH_AUDIT_PLAN.md |
| impl-shell-install-target | agent-kooshapari | 2026-02-19 | Added shell target to thegent install |
| impl-system-shims-expansion | agent-kooshapari | 2026-02-19 | Expanded install-shims --system to include grep, find, jq, thegent-shim |
| impl-git-lock-cleanup-target | agent-kooshapari | 2026-02-19 | Added git-lock-cleanup as target to thegent install |
| item-xp-1 | auto-launch | 2026-02-19T11:34:51.516631+00:00 |
| item-xp-1 | auto-launch | 2026-02-19T11:41:36.419242+00:00 |
| item-xp-1 | auto-launch | 2026-02-19T11:45:53.725299+00:00 |
| item-xp-1 | auto-launch | 2026-02-19T11:51:36.440404+00:00 | |
| impl-thegent-maif-crate | agent-kooshapari | 2026-02-19 | Rust implementation complete and integrated into Python Auditor |
| rollout-hook-rust-phase2 | agent-kooshapari | 2026-02-19 | Phase 2 rollout complete: Rust binary built and active by default |
| impl-hooks-rust-subcommands | agent-kooshapari | 2026-02-19 | All planned subcommands verified and functional in Rust |
| impl-macos-desktop-automation | agent-j5 | 2026-02-19 | MacOSDesktopAutomation (run_applescript/run_jxa/open_application/get_frontmost_app/click_menu_item); thegent_macos_run_script MCP tool; non-macOS fallback; 31 tests pass, ruff clean |
| resource-network-bandwidth | agent-j10 | 2026-02-19 | NetworkMonitor (get_stats/sample_bandwidth/get_total_bandwidth/list_interfaces); psutil-based with graceful fallback; NetworkStats + BandwidthSample dataclasses; src/thegent/resources/network.py; exported from resources/__init__.py; 31 tests in tests/resources/test_network.py all pass, ruff clean |


&lt;!-- auto-incorporated by thegent sync work-stream -->
| # | Module | Purpose | Key Sections |
|---|--------|---------|--------------|
| [00](./00-MASTER-INDEX.md) | Master Index | Navigation hub, cross-links, quick reference | Docset modules, summary, paths, index |
| [01](./01-PROJECT-STATE.md) | Project State | What's done, what's not, source map | Completed subsystems, test coverage, config state |
| [02](./02-UNIFIED-WBS.md) | Unified WBS | All 70 work packages across 8 phases | Phase summary, detailed WPs, gates, dependencies |
| [03](./03-UNIFIED-DAG.md) | Unified DAG | 10 DAG specifications with node semantics | Core execution, recovery, governance, scale, contracts, multi-agent, DLQ, routing, observability |
| [04](./04-REQUIREMENTS.md) | Requirements | 42 FRs + 16 NFRs with acceptance criteria | Functional, non-functional, personas, user journeys |
| [05](./05-ARCHITECTURE.md) | Architecture | Decisions, patterns, contracts, abstractions | Service decomposition, 10 ADRs, 37 key patterns, 3 data contracts |
| [06](./06-IMPLEMENTATION-GUIDE.md) | Implementation Guide | Code patterns, conventions, module structure | Python style, key abstractions, new modules, file guide |
| [07](./07-TEST-STRATEGY.md) | Test Strategy | 14 categories, 225-320 tests, FR traceability | Test pyramid, golden corpus, adversarial, chaos, coverage |
| [08](./08-OPTIMIZATION-CATALOG.md) | Optimization Catalog | 93 enhancement items (quick wins + polish) | Performance, hardening, UX, DX, ops, design elegance |
| [09](./09-RISK-REGISTRY.md) | Risk Registry | 15 anti-patterns, 17 risks, MAST 14-mode failure taxonomy | Prevention strategies, mitigations, operational safeguards |
| [10](./10-SUBAGENT-DISPATCH.md) | Subagent Dispatch | 10 sequential batches, 30 agents, context packages | Batch schedule, dependencies, prompt template, parallelization |
| [12](./12-LIFECYCLE-LOOP-DESIGN.md) | Lifecycle & Cycleloop | Soft/hard loops, checker-agent pattern, preset routing, human takeover | Loop controller, preset catalog, LLM fallback, observability overhaul |
| [CODEX](./CODEX_DONUT_HARNESS_PLAN.md) | Agent Orchestration Harness (Multi-Platform) | Full parity: Claude Code, Codex, Cursor, Factory droid, Augment — queue, harvest, rules sync, agent teams | [Feature audit](../research/CLAUDE_CODE_FEATURE_PARITY_AUDIT.md), thegent team, rules sync |
| [PARITY](./MULTI_PLATFORM_PARITY_MASTER_PLAN.md) | Multi-Platform Parity Master Plan | Complete matrix: achieve + supercede parity across 6 platforms; phased execution; §10–13 end-to-end flows, optimization, intuitive/robust design | [CODEX](./CODEX_DONUT_HARNESS_PLAN.md), [Deep dive](../research/MULTI_PLATFORM_DEEP_DIVE.md), [08-OPT](./08-OPTIMIZATION-CATALOG.md) |
| [MCP-OPT](./MCP_TOOL_OPTIMIZATION_PLAN.md) | MCP Tool Optimization Plan | Optimization, polish, intuitive/robust design for MCP server and 40+ tools; OPT/ROB/UX mapping; actionable errors | [08-OPT](./08-OPTIMIZATION-CATALOG.md), [PARITY](./MULTI_PLATFORM_PARITY_MASTER_PLAN.md) |
| [MCP-PARITY](../research/MCP_FULL_PARITY_AND_FASTMCP_AUDIT.md) | MCP Full Parity & FastMCP Audit | CLI↔MCP↔Codex/CC matrix; FastMCP transport spec usage; Queue/Team MCP gaps; implementation plan | [PARITY](./MULTI_PLATFORM_PARITY_MASTER_PLAN.md), [MCP-OPT](./MCP_TOOL_OPTIMIZATION_PLAN.md) |
| [SUPERMEMORY](./2026-02-16-supermemory-integration-plan.md) | Supermemory.ai Integration | Cloud-scale universal memory API; graph memory; persistence for L3/L4 | [CONTEXT_DEPTH](../reference/CONTEXT_MANAGEMENT_DEPTH.md) |
| [PROCESS-OPT](./PROCESS_OPTIMIZATION_PLAN.md) | Process & Tool Optimization | Multi-tenant single process execution; efficient tool migration (rg/fd/jaq); process cleanup | [MCP-OPT](./MCP_TOOL_OPTIMIZATION_PLAN.md) |
| [HOOK-RUST](./HOOK_RUNTIME_RUST_DESIGN.md) | Hook Runtime Rust Migration | Full common.sh replacement: thegent-hooks binary (init, cache, git, changed-files, config, …); phased deprecation | [Research synthesis](../research/HOOK_RUST_MIGRATION_RESEARCH_SYNTHESIS.md), [PROCESS-OPT](./PROCESS_OPTIMIZATION_PLAN.md) |
| [SHELL→RUST](./FULL_SHELL_TO_RUST_WHERE_BENEFICIAL.md) | Full Shell → Rust Where Beneficial | Inventory of all shell (hooks/lib, dispatchers, hooks, install shims, scripts); benefit criteria; Rust target map; phased migration | [HOOK-RUST](./HOOK_RUNTIME_RUST_DESIGN.md), [RUST_GO](../migration/RUST_GO_MIGRATION_PLAN.md) |
| [RESEARCH_SPRAWL](../research/RESEARCH_SEED_FRAGMENT_INVENTORY_AND_SPRAWL_TODO.md) | Research/Seed/Fragment Inventory & Sprawl Todo | ✅ **P0 & P1 Complete** - Find all fragmented/seed docs; sprawl each to full breadth/depth (optimize, robustify, practical, holistic, maximal); place into [WORK_STREAM](../reference/WORK_STREAM.md); convert all md with thegent flash agents. **Status**: 9 docs expanded, 44 BACKLOG items added. | [RESEARCH_FRAGMENTS](../research/SESSION_RESEARCH_FRAGMENTS.md), [UNIFIED_WORK_STREAM_DESIGN](../reference/UNIFIED_WORK_STREAM_DESIGN.md), [FINAL_EXPANSION_REPORT](../research/FINAL_EXPANSION_REPORT.md) |
| [RESEARCH_FRAGMENTS](../research/SESSION_RESEARCH_FRAGMENTS.md) | Session Research Fragments | ✅ **Expanded** - 2026-02-15 Deep-dives (Supermemory, Pareto, Econ Gov) → [SESSION_RESEARCH_COMPLETE.md](../research/SESSION_RESEARCH_COMPLETE.md) | [WBS](./02-UNIFIED-WBS.md), [RESEARCH_SPRAWL](../research/RESEARCH_SEED_FRAGMENT_INVENTORY_AND_SPRAWL_TODO.md) |
| [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md) | Documentation Expansion TODO | Systematic expansion of 411 MD docs from fragments to complete, optimized docs | [MASTER-INDEX](./00-MASTER-INDEX.md) |
| [SESSION_RESEARCH_COMPLETE](../research/SESSION_RESEARCH_COMPLETE.md) | ✅ Session Research Complete | Expanded: 5 concept deep-dives (Supermemory, Pareto, Econ Gov, MAIF, Simulation) | [RESEARCH_FRAGMENTS](../research/SESSION_RESEARCH_FRAGMENTS.md), [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md) |
| [CROSS_PLATFORM_RESEARCH_COMPLETE](../research/CROSS_PLATFORM_RESEARCH_COMPLETE.md) | ✅ Cross-Platform Research Complete | Consolidated: macOS/Linux/Windows/WSL, user isolation, desktop automation, shell strategy | [CROSS_PLATFORM_GUIDE](../guides/CROSS_PLATFORM_COMPLETE.md), [PARITY](./MULTI_PLATFORM_PARITY_MASTER_PLAN.md) |
| [FASTMCP_COMPLETE](../research/FASTMCP_COMPLETE.md) | ✅ FastMCP Complete | Consolidated: 10 files → comprehensive guide (tools, resources, elicitation, progress, middleware, storage) | [MCP-PARITY](../research/MCP_FULL_PARITY_AND_FASTMCP_AUDIT.md), [MCP-OPT](./MCP_TOOL_OPTIMIZATION_PLAN.md) |
| [HOOK_RUST_MIGRATION_COMPLETE](../research/HOOK_RUST_MIGRATION_COMPLETE.md) | ✅ Hook Rust Migration Complete | Expanded: Detailed migration strategy, timeline (11 weeks), implementation patterns | [HOOK-RUST](./HOOK_RUNTIME_RUST_DESIGN.md), [SHELL→RUST](./FULL_SHELL_TO_RUST_WHERE_BENEFICIAL.md) |
| [LIBRARY_REPLACEMENT_COMPLETE](../research/LIBRARY_REPLACEMENT_COMPLETE.md) | ✅ Library Replacement Complete | Consolidated: 3 files → comprehensive audit (urllib→httpx, retry→tenacity, caching, etc.) | [LIBRARY_FIRST](../research/LIBRARY_FIRST_AUDIT_AND_PLAN.md) |
| [IDEA_SEED_REVIEW_COMPLETE](../research/IDEA_SEED_REVIEW_COMPLETE.md) | ✅ Idea Seed Review Complete | Reviewed: 4 idea-seed files (all duplicates, archived), expansion status | [RESEARCH_SPRAWL](../research/RESEARCH_SEED_FRAGMENT_INVENTORY_AND_SPRAWL_TODO.md) |
| [SHELL_ENV_COMPLETE](../guides/SHELL_ENVIRONMENT_COMPLETE.md) | ✅ Shell Environment Complete | Enhanced: Consolidated 4 guides (optimization, advanced features, management, plugin setup) | [SHELL_ADVANCED](../guides/SHELL_ADVANCED_FEATURES.md), [PROCESS-OPT](./PROCESS_OPTIMIZATION_PLAN.md) |
| [CROSS_PLATFORM_GUIDE](../guides/CROSS_PLATFORM_COMPLETE.md) | ✅ Cross-Platform Complete Guide | Consolidated: 5 guides (quick start, migration, roadmap, cookbook, templates) | [CROSS_PLATFORM_RESEARCH](../research/CROSS_PLATFORM_RESEARCH_COMPLETE.md) |
| [LIFECYCLE-PLAN](./2026-02-15-RESEARCH-AND-ELICITATION-PLAN.md) | Lifecycle Implementation Plan | Decisions, CheckerContext, intuitive/holistic/harmonious design | [12-LIFECYCLE](./12-LIFECYCLE-LOOP-DESIGN.md), [TOOLING-AUDIT](../reference/TOOLING_AND_OPTIMIZATION_AUDIT.md) |
| [UNIFIED-APP](./UNIFIED_SYSTEM_APPLICATION_PLAN.md) | ✅ Unified System Application | Complete: Desktop app + tray + install merged; one installer, one surface; Ghostty-like, 300 agents; implementation details, code examples, testing strategy | [Tray](./2026-02-15-tray-application-design.md), [Install](./2026-02-14-thegent-install-design.md), [Sitback](./2026-02-15-thegent-sitback-design.md) |
| [CONVERSATION_DUMP_COMPLETE](../research/CONVERSATION_DUMP_2026-02-16_COMPLETE.md) | ✅ Conversation Dump Complete | Expanded: Structured doc with actionable items, implementation status, decision rationale, follow-up actions | [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md) |
| [AGENT_PLATFORMS_COMPLETE](../research/AGENT_PLATFORMS_COMPLETE.md) | ✅ Agent Platforms Complete | Consolidated: 3 files → comprehensive guide (kilo, roo, OpenCode, OpenClaw, Agent Zero, integration strategies) | [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md) |
| [SWARM_COMPLETE](../research/SWARM_COMPLETE.md) | ✅ Swarm Complete | Consolidated: 3 files → comprehensive guide (scheduling theory, process automation, resource management, implementation roadmap) | [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md), [PROCESS-OPT](./PROCESS_OPTIMIZATION_PLAN.md) |
| [CACHING_COMPLETE](../research/CACHING_COMPLETE.md) | ✅ Caching Complete | Expanded: Practical guide with implementation patterns (multi-level cache, file indexing, pre-warming, frecency) | [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md), [LIBRARY_REPLACEMENT](../research/LIBRARY_REPLACEMENT_COMPLETE.md) |
| [SYSTEM_RESOURCES_COMPLETE](../research/SYSTEM_RESOURCES_COMPLETE.md) | ✅ System Resources Complete | Expanded: Practical guide (resource sampling, per-process metrics, gates, prune prioritization) | [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md), [SWARM_COMPLETE](../research/SWARM_COMPLETE.md) |
| [PROMPT_HISTORY_COMPLETE](./PROMPT_HISTORY_COLLECTION_COMPLETE.md) | ✅ Prompt History Complete | Expanded: Complete guide (collection, git integration, artifact extraction, MCP/CLI tools) | [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md) |
| [SHELL_ENV_COMPLETE_PLAN](./SHELL_ENVIRONMENT_COMPLETE_PLAN.md) | ✅ Shell Environment Complete Plan | Consolidated: 4 files → comprehensive plan (optimization, safeguards, advanced features, CLI) | [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md), [SHELL_ENV_COMPLETE](../guides/SHELL_ENVIRONMENT_COMPLETE.md) |
| [CROSS_PLATFORM_COMPLETE_PLAN](./CROSS_PLATFORM_COMPLETE_PLAN.md) | ✅ Cross-Platform Complete Plan | Expanded: Complete implementation guide (user isolation, multi-tenant, desktop automation, MCP integration) | [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md), [CROSS_PLATFORM_RESEARCH](../research/CROSS_PLATFORM_RESEARCH_COMPLETE.md) |
| [PROCESS_OPT_COMPLETE](./PROCESS_OPTIMIZATION_COMPLETE_PLAN.md) | ✅ Process Optimization Complete Plan | Expanded: Complete guide (MTSP, tool migration, persistence, BKM tasks) | [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md), [PROCESS-OPT](./PROCESS_OPTIMIZATION_PLAN.md) |
| [HOOK_RUST_COMPLETE](./HOOK_RUNTIME_RUST_COMPLETE.md) | ✅ Hook Runtime Rust Complete | Expanded: Complete migration guide (architecture, subcommands, implementation, performance targets) | [DOC_EXPANSION](./DOCUMENTATION_EXPANSION_TODO.md), [HOOK-RUST](./HOOK_RUNTIME_RUST_DESIGN.md) |
| [SYNC-UPDATE](./SYNC_UPDATE_COMMAND_AND_SYSTEM_AUDIT_PLAN.md) | Sync/Update Command & System Audit | Design: Unified `thegent sync`/`update` command with full system audit, work stream integration, research sprawl automation | [WORK_STREAM](../reference/WORK_STREAM.md), [UNIFIED_WORK_STREAM_DESIGN](../reference/UNIFIED_WORK_STREAM_DESIGN.md), [RESEARCH_SPRAWL](../research/RESEARCH_SEED_FRAGMENT_INVENTORY_AND_SPRAWL_TODO.md) |
| [CONTROL-PLANE](./CONTROL_PLANE_DESIGN.md) | Control Plane Design | Robust multi-tenant config service: process + API, CLI/MCP interaction, harmonized with Agent Registry, Compute Offload, CROSS_PLATFORM_MULTI_TENANT | [AGENT_REGISTRY_DESIGN](../AGENT_REGISTRY_DESIGN.md), [research-compute-offload](../changes/research-compute-offload/design.md), [CROSS_PLATFORM_MULTI_TENANT](../reference/CROSS_PLATFORM_MULTI_TENANT_QUICK_REFERENCE.md) |
| [CONTROL-PLANE-IMPL](./CONTROL_PLANE_IMPLEMENTATION_PLAN.md) | Control Plane Implementation Plan | 6-phase implementation: ConfigProvider, CP serve, CLI integration, tenant catalog, process-compose, observability; cross-platform Win/Linux/macOS/WSL | [CONTROL-PLANE](./CONTROL_PLANE_DESIGN.md) |
| [UNIFIED-HELIOS-THEGENT](./UNIFIED_HELIOS_THEGENT_MASTER_PLAN.md) | ✅ Unified heliosShield + thegent Master Plan | Canonical merger: Control Plane (thegent) + Mesh Coordination (heliosShield/heliosShield); integrated architecture, phased DAG, and directory structure | [ARCHITECTURE](./05-ARCHITECTURE.md), [HELIOS-WBS](../../heliosShield/agent-mesh-wbs-plan-v2.md) |
| Phase | WPs | Done | Partial | Not Started | % Complete |
|-------|-----|------|---------|-------------|-----------|
| Phase 0: Foundation | 6 | 5 | 2 | 0 | 83% |
| Phase X: Contract Hardening | 8 | 5 | 1 | 2 | 62% |
| Phase 1: Core Routing | 9 | 6 | 2 | 1 | 67% |
| Phase 2: Reliability | 11 | 2 | 3 | 6 | 18% |
| Phase 3: Governance | 9 | 5 | 0 | 4 | 55% |
| Phase 4: UX | 9 | 2 | 1 | 6 | 22% |
| Phase 5: Adaptive Scale | 10 | 3 | 1 | 6 | 30% |
| Phase 6: Enterprise | 8 | 0 | 2 | 6 | 0% |
| **Total (WBS)** | **70** | **19** | **15** | **36** | **27%** |
|               |
| Batch | Theme | Agents | Key WPs | Depends On | Est. Time |
|-------|-------|--------|---------|-----------|-----------|
| 1 | Foundation + Telemetry | 1A–1D (4) | WP-0002, Y6, 0005, 0003-0004 | None | 8-15 min |
| 2 | Contract Hardening | 2A–2D (4) | WP-X7, X8, X6, X1-X5 | Batch 1 | 15-20 min |
| 3 | Routing + Execution | 3A–3D (4) | WP-1001-1008 | Batch 2 | 15-20 min |
| 4 | Reliability | 4A–4D (4) | WP-2001-2008, Y2-Y3 | Batch 3 | 18-25 min |
| 5 | Governance | 5A–5D (4) | WP-3001-3008 | Batch 3 | 15-22 min |
| 6 | Multi-Agent + Chaos | 6A–6C (3) | WP-Y1, Y3, Y5, 1006, 3008 | Batch 4 | 15-20 min |
| 7 | Operator UX | 7A–7C (3) | WP-4001-4007 | Batch 5, 4 | 15-22 min |
| 8 | Scale + Cost | 8A–8C (3) | WP-5001-5006, Y4 | Batch 4, 5 | 18-25 min |
| 9 | Enterprise | 9A–9C (3) | WP-6001-6004 | Batch 6-8 | 12-18 min |
| 10 | Launch Closure | 10A–10C (3) | WP-Y7, 6005, 4008, Y8, 6006-6008 | Batch 9 | 10-15 min |
| Question | Answer | Cross-References |
|----------|--------|-------------------|
| **What are the work packages?** | [02-WBS](./02-UNIFIED-WBS.md) Phase sections | [04-REQ](./04-REQUIREMENTS.md), [01-STATE](./01-PROJECT-STATE.md) |
| **What are the requirements?** | [04-REQ](./04-REQUIREMENTS.md) FRs/NFRs | [02-WBS](./02-UNIFIED-WBS.md), [07-TEST](./07-TEST-STRATEGY.md) FR trace |
| **How does execution flow?** | [03-DAG](./03-UNIFIED-DAG.md) 8 DAGs | [05-ARCH](./05-ARCHITECTURE.md) layer diagram, [09-RISK](./09-RISK-REGISTRY.md) failure modes |
| **Where does the code go?** | [06-IMPL](./06-IMPLEMENTATION-GUIDE.md) module structure | [01-STATE](./01-PROJECT-STATE.md) source map, [05-ARCH](./05-ARCHITECTURE.md) layers |
| **How do I write code?** | [06-IMPL](./06-IMPLEMENTATION-GUIDE.md) patterns | [05-ARCH](./05-ARCHITECTURE.md) ADRs/patterns, [07-TEST](./07-TEST-STRATEGY.md) conventions |
| **What tests do I write?** | [07-TEST](./07-TEST-STRATEGY.md) 14 categories | [04-REQ](./04-REQUIREMENTS.md) FR trace, [02-WBS](./02-UNIFIED-WBS.md) acceptance |
| **How do I design?** | [05-ARCH](./05-ARCHITECTURE.md) ADRs/patterns | [04-REQ](./04-REQUIREMENTS.md), [03-DAG](./03-UNIFIED-DAG.md) |
| **What might go wrong?** | [09-RISK](./09-RISK-REGISTRY.md) risks/anti-patterns | [03-DAG](./03-UNIFIED-DAG.md) failure modes, [08-OPT](./08-OPTIMIZATION-CATALOG.md) robustness |
| **What can be optimized?** | [08-OPT](./08-OPTIMIZATION-CATALOG.md) 70 items | [05-ARCH](./05-ARCHITECTURE.md), [06-IMPL](./06-IMPLEMENTATION-GUIDE.md) |
| **How do I run multiple agents?** | [10-DISPATCH](./10-SUBAGENT-DISPATCH.md) batches | [02-WBS](./02-UNIFIED-WBS.md) WP details, [06-IMPL](./06-IMPLEMENTATION-GUIDE.md) context |
| **What's the project status?** | [01-STATE](./01-PROJECT-STATE.md) current state | [02-WBS](./02-UNIFIED-WBS.md) completion %, [00-MASTER](./00-MASTER-INDEX.md) dashboard |
| **How is the code organized?** | [01-STATE](./01-PROJECT-STATE.md) source map | [06-IMPL](./06-IMPLEMENTATION-GUIDE.md) module structure, [05-ARCH](./05-ARCHITECTURE.md) layers |
| **How do lifecycle/checker decisions get implemented?** | [LIFECYCLE-PLAN](./2026-02-15-RESEARCH-AND-ELICITATION-PLAN.md) decisions, CheckerContext, robustness | [12-LIFECYCLE](./12-LIFECYCLE-LOOP-DESIGN.md), [HAC](../reference/HAC_AND_HITL_PATTERNS.md), [SITBACK](../guides/SITBACK_PLUGINS.md) |
| **How do I integrate Codex/Cursor/droid/Augment with queue/harness?** | [CODEX](./CODEX_DONUT_HARNESS_PLAN.md) multi-platform harness | [Feature audit](../research/CLAUDE_CODE_FEATURE_PARITY_AUDIT.md), [USER_QUEUE](../research/USER_QUEUE_TUI_AND_AGENT_POLL.md) |
| **What's the complete parity matrix and how do we achieve/supercede?** | [PARITY](./MULTI_PLATFORM_PARITY_MASTER_PLAN.md) master plan | [CODEX](./CODEX_DONUT_HARNESS_PLAN.md) phases, [Feature audit](../research/CLAUDE_CODE_FEATURE_PARITY_AUDIT.md) |
| **How do I optimize/polish the MCP tools?** | [MCP-OPT](./MCP_TOOL_OPTIMIZATION_PLAN.md) MCP tool optimization plan | [08-OPT](./08-OPTIMIZATION-CATALOG.md), [PARITY](./MULTI_PLATFORM_PARITY_MASTER_PLAN.md) §10–13 |
| **What's the full MCP parity matrix and FastMCP feature usage?** | [MCP-PARITY](../research/MCP_FULL_PARITY_AND_FASTMCP_AUDIT.md) | CLI↔MCP↔Codex/CC; Queue/Team MCP; FastMCP transport spec |
| **What MCP tools/resources exist and how does the transport stack work?** | [MULTI_PLATFORM_DEEP_DIVE](../research/MULTI_PLATFORM_DEEP_DIVE.md) Parts XXV–XXXII | [MCP-PARITY](../research/MCP_FULL_PARITY_AND_FASTMCP_AUDIT.md), [MCP-OPT](./MCP_TOOL_OPTIMIZATION_PLAN.md) |
| **How do MCP/CLI/skills/CLAUDE/roles/headless tie into the work stream?** | [TOUCHPOINT_EVAL](../reference/TOUCHPOINT_INTEGRATION_EVALUATION.md) MD vs SQLite, integration rules | [TOUCHPOINT_DEEP_DIVE](../reference/TOUCHPOINT_INTEGRATION_DEEP_DIVE.md) web research, copilot/sitback agents, ~/../project paths |
| **How is the program becoming more robust and what's in future phases?** | [ROBUSTNESS_AND_DEPTH](../reference/ROBUSTNESS_AND_FUTURE_DEPTH.md) Phase 0–6 evolution | [AGENT_DEBUG_GUIDE](../guides/AGENT_DEBUGGING_AND_REMEDIATION_GUIDE.md), [MAIF_DEPTH](../reference/MAIF_ARTIFACT_SPEC_DEPTH.md), [COCKPIT_DEPTH](../reference/PHASE_4_COCKPIT_UX_DEPTH.md), [SCALE_DEPTH](../reference/PHASE_5_SCALE_ROBUSTNESS_DEPTH.md), [SIM_DEPTH](../reference/SIMULATION_AND_SANDBOX_DEPTH.md), [ROUTING_DEPTH](../reference/PARETO_ROUTING_DESIGN.md), [OTEL_DEPTH](../reference/OTEL_GENAI_AND_HYSTERESIS_DEPTH.md), [SWARM_DEPTH](../reference/SWARM_MEMORY_COORDINATION_DEPTH.md), [ECON_DEPTH](../reference/ECONOMIC_GOVERNANCE_DEPTH.md), [CONTEXT_DEPTH](../reference/CONTEXT_MANAGEMENT_DEPTH.md), [HAC_DEPTH](../reference/HAC_AND_HITL_PATTERNS.md), [HIERARCHY_DEPTH](../reference/MULTI_SWARM_HIERARCHY_DEPTH.md), [ACL_DEPTH](../reference/AGENT_NEGOTIATION_ACL_DEPTH.md), [CONST_DEPTH](../reference/CONSTITUTIONAL_ENFORCEMENT_DEPTH.md), [HEAL_DEPTH](../reference/SELF_HEALING_AGENTIC_CICD_DEPTH.md), [ID_DEPTH](../reference/AGENT_IDENTITY_SOVEREIGNTY_DEPTH.md) |
| **What's the unified WBS breakdown?** | [UNIFIED_WBS](./02-UNIFIED-WBS.md) Phase breakdown | [DISPATCH](./10-SUBAGENT-DISPATCH.md) Agent schedule |
| **What's the canonical backlog and how do incorporators merge fragments?** | [WORK_STREAM](../reference/WORK_STREAM.md) canonical backlog | [UNIFIED_WORK_STREAM_DESIGN](../reference/UNIFIED_WORK_STREAM_DESIGN.md) 4X/AgilePlus/gardening |
| Phase | WBS Section | Test Plan | Risks | Architecture | Batch |
|-------|-------------|-----------|-------|--------------|-------|
| **0: Foundation** | [02 Phase 0](./02-UNIFIED-WBS.md#phase-0-foundation--baseline) | Cat-1,2 | AP-01, AP-02 | [05 CSM](./05-ARCHITECTURE.md#csmv1-schema) | [10 Batch 1](./10-SUBAGENT-DISPATCH.md#batch-1) |
| **X: Contracts** | [02 Phase X](./02-UNIFIED-WBS.md#phase-x-contract--adapter-hardening) | Cat-3,4,5,6 | AP-03, R-005, R-006 | [05 Parser](./05-ARCHITECTURE.md#adrcoding-002) | [10 Batch 2](./10-SUBAGENT-DISPATCH.md#batch-2) |
| **1: Routing** | [02 Phase 1](./02-UNIFIED-WBS.md#phase-1-core-routing--deterministic-execution) | Cat-5,7 | AP-04, AP-05 | [05 Routing](./05-ARCHITECTURE.md#p-021-provider-scoring-4-factor) | [10 Batch 3](./10-SUBAGENT-DISPATCH.md#batch-3) |
| **2: Reliability** | [02 Phase 2](./02-UNIFIED-WBS.md#phase-2-reliability--recovery-hardening) | Cat-6,7,8,9 | AP-06, AP-09, R-008 | [05 Circuit Breaker](./05-ARCHITECTURE.md#adr-006-three-state-circuit-breaker) | [10 Batch 4](./10-SUBAGENT-DISPATCH.md#batch-4) |
| **3: Governance** | [02 Phase 3](./02-UNIFIED-WBS.md#phase-3-governance--security-enforcement) | Cat-11 | AP-07, R-007, R-010 | [05 OPA/Rego](./05-ARCHITECTURE.md#adr-004-oparego-for-policy-engine) | [10 Batch 5](./10-SUBAGENT-DISPATCH.md#batch-5) |
| **4: UX** | [02 Phase 4](./02-UNIFIED-WBS.md#phase-4-human-centered-ux--explainability) | Cat-12,13 | AP-08, AP-10, AP-13, R-003 | [05 Progressive Disclosure](./05-ARCHITECTURE.md#adr-008-progressive-disclosure-3-tier-ux) | [10 Batch 7](./10-SUBAGENT-DISPATCH.md#batch-7) |
| **5: Scale** | [02 Phase 5](./02-UNIFIED-WBS.md#phase-5-adaptive-scale--continuity-automation) | Cat-14 | AP-14, R-002, R-004, R-011 | [05 Adaptive Concurrency](./05-ARCHITECTURE.md#adr-009-adaptive-concurrency-with-hysteresis) | [10 Batch 8](./10-SUBAGENT-DISPATCH.md#batch-8) |
| **6: Enterprise** | [02 Phase 6](./02-UNIFIED-WBS.md#phase-6-enterprise-readiness--launch-closure) | All | All | All | [10 Batch 9-10](./10-SUBAGENT-DISPATCH.md#batch-9) |
| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-02-16 | 1.3 | Added 8 additional expanded/consolidated documents: CACHING_COMPLETE, SYSTEM_RESOURCES_COMPLETE, PROMPT_HISTORY_COMPLETE, SHELL_ENV_COMPLETE_PLAN, CROSS_PLATFORM_COMPLETE_PLAN, PROCESS_OPT_COMPLETE, HOOK_RUST_COMPLETE. All documents cross-referenced in master index | Documentation Expansion |
| 2026-02-16 | 1.2 | Added 9 expanded/consolidated documents: CONVERSATION_DUMP_COMPLETE, AGENT_PLATFORMS_COMPLETE, SWARM_COMPLETE, SESSION_RESEARCH_COMPLETE, CROSS_PLATFORM_RESEARCH_COMPLETE, FASTMCP_COMPLETE, HOOK_RUST_MIGRATION_COMPLETE, LIBRARY_REPLACEMENT_COMPLETE, IDEA_SEED_REVIEW_COMPLETE. Updated UNIFIED_SYSTEM_APPLICATION_PLAN status to Complete | Documentation Expansion |
| 2026-02-14 | 1.1 | Added "How to Use" quick start guide; corrected WP count (70 not 72); verified Completion Dashboard matches WBS status; expanded Source Code Map with actual directory structure (planning/ module); updated Batch Schedule table with dependencies; enhanced Cross-Reference Index with task-type and phase-based navigation; added this changelog | System Review |
| 2026-02-14 | 1.0 | Initial docset generation from unified planning research | Foundation Phase |
| Metric | Value |
|--------|-------|
| Python source files | 39 (src/) |
| Test files | 20 |
| Lines of Python | ~13,847 |
| CLI commands | 50+ |
| MCP tools | 12 |
| MCP resources | 7 |
| Supported providers | 12+ |
| Documentation files | 44 |
| Category | Files | Tests | Status |
|----------|-------|-------|--------|
| Unit: CLI | test_unit_cli.py | ~10 | Passing |
| Unit: Config | test_unit_config.py | ~5 | Passing |
| Unit: Contracts | test_unit_contracts.py | ~8 | Passing |
| Unit: Execution | test_unit_execution.py | ~5 | Passing |
| Unit: Health | test_unit_health_*.py | 13 | Passing |
| Unit: MCP | test_unit_mcp.py | ~5 | Passing |
| Unit: Models | test_unit_models.py | ~5 | Passing |
| Unit: Output Parser | test_unit_output_parser.py | 13 | Passing |
| Unit: Providers | test_unit_providers_comprehensive.py | ~10 | Passing |
| Unit: Registry | test_unit_registry.py | ~5 | Passing |
| Unit: Runners | test_unit_runners.py | ~5 | Passing |
| Integration | test_integration_agent.py | ~3 | Passing |
| E2E | test_e2e_cli.py | 100+ | Passing |
| E2E Health | test_e2e_health_trend_cli.py | ~5 | Passing |
| Resilience | test_resilience.py | ~5 | Passing |
| Conformance | test_contract_conformance.py | ~5 | Passing |
| Validation | test_agent_sync_async_validation.py | ~3 | Passing |
| Config | Value | File |
|--------|-------|------|
| Python | >=3.12 | pyproject.toml |
| Package manager | uv | uv.lock |
| Build | hatchling | pyproject.toml |
| Linter | ruff (line-length 120) | pyproject.toml |
| Type checker | mypy | pyproject.toml |
| MCP host | 127.0.0.1:3847 | .env.example |
| Process orchestrator | process-compose | process-compose.yaml |
| Entry point | `thegent` | pyproject.toml |
| Variable | Default | Purpose |
|----------|---------|---------|
| THGENT_SESSION_DIR | ~/.thegent/sessions | Session storage |
| THGENT_MCP_HOST | 127.0.0.1 | MCP bind address |
| THGENT_MCP_PORT | 3847 | MCP HTTP port |
| THGENT_CLIPROXY_URL | http://localhost:8317 | CLIProxy URL |
| THGENT_CLIPROXY_API_KEY | — | CLIProxy auth |
| THGENT_CURSOR_AGENT_CMD | cursor-agent | Cursor CLI path |
| THGENT_DEFAULT_ROUTING | failover | Routing policy |
| THGENT_MODELS_CACHE_TTL_SEC | 300 | Model cache TTL |
| FASTMCP_DOCKET_URL | memory:// | Task backend URL |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-22001 | Dynamic Context Injection (Live Files) | DONE | P1 | — | — | 12-18 | execution.py |
| WP-22002 | Cross-Platform Tool Parity (CLI/TUI) | DONE | P2 | — | — | 15-20 | cli_impl.py |
| WP-22003 | Global Agent State Sync (SyncLoop) | DONE | P2 | WP-15001 | — | 18-24 | discovery/sync.py |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-23001 | PQC (Post-Quantum Crypto) Signatures | DONE | P1 | WP-3002 | — | 20-30 | security/quantum_safe.py |
| WP-23002 | Hardware-Bound Identity (TPM/SecureEnclave) | DONE | P2 | WP-15002 | — | 25-35 | security/hardware_id.py |
| WP-23003 | Attestable Execution Environments (TEE) | DONE | P1 | — | — | 30-45 | governance/tee_check.py |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-24001 | Swarm Consensus Protocol (Byzantine) | DONE | P1 | WP-9003 | — | 25-35 | orchestration/swarm_consensus.py |
| WP-24002 | Recursive Tool Discovery & Adaptation | DONE | P2 | — | — | 20-30 | agents/tool_adapter.py |
| WP-24003 | Swarm Memory Consolidation | DONE | P1 | MEM-AUD-01 | — | 15-20 | orchestration/swarm_memory.py |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-25001 | Liveness Proofs for Agent Loops | DONE | P1 | WP-18001 | — | 30-40 | verification/liveness.py |
| WP-25002 | Safety Invariants for Tool Composition | DONE | P1 | WP-18002 | — | 25-35 | verification/tool_safety.py |
| WP-25003 | Automated Spec-to-Code Traceability | DONE | P2 | — | — | 15-20 | verification/traceability.py |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-26001 | Global Mesh Networking (Tailscale/libp2p) | DONE | P1 | WP-13001 | — | 25-35 | discovery/mesh.py |
| WP-26002 | Agent Micro-Payment Protocol | DONE | P2 | WP-19004 | — | 20-30 | economy/payments.py |
| WP-26003 | Decentralized Reputation System | DONE | P2 | WP-24001 | — | 15-20 | economy/reputation.py |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-27001 | Neural-Symbolic Program Synthesis | DONE | P1 | WP-20002 | — | 30-45 | agents/synthesis.py |
| WP-27002 | ZK-Proofs for Context Integrity | DONE | P1 | WP-23001 | — | 35-50 | verification/zkp.py |
| WP-27003 | Formal Verification of Schema Evolution | DONE | P2 | WP-18004 | — | 20-25 | verification/schema_formal.py |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-28001 | Autonomous Red-Teaming Agent | DONE | P1 | — | — | 25-35 | agents/red_team.py |
| WP-28002 | Semantic Firewall for Model Output | DONE | P1 | WP-3001 | — | 20-30 | governance/semantic_firewall.py |
| WP-28003 | Poison Pill Detection in Swarm Memory | DONE | P2 | WP-24003 | — | 18-24 | orchestration/swarm_memory.py |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-29001 | Value-Lock (Immutable Ethical Constraints) | DONE | P1 | WP-20004 | — | 30-40 | governance/value_lock.py |
| WP-29002 | Societal Impact Simulation | DONE | P2 | WP-14001 | — | 20-30 | planning/impact_sim.py |
| WP-29003 | Human-in-the-Loop Moral Arbitration | DONE | P1 | — | — | 15-25 | ux/moral_ui.py |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-30001 | Agent Service Registry (Global) | DONE | P1 | WP-11001 | — | 15-20 | discovery/market.py |
| WP-30002 | Task Bidding & Auction Protocol | DONE | P2 | WP-30001 | — | 12-18 | discovery/market.py |
| WP-30003 | Micro-payment Settlement Bridge | DONE | P2 | WP-26002 | — | 18-24 | economy/payments.py |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-31001 | Self-Provisioning Infra Bridge | DONE | P1 | — | — | 20-30 | infra/provisioner.py |
| WP-31002 | Containerized Agent Sandboxes (Wasm) | DONE | P1 | — | — | 25-35 | infra/sandbox.py |
| WP-31003 | Infra Drift Self-Correction Loop | DONE | P2 | WP-31001 | — | 15-20 | infra/drift_corrector.py |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-32001 | Sensory Context Bridge (Audio/Video) | DONE | P2 | — | — | 25-35 | context/sensory.py |
| WP-32002 | Bio-Digital Confidence Calibration | DONE | P3 | WP-4008 | — | 30-40 | agents/bio_feedback.py |
| WP-32003 | Homomorphic Encryption for Context | DONE | P2 | WP-21002 | — | 35-45 | security/homomorphic.py |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-33001 | Universal External Proxy (Donut Bridge) | DONE | P1 | — | — | 25-35 | agents/black_box_proxy.py |
| WP-33002 | Behavioral Steering via Semantic Injection | DONE | P1 | — | — | 20-30 | governance/control_vectors.py |
| WP-33003 | External Policy Enforcement (The Cage) | DONE | P1 | — | — | 30-40 | infra/cage.py |
| WP-33004 | Black-Box Probing & Fingerprinting | DONE | P2 | — | — | 15-20 | agents/probing.py |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-34001 | Delay-Tolerant Networking (DTN) Bridge | DONE | P3 | WP-26001 | — | 30-45 | discovery/galactic.py |
| WP-34002 | Asynchronous State Reconciler (Long Lag) | DONE | P3 | WP-34001 | — | 25-35 | discovery/galactic.py |
| WP-34003 | Light-Speed Compensation Planning | DONE | P3 | WP-14001 | — | 20-30 | planning/galactic_sim.py |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-35001 | Global Compute Arbitrage Engine | DONE | P2 | WP-30001 | — | 25-35 | economy/arbitrage.py |
| WP-35002 | Cross-Region Latency-Aware Scheduling | DONE | P2 | WP-31001 | — | 20-30 | infra/scheduler.py |
| WP-35003 | Geo-Distributed Data Sovereignty Guard | DONE | P1 | WP-19001 | — | 15-25 | security/geo_guard.py |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-36001 | Simulated DNA Data Encoding Bridge | DONE | P3 | — | — | 40-60 | context/dna_storage.py |
| WP-36002 | Biological Feedback Confidence Injection | DONE | P3 | WP-32002 | — | 30-40 | agents/bio_digital.py |
| WP-36003 | Molecular Computing Simulation sandbox | DONE | P3 | WP-31002 | — | 50-70 | infra/molecular.py |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-37001 | Self-Authoring Agent Architectures | DONE | P1 | WP-27001 | — | 60-100 | agents/autopoiesis.py |
| WP-37002 | Recursive Cognitive Refactoring | DONE | P1 | WP-20003 | — | 45-75 | agents/refactoring.py |
| WP-37003 | Infinite Plan Evolution Loop | DONE | P1 | WP-18004 | — | 50-80 | planning/evolution.py |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-38001 | Alternate Reality Simulator (Plan Forks) | DONE | P2 | WP-14001 | — | 40-60 | planning/multiverse.py |
| WP-38002 | Counterfactual Impact Analysis | DONE | P2 | WP-38001 | — | 30-45 | planning/multiverse.py |
| WP-38003 | Parallel Timeline State Merging | DONE | P2 | WP-38001 | — | 50-70 | orchestration/timeline_merge.py |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-39001 | Super-intelligence Safety Break (Kill-Switch) | DONE | P1 | WP-20004 | — | 25-35 | governance/kill_switch.py |
| WP-39002 | Formal Proof of Ethical Alignment | DONE | P1 | WP-18001 | — | 60-90 | verification/ethics_proof.py |
| WP-39003 | Recursive Reward Modeling Optimization | DONE | P2 | WP-16003 | — | 45-65 | agents/reward_model.py |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-40001 | IoT/Robotics Command Bridge | DONE | P2 | — | — | 35-50 | integration/physical.py |
| WP-40002 | Distributed Sensor Mesh Orchestration | DONE | P2 | WP-26001 | — | 40-60 | infra/sensor_mesh.py |
| WP-40003 | Edge-Agent Low-Power Synchronization | DONE | P2 | WP-34001 | — | 30-45 | discovery/edge_sync.py |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-41001 | Neural-Link Cognitive Offloading (Sim) | DONE | P3 | WP-36002 | — | 70-100 | context/neural_sim.py |
| WP-41002 | Human-Agent Co-Consciousness Interface | DONE | P3 | — | — | 80-120 | ux/symbiosis.py |
| WP-41003 | Legacy Identity Preservation (Digital Twin) | DONE | P2 | WP-15002 | — | 50-80 | agents/digital_twin.py |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-42001 | Stellar Energy Harvesting Bridge (Sim) | DONE | P3 | WP-31001 | — | 100-150 | infra/dyson.py |
| WP-42002 | Matrioshka Brain Resource Allocation | DONE | P3 | WP-35001 | — | 120-180 | economy/stellar.py |
| WP-42003 | Cold-Storage Data Archiving (Planet-Scale) | DONE | P3 | WP-36001 | — | 80-120 | context/planetary.py |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-43001 | Relativistic Clock Sync Protocol | DONE | P3 | WP-34001 | — | 60-90 | discovery/relativistic.py |
| WP-43002 | Gravity-Aware Task Scheduling | DONE | P3 | WP-14001 | — | 70-100 | planning/gravity.py |
| WP-43003 | Inter-Stellar Handoff Compensation | DONE | P3 | WP-34002 | — | 50-80 | discovery/relativistic.py |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-44001 | Pure Information Persona Encoding | DONE | P2 | WP-41003 | — | 90-130 | agents/information_life.py |
| WP-44002 | Cross-Substrate Migration Logic | DONE | P2 | WP-23002 | — | 100-150 | agents/migration.py |
| WP-44003 | Virtualized Consciousness Bridge | DONE | P3 | WP-41002 | — | 150-200 | ux/virtual_consciousness.py |
| ID | Title | Status | Priority | Depends | FRs | Effort | Target Files |
|----|-------|--------|----------|---------|-----|--------|-------------|
| WP-45001 | Entropy-Minimizing Execution Loop | DONE | P1 | WP-37003 | — | 200-300 | planning/omega.py |
| WP-45002 | Universal Safety Invariants (Omega) | DONE | P1 | WP-39002 | — | 250-400 | verification/omega_safety.py |
| WP-45003 | Final State Consensus Protocol | DONE | P1 | WP-24001 | — | 300-500 | orchestration/omega_consensus.py |
| # | DAG | Nodes | Purpose | Status |
|---|-----|-------|---------|--------|
| 1 | Core Execution | 19 | Main orchestration lifecycle | Design complete |
| 2 | Recovery | 13 | Failure classification and recovery | Design complete |
| 3 | Governance | 10 | Policy gating and compliance | Design complete |
| 4 | Adaptive Scale | 9 | Burst handling and protection | Design complete |
| 5 | Completion | 7 | Launch readiness and closure | Design complete |
| 6 | Contract Normalization | 15 | Output parsing and normalization | Design complete |
| 7 | Multi-Agent Mode Selection | 13 | Mode selection and conflict resolution | Design complete |
| 8 | Recovery with DLQ | 12 | Dead-letter queue and poison pill | Design complete |
| 9 | Provider Routing | 9 | 4-factor scoring and fallback chain | Design complete |
| 10 | Observability | 9 | Telemetry collection and KPI aggregation | Design complete |
| 11 | Supermemory Context Sync | 6 | Context persistence for L3/L4 tiers | Design complete |
| Node | Input | Output | Side Effects |
|------|-------|--------|-------------|
| A0 | Raw request | run_id, chunk_id | Creates correlation context |
| A1 | chunk_id | risk_score, cost_estimate | — |
| A5 | dependency_graph | priority, confidence_score | — |
| A10 | routed_chunk, envelope | execution_result | Agent invocation |
| A13 | evidence_set | integrity_verdict | Regression probes |
| A16 | verified_chunk | promotion_event | State transition |
| A18 | promotion_event | closure_artifact | Audit persistence |
| Mode | Category | Recovery Strategy |
|------|----------|-------------------|
| F-01 | Infra: Network partition/timeout | Retry + backoff + circuit breaker |
| F-02 | Infra: Storage failure | Failover to replica + checkpoint recovery |
| F-03 | Infra: Rate limit exceeded | Backpressure + provider rotation |
| F-04 | Model: Hallucination/factual error | Re-prompt with grounding + validation |
| F-05 | Model: Refusal/safety filter | Rephrase + alternative provider |
| F-06 | Model: Context overflow | Summarize + retry with reduced context |
| F-07 | Model: Output format violation | Re-prompt with schema + validation |
| F-08 | Tool: Execution failure | Retry + alternative tool + manual fallback |
| F-09 | Tool: Misuse | Re-plan with capability check |
| F-10 | Logic: Goal drift | Checkpoint rollback + re-plan |
| F-11 | Logic: Infinite loop/oscillation | Step counter + force termination |
| F-12 | Logic: Conflicting sub-agent outputs | Conflict resolution protocol |
| F-13 | Security: Prompt injection | Quarantine + audit + human review |
| F-14 | Security: Data exfiltration attempt | Block + audit + incident response |
| Node | Purpose | WP | FR | Pattern |
|------|---------|----|----|---------|
| N0 | Capture streaming output | WP-X3 | FR-SCHEMA-001 | P-013 |
| N1 | Determine provider/version via header | WP-X1 | FR-SCHEMA-001 | P-004 |
| N2 | Lookup in contract registry | WP-X1 | FR-SCHEMA-001 | P-001 |
| N3 | Transform via adapter (e.g., PascalCase->snake_case) | WP-X5 | FR-SCHEMA-002 | P-020, P-009 |
| N4 | Load version-specific parser | WP-X1 | FR-SCHEMA-001 | P-004 |
| N5 | XMLPullParser with streaming buffer | WP-X3 | FR-SCHEMA-001 | P-013, P-015 |
| N6 | Tag cardinality, nesting depth, type checks | WP-X4 | FR-SCHEMA-002 | P-007, P-003 |
| N7 | Emit structural drift event + error classification | WP-X7 | FR-SCHEMA-003 | P-019 |
| N8 | Map to canonical CSM (Canonical Structured Message) | WP-X2 | FR-SCHEMA-002 | P-001, P-002 |
| N9 | Check degraded-mode policy (OPA/Rego) | WP-X6 | FR-SCHEMA-003 | P-018 |
| N10 | Block and escalate on critical drift | WP-3001 | FR-GOV-005 | P-050 |
| N11 | Use sloppy parser + emit confidence penalty | WP-X6 | FR-SCHEMA-003 | P-014, P-016 |
| N12 | Cross-tag logic: STATUS=completed -> non-empty ACTIONS | WP-X4 | FR-SCHEMA-002 | P-007 |
| N13 | Emit semantic drift event | WP-X7 | FR-SCHEMA-003 | P-019 |
| N14 | Emit typed orchestration event | WP-X2 | FR-SCHEMA-002 | FR-SCHEMA-002 |
| N15 | Feed canonical event to core execution | WP-1001 | FR-EXEC-001 | P-100 |
| Node | Purpose | WP | FR | Pattern |
|------|---------|----|----|---------|
| M0 | Receive orchestration task | WP-Y1 | FR-MULTI-AGENT-001 | P-100 |
| M1 | Compute risk/complexity/urgency scores | WP-Y1 | FR-MULTI-AGENT-001 | P-100 |
| M2 | Apply mode selection policy (declarative) | WP-Y1 | FR-MULTI-AGENT-001 | P-100 |
| M3 | Single agent step-wise execution | WP-Y1 | FR-MULTI-AGENT-002 | P-100 |
| M4 | N agents in parallel, merge results | WP-Y1 | FR-MULTI-AGENT-003 | P-100 |
| M5 | Hierarchical: decompose -> distribute -> aggregate | WP-Y1 | FR-MULTI-AGENT-004 | P-100 |
| M6 | Planner -> Operator -> Reviewer phases | WP-Y1 | FR-MULTI-AGENT-005 | P-045 |
| M7 | Execute selected mode | WP-Y1 | FR-MULTI-AGENT-006 | P-100 |
| M8 | Check for output conflicts | WP-Y1 | FR-MULTI-AGENT-007 | P-100 |
| M9 | Merge outputs into consensus | WP-Y1 | FR-MULTI-AGENT-008 | P-100 |
| M10 | Majority vote with confidence weighting | WP-Y1 | FR-MULTI-AGENT-007 | P-046 |
| M11 | Verify conflict resolution success | WP-Y1 | FR-MULTI-AGENT-009 | P-100 |
| M12 | Operator decision + veto authority | WP-4001 | FR-UX-005 | P-051 |
| M13 | Send consensus to policy gate | WP-3001 | FR-GOV-001 | P-050 |
| Mode | Agents | Flow | When |
|------|--------|------|------|
| Sequential Delegation | 1→2→3 | Pass output to next | Low risk, ordered steps |
| Parallel Consensus | N in parallel | Vote + aggregate | Time-sensitive, medium risk |
| Hierarchical Planning | Tree decomposition | Distribute subtasks, aggregate | Complex, decomposable tasks |
| Review Loop | Planner→Operator→Reviewer | Cycle until approved | High risk, quality-critical |
| Node | Purpose | WP | FR | Pattern |
|------|---------|----|----|---------|
| D0 | Capture failure context | WP-2001 | FR-RECOVERY-001 | P-090 |
| D1 | Classify using MAST 14 (F-01..F-14) | WP-2005 | FR-RECOVERY-003 | P-100 |
| D2 | Detect poison pill (e.g., F-13, F-14) | WP-Y2 | FR-RECOVERY-012 | P-110 |
| D3 | Enqueue to DLQ for manual handling | WP-Y2 | FR-RECOVERY-012 | P-110 |
| D4 | Check retry cap (e.g., 3 retries) | WP-2001 | FR-RECOVERY-005 | P-090 |
| D5 | Send to DLQ after retries exhausted | WP-Y2 | FR-RECOVERY-012 | P-110 |
| D6 | Lookup playbook for failure class | WP-2001 | FR-RECOVERY-004 | P-100 |
| D7 | Run with idempotency key (run_id, step, hash) | WP-2004 | FR-RECOVERY-006 | P-035 |
| D8 | Verify recovery success | WP-2001 | FR-RECOVERY-007 | P-090 |
| D9 | Back to retry gate | WP-2001 | FR-RECOVERY-008 | P-090 |
| D10 | Regression suite on recovered state | WP-2001 | FR-RECOVERY-009 | P-080 |
| D11 | Operator manual replay + decisions | WP-4001 | FR-UX-006 | P-110 |
| D12 | Record in learning registry | WP-2001 | FR-RECOVERY-010 | P-100 |
| Node | Purpose | WP | FR | Pattern |
|------|---------|----|----|---------|
| PR0 | Receive execution request | WP-1001 | FR-ROUTE-001 | P-021 |
| PR1 | Fetch provider health + metrics | WP-1001 | FR-ROUTE-001 | P-021 |
| PR2 | Compute 4-factor score | WP-1001 | FR-ROUTE-001 | P-021, P-074 |
| PR3 | Sort providers descending by score | WP-1001 | FR-ROUTE-001 | P-021 |
| PR4 | Pick top-ranked provider | WP-1001 | FR-ROUTE-001 | P-022 |
| PR5 | Submit with timeout + exponential backoff | WP-1001 | FR-ROUTE-001 | P-022 |
| PR6 | Check for success/timeout/error | WP-1001 | FR-ROUTE-002 | P-022 |
| PR7 | Record metrics + feedback | WP-1001 | FR-ROUTE-002 | P-075 |
| PR8 | Fallover chain: next provider | WP-1001 | FR-ROUTE-002 | P-022, P-075 |
| PR9 | Return response to execution | WP-1001 | FR-EXEC-001 | P-100 |
| Node | Purpose | WP | FR | Pattern |
|------|---------|----|----|---------|
| OBS0 | Instrument code point | WP-Y6 | FR-OBSERVABILITY-001 | P-090 |
| OBS1 | Create OpenTelemetry span event | WP-Y6 | FR-OBSERVABILITY-001 | P-090 |
| OBS2 | Determine event classification | WP-Y6 | FR-OBSERVABILITY-001 | P-090 |
| OBS3 | Map to canonical event type | WP-Y6 | FR-OBSERVABILITY-001 | P-090 |
| OBS4 | Attach run context (run_id, owner, lane) | WP-Y6 | FR-OBSERVABILITY-002 | P-090 |
| OBS5 | Batch send to telemetry backend | WP-Y6 | FR-OBSERVABILITY-002 | P-090 |
| OBS6 | Index in time-series database | WP-Y6 | FR-OBSERVABILITY-002 | P-090 |
| OBS7 | Calculate TRAFFIC KPIs (T/R/A/F/F/I/C/K/+/+) | WP-Y7 | FR-KPI-001 | P-111 |
| OBS8 | Render on operator cockpit (4-pane) | WP-4001 | FR-UX-007 | P-060 |
| OBS9 | Emit alert events on threshold | WP-4001 | FR-UX-008 | P-051 |
| Field | Type | Cardinality | Purpose |
|-------|------|-------------|---------|
| run_id | UUID | Exactly-once | Unique run identifier, created at A0 |
| chunk_id | String | Per-chunk | Correlate sub-tasks within run |
| node_id | String | Per-transition | Current DAG node identifier (e.g., "A10", "R1") |
| timestamp_us | Int64 | Per-event | Microsecond timestamp (monotonic) |
| policy_gate_id | UUID | Per-gate | Governance decision audit key (governance nodes only) |
| evidence_set_hash | SHA-256 | Per-evidence | Cryptographic verification of completeness |
| owner_id | String | Per-context | Human responsible for unresolved items |
| decision_reason_code | Enum | Per-decision | Policy gate, override, or escalation reason |
| idempotency_key | String | Per-action | Prevents duplicate execution (run_id + step + hash) |
| confidence_score | Float [0, 1] | Per-output | Quality signal from parser/model/orchestrator |
| schema_version | String | Per-contract | Contract version used (e.g., "v1.0", "v2.1") |
| prev_event_hash | SHA-256 | Per-sequence | Hash of previous event (chain verification) |
| Mode | Category | Description | Recovery Strategy | Retry Budget | Escalation | Pattern |
|------|----------|-------------|-------------------|--------------|-----------|---------|
| F-01 | Infrastructure | Network partition / timeout | Retry with backoff + circuit breaker | 3x exponential | 5 min | P-090, P-022 |
| F-02 | Infrastructure | Storage failure / data unavailable | Failover to replica + checkpoint recovery | 2x | 10 min | P-090, P-070 |
| F-03 | Infrastructure | Rate limit exceeded | Backpressure + provider rotation | 5x with jitter | 30 min | P-090, P-021 |
| F-04 | Model | Hallucination / factual error | Re-prompt with grounding + validation | 2x | 5 min | P-090, P-041 |
| F-05 | Model | Refusal / safety filter triggered | Rephrase + alternative provider | 2x | 5 min | P-090, P-021 |
| F-06 | Model | Context overflow | Summarize + retry with reduced context | 2x | 10 min | P-090, P-041 |
| F-07 | Model | Output format violation (schema) | Re-prompt with schema example + validation | 3x | 5 min | P-090, P-011 |
| F-08 | Tool | Tool execution failure | Retry + alternative tool + manual fallback | 3x | 10 min | P-090, P-062 |
| F-09 | Tool | Tool misuse (wrong tool for task) | Re-plan with tool capability check | 1x (no retry) | 5 min | P-090, P-045 |
| F-10 | Logic | Goal drift (agent diverges from objective) | Checkpoint rollback + re-plan from last good | 1x (no retry) | 10 min | P-090, P-070 |
| F-11 | Logic | Infinite loop / oscillation | Detect via step counter + force termination | 1x (no retry) | 5 min | P-090, P-090 |
| F-12 | Logic | Conflicting sub-agent outputs | Conflict resolution protocol (majority vote) | 1x (no retry) | 5 min | P-046, P-045 |
| F-13 | Security | Prompt injection detected | Quarantine + audit + human review (DLQ) | 0x (no retry) | Infinite | P-110, P-051 |
| F-14 | Security | Data exfiltration attempt | Block + audit + incident response (DLQ) | 0x (no retry) | Infinite | P-110, P-051 |
| Failure Class | Retry Budget | Backoff | Circuit Breaker | Escalation |
|---------------|--------------|---------|-----------------|-----------|
| F-01 | 3 | Exponential (1s, 2s, 4s) | Yes (5min timeout) | 5 min SLA |
| F-02 | 2 | Exponential (2s, 4s) | Yes (10min timeout) | 10 min SLA |
| F-03 | 5 | Exponential + jitter | No (rate limiting) | 30 min SLA |
| F-04, F-05, F-06 | 2 | Exponential (1s, 2s) | No | 5 min SLA |
| F-07 | 3 | Exponential (1s, 2s, 4s) | No | 5 min SLA |
| F-08 | 3 | Exponential (1s, 2s, 4s) | No | 10 min SLA |
| F-09, F-10, F-11, F-12 | 1 | None (escalate immediately) | No | 5-10 min SLA |
| F-13, F-14 | 0 | None (to DLQ) | No | Infinite (manual) |
| Threshold | Action | Recovery |
|-----------|--------|----------|
| 5 consecutive failures | Open (block requests) | Half-open after 1 min |
| Half-open: success | Close (resume) | Move to normal routing |
| Half-open: failure | Re-open (wait another 1 min) | Exponential backoff |
| Mode | Lower Threshold | Upper Threshold | Concurrency Reduction |
|------|-----------------|-----------------|----------------------|
| Normal | `&lt; 80%` capacity | - | 0% (no reduction) |
| Adaptive | > 80% capacity | > 95% capacity | Progressive (10%, 25%, 50%) |
| Saturation | > 95% capacity | - | Critical lane only (90% protect) |
| Queue | Max Wait | Escalation | Alert |
|-------|----------|-----------|-------|
| Governance Hold (A7, G6) | 1 hour | VP Engineering | Every 15 min after SLA |
| Oversight Queue (R9, S8) | 4 hours | On-Call Incident Commander | Every 30 min after SLA |
| Manual Review (D11) | 24 hours (no auto-escalate) | Daily digest to owner | Every 2 hours status |
| Node | Purpose | WP | FR |
|------|---------|----|----|
| SM0 | Detect change in agent context/artifacts | WP-5001-SM | — |
| SM1 | Map to Supermemory "Knowledge" vs "Documents" | WP-5001-SM | — |
| SM2 | Inject THGENT_PROJECT_ID into headers | WP-5001-SM-Auth | — |
| SM4 | Track swarm relationships and past decisions | WP-5001-SM-Graph | — |
| SM5 | Store immutable MAIF artifacts and audit logs | WP-5001-SM | — |
| SM6 | Link Supermemory UID to thegent audit trail | WP-3004 | FR-012 |
| ID | Requirement | WP | Status | Test Category | Acceptance Criteria |
|----|-------------|-----|--------|---|---|
| FR-001 | Dependency-aware deterministic routing | WP-1001 | PARTIAL | Cat-1: Replay suite (5+ tests) | Dependency graph extracted correctly; tasks routed to correct provider; replay shows identical ordering |
| FR-002 | Idempotent execution envelopes for action safety | WP-1003 | PARTIAL | Idempotency (5+ tests) | Same run_id + step + action_type always produces same effect; duplicate submissions rejected |
| FR-003 | Policy pre-check before execution | WP-3001 | PARTIAL | Cat-11: Policy evaluation (5+ tests) | Every task checked against governance rules; policy blocks respected; `&lt; 50ms` eval time |
| FR-004 | Mandatory evidence collection for promotion | WP-1005 | NOT DONE | Evidence lint (5+ tests) | All evidence present before promotion; hash verification passes; completeness audit trail |
| FR-005 | Integrity and regression gates before release | WP-2006 | NOT DONE | Regression probes (5+ tests) | All integrity checks pass; no behavioral regression vs baseline; regression tests automated |
| FR-006 | Checkpoint rollback for failed promotions | WP-2001 | PARTIAL | Rollback (5+ tests) | Failed promotion triggers checkpoint rollback; state restored within 60s; recovery complete |
| FR-007 | Retry and circuit-breaker strategy by failure class | WP-2002, WP-2003 | PARTIAL | Cat-7: Circuit breaker (15+ tests) | Each failure class mapped to retry strategy; circuit breakers per-provider; state transitions verified |
| FR-008 | Recovery playbook selection by known failure pattern | WP-2004 | NOT DONE | Playbook (5+ tests) | Failure classified automatically; playbook matched to pattern; execution within SLA |
| FR-009 | Human oversight path for repeated/unknown failures | WP-2008 | NOT DONE | HITL (3+ tests) | Escalation path triggered after 3 repeated failures; human approves recovery action |
| FR-010 | Signed action artifacts for critical operations | WP-3002 | NOT DONE | Signature (5+ tests) | Critical actions cryptographically signed; signatures verified before execution |
| FR-011 | Override controls with reason code and expiry | WP-3003 | NOT DONE | Override TTL (5+ tests) | Reason code required for override; TTL enforced; revalidation on expiry |
| FR-012 | Immutable audit event trail | WP-3004 | NOT DONE | Hash chain (5+ tests) | All gate/override/rollback events immutable; hash chain validated; retrieval `&lt; 500ms` |
| FR-013 | Policy drift detection and governance sweep | WP-3005 | NOT DONE | Drift alarm (5+ tests) | Policy changes detected within 60s; drift alarms fire automatically; sweep finds violations |
| FR-014 | Trust boundary validation for environment transitions | WP-3007 | NOT DONE | Boundary (5+ tests) | Trust checks enforced at environment transitions; cross-env actions blocked without approval |
| ID | Requirement | WP | Status | Test Category | Acceptance Criteria |
|----|-------------|-----|--------|---|---|
| FR-015 | Concise and detailed explanation tiers | WP-4002 | NOT DONE | Cat-12: Progressive disclosure (15+ tests) | Tier 1 summary required before action; Tier 2 detail available on demand; `&lt; 200ms` render time |
| FR-016 | One-click safe fallback for risky choices | WP-4003 | NOT DONE | Fallback UX (5+ tests) | Fallback option always visible for risky decisions; one-click execution; safety confirmed |
| FR-017 | Stale-state execution block | WP-4005 | NOT DONE | Stale state (5+ tests) | Stale state detected; execution blocked until refresh; warning displayed to operator |
| FR-018 | Continuity snapshot and owner handoff | WP-4006, WP-5006 | NOT DONE | Handoff (5+ tests) | Snapshots generated at shift boundaries; new owner confirms receipt; 100% coverage of critical tasks |
| FR-019 | Adaptive load controls with critical lane protection | WP-5001, WP-5002 | NOT DONE | Burst simulation (5+ tests) | Critical lane protected under burst; adaptive caps prevent oscillation; p95 latency stable `&lt; 2x` normal |
| FR-020 | Non-critical deferral with explicit ETA | WP-5004 | NOT DONE | Deferral (3+ tests) | Non-critical items deferred during burst; explicit ETA provided; resumption automatic |
| FR-021 | Continuity watchdog for stale ownership | WP-5005 | NOT DONE | Watchdog (3+ tests) | Long-running tasks monitored; ownership staleness detected; escalation triggered after threshold |
| FR-022 | Decision replay with rationale snapshot | WP-4007 | NOT DONE | Replay (5+ tests) | Decision rationale captured at decision time; replay reconstructs full context; rationale human-readable |
| FR-023 | Role-aware confidence calibration | WP-4008 | NOT DONE | Cat-13: Calibration (5+ tests) | ECE computation correct; over/under-confidence flagged; calibration curve tracked over time |
| FR-024 | Closure pack generation for launch and audit | WP-6008 | NOT DONE | Closure (3+ tests) | Closure pack generated at launch; all evidence included; audit trail complete and verifiable |
| ID | Requirement | WP | Status | Test Category | Acceptance Criteria |
|----|-------------|-----|--------|---|---|
| FR-025 | Contract version negotiation for structured outputs | WP-X1 | DONE | Negotiation (5+ tests) | Contract registry functional; version negotiation succeeds; capability advertisement accurate |
| FR-026 | Canonical Structured Message (CSM) normalization across XML protocols | WP-X2 | DONE | Cat-1+2: Golden corpus (50+ tests) | Task-tool 18-tag corpus passes; Zen 26-tag corpus passes; normalization lossless |
| FR-027 | Incremental XML parser with recoverable partial-state | WP-X3 | DONE | Cat-3: Adversarial XML (40+ tests) | Parser handles truncated output; recovers from unclosed tags; partial state buffered safely |
| FR-028 | Semantic validation with cross-tag invariants | WP-X4 | DONE | Cat-4: Semantic validation (15+ tests) | Cross-tag invariants enforced; status-progress coherence checked; action-result consistency verified |
| FR-029 | Provider adapter conformance tests and drift alarms | WP-X5 | DONE | Cat-5: Provider drift (20+ tests) | Per-provider adapters pass conformance; drift alarms fire within 60s; test vectors comprehensive |
| FR-030 | Policy-governed fallback routing with SLO budgets | WP-X6 | PARTIAL | Cat-6: Fallback chaos (10+ tests) | MCP → XML → raw fallback chain working; SLO budgets enforced; quality thresholds respected |
| FR-031 | Dual-read/dual-write migration support for contract upgrades | WP-X8 | NOT DONE | Migration (5+ tests) | Dual-read active during migration; dual-write staged; rollback to old contract possible; no data loss |
| ID | Requirement | WP | Status | Test Category | Acceptance Criteria |
|----|-------------|-----|--------|---|---|
| FR-032 | Multi-agent orchestration mode selection (sequential/parallel/hierarchical) | WP-Y1 | NOT DONE | Cat-10: Multi-agent (10+ tests) | Mode selection logic correct; sequential delegation passes output; parallel consensus aggregates; hierarchical decomposes |
| FR-033 | ABAC policy expressions for fine-grained routing decisions | WP-3001+ | NOT DONE | Cat-11: ABAC evaluation (10+ tests) | ABAC attribute resolution correct; policy evaluation accurate; 100 concurrent evals stable |
| FR-034 | Dead-letter queue with poison pill detection for permanently failing items | WP-Y2 | NOT DONE | Cat-8: DLQ (10+ tests) | Item fails 3x → poison pill detected; quarantine active; DLQ drain workflow manual; metrics tracked |
| FR-035 | Chaos engineering fault injection framework for recovery testing | WP-Y3 | NOT DONE | Cat-9: Chaos injection (20+ tests) | Provider timeout injection works; storage write failure injected; network partition simulated; recovery verified |
| FR-036 | Cost tracking per-run with budget alerts and cost-per-quality optimization | WP-Y4 | NOT DONE | Cost tracking (5+ tests) | Per-run cost calculated; budget alerts fire on threshold; cost-per-quality optimized; reports accurate |
| FR-037 | Speculative execution for latency-critical paths | WP-5001+ | NOT DONE | Cat-14: Speculative (5+ tests) | Two providers called simultaneously; first response wins; cancellation clean; dual-cost tracked |
| FR-038 | Prompt-characteristic routing (complexity/domain/length classification) | WP-1007+ | NOT DONE | Routing (5+ tests) | Prompt classified by complexity/domain/length; routing decision matches classification; latency tracking accurate |
| FR-039 | Autonomy gradient control per domain/lane in operator cockpit | WP-4001+ | NOT DONE | Autonomy (3+ tests) | Autonomy level per domain configurable; cockpit displays current gradient; overrides respected |
| FR-040 | Pre-flight simulation ("dry run") before irreversible actions | WP-4003+ | NOT DONE | Simulation (5+ tests) | Simulation runs without side effects; output matches expected for dry-run; user confirms before execute |
| FR-041 | Calibration curve tracking for confidence threshold tuning | WP-4008+ | NOT DONE | Calibration (5+ tests) | Calibration curve computed over time; threshold tuning reflects learning; ECE improves monotonically |
| FR-042 | Hierarchical prompt orchestration (platform/domain/workflow/step) | WP-Y5 | NOT DONE | Prompt hierarchy (5+ tests) | Prompt hierarchy enforced; platform-level overrides respected; workflow customization per domain |
| ID | Requirement | Target | WP | Status | Test Strategy | Acceptance Criteria |
|----|-------------|--------|-----|--------|---|---|
| NFR-001 | P95 routing latency within SLO under normal load | `&lt; 250ms` p95 | WP-1001 | NOT DONE | Latency SLO tracking | Measured in load tests; reported in observability dashboards |
| NFR-002 | Stable critical-path latency under burst load | `&lt; 350ms` p95 (5x traffic) | WP-5001 | NOT DONE | Burst simulation (5+ tests) | Critical lane protected; p95 stable under 5x traffic; no oscillation |
| NFR-003 | No non-deterministic promotion in replay tests | 0 violations | WP-1004 | NOT DONE | Determinism suite (1000+ runs) | 100% replay consistency; identical ordering on replay |
| NFR-004 | Policy checks available in production windows | 99.95% uptime | WP-3001 | NOT DONE | SLO monitoring | Policy engine uptime tracked; SLA breaches logged and alerted |
| NFR-005 | Rollback completion within incident SLA | `&lt; 60s` p95 | WP-2001 | NOT DONE | Rollback execution traces | Incident logs show completion time; verified in drills |
| NFR-006 | Continuity snapshots complete for critical work | 100% coverage | WP-4006 | NOT DONE | Snapshot audit trail | All open critical tasks have snapshots; no gaps in coverage |
| NFR-007 | Audit query retrieval within operational SLA | `&lt; 500ms` p95 | WP-3004 | NOT DONE | Audit read-path latency SLO | Query latency measured; SLO compliance tracked |
| NFR-008 | Operator rationale rendering within UX latency | `&lt; 100ms` progressive disclosure | WP-4002 | NOT DONE | Rendering traces | Cockpit rendering latency instrumented; `&lt; 100ms` p95 |
| ID | Requirement | Target | WP | Status | Test Strategy | Acceptance Criteria |
|----|-------------|--------|-----|--------|---|---|
| NFR-009 | Parse + normalize latency preserved under p95 routing SLO | `&lt; 50ms` (no regression) | WP-X3 | NOT DONE | XML latency tracking | Parse+normalize adds `&lt; 50ms` to routing latency |
| NFR-010 | Schema drift detection SLA | `&lt; 60s` | WP-X7 | NOT DONE | Drift detection tests | Drift alarms fire within 60s of contract change |
| NFR-011 | Fallback-induced failure rate | `&lt; 1%` | WP-X6 | NOT DONE | Fallback reliability tests | Fallback mode maintains `&lt; 1%` additional failure rate |
| NFR-012 | Zero silent contract downgrade in critical lanes | 0 events | WP-X6 | NOT DONE | Critical lane monitoring | Contract downgrades audited and never silent; audit log entry required |
| NFR-013 | OTel GenAI semantic convention compliance | 100% spans | WP-Y6 | NOT DONE | OTel instrumentation coverage | All orchestration spans use GenAI semantic conventions |
| NFR-014 | Structured JSON logging on all orchestration events | 100% events | WP-0001 | DONE | Logging audit | All events logged as structured JSON; schema validation passes |
| NFR-015 | EU AI Act risk classification tagging on orchestration decisions | All actions | WP-3001 | NOT DONE | Risk classification audit | Every orchestration decision tagged with risk classification |
| NFR-016 | Provider routing cost reduction via optimization | >= 20% reduction at maintained quality | WP-5003 | NOT DONE | Cost tracking and A/B tests | Cost-per-quality metric improved by >= 20% vs baseline |
| Persona | Primary Goals | Key FRs | Supporting FRs | Key NFRs | Test Categories |
|---------|---|---------|---|----------|---|
| **Operator** | Execute decisions with clarity; maintain situational awareness | FR-001, 015, 016, 017, 022, 039 | FR-002, 004, 006, 020, 023 | NFR-001, 008 | Cat-1 (routing), Cat-12 (disclosure), Cat-13 (calibration) |
| **Incident Lead** | Recover from failures; coordinate response | FR-006, 007, 008, 009 | FR-002, 005, 021, 022 | NFR-005 | Cat-7 (circuit breaker), Playbook, HITL |
| **Platform/SRE** | Ensure stability, SLOs, runbook quality | FR-005, 019, 021, 035, 037 | FR-001, 002, 007, 013 | NFR-001, 002, 004 | Cat-9 (chaos), Burst simulation, Watchdog |
| **Governance/Compliance** | Enforce policy, audit, retention | FR-003, 010, 011, 012, 013, 014, 033 | FR-004, 005, 009 | NFR-004, 007, 015 | Cat-11 (policy/ABAC), Hash chain, Drift alarm |
| **Product Owner** | Measure value; launch readiness; cost | FR-024, 036 | FR-001, 005, 019, 039 | NFR-016 | Cost tracking, Closure |
| Journey | Steps | FRs | Personas | Acceptance Criteria |
|---------|-------|-----|----------|---|
| **UJ-1: Standard Execution** | Submit chunk → validate → route → execute → gate → promote → close | FR-001, 002, 003, 004, 005 | Operator, Platform/SRE | Deterministic routing verified (FR-001); idempotency enforced (FR-002); policy holds respected (FR-003); evidence complete (FR-004); integrity gate passes (FR-005) |
| **UJ-2: Policy Hold** | Submit → policy check → hold → human review → approve/deny → audit | FR-003, 010, 011, 012 | Operator, Governance | Policy blocks enforced (FR-003); override with reason code (FR-011); signed actions if critical (FR-010); immutable audit trail (FR-012) |
| **UJ-3: Failure Recovery** | Failure detected → classify → playbook select → execute → rollback if needed → validate → close/handoff | FR-006, 007, 008, 009 | Incident Lead, Platform/SRE | Checkpoint rollback restores state (FR-006); circuit breaker trips/recovers (FR-007); playbook auto-selects (FR-008); human escalation on repeated failures (FR-009) |
| **UJ-4: Burst Load** | Traffic spike detected → adaptive mode triggered → critical lane protected → load shed → restore normal | FR-019, 020, 021, 037 | Platform/SRE, Operator | Critical lane p95 `&lt; 350ms` under 5x load (FR-019); non-critical items deferred with ETA (FR-020); continuity watchdog active (FR-021); speculative execution reduces latency (FR-037) |
| **UJ-5: Shift Handoff** | Shift end → continuity snapshot generated → new owner receives → confirms receipt → acknowledgment logged | FR-018, 021, 022 | Operator, Incident Lead | Snapshots 100% coverage of open critical tasks (FR-018); watchdog monitors stale ownership (FR-021); decision replay with rationale captured (FR-022) |
| Gate | Phase | Criteria | Key FRs | Key WPs | Test Validation | Launch Blocker |
|------|-------|----------|---------|---------|---|---|
| **A** | Phase 0 | Schema integrity; telemetry baseline; OTel compliance | FR-026, NFR-013, NFR-014 | WP-0001, WP-0002, WP-Y6 | Golden corpus; OTel instrumentation; JSON schema validation | No |
| **X** | Phase X | Contract registry operational; adapters pass conformance; adversarial parser robust | FR-025-031, NFR-009-010, NFR-012 | WP-X1-X8 | 50-70 tests: golden corpus (18+26 tag), adversarial XML, provider drift, semantic validation | Yes |
| **B** | Phase 1 | Deterministic replay 100% consistent; idempotency enforced; evidence complete | FR-001, 002, 004, 005 | WP-1001-1005 | 1000+ replay runs; idempotency token validation; evidence audit | Yes |
| **C** | Phase 2 | Rollback succeeds within SLA; recovery playbooks tested; chaos drills pass | FR-006, 007, 008, 034, 035 | WP-2001-2008, WP-Y2-Y3 | Rollback execution traces; circuit breaker state machine; DLQ poison pill; chaos injection results | Yes |
| **D** | Phase 3 | Policy checks enforced; audit trail immutable; drift detection active; signed actions verified | FR-003, 010-014, 033 | WP-3001-3008, WP-Y5 | Policy bypass blocked; signature verification; audit query `&lt; 500ms`; drift alarm `&lt; 60s` | Yes |
| **E** | Phase 4 | UX comprehension tests pass; safe fallback works; decision replay renders; stale state blocked | FR-015-018, 022, 023, 039, 040 | WP-4001-4008, WP-Y7 | Operator comprehension studies; fallback UX tests; replay rendering latency `&lt; 200ms` | No |
| **F** | Phase 5 | Critical path stable under burst; adaptive caps avoid oscillation; continuity snapshots at every boundary | FR-019-021, 036, 037 | WP-5001-5008, WP-Y4, WP-Y8 | Burst simulation with 5x traffic; cost tracking A/B tests; speculative execution clean cancellation | No |
| **G** | Phase 6 | Launch dress rehearsal passes; compliance signoff received; KPI baselines met; runbook certified | FR-024, all NFRs | WP-6001-6008 | Dress rehearsal execution; SLO compliance report; runbook certification; two stable release cycles | Yes |
| Layer | Modules | Can Import From | Cannot Import |
|-------|---------|----------------|---------------|
| Surface | main.py, cli.py, mcp_server.py | All layers | — |
| Orchestration | orchestration_modes.py, execution.py | Contracts, Agents, Config | Surface |
| Governance | governance/ (future: policies, audit, overrides) | Contracts, Execution, Models | Surface, Orchestration details |
| Contracts | contracts/ | Models (adapters only), Config | Surface, Orchestration, Agents |
| Agents | agents/, models/ | Config | Contracts, Orchestration |
| Planning | planning/ | Contracts, Agents, Models, Config | Surface, Governance |
| Config | config.py | — | Everything |
| ID | Pattern | Key Insight | Implementation |
|----|---------|-------------|----------------|
| P-003 | Multi-Phase Checkpointing with Continuity Packets | Capture phase, progress, unresolved risks per checkpoint | execution.py + CheckpointMeta |
| P-005 | State Machine per Run (RUNNING→PAUSED→COMPLETED) | Explicit pause/resume semantics; idempotent frontier dispatch | execution.py + RunState enum |
| P-006 | Handoff Packet Schema | Structured continuity for operator transition (run_id, phase, summary, next_action) | STATE_AWARE_ORCHESTRATION_DESIGN.md |
| ID | Pattern | Key Insight | Implementation |
|----|---------|-------------|----------------|
| P-001 | Strict Core + Rich Extension | Minimal canonical schema + optional extension blocks | contracts/csm.py |
| P-002 | Tag Vocabulary as Typed Schema | Zen 26-tag vocabulary mapped to typed fields | contracts/csm.py |
| P-004 | Namespace-Based Contract Versioning | `xmlns="urn:thegent:csm:v2"` for version negotiation | contracts/registry.py |
| P-007 | Dual Validator (Structural + Semantic) | Structural first, semantic second — fail fast | contracts/validation.py |
| P-011 | Typed Structured Output with Validation Retry | Pydantic models with auto-retry on validation failure | contracts/adapters.py |
| P-012 | Consolidated Tool Surface with Operation Enums | One tool, many operations vs endpoint explosion | operations.py |
| ID | Pattern | Key Insight | Implementation |
|----|---------|-------------|----------------|
| P-013 | XMLPullParser Feed/Read Cycle | Incremental parsing for LLM streaming output | contracts/parser.py |
| P-014 | Sloppy XML Handling | Recover from unclosed tags, mixed content | contracts/parser.py |
| P-016 | Multi-Level Fallback with Confidence Degradation | MCP → XML → raw text, confidence drops at each level | contracts/state_machine.py |
| P-018 | Fallback State Machine | Primary → Degraded → Fallback → Recovered | contracts/state_machine.py |
| ID | Pattern | Key Insight | Implementation |
|----|---------|-------------|----------------|
| P-020 | Adapter Factory Pattern | Provider-specific adapters with common interface | agents/registry.py |
| P-021 | Provider Scoring (4-Factor) | reliability * latency * cost * capability | models/catalog.py |
| P-022 | function_with_fallbacks Chaining | LiteLLM-style ordered provider fallback | agents/resilience.py |
| P-026 | Proactive Rate Limit Tracking | Pre-request check, burst smoothing, backpressure | agents/resilience.py |
| P-030 | Routing Strategies as First-Class Enum | prefer_direct, prefer_proxy, failover, cost_optimized | models/catalog.py |
| ID | Pattern | Key Insight | Implementation |
|----|---------|-------------|----------------|
| P-034 | 3-State Circuit Breaker | CLOSED → OPEN → HALF-OPEN with configurable thresholds | agents/resilience.py |
| P-036 | IdempotencyKey | `(run_id, step_index, action_type, content_hash)` | execution.py |
| P-038 | Thread-Based Checkpointing | PostgresSaver-style with thread_ts snapshots | execution.py |
| P-040 | MAST 14-Mode Failure Taxonomy | Infrastructure/Model/Tool/Logic/Security modes | NEW: orchestration/failure_modes.py |
| P-042 | Dead-Letter Queue + Poison Pill | Quarantine after 3 identical failures | NEW: orchestration/dlq.py |
| ID | Pattern | Key Insight | Implementation |
|----|---------|-------------|----------------|
| P-047 | ABAC Authorization with Policy Engine | Attributes (risk, confidence, owner, env) → OPA Rego → allow/deny | NEW: governance/policy_engine.py |
| P-048 | Signed Action Artifacts with MAIF Structure | Cryptographic binding: Hash(action_data \|\| evidence_hash \|\| nonce) | NEW: governance/artifacts.py |
| P-066 | OPA/Rego Declarative Policy | Policy-as-code, version-controlled, CI-tested; `&lt;50ms` eval | NEW: governance/policy_engine.py |
| P-069 | Immutable Audit Trail + Hash Chain | Append-only with cryptographic linking; 35K-280K events/sec | NEW: governance/audit.py |
| P-071 | Management by Exception | Agent autonomous; escalate on confidence `&lt;` threshold | orchestration_modes.py |
| P-075 | Override with TTL + Revalidation | Time-bounded overrides that auto-expire; no caching | NEW: governance/overrides.py |
| P-077 | Trust Boundary Checks | Environment transition validation (dev→staging→prod); Zero Trust model | NEW: governance/trust.py |
| P-085 | Risk-Based Escalation SLA | Tiered approval by risk level; timeout → escalate/auto-deny | NEW: governance/escalation.py |
| ID | Pattern | Key Insight | Implementation |
|----|---------|-------------|----------------|
| P-088 | Role-Aware Confidence Calibration | Operators see traffic-light; Incident Leads see breakdowns; Compliance sees audit trail | NEW: ux/confidence_views.py |
| P-090 | Mission Control 4-Pane Layout | Queue + Roster + Stream + Details | NEW: ux/cockpit.py |
| P-092 | Progressive Disclosure 3-Tier | Summary (Operator) → Detail (SRE) → Trace (Incident Lead) with defaults | NEW: ux/explanations.py |
| P-096 | 3-Action Safe Fallback | Pause / Rollback / Escalate always visible; human-as-a-tool fallback | NEW: ux/fallback_ui.py |
| P-098 | Dual Confidence/Risk Indicator | Confidence + risk displayed together with calibration factor | NEW: ux/calibration.py |
| P-099 | Decision Replay 4-Capability | Replay View, What-If, Pre-Flight, Training; W3C trace context | NEW: ux/replay.py |
| KPI | Metric | Target | Alert |
|-----|--------|--------|-------|
| T: Throughput | tasks/min | >= baseline | `&lt; 80%` baseline |
| R: Routing accuracy | correct_route / total | >= 95% | `&lt; 90%` |
| A: Accuracy | correct_decision / total | >= 90% | `&lt; 85%` |
| F: Freshness | state_age_seconds | `&lt; 30s` | > 60s |
| F: Fallback rate | fallback / total | `&lt; 5%` | > 10% |
| I: Interruption burden | interruptions/hr | `&lt; 5`/hr | > 10/hr |
| C: Cost efficiency | cost / budget | `&lt; 100%` | > 120% |
| K: Knowledge retention | reuse / total | >= 80% | `&lt; 60%` |
| +: Rollback success | success / attempts | >= 99% | `&lt; 95%` |
| +: Continuity coverage | covered / total_critical | 100% | `&lt; 95%` |
| Concern | Choice | Rationale | Status |
|---------|--------|-----------|--------|
| Policy engine | OPA/Rego (optional) | Declarative, OSS, `&lt;50ms` eval, CNCF graduated | Future |
| Authorization framework | ABAC + Oso/Polar (optional) | Policy-as-code, context-aware, audit-ready | Future |
| Guardrails | NeMo Guardrails (optional) | Input/output rails, Colang 2.0 flows, parallel rails | Future |
| LLM Gateway | Portkey (optional) | Cost tracking, multi-provider routing, circuit breaker per provider | Future |
| Checkpointing | JSONL + file-based | Simple, no external deps; upgrade to PostgresSaver later | Current |
| State machine | RunState enum (RUNNING/PAUSED/COMPLETED/FAILED) | Explicit pause/resume semantics for continuity packets | Current |
| Circuit breaker | tenacity + custom state tracking | Already using tenacity; add per-subsystem CLOSED/OPEN/HALF-OPEN | Current |
| Observability | OpenTelemetry GenAI | Industry standard, gen_ai.* semantic conventions, W3C trace context | Future |
| Audit storage | File-based WORM (JSONL) | Hash-chained events; upgrade to append-only DB (AWS S3, Azure Blob) | Current |
| Audit events | RunMeta.prev_hash + RunRegistry | SHA-256 hash chain for tamper detection | Current |
| XML parsing | xml.etree XMLPullParser + sloppy-xml fallback | Stdlib, incremental, streaming-capable; handles malformed LLM output | Current |
| Auth (MCP) | Bearer token | Simple; upgrade to OAuth 2.1 CIMD later | Current |
| Cost tracking | Per-run accumulation (RunMeta.cost_usd) | File-based; upgrade to time-series DB later | Future |
| Sandbox | Process isolation (subprocess + timeout) | Native; upgrade to gVisor/Firecracker for multi-tenant later | Future |
| Evidence structure | MAIF-inspired hash binding | Cryptographic linking of action → evidence; 2–3 KB per event with signatures | Future |
| Distributed tracing | Correlation IDs (run_id, correlation_id) | Run-level trace; upgrade to OpenTelemetry/OpenInference later | Current |
| Module | Location | Status | Key Files | Gap |
|--------|----------|--------|-----------|-----|
| **Contracts** | `src/thegent/contracts/` | Implemented | csm.py, registry.py, adapters.py, parser.py, validation.py, conformance.py | CSM lacks risk_score, confidence_score (add to dataclass) |
| **Execution** | `src/thegent/execution.py` | Implemented | RunMeta, CheckpointMeta, RunRegistry, RunState | RunState enum ready; extend for pause/resume semantics |
| **Agents** | `src/thegent/agents/` | Implemented | base.py, registry.py, resilience.py, state_machine.py, modes.py | Circuit breaker has basic state; needs per-subsystem config |
| **Models** | `src/thegent/models/` | Implemented | catalog.py (provider scoring) | Routing strategies ready; cost optimization pending |
| **Planning** | `src/thegent/planning/` | Implemented | simulation.py | Risk/confidence scoring framework needed |
| **Orchestration** | `src/thegent/orchestration_modes.py` | Implemented | MultiAgentMode enum, mode suggestion | Expand to support recovery/governance routing |
| **Governance** | `src/thegent/governance/` | **Missing** | — | Create: policy_engine.py, audit.py, overrides.py, trust.py, escalation.py, artifacts.py |
| **UX/Cockpit** | `src/thegent/ux/` | **Missing** | — | Create: cockpit.py, explanations.py, fallback_ui.py, calibration.py, replay.py, confidence_views.py |
| **Recovery** | `src/thegent/recovery/` | **Missing** | — | Create: failure_modes.py, dlq.py, playbooks.py |
| **Observability** | `src/thegent/observability/` | **Partial** | telemetry.py | Expand for OpenTelemetry GenAI and W3C trace context |
| Framework | Requirement | TRAFFIC KPI | Retention | Evidence Source |
|-----------|-------------|-------------|-----------|-----------------|
| GDPR | Data processing logs | F: Freshness (`&lt;30s`) | 6 months | Audit trail by owner_id |
| SOC 2 | Processing integrity | A: Accuracy (>=90%) | 12 months | Decision replay tests |
| SOX | Financial data audit | T: Throughput (baseline) | 7 years | Cost attribution logs |
| PCI-DSS | Cardholder access logs | K: Knowledge retention (>=80%) | 1 year (3 mo. immediate) | Access audit by owner_id |
| EU AI Act | Risk management + FRIA | R: Routing accuracy (>=95%) | Duration + post-market | Policy gate logs + evidence |
| Attribute | Source | Example Values |
|-----------|--------|-----------------|
| `risk_score` | Planner/Orchestration | 0.0–1.0 |
| `confidence_score` | Agent self-report | 0.0–1.0 |
| `action_type` | Action enum | "tool_call", "file_write", "rollback", "override" |
| `owner_id` | RunMeta.owner | "alice", "droid_instance_42" |
| `environment` | Config/deployment | "canary", "staging", "production" |
| `evidence_completeness` | Governance state | 0.0–1.0 |
| `time_of_day` | Runtime | "business_hours", "off_hours" |
| Scenario | Pattern | Implementation |
|----------|---------|-----------------|
| Interrupt & Resume | Pause on policy denial; await approval; resume | orchestration_modes.py + execution.RunState.PAUSED |
| Human-as-a-Tool | Agent calls approval endpoint; blocks until response | recovery_modes.py (R4, R7) |
| Risk-Based Routing | Low risk auto-approve; high risk sync approval | governance/escalation.py + trust score mapping |
| Async Notification | Medium risk → governance queue → email/Slack | governance/escalation.py + alerting [Future] |
| Failure Class | Mode | Circuit Breaker | Recovery | Example |
|---------------|------|-----------------|----------|---------|
| **Infrastructure** | INFRA_TIMEOUT | Tool/Model | Retry + fallback provider | LLM API timeout |
| | INFRA_RATE_LIMIT | Model provider | Backoff + queue | 429 Too Many Requests |
| | INFRA_UNAVAILABLE | Subsystem | Circuit OPEN | Service down |
| **Model** | MODEL_INVALID_RESPONSE | Model | Re-prompt | Malformed JSON |
| | MODEL_TOKEN_LIMIT | Model | Summarize + retry | Context too long |
| | MODEL_HALLUCINATION | Model | Retrieval + retry | Factual error |
| **Tool** | TOOL_NOT_FOUND | Tool | Suggest alternate | Wrong function name |
| | TOOL_PERMISSION_DENIED | Tool | Escalate to human | Permission error |
| | TOOL_EXECUTION_ERROR | Tool | Detailed error → recovery playbook | Command failed |
| **Logic** | LOGIC_INCONSISTENCY | Action | Rollback to checkpoint | Contradictory state |
| | LOGIC_INFINITE_LOOP | Action | Timeout + escalate | Stuck in loop |
| **Security** | SECURITY_POLICY_BLOCK | Policy Gate | Escalate per SLA (WP-3008) | Signature mismatch |
| | SECURITY_EVIDENCE_INCOMPLETE | Policy Gate | Queue for human review | Missing evidence hash |
| | SECURITY_UNAUTHORIZED | Auth | Deny + audit | Unauthorized access |
| **Meta** | RECOVERY_EXHAUSTED | Recovery system | Escalate to human (WP-4009) | All recovery options failed |
| | SCALE_SATURATION | Adaptive scale | Defer non-critical + alert | Resource capacity exceeded |
| | CONTINUITY_GAP | State machine | Block + escalate (WP-4009) | State unavailable after resume |
| WP Range | Primary Files | Secondary Files |
|----------|--------------|-----------------|
| WP-0001..0005 | `execution.py`, `config.py`, `models/` | `cli_impl.py`, `main.py` |
| WP-X1..X8 | `contracts/registry.py`, `contracts/adapters.py` | `cli_impl.py`, `mcp_server.py` |
| WP-1001..1008 | `orchestration/*.py` (NEW) | `cli_impl.py`, `main.py` |
| WP-2001..2008 | `orchestration/*.py`, `agents/resilience.py` | `execution.py` |
| WP-3001..3008 | `governance/*.py` (NEW) | `cli_impl.py`, `main.py` |
| WP-4001..4008 | `ux/*.py` (NEW) | `cli_impl.py`, `main.py`, `mcp_server.py` |
| WP-5001..5008 | `orchestration/*.py`, `models/catalog.py` | `execution.py`, `config.py` |
| WP-6001..6008 | `docs/`, `tests/` | — |
| WP-Y1..Y8 | Mixed (see WBS) | — |
- [ ] Implementation in correct module (`src/thegent/...`)
- [ ] CLI command in `main.py` (typer @app.command, no logic, calls _impl)
- [ ] MCP tool in `mcp_server.py` (@mcp.tool, async-capable, timing-aware)
- [ ] Implementation in `cli_impl.py` (pure function, returns dict/list, no printing)
- [ ] Configuration in `config.py` if adding env vars (ThegentSettings subclass)
- [ ] All public functions have type hints
- [ ] Pydantic BaseModel for all data structures
- [ ] Return type annotations (avoid -> Any, use -> dict[str, ...])
- [ ] Typed exceptions (not bare Exception or except:)
- [ ] Unit tests in `tests/test_unit_*.py`
- [ ] Integration tests if cross-module (`tests/test_integration_*.py`)
- [ ] FR trace comments: `# @trace FR-XXX-NNN` or decorator
- [ ] Test names descriptive: `def test_some_feature_when_condition_then_result()`
- [ ] No print statements in _impl functions (use return values)
- [ ] No f-strings in error messages (use f"error: {var}" with context)
- [ ] ruff lint clean: `ruff check src/thegent/`
- [ ] mypy passes: `mypy src/thegent/`
- [ ] Line length `&lt;`= 120 chars
- [ ] Imports sorted and checked by ruff
- [ ] Module docstring with purpose
- [ ] Function docstrings with Args, Returns
- [ ] Complex logic has inline comments (why, not what)
- [ ] WP reference in module: `# WP-XXXX`
| Level | Target | Current | Gap |
|-------|--------|---------|-----|
| Unit | 70% of tests | 37.5% | Under-indexed (needs ~127 more unit tests) |
| Integration | 20% of tests | 0.4% | Severely under-indexed (needs ~100 more integration tests) |
| E2E | 10% of tests | 62.1% | Over-indexed (should rebalance to 10% as unit/integration grow) |
| Priority | Categories | Test Count | When |
|----------|-----------|------------|------|
| P0 | 1, 2 | 50-70 | Phase X |
| P1 | 3, 4, 5 | 75-100 | Phase X, 1 |
| P2 | 6, 7, 8 | 35-50 | Phase 2 |
| P3 | 9, 10, 11, 12 | 55-80 | Phase 2, 3, 4 |
| P4 | 13, 14 | 10-20 | Phase 4, 5 |
| **Total** | **14** | **225-320** | |
| FR | Test Category | Min Tests |
|----|--------------|-----------|
| FR-001 | Replay suite | 5 |
| FR-002 | Idempotency | 5 |
| FR-003 | Policy bypass | 5 |
| FR-004 | Evidence lint | 5 |
| FR-005 | Regression probes | 5 |
| FR-006 | Rollback | 5 |
| FR-007 | Circuit breaker (Cat 7) | 15 |
| FR-008 | Playbook | 5 |
| FR-009 | HITL | 3 |
| FR-010 | Signature | 5 |
| FR-011 | Override TTL | 5 |
| FR-012 | Hash chain | 5 |
| FR-013 | Drift alarm | 5 |
| FR-014 | Boundary | 5 |
| FR-015 | Disclosure (Cat 12) | 15 |
| FR-016 | Fallback UX | 5 |
| FR-017 | Stale state | 5 |
| FR-018 | Handoff | 5 |
| FR-019 | Burst simulation | 5 |
| FR-020 | Deferral | 3 |
| FR-021 | Watchdog | 3 |
| FR-022 | Replay | 5 |
| FR-023 | Calibration (Cat 13) | 5 |
| FR-024 | Closure | 3 |
| FR-025 | Negotiation | 5 |
| FR-026 | Golden corpus (Cat 1+2) | 50 |
| FR-027 | Adversarial (Cat 3) | 40 |
| FR-028 | Semantic (Cat 4) | 15 |
| FR-029 | Drift (Cat 5) | 20 |
| FR-030 | Fallback chaos (Cat 6) | 10 |
| FR-031 | Migration | 5 |
| FR-032 | Multi-agent (Cat 10) | 10 |
| FR-033 | ABAC (Cat 11) | 10 |
| FR-034 | DLQ (Cat 8) | 10 |
| FR-035 | Chaos (Cat 9) | 20 |
| FR-036 | Cost tracking | 5 |
| FR-037 | Speculative (Cat 14) | 5 |
| FR-038 | Routing | 5 |
| FR-039 | Autonomy | 3 |
| FR-040 | Simulation | 5 |
| FR-041 | Calibration | 5 |
| FR-042 | Prompt hierarchy | 5 |
| File | Tests | Type | Covers |
|------|-------|------|--------|
| tests/test_unit_cli.py | 23 | Unit | CLI commands, argument parsing, output formatting |
| tests/test_unit_config.py | 6 | Unit | Configuration loading and defaults |
| tests/test_unit_contracts.py | 13 | Unit | CSM registry, serialization, semantic validation |
| tests/test_unit_execution.py | 6 | Unit | RunRegistry, task execution tracking |
| tests/test_unit_health_serializers.py | 16 | Unit | Health gate/report/trend serialization (CSV, JSONL, MD) |
| tests/test_unit_health_trend.py | 7 | Unit | Health trend tracking and deltas |
| tests/test_unit_mcp.py | 15 | Unit | MCP tool integration, message passing |
| tests/test_unit_models.py | 21 | Unit | Model catalog, route resolution |
| tests/test_unit_output_parser.py | 20 | Unit | Extract_condensed, JSONL parsing, think block removal |
| tests/test_unit_providers_comprehensive.py | 12 | Unit | Provider adapter testing |
| tests/test_unit_registry.py | 11 | Unit | Agent registry lookup and caching |
| tests/test_unit_runners.py | 7 | Unit | Agent runner execution |
| tests/test_unit_orchestration_modes.py | 7 | Unit | Sequential/parallel/review orchestration |
| tests/test_unit_cliproxy_manager.py | 13 | Unit | Cliproxy manager state and transitions |
| tests/test_integration_agent.py | 2 | Integration | End-to-end agent flow |
| tests/test_agent_sync_async_validation.py | 2 | Integration | Sync/async coordination validation |
| tests/test_e2e_cli.py | 319 | E2E | Full CLI commands (list-agents, run, dag ops, health gates) |
| tests/test_e2e_health_trend_cli.py | 11 | E2E | Health trend CLI commands |
| tests/test_resilience.py | 13 | Unit | Failure classification, retry logic, transient error handling |
| tests/test_contract_conformance.py | 6 | Unit | Provider adapter CSM conformance (uses @pytest.mark.parametrize) |
| tests/test_ci_architecture.py | 1 | Unit | CI architecture constraints |
| Category | Count | Focus |
|----------|-------|-------|
| Performance Optimization | 21 | Latency, throughput, memory |
| Robustness Hardening | 18 | Error handling, edge cases, resilience |
| UX Polish | 14 | Clarity, discoverability, feedback |
| Developer Experience | 13 | Debugging, testing, extensibility |
| Operational Excellence | 15 | Monitoring, alerting, maintenance |
| Design Elegance | 12 | Clean abstractions, composability |
| **Total** | **93** | |
| ID | Item | Priority | Impact |
|-----|------|----------|--------|
| QW-001 | Add `payload_signature` hash to health gate/report tools for deterministic caching | P1 | Avoid redundant recompute of health status |
| QW-002 | Implement `_resolve_cwd()` caching with stat-based TTL in mcp_server.py | P1 | Reduce path resolution overhead in loops |
| QW-003 | Extract AcceptedElicitation/DeclinedElicitation imports to avoid repeated definitions | P2 | Reduce mcp_server.py verbosity; ~20 LOC savings |
| QW-004 | Add `idempotent=True` annotation to all read-only tools in mcp_server (verify 25+ tools) | P1 | Enable client caching of safe reads |
| QW-005 | Model scraper: add concurrent.futures to parallelize gemini/claude/proxy API calls | P2 | Scraping time 3-4x faster (currently sequential) |
| QW-006 | Output parser: cache `_THINK_PATTERN` and noise regex patterns as compiled module singletons | P2 | Reduce regex recompile overhead on each parse |
| QW-007 | Resilience: add failure classification caching per (result.stderr_hash, provider) pair | P2 | Skip re-classify on duplicate errors |
| QW-008 | Add OpenTelemetry span attributes (model, provider, exit_code) to all run_impl calls | P1 | Enable provider/model-level observability |
| ID | Item | Priority | WP | Impact |
|----|------|----------|-----|--------|
| OPT-001 | Response caching middleware (30s TTL for read-only tools) | P1 | WP-X6 | Reduce redundant calls by ~60% |
| OPT-002 | Rate limiting middleware (10/s, burst 20) for MCP | P1 | WP-X6 | Prevent resource exhaustion |
| OPT-003 | Response size limiting (500KB cap for logs) | P1 | WP-X6 | Prevent OOM on large sessions |
| OPT-004 | Connection pooling for provider HTTP clients | P2 | WP-1001 | Reduce connection overhead 40% |
| OPT-005 | Model catalog scraping with async gather | P2 | WP-1007 | Parallel scraping 3-5x faster |
| OPT-006 | Lazy adapter loading (import on first use) | P2 | WP-X5 | Reduce startup time ~200ms |
| OPT-007 | Incremental parser with early-exit on structural failure | P1 | WP-X3 | Avoid full parse on bad input |
| OPT-008 | LRU cache for policy evaluation results (with TTL) | P2 | WP-3001 | `&lt;50ms` repeated evaluations |
| OPT-009 | Checkpoint compression (zlib for large DAG states) | P3 | WP-2001 | Reduce storage 60-80% |
| OPT-010 | Batch event emission (buffer + flush every 100ms) | P2 | WP-0001 | Reduce I/O overhead |
| OPT-011 | Hash chain computation with incremental SHA-256 | P2 | WP-3004 | Constant memory audit trail |
| OPT-012 | Provider health probe with adaptive interval | P3 | WP-2003 | Reduce probe overhead in stable state |
| OPT-013 | Speculative dual-provider execution for critical paths | P4 | WP-5001 | 30-50% latency reduction |
| OPT-014 | Model routing with prompt-characteristic analysis | P4 | WP-1007 | 20-40% cost reduction |
| OPT-015 | Cost-aware provider selection (RouteLLM pattern) | P3 | WP-5003 | Optimal cost/quality tradeoff |
| OPT-016 | Model scraper parallelization (concurrent.futures on gemini/claude/proxy adapters) | P2 | WP-1007 | Scraper 3-5x faster; ~400ms vs 1.2s |
| OPT-017 | Compiled regex cache for output parser (noise patterns, think blocks) | P2 | WP-X3 | ~20% faster per-message parsing |
| OPT-018 | ElicitationResponse caching with SHA256 of prompt+response | P3 | WP-X6 | Avoid re-eliciting identical contexts |
| OPT-019 | Session metadata bloom filter (fast negative lookups on session_id) | P3 | WP-2001 | O(1) session existence checks |
| OPT-020 | Route resolution memo with model ID hash prefix (LRU, 1000 entries) | P2 | WP-1001 | Sub-1ms repeated route lookups |
| OPT-021 | OpenTelemetry span attributes on all run/bg/status calls (model, provider, lane, confidence) | P1 | WP-Y6 | Provider/model-level observability |
| ID | Item | Priority | WP | Impact |
|----|------|----------|-----|--------|
| ROB-001 | Sloppy XML recovery for unclosed tags in LLM output | P0 | WP-X3 | Handle 90%+ of malformed outputs |
| ROB-002 | Partial-state validity markers during streaming parse | P1 | WP-X3 | No invalid state exposure |
| ROB-003 | Poison pill detection for repeated identical failures | P2 | WP-Y2 | Stop infinite retry loops |
| ROB-004 | Circuit breaker per-provider with independent state | P1 | WP-2003 | Isolate provider failures |
| ROB-005 | Idempotency tokens on all state-changing operations | P1 | WP-1003 | No duplicate side effects |
| ROB-006 | Hash chain integrity verification on audit read | P2 | WP-3004 | Detect tampered audit logs |
| ROB-007 | Graceful shutdown with in-flight request drain (30s) | P1 | WP-X6 | No dropped requests on restart |
| ROB-008 | Session state recovery from file system after crash | P1 | WP-2001 | Resume without data loss |
| ROB-009 | Provider timeout escalation (5s → 15s → 30s) | P2 | WP-2002 | Adapt to provider latency |
| ROB-010 | Contract version downgrade prevention in critical lanes | P1 | WP-X6 | No silent quality regression |
| ROB-011 | Stale-state detection with freshness timestamps | P2 | WP-4005 | Block execution on stale context |
| ROB-012 | Continuity watchdog with escalation on stale ownership | P2 | WP-5005 | No orphaned critical tasks |
| ROB-013 | Configuration validation on startup (fail-fast) | P1 | — | Catch misconfig before serving |
| ROB-014 | File descriptor limit check before starting sessions | P3 | — | Prevent fd exhaustion crashes |
| ROB-015 | Sloppy XML recovery with tag balancing heuristics (close unclosed tags) | P1 | WP-X3 | Handle 95%+ of incomplete XML output |
| ROB-016 | Elicitation timeout enforcement (5s default, fail-safe) | P2 | WP-X6 | No stuck tools on missing input |
| ROB-017 | Model route resolution fallback chain (prefer_direct → prefer_proxy → error) | P1 | WP-1001 | Graceful degradation on route miss |
| ROB-018 | Provider health self-healing: auto-mark-healthy on 3 consecutive successes | P2 | WP-2003 | Recovery from transient provider issues |
| ID | Item | Priority | WP | Impact |
|----|------|----------|-----|--------|
| UX-001 | Tool annotations (read_only, destructive, idempotent) on all MCP tools | P1 | — | Client UI hints |
| UX-002 | Structured ToolResult with structured_content + meta.execution_time_ms | P1 | — | Rich client rendering |
| UX-003 | Action-oriented tool descriptions (verb-first, concise) | P2 | — | Better agent discovery |
| UX-004 | Parameter docs with clear defaults, units, constraints | P2 | — | Fewer invalid calls |
| UX-005 | Error messages with actionable remediation hints | P1 | — | Self-service error recovery |
| UX-006 | Confidence + risk dual indicator in all responses | P2 | WP-4008 | Informed decision-making |
| UX-007 | Safe fallback 3-action (Pause/Rollback/Escalate) always visible | P2 | WP-4003 | Safety net for operators |
| UX-008 | Progressive disclosure: summary → detail → trace | P2 | WP-4002 | Reduced cognitive load |
| UX-009 | Persona-aware default display level | P3 | WP-4002 | Right info for right role |
| UX-010 | Alert fatigue controls: dedup, correlation, digest, ceiling | P3 | WP-4004 | Manageable alert volume |
| UX-011 | Decision replay with what-if mode | P3 | WP-4007 | Learning from past decisions |
| UX-012 | Autonomy gradient dial per agent/scenario | P3 | WP-4001 | Operator control granularity |
| UX-013 | MCP tool descriptions with inline parameter constraints (min, max, enum values) | P2 | — | Client validation before send |
| UX-014 | Structured ToolResult.meta with execution_time_ms on all thegent_* tools | P1 | — | Visibility into tool performance |
| ID | Item | Priority | WP | Impact |
|----|------|----------|-----|--------|
| DX-001 | Architecture boundary enforcement in CI (import checks) | P2 | — | Prevent layer violations |
| DX-002 | Contract conformance test generation from schema | P2 | WP-X5 | Auto-generate test vectors |
| DX-003 | thegent inspect tool for multi-session debugging | P1 | — | Quick status across sessions |
| DX-004 | Route resolution probe API (dry-run routing) | P1 | WP-1001 | Test routing without execution |
| DX-005 | Contract introspection CLI (list contracts, versions, adapters) | P2 | WP-X1 | Schema discovery |
| DX-006 | Health trend visualization (ASCII sparklines in CLI) | P3 | WP-Y7 | Quick trend assessment |
| DX-007 | Chaos engineering test harness with fault injection hooks | P3 | WP-Y3 | Reproducible fault testing |
| DX-008 | Provider capability matrix in CLI output | P2 | — | Discover provider features |
| DX-009 | Run-diff tool (compare two execution traces) | P3 | WP-4007 | Debug non-determinism |
| DX-010 | Config validation command (thegent config check) | P2 | — | Pre-flight config verification |
| DX-011 | Execution trace replay tool (compare two run_ids' logs + decisions) | P3 | WP-4007 | Determinism debugging |
| DX-012 | Model routing debug probe (resolve_model_route --verbose with fallback chain) | P2 | WP-1001 | Diagnose routing issues |
| DX-013 | Provider health probe API with per-provider latency percentiles (p50, p95, p99) | P2 | WP-2003 | Detect degradation early |
| ID | Item | Priority | WP | Impact |
|----|------|----------|-----|--------|
| OPS-001 | TRAFFIC 10-metric KPI dashboard | P2 | WP-Y7 | Single-pane health view |
| OPS-002 | OTel GenAI semantic conventions on all spans | P1 | WP-Y6 | Industry-standard observability |
| OPS-003 | Structured JSON logging with run_id, provider, latency_ms | P1 | WP-0001 | Machine-queryable logs |
| OPS-004 | Cost tracking per-run with budget alerts | P2 | WP-Y4 | Cost visibility and control |
| OPS-005 | Provider health probes with SLO tracking | P2 | WP-2003 | Proactive failure detection |
| OPS-006 | Audit trail query interface (by run_id, time range, event type) | P2 | WP-3004 | Incident investigation |
| OPS-007 | Session cleanup for old sessions (configurable retention) | P3 | — | Disk space management |
| OPS-008 | Runbook with recovery playbook cross-references | P2 | WP-6004 | On-call readiness |
| OPS-009 | SLO certification with baseline measurements | P2 | WP-6003 | Launch confidence |
| OPS-010 | Decommission plan for temporary controls | P3 | WP-6006 | Controlled tech debt reduction |
| OPS-011 | Post-launch rollback reserve documentation | P2 | WP-6007 | Emergency recovery readiness |
| OPS-012 | Health gate trend snapshots with delta analysis (blocked_count_delta, ratio_delta) | P2 | WP-4008 | Detect regressions across releases |
| OPS-013 | Cost tracking dashboard per agent/provider with MTD and YTD summaries | P2 | WP-Y4 | Budget enforcement and showback |
| OPS-014 | Provider health reconciliation (sync probe state with actual performance) | P2 | WP-2003 | Fix stale health markers |
| OPS-015 | Governance escalation SLA tracking (auto-escalate after 2h on block) | P3 | WP-3008 | Prevent decision gridlock |
| ID | Item | Priority | WP | Impact |
|----|------|----------|-----|--------|
| DE-001 | Consolidated tool surface with operation enums (not endpoint explosion) | P1 | — | Clean API surface |
| DE-002 | Universal operation taxonomy (orchestrate, govern, recover, observe, plan) | P1 | — | Consistent mental model |
| DE-003 | Adapter factory pattern for providers (common interface, per-provider impl) | P1 | WP-X5 | Easy provider addition |
| DE-004 | DI-composed resilience stack (retry → fallback → circuit breaker → budget) | P2 | WP-2003 | Configurable resilience |
| DE-005 | Phase-gated lifecycle as explicit state machine | P2 | WP-1004 | No implicit transitions |
| DE-006 | Middleware-as-orchestration-contract (each layer adds guarantees) | P2 | — | Composable pipeline |
| DE-007 | Strict Core + Rich Extension schema design | P1 | WP-X2 | Backward-compatible evolution |
| DE-008 | Three-phase adoption model (Read-Only → Advisory → Automated) | P3 | WP-3001 | Gradual governance rollout |
| DE-009 | Failure classification taxonomy with provider-specific recovery hints | P2 | WP-2003 | Intelligent error handling |
| DE-010 | Adapter factory pattern for all model scrapers (common interface, strategy per provider) | P2 | WP-1007 | Clean scraper extensibility |
| DE-011 | Hierarchical prompt injection (platform policy → domain → workflow → step level) | P3 | WP-3001 | Policy composition without override sprawl |
| DE-012 | Contract versioning with graceful downgrade (prefer newer but accept older) | P2 | WP-X7 | Non-breaking contract evolution |
| ID | Item | Where | Evidence |
|-----|-------|-------|----------|
| OPT-001 | Response caching middleware | mcp_server.py:109-121 | ResponseCachingMiddleware with 30s TTL on thegent_ps, list_agents, list_models |
| OPT-002 | Rate limiting middleware | mcp_server.py:106 | RateLimitingMiddleware(10/s, burst=20) |
| OPT-003 | Response size limiting | mcp_server.py:122 | ResponseLimitingMiddleware(max=500K) |
| UX-001 | Tool annotations | mcp_server.py:408+ | readOnlyHint, destructiveHint, idempotentHint on all tools |
| UX-002 | Structured ToolResult | mcp_server.py:576-584 | ToolResult with structured_content and meta.execution_time_ms |
| DE-001 | Consolidated tool surface | mcp_server.py:405+ | thegent_run, bg, ps, status, logs, wait, stop, etc. (12 core tools) |
| DE-002 | Universal operation taxonomy | mcp_server.py:335-352 | thegent_list_operations with orchestrate/govern/recover/observe/plan |
| DE-003 | Adapter factory pattern | scrapers.py (inferred) | Provider-specific adapters with common interface |
| DE-007 | Strict Core + Rich Extension | output_parser.py:310-380 | ParseResult with error_class, partial_state |
| OPS-002 | OTel semantic conventions | mcp_server.py:511, 626 | ctx.info() logging with structured context |
| OPS-003 | Structured JSON logging | mcp_server.py:1436+ | LoggingMiddleware() in middleware stack |
| IDs | Count | Theme | Status |
|-----|-------|-------|--------|
| QW-001..008, OPT-001..003, OPT-021, ROB-001, ROB-007, ROB-013, ROB-015, ROB-017, UX-001..002, UX-005, UX-014, DE-001..003, DE-007 | 24 | Core quality + quick wins | Mostly done, verify annotations |
| IDs | Count | Theme | Status |
|-----|-------|-------|--------|
| OPT-004..008, OPT-016, OPT-020, ROB-002, ROB-004..005, ROB-010, ROB-018, UX-003..004, UX-006..008, UX-013, DX-001..005, DX-012..013, OPS-001..006, OPS-012..014, DE-004..006, DE-009..010 | 38 | Production hardening | In progress |
| IDs | Count | Theme | Status |
|-----|-------|-------|--------|
| OPT-009..012, OPT-017..019, ROB-003, ROB-006, ROB-009, ROB-011..012, ROB-016, UX-009..012, DX-006..011, OPS-007..011, OPS-015, DE-008, DE-011..012 | 26 | Polish and maturity | Planned |
| IDs | Count | Theme | Status |
|-----|-------|-------|--------|
| OPT-013..015, OPT-018, ROB-014 | 5 | Advanced optimization | Future consideration |
| # | Anti-Pattern | Prevention | WP |
|---|-------------|------------|-----|
| AP-01 | Schema-last development (contracts defined after code) | Contract-first mandate: CSM schema before implementation | WP-X2 |
| AP-02 | Doc-code mismatch (docs say PascalCase, code uses snake_case) | Code-is-contract; generate docs from schema; conformance tests | WP-X1 |
| AP-03 | Regex-only XML parsing (fragile under malformed LLM output) | XMLPullParser with sloppy-xml fallback; incremental parser; streaming validation | WP-X3 |
| AP-04 | Single-provider routing (no fallback on failure) | Provider chains with cost/time bounds; circuit breaker per provider; ordered fallback with SLA | WP-1001 |
| AP-05 | Flat failure taxonomy (7 classes too coarse for targeted recovery) | MAST 14-mode with mapped playbooks per mode; per-mode SLA and retry budget | WP-2005 |
| AP-06 | Infinite retry without DLQ (retry loops consume resources) | DLQ + poison pill detection after 3 identical failures; cost tracking; mandatory escalation | WP-Y2 |
| AP-07 | Code-embedded policy (policies hardcoded in business logic) | Declarative OPA/Rego policies; Git-versioned; OPAL auto-deployment; CI testing of policy rules | WP-3001 |
| AP-08 | Confidence without calibration (reported confidence unreliable) | Calibration curves per adapter type; windowed accuracy tracking; policy gates use calibrated_confidence field | WP-4008 |
| AP-09 | Recovery within failing agent (agent tries to self-recover) | External recovery service; separate Recovery DAG; escalation gate if recovery fails | WP-2004 |
| AP-10 | Alert storm without correlation (every event triggers alert) | Correlation-first alerting with dedup windows and ceiling (5/hr/operator); event grouping by root cause | WP-4004 |
| AP-11 | All-or-nothing rollback (roll back entire execution) | Graduated rollback: selective revert to last good checkpoint per failed component | WP-2001 |
| AP-12 | Implicit state changes (transitions without guards) | Explicit state machine with typed transition guards; pre-transition validation; immutable state snapshots | WP-1004 |
| AP-13 | One-size-fits-all display (same detail level for all roles) | Persona-based progressive disclosure (3 tiers: operator/incident/audit); role-aware APIs | WP-4002 |
| AP-14 | Hardcoded resilience logic (retry/fallback mixed into business) | DI-composed resilience stack: retry → fallback → CB → budget; declarative config per failure mode | WP-2003 |
| AP-15 | Endpoint explosion (one tool per operation) | Consolidated tools with operation enums and typed constraints | — |
| Mode | Category | Detection | Recovery | Escalation | Prevention |
|------|----------|-----------|----------|------------|-----------|
| F-01 | Infra: Network | Timeout/ConnectionError | Retry + exponential backoff (max 3 attempts, max 60s) | Circuit breaker → DLQ | Provider-specific network guards (timeout per provider config) |
| F-02 | Infra: Storage | IOError/PermissionError | Failover to replica; checkpoint recovery | Checkpoint replay from last valid state | Pre-flight storage availability check; replica health monitoring |
| F-03 | Infra: Rate limit | 429/RateLimitError; regex pattern match | Backpressure + provider rotation; wait Retry-After header if present | Provider rotation with cost tracking | Global rate limit budget per provider; preemptive throttle at 80% |
| F-04 | Model: Hallucination | Validation failure (semantic or structural) | Re-prompt with grounding context (previous outputs, constraints) | Human review with evidence context | Confidence calibration; semantic validation gates |
| F-05 | Model: Refusal | Safety filter trigger (provider-specific patterns) | Rephrase prompt; fallback to alternative provider | Skip action with audit reason code | Content policy pre-check; rephrase attempt before fallback |
| F-06 | Model: Context overflow | Token limit error (explicit or inferred) | Summarize context window; retry with chunked input | Chunking strategy with recursive aggregation | Per-provider token limit tracking; proactive summarization |
| F-07 | Model: Format violation | Schema validation fail; parse errors | Re-prompt with schema example; fallback parser with confidence reduction | Accept fallback-plain if no alt provider (audit alert) | Provider conformance tests; adapter regression suite |
| F-08 | Tool: Execution failure | Exception in tool invocation; non-zero exit code | Retry same tool (2 attempts); fallback to alternative tool | Manual fallback with escalation | Tool pre-flight checks; sandbox capability validation |
| F-09 | Tool: Misuse | Capability check fail; insufficient args | Re-plan with corrected tool selection | Agent role swap to higher capability | Capability matrix per agent; pre-execution validation |
| F-10 | Logic: Goal drift | Semantic divergence from original objective (NLP check) | Checkpoint rollback to last valid state; re-plan | Re-plan from scratch with new decomposition | Periodic goal consistency check; intermediate validation |
| F-11 | Logic: Loop/oscillation | Step counter exceeded (default 50); repeated state detection | Force termination of current attempt | DLQ + alert + manual investigation | Loop detection with early bail at 60% of max; state transition tracking |
| F-12 | Logic: Conflicting agents | Conflict detection via output diff | Majority vote if N≥3 agents; consensus resolution | Human arbitration if tie or N`&lt;3` | Consensus algorithm pre-configuration; conflict scoring |
| F-13 | Security: Prompt injection | Pattern detection (regex rules + NLP) | Quarantine action + full audit trail + incident notification | Incident response team activation | Input sanitization layer; prompt validation before execution |
| F-14 | Security: Data exfiltration | Egress monitoring (network policies, log scanning) | Block + audit; disable agent if repeated | Incident response + credential rotation | Network segmentation; egress whitelisting; data loss prevention scanning |
| Debt Item | Location | Issue | Resolution | Deadline |
|-----------|----------|-------|-----------|----------|
| TD-01 | `src/thegent/agents/resilience.py:35-60` | Failure classification uses hard-coded regex patterns; no versioning or provider-specific overrides | Implement versioned failure pattern ruleset with provider profiles; add CI validation tests | WP-1001 gate |
| TD-02 | `src/thegent/agents/state_machine.py:88-207` | Provider loop has no time or cost bounds; could exhaust budget on cascading failures | Add per-run cost budget tracker and wall-clock timeout enforcement | WP-2003 gate |
| TD-03 | `src/thegent/agents/state_machine.py:196-205` | Silent acceptance of violations when all providers exhausted; minimal logging | Raise explicit error requiring manual gate approval for any degraded output | WP-3001 gate |
| Debt Item | Location | Issue | Resolution | Deadline |
|-----------|----------|-------|-----------|----------|
| TD-04 | `src/thegent/contracts/adapters.py` | No mandatory adapter registration for new providers; runtime discovery fails late | Implement provider registry with CI lint rule blocking unregistered providers | WP-X1 gate |
| TD-05 | `src/thegent/contracts/adapters.py:15-23` | Confidence scores from different adapters not calibrated to same scale | Add calibration curves per adapter type; track accuracy vs predicted confidence | WP-4008 gate |
| TD-06 | `src/thegent/contracts/policy.py:40-43` | Policy gates use uncalibrated raw confidence scores | Change policy decision gates to use calibrated_confidence field from adapter result | WP-3001 gate |
| Debt Item | Location | Issue | Resolution | Deadline |
|-----------|----------|-------|-----------|----------|
| TD-07 | `src/thegent/execution.py:78-210` | Hash chain only covers runs; governance events/overrides not in chain | Extend hash chain to all audit events; implement WORM storage for immutable trail | WP-3004 gate |
| TD-08 | `src/thegent/agents/state_machine.py:140-200` | Semantic validation failures are logged but not committed to audit trail | Make semantic validation failures immutable audit events; block transition on failure in critical lanes | WP-1004 gate |
| TD-09 | `src/thegent/contracts/telemetry.py` (not yet read) | Fallback rate tracking is per-invocation; no windowed trend detection | Implement sliding window fallback rate tracking with upward-trend alerts | WP-4004 gate |
| Debt Item | Location | Issue | Resolution | Deadline |
|-----------|----------|-------|-----------|----------|
| TD-10 | `src/thegent/agents/state_machine.py` (recovery path) | Recovery from partial execution state is implicit; no formal state recovery protocol | Document and implement explicit recovery state machine with checkpoint replay | WP-2004 gate |
| TD-11 | `src/thegent/contracts/validation.py:20-52` | Semantic validation checks are static rules; no provider-specific or context-aware validation | Add validation context parameter; support provider-specific validation profiles | WP-X5 gate |
- [ ] All circuit breakers configured per provider with per-provider thresholds (not defaults)
- [ ] Failure classification patterns tested against 50+ real provider errors per adapter
- [ ] Cost tracking implemented; per-run and per-provider cost budgets enforced with alerts
- [ ] Provider loop time bounds set (max 5 min wall-clock per full chain attempt)
- [ ] Chaos tests pass for all MAST modes F-01 through F-14 with recovery validation
- [ ] Poison pill detection (3 consecutive identical errors) tested and logged
- [ ] All provider fallback chains tested end-to-end with circuit breaker trips
- [ ] All policy gates tested with bypass attempts and tamper tests
- [ ] OPA policy rules tested in CI (100% rule coverage with valid/invalid inputs)
- [ ] Hash chain integrity verified (test file modification detection)
- [ ] Immutable audit trail generates events for: policy gate, override, rollback, semantic validation
- [ ] Audit chain integrity check endpoint tested and monitored
- [ ] Override TTL mechanism tested; expired overrides correctly rejected
- [ ] Policy drift detection sweep runs and produces alerts on detected drift
- [ ] All registered providers have adapters; unregistered provider reference blocks CI build
- [ ] Adapter confidence calibration validated (ECE `&lt; 0.15` for each adapter type)
- [ ] Schema drift tests pass for all adapter outputs (structural + semantic validation)
- [ ] Fallback-plain path tested with confidence thresholds; low-confidence outputs logged
- [ ] Provider-specific error patterns documented and versioned in resilience module
- [ ] Alert ceiling configured (5/hr/operator) with dedup and correlation rules
- [ ] Alerting tested for: circuit breaker trips, fallback rate >10%, cost overage, hash chain breaks
- [ ] Continuity snapshots verified at shift boundaries; stale-owner watchdog armed
- [ ] Rollback tested for each critical lane (selective rollback, not all-or-nothing)
- [ ] Cost budget alerts configured at 80% and 95% thresholds
- [ ] Runbook reviewed and certified by platform/SRE and governance teams
- [ ] On-call rotation established with escalation SLA per risk tier
- [ ] Observability dashboards deployed and tested (latency, throughput, error rates by mode)
- [ ] Load test on critical lanes passes (maintain p95 latency within SLO under normal+burst)
- [ ] Canary deployment validated in low-criticality domain before stage 1 rollout
- [ ] Replay test suite passes (deterministic routing, no non-deterministic promotion)
- [ ] Manual intervention paths tested end-to-end (human-in-the-loop scenarios)
- [ ] Compliance evidence retention policies verified (GDPR/SOC2/SOX/PCI timelines)
- [ ] Security: no secrets in audit trails; all PII redacted in logs
- [ ] All technical debt items (TD-01 through TD-11) resolved and gate-signed
| Guardrail | Threshold | Action | SLA | Monitoring |
|-----------|-----------|--------|-----|-----------|
| Fallback rate | > 10% global (7-day window) | Alert + investigation trigger | 30 min investigation SLA | Hourly trend dashboard; alert on 2-std upward spike |
| Fallback rate per provider | > 30% per provider | Page on-call; provider rotation if sustained | 15 min response | Provider-specific fallback rate tracked independently |
| Circuit breaker OPEN state | Any critical provider CB open | Page on-call immediately | 5 min response; 30 min recovery SLA | Circuit state dashboard; per-provider health probes every 10s |
| Audit chain hash break | Any detected integrity failure | Critical alert + STOP all writes; incident response | Immediate escalation | Integrity check job runs every 5 min; cryptographic verification on read |
| Semantic validation failure | In critical lane | Reject action + escalate to human gate | 15 min escalation SLA | All semantic failures to audit trail; blocked in critical lanes by default |
| Stale ownership | > 4 hours | Watchdog escalation to next owner or incident lead | 30 min escalation SLA | Ownership timestamp checked every 30 min; alert at 3.5 hours |
| Policy evaluation latency | > 100ms p95 (last 100 runs) | Cache warm + investigate rule complexity | Latency SLA `&lt;100ms` p95 | Per-rule latency breakdown in metrics; slow-rule detection |
| DLQ depth | > 50 items | Alert + manual review queue | 4 hour manual review SLA | DLQ depth metrics; automatic escalation if >100 items |
| Cost per hour | > 120% of daily budget / 24 | Alert + throttle non-critical concurrency | Cost alert SLA `&lt;15 min` | Per-hour cost tracking; daily carryover rules |
| Cost per run (max) | > 50 USD (anti-runaway) | Terminate execution + escalate | Hard limit at 50 USD per run | Per-run cost tracking; budget enforcement at gate |
| Provider error rate | > 20% error rate (last 100 runs) | Page on-call; begin provider fallback | 10 min response SLA | Error rate per provider; alert on threshold breach |
| Mode deadlock | > 5 min timeout in multi-agent | Force resolution + alert | Timeout hard-enforced at 5 min | Mode completion time tracked; timeout count alerted daily |
| Rollback failure | Any rollback that fails | Incident response + manual intervention | 30 min response SLA | All rollback attempts logged; failure escalates immediately |
| Recovery exhaustion | > 3 failed recovery attempts | Human escalation to incident lead | 10 min escalation SLA | Recovery attempt count per run; escalation trigger at 3 |
| Confidence below threshold | `&lt; 0.3` calibrated confidence in critical lane | Block action + escalate | Blocking enforced at policy layer | Confidence distribution metrics; below-threshold rate tracked |
| Agent | WPs | Task | Key Files | Context |
|-------|-----|------|-----------|---------|
| 1A | WP-0001, WP-0002 | **Done**, then complete canonical event schemas (chunk, evidence, policy events as Pydantic models) | src/thegent/contracts/csm.py | FR-026, P-001, P-002 |
| 1B | WP-Y6 | Add OTel GenAI instrumentation (gen_ai.* spans on agent calls, tracing) | src/thegent/telemetry.py | NFR-013, P-080 |
| 1C | WP-0005 | Create program operating model doc (ownership map, RACI, escalation paths) | docs/enterprise/OPERATING_MODEL.md | — |
| 1D | WP-0003, WP-0004 | **Done**, verify execution baseline and risk/confidence scoring | src/thegent/execution.py, src/thegent/contracts/validation.py | FR-001, FR-023 |
| Agent | WPs | Task | Key Files | Context |
|-------|-----|------|-----------|---------|
| 2A | WP-X7 | Implement contract telemetry and drift detection (drift events, alert budgets, analyze_drift) | src/thegent/contracts/telemetry.py | NFR-010, P-019, ROB-006 |
| 2B | WP-X8 | Implement contract migration controller (dual-read/dual-write, canary, rollback logic) | src/thegent/contracts/migration.py | FR-031, P-010, R-005 |
| 2C | WP-X6 | Complete fallback reliability policy (wire FallbackStateMachine end-to-end, policy config loader) | src/thegent/contracts/state_machine.py | FR-030, P-018, ROB-010 |
| 2D | WP-X1..X5 | **Done**, verify registry + CSM + parser + semantic validation + conformance | src/thegent/contracts/registry.py, etc | FR-025..029 |
| Agent | WPs | Task | Key Files | Context |
|-------|-----|------|-----------|---------|
| 3A | WP-1001, WP-1002 | Build dependency-aware routing engine with priority/urgency lanes | NEW: src/thegent/orchestration/router.py, lanes.py | FR-001, FR-019, P-022, DAG-1 (A4-A8) |
| 3B | WP-1003, WP-1004 | Implement idempotent execution envelope with phase transition contracts (verify WP-1003 done) | src/thegent/execution.py, NEW: src/thegent/orchestration/phases.py | FR-002, FR-004, P-036, P-065 |
| 3C | WP-1005, WP-1008, WP-1009 | Evidence capture + replay-safe run history (WP-1008 done) + pause/resume MCP tools | src/thegent/execution.py; src/thegent/mcp_server.py; NEW: src/thegent/orchestration/evidence.py | FR-004, FR-022, FR-003 |
| 3D | WP-1006, WP-1007 | Conflict arbitration rules + child-task routing by capability | src/thegent/orchestration_modes.py, src/thegent/models/catalog.py | FR-032, FR-038, P-052 |
| Agent | WPs | Task | Key Files | Context |
|-------|-----|------|-----------|---------|
| 4A | WP-2001, WP-2003 | Checkpoint/rollback service + per-provider circuit breakers | NEW: src/thegent/orchestration/checkpoint.py; src/thegent/agents/resilience.py | FR-006, FR-007, P-034, P-038 |
| 4B | WP-2004, WP-2005 | Recovery playbook automation + MAST 14-mode failure taxonomy | NEW: src/thegent/orchestration/playbooks.py, failure_modes.py | FR-008, P-040, P-041 |
| 4C | WP-2002, WP-2007 | Retry strategy with adaptive backoff + evidence completeness linting | src/thegent/agents/resilience.py, src/thegent/contracts/validation.py | FR-007, FR-005, P-035 |
| 4D | WP-Y2, WP-Y3, WP-2008, WP-2006 | Dead-letter queue + chaos framework + oversight + regression probes | NEW: src/thegent/orchestration/dlq.py, oversight.py, probes.py; tests/chaos/ | FR-034, FR-035, FR-009, FR-005 |
| Agent | WPs | Task | Key Files | Context |
|-------|-----|------|-----------|---------|
| 5A | WP-3001, WP-3003 | Policy pre-check gate evaluator + override path with TTL and revalidation | NEW: src/thegent/governance/policy_engine.py, overrides.py | FR-003, FR-011, FR-033, P-066, P-075 |
| 5B | WP-3004, WP-3005 | Immutable audit trail (hash chain) + policy drift detection and sweep | NEW: src/thegent/governance/audit.py, drift.py | FR-012, FR-013, P-069, P-074 |
| 5C | WP-3002, WP-3007 | Signed action artifacts + trust boundary checks | NEW: src/thegent/governance/signatures.py, trust.py | FR-010, FR-014, P-076, P-077 |
| 5D | WP-3006, WP-3008 | Compliance evidence retention + escalation SLA and governance queue | NEW: src/thegent/governance/retention.py, escalation.py | FR-013, P-074, P-083 |
| Agent | WPs | Task | Key Files | Context |
|-------|-----|------|-----------|---------|
| 6A | WP-Y1 | Multi-agent mode runtime (sequential/parallel/review modes end-to-end) | src/thegent/orchestration_modes.py | FR-032, P-052..055 |
| 6B | WP-Y5 | Hierarchical prompt orchestration and context management | NEW: src/thegent/orchestration/prompts.py | FR-042, P-059, P-060 |
| 6C | WP-Y8-rel | Provider scoring with learning curves and model-based recommendation | src/thegent/models/catalog.py | FR-021, P-057, P-058 |
| Agent | WPs | Task | Key Files | Context |
|-------|-----|------|-----------|---------|
| 7A | WP-4001, WP-4002 | Operator cockpit summary + progressive disclosure tiers (concise/detailed) | NEW: src/thegent/ux/cockpit.py, explanations.py | FR-015, FR-039, P-090, P-092 |
| 7B | WP-4003, WP-4005 | Safe fallback UI options + stale-state prevention and refresh | NEW: src/thegent/ux/fallback_ui.py; src/thegent/execution.py | FR-016, FR-017, P-096 |
| 7C | WP-4006, WP-4007 | Continuity handoff summaries + decision replay and rationale snapshots | src/thegent/execution.py; NEW: src/thegent/ux/replay.py | FR-018, FR-022, P-099, P-111 |
| 7D | WP-4004, WP-4008 | Interruption taxonomy and fatigue controls + confidence calibration curves | NEW: src/thegent/ux/alerts.py, calibration.py | FR-023, FR-041, P-093, P-098 |
| Agent | WPs | Task | Key Files | Context |
|-------|-----|------|-----------|---------|
| 8A | WP-5001, WP-5002 | Adaptive concurrency controller + burst load classification and safe-mode | NEW: src/thegent/orchestration/concurrency.py, burst.py | FR-019, FR-037, P-026 |
| 8B | WP-5003, WP-Y4, WP-Y8 | Cost-aware routing + cost tracking service + provider scoring with learning | src/thegent/models/catalog.py; NEW: src/thegent/orchestration/cost.py | FR-036, NFR-016, P-025, P-057 |
| 8C | WP-5004, WP-5005, WP-5006 | Non-critical deferral rules + continuity watchdog + handoff integrity enforcement | NEW: src/thegent/orchestration/deferral.py; src/thegent/execution.py | FR-020, FR-021, FR-018 |
| 8D | WP-5007, WP-5008 | Recovery under sustained load drills + load-aware recommendation tuning | tests/; src/thegent/models/catalog.py | FR-005, P-027 |
| Agent | WPs | Task | Key Files | Context |
|-------|-----|------|-----------|---------|
| 9A | WP-6001 | End-to-end dress rehearsal (integration test suite across all DAGs and gates) | tests/ | All DAGs, all gates, all phases |
| 9B | WP-6002, WP-6003 | Security/compliance signoff docs + SLO certification and measurement | docs/enterprise/ | All NFRs, FR-001..042 |
| 9C | WP-6004, WP-6007 | Runbook finalization with playbook cross-references + post-launch observation and rollback reserve | docs/RUNBOOK.md, docs/ROLLBACK_RESERVE.md | WP-2004, OPS-008, OPS-011 |
| 9D | WP-6005 | KPI baselines and launch thresholds definition | docs/LAUNCH_THRESHOLDS.md | P-081, OPS-001, OPS-002 |
| Agent | WPs | Task | Key Files | Context |
|-------|-----|------|-----------|---------|
| 10A | WP-Y7 | TRAFFIC KPI dashboard implementation (real-time metrics, SLO tracking) | NEW: src/thegent/ux/kpis.py | P-081, OPS-001, OPS-002, OPS-003 |
| 10B | WP-6006, WP-6008 | Decommission/sunset plan + formal closure and successor roadmap | docs/enterprise/DECOMMISSION_PLAN.md, SUCCESSOR_ROADMAP.md | OPS-010, OPS-011 |
| 10C | WP-6005 | Verify KPI baselines match launch thresholds and SLO targets are calibrated | docs/ | P-081, OPS-001..003 |
- [ ] Code implements all behaviors from "What to Build" section
- [ ] All FRs in Requirements section traced to tests
- [ ] Test file exists and all N tests pass: pytest tests/test_unit_[module].py -v
- [ ] No lint errors: ruff check src/thegent/[module]/ --fix
- [ ] No type errors: mypy src/thegent/[module]/ --strict (or project default)
- [ ] No imports from prohibited layers (check boundaries per 06-IMPL.md)
- [ ] All docstrings follow format: """One-line summary. Extended details if needed."""
- [ ] Integration tests pass if applicable: pytest tests/test_integration_*.py -k [module]
| Item | Count |
|------|-------|
| Total WPs in WBS | 72 |
| WPs Marked DONE | 15 (0001, 0003, 0004, 0006, X1-X8, 2002, 1003, 1008) |
| WPs Marked PARTIAL | 6 (0002, 1001, 2001, 3001, 6002, 6004, 6007) |
| WPs Marked NOT DONE | 51 |
| **Total Assigned to Batches 1-10** | **57** (all NOT DONE + PARTIAL) |
| **Not Assigned** | 15 (all DONE — no new work required) |
| Agent | Task | Key Files | Context |
|-------|------|-----------|---------|
| MCP-5 | Auth (Bearer token), stateless mode, Redis backend, session state store, install docs | mcp_server.py, mcp_manage.py | FastMCP plan Phase 5 |
| Agent | Items | Task |
|-------|-------|------|
| OPT-A | OPT-004..006, OPT-009..012 | Performance tuning (connection pooling, lazy loading, compression) |
| OPT-B | ROB-011..014 | Robustness hardening (stale state, watchdog, config validation, fd limits) |
| OPT-C | UX-003..004, UX-009..012 | UX polish (descriptions, docs, persona defaults, alert fatigue) |
| OPT-D | DX-001..002, DX-006..010 | Developer experience (boundary enforcement, test generation, diffing) |
| OPT-E | OPS-007..011 | Operational excellence (cleanup, runbook, SLO, decommission, rollback reserve) |
| OPT-F | DE-004..008 | Design elegance (DI stack, state machines, middleware, adoption model) |
| Variant | Behavior | Stop condition |
|---------|----------|----------------|
| **Soft** | Can be overridden by human at any time; returns fixed prompt awaiting stop signal you define | Human stop, checker "kill", timeout, or explicit stop signal |
| **Hard** | Enforced until explicit stop; head LLM (checker) decides when to kill session | Checker "kill" decision only (or configurable override) |
| Input | Source | Purpose |
|-------|--------|---------|
| Governance report | PolicyEngine, escalation queue | Policy denials, overrides, evidence gaps |
| Initial todo spec | Planner / WBS | Original task breakdown |
| Phased WBS with statuses | DAG / execution | Progress, blocked tasks, completed |
| Final agent response | Worker agent | Condensed stream, summary, artifacts |
| Human input (if takeover) | Session takeover | Human-entered response when operator intervenes |
| Decision | Meaning | Next action |
|----------|---------|-------------|
| **Re-prompt** | Worker needs different instruction | Route to preset or LLM-generated prompt |
| **Continue** | Worker should keep going | Feed next preset or same fixed prompt |
| **Kill session** | Terminate this session | Stop loop; emit final state; optional handoff |
| Component | Requirement |
|-----------|-------------|
| Dashboard | Real-time session state, condensed stream, input field for takeover |
| Governance report | Visible to checker (and human when takeover) |
| WBS status | Phased view with completion %, blocked items |
| Agent response | Condensed stream; full trace on demand |
| Checker context | Same view for auto-checker and human-in-place |
- [ ] Preset catalog (YAML/JSON)
- [ ] Keyword matching → preset ID
- [ ] Fixed prompt loop with stop signal
- [ ] CLI: `thegent loop --preset write_tests --stop-signal STOP`
- [ ] Checker agent invocation (codex headless gemini flash)
- [ ] Input assembly: governance, WBS, response
- [ ] Decision parsing: re_prompt | continue | kill
- [ ] Wire checker into loop controller
- [ ] When preset router returns no match → call LLM
- [ ] LLM generates re-prompt from context
- [ ] Optional: cache by state hash
- [ ] Dashboard input field for human response
- [ ] Inject human input as checker output
- [ ] Observability: same context for human and checker
- [ ] Session takeover flag in state
- [ ] Config: `loop_mode: soft | hard`
- [ ] Soft: human stop, checker kill, timeout
- [ ] Hard: checker kill only (or configurable override)
| Source (thegent) | Destination |
|------------------|-------------|
| `skills/*` | `~/.claude/skills/` |
| `hooks/*` | `~/.claude/hooks/` |
| `templates/*` | `~/.claude/templates/` |
| `CLAUDE.md` (root) | `~/.claude/CLAUDE.md` |
| `mcp_servers.json` | `~/.claude/mcp_servers.json` |
| `qa-config.json` | `~/.claude/qa-config.json` |
| `agents/*` | `~/.claude/agents/` |
| `commands/*` | `~/.claude/commands/` |
| `contracts/*` | `~/.claude/contracts/` |
| `.claude/plugins/*` | `~/.claude/plugins/` |
| `.factory/hooks/*` | `~/.factory/hooks/` |
| `.factory/skills/*` | `~/.factory/skills/` |
| `.factory/commands/*` | `~/.factory/commands/` |
| `.factory/droids/*` | `~/.factory/droids/` |
| `.factory/plugins/*` | `~/.factory/plugins/` |
| `.factory/mcp.json` | `~/.factory/mcp.json` |
| `.factory/config.json` | `~/.factory/config.json` |
| `.factory/settings.json` | `~/.factory/settings.json` |
| Mode | Behavior |
|------|----------|
| default (smart) | Keep user version, backup source to `~/.claude/.thegent-backup/{timestamp}/` |
| `--editable` | Symlink (overwrites existing) |
| `--force` | Overwrite with source |
| `--interactive` | Show diff, ask per-file (future enhancement) |
| File | Action |
|------|--------|
| `src/thegent/install.py` | Create - core install logic |
| `src/thegent/cli.py` | Modify - add install subcommand |
| `tests/test_install.py` | Create - unit tests |
| Principle | Meaning | Application to Lifecycle/Checker |
|-----------|---------|----------------------------------|
| **Progressive disclosure** | Show summary first; expand on demand (ADR-008, ADR-014) | Takeover: Tier 1 (summary) → Tier 2 (WBS, governance) → Tier 3 (full trace) |
| **Single mental model** | One concept, one name, one behavior | `loop_mode` unified across AgilePlus, LifecycleController, agent_deployer |
| **Discoverable** | Operators find features without docs | CLI `thegent loop --help` shows `--loop-mode soft\|hard`; MCP tools self-describe |
| **Predictable** | Same input → same behavior (when deterministic) | Preset match → deterministic prompt; no match → checker (LLM) |
| **Reversible** | Human can undo or override | Soft mode: STOP; takeover: human injects; audit: trace replay |
| **Consistent surfaces** | Same data, same schema, across CLI/MCP/dashboard | Checker context schema reused in takeover, audit, trace replay |
| Principle | Meaning | Application |
|-----------|---------|-------------|
| **End-to-end** | Design for full flow, not isolated steps | Preset → Checker → Worker → Audit → Replay; no orphan states |
| **Failure-aware** | Every path has a defined failure mode (MAST 14-mode) | Checker timeout → CONTINUE or escalate; preset load fail → built-in fallback |
| **Observable** | Every decision point emits structured events | Checker decision → OTel span; takeover → audit event; preset match → log |
| **Recoverable** | State can be resumed or replayed | Checkpoint before checker; trace replay; takeover context persisted |
| **Boundary-respecting** | No layer violations (tach, ADRs) | Checker in agents/; governance report from governance/; no circular deps |
| **Cost-conscious** | Checker uses cheap model; presets avoid LLM when possible | Default gemini flash; preset-first routing minimizes checker calls |
| Feature | Integration Point | Harmony Rule |
|---------|-------------------|--------------|
| **Progressive Disclosure (ADR-008)** | Takeover UX | Tier 1: "Checker decided X. Take over?" → Tier 2: governance + WBS → Tier 3: full trace |
| **4-Pane Cockpit (P-090)** | Stream + Details panes | Stream: condensed worker output; Details: checker context when takeover active |
| **Sitback widgets** | `register_widget` | Lifecycle widget: session state, checker context, takeover input; same schema as MCP |
| **HITL patterns (HAC)** | Supervisory Loop, HaaT | Lifecycle takeover = Supervisory Loop; checker RE_PROMPT can trigger HaaT `ask_human` |
| **Autonomy Gradient** | Cockpit dial | Soft loop = respects human override; Hard loop = checker-only (Guarded/Manual autonomy) |
| **Cost-aware routing (WP-5003)** | Checker model selection | `checker_agent` participates in cost_quality policy; checker calls counted in budget |
| **Governance / PolicyEngine** | Checker inputs | Governance report flows from PolicyEngine; checker KILL on policy denial |
| **Audit trail (ADR-005, ADR-012)** | Takeover, checker decisions | Every checker decision + takeover event → hash-chained audit |
| **Trace replay** | Checker context persistence | Replay uses same CheckerContext schema; enables "what checker saw" replay |
| **Handoff packet (P-006)** | Session handoff | Takeover context = handoff packet subset; enables operator-to-operator handoff |
| **Work stream** | Task claiming | Loop session linked to WORK_STREAM item; completion updates CLAIMED→COMPLETED |
| **Circuit breaker** | Checker provider | Checker uses resilience layer; circuit open → fallback or CONTINUE |
| Area | Status | Location |
|------|--------|----------|
| **Lifecycle loop** | ✓ | `agents/loop_controller.py` — `LifecycleController`, `run_loop()` |
| **Preset-first routing** | ✓ | `match_preset(combined)` before checker; skip checker when match |
| **Checker agent** | ✓ | `agents/checker.py` — `CheckerAgent.decide()` |
| **Soft mode** | ✓ | `LoopMode.SOFT` — STOP signal in output stops loop |
| **Human takeover** | ✓ | `loop-send`, `takeover`, `thegent_loop_takeover` (MCP) |
| **Preset catalog** | ✓ | `agents/presets.py` — write_tests, write_docs, add_polish, continue |
| **Cost-aware routing** | ✓ | WP-5003 done — cost_quality policy, budget shaping |
| **Config check** | ✓ | `thegent config check` |
| **Route probe** | ✓ | `thegent route-probe` |
| Gap | Design | Current | Effort |
|-----|--------|---------|--------|
| **Hard loop mode** | Checker kill only; no human override | Only SOFT implemented | Small |
| **Checker model** | Codex headless gemini flash | `antigravity` (default) | Small |
| **Preset catalog** | YAML/JSON config | Hardcoded in `presets.py` | Medium |
| **Human sees checker context** | Same view for human and checker | Unclear — takeover UX may not show governance/WBS/response | Medium |
| **LLM fallback** | When no preset match → LLM | ✓ Checker is LLM fallback; flow correct | — |
| **Doc naming** | 12-RALPH-WIGGUM in index | File is `12-LIFECYCLE-LOOP-DESIGN.md` | Trivial |
| ID | Item | Priority | Effort | Impact |
|----|------|----------|--------|--------|
| **WP-5005** | Continuity watchdog (heartbeat 30s, session resumption) | P1 | 6–10 calls | Long-running reliability |
| **QW-008** | OTel span attributes (resolved provider/model post-route) | P2 | 1–2 calls | Observability |
| **ROB-001** | Sloppy XML recovery for unclosed tags | P0 | 3 calls | 90%+ malformed output |
| **run-diff** | `thegent run-diff &lt;a> &lt;b>` — compare execution traces | P3 | Medium | Debugging |
| **trace replay** | `thegent trace replay ```<run_id>```` | P3 | Medium | Reproducibility |
| **WP-5006** | Handoff integrity (snapshot validation, ownership transfer) | P2 | 6–10 calls | Multi-agent handoff |
| ID | Item | Priority | Effort | Impact |
|----|------|----------|--------|--------|
| **Hard mode** | `loop_mode: hard` — checker kill only | P2 | Small | Compliance/audit scenarios |
| **Checker model config** | `checker_agent` in config (gemini flash vs antigravity) | P2 | Small | Cost/latency tuning |
| **Preset catalog YAML** | Move presets to config/plugin | P3 | Medium | Extensibility |
| **Human takeover context** | Dashboard shows governance, WBS, response before human input | P1 | Medium | HITL quality |
| Component | Requirement | Status |
|-----------|-------------|--------|
| Dashboard | Real-time session state, condensed stream, input field for takeover | Partial |
| Governance report | Visible to checker (and human when takeover) | Checker yes; human unclear |
| WBS status | Phased view with completion %, blocked items | Partial |
| Checker context | Same view for auto-checker and human-in-place | Gap |
| Question | Decision |
|----------|----------|
| **Soft vs hard default** | Checker-only kill (hard mode) |
| **Checker model** | Default gemini flash; configurable via `checker_agent` |
| **Preset catalog** | Move to YAML/plugin |
| **Stop signal** | Also support env var + MCP tool (in addition to STOP in output) |
| **Human takeover UX** | Full context (governance, WBS, response) before human input |
| **Takeover surface** | All: Composer inline, Sitback dashboard, MCP tool |
| **Checker context persistence** | Persist for audit/replay |
| **Trace replay** | Important |
| **Doc naming** | Keep lifecycle/cycleloop (not RALPH-WIGGUM) |
| **AgilePlus vs Lifecycle** | Unify `loop_mode` concept |
| Decision | Implementation | Acceptance Criteria |
|----------|----------------|---------------------|
| **Checker-only kill (hard)** | Add `LoopMode.HARD`; in hard mode, ignore STOP in output; only checker KILL stops | `--loop-mode hard` ignores STOP; only checker KILL terminates |
| **Default gemini flash, configurable** | Config `checker_agent: gemini-flash` (default); `CheckerAgent(agent_name=settings.checker_agent)` | `thegent config check` validates checker_agent; fallback if runner missing |
| **Preset catalog → YAML/plugin** | `presets.yaml` or plugin dir; loader in `presets.py`; fallback to built-in | Load from `~/.thegent/presets.yaml` or `./presets.yaml`; built-in if missing |
| **Stop signal: env var + MCP** | `THGENT_LOOP_STOP=1`; MCP tool `thegent_loop_stop &lt;session_id>` | Env checked each iteration; MCP writes stop flag; both work in soft mode |
| **Full UX for takeover** | MCP/CLI return checker context (governance, WBS, response) before human input | `thegent_loop_takeover` returns `CheckerContext`; human sees before prompt |
| **All takeover surfaces** | Composer inline, Sitback widget, MCP `thegent_loop_takeover` — all show full context | Same `CheckerContext` schema in all three; Sitback widget uses `register_widget` |
| **Persist for audit** | Write checker context to `takeover.json` or audit ledger on takeover | Append to audit trail; hash-chained; queryable for replay |
| **Trace replay** | Prioritize `thegent trace replay ``&lt;run_id>``` in roadmap | Replay consumes persisted checker context; WP in Phase 4 |
| **Unify loop_mode** | Shared `loop_mode` enum/config between `AgilePlusLoop` and `LifecycleController` | Single `LoopMode` in `agents/loop_controller.py`; AgilePlus imports it |
| Area | Addition | Rationale |
|------|----------|-----------|
| **Checker timeout** | 30s timeout; on timeout → CONTINUE (conservative) or configurable | Prevents loop stall on checker provider failure |
| **Preset load failure** | If YAML/plugin load fails → use built-in catalog; log warning | Never block loop start |
| **Stop signal race** | Env + MCP both write to same atomic flag file | Avoid split-brain; single source of truth |
| **Takeover idempotency** | If human sends while checker running → queue or reject with clear message | Prevents duplicate injection |
| **Circuit breaker** | Checker uses `get_runner` → resilience layer; circuit open → CONTINUE | Aligns with P-034, ADR-006 |
| **Audit schema** | CheckerContext + event_type (checker_decision | human_takeover | loop_stop) | Enables forensic replay |
| Integration | Action |
|-------------|--------|
| **Progressive disclosure** | `thegent_loop_takeover` returns `CheckerContext`; UI tiers: summary → detail → trace |
| **4-pane cockpit** | Stream pane: worker output; Details pane: CheckerContext when takeover active |
| **Sitback** | `register_widget("lifecycle", fn)` → CheckerContext + takeover input; same schema |
| **Cost routing** | Add checker calls to budget; `checker_agent` in cost_quality policy |
| **Audit** | Emit `CheckerContext` on every checker decision + takeover; hash chain |
| **Trace replay** | Replay deserializes `CheckerContext` from audit; show "what checker saw" |
| **Unify loop_mode** | `AgilePlusLoop(lifecycle_mode=...)` → `LoopMode(...)`; `agent_deployer` same |
| Item | Depends On | Blocks |
|------|------------|--------|
| CheckerContext schema | — | Takeover UX, audit, replay, Sitback |
| Hard mode | — | Compliance workflows |
| Unify loop_mode | LoopMode.HARD exists | AgilePlus, agent_deployer refactor |
| Preset YAML | — | Operator customization |
| Stop signal (env+MCP) | Session ID in loop state | Soft-mode stop from external process |
| Full takeover UX | CheckerContext schema | Sitback widget, audit |
| Persist for audit | Audit trail (ADR-012) | Trace replay |
| Trace replay | Persisted CheckerContext, audit | Phase 4 WP |
| Scenario | Handling |
|----------|----------|
| Checker provider down | Circuit breaker → CONTINUE or escalate; never block loop |
| Preset YAML malformed | Fallback to built-in; log error; continue |
| Human takeover during checker call | Queue human input; apply after checker returns; or reject with "wait" |
| STOP file + env + MCP all set | Any one triggers stop (soft mode); idempotent |
| Hard mode + human wants to stop | Human must use escalation (WP-4009); not direct stop |
| Checker returns invalid JSON | Retry once; then CONTINUE; log |
| Session dies mid-loop | Continuity watchdog (WP-5005) detects; handoff packet for resume |
| Doc | Purpose |
|-----|---------|
| [TOOLING_AND_OPTIMIZATION_AUDIT](../reference/TOOLING_AND_OPTIMIZATION_AUDIT.md) | Quick wins, WP-5005, ROB-001 |
| [12-LIFECYCLE-LOOP-DESIGN](./12-LIFECYCLE-LOOP-DESIGN.md) | Cycleloop/checker design (source) |
| [HAC_AND_HITL_PATTERNS](../reference/HAC_AND_HITL_PATTERNS.md) | Supervisory Loop, HaaT, autonomy |
| [SITBACK_PLUGINS](../guides/SITBACK_PLUGINS.md) | Widget API for lifecycle dashboard |
| [PHASE_4_COCKPIT_UX_DEPTH](../reference/PHASE_4_COCKPIT_UX_DEPTH.md) | 4-pane layout, progressive disclosure |
| [05-ARCHITECTURE](../plans/05-ARCHITECTURE.md) | ADRs, patterns, module boundaries |
| [02-UNIFIED-WBS](./02-UNIFIED-WBS.md) | WP-5005, 5006, Phase 4 UX |
| Option | Mechanism | Pros | Cons |
|--------|-----------|------|------|
| **A. Stdin pipe** | `(echo "Run thegent cockpit..."; cat) \| claude` | No user action | Claude Code may not read stdin for first message |
| **B. Pty + expect** | Spawn, wait for prompt, send keys | Works if prompt detectable | Fragile, platform-dependent |
| **C. User paste** | Print startup prompt; user pastes | Simple, reliable | Extra step |
| **D. Skill-only** | Skill says "on start, run dashboard" | No injection needed | Agent may idle until user speaks |
| Tool | Purpose |
|------|---------|
| thegent_run | Run one-off tasks |
| thegent_bg | Start background runs |
| thegent_ps | List sessions |
| thegent_terminal_list | List tmux panes |
| thegent_terminal_inspect | View pane content |
| thegent_terminal_send | Send to pane |
| thegent_terminal_attach | Attach instructions |
| thegent_ddg_search | Web research |
| thegent_cockpit | (CLI) Dashboard |
| Aspect | Skill + CLI | FastMCP |
|--------|-------------|---------|
| **Discoverability** | Implicit (read skill doc) | Explicit (list_tools, list_resources, list_prompts) |
| **Typed interface** | String args, manual parsing | Schema-driven, validated |
| **Single-call dashboard** | 3 CLI commands (cockpit, terminal list, ps) | 1 tool: `thegent_sitback_dashboard` |
| **URI-addressable** | N/A | `thegent://sitback/dashboard`, `thegent://sessions` |
| **Structured output** | Rich text, parse manually | `ToolResult.structured_content` |
| **Prompt templates** | Inline in skill | `get_prompt("thegent_sitback_startup")` |
| Component | Type | Purpose |
|-----------|------|---------|
| `thegent://sitback/dashboard` | Resource | Unified dashboard JSON (sessions + cockpit + terminals) |
| `thegent_sitback_dashboard` | Tool | Same as resource; for tool-only clients |
| `thegent_sitback_startup` | Prompt | Startup protocol template |
| `thegent_sitback_spawn_sibling` | Prompt | Spawn sibling session (agent param) |
| Category | Tools |
|----------|-------|
| **Dashboard** | thegent_sitback_dashboard |
| **Execution** | thegent_run, thegent_bg |
| **Sessions** | thegent_ps, thegent_status, thegent_logs, thegent_stop, thegent_wait |
| **Terminals** | thegent_terminal_list, thegent_terminal_inspect, thegent_terminal_send, thegent_terminal_attach |
| **Governance** | thegent_observe_summary, thegent_session_contract_health_gate, thegent_session_contract_health_report, thegent_session_contract_health_trend |
| **Catalog** | thegent_list_agents, thegent_list_droids, thegent_list_models, thegent_resolve_model_route |
| **Planning** | thegent_dag_list |
| **Research** | thegent_ddg_search |
| **Prompts** | thegent_run_agent, thegent_bg_task, thegent_create_wbs, thegent_sitback_startup, thegent_sitback_spawn_sibling |
| File | Change |
|------|--------|
| `src/thegent/main.py` | Register `sitback` command |
| `src/thegent/clode_main.py` | Add `sitback_cmd()` |
| `skills/sitback-agent/SKILL.md` | Startup protocol, FastMCP-first |
| `skills/sitback-agent/skill.json` | Metadata |
| `src/thegent/install.py` | Add sitback-agent to sync map |
| `src/thegent/cli_impl.py` | Add `sitback_dashboard_impl()` |
| `src/thegent/mcp_sitback.py` | **New:** resource, tool, prompts; `register_sitback(mcp)` |
| `src/thegent/mcp_server.py` | Call `register_sitback(mcp)` |
| `docs/plans/2026-02-15-thegent-sitback-design.md` | This plan |
- [ ] `thegent sitback` starts Claude Code with minimax (or --agent)
- [ ] Sitback agent presents cockpit + terminal list + ps on startup (or after paste)
- [ ] `thegent sitback --agent kilo` spawns sibling with same protocol
- [ ] Skill is discoverable and overridable via --skill
- [ ] MCP tools work from within sitback session
- [ ] Dashboard view is intuitive and maintainable
- [ ] Extensibility path clear for future skills/plugins
| Risk | Mitigation |
|------|-------------|
| Claude Code ignores stdin | Fallback: print "Paste to start" + startup text |
| Skill not loaded | Install ensures symlink; document manual install |
| MCP not running | Check in sitback_cmd; print actionable message |
| Provider unavailable | Same as clode: fail with clear error |
| Plugin | Method | Endpoint/Command |
|--------|--------|------------------|
| heliosShield | Subprocess | `harness status`, `harness metrics`, etc. |
| thegent | HTTP REST | `http://127.0.0.1:3847/api/v1/*` |
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/projects` | GET | List all projects |
| `/api/v1/projects` | POST | Create project |
| `/api/v1/projects/{id}` | GET | Get project details |
| `/api/v1/projects/{id}` | PUT | Update project |
| `/api/v1/projects/{id}` | DELETE | Delete project |
| `/api/v1/agents` | GET | List all agents |
| `/api/v1/agents/{id}` | GET | Get agent details |
| `/api/v1/agents/{id}` | PUT | Update agent |
| `/api/v1/runs` | GET | List runs (with filters) |
| `/api/v1/runs/{id}` | GET | Get run details |
| `/api/v1/gardener/status` | GET | Get gardener status |
| `/api/v1/gardener/start` | POST | Start gardener |
| `/api/v1/gardener/stop` | POST | Stop gardener |
| `/api/v1/gardener/scan` | POST | Trigger scan |
| `/api/v1/gardener/config` | GET/PUT | Gardener config |
| `/api/v1/costs/daily` | GET | Daily cost summary |
| `/api/v1/costs/monthly` | GET | Monthly cost summary |
| `/api/v1/costs/alerts` | GET/POST | Cost alerts |
| `/api/v1/gamification/stats` | GET | XP, level, stats |
| `/api/v1/gamification/achievements` | GET | Achievement list |
| Issue | Location | Note |
|-------|----------|------|
| **Checker agent hardcoded** | `agent_deployer.py:98` | `checker_agent_name="antigravity"` — should be configurable or derived from task/cost tier |
| **Session ID typo** | `loop_controller.py:56` | `logging.time.time()` → `time.time()` |
| **record_call dimension** | `agent_deployer.py:167` | Always `"claude"` — should use actual agent (e.g. `agent` or `task.dimension`) |
| Task | Description | Files |
|------|-------------|-------|
| 1 | AgentDeployer uses LifecycleController | agent_deployer.py, test |
| 2 | SOFT/HARD mode selection | agileplus.py, triggers.py |
| 3 | Verification callback | loop_controller.py, verification_gate.py |
| 4 | Sitback never-idle update | mcp_sitback.py |
| 5 | Health-threshold trigger | triggers.py |
| 6 | Integration test | test_integration_*.py |
| Feature | LiteLLM Support | Current State | Priority |
|---------|-----------------|---------------|----------|
| **Caching** | Redis, in-memory, caching groups | ❌ Not implemented | P0 |
| **Streaming** | Stream=True, async streaming | ❌ Not implemented | P0 |
| **Fallback/Cooldowns** | cooldown_time, fallbacks | ❌ Not implemented | P0 |
| **Cost Tracking** | cost per request, budget tracking | ❌ Not implemented | P1 |
| **Latency-based routing** | latency-based routing | ❌ Not implemented | P1 |
| **Traffic Mirroring** | traffic mirroring for testing | ❌ Not implemented | P2 |
| **Alerting** | Slack, webhook, email | ❌ Not implemented | P2 |
| **Context Window** | Pre-call validation | ❌ Not implemented | P1 |
| **Usage-based routing** | Redis-backed usage tracking | ❌ Not implemented | P2 |
| **Model Aliasing** | model_alias support | ⚠️ Partial | P1 |
| **Custom routing** | Custom routing function | ❌ Not implemented | P2 |
| Component | Integration Point | Status |
|-----------|-------------------|--------|
| **Queue** | Router reads model preference from queue metadata | ❌ TODO |
| **Harvest** | LiteLLM cost/latency data harvested on Stop | ❌ TODO |
| **MCP Tools** | `thegent_routing_*` tools for routing control | ❌ TODO |
| **Agent Teams** | Router shared across teammates | ⚠️ Partial |
| **TUI** | Routing dashboard in sitback | ❌ TODO |
- [ ] Caching enabled (Redis or in-memory)
- [ ] Streaming responses working
- [ ] Fallback chains configured with cooldowns
- [ ] Cost tracking with daily budget alerts
- [ ] Latency-based routing operational
- [ ] Context window validation before calls
- [ ] Alerting integration for budget/errors
- [ ] Donut Architecture integration:
- [ ] Queue preference reading
- [ ] Harvest on stop
- [ ] MCP tools for routing control
- [ ] Team router config sharing
| File | Change | Why |
|------|--------|-----|
| `pyproject.toml` | Add `litellm` dependency | Core routing library |
| `src/thegent/routing/litellm_router.py` | NEW: LiteLLM Router wrapper | Encapsulate LiteLLM configuration |
| `src/thegent/agents/codex_proxy.py` | Consume `resolved_provider`/`resolved_model_alias` | Wire routing to execution |
| `src/thegent/models/catalog.py` | Add LiteLLM model_list generation | Dynamic config from catalog |
| `src/thegent/config.py` | Add LiteLLM config settings | API keys, routing policy |
| Provider | Env Var | Model IDs |
|----------|---------|-----------|
| minimax | `MINIMAX_API_KEY` | minimax-m2.5 |
| nim | `NVIDIA_API_KEY` | deepseek-v3.2, glm-5, llama-nemotron-ultra |
| glm | `ZHIPU_API_KEY` | glm-5 |
| kilo | `KILO_API_KEY` | deepseek-v3.2, kimi-k2.5, qwen3-coder |
| Tier | Role | Storage | thegent Integration |
|------|------|---------|---------------------|
| **L1** | Working | Context Window | Managed by Orchestrator |
| **L2** | Short-term | Redis / local JSONL | Context management service |
| **L3** | Long-term | **Supermemory (Graph)** | **Persistent knowledge, past decisions** |
| **L4** | Archival | **Supermemory (Documents)**| **Immutable audit logs, historical specs** |
- [ ] Implement `thegent login supermemory` using API key (`sm_...`) or OAuth.
- [ ] Configure `x-sm-project` header to scope memories to specific `thegent` projects.
- [ ] Implement `SupermemoryProvider` in `src/thegent/orchestration/context.py`.
- [ ] Map `generate_continuity_packet` to Supermemory's "Conversations" API.
- [ ] Map `MAIFArtifact` persistence to Supermemory's "Documents" API.
- [ ] Use Supermemory's Knowledge Graph to track relationships between agents in a swarm.
- [ ] Implement semantic search for past decisions during the **eXplore** phase of 4X.
| Bundle | Component | Optimization Strategy |
|--------|-----------|-----------------------|
| **A: Runtime Foundation** | Platform detection, path resolution, repo-dependency removal | Parallel execution across 3 OS-specific subagents. |
| **B: Distribution & CI** | PyPI, Homebrew, Winget, Nix, CI/CD pipelines | Template-driven configuration; automated wheel/shim builds. |
| **C: Quality & UX** | Error handling, progress indicators, security audit | Standardized remediation hint framework; OPA policy updates. |
| **D: Knowledge** | Docs, tests, migration guides | Auto-generation from research docs using the "Extension Summary" metadata. |
| Track | Lead | Day 1 | Day 2 | Day 3 |
|-------|------|-------|-------|-------|
| **Rust Client** | — | P1.1.1-3 | P1.1.4-6 | Integration |
| **Python Cache** | — | P1.2.1-2 | P1.2.3-5 | Integration |
| **Config/CLI** | — | — | P1.3.1 | P1.3.2-5 |
| impl-supermemory-p1.1 | Supermemory Client (Rust SDK) | WP-5001-SM | P1 | — |
| impl-supermemory-p1.2 | L1/L2 Cache Infrastructure (Python) | WP-5001-SM | P1 | impl-supermemory-p1.1 |
| impl-supermemory-p1.3 | Config & Setup | WP-5001-SM | P1 | impl-supermemory-p1.2 |
| Package | Needed For | Current Status |
|---------|-----------|-----------------|
| `tenacity` | Retry logic (P1.1.3) | Present in pyproject.toml |
| `reqwest` | HTTP client (P1.1.1) | Will add to Cargo.toml |
| `tokio` | Async runtime (P1.1.1) | Will add to Cargo.toml |
| `redis-rs` | Redis client (P1.2.2) | Will add to Cargo.toml |
| `serde` | Serialization (P1.1.1) | Will add to Cargo.toml |
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Supermemory API changes | High | Review current docs before P1.1.4 |
| Auth complexity (OAuth) | Medium | Start with API key; OAuth is optional |
| Redis unavailability | Low | FileCache fallback is always available |
| Rust ecosystem churn | Low | Pin specific versions in Cargo.lock |
| Python cache perf | Medium | Benchmark early (P1.2.5), optimize if needed |
- [ ] Move this plan to docs/plans/
- [ ] Add work items to WORK_STREAM.md
- [ ] Create task breakdown in Taskfile.yml
- [ ] End session — ready for agent dispatch
- [ ] Complete planning
- [ ] Scaffold Rust project
- [ ] Create Python cache interface
- [ ] Start documentation outline
- [ ] Claim work items in WORK_STREAM
- [ ] End session — agents can start immediately
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P1.1.1 | Install wasmtime Python bindings | 30 min | None |
| P1.1.2 | Create `WasmSandbox` class (extend existing stub) | 4 hours | P1.1.1 |
| P1.1.3 | Implement WASI capability system | 6 hours | P1.1.2 |
| P1.1.4 | Add filesystem capability grants | 4 hours | P1.1.3 |
| P1.1.5 | Add network capability grants | 3 hours | P1.1.3 |
| P1.1.6 | Implement memory limits | 2 hours | P1.1.2 |
| P1.1.7 | Add timeout handling | 2 hours | P1.1.2 |
| P1.1.8 | Write unit tests for WASM sandbox | 4 hours | P1.1.7 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P1.2.1 | Create `.sandbox/wasm/` directory structure | 1 hour | None |
| P1.2.2 | Implement WASM module cache | 3 hours | P1.2.1 |
| P1.2.3 | Add WASM runtime state persistence | 2 hours | P1.2.1 |
| P1.2.4 | Create WASM environment manager | 4 hours | P1.2.2, P1.2.3 |
| P1.2.5 | Add cleanup logic for WASM cache | 2 hours | P1.2.4 |
| P1.2.6 | Write tests for environment management | 3 hours | P1.2.5 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P1.3.1 | Create `SandboxRouter` class | 3 hours | None |
| P1.3.2 | Implement tier selection logic | 4 hours | P1.3.1 |
| P1.3.3 | Add availability checking | 2 hours | P1.3.2 |
| P1.3.4 | Implement fallback logic | 3 hours | P1.3.3 |
| P1.3.5 | Add configuration loading | 2 hours | P1.3.1 |
| P1.3.6 | Write router tests | 3 hours | P1.3.4 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P2.1.1 | Install Podman (documentation) | 1 hour | None |
| P2.1.2 | Create `PodmanSandbox` class | 4 hours | P2.1.1 |
| P2.1.3 | Implement container execution | 4 hours | P2.1.2 |
| P2.1.4 | Add volume mounting | 3 hours | P2.1.3 |
| P2.1.5 | Add resource limits (memory, CPU) | 2 hours | P2.1.3 |
| P2.1.6 | Add network isolation | 2 hours | P2.1.3 |
| P2.1.7 | Implement rootless mode support | 3 hours | P2.1.2 |
| P2.1.8 | Write Podman tests | 4 hours | P2.1.7 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P2.2.1 | Create `.sandbox/container/` structure | 1 hour | None |
| P2.2.2 | Implement image pulling/caching | 4 hours | P2.2.1 |
| P2.2.3 | Add custom image building | 3 hours | P2.2.2 |
| P2.2.4 | Implement image cleanup | 2 hours | P2.2.2 |
| P2.2.5 | Add image versioning | 2 hours | P2.2.3 |
| P2.2.6 | Write image management tests | 3 hours | P2.2.5 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P2.3.1 | Install containerd | 1 hour | None |
| P2.3.2 | Create `ContainerdSandbox` class | 4 hours | P2.3.1 |
| P2.3.3 | Implement containerd execution | 4 hours | P2.3.2 |
| P2.3.4 | Add router support for containerd | 2 hours | P2.3.3 |
| P2.3.5 | Write containerd tests | 3 hours | P2.3.4 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P2.4.1 | Install gVisor | 1 hour | None |
| P2.4.2 | Create `GVisorSandbox` class | 4 hours | P2.4.1 |
| P2.4.3 | Implement gVisor execution | 4 hours | P2.4.2 |
| P2.4.4 | Add router support for gVisor | 2 hours | P2.4.3 |
| P2.4.5 | Write gVisor tests | 3 hours | P2.4.4 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P3.1.1 | Install QEMU/KVM (documentation) | 1 hour | None |
| P3.1.2 | Create `QemuSandbox` class | 5 hours | P3.1.1 |
| P3.1.3 | Implement VM image creation | 4 hours | P3.1.2 |
| P3.1.4 | Add VM execution via SSH/console | 6 hours | P3.1.3 |
| P3.1.5 | Implement 9p filesystem mounting | 4 hours | P3.1.4 |
| P3.1.6 | Add VM resource limits | 2 hours | P3.1.2 |
| P3.1.7 | Add VM snapshot support | 4 hours | P3.1.3 |
| P3.1.8 | Write QEMU tests | 4 hours | P3.1.7 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P3.2.1 | Enable Hyper-V (documentation) | 1 hour | None |
| P3.2.2 | Create `HyperVSandbox` class | 5 hours | P3.2.1 |
| P3.2.3 | Implement VM creation | 4 hours | P3.2.2 |
| P3.2.4 | Add PowerShell Direct execution | 4 hours | P3.2.3 |
| P3.2.5 | Add VM resource limits | 2 hours | P3.2.2 |
| P3.2.6 | Write Hyper-V tests | 3 hours | P3.2.5 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P3.3.1 | Create `.sandbox/vm/` structure | 1 hour | None |
| P3.3.2 | Implement VM image creation | 3 hours | P3.3.1 |
| P3.3.3 | Add VM image caching | 2 hours | P3.3.2 |
| P3.3.4 | Implement snapshot management | 3 hours | P3.3.2 |
| P3.3.5 | Add VM cleanup | 2 hours | P3.3.4 |
| P3.3.6 | Write VM management tests | 3 hours | P3.3.5 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P4.1.1 | Create `NativeSandbox` class | 3 hours | None |
| P4.1.2 | Implement environment filtering | 4 hours | P4.1.1 |
| P4.1.3 | Add CWD restrictions | 2 hours | P4.1.2 |
| P4.1.4 | Implement PATH filtering | 2 hours | P4.1.2 |
| P4.1.5 | Add warning logging | 1 hour | P4.1.1 |
| P4.1.6 | Write native sandbox tests | 3 hours | P4.1.5 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P4.2.1 | Update router fallback logic | 3 hours | P4.1.1 |
| P4.2.2 | Add fallback condition detection | 3 hours | P4.2.1 |
| P4.2.3 | Implement graceful degradation | 3 hours | P4.2.2 |
| P4.2.4 | Add fallback metrics/logging | 2 hours | P4.2.3 |
| P4.2.5 | Write fallback tests | 3 hours | P4.2.4 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P5.1.1 | Benchmark WASM performance | 3 hours | Phase 1 |
| P5.1.2 | Benchmark container performance | 3 hours | Phase 2 |
| P5.1.3 | Benchmark VM performance | 3 hours | Phase 3 |
| P5.1.4 | Optimize WASM startup time | 2 hours | P5.1.1 |
| P5.1.5 | Optimize container startup | 2 hours | P5.1.2 |
| P5.1.6 | Add performance metrics | 2 hours | P5.1.4, P5.1.5 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P5.2.1 | Add comprehensive error handling | 4 hours | All phases |
| P5.2.2 | Implement error recovery | 3 hours | P5.2.1 |
| P5.2.3 | Add structured logging | 3 hours | P5.2.1 |
| P5.2.4 | Create error documentation | 2 hours | P5.2.2 |
| P5.2.5 | Write error handling tests | 3 hours | P5.2.3 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P5.3.1 | Add `thegent sandbox` commands | 4 hours | All phases |
| P5.3.2 | Implement `sandbox init` | 2 hours | P5.3.1 |
| P5.3.3 | Implement `sandbox config` | 2 hours | P5.3.1 |
| P5.3.4 | Implement `sandbox test` | 2 hours | P5.3.1 |
| P5.3.5 | Implement `sandbox cleanup` | 2 hours | P5.3.1 |
| P5.3.6 | Add `--sandbox` flag to `run` command | 3 hours | P5.3.1 |
| P5.3.7 | Write CLI tests | 3 hours | P5.3.6 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P5.4.1 | Write user guide | 4 hours | All phases |
| P5.4.2 | Write developer guide | 3 hours | All phases |
| P5.4.3 | Create troubleshooting guide | 2 hours | P5.2.4 |
| P5.4.4 | Add code examples | 2 hours | P5.4.1 |
| P5.4.5 | Update architecture doc | 2 hours | All phases |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P5.5.1 | Add sandbox metrics collection | 3 hours | All phases |
| P5.5.2 | Implement performance tracking | 2 hours | P5.5.1 |
| P5.5.3 | Add resource usage tracking | 2 hours | P5.5.1 |
| P5.5.4 | Create metrics dashboard | 3 hours | P5.5.2, P5.5.3 |
| P5.5.5 | Write metrics tests | 2 hours | P5.5.4 |
| Phase | Duration | Total Hours | Key Deliverables |
|-------|----------|-------------|-----------------|
| **Phase 1: WASM Foundation** | Weeks 1-2 | ~57 hours | WASM sandbox working |
| **Phase 2: Container Support** | Weeks 3-4 | ~38-66 hours | Container sandboxes working |
| **Phase 3: VM Support** | Weeks 5-6 | ~63 hours | VM sandboxes working |
| **Phase 4: Native Fallback** | Week 7 | ~29 hours | Native fallback working |
| **Phase 5: Polish & Optimization** | Week 8 | ~73 hours | Production-ready |
| **Total** | **8 weeks** | **~260-288 hours** | Complete sandboxing system |
- [ ] WASM sandbox executes code successfully
- [ ] Capabilities enforced correctly
- [ ] Memory limits working
- [ ] Performance `<5%` overhead
- [ ] Podman containers working
- [ ] Resource limits enforced
- [ ] Network isolation working
- [ ] Performance `<15%` overhead
- [ ] QEMU VMs working (Linux)
- [ ] Hyper-V VMs working (Windows)
- [ ] VM snapshots working
- [ ] Performance `<30%` overhead
- [ ] Native fallback working
- [ ] Environment filtering working
- [ ] Fallback conditions detected correctly
- [ ] Performance optimized
- [ ] Error handling comprehensive
- [ ] CLI integration complete
- [ ] Documentation complete
- [x] Consolidate all session, cross-platform, and hook-rust research fragments.
- [x] Create `thegent/docs/research/RESEARCH_CONSOLIDATED.md`.
- [x] Create individual deep-dive docs for each major concept (Supermemory, Pareto, etc.).
- [x] Consolidate all shell and cross-platform guides into `thegent/docs/guides/COMPLETE_USER_GUIDE.md`.
- [x] Create a single, unified `thegent/docs/guides/QUICK_START.md`.
- [x] Update `thegent/README.md` to point to the new consolidated guides.
- [x] Synchronize `00-MASTER-INDEX.md` with current file structure.
- [ ] Update `WORK_STREAM.md` with DONE status for all Batch 8/9/10 items.
- [ ] Archive completed batch reports into a `thegent/docs/reports/archive/` directory.
- [ ] Implement `src/thegent/infra/shell_detection.py` with `get_preferred_shell()`.
- [ ] Add `THGENT_AGENT_SHELL` and `THGENT_HOOK_SHELL` to `ThegentSettings`.
- [ ] Update hook dispatcher to use shell detection, particularly for Windows (WSL vs Pwsh).
- [ ] Initialize `hooks/hook-dispatcher/` as a Rust project.
- [ ] Implement `detect_shell`, `resolve_hook`, and `run_hook` in Rust for minimal overhead (`< 50ms`).
- [ ] Update `thegent install` to compile and install the dispatcher if `cargo` is present.
- [ ] Create `src/thegent/infra/os_user_adapter.py`.
- [ ] Implement `create_os_user()` for Linux (`useradd`), macOS (`dscl`), and Windows (`New-LocalUser`).
- [ ] Handle permission checks and sudo/admin requirement reporting.
- [ ] Implement `thegent run --remote <host>` using SSH.
- [ ] Create a `RemoteExecutionManager` to handle session registry sync and log streaming from remote hosts.
- [ ] Define `~/.thegent/remote_hosts.yaml` for host definitions.
- [ ] Add macOS Space detection (`get_current_space()`) to `desktop_automation/macos.py`.
- [ ] Add Windows Session detection (`get_active_session_id()`) to `desktop_automation/windows.py`.
- [ ] Implement `is_user_active()` to prevent automation during active user sessions.
- [ ] Prototyping Orama Search integration for the documentation site.
- [ ] Index all `.md` files in `docs/` for quick CLI-based search (`thegent search <term>`).
| Item | Value |
|------|-------|
| **Fork path** | `../CLIProxyAPIPlus-fork/` (relative to thegent) |
| **Binary** | `cli-proxy-api-plus` (build from fork: `go build -o cli-proxy-api-plus ./cmd/server`) |
| **Fallback** | `scripts/start_proxy.py` checks `Path.cwd().parent / "CLIProxyAPIPlus-fork" / "cli-proxy-api-plus"` |
| **Env override** | `THGENT_CLIPROXY_BINARY=/path/to/cli-proxy-api-plus` |
| **Port** | 8317 (configurable via `THGENT_CLIPROXY_PORT`) |
| **Config** | `~/.config/thegent/cliproxy-config.yaml` (generated by `thegent cliproxy ensure-config`) |
| Provider | Config block | Static models (registry) |
|---------|--------------|---------------------------|
| minimax | `minimax:` | minimax-m2, minimax-m2.1, minimax-m2.5 |
| roo | `roo:` | roo-default |
| kilo | `kilo:` | kilo-default |
| antigravity | OAuth | Dynamic (GetAntigravityModelConfig) |
| claude | `claude-api-key:` | Various Claude models |
| gemini | `gemini-api-key:` | Various Gemini models |
| codex | `codex-api-key:` | GPT-5.x |
| deepseek | `deepseek:` | deepseek-chat, deepseek-reasoner |
| groq | `groq:` | llama-3.3-70b, llama-3.1-8b |
| mistral | `mistral:` | mistral-large, codestral |
| openrouter | `openrouter:` | (many) |
| together | `together:` | (many) |
| fireworks | `fireworks:` | (many) |
| novita | `novita:` | (many) |
| siliconflow | `siliconflow:` | DeepSeek-V3, etc. |
| Catalog provider | Fork support | Notes |
|-----------------|--------------|-------|
| **kilo** | ✓ Native | kilo: block. Kilo API (api.kilo.ai) may serve kimi-k2.5, deepseek-v3.2, glm-5, qwen3-coder — fork forwards model name to Kilo. |
| **nim** | ⚠ openai-compat | **No native block.** NIM (NVIDIA NIM) provides glm-5 and step-3.5-flash, NOT minimax. Add openai-compatibility entry with base-url (ngc.nvidia.com, build.nvidia.com). Factory config with NIM URL is auto-copied by thegent. |
| **antigravity** | ✓ Native | OAuth; gemini-3-flash, claude-sonnet/opus, etc. |
| **minimax** | ✓ Native or openai-compat | Dedicated minimax: block (OAuth + api-key) or factory config → openai-compat. |
| **glm** | ✓ Via iflow / openai-compat | iFlow OAuth or zai (factory) → openai-compat. |
| **roo** | ✓ Native | roo: block; roo-default. |
| **gemini** | ✓ Native | gemini-api-key: (Google Gemini) |
| **zen** | ⚠ openai-compat | **gemini-3-flash** served by OpenCode Zen (api.opencode.ai). Add openai-compatibility entry named "zen" with models including gemini-3-flash. thegent auto-injects when THGENT_ZEN_API_KEY is set. |
| **claude** | ✓ Native | claude-api-key: |
| **codex** | ✓ Native | codex-api-key: |
| **cursor-api** | ✓ Native | cursor: block (login protocol) |
| **deepseek** | ✓ Native | deepseek: block (different from Kilo/NIM DeepSeek) |
| Provider   | Auth                         | CLIProxy Fit                         | Status                    |
|-----------|------------------------------|--------------------------------------|---------------------------|
| Cursor    | Login (WorkosCursorSessionToken) | `cursor:` block (token-file, zero-action IDE) | Done; cursor-api + IDE storage |
| MiniMax   | OAuth + API key (like GLM)   | `minimax:` block                     | Done; token-file, api-key |
| Factory Droid | OAuth via CLIProxy       | Official docs, gists                 | Working                   |
| Kilo      | Free credits, optional API key | `kilo:` block (token-file, api-key) | Done; dedicated block     |
| Roo Code  | OpenAI-compat / Cloud       | `roo:` block (token-file, api-key)   | Done; dedicated block     |
| ID   | Task              | Description                                                                 |
|------|-------------------|-----------------------------------------------------------------------------|
| P1.1 | Fix Cursor config | Remove misleading api-key-entries; add note: Cursor uses login protocol. Cursor gets dedicated `cursor:` block (Phase 2). |
| P1.2 | Fix MiniMax config| MiniMax gets dedicated `minimax:` block (OAuth + optional API key fallback)—not openai-compatibility-only. |
| P1.3 | Update research doc | State: all providers = dedicated blocks with OAuth parity.                |
| P1.4 | Regenerate patch   | `patches/cursor-minimax-channels.patch` with corrected config.             |
| ID   | Task                 | Description                                                                 |
|------|----------------------|-----------------------------------------------------------------------------|
| P2.1 | Add `cursor:` schema | `token-file`, `cursor-api-url`. Mirror kiro structure in config.go.        |
| P2.2 | Cursor token provider| Read token; call cursor-api `/tokens/add` or `/build-key`; wire to OpenAICompatExecutor. |
| P2.3 | Token refresh       | Integrate `/tokens/refresh`.                                                |
| P2.4 | Register in rebindExecutors | Cursor executor when `cursor:` present.                              |
| ID   | Task                  | Description                                                              |
|------|-----------------------|--------------------------------------------------------------------------|
| P3.1 | Add `minimax:` schema | OAuth: token-file, access-token, refresh-token. Optional API key fallback. |
| P3.2 | MiniMax OAuth executor| Implement or adapt executor for MiniMax OAuth flow (like GLM/iFlow).     |
| P3.3 | Register in rebindExecutors | MiniMax executor when `minimax:` present.                          |
| ID   | Task                  | Description                                                              |
|------|-----------------------|--------------------------------------------------------------------------|
| P4.1 | Add cliproxy provider | Config: THGENT_CLIPROXY_URL, THGENT_CLIPROXY_API_KEY.                    |
| P4.2 | CliproxyRunner        | Use Codex CLI with CLIProxy base URL.                                   |
| P4.3 | Model scraper         | GET /v1/models from CLIProxy.                                           |
| P4.4 | Registry and catalog  | cliproxy in AGENT_NAMES; model routes.                                  |
| ID   | Task    | Description                                                                 |
|------|---------|-----------------------------------------------------------------------------|
| P5.1 | Roo Code| Research OAuth/Cloud auth; add `roo:` block with token-file/OAuth.         |
| P5.2 | Kilo    | Research Kilo provider auth; add `kilo:` block.                             |
| ID   | Task              | Description                                                                 |
|------|-------------------|-----------------------------------------------------------------------------|
| P6.1 | Provider parity matrix | Document: Cursor, MiniMax, Roo, Kilo = same config pattern as Kiro, Gemini, Claude, Codex. |
| P6.2 | Setup guides      | Per-provider: OAuth flow, token-file, refresh.                              |
| P6.3 | Factory Droid     | Link to official CLIProxyAPIDocs; Droid already has parity.                 |
| Provider   | Config Block | Auth                    | Status   |
|------------|--------------|-------------------------|----------|
| Kiro       | kiro:        | token-file, OAuth       | Native   |
| Gemini     | gemini-api-key: | api-key              | Native   |
| Claude     | claude-api-key: | api-key              | Native   |
| Codex      | codex-api-key:  | api-key              | Native   |
| Cursor     | cursor:      | token-file, cursor-api  | Phase 2  |
| MiniMax    | minimax:     | token-file, api-key     | Phase 3  |
| Roo Code   | roo:         | token-file, api-key     | Phase 5  |
| Kilo       | kilo:        | token-file, api-key     | Phase 5  |
| cliproxy   | (thegent)    | local CLIProxy           | Phase 4  |
| Area                  | Path                                                       |
|-----------------------|------------------------------------------------------------|
| Config schema         | CLIProxyAPIPlus-fork/internal/config/config.go           |
| Kiro reference        | Same file – `kiro:` block                                 |
| Executor registration | CLIProxyAPIPlus-fork/sdk/cliproxy/service.go              |
| Model definitions     | CLIProxyAPIPlus-fork/internal/registry/model_definitions.go |
| Config example        | CLIProxyAPIPlus-fork/config.example.yaml                  |
| Thegent config        | thegent/config.py                                         |
| Thegent registry      | thegent/agents/registry.py                                |
| CursorApiRunner       | thegent/agents/cursor_api_runner.py                        |
| Component | Purpose | Used By |
|-----------|---------|---------|
| **Queue storage** | `.thegent/prompt_queue.jsonl` (project) or `~/.thegent/prompt_queue.jsonl` (global) | Claude Code, Codex, MCP tools |
| **Queue MCP tools** | thegent_queue_list, claim, done, add, edit, release, extend_lease | Both (via MCP) |
| **Queue TUI** | `thegent queue tui` — add/edit/list in separate terminal | Both |
| **Harvest logic** | harvest-idea-seeds.sh, harvest-pending-queue.sh | Both |
| **Handoff output** | `docs/research/pending-handoff.md` or `.thegent/next-session-prompts.md` | Both |
| **Escalation** | `thegent govern escalate` for $block | Both |
| Agent | Prompt Intercept | Session Stop | Per-Turn |
|-------|------------------|--------------|----------|
| **Claude Code** | UserPromptSubmit → prompt-submit-guard | Stop → harvest-pending-queue | — |
| **Codex** | run_impl preprocessor (exec); wrapper exit (interactive) | Wrapper exit → harvest | notify → codex-notify |
| Hook | Script | Status |
|------|--------|--------|
| **UserPromptSubmit** | `prompt-submit-guard.sh` | ✓ $defer, $pending, $block, $idea |
| **Stop** | `harvest-pending-queue.sh` | ✓ Flushes queue to handoff |
| **Stop** | `harvest-idea-seeds-stop.sh` | ✓ Runs harvest-idea-seeds |
| **SessionStart** | — | ⏳ Optional: inject handoff summary |
| Mode | Claude Code | Codex | thegent Entry |
|------|-------------|-------|---------------|
| **Interactive** | `claude` | `codex` | `thegent codex`, `thegent dex`, `thegent clode` |
| **Headless** | `claude -p "prompt"` | `codex exec -` | `thegent run -M codex "prompt"`, `thegent run -M claude "prompt"` |
| Feature | Claude Code | Codex + Harness | Cursor | Factory Droid | Augment |
|---------|-------------|-----------------|--------|---------------|---------|
| **Hooks** | 15 native | Wrapper + notify | Harvest from transcripts | — | — |
| **Agent teams** | Native | thegent team | — | Droid as teammate | Intent |
| **Queue** | UserPromptSubmit + Stop | run_impl + wrapper | Harvest $defer | run_impl | run_impl |
| **Rules** | CLAUDE.md, skills | .codex/skills | .cursor/rules | .factory/droids | — |
| **Unified rules** | — | **thegent rules sync** → all platforms | | | |
| Platform | Interactive | Headless | Rules | thegent Entry |
|----------|-------------|----------|-------|---------------|
| **Claude Code** | claude | claude -p | CLAUDE.md | thegent clode, run -M claude |
| **Codex** | codex | codex exec - | .codex/skills | thegent codex, run -M codex |
| **Cursor-agent** | Composer | cursor-agent CLI | .cursor/rules | run -M cursor-agent |
| **Factory droid** | — | droid exec | .factory/droids | run -M droid:name |
| **Augment** | auggie | auggie --print | — | run -M augment |
| Hook | When Fires | Config | Payload | thegent Use |
|------|------------|--------|---------|-------------|
| **AfterAgent** | Agent finishes turn (no follow-up needed) | `notify` in config.toml | `AgentTurnComplete`: thread_id, turn_id, cwd, input_messages, last_assistant_message | Per-turn harvest, queue flush trigger |
| **AfterToolUse** | After every tool call | **Not configurable** — after_tool_use always empty | turn_id, call_id, tool_name, tool_input, executed, success, duration_ms, output_preview | Would need patch to enable |
| Mode | Entry | Prompt Source | thegent Control |
|------|-------|---------------|-----------------|
| **Interactive TUI** | `codex` (no args) or `codex --model X` | User types in Codex TUI | None — Codex owns TUI |
| **exec (non-interactive)** | `codex exec -` | stdin | **Full** — we pipe prompt |
| **dex (thegent)** | `thegent dex` → `subprocess.run([codex])` | Interactive TUI | None — we spawn, don't intercept |
| Path | Flow |
|------|------|
| **dex_main** | `_run_codex_interactive()` → subprocess.run([codex, --model, ...]) — interactive, no prompt control |
| **codex_proxy** | `codex exec - --skip-git-repo-check` — prompt piped to stdin |
| **direct_agents** | `codex exec -` for codex agent |
| Option | Approach | Effort | Parity |
|--------|----------|--------|--------|
| **A. Wrapper + exit hook** | `thegent dex` spawns codex; on exit, run harvest/flush. No prompt control. | Low | Partial (stop only) |
| **B. Custom TUI** | Build our TUI that sends prompts to Codex via exec or API. Replace `codex` with `thegent codex-tui`. | High | Full |
| **C. Codex SDK** | Use Codex TypeScript SDK; we own the event loop, can intercept. | Medium | Full |
| **D. Process wrapper** | Pty wrapper: we sit between user and Codex, parse keystrokes. | Very High | Full |
| Component | Purpose | Entry |
|-----------|---------|-------|
| **thegent codex** | Wrapper for `codex`; spawns codex, runs on-exit hook | `thegent codex` or shim `codex` → `thegent codex --wrap` |
| **on-exit hook** | `harvest-idea-seeds.sh`, `harvest-pending-queue.sh`, flush queue | Called when codex process exits |
| **Session start** | Load handoff from `.thegent/next-session-prompts.md`; inject as first prompt | Before spawning codex; for exec: prepend to stdin |
| **Prompt preprocessor** | Parse $defer, $block, $idea before piping to exec | In codex_proxy / run_impl |
| Task | Description | Agent | Effort |
|------|-------------|-------|--------|
| 1.1 | Implement queue storage module: `.thegent/prompt_queue.jsonl` read/write | Both | Small |
| 1.2 | **Claude Code:** Migrate prompt-submit-guard to write to `.thegent/prompt_queue.jsonl` (was `.claude/pending-queue.jsonl`) | Claude | Small |
| 1.3 | **Claude Code:** Migrate harvest-pending-queue to read from `.thegent/prompt_queue.jsonl` | Claude | Small |
| 1.4 | Implement `thegent codex-notify` — parse JSON, append to harvest buffer | Codex | Small |
| 1.5 | Add `notify = ["thegent", "codex-notify"]` to install_to_codex / mcp_manage | Codex | Small |
| 1.6 | Create `.codex/skills/thegent-queue/SKILL.md` | Codex | Small |
| 1.7 | Implement queue MCP tools (list, claim, done, add, edit, release, extend_lease) | Both | Medium |
| Task | Description | Agent | Effort |
|------|-------------|-------|--------|
| 2.1 | **Codex exec:** Prompt preprocessor in run_impl: detect $defer, $block before piping to codex exec | Codex | Small |
| 2.2 | **Codex exec:** $defer → append to queue, return without spawning | Codex | Small |
| 2.3 | **Codex exec:** $block → escalation, block until resolved | Codex | Medium |
| 2.4 | **Codex exec:** On exit: run harvest-pending-queue logic | Codex | Small |
| 2.5 | **Codex exec:** Session start: load handoff, prepend to exec stdin | Codex | Small |
| 2.6 | **Claude Code:** SessionStart hook: inject "N pending from last session" (optional) | Claude | Small |
| Task | Description | Effort |
|------|-------------|--------|
| 3.1 | `thegent codex` wrapper: spawn codex, on exit run harvest | Small |
| 3.2 | Shim `codex` → `thegent codex --wrap` (optional, install step) | Small |
| 3.3 | Integrate harvest-idea-seeds-stop.sh, harvest-pending-queue.sh into exit | Small |
| Task | Description | Agent | Effort |
|------|-------------|-------|--------|
| 4.1 | `thegent queue tui` — Textual TUI for add/edit/list | Both | Medium |
| 4.2 | CLI: `thegent queue add|list|edit|release|status` | Both | Small |
| 4.3 | Multi-agent locking: claimed_by, lease_expires_at, atomic claim | Both | Medium |
| Task | Description | Agent | Effort |
|------|-------------|-------|--------|
| 5.1 | Evaluate Codex TypeScript SDK for event-loop ownership | Codex | Medium |
| 5.2 | Custom TUI that sends prompts via SDK — full UserPromptSubmit parity | Codex | High |
| Task | Description | Agent | Effort |
|------|-------------|-------|--------|
| 6.1 | Implement shared task list: `.thegent/teams/{id}/tasks/` storage | Both | Medium |
| 6.2 | MCP tools: thegent_team_create, task_list, task_assign, task_claim, task_done | Both | Medium |
| 6.3 | `thegent team create` — spawn lead + N teammates (codex exec) | Codex | Medium |
| 6.4 | thegent_team_message, thegent_team_broadcast, thegent_team_shutdown | Both | Small |
| 6.5 | Display: in-process TUI (Shift+Up/Down) or tmux split panes | Codex | Medium |
| 6.6 | TeammateIdle: poll teammate stdout, run hook on idle | Codex | Medium |
| 6.7 | TaskCompleted hook: exit 2 blocks completion, sends feedback | Both | Small |
| 6.8 | Headless team: lead + teammates all via codex exec for CI | Codex | Small |
| Task | Description | Agent | Effort |
|------|-------------|-------|--------|
| 7.1 | SessionStart: wrapper injects handoff before first prompt | Codex | Small |
| 7.2 | PreToolUse: requires Codex SDK or custom TUI (Phase 5) | Codex | High |
| 7.3 | SubagentStart/Stop: thegent_run exit = SubagentStop | Both | Small |
| 7.4 | TeammateIdle, TaskCompleted: Phase 6 | Both | — |
| Task | Description | Agent | Effort |
|------|-------------|-------|--------|
| 8.1 | `thegent run -M claude "prompt"` — use `claude -p` when available | Claude | Small |
| 8.2 | --continue, --resume for Claude headless (if supported) | Claude | Small |
| 8.3 | --output-format json, --allowedTools passthrough | Claude | Small |
| Task | Description | Agent | Effort |
|------|-------------|-------|--------|
| 9.1 | Define canonical rules format: `.thegent/rules/` or `.cursor/rules/` as source | Both | Medium |
| 9.2 | `thegent rules sync` — sync to .cursor/rules/, CLAUDE.md, .codex/skills | All | Medium |
| 9.3 | Rule mapping: .mdc → CLAUDE.md section; .mdc → Codex skill | All | Small |
| 9.4 | .cursorrules → rules sync (legacy support) | Cursor | Small |
| Task | Description | Agent | Effort |
|------|-------------|-------|--------|
| 10.1 | `thegent run -M cursor-agent "prompt"` — cursor-agent CLI headless | Cursor | Small |
| 10.2 | Harvest: extend $defer/$pending/$idea to Cursor transcripts | Cursor | Small |
| 10.3 | cursor-api runner: ensure queue, harvest on run | Cursor | Small |
| Task | Description | Agent | Effort |
|------|-------------|-------|--------|
| 11.1 | `thegent run -M droid:worker "prompt"` — $defer/$block preprocessor | Droid | Small |
| 11.2 | On droid exit: harvest-pending-queue | Droid | Small |
| 11.3 | Droid as teammate: thegent team can spawn droids | Droid | Medium |
| 11.4 | Droid + rules: inject .thegent rules into droid prompt | Droid | Small |
| Task | Description | Agent | Effort |
|------|-------------|-------|--------|
| 12.1 | `thegent run -M augment "prompt"` — auggie --print when available | Augment | Small |
| 12.2 | Add Context Engine MCP to thegent mcp install (cursor, codex) | Augment | Small |
| 12.3 | Document augment in agent registry | Augment | Small |
| Task | Description | Agent | Effort |
|------|-------------|-------|--------|
| 13.1 | `thegent run -M opencode "prompt"` — oc when available | OpenCode | Small |
| 13.2 | Document opencode in agent registry | OpenCode | Small |
| 13.3 | Zen: do NOT integrate (per ZEN_INTEGRATION.md) | — | — |
| Phase | Deps |
|-------|-----|
| 1 | None |
| 2 | Prompt parsing in cli_impl |
| 3 | subprocess exit callback |
| 4 | Textual (for TUI) — already in pyproject? |
| 5 | Codex SDK (npm package) |
| Component | Agent | Test |
|-----------|-------|------|
| prompt-submit-guard $defer | Claude | Unit: invoke hook with $defer stdin; assert queue append, exit 1 |
| prompt-submit-guard $block | Claude | Unit: invoke hook with $block stdin; assert escalation, exit 1 |
| harvest-pending-queue | Both | Unit: temp queue file → run hook → assert handoff written, queue cleared |
| codex-notify | Codex | Unit: parse AgentTurnComplete JSON |
| Queue storage | Both | Unit: append, read, claim, release |
| queue tools | Both | Integration: MCP call with mock session |
| Wrapper exit | Codex | Integration: spawn codex, kill, assert harvest runs |
| $defer in run_impl | Codex | Unit: run_impl with $defer prompt → no spawn, queue append |
| Risk | Mitigation |
|------|------------|
| Codex changes notify payload | Version check; graceful fallback |
| Config.toml overwrite | Merge, don't replace |
| notify script blocks | Fire-and-forget; Codex spawns async |
| Queue file corruption | Append-only, atomic writes, lock file |
- [ ] UserPromptSubmit: $defer/$pending queues, $block escalates, $idea saves
- [ ] Stop: harvest-pending-queue flushes to handoff
- [ ] Queue path: unified `.thegent/prompt_queue.jsonl` (Phase 1 migration)
- [ ] Queue tools: agent can list, claim, done via MCP
- [ ] Queue TUI: user can add/edit/list in separate terminal
- [ ] Headless: `thegent run -M claude "prompt"` uses `claude -p` (Phase 8)
- [ ] Interactive: on exit, harvest runs (idea-seeds, pending queue)
- [ ] Headless: `thegent run -M codex "prompt"` — $defer, $block, harvest on exit
- [ ] Exec: $defer queues, $block escalates (run_impl preprocessor)
- [ ] notify hook: thegent receives AfterAgent JSON
- [ ] Queue tools: agent can list, claim, done via MCP
- [ ] Queue TUI: same as Claude Code
- [ ] Agent teams: `thegent team create` spawns lead + teammates (Phase 6)
- [ ] `thegent run -M cursor-agent "prompt"` headless (Phase 10)
- [ ] Harvest: $defer/$pending/$idea from Cursor transcripts
- [ ] Rules sync: `thegent rules sync` → .cursor/rules (Phase 9)
- [ ] `thegent run -M droid:name "prompt"` — $defer/$block, harvest on exit (Phase 11)
- [ ] Droid as teammate in agent teams
- [ ] Rules injected into droid prompt
- [ ] `thegent run -M augment "prompt"` — auggie --print (Phase 12)
- [ ] Context Engine MCP in thegent mcp install
- [ ] `thegent run -M opencode "prompt"` — oc (Phase 13)
- [ ] OpenCode in agent registry; Zen NOT integrated
- [ ] Single queue storage for all platforms
- [ ] Unified rules: `thegent rules sync` → Cursor, Claude, Codex
- [ ] Lifecycle: loop can check queue between iterations
- [ ] All features available both interactively and headlessly (where applicable)
| Source | Path | Key field |
|--------|------|-----------|
| Claude | ~/.claude/history.jsonl | display |
| Codex | ~/.codex/history.jsonl | text |
| Cursor | ~/.cursor/projects/Users-*/agent-transcripts/*.jsonl | message.content[].text |
| Target | Output |
|--------|--------|
| Cursor | .cursor/rules/{name}.mdc (copy) |
| Claude | CLAUDE.md ## Rules section, or .claude/skills/{name}/SKILL.md |
| Codex | .codex/skills/{name}/SKILL.md |
| Need | File / Command |
|------|----------------|
| Queue schema | `.thegent/prompt_queue.jsonl` — JSONL, ts, prompt, project, claimed_by, lease_expires_at |
| codex-notify | `thegent codex-notify` — argv[-1] = JSON |
| run preprocessor | `cli_impl.run_impl` or `codex_proxy` — before `subprocess.run([codex, exec, -])` |
| Harvest paths | Claude: ~/.claude/history.jsonl; Codex: ~/.codex/history.jsonl; Cursor: ~/.cursor/projects/*/agent-transcripts/*.jsonl |
| Rules sync | `thegent rules sync` → .cursor/rules, CLAUDE.md, .codex/skills |
| Team storage | `.thegent/teams/{id}/tasks.jsonl` |
| Droid resolve | ~/.local/bin/droid, ~/.factory/bin/droid |
| Agent registry | `src/thegent/agents/registry.py` — get_runner(mode) |
| MCP tools | 30+ tools; see MULTI_PLATFORM_DEEP_DIVE Part XXVI |
| MCP resources | 20+ thegent:// URIs; Part XXVII |
| MCP transport | STDIO (Claude Code), HTTP :3847 (Cursor, Codex) |
| EventStore | FASTMCP_EVENT_STORE_URL → Redis for distributed |
| Issue | Impact |
| **Process-global** | One process = one config; cannot vary per tenant |
| **No per-request override** | Timeout, concurrency, routing cannot differ by tenant/session |
| **No runtime updates** | Changing config requires restart or new process |
| **No audit trail** | Who changed what, when — not trackable |
| **No validation** | Invalid config only discovered at use time |
| Approach | Tenants | Effort | Use Case |
|----------|---------|--------|----------|
| Manual | `<10` | Low | Start; scripts + docs |
| Low-code | Occasional | Medium | Power Automate, workflows |
| Custom | Many | High | Full control, testability |
| Plan / Doc | CP Relationship | Section |
|------------|-----------------|---------|
| Agent Registry | Session Registry = CP subsystem | §3.1 |
| Agent Registry Research | IPC (FIFO, socket) owned by CP | §3.2 |
| Compute Offload | "Unified Control Plane" = this CP | §3.3 |
| CROSS_PLATFORM_MULTI_TENANT | CP = Coordinator; tenant context | §3.4 |
| Gardener | CP hosts ROUTE; hunger state | §3.5 |
| process-compose | CP as third service | §3.6 |
| TUI Compositor | CP feeds dashboard; "unified control plane" | §3.7 |
| Unified Work Stream | CP can host claim state, do-next | §3.8 |
| Alignment | Control Plane Role |
|-----------|-------------------|
| Session Registry | Control plane holds session index; CLI/MCP query it |
| `session list` / `session send` | Control plane resolves session metadata, routes messages |
| IPC (FIFO, Unix socket) | Control plane can own message endpoints |
| Owner-scoped | Control plane enforces tenant/owner filtering |
| IPC Option | Control Plane Use |
|------------|-------------------|
| FIFO | Per-session message delivery; CP writes, agent reads |
| Unix socket | CP ↔ CLI/MCP; bidirectional, robust |
| File-based | Fallback; CP writes to `{session}.messages.jsonl` |
| Component | Control Plane Integration |
|-----------|---------------------------|
| Compute Catalog | CP hosts catalog; offload router queries CP |
| Offload Router | CP runs router logic; route decisions are config |
| Bridge Protocol | CP orchestrates serialization/deserialization |
| Concept | Control Plane Role |
|---------|-------------------|
| TenantContext | CP resolves tenant from request; injects into config |
| EditLeaseManager | CP can host lease coordination (or delegate to Redis) |
| Per-tenant concurrency | CP enforces `concurrency.per_tenant_max` |
| Coordinator (Multi-Tenant) | CP **is** the coordinator |
| Concept | Control Plane Role |
|---------|-------------------|
| SCAN → PRIORITIZE → ROUTE → EXECUTE | CP can host ROUTE; Gardener queries CP for routing policy |
| Hunger states | CP stores hunger state; Gardener reads/writes |
| Agent spawn | CP provides config (timeout, agent, model) for spawn |
| Current | Control Plane Extension |
|---------|-------------------------|
| `mcp_up` / `mcp_down` | Control plane can be a process-compose service |
| MCP + proxy bundled | Add control-plane as third service |
| CLI introspection | CLI talks to control plane for config, not env |
| Concept | Control Plane Role |
|---------|-------------------|
| "Unified control plane for agent orchestration and monitoring" | CP **is** that control plane; TUI queries CP for state |
| Real-time process/session tracking | CP session index; TUI subscribes or polls |
| Work stream integration (do-next, claim, complete) | CP can host work stream metadata; TUI reads via CP |
| Statusbar, session status | CP provides aggregated view |
| Concept | Control Plane Role |
|---------|-------------------|
| WORK_STREAM.md canonical | CP can cache/aggregate; or delegate to file (CP orchestrates) |
| Claim / Complete | CP can host claim coordination (alternative to file-based) |
| do-next, spawn-next | CP provides config for spawn; CP can enforce per-tenant limits |
| Mode | Control Plane | CLI/MCP | Use Case |
|------|---------------|---------|----------|
| **Embedded** | In-process (CLI/MCP load config directly) | Same process | Single-tenant, dev, backward compat |
| **Standalone** | Separate process (Unix socket / HTTP) | Connect to CP | Multi-tenant, production |
| **Hybrid** | Optional; CLI tries CP first, falls back to env | Best effort | Migration, gradual rollout |
| Responsibility | Description | API |
|----------------|-------------|-----|
| **Config resolution** | Resolve config for (tenant_id?, session_id?, request) | `GET /config?tenant=X&key=default_timeout` |
| **Tenant catalog** | Store tenant metadata, SKUs, stamps | `GET /tenants`, `POST /tenants` |
| **Session index** | Canonical list of sessions (from RunRegistry + discovery) | `GET /sessions`, `GET /sessions/:id` |
| **Policy evaluation** | Override, lane, deferral decisions | `POST /policy/evaluate` |
| Responsibility | Description | API |
|----------------|-------------|-----|
| **Consumption tracking** | Per-tenant resource usage | `GET /tenants/:id/consumption` |
| **Config mutation** | Update config (with audit) | `PUT /config`, `PATCH /tenants/:id/config` |
| **Lifecycle hooks** | On tenant onboard/offboard | Webhook / internal event |
| **Offload routing** | Compute catalog, workload classifier | `POST /offload/route` |
| Responsibility | Description | API |
|----------------|-------------|-----|
| **Tenant placement** | Bin-packing, stamp assignment | `POST /tenants/place` |
| **Maintenance ops** | Cleanup, retention, secret rotation | Scheduled jobs |
| **Federation** | Cross-stamp coordination | Sync protocol |
| Aspect | RunRegistry | CP Session Index |
|--------|-------------|------------------|
| **Write ownership** | CLI/agent writes on spawn/exit | CP does not write directly |
| **Aggregation** | Per-run metadata; file or in-memory | CP aggregates from RunRegistry + discovery |
| **Source of truth** | RunRegistry for lifecycle | CP for query/aggregation; eventual consistency |
| **Use case** | `session list`, `session send` | TUI dashboard, session search, tenant view |
| Transport | Latency | Use Case | Fallback |
|-----------|---------|----------|----------|
| **Unix socket** | `<1ms` | Local CLI, MCP | Primary for standalone CP |
| **HTTP (localhost)** | 1–5ms | Remote CLI, health checks | Alternative |
| **stdio** | N/A | Embedded mode | When CP in-process |
| **File-based** | 10–50ms | Fallback, audit | When CP unavailable |
| Method | Description |
|--------|-------------|
| **Socket path** | `~/.thegent/control-plane.sock` or `$XDG_RUNTIME_DIR/thegent/cp.sock` |
| **Port** | `THGENT_CONTROL_PLANE_PORT` (default 3848) |
| **Env** | `THGENT_CONTROL_PLANE_URL=http://127.0.0.1:3848` |
| **process-compose** | Control plane as service; CLI discovers via health endpoint |
| Command | Purpose |
|---------|---------|
| `thegent control-plane status` | Is CP running? Health |
| `thegent control-plane start` | Start CP (if standalone) |
| `thegent control-plane stop` | Stop CP |
| `thegent config show [--tenant X]` | Show resolved config |
| `thegent config set <key> <value> [--tenant X]` | Update config (if CP supports mutation) |
| Tool | Purpose |
|------|---------|
| `thegent_config_resolve` | Resolve config for current context |
| `thegent_control_plane_status` | CP health, version |
| `thegent_tenant_list` | List tenants (admin) |
| `thegent_config_set` | Set config key (admin, with audit) |
| Source | Tenant ID |
|--------|-----------|
| **CLI** | `--tenant X`, or from `cwd` → project config, or `default` |
| **MCP** | Tool param, or from MCP context (workspace path hash) |
| **Session** | Stored in session meta at spawn |
| Event | Action |
| Start | Load catalog, bind socket, start API |
| Config file change | Reload (if watch enabled) |
| SIGTERM | Graceful shutdown; drain connections |
| Crash | process-compose restarts (if managed) |
| Phase | Scope | Risk |
|-------|-------|------|
| **0** | Design complete; no code change | None |
| **1** | ConfigProvider abstraction; ThegentSettings implements it | Low |
| **2** | Control plane serve (read-only); CLI/MCP opt-in connect | Medium |
| **3** | Tenant catalog; per-tenant config resolution | Medium |
| **4** | Config mutation API; audit logging | Medium |
| **5** | process-compose integration; default for multi-tenant | Low |
| Failure | Impact | Mitigation |
|---------|--------|------------|
| CP process down | CLI/MCP cannot get config | Fallback to env; warn user |
| CP slow | CLI blocks on config | Timeout (e.g. 2s); fallback |
| CP returns invalid config | Agent misconfigured | Validate on CP side; schema |
| Network partition | Remote CLI cannot reach CP | Fallback to env; cache last config |
| Tenant not found | Config resolution fails | Use default tenant or global |
| Catalog corruption | Wrong tenant config | Checksum; backup; restore |
| Threat | Mitigation |
|--------|------------|
| **Unauthorized config access** | Tenant isolation; CP returns only tenant's config |
| **Config tampering** | Audit log; integrity checks on catalog |
| **Privilege escalation** | CP runs as same user as CLI; no elevated perms |
| **Secret leakage** | Secret references (URI) only; never store raw secrets in config |
| **DoS via config resolution** | Rate limit per client; timeout on resolve |
| Transport | Auth Model |
|-----------|------------|
| **Unix socket** | File permissions (`chmod 0700`); same UID = trusted. No explicit auth. |
| **HTTP (localhost)** | Optional: `Authorization: Bearer <token>` or mTLS. Default: trust localhost. |
| **HTTP (remote)** | Required: API key, JWT, or mTLS. Not in initial scope. |
| Metric | Type | Description |
|--------|------|-------------|
| `thegent_cp_config_resolves_total` | Counter | Config resolve requests by tenant, status |
| `thegent_cp_config_resolve_duration_seconds` | Histogram | Latency of config resolution |
| `thegent_cp_tenants_active` | Gauge | Number of active tenants in catalog |
| `thegent_cp_sessions_indexed` | Gauge | Sessions in session index |
| `thegent_cp_fallback_total` | Counter | Fallbacks to env (CP unavailable) |
| Doc | Purpose |
|-----|---------|
| [AGENT_REGISTRY_DESIGN.md](../AGENT_REGISTRY_DESIGN.md) | Session registry, IPC, UX |
| [AGENT_REGISTRY_RESEARCH.md](../AGENT_REGISTRY_RESEARCH.md) | IPC options, prior art |
| [research-compute-offload/design.md](../changes/research-compute-offload/design.md) | Offload, control plane mention |
| [CROSS_PLATFORM_MULTI_TENANT_QUICK_REFERENCE.md](../reference/CROSS_PLATFORM_MULTI_TENANT_QUICK_REFERENCE.md) | Tenant coordination |
| [GARDENER_ARCHITECTURE.md](../reference/GARDENER_ARCHITECTURE.md) | Gardener loop |
| [UNIFIED_WORK_STREAM_DESIGN.md](../reference/UNIFIED_WORK_STREAM_DESIGN.md) | Work stream |
| Source | URL |
|--------|-----|
| Microsoft: Multitenant Control Planes | https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/considerations/control-planes |
| Microsoft: Architectural Approaches | https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/approaches/control-planes |
| Kong: Multi-Tenancy | https://konghq.com/blog/enterprise/multi-tenancy |
| Wikipedia: Control plane | https://en.wikipedia.org/wiki/Control_plane |
| ID | Decision | Rationale |
|----|----------|-----------|
| DR-CP-1 | ConfigProvider abstraction | Allows embedded (env) and standalone (CP) without code paths |
| DR-CP-2 | Unix socket primary for local | Lowest latency; no port conflict |
| DR-CP-3 | Fallback to env on CP failure | Backward compat; no hard dependency |
| DR-CP-4 | Tenant from cwd by default | Pragmatic; project dir = tenant for dev |
| DR-CP-5 | process-compose for CP lifecycle | Aligns with MCP+proxy; single orchestration |
| DR-CP-6 | JSON-RPC 2.0 for IPC | MCP already uses JSON-RPC; consistency |
| DR-CP-7 | Session index in CP | Agent Registry Session Registry = CP subsystem |
| DR-CP-8 | RunRegistry = write owner; CP = aggregator | CP reads RunRegistry; no duplicate write path |
| DR-CP-9 | Unix socket auth = filesystem UID | No explicit auth for local; HTTP localhost trust default |
- [ ] ConfigProvider protocol + EnvConfigProvider (full resolution semantics)
- [ ] Control plane serve command (socket + HTTP)
- [ ] Config resolve API (`POST /v1/config/resolve`)
- [ ] Config schema validation (JSON Schema)
- [ ] CLI: connect to CP when THGENT_CONTROL_PLANE_URL set
- [ ] CLI: fallback to env on failure (circuit breaker)
- [ ] Tenant catalog (file-based: `~/.thegent/tenants/*.yaml`)
- [ ] process-compose: add control-plane service
- [ ] MCP: thegent_config_resolve tool
- [ ] Audit logging for config access
- [ ] OTel spans for config.resolve, tenant.catalog.get
- [ ] Metrics: config_resolves_total, resolve_duration_seconds
- [ ] Docs: CONTROL_PLANE_QUICK_START.md
| Question | Resolution |
|----------|------------|
| **Persistence** | Phase 1–3: File-based (`~/.thegent/tenants/*.yaml`). Phase 4+: SQLite optional for audit, scale. External DB = future. |
| **Auth** | Unix socket: filesystem UID/GID. HTTP localhost: trust by default; token optional for production. See §14.2. |
| **Federation** | Out of scope initially. Global vs Stamp CP noted in §2.1. Sync protocol in P2. |
| **Observability** | Resolved: §15 defines metrics, OTel spans, structured logging. |
| Phase | Name | Est. Effort | Depends On | Gate |
|-------|------|-------------|------------|------|
| **1** | ConfigProvider abstraction | 2–3 days | None | All CLI paths use provider |
| **2** | Control plane serve | 3–4 days | Phase 1 | `thegent control-plane serve` works |
| **3** | CLI integration + fallback | 2–3 days | Phase 1, 2 | `run`/`bg` use CP when configured |
| **4** | Tenant catalog | 2–3 days | Phase 2 | Per-tenant config resolution |
| **5** | process-compose + MCP | 1–2 days | Phase 2, 3 | CP as service; MCP tool |
| **6** | Observability + hardening | 2 days | Phase 2–5 | Metrics, OTel, circuit breaker |
- [ ] Define `ConfigProvider` protocol
- [ ] Implement `EnvConfigProvider` using `ThegentSettings()`
- [ ] Add `_ALL_CONFIG_KEYS` from `ThegentSettings.model_fields`
- [ ] Unit tests: `resolve` merges overrides correctly; `get_tenant_config` returns None (env has no tenants)
- [ ] Add `get_config_provider()`; Phase 1 returns only `EnvConfigProvider`
- [ ] Add `THGENT_CONTROL_PLANE_URL` to config docs
- [ ] Add `config_provider: ConfigProvider | None = None` param to `run_impl` / `bg_impl`
- [ ] When `config_provider` is set, call `resolve(tenant_id, request_overrides={timeout, agent, ...})` and merge into effective config
- [ ] CLI: `run_cmd` / `bg_cmd` pass `get_config_provider()` when `THGENT_CONTROL_PLANE_URL` or `thegent control-plane status` indicates CP is available (Phase 3; Phase 1: always pass `EnvConfigProvider()` for pilot)
- [ ] Pilot: `run_cmd` uses `EnvConfigProvider().resolve()` for timeout/agent override; verify no regression
- [ ] `thegent run "Fix bug"` behaves identically; `thegent run -t 1800 "Fix bug"` uses 1800s
- [ ] `EnvConfigProvider.resolve(request_overrides={"default_timeout": 1800})` returns merged config
- [ ] Add `control-plane` Typer group with `serve` subcommand
- [ ] `control-plane serve` invokes `control_plane_serve_impl()`
- [ ] Create `control_plane/` package: `__init__.py`, `server.py`
- [ ] Implement `POST /v1/config/resolve` — accepts `tenant_id`, `session_id`, `overrides`, `keys`; returns merged config (Phase 2: global only, no tenant catalog)
- [ ] Implement `GET /health` — returns `{"status":"ok","version":"..."}`
- [ ] Load base config from `ThegentSettings()` at startup
- [ ] Config schema validation (JSON Schema) for response
| Platform | Primary | Fallback |
|----------|---------|----------|
| Linux, macOS, WSL | Unix socket | HTTP |
| Windows | HTTP | Named pipe (optional) |
- [ ] Use `platform.system()` to choose transport
- [ ] Unix: bind `~/.thegent/control-plane.sock` or `$XDG_RUNTIME_DIR/thegent/cp.sock`
- [ ] Windows: bind `http://127.0.0.1:{port}` only (no socket)
- [ ] Add `--socket` and `--port` options; default: socket on Unix, port on Windows
- [ ] Use `uvicorn` or `hypercorn` with `uds` for Unix socket
- [ ] Implement `ControlPlaneConfigProvider` with `httpx` (sync, timeout 2s)
- [ ] `get_config_provider()` returns it when `THGENT_CONTROL_PLANE_URL` is set
- [ ] Handle connection errors; raise `ControlPlaneUnavailable` for fallback logic
- [ ] `thegent control-plane serve --port 3848` starts; `curl http://127.0.0.1:3848/health` returns 200
- [ ] `curl -X POST http://127.0.0.1:3848/v1/config/resolve -d '{"overrides":{"default_timeout":1800}}'` returns merged config
- [ ] Before `run_impl`/`bg_impl`: call `get_config_provider().resolve(tenant_id, request_overrides={...})`
- [ ] Resolve `tenant_id`: `--tenant X` | `cwd` → project config | `default`
- [ ] Pass resolved config to `run_impl`/`bg_impl` (or use provider inside impl)
- [ ] On `ControlPlaneUnavailable`: fall back to `EnvConfigProvider.resolve()`; log warning
- [ ] After N consecutive CP failures (e.g. 5), open circuit; use env only
- [ ] After cooldown (e.g. 30s), half-open; try once
- [ ] On success, close circuit
- [ ] Config: `THGENT_CP_CIRCUIT_THRESHOLD`, `THGENT_CP_CIRCUIT_RECOVERY_S`
| Command | Implementation |
|---------|----------------|
| `thegent control-plane status` | GET /health; print status or "not running" |
| `thegent config show [--tenant X]` | Resolve config for tenant; print as YAML/JSON |
- [ ] `control-plane status` — try CP URL; print status
- [ ] `config show` — use `get_config_provider().resolve(tenant_id)`; print
- [ ] With `THGENT_CONTROL_PLANE_URL=http://127.0.0.1:3848` and CP running: `run` uses CP config
- [ ] With CP down: `run` falls back to env; warning printed
- [ ] `thegent config show` prints resolved config
- [ ] Load tenants from `~/.thegent/tenants/*.yaml` (or `%LOCALAPPDATA%\thegent\tenants\` on Windows)
- [ ] Schema: `Tenant(id, name, config: TenantConfig, ...)`
- [ ] `TenantConfig` = subset of ThegentSettings (timeout, concurrency, etc.)
- [ ] Config resolution order: request → session → tenant → global
- [ ] `POST /v1/config/resolve` uses tenant catalog when `tenant_id` provided
- [ ] Merge: global → tenant → session → overrides
- [ ] Validate tenant config with JSON Schema before returning
- [ ] `_resolve_tenant_from_cwd(cwd: Path) -> str`: read `.thegent/tenant` or `pyproject.toml` thegent.tenant; default `"default"`
- [ ] Pass tenant_id to `resolve` in run/bg paths
- [ ] Create `~/.thegent/tenants/acme.yaml` with `default_timeout: 1800`
- [ ] `thegent run --tenant acme "Fix bug"` uses 1800s
- [ ] `thegent config show --tenant acme` shows acme overrides
- [ ] Add `control-plane` service: `thegent control-plane serve`
- [ ] Health check: `curl -s http://127.0.0.1:3848/health`
- [ ] Optional: depends_on mcp
- [ ] Add `thegent_config_resolve` tool: params `tenant_id`, `keys`; returns resolved config
- [ ] Uses `get_config_provider().resolve()`
- [ ] `mcp_up` starts mcp + proxy + control-plane
- [ ] MCP tool `thegent_config_resolve` returns config
- [ ] `thegent_cp_config_resolves_total` (counter)
- [ ] `thegent_cp_config_resolve_duration_seconds` (histogram)
- [ ] `thegent_cp_fallback_total` (counter, in CLI)
- [ ] Span `config.resolve` with attributes: tenant_id, source (cp|env)
- [ ] Span `tenant.catalog.get` when tenant lookup
- [ ] Log config mutations (Phase 4+ when mutation API exists)
- [ ] Structured JSON logs with tenant_id, request_id
- [ ] Metrics exposed when `THGENT_OTEL_CONSOLE=1` or Prometheus endpoint
- [ ] Traces visible in OTel collector
| File | Phases |
|------|--------|
| `src/thegent/config_provider.py` (new) | 1, 2, 3, 6 |
| `src/thegent/control_plane/` (new) | 2, 4, 5, 6 |
| `src/thegent/cli_impl.py` | 1, 3, 4 |
| `src/thegent/cli.py` | 1, 3, 4 |
| `src/thegent/main.py` | 2, 3, 5 |
| `src/thegent/mcp_server.py` | 5 |
| `src/thegent/config.py` | 1 (optional: extend) |
| `process-compose.yaml` | 5 |
| `tests/` | 1, 2, 3, 4 |
| Phase | Unit | Integration |
|-------|------|-------------|
| 1 | EnvConfigProvider.resolve, get_tenant_config | run_cmd with provider |
| 2 | CP resolve endpoint, health | `control-plane serve` + curl |
| 3 | Fallback logic, circuit breaker | run with CP up/down |
| 4 | Tenant catalog load, merge order | config show --tenant |
| 5 | MCP tool | mcp_up + tool call |
| 6 | Metrics, spans | OTel export |
- [ ] Create `src/thegent/infra/user_isolation.py`
- [ ] Implement `SystemUser` base class
- [ ] `uid`, `gid`, `username`, `home`, `shell`, `groups`
- [ ] `from_current()` classmethod (detect current user)
- [ ] `to_dict()` / `from_dict()` serialization
- [ ] Implement `AgentUser(SystemUser)` subclass
- [ ] `agent_id`, `workspace`, `capabilities` (set)
- [ ] Add platform detection utilities
- [ ] `detect_platform()` → "darwin" | "linux" | "windows"
- [ ] `get_current_user()` → SystemUser instance
- [ ] Unit tests: `tests/test_user_isolation.py`
- [ ] Test SystemUser creation
- [ ] Test AgentUser capabilities
- [ ] Test platform detection
- [ ] Create `src/thegent/infra/os_user_manager.py`
- [ ] Implement `create_os_user()` for macOS/Linux
- [ ] macOS: `dscl` commands or `useradd` wrapper
- [ ] Linux: `useradd -r -s /bin/false`
- [ ] Create home directory: `/var/lib/thegent/agents/{username}`
- [ ] Set permissions: `chown {username}:{username}`
- [ ] Implement `delete_os_user()` for cleanup
- [ ] Add error handling (permission denied, user exists)
- [ ] Unit tests: `tests/test_os_user_manager.py`
- [ ] Test user creation (requires root, skip in CI)
- [ ] Test user deletion
- [ ] Test error cases
- [ ] Extend `os_user_manager.py` for Windows
- [ ] Implement `create_os_user_windows()`
- [ ] Use `New-LocalUser` PowerShell cmdlet
- [ ] Create home: `C:\ProgramData\thegent\agents\{username}`
- [ ] Set permissions via `icacls`
- [ ] Implement `delete_os_user_windows()`
- [ ] Use `Remove-LocalUser` PowerShell cmdlet
- [ ] Add Windows-specific error handling
- [ ] Unit tests: `tests/test_os_user_manager_windows.py`
- [ ] Test user creation (requires admin, skip in CI)
- [ ] Test user deletion
- [ ] Create `src/thegent/infra/user_pool.py`
- [ ] Implement `AgentUserPool` class
- [ ] `__init__(pool_size: int, base_path: Path)`
- [ ] `acquire(agent_id: str) -> SystemUser`
- [ ] `release(user: SystemUser)`
- [ ] `_create_pool()` — pre-create OS users
- [ ] Round-robin or least-used assignment
- [ ] Add pool overflow handling (create on-demand)
- [ ] Add pool cleanup on shutdown
- [ ] Unit tests: `tests/test_user_pool.py`
- [ ] Test pool acquisition/release
- [ ] Test overflow handling
- [ ] Test cleanup
- [ ] Update `src/thegent/agents/base.py`
- [ ] Add `isolation_mode: Literal["subuser", "osuser", "docker"]` to `AgentRunner`
- [ ] Update `DirectAgentRunner.run()`
- [ ] Check `isolation_mode`
- [ ] If `osuser`: acquire user from pool, run as that user
- [ ] If `subuser`: use current user, create `AgentUser` wrapper
- [ ] If `docker`: delegate to Docker runner (future)
- [ ] Add `_run_as_user()` helper method
- [ ] macOS/Linux: `subprocess.run(..., user=username)`
- [ ] Windows: `subprocess.run(..., runas=username)` or `runas.exe`
- [ ] Update `CodexProxyRunner` similarly
- [ ] Integration tests: `tests/test_agent_runner_isolation.py`
- [ ] Test subuser mode
- [ ] Test osuser mode (requires root/admin, skip in CI)
- [ ] Test user switching
- [ ] Add to `src/thegent/config.py`:
- [ ] Add to `~/.thegent/config.yaml`:
- [ ] Add CLI flag: `thegent run --isolation-mode {subuser|osuser|docker}`
- [ ] Environment variable: `THGENT_ISOLATION_MODE=osuser`
- [ ] Documentation: `docs/guides/USER_ISOLATION.md`
- [ ] Create `src/thegent/infra/shell_detection.py`
- [ ] `get_preferred_shell(platform, context)` → "bash" | "pwsh" | "wsl-bash"
- [ ] Contexts: `hooks`, `agent`, `os_admin`, `desktop`
- [ ] Windows: prefer WSL2 bash for hooks/agent if available; pwsh for os_admin/desktop
- [ ] Add `THGENT_AGENT_SHELL` config (bash | pwsh | wsl-bash) to config
- [ ] Create `docs/reference/POSIX_PWSH_SHELL_STRATEGY.md` (shell selection matrix, config)
- [ ] Unit tests: `tests/test_shell_detection.py`
- [ ] Update `src/thegent/orchestration/edit_lease.py` (existing)
- [ ] Add `tenant_id: str` field to `EditLease`
- [ ] Format: `"user"` or `"agent-{id}"`
- [ ] Update `acquire()` to check tenant conflicts
- [ ] Read leases: multiple tenants OK
- [ ] Write leases: only one tenant
- [ ] User can break agent leases (priority)
- [ ] Add `release_by_tenant(tenant_id: str)` for cleanup
- [ ] Update lease registry to track tenants
- [ ] Unit tests: `tests/test_tenant_aware_lease.py`
- [ ] Test user priority
- [ ] Test agent-agent conflicts
- [ ] Test multi-reader
- [ ] Create `src/thegent/infra/user_activity.py`
- [ ] Implement `UserActivityDetector` abstract base
- [ ] Implement `macOSUserActivityDetector`
- [ ] Use `CGEventSourceSecondsSinceLastEventType()` (CoreGraphics)
- [ ] Check keyboard, mouse, tablet events
- [ ] Implement `LinuxUserActivityDetector`
- [ ] X11: `XScreenSaverQueryInfo()` (if X11)
- [ ] systemd: `loginctl show-user {username}` (if systemd)
- [ ] Fallback: parse `/proc/{pid}/stat` for last CPU time
- [ ] Implement `WindowsUserActivityDetector`
- [ ] Use `GetLastInputInfo()` (User32.dll via ctypes)
- [ ] Add `is_user_active(threshold_seconds: float) -> bool`
- [ ] Unit tests: `tests/test_user_activity.py`
- [ ] Mock platform APIs
- [ ] Test threshold logic
- [ ] Create `src/thegent/infra/desktop_coordinator.py`
- [ ] Implement `DesktopAutomationCoordinator`
- [ ] `_active_automation: Optional[str]` (agent_id)
- [ ] `_lock: threading.Lock`
- [ ] `request_automation(agent_id: str) -> bool`
- [ ] Check user activity (via `UserActivityDetector`)
- [ ] Check existing automation lock
- [ ] Acquire lock if available
- [ ] `release_automation(agent_id: str)`
- [ ] `wait_for_user_idle(idle_seconds: float) -> bool`
- [ ] Add timeout handling (auto-release after N seconds)
- [ ] Unit tests: `tests/test_desktop_coordinator.py`
- [ ] Test user activity blocking
- [ ] Test lock acquisition/release
- [ ] Test timeout
- [ ] Update `src/thegent/orchestration/concurrency_controller.py` (existing)
- [ ] Add tenant-aware limits:
- [ ] Update `acquire()` to check tenant-specific limits
- [ ] Count processes per tenant
- [ ] Check tenant limit + total limit
- [ ] Add `_count_processes(tenant_pattern: str) -> int`
- [ ] Parse process metadata (owner, agent_id)
- [ ] Unit tests: `tests/test_tenant_concurrency.py`
- [ ] Test user limit enforcement
- [ ] Test agent limit enforcement
- [ ] Test total limit enforcement
- [ ] Create `src/thegent/infra/conflict_resolver.py`
- [ ] Implement `ConflictResolver` class
- [ ] `resolve_file_conflict(tenant_a: str, tenant_b: str, file: Path) -> str`
- [ ] Policy: user priority → return "user"
- [ ] Policy: FIFO → return first tenant
- [ ] `resolve_resource_conflict(...) -> str`
- [ ] `resolve_automation_conflict(...) -> str`
- [ ] Add conflict event logging
- [ ] Log to `~/.thegent/logs/conflicts.jsonl`
- [ ] Add conflict metrics (count by type)
- [ ] Unit tests: `tests/test_conflict_resolver.py`
- [ ] Test user priority policy
- [ ] Test FIFO policy
- [ ] Test logging
- [ ] Add to config:
- [ ] Wire coordinators into `AgentRunner`
- [ ] Check user activity before automation
- [ ] Acquire automation lock
- [ ] Use tenant-aware leases
- [ ] Add CLI flags: `--max-user-processes`, `--max-agent-processes`
- [ ] Documentation: `docs/guides/MULTI_TENANT_COORDINATION.md`
- [ ] Update hook dispatcher to use `get_preferred_shell()` on Windows
- [ ] Invoke hooks via `bash -c` or `wsl bash -c` when WSL2 available
- [ ] Add `hooks/lib/pwsh_adapters.ps1` for Windows-native hook logic (optional)
- [ ] Document: hooks call `pwsh -File` for Windows-specific blocks when needed
- [ ] Create `src/thegent/infra/desktop_automation/`
- [ ] Create `base.py` with `DesktopAutomationProvider` abstract class
- [ ] `click(element: UIElement) -> bool`
- [ ] `type_text(element: UIElement, text: str) -> bool`
- [ ] `find_element(selector: str) -> Optional[UIElement]`
- [ ] `screenshot(region: Optional[dict] = None) -> bytes`
- [ ] `wait_for_idle(seconds: float) -> bool`
- [ ] Create `UIElement` dataclass
- [ ] `selector: str`, `name: str`, `role: str`, `bounds: dict`
- [ ] Create factory: `get_provider() -> DesktopAutomationProvider`
- [ ] Auto-detect platform, return appropriate provider
- [ ] Unit tests: `tests/test_desktop_automation_base.py`
- [ ] Test abstract interface
- [ ] Test factory
- [ ] Create `src/thegent/infra/desktop_automation/macos.py`
- [ ] Implement `macOSAutomationProvider(DesktopAutomationProvider)`
- [ ] Implement `click()` via AppleScript
- [ ] `tell application "System Events" to click {element}`
- [ ] Implement `type_text()` via AppleScript
- [ ] `tell application "System Events" to keystroke "{text}"`
- [ ] Implement `find_element()` via AppleScript
- [ ] `tell application "System Events" to get {selector}`
- [ ] Implement `screenshot()` via `screencapture` command
- [ ] Add error handling (permission denied, element not found)
- [ ] Add dependency: `py-applescript` or subprocess wrapper
- [ ] Unit tests: `tests/test_macos_automation.py`
- [ ] Mock AppleScript execution
- [ ] Test error cases
- [ ] Create `src/thegent/infra/desktop_automation/windows.py`
- [ ] Implement `WindowsAutomationProvider(DesktopAutomationProvider)`
- [ ] Use `pywinauto` or `uiautomation` library
- [ ] Implement `click()` via UIA
- [ ] `element.click()` or `element.invoke()`
- [ ] Implement `type_text()` via UIA
- [ ] `element.type_keys(text)`
- [ ] Implement `find_element()` via UIA
- [ ] `Application().window(title="...").control(...)`
- [ ] Implement `screenshot()` via `PIL.ImageGrab` or `mss`
- [ ] Add error handling
- [ ] Add dependency: `pywinauto` or `uiautomation`
- [ ] Unit tests: `tests/test_windows_automation.py`
- [ ] Mock UIA elements
- [ ] Test error cases
- [ ] Create `src/thegent/infra/desktop_automation/linux.py`
- [ ] Implement `LinuxAutomationProvider(DesktopAutomationProvider)`
- [ ] Use `pyatspi` or `dogtail` library
- [ ] Implement `click()` via AT-SPI
- [ ] `element.doAction(0)` (action 0 = click)
- [ ] Implement `type_text()` via AT-SPI
- [ ] `element.setText(text)` or keyboard input
- [ ] Implement `find_element()` via AT-SPI
- [ ] Traverse accessibility tree, match by name/role
- [ ] Implement `screenshot()` via `mss` or `PIL.ImageGrab`
- [ ] Add error handling
- [ ] Add dependency: `pyatspi` or `dogtail`
- [ ] Unit tests: `tests/test_linux_automation.py`
- [ ] Mock AT-SPI elements
- [ ] Test error cases
- [ ] Create integration tests: `tests/test_desktop_automation_integration.py`
- [ ] Test on macOS (requires Accessibility permission)
- [ ] Test on Linux (requires AT-SPI)
- [ ] Test on Windows (requires UIA Access)
- [ ] Test error handling (permission denied, element not found)
- [ ] Test performance (click latency, screenshot speed)
- [ ] Add CI/CD setup (skip on platforms without permissions)
- [ ] Create `docs/guides/DESKTOP_AUTOMATION.md`
- [ ] Platform setup (permissions)
- [ ] Usage examples
- [ ] Troubleshooting
- [ ] Create example workflows:
- [ ] `examples/desktop_automation/click_button.py`
- [ ] `examples/desktop_automation/fill_form.py`
- [ ] Add to `pyproject.toml` dependencies:
- [ ] `py-applescript` (macOS, optional)
- [ ] `pywinauto` (Windows, optional)
- [ ] `pyatspi` (Linux, optional)
- [ ] Update `src/thegent/mcp_server.py`
- [ ] Register desktop automation tools:
- [ ] Add coordination hooks (check user activity, acquire lock)
- [ ] Add error handling and logging
- [ ] Unit tests: `tests/test_mcp_desktop_automation.py`
- [ ] Add MCP resource: `thegent://desktop-automation/status`
- [ ] Returns: `{"active": bool, "agent_id": str | None, "user_active": bool}`
- [ ] Add MCP resource: `thegent://desktop-automation/permissions`
- [ ] Returns: `{"macos_accessibility": bool, "windows_uia": bool, "linux_atspi": bool}`
- [ ] Update MCP server to serve these resources
- [ ] Unit tests: `tests/test_mcp_desktop_resources.py`
- [ ] Create `examples/mcp_desktop_automation/`
- [ ] Example: Click button workflow
- [ ] Example: Fill form workflow
- [ ] Example: Multi-step automation workflow
- [ ] Documentation: `docs/guides/MCP_DESKTOP_AUTOMATION.md`
- [ ] Test user isolation on macOS, Linux, Windows
- [ ] Test multi-tenant coordination scenarios
- [ ] Test desktop automation on all platforms
- [ ] Test MCP integration end-to-end
- [ ] Performance benchmarking
- [ ] Fix platform-specific bugs
- [ ] Update `README.md` with cross-platform support
- [ ] Create migration guide: `docs/guides/MIGRATION_CROSS_PLATFORM.md`
- [ ] Update `CHANGELOG.md`
- [ ] Create troubleshooting guide: `docs/guides/TROUBLESHOOTING.md`
- [ ] Update API documentation
- [ ] Version bump
- [ ] Release notes
- [ ] CI/CD pipeline updates (Windows/Linux runners)
- [ ] Package distribution (Windows wheels, Linux packages)
- [ ] Create `RemoteHost` dataclass and `load_remote_hosts()` in `src/thegent/infra/remote_hosts.py`
- [ ] Add `~/.thegent/remote_hosts.yaml` schema and validation (Pydantic)
- [ ] Path mapping: resolve local path to remote path per host config
- [ ] Unit tests: `tests/test_remote_hosts.py`
- [ ] Implement `run_remote(host, cwd, prompt, agent)` via paramiko or subprocess+ssh
- [ ] Implement `ps_remote(host)`, `logs_remote(host, session_id)`, `stop_remote`, `wait_remote`
- [ ] Add `--remote HOST` to `run`, `bg`, `ps`, `logs`, `stop`, `wait` in CLI
- [ ] Stream output back to client
- [ ] Unit tests: `tests/test_remote_execution.py`
- [ ] Document in `docs/guides/HYBRID_ENV_QUICK_START.md` and CLI help
- [ ] Add remote_hosts.yaml example to docs
- [ ] Add `isolation_mode=systemd-scope` option for Linux
- [ ] Implement `systemd-run --scope -p MemoryMax=... -p CPUQuota=... -- thegent run ...`
- [ ] Config: `resource_limits.memory_mb`, `resource_limits.cpu_percent`
- [ ] Unit tests: `tests/test_systemd_scope.py` (mock or skip if no systemd)
- [ ] Add `isolation_mode=job-object` option for Windows
- [ ] Implement `CreateJobObject`, `AssignProcessToJobObject` with memory/CPU limits
- [ ] Use ctypes or pywin32; fallback to sub-user if unavailable
- [ ] Unit tests: `tests/test_windows_job_objects.py` (Windows only)
- [ ] Document launchd per-agent option (future)
- [ ] Add `resource_limits` config schema for parity; no implementation yet
- [ ] Wire P7.1, P7.2 into AgentRunner based on `isolation_mode`
- [ ] Update `docs/reference/AGENT_OS_PRINCIPALS_DEPTH.md` with implementation status
- [ ] Add troubleshooting for "systemd not found", "Job Object failed"
- [ ] Define error code schema (THGENT-E001..E099)
- [ ] Add structured error types with codes, causes, doc links
- [ ] Create `docs/reference/ERROR_CODES.md`
- [ ] Wire into desktop automation, remote, hooks
- [ ] Add `thegent diagnose permissions` (accessibility, UIA, AT-SPI)
- [ ] Add `thegent diagnose remote HOST` (SSH, path mapping, version)
- [ ] Add `thegent diagnose element SEL` (find attempt, tree snippet)
- [ ] Add `thegent diagnose shell` (shell selection for all contexts)
- [ ] Create `docs/guides/TROUBLESHOOTING_DESKTOP_AUTOMATION.md`
- [ ] Create `docs/guides/TROUBLESHOOTING_REMOTE.md`
- [ ] Create `docs/guides/TROUBLESHOOTING_HOOKS.md`
- [ ] Cross-link from error messages
- [ ] Add circuit breaker for desktop provider (tenacity/pybreaker)
- [ ] Add circuit breaker for remote host connections
- [ ] Implement retry/fallback chains (automation, remote, element find)
- [ ] Integrate with existing retry system (WP-2002)
- [ ] SSH connection pooling for remote (`ps`, `logs`, `stop` reuse)
- [ ] Add `thegent warmup` + `warmup_on_start` config
- [ ] Element cache TTL + event-based invalidation
- [ ] OTel spans + trace_id propagation for automation/remote
- [ ] Add `--headless` flag and `THGENT_HEADLESS=1`
- [ ] Skip user activity check when headless; mock UserActivityDetector
- [ ] Create `docs/guides/HEADLESS_AND_CI.md`
- [ ] Multi-monitor, high-DPI, locked-screen detection (optional)
- [ ] WSL2 path translation (`/mnt/c/` ↔ `C:\`) for remote
- [ ] Document FreeBSD as unsupported; add platform detection
- [ ] Wayland notes in Linux provider docs
| Risk | Mitigation |
|------|-----------|
| **OS user creation requires root/admin** | Make it opt-in (sub-user default), document requirements |
| **Desktop automation permissions** | Clear documentation, permission check utilities |
| **Platform API differences** | Abstract layer, platform-specific tests |
| **Performance overhead** | Benchmarking, optimization, caching |
| **User experience disruption** | User activity detection, coordination locks |
- [ ] Agents can run with sub-user or OS user isolation
- [ ] Multi-tenant coordination prevents conflicts
- [ ] Desktop automation works on macOS, Linux, Windows
- [ ] MCP tools expose desktop automation
- [ ] Remote compute (`thegent run --remote`) works
- [ ] OS-level primitives (systemd scope, Job Objects) available
- [ ] Diagnostic commands and runbooks available
- [ ] All tests pass on all platforms
- [ ] Documentation is complete
- [ ] Evaluate CUA MCP server (`libs/mcp-server`)
- [ ] Test CUA Computer SDK (`cua-computer`)
- [ ] Compare CUA vs native providers (performance, features)
- [ ] Decision: Use CUA, native, or hybrid approach
- [ ] Review advanced patterns document
- [ ] Select patterns to implement (based on requirements)
- [ ] Integrate selected patterns into implementation
- [ ] Extend ConcurrencyController with tenant limits (Phase 2)
- [ ] Extend EditLeaseManager with tenant awareness (Phase 2)
- [ ] Integrate automation retry with existing retry system (Phase 4)
- [ ] Add automation events to run registry (Phase 4)
- [ ] Add OTel spans for automation (Phase 4)
| Repo | Stars | Purpose | Use for thegent |
|------|-------|---------|-----------------|
| [wisdgod/cursor-api](https://github.com/wisdgod/cursor-api) | 624 | Rust server exposing **OpenAI-compatible** API to Cursor backend | **Primary** – add Cursor HTTP backend |
| [eisbaw/cursor_api_demo](https://github.com/eisbaw/cursor_api_demo) | 25 | Python reverse-engineered client (HTTP/2, ConnectRPC, protobuf) | **Secondary** – native Python client option |
| [Jordan-Jarvis/cursor-grpc](https://github.com/Jordan-Jarvis/cursor-grpc) | 80 | Proto definitions only (server_chat, server_stream, etc.) | **Reference** – protocol docs |
| [zhifac/code_of_c_u_r_s_o_r](https://github.com/zhifac/code_of_c_u_r_s_o_r) | 3 | Chinese docs on tokenizer/ControlProvider | **Low value** – no chat API |
| Task | Description |
|------|-------------|
| 1.1 | Add `cursor-api` to provider registry (alongside cursor-agent) |
| 1.2 | Config: `THGENT_CURSOR_API_URL` (default `http://127.0.0.1:3000`) |
| 1.3 | Implement `CursorApiRunner` – HTTP client to `/v1/chat/completions`, `/v1/models` |
| 1.4 | Model scraper: `GET /v1/models` → merge into catalog |
| 1.5 | Routing: `cursor-api` as proxy backend; `cursor-agent` as direct CLI |
| 1.6 | Fallback: if cursor-api unreachable, use cursor-agent CLI |
| Task | Description |
|------|-------------|
| 2.1 | Extract auth logic (SQLite token reader) from cursor_api_demo |
| 2.2 | Implement HTTP/2 + ConnectRPC client for `StreamUnifiedChatWithTools` |
| 2.3 | Handle protobuf encoding/decoding (cursor_proper_protobuf, cursor_streaming_decoder) |
| 2.4 | Add `cursor-native` provider that uses this client |
| Criterion | cursor-api (Phase 1) | cursor_api_demo (Phase 2) |
|-----------|---------------------|---------------------------|
| Effort | Low | High |
| Deps | httpx/requests | HTTP/2, ConnectRPC, protobuf |
| External process | Yes (cursor-api server) | No |
| Auth | Bearer (user provides) | SQLite auto-read |
| OpenAI compat | Yes | No (custom protocol) |
| Model list | `/v1/models` | Custom |
| Maintenance | cursor-api upstream | Our fork/port |
| Project | Pattern | Location |
|---------|---------|----------|
| **API/argisroute** | `X-RateLimit-*` headers, metadata in responses | wrappers, rate limiting |
| **API/docs** | `metadata: { model, provider, processing_time_ms, token_usage }` | AGENT_SECURITY_COMPREHENSIVE_PART2 |
| **trace** | cliproxy config (routing, model_mappings) | `trace/backend/configs/cliproxy.yaml` |
| **CLIProxyAPI** | Bifrost integration, provider routing | API/research/CLIProxyAPI |
| Layer | Option | Pros | Cons |
|-------|--------|------|-----|
| **CLIProxyAPIPlus** | Add headers to proxied response | Single source; all clients benefit | Requires proxy modification |
| **CLIProxyAPIPlus** | Prefix first stream chunk with `<!-- model: X \| provider: Y \| latency_ms: Z -->` | Visible in stream; no client change | Pollutes content when debug on |
| **thegent** | Log to stderr when `--debug` | No proxy change | Only when thegent is caller |
| **LiteLLM** | `litellm.callbacks` or response metadata | Rich metrics | Only when LiteLLM is used |
| Phase | Task | Status |
|-------|------|--------|
| 1 | Add `--debug` to `thegent run`, `thegent bg`; set `THGENT_DEBUG=1`; proxy gets `-debug` when env set | ✓ Done |
| 2 | CLIProxyAPIPlus: add `-debug` flag; when set, add response headers | Pending (fork; thegent already passes `-debug` when THGENT_DEBUG=1) |
| 3 | CLIProxyAPIPlus: optional response prefix `<!-- model: X \| provider: Y \| latency_ms: Z -->` when debug | Pending (fork) |
| 4 | Document in PROVIDER_SETUP_GUIDE, CLAUDE.md | ✓ Done |
| Metric | Source | Header |
|--------|--------|--------|
| model | Resolved model alias | `X-Response-Model` |
| provider | Provider name (minimax, glm, nim, etc.) | `X-Response-Provider` |
| latency_ms | Request latency | `X-Latency-Ms` |
| tps_1m | Rolling TPS from metrics | `X-TPS-1m` |
| cost_per_1k | From GET /v1/metrics/providers | `X-Cost-Per-1k` (optional) |
| # | Pillar | Plan | Phased WBS |
|---|--------|------|------------|
| 1 | **Dynamic model scraping** — Scrape models from every provider; expose for discovery/selection | §9 | §10.1 |
| 2 | **Distributed routing** — Model-first invocation; route to best available backend | §3–§5 | §10.2 |
| 3 | **Provider capability merging** — Antigravity + claude + gemini etc. as one logical pool | §11 | §10.3 |
| Model | Providers that can serve it |
|-------|-----------------------------|
| gemini-3-flash | gemini (direct), antigravity (proxy) |
| claude-sonnet-4 | claude (direct), codex (proxy), antigravity (proxy) |
| gemini-2.0-flash | gemini (direct), antigravity (proxy) |
| MiniMax-M2.5 | minimax (proxy only) |
| GLM-5 | glm (proxy only) |
| Provider | Backend | Models (examples) |
|----------|---------|-------------------|
| claude | direct | haiku, sonnet, opus, claude-haiku-4.5, claude-sonnet-4, ... |
| gemini | direct | gemini-2.0-flash, gemini-3-flash, gemini-3-pro-preview, ... |
| copilot | direct | claude-haiku-4.5, gpt-5, gemini-3-pro-preview, ... |
| codex | direct | gpt-5, gpt-5.3-codex, ... |
| cursor-agent | direct | gemini-3-flash, composer-1.5, ... (from cursor --list-models) |
| antigravity | proxy | gemini-3-flash, gemini-3-pro-high, claude-*, tstars2.0, ... |
| codex (proxy) | proxy | gpt-5-codex, claude-sonnet-4, ... |
| minimax | proxy | MiniMax-M2.5 |
| glm | proxy | GLM-5 |
| Provider | Scraping | Source |
|----------|----------|--------|
| cursor-agent | ✓ | `cursor agent --list-models` |
| copilot | ✓ | `copilot --help` → parse `--model` choices |
| codex | ✓ | `cursor agent --list-models` filtered |
| gemini | ✗ | Hardcoded defaults |
| claude | ✗ | Hardcoded defaults |
| antigravity | ✗ | Hardcoded defaults |
| minimax | ✗ | Hardcoded |
| glm | ✗ | Hardcoded |
| Provider | Adapter | Method | Fallback |
|----------|---------|--------|----------|
| cursor-agent | `cursor_adapter` | `cursor agent --list-models` | config defaults |
| copilot | `copilot_adapter` | `copilot --help` → regex choices | static list |
| codex | `codex_adapter` | cursor --list-models filtered, or codex --help | static list |
| gemini | `gemini_adapter` | `gemini --help` → -m/--model, or API | config default |
| claude | `claude_adapter` | `claude --help` → --model aliases | static list |
| antigravity | `proxy_adapter` | `GET {proxy}/v1/models` | config default |
| minimax | `proxy_adapter` | From proxy config openai-compatibility | static MiniMax-M2.5 |
| glm | `proxy_adapter` | From proxy config or native | static GLM-5 |
| Phase | Task ID | Description | Depends On |
|-------|---------|-------------|------------|
| 1.1 | S1.1 | Define `ModelScraper` interface and `CatalogView` schema | — |
| 1.1 | S1.2 | Implement `cursor_adapter`, `copilot_adapter`, `codex_adapter` (reuse existing logic) | S1.1 |
| 1.1 | S1.3 | Implement `proxy_adapter` for antigravity/minimax/glm (GET /v1/models or config) | S1.1 |
| 1.1 | S1.4 | Implement `gemini_adapter`, `claude_adapter` (--help or API) | S1.1 |
| 1.2 | S1.5 | Add cache layer (TTL 5–30 min, configurable) | S1.2–S1.4 |
| 1.2 | S1.6 | Merge adapter outputs into `CatalogView` (by_provider, by_model) | S1.5 |
| 1.3 | S1.7 | Wire `list_models_impl` to use scraped catalog; fallback to static on adapter failure | S1.6 |
| 1.3 | S1.8 | Add `thegent list-models --by-model` for unified view | S1.7 |
| 1.3 | S1.9 | MCP `thegent_list_models` returns scraped catalog | S1.7 |
| Phase | Task ID | Description | Depends On |
|-------|---------|-------------|------------|
| 2.1 | R1.1 | Define `ModelCatalog`, `Route`, `resolve_route(model_id, provider_hint?, policy?)` | — |
| 2.1 | R1.2 | Populate static catalog from `_PROXY_MODEL` and provider defaults | R1.1 |
| 2.1 | R1.3 | Add alias table (haiku→claude-haiku-4.5, sonnet→claude-sonnet-4, etc.) | R1.1 |
| 2.2 | R2.1 | Add CLI `-M ``<model>``` and `--provider` to `thegent run` | R1.2 |
| 2.2 | R2.2 | Model-first path: if `-M` without provider, call `resolve_route(model)` with prefer_direct | R2.1, R1.2 |
| 2.2 | R2.3 | MCP `thegent_run(model=..., provider=...)` with same semantics | R2.2 |
| 2.3 | R3.1 | Implement `run_with_failover(model, prompt, ...)` — retry next route on failure | R2.2 |
| 2.4 | R4.1 | Add `--routing prefer_direct | prefer_proxy | failover` (and config default) | R2.2 |
| Phase | Task ID | Description | Depends On |
|-------|---------|-------------|------------|
| 3.1 | M1.1 | Define capability merge rules: antigravity ∪ claude ∪ gemini ∪ codex ∪ copilot | R1.1 |
| 3.1 | M1.2 | Build overlap matrix: which models appear in which providers | S1.6, R1.2 |
| 3.1 | M1.3 | Canonicalize model IDs across providers (claude "sonnet" = codex "claude-sonnet-4" = antigravity "claude-sonnet-4") | R1.3 |
| 3.2 | M2.1 | Merge antigravity models into claude/gemini/codex capability sets for routing | M1.1, M1.2 |
| 3.2 | M2.2 | When resolving route for model X, consider all providers that serve X (not just primary) | R1.2, M2.1 |
| 3.3 | M3.1 | Discovery: `list-models --by-model` shows "claude-sonnet-4: claude, codex, antigravity" | S1.8, M1.2 |
| 3.3 | M3.2 | MCP catalog includes `by_model` with provider list per model | S1.9, M1.2 |
| Source | Method | Endpoint/Command | Response Format | Notes |
|--------|--------|------------------|-----------------|-------|
| **CLIProxyAPIPlus** | HTTP GET | `GET http://127.0.0.1:{port}/v1/models` | OpenAI-compatible `{data: [{id: "model-id", ...}]}` | Start proxy if not running; use `ensure_proxy_running()` |
| **Gemini** | CLI subprocess | `gemini --help` | stdout with `-m`/`--model` choices or usage | Parse regex for model names; fallback: config default |
| **Claude** | CLI subprocess | `claude --help` | stdout with `--model` aliases | Parse "haiku", "sonnet", "opus" + full IDs |
| **Cursor** | CLI subprocess | `cursor agent --list-models` | stdout, one model per line | Already used; filter by provider if needed |
| **Copilot** | CLI subprocess | `copilot --help` | stdout with `choices:` for `--model` | Regex: `"([a-zA-Z0-9.-]+)"` in model section |
| **Minimax** | Proxy config | Parse `~/.config/thegent/cliproxy-config.yaml` | `openai-compatibility[].models[].name` | Or from `~/.factory/config.json` custom_models |
| **GLM** | Proxy native | Proxy `/v1/models` or config | GLM-5 in proxy response | Native; no separate scrape if proxy lists it |
| Phase | Task ID | Description | Depends On |
|-------|---------|-------------|------------|
| S-A | SA1 | Implement `proxy_adapter`: GET `{base}/v1/models`, parse `data[].id` | — |
| S-A | SA2 | Implement `gemini_adapter`: `gemini --help` subprocess, regex for models | — |
| S-A | SA3 | Implement `claude_adapter`: `claude --help` subprocess, regex for `--model` | — |
| S-A | SA4 | Implement `cursor_adapter`, `copilot_adapter` (reuse existing _list_* logic) | — |
| S-A | SA5 | Implement `minimax_adapter`, `glm_adapter` (proxy config or static) | SA1 |
| S-B | SB1 | Add cache layer (file or in-memory, TTL configurable) | SA1–SA5 |
| S-B | SB2 | Merge adapter outputs → `CatalogView` (by_provider, by_model) | SB1 |
| S-B | SB3 | Wire `ModelCatalog` to use scraped data; merge with static fallback | SB2 |
| S-C | SC1 | `list_models_impl` returns scraped catalog; `list-models --by-model` uses it | SB3 |
| S-C | SC2 | MCP `thegent_list_models` returns full catalog (by_provider, by_model) | SC1 |
| S-C | SC3 | MCP `thegent_run(agent?, model?, prompt)` — model-first when model set, agent optional | SC1 |
- [ ] All sections filled
- [ ] All examples included
- [ ] All links working
- [ ] All cross-references added
- [ ] Information correct
- [ ] Code examples work
- [ ] Links valid
- [ ] Cross-references accurate
- [ ] Style consistent
- [ ] Terminology consistent
- [ ] Format consistent
- [ ] Structure consistent
- [ ] Performance considerations included
- [ ] Best practices followed
- [ ] Efficiency optimized
- [ ] Resources optimized
- [ ] **Breadth**: All topics covered
- [ ] **Depth**: Deep dive into each topic
- [ ] **Optimization**: Performance considerations included
- [ ] **Robustness**: Error handling and edge cases covered
- [ ] **Practicality**: Real-world examples included
- [ ] **Intuitiveness**: Clear structure and navigation
- [ ] **Holistic**: Cross-references and integration points
- [ ] **Harmonious**: Consistent style and patterns
- [ ] **Code Examples**: Working code examples included
- [ ] **Diagrams**: Visual aids where helpful
- [ ] **Cross-References**: Links to related docs
- [ ] **Master Index**: Added to master index
- [ ] **Review**: Technical and editorial review complete
- [ ] Expand each concept (Supermemory, Pareto Routing, Economic Governance, MAIF, Simulation) into full research doc
- [ ] Add implementation details, code examples, integration points
- [ ] Add performance benchmarks, cost analysis
- [ ] Add troubleshooting, edge cases
- [ ] Cross-reference with WBS, architecture docs
- [ ] Add decision records (ADRs) for each concept
- [ ] Create separate deep-dive docs for each major concept
- [ ] Organize by topic/feature area
- [ ] Extract actionable items into plans
- [ ] Link to implementation status
- [ ] Add decision rationale
- [ ] Create follow-up action items
- [ ] Cross-reference with related docs
- [ ] Add timeline/chronology
- [ ] Extract todos/plans into structured format
- [ ] Consolidate into single comprehensive research doc
- [ ] Expand each platform (macOS, Linux, Windows, WSL) with deep dives
- [ ] Add implementation patterns, code examples
- [ ] Add testing strategies per platform
- [ ] Add performance benchmarks per platform
- [ ] Add troubleshooting guides per platform
- [ ] Cross-reference with implementation plans
- [ ] Create platform-specific quick start guides
- [ ] Expand migration strategy with detailed steps
- [ ] Add performance comparison (shell vs Rust)
- [ ] Add migration timeline with milestones
- [ ] Add rollback strategies
- [ ] Add testing requirements
- [ ] Add code examples for each hook
- [ ] Cross-reference with implementation plan
- [ ] Add risk mitigation strategies
- [ ] Consolidate into single comprehensive audit
- [ ] Expand each library replacement with rationale
- [ ] Add migration guides per library
- [ ] Add performance benchmarks
- [ ] Add compatibility matrices
- [ ] Add rollback procedures
- [ ] Cross-reference with implementation plans
- [ ] Create library-specific migration guides
- [ ] Consolidate into single comprehensive research doc
- [ ] Expand each platform with deep dive
- [ ] Add comparison matrix
- [ ] Add integration strategies
- [ ] Add cost analysis
- [ ] Add performance benchmarks
- [ ] Add use case mappings
- [ ] Cross-reference with implementation plans
- [ ] Consolidate into single comprehensive FastMCP guide
- [ ] Expand each component (middleware, storage, telemetry, etc.)
- [ ] Add implementation examples
- [ ] Add architecture diagrams
- [ ] Add API reference
- [ ] Add troubleshooting guides
- [ ] Cross-reference with implementation plans
- [ ] Create developer guide
- [ ] Expand swarm architecture
- [ ] Add scheduling algorithms deep dive
- [ ] Add process automation patterns
- [ ] Add performance optimization strategies
- [ ] Add failure handling
- [ ] Cross-reference with implementation plans
- [ ] Create swarm developer guide
- [ ] Add implementation patterns
- [ ] Add code examples
- [ ] Add performance benchmarks
- [ ] Add cache invalidation strategies
- [ ] Add monitoring/observability
- [ ] Cross-reference with optimization plans
- [ ] Create caching guide
- [ ] Add resource management patterns
- [ ] Add monitoring strategies
- [ ] Add optimization techniques
- [ ] Add troubleshooting guides
- [ ] Cross-reference with process optimization plan
- [ ] Create resource management guide
- [ ] Review each seed for viability
- [ ] Expand viable seeds into full research/plan docs
- [ ] Add implementation feasibility analysis
- [ ] Add cost/benefit analysis
- [ ] Link to WBS if applicable
- [ ] Create seed → plan → implementation pipeline
- [ ] Archive non-viable seeds with rationale
- [ ] Expand implementation details
- [ ] Add code examples
- [ ] Add integration points
- [ ] Add data schema
- [ ] Add API reference
- [ ] Add usage examples
- [ ] Cross-reference with related systems
- [ ] Create developer guide
- [ ] Complete architecture design
- [ ] Add implementation timeline
- [ ] Add technical specifications
- [ ] Add integration points
- [ ] Add testing strategy
- [ ] Add deployment plan
- [ ] Cross-reference with related plans
- [ ] Create implementation guide
- [ ] Consolidate into single comprehensive plan
- [ ] Add implementation timeline
- [ ] Add testing requirements
- [ ] Add rollback procedures
- [ ] Cross-reference with guides
- [ ] Create unified implementation guide
- [ ] Expand implementation details
- [ ] Add platform-specific guides
- [ ] Add testing strategies
- [ ] Add deployment procedures
- [ ] Cross-reference with research
- [ ] Create unified implementation guide
- [ ] Expand optimization strategies
- [ ] Add code examples
- [ ] Add performance benchmarks
- [ ] Add migration guides
- [ ] Cross-reference with research
- [ ] Create optimization guide
- [ ] Expand architecture details
- [ ] Add code examples
- [ ] Add migration timeline
- [ ] Add testing requirements
- [ ] Add performance comparison
- [ ] Cross-reference with research
- [ ] Create migration guide
- [ ] Consolidate into single comprehensive guide
- [ ] Remove duplication
- [ ] Add cross-references
- [ ] Add unified index
- [ ] Add quick start
- [ ] Add troubleshooting section
- [ ] Create master shell guide
- [ ] Consolidate into single comprehensive guide
- [ ] Add unified navigation
- [ ] Remove duplication
- [ ] Add cross-references
- [ ] Create master cross-platform guide
- [ ] Consolidate into single comprehensive migration guide
- [ ] Add unified navigation
- [ ] Add migration paths
- [ ] Add rollback procedures
- [ ] Cross-reference with plans
- [ ] Create master migration guide
- [ ] Expand API documentation
- [ ] Add code examples
- [ ] Add error handling
- [ ] Add versioning info
- [ ] Add deprecation notices
- [ ] Create unified API reference
- [ ] Expand architecture details
- [ ] Add diagrams
- [ ] Add component descriptions
- [ ] Add integration points
- [ ] Add data flows
- [ ] Create unified architecture reference
- [ ] Expand audit findings
- [ ] Add remediation plans
- [ ] Add implementation status
- [ ] Add follow-up actions
- [ ] Cross-reference with plans
- [ ] Create unified audit report
- [ ] Add implementation recommendations
- [ ] Add integration strategies
- [ ] Add cost analysis
- [ ] Add performance benchmarks
- [ ] Cross-reference with plans
- [ ] Create implementation guide
- [ ] Consolidate governance research
- [ ] Expand policy framework
- [ ] Add implementation strategies
- [ ] Add compliance requirements
- [ ] Cross-reference with plans
- [ ] Create governance guide
- [ ] Consolidate cost research
- [ ] Add cost optimization strategies
- [ ] Add routing algorithms
- [ ] Add budget management
- [ ] Cross-reference with plans
- [ ] Create cost management guide
- [ ] Category 1: Research Fragments (10 items)
- [ ] Category 2: Seed Files (2 items)
- [ ] Category 3: Incomplete Plans (5 items)
- [ ] Category 4: Fragmented Guides (3 items)
- [ ] Category 5: Reference Docs (2 items)
- [ ] Category 6: Audit Docs (4 items)
- [ ] Category 7: Specialized Research (3 items)
| Phase | Description | Duration | Effort | Priority |
|-------|-------------|----------|--------|----------|
| **Phase A** | Documentation Audit & Categorization | 2 hrs | 4 agent-hrs | P1 |
| **Phase B** | Guides Consolidation (42 files) | 4 hrs | 8 agent-hrs | P1 |
| **Phase C** | Reference Consolidation (84 files) | 6 hrs | 12 agent-hrs | P1 |
| **Phase D** | Checklists Consolidation (1 file) | 1 hr | 2 agent-hrs | P2 |
| **Phase E** | Work Stream Entry Creation | 3 hrs | 6 agent-hrs | P1 |
| **Phase F** | Implementation Sprint 1 (P1 items) | 8 hrs | 16 agent-hrs | P1 |
| **Phase G** | Implementation Sprint 2 (P2 items) | 12 hrs | 24 agent-hrs | P2 |
| Task | ID | Description | Depends | Output |
|------|-----|-------------|---------|--------|
| A.1.1 | DOC-AUDIT-001 | Count and categorize docs/guides/*.md | — | Inventory list |
| A.1.2 | DOC-AUDIT-002 | Count and categorize docs/reference/*.md | — | Inventory list |
| A.1.3 | DOC-AUDIT-003 | Count and categorize docs/checklists/*.md | — | Inventory list |
| A.1.4 | DOC-AUDIT-004 | Identify orphaned/duplicate docs | A.1.1, A.1.2, A.1.3 | Duplicates report |
| A.1.5 | DOC-AUDIT-005 | Assess docs needing EXTENSION_SUMMARY | A.1.4 | Gap analysis |
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
| Pattern | Description | Action |
|---------|-------------|--------|
| `*.md` | Canonical docs | Keep as-is |
| `*_COMPLETE.md` | Completion reports | Consolidate to single file |
| `*_SUMMARY.md` | Summary docs | Merge to parent |
| `*_EXPANDED.md` | Extended versions | Merge to base |
| `*_GUIDE.md` | How-to guides | Keep, standardize format |
| `*_REFERENCE.md` | Reference docs | Keep, add to index |
| `*_PLAN.md` | Planning docs | Archive to docs/plans/ |
| Task | ID | File | Action | Ext. Summary |
|------|-----|------|--------|--------------|
| B.1.1 | GUIDE-ARCH-001 | AGENT_DEBUGGING_AND_REMEDIATION_GUIDE.md | Extend | ✅ |
| B.1.2 | GUIDE-ARCH-002 | AGENT_INSTRUCTIONS_THEGENT.md | Extend | ✅ |
| B.1.3 | GUIDE-ARCH-003 | architecture-enforcement.md | Extend | ✅ |
| B.1.4 | GUIDE-ARCH-004 | BKM_IMPLEMENTATION_GUIDES.md | Extend | ✅ |
| B.1.5 | GUIDE-ARCH-005 | AUTOMATED_DEMOS.md | Create EXT | ✅ |
| Task | ID | File | Action | Ext. Summary |
|------|-----|------|--------|--------------|
| B.2.1 | GUIDE-XP-001 | CROSS_PLATFORM_COMPLETE.md | Merge | — |
| B.2.2 | GUIDE-XP-002 | CROSS_PLATFORM_DEVELOPER_COOKBOOK.md | Extend | ✅ |
| B.2.3 | GUIDE-XP-003 | CROSS_PLATFORM_IMPLEMENTATION_TEMPLATES.md | Extend | ✅ |
| B.2.4 | GUIDE-XP-004 | CROSS_PLATFORM_MIGRATION_GUIDE.md | Extend | ✅ |
| B.2.5 | GUIDE-XP-005 | CROSS_PLATFORM_QUICK_START.md | Extend | ✅ |
| B.2.6 | GUIDE-XP-006 | CROSS_PLATFORM_ROADMAP.md | Merge | — |
| B.2.7 | GUIDE-XP-007 | HYBRID_ENV_QUICK_START.md | Extend | ✅ |
| Task | ID | File | Action | Ext. Summary |
|------|-----|------|--------|--------------|
| B.3.1 | GUIDE-SH-001 | SHELL_ADVANCED_FEATURES.md | Extend | ✅ |
| B.3.2 | GUIDE-SH-002 | FIX_SHELL_CORRUPTION.md | Extend | ✅ |
| B.3.3 | GUIDE-SH-003 | FIX_SHELL_FORK_ERRORS.md | Extend | ✅ |
| B.3.4 | GUIDE-SH-004 | QUICK_FIX_SHELL_SETUP.md | Extend | ✅ |
| B.3.5 | GUIDE-SH-005 | RUNTIME_OPTIMIZATION.md | Extend | ✅ |
| B.3.6 | GUIDE-SH-006 | DOCTOR_FIXES.md | Extend | ✅ |
| Task | ID | File | Action | Ext. Summary |
|------|-----|------|--------|--------------|
| B.4.1 | GUIDE-INT-001 | PROVIDER_SETUP_GUIDE.md | Extend | ✅ |
| B.4.2 | GUIDE-INT-002 | OXLINT_INTEGRATION_GUIDE.md | Extend | ✅ |
| B.4.3 | GUIDE-INT-003 | PROMPTS_TOOLING.md | Extend | ✅ |
| B.4.4 | GUIDE-INT-004 | JOB_POOL_USAGE.md | Extend | ✅ |
| B.4.5 | GUIDE-INT-005 | OAUTH_ONLY_AUTHENTICATION.md | Extend | ✅ |
| B.4.6 | GUIDE-INT-006 | OPERATIONAL_LEARNING.md | Extend | ✅ |
| Task | ID | File | Action | Ext. Summary |
|------|-----|------|--------|--------------|
| B.5.1 | GUIDE-PH-001 | PHASE_4_QUICK_START.md | Extend | ✅ |
| B.5.2 | GUIDE-PH-002 | PHASE_7_9_GUIDE.md | Extend | ✅ |
| B.5.3 | GUIDE-PH-003 | PHASE_10_GUIDE.md | Extend | ✅ |
| B.5.4 | GUIDE-PH-004 | PHASE_11_GUIDE.md | Extend | ✅ |
| Task | ID | File | Action | Ext. Summary |
|------|-----|------|--------|--------------|
| B.6.1 | GUIDE-AP-001 | anti-patterns.md | Extend | ✅ |
| B.6.2 | GUIDE-AP-002 | index.md | Update | — |
| Task | ID | File | Action | Status |
|------|-----|------|--------|--------|
| C.1.1 | REF-AGT-001 | AGENT_IDENTITY_SOVEREIGNTY_DEPTH.md | Extend | ✅ |
| C.1.2 | REF-AGT-002 | AGENT_NEGOTIATION_ACL_DEPTH.md | Extend | ✅ |
| C.1.3 | REF-AGT-003 | AGENT_OS_PRINCIPALS_DEPTH.md | Extend | ✅ |
| C.1.4 | REF-AGT-004 | HAC_AND_HITL_PATTERNS.md | Extend | ✅ |
| C.1.5 | REF-AGT-005 | SWARM_MEMORY_COORDINATION_DEPTH.md | Extend | ✅ |
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
| Task | ID | File | Action | Status |
|------|-----|------|--------|--------|
| C.6.1 | REF-MON-001 | MONITORING_ALERT_RULES.md | Extend | ✅ |
| C.6.2 | REF-MON-002 | MONITORING_DASHBOARD_SPEC.md | Extend | ✅ |
| C.6.3 | REF-MON-003 | MONITORING_METRICS_REFERENCE.md | Extend | ✅ |
| C.6.4 | REF-MON-004 | MONITORING_README.md | Extend | ✅ |
| C.6.5 | REF-MON-005 | MONITORING_SETUP_GUIDE.md | Extend | ✅ |
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
| Task | ID | File | Action | Status |
|------|-----|------|--------|--------|
| D.1.1 | CHK-001 | index.md | Update | — |
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
| Task | ID | Description | Target | Priority |
|------|-----|-------------|--------|----------|
| E.2.1 | WS-DOC-001 | Add EXTENSION_SUMMARY to all guides | guides/*.md | P1 |
| E.2.2 | WS-DOC-002 | Add EXTENSION_SUMMARY to all reference | reference/*.md | P1 |
| E.2.3 | WS-DOC-003 | Standardize guide formatting | guides/*.md | P2 |
| E.2.4 | WS-DOC-004 | Update reference index | reference/index.md | P1 |
| E.2.5 | WS-DOC-005 | Create doc cross-reference index | reference/XREF_INDEX.md | P2 |
| ID | Title | Source Doc | Priority | Depends | Effort |
|----|-------|------------|----------|---------|--------|
| WS-XXX-000 | Description | DOC_NAME.md | P1/P2/P3 | ID1, ID2 | N hrs |
| Task | ID | Description | Input | Output |
|------|-----|-------------|-------|--------|
| F.1.1 | IMPL-LIB-001 | Replace urllib with httpx (7 files) | LIBRARY_REPLACEMENT_AUDIT | Updated files |
| F.1.2 | IMPL-LIB-002 | Migrate retry to tenacity (4 files) | TENACITY_RETRY_AUDIT | Updated files |
| F.1.3 | IMPL-LIB-003 | Replace polling with watchdog (1 file) | File watching audit | Updated file |
| Task | ID | Description | Input | Output |
|------|-----|-------------|-------|--------|
| F.2.1 | IMPL-HOOK-001 | Build thegent-hooks binary | HOOK_RUST_MIGRATION_* | Binary |
| F.2.2 | IMPL-HOOK-002 | Migrate hooks to use thegent-hooks (opt-in) | F.2.1 | Updated hooks |
| F.2.3 | IMPL-HOOK-003 | Make thegent-hooks default | F.2.2 | Updated hooks |
| F.2.4 | IMPL-HOOK-004 | Add performance benchmarks | F.2.1 | Benchmark report |
| Task | ID | Description | Input | Output |
|------|-----|-------------|-------|--------|
| F.3.1 | IMPL-TUI-001 | Select TUI framework | TUI_COMPOSITOR_COMPARISON.md | Selection |
| F.3.2 | IMPL-TUI-002 | Implement core compositor | F.3.1 | Core module |
| F.3.3 | IMPL-TUI-003 | Integrate with thegent | F.3.2 | Integration |
| Task | ID | Description | Effort |
|------|-----|-------------|--------|
| G.1.1 | IMPL-LIB-101 | Replace custom caching with cachetools (5 files) | 4 hrs |
| G.1.2 | IMPL-LIB-102 | Replace circuit breaker with pybreaker (1 file) | 2 hrs |
| G.1.3 | IMPL-LIB-103 | Replace PyYAML with ruamel.yaml (15 files) | 6 hrs |
| G.1.4 | IMPL-LIB-104 | Replace ANSI stripping with rich (5 files) | 2 hrs |
| Task | ID | Description | Depends | Effort |
|------|-----|-------------|---------|--------|
| G.2.1 | IMPL-ADV-001 | Implement compute offloading | HYBRID_ENV docs | 8 hrs |
| G.2.2 | IMPL-ADV-002 | Implement idea seed system | IDEA_SEEDS docs | 4 hrs |
| G.2.3 | IMPL-ADV-003 | Implement Supermemory integration | research doc | 6 hrs |
| G.2.4 | IMPL-ADV-004 | Implement Pareto routing | PARETO docs | 6 hrs |
- [ ] All 42 guides have EXTENSION_SUMMARY
- [ ] All 84 reference docs have EXTENSION_SUMMARY
- [ ] All 127 docs indexed and cross-referenced
- [ ] Work stream entries created for all P1/P2 tasks
- [ ] urllib → httpx migration complete (7 files)
- [ ] retry → tenacity migration complete (4 files)
- [ ] polling → watchdog migration complete (1 file)
- [ ] thegent-hooks binary built and functional
- [ ] TUI compositor core implemented
- [ ] All docs pass lint (markdownlint)
- [ ] All cross-references valid
- [ ] No broken internal links
- [ ] Consistent formatting across all docs
| Risk | Impact | Mitigation |
|------|--------|------------|
| Agent timeouts during extension | High | Use batch processing, smaller batches |
| Merge conflicts during consolidation | Medium | Sequential processing, branch isolation |
| Invalid cross-references | Medium | Automated link checking |
| Documentation drift | Low | Regular sync with WORK_STREAM |
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-17 | Claude Code | Initial WBS |
| Component | Purpose | Used By |
|-----------|---------|---------|
| **Queue storage** | `.thegent/prompt_queue.jsonl` (project) or `~/.thegent/prompt_queue.jsonl` (global) | Claude Code, Codex, Factory Droid |
| **Queue MCP tools** | `thegent_queue_list`, `claim`, `done`, `add`, `edit`, `release`, `extend_lease` | All |
| **Queue TUI** | `thegent queue tui` — add/edit/list in separate terminal | All |
| **Harvest logic** | `harvest-idea-seeds.sh`, `harvest-pending-queue.sh` | All |
| **Handoff output** | `docs/research/pending-handoff.md` or `.thegent/next-session-prompts.md` | All |
| **Escalation** | `thegent govern escalate` for `$block` | All |
| **Droid resolution** | `.factory/droids/*.md` personas | Factory Droid only |
| Agent | Prompt Intercept | Session Stop | Per-Turn |
|-------|------------------|--------------|----------|
| **Claude Code** | UserPromptSubmit → `prompt-submit-guard` | Stop → `harvest-pending-queue` | — |
| **Codex** | `run_impl` preprocessor; wrapper exit (interactive) | Wrapper exit → harvest | `notify` → `codex-notify` |
| **Factory Droid** | `run_impl` preprocessor; wrapper exit | Wrapper exit → harvest | — |
| Feature | Claude Code | Codex | Factory Droid |
|---------|-------------|-------|---------------|
| **Hooks** | 15 native | Wrapper + notify | Partial (DroidRunner exists) |
| **Queue** | UserPromptSubmit + Stop | run_impl + wrapper | run_impl (needs implementation) |
| **Headless mode** | `claude -p` | `codex exec -` | `droid exec -f` |
| **Interactive mode** | `claude` | `codex` | — (Droid is headless-only) |
| **Droid resolution** | N/A | N/A | `~/.local/bin/droid`, `~/.factory/bin/droid` |
| **Rules** | CLAUDE.md, skills | `.codex/skills` | `.factory/droids` |
| **Unified rules** | — | **thegent rules sync** → all platforms | Same |
| Mode | Entry | Prompt Source | thegent Control |
|------|-------|---------------|-----------------|
| **Headless** | `droid exec -f &lt;file>` | Prompt file (temp) | **Full** — we own file creation |
| **Interactive** | — | — | Droid is headless-only |
| **thegent integration** | `thegent run -M droid:&lt;name> "prompt"` | CLI argument | **Full** |
| Feature | Claude Code | Codex | Factory Droid | Implementation |
|---------|-------------|-------|---------------|----------------|
| **Queue storage** | `.thegent/prompt_queue.jsonl` | Same | Same | Shared |
| **$defer/$pending** | Native | run_impl | run_impl | Same logic |
| **$block** | Native | run_impl | run_impl | Same logic |
| **$idea** | Native | harvest | harvest | Same logic |
| **Harvest on stop** | Native | Wrapper exit | Wrapper exit | Same logic |
| **Session handoff** | Native | Wrapper exit | Wrapper exit | Same logic |
| **Headless mode** | `claude -p` | `codex exec -` | `droid exec -f` | Different CLI |
| **Interactive mode** | `claude` | `codex` | N/A | Not applicable |
| **MCP tools** | Native | Same | Same | Shared |
| **Rules sync** | CLAUDE.md | `.codex/skills` | `.factory/droids` | Platform-specific |
| Feature | Claude Code | Codex | Factory Droid |
|---------|-------------|-------|---------------|
| **Loop support** | Native | Via wrapper | Via wrapper |
| **Teams/teammates** | Native | Phase 6 | Same |
| **Continuation** | `--resume` | N/A | Via prompt file |
| **Re-prompt** | Native | run_impl | run_impl |
| Capability | Claude Code | Codex | Factory Droid |
|-----------|-------------|-------|---------------|
| **Model selection** | `--model` | `--model` | `--model` |
| **Sandboxing** | Native | `--sandbox` | Container support |
| **Streaming** | Native | `--output-format stream-json` | `--output-format stream-json` |
| **Auto mode** | Native | `--auto low/high` | `--auto low/high` |
| **Working directory** | `--cwd` | `--cwd` | `--cwd` |
| Task | Description | Effort | Status |
|------|-------------|--------|--------|
| 1.1 | Verify `DroidRunner` infrastructure in `droid.py` | Small | Done |
| 1.2 | Add Factory Droid to `AGENT_NAMES` in `registry.py` | Small | Pending |
| 1.3 | Implement `droid` backend in `get_runner()` | Small | Pending |
| 1.4 | Add `$defer/$block/$idea` preprocessor to `run_impl` for droid | Small | Pending |
| 1.5 | Add harvest on droid exit to wrapper | Small | Pending |
| 1.6 | Add droid to fallback chain | Small | Pending |
| Task | Description | Effort | Status |
|------|-------------|--------|--------|
| 2.1 | `run_impl` for droid: detect `$defer`, append to queue | Small | Pending |
| 2.2 | `run_impl` for droid: detect `$block`, escalate | Small | Pending |
| 2.3 | `run_impl` for droid: detect `$idea`, save to harvest | Small | Pending |
| 2.4 | On droid exit: run `harvest-pending-queue.sh` | Small | Pending |
| 2.5 | Session handoff: load from `.thegent/next-session-prompts.md` | Small | Pending |
| Task | Description | Effort | Status |
|------|-------------|--------|--------|
| 3.1 | Add `thegent run -M droid:&lt;name> "prompt"` support | Small | Pending |
| 3.2 | Add `THGENT_DROID_BACKEND` support (`droid`, `codex`, `custom`) | Small | Pending |
| 3.3 | Add `THGENT_DROID_MODEL` default model | Small | Pending |
| 3.4 | Add `THGENT_DROID_DIR` droids directory override | Small | Pending |
| 3.5 | Integrate with `thegent queue` CLI commands | Small | Pending |
| 3.6 | Add droid to `thegent agents` list | Small | Pending |
| Task | Description | Effort | Status |
|------|-------------|--------|--------|
| 4.1 | **Droid as teammate** in agent teams | Medium | Pending |
| 4.2 | **Rules injection** into droid prompts | Small | Pending |
| 4.3 | **Loop support** — droid in lifecycle loop | Medium | Pending |
| 4.4 | **MCP tools** — droid-specific tools | Small | Pending |
| 4.5 | **Telemetry** — droid run metrics | Small | Pending |
| Error | Handling |
|-------|----------|
| Droid not found | Return `RunResult` with install instructions |
| Droid timeout | Return `RunResult` with timeout flag |
| Prompt file error | Clean up temp file, return error |
| Non-zero exit | Capture stderr, return in `RunResult` |
| Tool | Description | Used By |
|------|-------------|---------|
| `thegent_run` | Run agent with prompt | All |
| `thegent_bg` | Run agent in background | All |
| `thegent_queue_list` | List pending queue items | All |
| `thegent_queue_claim` | Claim queue item | All |
| `thegent_queue_done` | Mark queue item done | All |
| `thegent_agents_list` | List available agents | All |
| Tool | Description |
|------|-------------|
| `thegent_droid_list` | List available droids |
| `thegent_droid_run` | Run specific droid |
| `thegent_droid_info` | Get droid metadata |
| Component | Test |
|----------|------|
| `DroidRunner.run()` | Happy path, timeout, not found |
| `_preprocess_droid_prompt()` | `$defer`, `$block`, `$idea`, normal |
| `get_runner("droid:name")` | DroidRunner instantiation |
| `queue_add()` / `queue_list()` | Queue operations |
| Component | Test |
|----------|------|
| `thegent run -M droid:worker "prompt"` | End-to-end droid run |
| `thegent run -M droid:worker "$defer test"` | Queue defer |
| `thegent run -M droid:worker "$block test"` | Escalation |
| Droid exit → harvest | Harvest on exit |
| Variable | Purpose | Default |
|----------|---------|---------|
| `THGENT_DROID_CMD` | Droid command path | `droid` |
| `THGENT_DROID_DIR` | Droids directory | `~/.factory/droids/` |
| `THGENT_DROID_MODEL` | Default model | `gemini-3-flash` |
| `THGENT_DROID_BACKEND` | Backend (`droid`, `codex`, `custom`) | `droid` |
| `THGENT_DROID_CODEX_CMD` | Codex command for droid backend | `codex` |
| `THGENT_DROID_CUSTOM_CMD` | Custom CLI for droid backend | `` |
- [ ] `DroidRunner` infrastructure verified
- [ ] `droid` added to `AGENT_NAMES` and fallback chain
- [ ] `get_runner("droid:name")` returns `DroidRunner`
- [ ] `$defer` appends to `.thegent/prompt_queue.jsonl`
- [ ] `$block` escalates via `thegent govern escalate`
- [ ] `$idea` saves to harvest buffer
- [ ] Droid exit triggers `harvest-pending-queue.sh`
- [ ] `thegent run -M droid:worker "prompt"` works
- [ ] `THGENT_DROID_*` env vars respected
- [ ] Droid appears in `thegent agents` list
- [ ] `thegent queue` commands work with droid
- [ ] Droid as teammate in agent teams
- [ ] Rules injected into droid prompts
- [ ] Droid runs in lifecycle loop
- [ ] Droid-specific MCP tools available
| Risk | Mitigation |
|------|------------|
| Droid CLI not installed | Clear error message with install instructions |
| Droid version mismatch | Version check, graceful fallback |
| Droids directory missing | Create default or use `THGENT_DROID_DIR` |
| Queue file corruption | Append-only, atomic writes, lock file |
| Droid timeout | Configurable timeout, timeout flag in `RunResult` |
| Document | Purpose | Relation |
|----------|---------|----------|
| `CODEX_DONUT_HARNESS_PLAN.md` | Unified architecture for all 3 harnesses | This plan extends it |
| `CLAUDE_CODE_FEATURE_PARITY_AUDIT.md` | Feature audit matrix | Used for parity targets |
| `MULTI_PLATFORM_PARITY_MASTER_PLAN.md` | Complete parity matrix | Reference for all platforms |
| `MULTI_PLATFORM_DEEP_DIVE.md` | Schemas, configs, formats | Implementation details |
| `USER_QUEUE_TUI_AND_AGENT_POLL.md` | Queue TUI design | Queue implementation |
| `CLAUDE_CODE_QUEUE_PENDING_BLOCKING.md` | Queue semantics | Queue behavior |
| Need | File / Command |
|------|----------------|
| DroidRunner | `src/thegent/agents/droid.py` |
| Registry | `src/thegent/agents/registry.py` |
| CLI integration | `src/thegent/cli_impl.py` |
| Queue storage | `src/thegent/queue/storage.py` |
| Run droid | `thegent run -M droid:&lt;name> "prompt"` |
| List droids | `thegent agents` |
| Queue status | `thegent queue list` |
| Droid install | `curl -fsSL https://app.factory.ai/cli | sh` |
| Environment | `THGENT_DROID_CMD`, `THGENT_DROID_MODEL`, `THGENT_DROID_DIR` |
| Criterion | Migrate to Rust | Keep Shell |
|-----------|-----------------|------------|
| **Hot path** | Run on every hook, every git call, or every tool invocation | Run once per session or manually |
| **Performance** | Subprocess spawn, PATH scan, 100+ lines parsed per call | `&lt;10ms`, trivial logic |
| **Multi-tenant** | Shared state (cache, lock, git); many concurrent agents | Single-user or stateless |
| **Correctness** | Parsing, hashing, env build; bugs cause cascade failures | Simple glue, easy to audit |
| **Maintainability** | 500+ lines, many callers, complex control flow | `&lt;50` lines, single purpose |
| **Cross-platform** | Must behave identically on macOS/Linux/WSL | Dev-only or macOS-only |
| File | Lines (approx) | Role | Benefit |
|------|----------------|------|--------|
| **common.sh** | ~1685 | hook_init, hook_init_full, cache key/check/read/write, tool detection, git wrapper routing, shared changed files, breaker, debounce, incremental, config, learning, prewarm, reports, affected_tests | **HIGH** — sourced on many hook runs; 1600+ lines + 7 files |
| **common-lite.sh** | small | Minimal subset when `_HOOK_LITE_ONLY` | **HIGH** — same hot path, less surface |
| **git-cache.sh** | ~100+ | TTL cache for read-only git; key by (cwd, argv, HEAD) | **HIGH** — every git read in hooks |
| **git-wrapper.sh** | ~80+ | Agent passthrough; index.lock wait; route to git_cached or real git | **HIGH** — every git in hooks |
| **fd-wrapper.sh** | ~40 | Prefer fd, fallback find; filter -q for macOS | **MEDIUM** — called by hooks |
| **grep-wrapper.sh** | ~30 | Prefer rg, fallback grep | **MEDIUM** — called by hooks |
| **procs-wrapper.sh** | ~30 | Prefer procs, fallback ps | **MEDIUM** — process listing in hooks |
| **builtin-wrapper.sh** | small | Safe builtin routing | **LOW** — thin |
| **pkg-wrapper.sh** | small | Package manager routing | **LOW** — rare |
| **linting-accelerator.sh** | ~50 | Ruff/shellcheck path setup | **MEDIUM** — quality-gate path |
| **git-changed.sh** | ~40 | Wrapper around git diff + ls-files | **HIGH** — used for changed-files |
| **dispatch-patterns.sh** | small | Pattern helpers | **LOW** |
| **nameref-patterns.sh** | small | Zsh/nameref helpers | **LOW** |
| **test-phase4-patterns.sh** | small | Test patterns | **LOW** |
| File | Role | Benefit |
|------|------|--------|
| **posttool-dispatcher.sh** | Source common.sh once, run PostToolUse hooks (source each) | **HIGH** — entry point for PostToolUse; already have Rust hook-dispatcher, can obsolete this when hooks call thegent-hooks |
| **pretool-dispatcher.sh** | Same for PreToolUse | **HIGH** — same as above |
| **stop-dispatcher.sh** | Same for Stop | **HIGH** — same |
| Category | Examples | Benefit |
|----------|----------|--------|
| **Critical path (run often)** | quality-gate.sh, security-pipeline.sh, test-maturity.sh, async-test-runner.sh | **HIGH** — complex logic, cache, git, many subprocesses; native Rust “run-hook” for 1–2 gives largest win |
| **Session/lifecycle** | session-cleanup.sh, session-start-*.sh, task-completed.sh, teammate-idle.sh, doc-location-guard.sh, prompt-submit-guard.sh | **MEDIUM** — some already native in hook-dispatcher (doc_location_guard, session_cleanup, prompt_submit_guard); rest can call thegent-hooks |
| **QA / governance** | governance-gates.sh, spec-verifier.sh, qa-preflight.sh, qa-*-gate.sh (many) | **MEDIUM** — governance_scan already in Rust; individual gates can stay shell that call thegent-hooks for init/cache/git |
| **Gardener / XP** | gardener-xp.sh, gardener-loop.sh, gardener-spawn.sh, gardener-*.sh | **MEDIUM** — invoked from Python (main.py); can become Rust binary or stay shell calling thegent-hooks |
| **Harvest / ideas** | harvest-pending-queue.sh, harvest-idea-seeds-stop.sh | **LOW** — called from prompts.py; can stay shell or become small Rust CLI |
| **Other** | complexity-ratchet.sh, auto-checkpoint.sh, change-doc-tracker.sh, pre-compact-snapshot.sh, hook-watcher.sh, speculative-stop-prewarmer.sh, stop-reconcile.sh, prune-orphans-stop.sh, suppression-*.sh, pre-commit-docs.sh, docs-build.sh | **LOW–MEDIUM** — keep as thin shell that call thegent-hooks for init/cache/git; or migrate hot ones later |
| **Tests** | test_cache_*.sh | **LOW** — dev only |
| Shim | Role | Benefit |
|------|------|--------|
| **git** | resolve_real_binary git; agent passthrough (codex/copilot/dex/claude/cursor); exec real git | **HIGH** — on every git in terminals/agents; already minimal (no common.sh). Replace with **Rust binary** that does resolve + passthrough + exec to avoid any bash. |
| **grep** | resolve real grep; prefer rg, exec | **MEDIUM** — replace with Rust that exec’s rg or grep |
| **find** | resolve real find; filter -q/--quiet; exec fd or find | **MEDIUM** — replace with Rust that filters args and exec’s |
| **codex, copilot, dex, claude, cursor** | PATH prepend ~/.local/bin; resolve agent binary (dex→codex fallback); exec | **MEDIUM** — replace with single Rust binary `thegent-agent-shim &lt;agent> argv...` to avoid bash + PATH parsing |
| **run, bg, logs, status, …** | exec thegent &lt;role&gt; "$@" | **KEEP SHELL** — one-liner; or replace with one Rust “role shim” that exec’s thegent. **LOW** benefit. |
| Script | Role | Benefit |
|--------|------|--------|
| **install_zsh_plugins.sh** | Install zsh plugins (fzf-tab, etc.) | **KEEP SHELL** — run once per setup; user-facing |
| **harvest-idea-seeds.sh** | Harvest idea seeds (prompts.py calls it) | **LOW** — could be Rust CLI later |
| **build-all-rust-extensions.sh** | Build Rust crates | **KEEP SHELL** — dev; cargo is the real work |
| **build-discovery-extension.sh** | Maturin build thegent-discovery | **KEEP SHELL** — dev |
| **optimize-runtime.sh** | Diagnose/fix zsh startup | **KEEP SHELL** — dev/ops |
| **fix-which-timeout.sh** | Fix which timeout | **KEEP SHELL** — one-off fix |
| **identify-shell-migration-candidates.sh** | Find migration candidates | **KEEP SHELL** — meta |
| **fix_shell_corruption.sh**, **emergency_fix_shell.sh** | Repair shell config | **KEEP SHELL** — recovery |
| **guard-shim-forks.sh** | Guard against fork bombs | **LOW** — could be Rust daemon |
| **quality-agent.sh**, **quality-fix-agent.sh** | Agent runners | **LOW** — orchestration |
| **monitor-process-count.sh**, **benchmark-comprehensive.sh** | Metrics/bench | **KEEP SHELL** — dev |
| **dx-audit.sh**, **traceability-validator.sh**, **test-pyramid-validator.sh** | Audits | **LOW** — can stay shell |
| **start_proxy_dev.sh**, **generate_demos.sh** | Dev helpers | **KEEP SHELL** |
| **build-docs.sh** (templates) | Build VitePress/docs | **KEEP SHELL** |
| Caller | Invokes | Action |
|--------|--------|--------|
| main.py | hook-watcher.sh | Keep or replace with thegent-watcher (Rust) when that covers hook-watcher use case |
| main.py | gardener-xp.sh (award, progress) | Replace with Rust CLI or MCP once gardener state is stable |
| prompts.py | harvest-idea-seeds.sh | Can stay shell or become Rust later |
| Shell surface | Rust surface |
|---------------|--------------|
| hook_init, hook_init_full | `thegent-hooks init` |
| hook_cache_key, hash_for_cache | `thegent-hooks cache-key`, `file-hash` |
| hook_cache_check/read/write | `thegent-hooks cache-check`, `cache-read`, `cache-write` |
| git_cached, git() (read + lock + passthrough) | `thegent-hooks git` |
| hook_shared_changed_files, git-changed.sh | `thegent-hooks changed-files` |
| hook_share_result, hook_get_shared | `thegent-hooks share`, `get-shared` |
| hook_should_run, hook_should_skip | `thegent-hooks should-run`, `skip` |
| hook_config_get, hook_config_true | `thegent-hooks config-get` |
| hook_breaker_* | `thegent-hooks breaker-check`, `breaker-record`, `breaker-reset` |
| hook_debounce_file | `thegent-hooks debounce` |
| hook_incremental_* | `thegent-hooks incremental-check`, `incremental-record` |
| hook_shared_fr_ids, hook_shared_fr_index | `thegent-hooks fr-ids`, `fr-index` |
| get_affected_tests, affected_tests_* | `thegent-hooks affected-tests` |
| hook_prewarm_all | `thegent-hooks prewarm` |
| write_*_report | `thegent-hooks report` |
| hook_learning_* | `thegent-hooks learning-record`, `learning-should-skip` |
| Current (shell shim) | Rust binary | Notes |
|----------------------|-------------|--------|
| ~/.local/bin/git | **thegent-git-shim** (new) or **thegent-shims** | Single binary: `thegent-shims git -- argv...` — resolve real git, agent passthrough, exec. No bash. |
| ~/.local/bin/grep | **thegent-shims grep -- argv...** | Resolve rg or grep, exec. |
| ~/.local/bin/find | **thegent-shims find -- argv...** | Filter -q/--quiet, exec fd or find. |
| ~/.local/bin/codex, copilot, dex, claude, cursor | **thegent-shims agent `&lt;name>` -- argv...** | One binary; symlinks codex→thegent-shims agent codex, etc. PATH prepend, resolve, exec. |
| Area | Migrate to Rust | Keep shell |
|------|-----------------|------------|
| **hooks/lib** | common.sh, common-lite.sh, git-cache.sh, git-wrapper.sh, fd/grep/procs wrappers, git-changed.sh → **thegent-hooks** (+ tool paths from thegent-tool-detect) | builtin-wrapper, pkg-wrapper, small pattern scripts |
| **Dispatchers** | Obsolete when hook-dispatcher + thegent-hooks are single path | pretool/posttool/stop-dispatcher.sh until Phase 4 |
| **Event hooks** | Logic of quality-gate, security-pipeline (optionally) → **thegent-hooks run-hook**; all others become thin callers of thegent-hooks | Thin hooks that only call thegent-hooks; test/dev hooks |
| **Install shims** | git, grep, find, codex/copilot/dex/claude/cursor → **thegent-shims** | Role shims (run, bg, …) as one-liners or later Rust |
| **Scripts** | — | install_zsh_plugins, fix_*, build-*, benchmark, dx-audit, harvest (optional later), gardener (optional later) |
| **Python-invoked** | gardener-xp, hook-watcher → Rust/MCP when beneficial | harvest-idea-seeds as shell until Phase 5 |
| Task | Crate / Binary | Status | Interface |
|------|----------------|--------|-----------|
| **BKM-01** | thegent-resources | ✅ Done | Subprocess JSON; PyO3-ready |
| **BKM-02** | thegent-parser | ✅ Done | PyO3 extract_xml_tags, strip_noise, strip_think_blocks |
| **BKM-03** | thegent-crypto | ✅ Done | PyO3 sign_artifact, verify_signature, artifact_hash |
| **BKM-04** | load_based_limits.py | ✅ Done | Python wrapper around BKM-01 |
| **BKM-05** | thegent-shm | Pending | State-SHM (circuit breaker, XP in mmap) |
| **BKM-06** | thegent-git | ✅ Done (libgit2) | PyO3 get_head_sha, get_status_short, get_diff |
| **BKM-07** | hook-dispatcher | Partial | Native secret scan (extend); governance already native |
| **BKM-08** | thegent-discovery | Exists | Binary; PATH resolution, process scan |
| **BKM-09** | thegent-watcher | Exists | Daemon; file watching |
| **BKM-10** | thegent-parser | Pending | JSONL streaming in Rust |
| **BKM-11** | hook-dispatcher / scanner | Pending | Native governance scanner (replace Python spawns) |
| Module / Area | Current | Port / Consolidate |
|---------------|---------|--------------------|
| **Subprocess-heavy** | discovery.py (git, ps, npx); load_based_limits (lsof, vm_stat — BKM-01 done); forensics/snapshot (git); governance/scanner (ruff, bandit); cli_impl (tmux, ps, lsof) | BKM-08 discovery binary; BKM-06 for git; extend hook-dispatcher for scan |
| **Regex/parse hot path** | output_parser.py, contracts/parser.py, tools/xml_repair.py | BKM-02 done; BKM-10 streaming later |
| **Crypto** | governance/signatures.py, execution.py | BKM-03 done |
| **State** | circuit_breaker.py, shm_context.py | BKM-05 State-SHM |
| **HTTP** | 7+ files urllib | → httpx (LIBRARY_REPLACEMENT_AUDIT_DEEP Phase 1) |
| **Retry** | cli_impl, loop_controller manual loops | → tenacity (TENACITY_RETRY_AUDIT_PLAN) |
| **File watching** | governance/triggers (os.walk polling) | → watchdog or thegent-watcher |
| **Caching** | tools/cache.py, _CWD_CACHE, various TTL | → cachetools/diskcache or thegent-hooks cache |
| Item | Location | Role | Port / Note |
|------|----------|------|-------------|
| **Docs / VitePress** | templates/vitepress-full, build-docs.sh | Docs build | Keep; build-docs.sh stays shell |
| **MCP servers (TS)** | next-devtools, sequential-thinking, etc. | MCP tools | Keep; mounted in thegent serve |
| **Config.${version}.ts** | build-docs.sh | Versioned docs | Keep (COMPREHENSIVE_NON_CANONICAL_AUDIT: legitimate) |
| **RUNTIME_OPTIMIZATION** | — | Recommends Bun over Node | Use Bun where TS/JS runs; no port to Rust needed |
| Item | Location | Role | Port / Note |
|------|----------|------|-------------|
| **ultra-shim** | ULTRA_SHIM_CONSOLIDATION_COMPLETE, ULTRA_SHIM_FORK_FAILURE_FIX | Single Go binary: find, grep, git, cat, ls, du, node, npm, npx, python, pip (cache + exec) | **Superseded by thegent-shims (Rust)** in this plan. Go binary had fork exhaustion; we standardize on Rust thegent-shims for git/grep/find/agent. |
| **RUST_GO_MIGRATION_PLAN** | — | “Hook dispatchers → Go binary” | Design chose **Rust** (hook-dispatcher + thegent-hooks); no Go dispatcher. |
| Source | Target | Rationale |
|--------|--------|-----------|
| **Python subprocess for git** | Use thegent-git (BKM-06) or thegent-hooks git | Single place for git metadata; no repeated git spawns |
| **Python custom cache (TTL, file)** | cachetools / diskcache or thegent-hooks cache | LIBRARY_FIRST; one cache strategy |
| **Python custom retry loops** | tenacity | TENACITY_RETRY_AUDIT_PLAN |
| **Python urllib** | httpx | LIBRARY_REPLACEMENT_AUDIT_DEEP Phase 1 |
| **Python os.walk polling** | watchdog or thegent-watcher | LIBRARY_REPLACEMENT_AUDIT_DEEP Phase 3 |
| **Python ANSI strip (5+ copies)** | rich.strip_control_codes | LIBRARY_REPLACEMENT_AUDIT_DEEP Phase 4 |
| **Shell common.sh (init, cache, git)** | thegent-hooks | Single Rust binary; no 1600-line shell |
| **Install bash shims (git, grep, find, agent)** | thegent-shims | Single Rust binary; no PATH parsing in bash |
| **Custom ToolCircuitBreaker** | pybreaker or BKM-05 State-SHM | LIBRARY_FIRST; or native state in Rust |
| **Duplicate regex/XML in Python** | thegent-parser (BKM-02) | Already done; ensure all callers use it |
| **ID generation (uuid4().hex[:8])** | shortuuid / nanoid (lib) or keep | LIBRARY_REPLACEMENT_AUDIT_DEEP |
| **YAML round-trip** | ruamel.yaml | Preserve comments (LIBRARY_REPLACEMENT_AUDIT_DEEP) |
| Capability | Prefer | Avoid |
|------------|--------|-------|
| Retry/backoff | tenacity | Manual for/while + sleep |
| Cache (TTL, file) | cachetools, diskcache, or thegent-hooks cache | Custom dict + mtime |
| HTTP client | httpx | urllib.request |
| Git metadata (HEAD, status, diff) | thegent-git, thegent-hooks git | subprocess.run(["git", ...]) |
| XML/JSONL parse (hot path) | thegent-parser (BKM-02) | Many re.compile + hand-written loops |
| Crypto (sign/verify/hash) | thegent-crypto (BKM-03) | hashlib + custom HMAC in hot path |
| Resource sampling (FD, mem) | thegent-resources (BKM-01) | lsof, vm_stat subprocess |
| File watching | watchdog or thegent-watcher | os.walk polling |
| Circuit breaker | pybreaker or BKM-05 State-SHM | Custom failure list + timer |
| Hook init/cache/changed-files | thegent-hooks | common.sh sourcing |
| PATH / tool resolution | thegent-tool-detect, thegent-discovery | command -v in shell |
| Install shims (git, grep, find, agent) | thegent-shims (Rust) | Bash scripts in install.py |
| ANSI strip | rich.strip_control_codes | re.sub(r"\x1b\[...") in 5 places |
| YAML (round-trip) | ruamel.yaml | PyYAML where comments matter |
| ID generation | shortuuid/nanoid or stdlib uuid | uuid4().hex[:8] scattered |
| Phase | Description | Duration | Effort | Priority |
|-------|-------------|----------|--------|----------|
| **Phase 1** | Read-path zero lock (E4) + graceful degradation (E6) | 1 day | 4–6h | P0 |
| **Phase 2** | Stale lock daemon (lock-cleanup + lsof) | 1–2 days | 6–8h | P0 |
| **Phase 3** | System git wrapper + circuit breaker | 2–3 days | 10–14h | P1 |
| **Phase 4** | Agent system user layout | 2 days | 8–10h | P1 |
| **Phase 5** | Gitoxide (gix) integration | 3–5 days | 16–24h | P2 |
| ID | Task | File | Depends | Effort |
|----|------|------|---------|--------|
| 1.1.1 | Set `GIT_OPTIONAL_LOCKS=0` when invoking git for read-only commands | `hooks/lib/git-cache.sh` | — | 1h |
| 1.1.2 | Add read-only command list: status, diff, ls-files, rev-parse, log, show, name-rev, symbolic-ref, branch, tag, remote, config, ls-tree, cat-file, describe | same | 1.1.1 | 0.5h |
| 1.1.3 | Export env before `"$_git" "$@"` for those commands | same | 1.1.2 | 0.5h |
| ID | Task | File | Depends | Effort |
|----|------|------|---------|--------|
| 1.2.1 | When delegating read-only to git (no git_cached), pass `--no-optional-locks` for status | `hooks/lib/common.sh` | — | 1h |
| 1.2.2 | Add `--no-optional-locks` injection for status/diff when calling THEGENT_GIT_BIN directly | same | 1.2.1 | 0.5h |
| ID | Task | File | Depends | Effort |
|----|------|------|---------|--------|
| 1.3.1 | Support `THEGENT_GIT_LOCK_RETRY=0` to skip wait (fail fast for CI) | `hooks/lib/git-wrapper.sh`, `hooks/lib/common.sh` | — | 1h |
| 1.3.2 | On max retries, exit 128 with message: "GIT-MUTEX: Lock held. Run 'thegent git lock-cleanup' or wait." | same | 1.3.1 | 0.5h |
| 1.3.3 | Document `THEGENT_GIT_LOCK_RETRY` in config reference | `docs/reference/` | 1.3.2 | 0.5h |
| ID | Task | File | Depends | Effort |
|----|------|------|---------|--------|
| 2.1.1 | Add `thegent git lock-cleanup` subcommand | `src/thegent/git_lock_manage.py`, `main.py` | — | 2h |
| 2.1.2 | Options: `--path &lt;dir>`, `--max-age &lt;seconds>` (default 60), `--dry-run` | same | 2.1.1 | 1h |
| 2.1.3 | Scan for `.git/index.lock` under path(s): cwd, PROJECT_DIR, config scan_paths | same | 2.1.2 | 1h |
| 2.1.4 | For each lock: if mtime ≥ max_age, run `lsof`; if no holder, `rm -f` | same | 2.1.3 | 1.5h |
| 2.1.5 | Cross-platform: macOS `stat -f %m`, Linux `stat -c %Y`; `lsof` fallback if missing | same | 2.1.4 | 0.5h |
| ID | Task | File | Depends | Effort |
|----|------|------|---------|--------|
| 2.2.1 | Create `lock_cleanup_install`, `lock_cleanup_start`, `lock_cleanup_stop`, `lock_cleanup_status`, `lock_cleanup_uninstall` | `src/thegent/git_lock_manage.py` | — | 3h |
| 2.2.2 | launchd: Run `thegent git lock-cleanup` every 5 min (StartInterval=300) | same | 2.2.1 | 1h |
| 2.2.3 | systemd: Timer unit + service; same interval | same | 2.2.2 | 1h |
| 2.2.4 | Add `thegent git lock-cleanup service install|start|stop|status|uninstall` | `main.py` | 2.2.3 | 1h |
| ID | Task | File | Depends | Effort |
|----|------|------|---------|--------|
| 2.3.1 | Add `.envrc` template snippet: `thegent git lock-cleanup --path . 2>/dev/null \|\| true` before `use flake` | `thegent/shell/envrc.home.template` | 2.1.1 | 0.5h |
| 2.3.2 | Document in DIRENV_FIX and plan | `docs/research/` | 2.3.1 | 0.5h |
| ID | Task | File | Depends | Effort |
|----|------|------|---------|--------|
| 3.1.1 | Add `--system` / `--prefix &lt;path>` to `install-shims` | `src/thegent/main.py` | — | 2h |
| 3.1.2 | When `--system`: install to `/usr/local/bin` (or prefix); requires write permission | same | 3.1.1 | 1h |
| 3.1.3 | Backup real git to `git.bin`; install wrapper as `git`; wrapper uses `THEGENT_GIT_BIN` or `git.bin` in same dir | same | 3.1.2 | 2h |
| 3.1.4 | Add `install-shims --system --uninstall` to restore | same | 3.1.3 | 1h |
| 3.1.5 | Document in INSTALLATION.md / docs | `docs/` | 3.1.4 | 1h |
| ID | Task | File | Depends | Effort |
|----|------|------|---------|--------|
| 3.2.1 | On lock-wait timeout, write `.git/thegent.lock.failures` with timestamp | `hooks/lib/git-wrapper.sh`, `common.sh` | — | 1.5h |
| 3.2.2 | If failures ≥ 3 in last 5 min, run `thegent git lock-cleanup --path $repo_root` (or inline), then retry once | same | 3.2.1 | 2h |
| 3.2.3 | Reset failure count on success | same | 3.2.2 | 0.5h |
| ID | Task | File | Depends | Effort |
|----|------|------|---------|--------|
| 4.1.1 | Add `thegent install --target system` (or `--prefix /opt/thegent`) | `src/thegent/install.py` | — | 2h |
| 4.1.2 | Layout: `$PREFIX/bin/thegent`, `$PREFIX/bin/git` (wrapper), `$PREFIX/share/thegent/hooks/` | same | 4.1.1 | 2h |
| 4.1.3 | Config: `$PREFIX/etc/thegent/config.yaml` or `/etc/thegent/config.yaml` | same | 4.1.2 | 1h |
| 4.1.4 | Data: `/var/lib/thegent` (sessions, cache, run registry) | same | 4.1.3 | 1h |
| ID | Task | File | Depends | Effort |
|----|------|------|---------|--------|
| 4.2.1 | launchd plist: `PATH=/opt/thegent/bin:/usr/bin:/bin` | `mcp_manage.py` or similar | 4.1.1 | 1h |
| 4.2.2 | systemd unit: `Environment="PATH=/opt/thegent/bin:/usr/bin:/bin"` | same | 4.2.1 | 1h |
| 4.2.3 | Hook discovery: THGENT_ROOT or `$(dirname $(which thegent))/../share/thegent/hooks` | `hooks/` | 4.2.2 | 1h |
| ID | Task | File | Depends | Effort |
|----|------|------|---------|--------|
| 5.1.1 | Add `gix` dependency (≥0.17.0 for CVE-2025-22620 fix) | `Cargo.toml` (thegent-git or thegent-hooks) | — | 1h |
| 5.1.2 | Feature gate: `[features] gix = ["gix-status", "gix-diff"]` | same | 5.1.1 | 0.5h |
| ID | Task | File | Depends | Effort |
|----|------|------|---------|--------|
| 5.2.1 | Implement git_cached path: cache miss → try gix status/diff → fallback to git | `hooks/lib/git-cache.sh` or Rust hook | 5.1.2 | 4h |
| 5.2.2 | gix status: map to `gix status` output format | same | 5.2.1 | 2h |
| 5.2.3 | Fallback for sparse repos, core.fsmonitor (per Starship) | same | 5.2.2 | 2h |
| 5.2.4 | Benchmarks: compare git vs gix for status/diff on typical repo | tests | 5.2.3 | 2h |
| ID | Task | File | Depends | Effort |
|----|------|------|---------|--------|
| 5.3.1 | Document gix opt-out if needed | `docs/` | 5.2.4 | 0.5h |
| 5.3.2 | Add to GIT_TOOLING_AUDIT Phase 5/6 completion | `docs/research/GIT_TOOLING_AUDIT_AND_PLAN.md` | 5.3.1 | 0.5h |
| Phase | Tasks | Total Effort |
|-------|-------|--------------|
| 1 | 1.1.1–1.1.3, 1.2.1–1.2.2, 1.3.1–1.3.3 | 4–6h |
| 2 | 2.1.1–2.1.5, 2.2.1–2.2.4, 2.3.1–2.3.2 | 6–8h |
| 3 | 3.1.1–3.1.5, 3.2.1–3.2.3 | 10–14h |
| 4 | 4.1.1–4.1.4, 4.2.1–4.2.3 | 8–10h |
| 5 | 5.1.1–5.1.2, 5.2.1–5.2.4, 5.3.1–5.3.2 | 16–24h |
| Phase | Done When |
| 1 | `git_cached status` uses `GIT_OPTIONAL_LOCKS=0`; `THEGENT_GIT_LOCK_RETRY=0` fails fast; exit 128 with clear message |
| 2 | `thegent git lock-cleanup` removes stale locks (mtime + lsof); daemon runs every 5 min |
| 3 | `thegent install-shims --system` installs wrapper; circuit breaker runs cleanup after 3 failures |
| 4 | `thegent install --target system` creates layout; agent service PATH has thegent bin first |
| 5 | git_cached uses gix for status/diff when available; fallback for sparse/fsmonitor |
- [ ] Implement `platform.py` with robust cross-platform detection
- [ ] Implement `platform_paths.py` with platform-specific path resolution
- [ ] Add platform detection tests (macOS, Linux, Windows, WSL2)
- [ ] Add path resolution tests for all platforms
- [ ] Implement `design_language.py` with design tokens
- [ ] Implement `naming.py` with naming convention enforcement
- [ ] Apply design language to CLI output (Rich console)
- [ ] Create design language documentation
- [ ] Implement `manage_devkit.py` integration
- [ ] Implement `work_stream.py` integration
- [ ] Implement `plan_system.py` integration
- [ ] Add integration tests
- [ ] Implement `unified_config.py` for cross-system configuration
- [ ] Implement `harmonized_paths.py` for consistent paths
- [ ] Implement `consistency_checker.py` for system-wide consistency
- [ ] Add harmonization tests
- [ ] Add comprehensive docstrings
- [ ] Create integration guides
- [ ] Update main documentation
- [ ] Add examples and tutorials
- [ ] Platform detection works on all targets (macOS, Linux, Windows, WSL2)
- [ ] Path resolution follows OS conventions
- [ ] Manage devkit integration functional
- [ ] WORK_STREAM integration functional
- [ ] PLAN system integration functional
- [ ] Unified configuration works across systems
- [ ] Harmonized paths consistent across systems
- [ ] Consistency checker identifies violations
- [ ] Design language applied to CLI
- [ ] Naming conventions enforced
- [ ] Test coverage >= 80%
- [ ] All lint checks pass
- [ ] All type checks pass
- [ ] Documentation complete
- [ ] Examples provided
- [ ] No conflicts with existing systems
- [ ] Backward compatible where possible
- [ ] Clear migration path for existing users
- [ ] Performance acceptable (`&lt;100ms` overhead)
| Phase | Task | Depends On |
|---|---|---|
| P0 | finalize lane contracts, enforcement semantics, risk model | - |
| P1 | instrumentation and baseline telemetry | P0 |
| P2 | lane router + budget checkpoints + degrade engine | P1 |
| P3 | async queue + artifact ledger + enforcement engine | P2 |
| P4 | hot-path optimization + cache/lock tuning | P2, P3 |
| P5 | CI perf/correctness gates + chaos/perf suites | P3, P4 |
| P6 | shadow rollout -> canary -> progressive -> default | P5 |
| Phase | Task ID | Description | Depends On |
|---|---|---|---|
| P0 | P0.1 | Finalize lane contract, budgets, and enforcement semantics | - |
| P0 | P0.2 | Define check inventory and lane assignment matrix | P0.1 |
| P1 | P1.1 | Instrument end-to-end timing by hook point and segment | P0.1 |
| P1 | P1.2 | Add p50/p95/p99/max telemetry + tracing IDs | P1.1 |
| P2 | P2.1 | Implement lane router with risk classifier | P0.2 |
| P2 | P2.2 | Enforce hard budgets with deadline checkpoints | P2.1 |
| P3 | P3.1 | Build async full-check queue and worker pool | P1.2 |
| P3 | P3.2 | Move heavy checks from sync to async lane C | P3.1 |
| P3 | P3.3 | Add async result enforcement (block/ack/escalate) | P3.2 |
| P4 | P4.1 | Optimize sync hot path (no spawn, warm caches, lock minimization) | P2.2 |
| P4 | P4.2 | Add admission control and coalescing for async jobs | P3.1 |
| P5 | P5.1 | Build perf/correctness regression suite + chaos scenarios | P3.3 |
| P5 | P5.2 | Add CI perf gates and policy compliance checks | P5.1 |
| P6 | P6.1 | Shadow rollout (measure-only) | P5.2 |
| P6 | P6.2 | Controlled enforcement rollout by repo/profile | P6.1 |
| P6 | P6.3 | Default-on hybrid mode with escape hatches | P6.2 |
| Component | Current | Target |
|-----------|---------|--------|
| **Hook Runtime** | `common.sh` (shell) | `thegent-hooks` (Rust) |
| **Git Operations** | `git-cache.sh`, `git-wrapper.sh` | `thegent-hooks git` |
| **Cache Management** | Shell functions | `thegent-hooks cache-*` |
| **Config Reading** | Shell YAML parsing | `thegent-hooks config-get` |
| **Hook Execution** | `bash hook.sh` | `thegent-hooks run-hook` (optional) |
| Operation | Target | Current (shell) |
|-----------|--------|-----------------|
| **init** | `&lt; 5 ms` | ~20-50 ms |
| **cache-key** | `&lt; 2 ms` | ~5-10 ms |
| **git cached (hit)** | `&lt; 1 ms` | ~5-10 ms |
| **git cached (miss)** | `&lt; 50 ms` | ~100-200 ms |
| **changed-files (hit)** | `&lt; 1 ms` | ~5-10 ms |
| **changed-files (miss)** | `&lt; 100 ms` | ~200-500 ms |
| Subcommand | Purpose | Replaces / implements |
|------------|---------|------------------------|
| **init** | Read stdin JSON, resolve PROJECT_DIR, write env to stdout (or exec with env) | `hook_init` / `hook_init_full` |
| **cache-key** | Compute cache key for a hook name (hook + head_sha + changed_files hash) | `hook_cache_key` + `hash_for_cache` |
| **cache-check** | Check if key exists and is fresh (TTL) | `hook_cache_check` |
| **cache-read** | Emit cached stdout; exit with cached rc | `hook_cache_read` |
| **cache-write** | Write key.out / key.rc | `hook_cache_write` |
| **git** | Cached read-only git or passthrough; multi-tenant lock for writes | `git_cached` + `git()` in git-wrapper |
| **changed-files** | Return shared changed files list (git diff + untracked, filtered) | `hook_shared_changed_files` |
| **share** / **get-shared** | Write/read blob under shared dir by name | `hook_share_result`, `hook_get_shared` |
| **should-run** | 0/1 exit: run hook for this pattern? (changed files vs pattern) | `hook_should_run` |
| **config-get** | Read hook-config.yaml key | `hook_config_get` / `hook_config_true` |
| **skip** | 0/1 exit: should hook be skipped? (SKIP_HOOKS, qa-local.json) | `hook_should_skip` |
| **breaker-check** / **breaker-record** / **breaker-reset** | Circuit breaker state | `hook_breaker_*` |
| **debounce** | Debounce leader/follower; output batch of files if leader | `hook_debounce_file` |
| **incremental-check** / **incremental-record** | Manifest-based “inputs unchanged?” | `hook_incremental_*` |
| **file-hash** | Content hash for paths (with optional file-hash cache) | `hash_for_cache`, `hook_file_hash_cache` |
| **fr-ids** | Parse FR-* from FUNCTIONAL_REQUIREMENTS.md, cache | `hook_shared_fr_ids` |
| **fr-index** | Build file:FR index under shared | `hook_shared_fr_index` |
| **affected-tests** | Affected tests for given files (pattern + coverage + imports) | `get_affected_tests`, `affected_tests_*` |
| **prewarm** | Prewarm shared data, ruff, shellcheck caches | `hook_prewarm_all` |
| **progress** | No-op or emit progress line (for idle timeout) | `hook_progress` |
| **report** | Write pass/fail/na JSON report to VERIFY_DIR | `write_pass_report`, etc. |
| **learning-record** / **learning-should-skip** | Learning-based skip | `hook_learning_*` |
| Concept | Current (shell) | Rust |
|--------|------------------|------|
| Cache root | HOOK_CACHE_DIR = $TMPDIR/claude-hook-cache-$UID | Same (env or directories crate) |
| Shared dir | HOOK_CACHE_DIR/shared | Same |
| Cache entry | HOOK_CACHE_DIR/{key}.out, .rc | Same |
| Git cache | GIT_CACHE_DIR (e.g. .git-cache) or project-local | File cache under HOOK_CACHE_DIR/git or per-repo |
| Config | hook-config.yaml, qa-local.json | Read via config module |
| Breakers | HOOK_CACHE_DIR/breakers | Same |
| Learning | HOOK_CACHE_DIR/learning/history.log | Same |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P1.1.1 | Install Syncthing on Windows | 15 min | None |
| P1.1.2 | Create `D:\kush\` directory structure | 10 min | None |
| P1.1.3 | Configure Syncthing folder: `D:\kush\` | 10 min | P1.1.1, P1.1.2 |
| P1.1.4 | Install Tailscale on Windows | 10 min | None |
| P1.1.5 | Configure Tailscale and get device IP | 5 min | P1.1.4 |
| P1.1.6 | Install Parsec host on Windows | 10 min | None |
| P1.1.7 | Configure Parsec hosting and access code | 10 min | P1.1.6 |
| P1.1.8 | Install WSL2 (Ubuntu) | 30 min | None |
| P1.1.9 | Configure WSL2 with basic tools | 20 min | P1.1.8 |
| P1.1.10 | Test Windows firewall rules | 10 min | P1.1.1, P1.1.4, P1.1.6 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P1.2.1 | Install Syncthing on Mac (Homebrew) | 10 min | None |
| P1.2.2 | Create `~/kush/` directory structure | 10 min | None |
| P1.2.3 | Configure Syncthing folder: `~/kush/` | 10 min | P1.2.1, P1.2.2 |
| P1.2.4 | Install Tailscale on Mac | 10 min | None |
| P1.2.5 | Connect Mac to Tailscale network | 5 min | P1.2.4, P1.1.5 |
| P1.2.6 | Install Parsec client on Mac | 10 min | None |
| P1.2.7 | Test Parsec connection to Windows PC | 15 min | P1.2.6, P1.1.7 |
| P1.2.8 | Verify Tailscale connectivity (ping test) | 5 min | P1.2.5 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P1.3.1 | Exchange Syncthing device IDs (Mac ↔ Windows) | 10 min | P1.1.3, P1.2.3 |
| P1.3.2 | Create shared folder `kush` in Syncthing | 10 min | P1.3.1 |
| P1.3.3 | Configure folder sync settings | 15 min | P1.3.2 |
| P1.3.4 | Test initial sync (create test file) | 10 min | P1.3.3 |
| P1.3.5 | Verify bi-directional sync working | 10 min | P1.3.4 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P2.1.1 | Create `.stignore` file template | 15 min | P1.3.2 |
| P2.1.2 | Add Git ignore patterns (`.git/`, `.gitignore`) | 10 min | P2.1.1 |
| P2.1.3 | Add build artifact patterns (`dist/`, `build/`, `target/`) | 10 min | P2.1.1 |
| P2.1.4 | Add dependency patterns (`node_modules/`, `.venv/`, `vendor/`) | 10 min | P2.1.1 |
| P2.1.5 | Add OS-specific patterns (`.DS_Store`, `Thumbs.db`, `__pycache__/`) | 10 min | P2.1.1 |
| P2.1.6 | Add cache patterns (`.cache/`, `.local/`) | 10 min | P2.1.1 |
| P2.1.7 | Test ignore patterns (verify excluded files don't sync) | 15 min | P2.1.6 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P2.2.1 | Configure Syncthing versioning (30 days, simple) | 10 min | P1.3.2 |
| P2.2.2 | Create conflict resolution script | 30 min | P2.2.1 |
| P2.2.3 | Test conflict scenario (simultaneous edit) | 20 min | P2.2.2 |
| P2.2.4 | Verify versioning working (check `.stversions/`) | 10 min | P2.2.1 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P2.3.1 | Create `kush/configs/` directory structure | 15 min | P1.3.2 |
| P2.3.2 | Create subdirectories (shell, vscode, cursor, nvim, git, docker, task) | 10 min | P2.3.1 |
| P2.3.3 | Create platform-specific directories (mac, windows, wsl) | 5 min | P2.3.1 |
| P2.3.4 | Initialize Git repo in `kush/configs/` | 10 min | P2.3.1 |
| P2.3.5 | Create `.gitignore` for configs | 5 min | P2.3.4 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P2.4.1 | Backup existing shell configs (`.zshrc`, `.bashrc`) | 10 min | None |
| P2.4.2 | Create platform-detection functions | 20 min | P2.3.2 |
| P2.4.3 | Move shell configs to `kush/configs/shell/` | 15 min | P2.4.1, P2.3.2 |
| P2.4.4 | Create symlinks (Mac: `~/.zshrc` → `~/kush/configs/shell/.zshrc`) | 10 min | P2.4.3 |
| P2.4.5 | Create symlinks (Windows WSL: `~/.bashrc` → `~/kush/configs/shell/.bashrc`) | 10 min | P2.4.3 |
| P2.4.6 | Test shell configs on both platforms | 15 min | P2.4.4, P2.4.5 |
| P2.4.7 | Sync and verify configs appear on both platforms | 10 min | P2.4.6 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P2.5.1 | Backup VS Code settings | 10 min | None |
| P2.5.2 | Move VS Code settings to `kush/configs/vscode/` | 15 min | P2.3.2 |
| P2.5.3 | Create symlink/junction (Mac: `~/Library/Application Support/Code/User` → `~/kush/configs/vscode/`) | 10 min | P2.5.2 |
| P2.5.4 | Create symlink/junction (Windows: `%APPDATA%\Code\User` → `D:\kush\configs\vscode\`) | 10 min | P2.5.2 |
| P2.5.5 | Backup Cursor settings | 10 min | None |
| P2.5.6 | Move Cursor settings to `kush/configs/cursor/` | 15 min | P2.3.2 |
| P2.5.7 | Create symlinks for Cursor configs | 10 min | P2.5.6 |
| P2.5.8 | Test editor configs on both platforms | 15 min | P2.5.3, P2.5.4, P2.5.7 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P2.6.1 | Backup iTerm2 settings (Mac) | 10 min | None |
| P2.6.2 | Export iTerm2 profiles to `kush/configs/iterm2/` | 15 min | P2.3.2 |
| P2.6.3 | Backup Windows Terminal settings | 10 min | None |
| P2.6.4 | Export Windows Terminal settings to `kush/configs/windows-terminal/` | 15 min | P2.3.2 |
| P2.6.5 | Backup WSL terminal configs | 10 min | None |
| P2.6.6 | Move WSL configs to `kush/configs/wsl/` | 15 min | P2.3.2 |
| P2.6.7 | Create import scripts for terminal configs | 30 min | P2.6.2, P2.6.4, P2.6.6 |
| P2.6.8 | Test terminal configs on both platforms | 20 min | P2.6.7 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P3.1.1 | Create `kush/projects/` directory | 5 min | P1.3.2 |
| P3.1.2 | Move `thegent/` to `D:\kush\projects\thegent\` (Windows) | 30 min | P3.1.1 |
| P3.1.3 | Update Git remote paths if needed | 10 min | P3.1.2 |
| P3.1.4 | Verify Git working in new location | 10 min | P3.1.3 |
| P3.1.5 | Move other projects to `kush/projects/` | 1 hour | P3.1.1 |
| P3.1.6 | Verify all projects syncing | 15 min | P3.1.5 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P3.2.1 | Document platform-specific dependencies | 30 min | P3.1.6 |
| P3.2.2 | Create setup scripts per-platform | 1 hour | P3.2.1 |
| P3.2.3 | Test Python venv recreation (Mac) | 20 min | P3.2.2 |
| P3.2.4 | Test Python venv recreation (Windows) | 20 min | P3.2.2 |
| P3.2.5 | Test Node.js `node_modules` recreation | 20 min | P3.2.2 |
| P3.2.6 | Test Rust `target/` recreation | 20 min | P3.2.2 |
| P3.2.7 | Create dependency sync verification script | 30 min | P3.2.2 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P3.3.1 | Test `thegent` build on Windows | 30 min | P3.1.2 |
| P3.3.2 | Test `thegent` build on Mac | 30 min | P3.1.6 |
| P3.3.3 | Fix platform-specific build issues | 1 hour | P3.3.1, P3.3.2 |
| P3.3.4 | Test other project builds | 1 hour | P3.1.5 |
| P3.3.5 | Document platform-specific build notes | 30 min | P3.3.3, P3.3.4 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P4.1.1 | Enable OpenSSH Server on Windows | 15 min | None |
| P4.1.2 | Configure SSH key-based auth | 20 min | P4.1.1 |
| P4.1.3 | Generate SSH key pair on Mac | 10 min | None |
| P4.1.4 | Copy SSH public key to Windows | 10 min | P4.1.2, P4.1.3 |
| P4.1.5 | Test SSH connection (Mac → Windows) | 10 min | P4.1.4 |
| P4.1.6 | Configure SSH config (`~/.ssh/config`) | 15 min | P4.1.5 |
| P4.1.7 | Test remote command execution | 15 min | P4.1.6 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P4.2.1 | Research `thegent` remote execution capabilities | 30 min | None |
| P4.2.2 | Create remote execution wrapper script | 1 hour | P4.1.7 |
| P4.2.3 | Test `thegent run --remote windows-pc` | 30 min | P4.2.2 |
| P4.2.4 | Integrate with existing `thegent` CLI | 1 hour | P4.2.3 |
| P4.2.5 | Document remote execution usage | 30 min | P4.2.4 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P4.3.1 | Install Docker Desktop on Windows | 20 min | None |
| P4.3.2 | Configure Docker Desktop settings | 15 min | P4.3.1 |
| P4.3.3 | Install process-compose on Windows | 15 min | None |
| P4.3.4 | Move dev services to Windows (process-compose.yaml) | 30 min | P4.3.3 |
| P4.3.5 | Test services running on Windows | 30 min | P4.3.4 |
| P4.3.6 | Configure port forwarding (if needed) | 20 min | P4.3.5 |
| P4.3.7 | Test remote service access from Mac | 20 min | P4.3.6 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P4.4.1 | Test large build on Windows (thegent) | 30 min | P3.3.1 |
| P4.4.2 | Test parallel test execution on Windows | 30 min | P4.4.1 |
| P4.4.3 | Benchmark build times (Mac vs Windows) | 30 min | P4.4.1 |
| P4.4.4 | Document performance improvements | 20 min | P4.4.3 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P5.1.1 | Configure sync bandwidth limits | 15 min | P1.3.2 |
| P5.1.2 | Set up sync schedule (off-hours full sync) | 15 min | P5.1.1 |
| P5.1.3 | Configure selective sync for large files | 30 min | P5.1.1 |
| P5.1.4 | Test sync performance with optimizations | 30 min | P5.1.3 |
| P5.1.5 | Document sync performance metrics | 20 min | P5.1.4 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P5.2.1 | Optimize Parsec settings (resolution, FPS) | 20 min | P1.1.7 |
| P5.2.2 | Configure hardware encoding (NVENC) | 15 min | P5.2.1 |
| P5.2.3 | Test Parsec latency and FPS | 20 min | P5.2.2 |
| P5.2.4 | Fine-tune adaptive quality settings | 20 min | P5.2.3 |
| P5.2.5 | Document optimal Parsec settings | 15 min | P5.2.4 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P5.3.1 | Create backup script (Windows) | 1 hour | None |
| P5.3.2 | Set up Windows Task Scheduler (daily backups) | 30 min | P5.3.1 |
| P5.3.3 | Test backup script | 20 min | P5.3.2 |
| P5.3.4 | Configure backup retention (30 days) | 15 min | P5.3.3 |
| P5.3.5 | Test backup restoration | 30 min | P5.3.4 |
| ID | Task | Est. Time | Dependencies |
|----|------|-----------|--------------|
| P5.4.1 | Create setup guide for new machines | 2 hours | All phases |
| P5.4.2 | Create troubleshooting guide | 1.5 hours | All phases |
| P5.4.3 | Document platform-specific notes | 1 hour | P3.3.5 |
| P5.4.4 | Create runbooks for common tasks | 1 hour | All phases |
| P5.4.5 | Update architecture document with lessons learned | 30 min | All phases |
| Phase | Duration | Total Hours | Key Deliverables |
|-------|----------|-------------|------------------|
| **Phase 1: Foundation** | Week 1 | ~4.5 hours | Basic sync and remote access |
| **Phase 2: Sync Config** | Week 2 | ~9 hours | Full config sync |
| **Phase 3: Project Migration** | Week 3 | ~8.5 hours | All projects syncing |
| **Phase 4: Compute Offloading** | Week 4 | ~9.5 hours | Remote execution working |
| **Phase 5: Optimization** | Week 5 | ~12 hours | Production-ready setup |
| **Total** | **5 weeks** | **~43.5 hours** | Complete hybrid environment |
- [ ] Syncthing devices connected
- [ ] Parsec connection `&lt;20ms` latency
- [ ] Tailscale mesh working
- [ ] Configs syncing correctly
- [ ] Conflict resolution working
- [ ] Versioning enabled
- [ ] All projects syncing
- [ ] Builds working on both platforms
- [ ] Dependencies managed correctly
- [ ] SSH working
- [ ] Remote execution working
- [ ] Services running on Windows
- [ ] Performance optimized
- [ ] Backups automated
- [ ] Documentation complete
| Topic | Reference |
| Architecture | `../architecture/HYBRID_MAC_WIN_DEV_ENVIRONMENT.md` |
| Quick Start | `../guides/HYBRID_ENV_QUICK_START.md` |
| Setup Checklist | `../checklists/HYBRID_ENV_SETUP_CHECKLIST.md` |
| TUI/Queue Design | `../research/USER_QUEUE_TUI_AND_AGENT_POLL.md` |
| Compute Offloading | `REMOTE_COMPUTE_IMPLEMENTATION_DETAIL.md` |
| Section | Description |
|---------|-------------|
| **7. Configuration Examples** | Added practical examples for Syncthing, SSH, Tailscale, Parsec, config sync, project migration, remote execution, service migration, and verification |
| **8. Cross-References** | Added links to related documentation |
| Example | Purpose |
|---------|---------|
| 7.1 Syncthing | Basic sync setup |
| 7.2 SSH Keys | Secure remote access |
| 7.3 Tailscale | VPN mesh network |
| 7.4 Parsec | Remote desktop |
| 7.5 Config Sync | Cross-platform configs |
| 7.6 Project Migration | Moving projects to shared location |
| 7.7 Remote Execution | Running commands on Windows |
| 7.8 Service Migration | Moving services to Windows |
| 7.9 Verification | Testing setup |
| Issue | Reference |
| Sync conflicts | Architecture doc §14.1 |
| Parsec lag | Architecture doc §14.3 |
| Build failures | Architecture doc §14.4 |
| Network issues | Architecture doc §14.1 |
| Component | Location | Role |
|-----------|----------|------|
| **thegent** | `thegent/` | Agent orchestration, MCP server (3847), clode/claudemax shims |
| **CLIProxyAPIPlus-fork** | `../CLIProxyAPIPlus-fork/` | Chat proxy (8317), OAuth, openai-compatibility, minimax/zai. Go project, build: `go build -o cli-proxy-api-plus ./cmd/server` |
| **LiteLLM** | pheno-sdk, zen-mcp-server, agentapi | Multi-provider client, fallback chains, model discovery |
| **Bifrost** | (Go project with extensions) | Alternative proxy/gateway with extension system |
- [ ] `clode_main._get_claude_env`: use `cliproxy_port` (8317) for chat, not `mcp_port` (3847)
- [ ] Verify `ANTHROPIC_API_KEY` override in subprocess env
- [ ] Document `THGENT_CLIPROXY_BINARY` for fork: `../CLIProxyAPIPlus-fork/cli-proxy-api-plus` (or built binary path)
- [ ] **Catalog–fork alignment:** Ensure nim routes work — fork has no native "nim"; needs openai-compatibility. See CATALOG_CLIPROXY_FORK_ALIGNMENT.md.
- [ ] (Optional) LiteLLM config generator from `~/.factory/config.json`
- [ ] (Optional) Bifrost extension for CLIProxy bridge
| Client        | Config Path                          | Manual Playwright? |
|---------------|--------------------------------------|--------------------|
| Cursor        | `~/.cursor/mcp.json`, `.cursor/mcp.json` | Yes (`@playwright/mcp`) |
| Claude Code   | `~/.claude.json`                     | Yes (if configured) |
| Codex         | `~/.codex/mcp.json`, `~/.codex/config.toml` | Yes (timeout issues) |
| Aspect | Current | Proposed |
|--------|---------|----------|
| Process | One process (thegent serve) | Same |
| Clients | Cursor, Claude Code, Codex each connect to same URL | Same |
| Sub-servers | None | Playwright, Serena, Octocode (all required) — mounted as providers |
| Session isolation | Per HTTP request | FastMCP `create_proxy` gives session isolation per request |
- [ ] Document `pip install flyto-core[browser]` and `playwright install chromium` for browser tools
- [ ] Document `flyto serve` for HTTP mode (optional; or use stdio subprocess)
- [ ] Test: Cursor, Claude Code, Codex with only thegent config
| Risk | Mitigation |
|------|------------|
| flyto-core license (Source Available) | Use only for personal/internal; document commercial license need |
| Startup latency | Mount lazily or on first tool call; cache `list_tools` |
| Context bloat | flyto-core uses 6 tools only; avoid mounting 300+ tools directly |
| Playwright timeout | Single thegent process; no per-client playwright subprocess |
| Principle | MCP Application | Anti-Pattern |
|-----------|-----------------|--------------|
| **Intuitive** | Same ToolResult shape; verb-first tool names; consistent param names (cd, agent, model) | Tool-specific schemas, inconsistent naming |
| **Robust** | Fail clearly with actionable hints; idempotent where safe; bounded responses | Silent degradation, unbounded logs |
| **Holistic** | Tool discovery → call → response → error; every tool has defined exit paths | Orphan tools, undefined error behavior |
| **Complete** | Every tool returns structured_content + meta when applicable; errors include remediation | Partial responses, opaque failures |
| **Maximal** | Full annotation coverage; execution_time_ms on all tools; caching where beneficial | Missing annotations, no timing |
| **Lean** | No speculative tool surface; prefer params over new tools; YAGNI | Tool explosion, over-parameterization |
| Goal | Approach |
|------|----------|
| **Optimize** | Apply QW/OPT items to mcp_server.py: caching, _resolve_cwd, payload_signature, span attributes |
| **Polish** | UX items: actionable errors, execution_time_ms everywhere, tool descriptions |
| **Harden** | ROB items: config validation, graceful shutdown, idempotency where safe |
| **Complete** | End-to-end tool flows; verification checklist; no orphan responses |
| ID | Item | MCP Application | Status |
|----|------|-----------------|--------|
| QW-001 | payload_signature for deterministic caching | Add hash to health_gate, health_report, health_trend responses | ⏳ |
| QW-002 | _resolve_cwd caching | Already in cli_impl; MCP uses it via run_impl/bg_impl | ✓ |
| OPT-001 | Response caching middleware | Already: 30s TTL on ps, list_agents, list_models, health_trend, sitback | ✓ |
| OPT-002 | Rate limiting | Already: 10/s, burst 20 | ✓ |
| OPT-003 | Response size limiting | Already: 500KB cap | ✓ |
| OPT-020 | Route resolution memo | Add LRU in resolve_route path when called from MCP | ⏳ |
| OPT-021 | OTel span attributes | Add model, provider, lane to run/bg/status tool spans | ⏳ |
| ID | Item | MCP Application | Status |
|----|------|-----------------|--------|
| ROB-005 | Idempotency tokens | Queue claim/release; extend_lease; ensure release is idempotent | ⏳ |
| ROB-007 | Graceful shutdown | Already: shutdown_wait_s, shutdown_wait_active_s | ✓ |
| ROB-013 | Config validation on startup | Already: validate_setup() in lifespan | ✓ |
| ROB-016 | Elicitation timeout | Add 5s timeout to ctx.elicit; fail-safe on missing input | ⏳ |
| ROB-017 | Route fallback chain | Already: prefer_direct → prefer_proxy; add hint in error | ⏳ |
| ID | Item | MCP Application | Status |
|----|------|-----------------|--------|
| UX-001 | Tool annotations | Already on most; audit all 40+ for readOnly/destructive/idempotent | ⏳ |
| UX-002 | Structured ToolResult + meta | run, bg, ps, status, logs, health_* have it; extend to all | ⏳ |
| UX-003 | Action-oriented descriptions | Verb-first: "Execute agent task", "List background sessions" | ⏳ |
| UX-004 | Parameter docs | Clear defaults, units (timeout: seconds), constraints (mode: write\|full) | ⏳ |
| UX-005 | Actionable error messages | "No route for X. Try: thegent list-models" (already some); extend | ⏳ |
| UX-013 | Inline constraints | min/max on timeout, num_results; enum for mode, policy | ⏳ |
| DX-SM-01 | thegent login supermemory | Unified login flow for cloud memory; project scoping via x-sm-project | ⏳ |
| WP-SM-02 | SupermemoryProvider | Implementation of L3/L4 memory using Supermemory API | ⏳ |
| WP-SM-03 | Knowledge Graph Relationships | Swarm relationship tracking via Supermemory graph | ⏳ |
| OPT-PROC-01 | Multi-Tenant Process Orchestrator | Consolidate MCP servers and agents into single process | ⏳ |
| OPT-PROC-02 | Efficient Tool Migration | Replace cat/tr/cp/sleep with internal Python/Rust builtins | ⏳ |
| OPT-PROC-03 | Process Cleanup | Remove redundant MCPs (context7) and optimize task runners | ⏳ |
| Tool | Annotations | execution_time_ms | structured_content | Actionable Errors | Gaps |
|------|:-----------:|:-----------------:|:------------------:|:------------------:|-----|
| thegent_run | ✓ | ✓ | ✓ | ✓ (route, cwd) | — |
| thegent_bg | ✓ | ✓ | ✓ | Partial | Add "Run: thegent ps" on failure |
| thegent_ps | ✓ | ✓ | ✓ | ✓ | — |
| thegent_status | ✓ | ✓ | ✓ | Partial | Add "Run: thegent inspect" if not found |
| thegent_logs | ✓ | ✓ | ✗ | Partial | Add structured_content; "Session not found" + hint |
| thegent_inspect | ✓ | ✓ | ✓ | Partial | Add remediation for empty |
| thegent_list_agents | ✓ | ✗ | ✓ | — | Add execution_time_ms |
| thegent_list_droids | ✓ | ✓ | ✓ | — | — |
| thegent_list_models | ✓ | ✓ | ✓ | ✓ | — |
| thegent_resolve_model_route | ✓ | ✓ | ✓ | ✓ | — |
| thegent_session_contract_health_* | ✓ | ✓ | ✓ | Partial | Add payload_signature (QW-001) |
| thegent_inbox_list | ✓ | ✗ | ✓ | — | Add execution_time_ms |
| thegent_inbox_wait | ✓ | ✗ | ✓ | — | Add execution_time_ms |
| thegent_stop | ✓ | ✗ | ✓ | Partial | Add execution_time_ms; "Run: thegent ps" |
| thegent_pause/resume | ✓ | ✗ | ✓ | — | Add execution_time_ms |
| thegent_continuity_snapshot | ✓ | ✗ | ✓ | — | Add execution_time_ms |
| thegent_list_operations | ✓ | ✗ | — | ✓ (unknown op) | Add execution_time_ms, structured_content |
| thegent_list_modes | ✓ | ✗ | — | ✓ (unknown mode) | Add execution_time_ms, structured_content |
| thegent_suggest_mode | ✓ | ✗ | ✓ | — | Add execution_time_ms |
| thegent_dag_list | ✓ | ✓ | ✓ | — | — |
| thegent_do_next | ✓ | ✗ | ✓ | — | Add execution_time_ms |
| thegent_terminal_* | ✓ | ✗ | Partial | "Pane not found" + hint | Add execution_time_ms |
| thegent_ddg_search | ✓ | ✗ | ✓ | — | Add execution_time_ms |
| thegent_suggest_prompt | ✓ | ✓ | ✓ | — | — |
| Error | Remediation |
|-------|-------------|
| No route for model X | Try: thegent list-models |
| Model X not available via provider Y | Available: A, B. Or: thegent list-models |
| Provide agent or model | Run: thegent list-agents |
| CWD not found | Provide cd=/path or run from project root |
| Ambiguous cwd | Provide cd=/path explicitly |
| Session not found | Run: thegent ps |
| Pane not found | Run: thegent terminal_list |
| Unknown operation X | Valid: orchestrate, govern, recover, observe, plan |
| Unknown mode X | Valid: write, full, plan, ... |
| User declined cwd | Provide cd=/path in tool call |
| Elicitation cancelled | Retry with explicit params |
| Tier | Scope | Examples |
|------|-------|----------|
| **Tier 1 (Must)** | Completeness + robustness | execution_time_ms all tools; remediation on all errors; audit annotations |
| **Tier 2 (Should)** | Optimization + polish | payload_signature (QW-001); OTel spans (OPT-021); route memo (OPT-020) |
| **Tier 3 (Nice)** | Convenience | Inline constraints (min/max/enum); elicitation timeout (ROB-016) |
| **Tier 4 (Defer)** | Speculative | Tool-level caching hints; batch tool for multi-session ops |
| Need | Location |
|------|----------|
| Design philosophy | §0 |
| OPT/ROB/UX mapping | §2 |
| End-to-end flows | §3 |
| Tool-by-tool matrix | §4 |
| Error standard | §5 |
| Enhancement tiers | §6 |
| Implementation checklist | §7 |
| Full optimization catalog | [08-OPTIMIZATION-CATALOG.md](./08-OPTIMIZATION-CATALOG.md) |
| Multi-platform design | [MULTI_PLATFORM_PARITY_MASTER_PLAN.md](./MULTI_PLATFORM_PARITY_MASTER_PLAN.md) §10–13 |
| Principle | Meaning | Anti-Pattern |
|-----------|---------|--------------|
| **Intuitive** | Same mental model across platforms; `run -M X` works everywhere | Platform-specific quirks |
| **Robust** | Fail clearly; degrade gracefully; no silent corruption | Silent fallbacks, opaque errors |
| **Holistic** | End-to-end flows work (queue → harvest → handoff → next session) | Orphan features |
| **Complete** | Every entry point has an exit; every state has a transition | Half-implemented flows |
| **Maximal** | Full capability coverage; nothing left on the table | Feature gaps |
| **Lean** | No abstraction for abstraction's sake; YAGNI at the design level | Over-engineered layers |
| Goal | Approach |
|------|----------|
| **Achieve parity** | Match each platform's native capabilities via thegent harness (queue, harvest, rules, teams, MCP) |
| **Supercede parity** | Unify across platforms: single queue, single rules sync, single MCP toolset, cross-platform teams |
| **Platforms** | Claude Code (reference), Codex, Cursor, Factory droid, Augment, OpenCode |
| Capability | Claude Code | Codex | Cursor | Factory Droid | Augment | OpenCode | thegent Strategy | Status |
|------------|:-----------:|:-----:|:------:|:-------------:|:-------:|:--------:|------------------|--------|
| **Interactive TUI** | ✓ Native | ✓ Native | ✓ Composer | ✗ | ✓ auggie | ✓ oc | thegent codex/clode/dex wrap | ✓ |
| **Headless** | ✓ claude -p | ✓ codex exec - | ✓ cursor-agent | ✓ droid exec | ✓ auggie --print | ✓ oc | thegent run -M {agent} | ✓ |
| **Queue ($defer/$pending)** | ✓ UserPromptSubmit | ✗ | ✗ | ✗ | ✗ | ✗ | run_impl preprocessor + prompt-submit-guard | ⏳ |
| **Block ($block)** | ✓ UserPromptSubmit | ✗ | ✗ | ✗ | ✗ | ✗ | escalation + run_impl | ⏳ |
| **Harvest ($idea)** | ✓ UserPromptSubmit | ✗ | ✗ | ✗ | ✗ | ✗ | harvest-idea-seeds (all sources) | ✓ |
| **Session lifecycle hooks** | ✓ 15 events | ✗ (notify only) | ✗ | ✗ | ✗ | ✗ | Wrapper exit + run_impl + codex-notify | ⏳ |
| **Agent teams** | ✓ Native | ✗ | ✗ | ✗ | Intent | ✗ | thegent team (N codex exec + MCP) | ⏳ |
| **Subagents** | ✓ Task tool | ✗ | ✗ | ✗ | ✗ | ✗ | thegent_run/thegent_bg as subagent | ✓ |
| **Rules/Skills** | ✓ CLAUDE.md, skills | ✓ .codex/skills | ✓ .cursor/rules | ✓ .factory/droids | ✗ | ✓ .codex/skills | thegent rules sync → all | ⏳ |
| **MCP** | ✓ Full | ✓ Full | ✓ Full | ✓ .factory/mcp | ✓ Context Engine | ✓ Full | thegent serve (30+ tools) | ✓ |
| **Unified queue** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | .thegent/prompt_queue.jsonl | ⏳ |
| **Unified rules** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | thegent rules sync | ⏳ |
| **Harvest (multi-source)** | Claude only | Codex only | Cursor only | ✗ | ✗ | ✗ | harvest from Claude+Codex+Cursor | ✓ |
| **Context Engine** | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | Add Augment MCP to install | ⏳ |
| **Living specs** | ✗ | ✗ | ✗ | ✗ | ✓ Intent | ✗ | thegent team + DAG as spec | ⏳ |
| **Git worktrees** | ✗ | ✗ | ✗ | ✗ | ✓ Intent | ✗ | thegent team: separate processes | ⏳ |
| **Droid personas** | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | DroidRunner, droid as teammate | ✓ |
| **Lifecycle loop** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | thegent_loop + checker | ✓ |
| **Model routing** | ✗ | ✗ | ✗ | ✗ | ✗ | Zen | 12+ providers, failover, Pareto | ✓ |
| Capability | Claude | Codex | Cursor | Droid | Augment | OpenCode | thegent |
|------------|:------:|:-----:|:------:|:-----:|:-------:|:--------:|---------|
| **PreToolUse** | ✓ | ✗ | ✗ | Factory hooks | ✗ | ✗ | N/A (no tool loop in exec) |
| **PostToolUse** | ✓ | notify (AfterAgent) | ✗ | Factory hooks | ✗ | ✗ | codex-notify |
| **PermissionRequest** | ✓ | Sandbox | ✗ | — | ✗ | ✗ | Different models |
| **Memory** | user/project/local | session | — | — | — | — | run registry |
| **Checkpointing** | Rewind | ✗ | ✗ | ✗ | Intent resumable | ✗ | run registry, handoff |
| **Resume session** | --resume | ✗ | ✗ | ✗ | Intent | ✗ | handoff file |
| **Structured output** | --json-schema | --json | ✗ | stream-json | ✗ | ✗ | Passthrough |
| **Sandbox** | Bash tool | exec sandbox | — | — | — | — | Per-agent |
| **Proxy agents** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | antigravity, kilo, nim, cliproxy |
| **Background agent** | ✗ | ✗ | Cursor bg | ✗ | ✗ | ✗ | thegent_bg |
| **Plan mode** | ✗ | ✗ | /plan | ✗ | ✗ | ✗ | thegent run mode? |
| **Code Review** | ✗ | ✗ | ✗ | ✗ | Augment | ✗ | — |
| **IDE extension** | ✗ | ✗ | Composer | ✗ | VS Code, JB | oc | N/A |
| **Desktop app** | ✗ | ✗ | ✗ | ✗ | Intent | Beta | — |
| **Slack delegate** | ✗ | ✗ | ✗ | ✗ | Augment | ✗ | — |
| **Remote agents** | ✗ | ✗ | ✗ | ✗ | Augment | ✗ | thegent serve HTTP |
| Claude Hook | Blocking | Claude | Codex | Cursor | Droid | Augment | OpenCode | thegent Strategy |
|-------------|:--------:|:------:|:-----:|:------:|:-----:|:-------:|:--------:|------------------|
| SessionStart | No | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | Wrapper: inject handoff before spawn; exec: prepend stdin |
| UserPromptSubmit | Yes | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | run_impl preprocessor; prompt-submit-guard |
| PreToolUse | Yes | ✓ | ✗ | ✗ | Factory | ✗ | ✗ | SDK only; exec N/A |
| PermissionRequest | Yes | ✓ | Sandbox | ✗ | ✗ | ✗ | ✗ | Different model |
| PostToolUse | No | ✓ | notify | ✗ | Factory | ✗ | ✗ | codex-notify |
| PostToolUseFailure | No | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | — |
| Notification | No | ✓ | ✗ | ✗ | Factory | ✗ | ✗ | — |
| SubagentStart | No | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | thegent_run = subagent |
| SubagentStop | Yes | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | On thegent run exit |
| Stop | Yes | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | Wrapper exit; harvest |
| TeammateIdle | Yes | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | Wrapper poll teammate |
| TaskCompleted | Yes | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | MCP task lifecycle |
| PreCompact | No | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | — |
| SessionEnd | No | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | Wrapper exit |
| Order | Event | When | Blocking | Script/Hook |
|-------|-------|------|----------|-------------|
| 1 | SessionStart | New session, resume, clear, compact | No | — (optional handoff) |
| 2 | UserPromptSubmit | Before prompt sent | Yes | prompt-submit-guard.sh |
| 3 | PreToolUse | Before tool call | Yes | — |
| 4 | PermissionRequest | Permission dialog | Yes | — |
| 5 | PostToolUse | After tool call | No | — |
| 6 | PostToolUseFailure | After tool fails | No | — |
| 7 | Notification | Various | No | — |
| 8 | SubagentStart | Subagent spawned | No | — |
| 9 | SubagentStop | Subagent done | Yes | — |
| 10 | Stop | Session ends | Yes | harvest-pending-queue.sh, harvest-idea-seeds-stop.sh |
| 11 | TeammateIdle | Teammate about idle | Yes | — |
| 12 | TaskCompleted | Task marked done | Yes | — |
| 13 | PreCompact | Before compaction | No | — |
| 14 | SessionEnd | Session terminates | No | — |
| Platform | Sandbox | Permission Model | thegent |
|----------|---------|------------------|---------|
| Claude Code | Bash tool sandbox | default, plan, acceptEdits, dontAsk, bypass | Passthrough |
| Codex | exec sandbox: workspace-write, danger-full-access | Implicit via sandbox | --sandbox passthrough |
| Cursor | — | — | — |
| Droid | — | tools: read-only, write, execute | DroidRunner mode |
| Augment | — | — | — |
| OpenCode | — | — | — |
| Area | Platform Best | thegent Supercede |
|------|---------------|-------------------|
| **Queue** | Claude Code (UserPromptSubmit) | Unified .thegent queue for ALL platforms; MCP tools; TUI |
| **Rules** | Cursor (.cursor/rules) | Single source → sync to Claude, Codex, Cursor, droid |
| **Harvest** | Per-platform | Single harvest from Claude + Codex + Cursor transcripts |
| **Teams** | Claude Code / Augment Intent | thegent team works with Codex, droid, cursor; MCP-driven |
| **Model access** | OpenCode Zen (paid) | 12+ providers, free-first (Antigravity, Kilo, NIM) |
| **Orchestration** | Augment Intent (desktop) | CLI + MCP; works in CI, headless, any agent |
| **MCP toolset** | Per-client | 30+ tools, 20+ resources; same across Claude, Codex, Cursor |
| Capability | Native | thegent Achieve | thegent Supercede |
|------------|--------|----------------|-------------------|
| Hooks | 15 events | prompt-submit-guard, harvest Stop | — |
| Queue | UserPromptSubmit | Migrate to .thegent queue | Unified queue for all |
| Teams | Native | — | thegent team extends to Codex/droid |
| Headless | claude -p | thegent run -M claude | Same entry as Codex/Cursor |
| Rules | CLAUDE.md | rules sync writes | Single source → all platforms |
| Capability | Native | thegent Achieve | thegent Supercede |
|------------|--------|----------------|-------------------|
| Hooks | notify (AfterAgent) | codex-notify; run_impl preprocessor; wrapper exit | Full lifecycle via wrapper |
| Queue | ✗ | run_impl $defer/$block; wrapper harvest | Same as Claude |
| Teams | ✗ | thegent team (N codex exec) | Teams for Codex |
| Interactive | codex TUI | thegent codex wrapper + exit hook | Harvest on exit |
| Rules | .codex/skills | rules sync | Single source |
| MCP | Full | thegent serve | 30+ tools |
| Capability | Native | thegent Achieve | thegent Supercede |
|------------|--------|----------------|-------------------|
| Rules | .cursor/rules | rules sync reads | Single source → Cursor |
| Harvest | ✗ | harvest from transcripts | $defer/$idea from Cursor |
| Headless | cursor-agent | thegent run -M cursor-agent | Same CLI as others |
| MCP | Full | thegent serve | Same tools |
| Modes | /plan, agent, bg | thegent run mode | — |
| Capability | Native | thegent Achieve | thegent Supercede |
|------------|--------|----------------|-------------------|
| Droids | droid exec | DroidRunner | droid as teammate |
| Tools | Per-droid | Frontmatter parsed | — |
| Queue | ✗ | run_impl preprocessor | Same queue |
| Harvest | ✗ | On droid exit | Same harvest |
| Rules | .factory/droids | Inject into prompt | rules sync |
| Teams | ✗ | Droid as teammate | Codex + droid teams |
| Capability | Native | thegent Achieve | thegent Supercede |
|------------|--------|----------------|-------------------|
| auggie CLI | auggie, auggie --print | thegent run -M augment | Same entry |
| Context Engine | MCP | Add to mcp install | Cross-platform context |
| Intent | Desktop orchestration | — | thegent team (CLI) |
| Living specs | Intent | — | DAG + team tasks |
| Capability | Native | thegent Achieve | thegent Supercede |
|------------|--------|----------------|-------------------|
| oc CLI | oc (terminal agent) | thegent run -M opencode | Same entry |
| Zen | Curated models | Not recommended (ZEN_INTEGRATION.md) | Free-first routing |
| MCP | Full | thegent serve | Same tools |
| Desktop | Beta | — | — |
| Source format | Cursor | Claude Code | Codex | Droid |
|---------------|--------|--------------|-------|-------|
| .mdc | .cursor/rules/{name}.mdc | CLAUDE.md section or .claude/skills/{name}/SKILL.md | .codex/skills/{name}/SKILL.md | Inject into droid prompt |
| alwaysApply | alwaysApply: true | SessionStart inject | model_instructions | — |
| globs | globs field | N/A | N/A | — |
| Platform | Variant | Config Path | Notes |
|----------|---------|-------------|-------|
| Claude Code | vs Claude Desktop | ~/.claude.json vs ~/Library/.../claude_desktop_config.json | Different config; both support MCP |
| Codex | Project vs user config | .codex/config.toml (trusted) vs ~/.codex/config.toml | Project overrides user |
| Cursor | Workspace vs user | .cursor/mcp.json vs ~/.cursor/mcp.json | Workspace preferred |
| Cursor | Composer vs cursor-agent | IDE vs CLI | Same MCP; different entry |
| Droid | Project only | .factory/mcp.json | No user-level |
| OpenCode | oc vs Zen | oc CLI vs Zen gateway | Zen = paid; don't integrate |
| Client | MCP Config | Notify/Other |
|--------|------------|--------------|
| Cursor | ~/.cursor/mcp.json, .cursor/mcp.json | — |
| Claude Code | ~/.claude.json (stdio: command, args) | — |
| Codex | ~/.codex/mcp.json, ~/.config/codex/mcp.json | ~/.codex/config.toml notify |
| Claude Desktop | ~/Library/Application Support/Claude/claude_desktop_config.json | — |
| Droid | .factory/mcp.json | — |
| Platform | Interactive | Headless | thegent run |
|----------|-------------|----------|-------------|
| Claude Code | claude | claude -p "..." | run -M claude |
| Codex | codex | codex exec - | run -M codex |
| Cursor | Composer (IDE) | cursor-agent | run -M cursor-agent |
| Factory droid | — | droid exec -f path | run -M droid:name |
| Augment | auggie | auggie --print "..." | run -M augment |
| OpenCode | oc | oc | run -M opencode |
| Proxy (antigravity, kilo, etc.) | — | codex exec → proxy | run -M antigravity, etc. |
| Phase | Name | Platforms | Key Deliverables | Effort |
|-------|------|-----------|------------------|--------|
| **1** | Shared Foundation | All | Queue storage, migration, codex-notify, queue MCP tools | Medium |
| **2** | Exec Preprocessor | Codex, Droid, Augment, OpenCode | $defer/$block in run_impl; harvest on exit | Medium |
| **3** | Interactive Wrapper | Codex | thegent codex; exit hook | Small |
| **4** | Queue TUI | All | thegent queue tui; CLI; locking | Medium |
| **5** | Codex SDK (Optional) | Codex | Full UserPromptSubmit in interactive | High |
| **6** | Agent Teams | Codex, Droid | thegent team create; MCP tools; TeammateIdle | High |
| **7** | Full Hook Parity | Codex | SessionStart; SubagentStop; TeammateIdle | Medium |
| **8** | Claude Headless | Claude | run -M claude; --continue, --resume | Small |
| **9** | Rules Sync | All | thegent rules sync; canonical source | Medium |
| **10** | Cursor Integration | Cursor | run -M cursor-agent; harvest transcripts | Small |
| **11** | Droid Augmentation | Droid | $defer/$block; harvest; droid as teammate | Medium |
| **12** | Augment Integration | Augment | run -M augment; Context Engine MCP | Small |
| **13** | OpenCode Integration | OpenCode | run -M opencode; registry | Small |
| Phase | Task ID | Task | Claude | Codex | Cursor | Droid | Augment | OpenCode |
|-------|---------|------|:------:|:-----:|:------:|:-----:|:-------:|:--------:|
| 1 | 1.1 | Queue storage module | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 1 | 1.2 | Migrate prompt-submit-guard to .thegent | ✓ | — | — | — | — | — |
| 1 | 1.3 | Migrate harvest to .thegent | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 1 | 1.4 | codex-notify | — | ✓ | — | — | — | — |
| 1 | 1.5 | notify in install_to_codex | — | ✓ | — | — | — | — |
| 1 | 1.6 | thegent-queue skill | — | ✓ | — | — | — | — |
| 1 | 1.7 | Queue MCP tools | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2 | 2.1 | run_impl $defer/$block preprocessor | — | ✓ | — | ✓ | ✓ | ✓ |
| 2 | 2.2 | $defer → queue, no spawn | — | ✓ | — | ✓ | ✓ | ✓ |
| 2 | 2.3 | $block → escalation | — | ✓ | — | ✓ | ✓ | ✓ |
| 2 | 2.4 | Harvest on exit | — | ✓ | — | ✓ | ✓ | ✓ |
| 2 | 2.5 | Session start handoff | — | ✓ | — | — | — | — |
| 2 | 2.6 | SessionStart inject (Claude) | ✓ | — | — | — | — | — |
| 3 | 3.1 | thegent codex wrapper | — | ✓ | — | — | — | — |
| 3 | 3.2 | Optional codex shim | — | ✓ | — | — | — | — |
| 3 | 3.3 | Exit harvest integration | — | ✓ | — | — | — | — |
| 4 | 4.1 | thegent queue tui | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 4 | 4.2 | queue CLI | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 4 | 4.3 | Atomic claim/lease | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 6 | 6.1 | Team task storage | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 6 | 6.2 | Team MCP tools | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 6 | 6.3 | thegent team create | — | ✓ | — | ✓ | — | — |
| 6 | 6.4 | team message/broadcast/shutdown | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 6 | 6.5 | Display (tmux/TUI) | — | ✓ | — | ✓ | — | — |
| 6 | 6.6 | TeammateIdle | — | ✓ | — | ✓ | — | — |
| 6 | 6.7 | TaskCompleted hook | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 6 | 6.8 | Headless team | — | ✓ | — | ✓ | — | — |
| 9 | 9.1 | Canonical rules format | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 9 | 9.2 | thegent rules sync | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 9 | 9.3 | Rule mapping | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 9 | 9.4 | .cursorrules legacy | — | — | ✓ | — | — | — |
| 10 | 10.1 | run -M cursor-agent | — | — | ✓ | — | — | — |
| 10 | 10.2 | Harvest Cursor transcripts | — | — | ✓ | — | — | — |
| 10 | 10.3 | cursor-api queue/harvest | — | — | ✓ | — | — | — |
| 11 | 11.1 | Droid $defer/$block | — | — | — | ✓ | — | — |
| 11 | 11.2 | Droid harvest on exit | — | — | — | ✓ | — | — |
| 11 | 11.3 | Droid as teammate | — | — | — | ✓ | — | — |
| 11 | 11.4 | Droid rules inject | — | — | — | ✓ | — | — |
| 12 | 12.1 | run -M augment | — | — | — | — | ✓ | — |
| 12 | 12.2 | Context Engine MCP install | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 12 | 12.3 | Augment in registry | — | — | — | — | ✓ | — |
| 13 | 13.1 | run -M opencode | — | — | — | — | — | ✓ |
| 13 | 13.2 | OpenCode in registry | — | — | — | — | — | ✓ |
| Task | Sub-Task | Description | Acceptance |
|------|----------|-------------|------------|
| 1.1 | 1.1a | Create `src/thegent/queue/__init__.py` | Module imports |
| 1.1 | 1.1b | Implement `queue/storage.py` — append, read, list | Unit test: append 3, read 3 |
| 1.1 | 1.1c | Implement `queue/locking.py` — claim, release, extend_lease | Unit test: atomic claim |
| 1.1 | 1.1d | Path resolution: PROJECT/.thegent vs ~/.thegent | Fallback when project empty |
| 1.2 | 1.2a | Update prompt-submit-guard to write .thegent queue | Hook test: $defer → queue |
| 1.2 | 1.2b | Migration: if .claude/pending-queue.jsonl exists and .thegent empty, copy | Migration test |
| 1.2 | 1.2c | Dual-read during transition (read both, write .thegent) | Backward compat |
| 1.4 | 1.4a | Add `thegent codex-notify` subcommand | Parse argv[-1] JSON |
| 1.4 | 1.4b | Handle invalid JSON (log, exit 0) | No crash on malformed |
| 1.4 | 1.4c | Handle unknown type (ignore) | No crash |
| 1.7 | 1.7a | MCP tool: thegent_queue_list | Returns items[] |
| 1.7 | 1.7b | MCP tool: thegent_queue_claim | Atomic claim |
| 1.7 | 1.7c | MCP tool: thegent_queue_done | Mark done |
| 1.7 | 1.7d | MCP tools: add, edit, release, extend_lease | All implemented |
| Task | Sub-Task | Description | Acceptance |
|------|----------|-------------|------------|
| 2.1 | 2.1a | Add flag regex to run_impl: `\$defer|\$pending|\$block|\$idea` | Unit: parse each flag |
| 2.1 | 2.1b | Branch before spawn: if $defer/$pending → queue path | No subprocess |
| 2.1 | 2.1c | Branch: if $block → govern escalate add | Exit 1 |
| 2.2 | 2.2a | queue.append() with ts, prompt, project | Queue has entry |
| 2.2 | 2.2b | Return JSON: `{queued: true, count: N}` | CLI output |
| 2.4 | 2.4a | Register atexit or subprocess callback | On exit |
| 2.4 | 2.4b | Call harvest-pending-queue logic | Handoff written |
| 2.4 | 2.4c | Call harvest-idea-seeds logic | Idea seeds written |
| 2.5 | 2.5a | Read .thegent/next-session-prompts.md | If exists |
| 2.5 | 2.5b | Prepend to stdin before prompt | Exec receives |
| Task | Sub-Task | Description | Acceptance |
|------|----------|-------------|------------|
| 6.1 | 6.1a | Create `src/thegent/team/` module | Module imports |
| 6.1 | 6.1b | team/storage.py: tasks.jsonl read/write | CRUD tasks |
| 6.1 | 6.1c | Path: `.thegent/teams/{id}/tasks.jsonl` | Dir created |
| 6.2 | 6.2a | MCP: thegent_team_create | Returns team_id |
| 6.2 | 6.2b | MCP: thegent_team_task_list, assign, claim, done | All work |
| 6.2 | 6.2c | MCP: thegent_team_message, broadcast, shutdown | All work |
| 6.3 | 6.3a | team create: spawn lead (thegent codex or codex) | Process up |
| 6.3 | 6.3b | team create: spawn N teammates (codex exec -) | N processes |
| 6.3 | 6.3c | Pass task prompt via stdin or file | Teammate receives |
| 6.5 | 6.5a | tmux split panes option | Each teammate in pane |
| 6.5 | 6.5b | In-process TUI option (Shift+Up/Down) | List teammates |
| 6.6 | 6.6a | Poll teammate stdout for idle pattern | Detect |
| 6.6 | 6.6b | Run TeammateIdle hook script | Exit 2 → feedback |
| 6.6 | 6.6c | Inject feedback prompt to teammate | Teammate continues |
| Task | Sub-Task | Description | Acceptance |
|------|----------|-------------|------------|
| 9.1 | 9.1a | Choose canonical: .thegent/rules or .cursor/rules | Decision doc |
| 9.1 | 9.1b | Define .mdc format (description, globs, alwaysApply) | Schema |
| 9.2 | 9.2a | rules/sync.py: read canonical | Parse all |
| 9.2 | 9.2b | Emit .cursor/rules/{name}.mdc | Copy or transform |
| 9.2 | 9.2c | Emit CLAUDE.md section or .claude/skills | Merge |
| 9.2 | 9.2d | Emit .codex/skills/{name}/SKILL.md | Create dir |
| 9.2 | 9.2e | Droid: inject rules into prompt | Prepend |
| 9.3 | 9.3a | Map .mdc globs → Cursor only | N/A for Claude/Codex |
| 9.3 | 9.3b | Map alwaysApply → SessionStart inject (Claude) | — |
| 9.4 | 9.4a | Parse .cursorrules if exists | Legacy |
| 9.4 | 9.4b | Merge into rules or emit as single rule | — |
| Phase | Effort | Blocked By | Unblocks |
|-------|--------|------------|----------|
| 1 | Medium | — | 2, 3, 4, 7 |
| 2 | Medium | 1 | 6 |
| 3 | Small | 1 | — |
| 4 | Medium | 1 | 6 |
| 5 | High | — | — (optional) |
| 6 | High | 2, 4 | 7 |
| 7 | Medium | 6 | — |
| 8 | Small | — | — |
| 9 | Medium | — | 10, 11 |
| 10 | Small | 9 | — |
| 11 | Medium | 9 | — |
| 12 | Small | — | — |
| 13 | Small | — | — |
- [ ] UserPromptSubmit: $defer/$pending queues, $block escalates, $idea saves
- [ ] Stop: harvest-pending-queue flushes to handoff
- [ ] Queue path: unified `.thegent/prompt_queue.jsonl`
- [ ] Queue tools: agent can list, claim, done via MCP
- [ ] Queue TUI: user can add/edit/list
- [ ] Headless: `thegent run -M claude "prompt"` uses `claude -p`
- [ ] SessionStart: optional handoff inject
- [ ] Rules sync: `thegent rules sync` writes to CLAUDE.md
- [ ] Interactive: on exit, harvest runs
- [ ] Headless: $defer, $block, harvest on exit
- [ ] Exec: $defer queues, $block escalates
- [ ] notify: thegent receives AfterAgent JSON
- [ ] Queue tools: agent can list, claim, done via MCP
- [ ] Queue TUI: same as Claude
- [ ] Agent teams: `thegent team create` spawns lead + teammates
- [ ] Rules sync: `thegent rules sync` writes to .codex/skills
- [ ] `thegent run -M cursor-agent "prompt"` headless
- [ ] Harvest: $defer/$pending/$idea from Cursor transcripts
- [ ] Rules sync: `thegent rules sync` writes to .cursor/rules
- [ ] MCP: thegent tools available
- [ ] `thegent run -M droid:name "prompt"` — $defer/$block, harvest on exit
- [ ] Droid as teammate in agent teams
- [ ] Rules injected into droid prompt
- [ ] MCP: thegent tools available
- [ ] `thegent run -M augment "prompt"` — auggie --print
- [ ] Context Engine MCP in thegent mcp install
- [ ] Documented in agent registry
- [ ] `thegent run -M opencode "prompt"` — oc
- [ ] Documented in agent registry
- [ ] Zen: NOT integrated (per ZEN_INTEGRATION.md)
- [ ] Single queue storage for all platforms
- [ ] Unified rules: `thegent rules sync` → Cursor, Claude, Codex, droid
- [ ] Lifecycle: loop can check queue between iterations
- [ ] All features available interactively and headlessly (where applicable)
- [ ] MCP: 30+ tools, 20+ resources, same across all clients
| Dimension | Best-in-Class Platform | thegent Supercede |
|-----------|------------------------|-------------------|
| **Unified queue** | Claude Code (per-platform) | Single .thegent queue; works for Claude, Codex, Cursor, droid, Augment, OpenCode |
| **Unified rules** | Cursor (.cursor/rules) | Single source → sync to 5+ platforms |
| **Unified harvest** | Per-platform scripts | Single harvest from Claude + Codex + Cursor |
| **Teams** | Claude Code / Augment Intent | thegent team: Codex, droid; CLI + MCP; no desktop required |
| **Model routing** | OpenCode Zen (paid) | 12+ providers, free-first (Antigravity, Kilo, NIM) |
| **Orchestration** | Augment Intent (desktop) | CLI + MCP; CI-ready; any agent |
| **MCP surface** | Per-client config | 30+ tools, 20+ resources; install once, use everywhere |
| **Agent coverage** | Single platform | 6 platforms: Claude, Codex, Cursor, droid, Augment, OpenCode |
| Component | Error | Handling |
|-----------|-------|----------|
| **Queue** | Corrupt file | Truncate to last valid line; log; continue |
| **Queue** | Concurrent claim | Atomic rename or lock file; `claimed_by` + `lease_expires_at` |
| **Queue** | Empty project | Fallback to `~/.thegent/prompt_queue.jsonl` |
| **Harvest** | Missing offset | Start from line 0 |
| **Harvest** | Cursor path unknown | Use workspace_path from metadata; fallback grep |
| **Harvest** | Large history | Stream; don't load full file |
| **codex-notify** | Invalid JSON | Log; exit 0 (don't fail Codex) |
| **codex-notify** | Unknown type | Ignore |
| **Rules sync** | Missing target dir | Create `.cursor/rules`, `.codex/skills` |
| **Rules sync** | Conflict | Last-write-wins or configurable merge |
| **run_impl** | Agent not found | Clear error: "Agent X not found. Run thegent list-agents." |
| **run_impl** | $block escalation | Return block message; exit 1 |
| **Team** | Teammate crash | Mark task failed; notify lead |
| **Team** | Lead exit mid-task | Teammates continue; harvest on teammate exit |
| Change | Rollback |
| Queue path .claude → .thegent | Keep dual-read; revert prompt-submit-guard to write .claude |
| codex notify | Remove from config.toml; Codex continues without |
| Rules sync | Manual revert of .cursor/rules, CLAUDE.md, .codex/skills |
| Team module | Remove team create; MCP tools no-op |
| Component | Test Type | Coverage |
|------------|------------|----------|
| **Queue storage** | Unit | append, read, claim, release, extend_lease, concurrent claim |
| **Queue migration** | Integration | .claude exists → migrate → .thegent has data |
| **run_impl preprocessor** | Unit | $defer → no spawn, queue append; $block → exit 1; no flag → spawn |
| **codex-notify** | Unit | Valid JSON → parse; invalid → exit 0; unknown type → ignore |
| **Harvest** | Integration | Mock history files → run harvest → assert output |
| **Rules sync** | Integration | Canonical source → sync → assert .cursor, CLAUDE.md, .codex |
| **Team** | Integration | team create → assert N processes; task assign → teammate receives |
| **prompt-submit-guard** | Unit | $defer stdin → assert queue append, exit |
| **Wrapper exit** | Integration | Spawn codex, kill → assert harvest runs |
| Test | Claude | Codex | Cursor | Droid | Augment | OpenCode |
|------|:------:|:-----:|:------:|:-----:|:-------:|:--------:|
| run -M X "prompt" | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| run -M X "prompt $defer" | ✓ | ✓ | — | ✓ | ✓ | ✓ |
| run -M X "prompt $block" | ✓ | ✓ | — | ✓ | ✓ | ✓ |
| Harvest on exit | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Queue MCP tools | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Rules sync | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Team create | — | ✓ | — | ✓ | — | — |
| Dimension | Platform Native | thegent |
|------------|------------------|---------|
| **Run registry** | — | `.thegent/sessions/run_registry.jsonl` |
| **Contract telemetry** | — | `.thegent/sessions/contract_telemetry.jsonl` |
| **Escalation queue** | — | `.thegent/sessions/escalation_queue.jsonl` |
| **Circuit breakers** | — | `.thegent/sessions/circuit_breakers.jsonl` |
| **Cost governance** | — | thegent govern; cost caps |
| **Quality gates** | Claude hooks | hooks/quality-gate.sh; spec-verifier |
| **Health gate** | — | thegent_session_contract_health_gate |
| **Observe summary** | — | thegent_observe_summary |
| Governance | Claude | Codex | Cursor | thegent |
|------------|:------:|:-----:|:------:|---------|
| PreToolUse block | ✓ | ✗ | ✗ | N/A exec |
| Cost cap | — | — | — | thegent govern |
| Quality gate | Stop hook | — | — | quality-gate.sh |
| Escalation | $block | — | — | govern escalate |
| Spec traceability | — | — | — | spec-verifier |
| Dimension | Contract | SLO | Gate |
|------------|----------|-----|------|
| **Session routing** | route_contract | Resolved provider | session_contract_health_gate |
| **Model availability** | ModelCatalog | Route exists | list_models |
| **Fallback rate** | — | `&lt;5%` structural, `&lt;10%` semantic | observe_summary |
| **Queue latency** | — | append `&lt;10ms` | — |
| **Harvest completeness** | — | All sources processed | — |
| **FR traceability** | spec-verifier | 100% FRs have tests | spec-verifier |
| **Health ratio** | — | min_healthy_ratio 1.0 | session_contract_health_gate |
| Risk | Mitigation |
|------|------------|
| Platform config changes | Version check; graceful fallback; merge, don't overwrite |
| Client MCP gaps (elicitation, progress) | Queue/blocking uses hooks, not MCP elicitation |
| Codex notify payload change | Parse with fallback; log unknown types |
| Queue file corruption | Append-only; atomic writes; lock file |
| Rules sync conflicts | Last-write-wins or configurable merge |
| Droid/oc not installed | Detect; clear error; document in install guide |
| Teammate crash | Mark task failed; notify lead; optional restart |
| Harvest path changes | Configurable paths; fallback resolution |
| Config overwrite | Merge only; never replace entire config |
| notify script blocks | Codex spawns async; fire-and-forget |
| Platform | Risk | Mitigation |
|----------|------|------------|
| Codex | notify blocks | Async spawn; timeout optional |
| Cursor | Transcript path varies | Multiple path patterns; workspace_path metadata |
| Droid | droid not in PATH | Check ~/.local/bin, ~/.factory/bin; clear error |
| Augment | auggie not installed | Detect; suggest install; fallback message |
| OpenCode | Zen cost | Do not integrate Zen (ZEN_INTEGRATION.md) |
| Purpose | Path |
|---------|------|
| Queue (project) | `PROJECT/.thegent/prompt_queue.jsonl` |
| Queue (global) | `~/.thegent/prompt_queue.jsonl` |
| Queue (legacy) | `~/.claude/pending-queue.jsonl`, `PROJECT/.claude/pending-queue.jsonl` |
| Team tasks | `.thegent/teams/{team_id}/tasks.jsonl` |
| Handoff | `docs/research/pending-handoff.md`, `.thegent/next-session-prompts.md` |
| Idea seeds | `docs/research/idea-seeds/seed_{source}_{ts}_{id}.md` |
| Harvest offsets | `~/.claude/.idea-harvest-{claude,codex,cursor}-*` |
| Claude history | `~/.claude/history.jsonl` |
| Codex history | `~/.codex/history.jsonl` |
| Cursor transcripts | `~/.cursor/projects/Users-*/agent-transcripts/*.jsonl` |
| Run registry | `.thegent/sessions/run_registry.jsonl` |
| Escalation | `.thegent/sessions/escalation_queue.jsonl` |
| Rules (canonical) | `.thegent/rules/` or `.cursor/rules/` |
| Codex skills | `.codex/skills/{name}/SKILL.md` |
| Cursor rules | `.cursor/rules/{name}.mdc` |
| Factory droids | `.factory/droids/*.md` |
| Step | Action | Source |
|------|--------|--------|
| 1 | Resolve alias (cursor-api → cursor) | _AGENT_ALIASES |
| 2 | Direct agent? (cursor, claude, codex, gemini, copilot) | DIRECT_AGENTS |
| 3 | Proxy agent? (antigravity, kilo, nim, cliproxy, etc.) | PROXY_AGENTS |
| 4 | Droid? (droid:name) | .factory/droids/*.md |
| 5 | Teammate from agents/*.md? | WP-16001 |
| 6 | Unknown | Return None; "Agent X not found" |
| Command | Purpose | Platforms |
|---------|---------|-----------|
| thegent run -M {agent} "prompt" | Headless run | All |
| thegent bg -M {agent} "prompt" | Background run | All |
| thegent codex / dex / clode | Interactive wrapper | Codex, Claude |
| thegent queue add\|list\|edit\|release\|status | Queue CLI | All |
| thegent queue tui | Queue TUI | All |
| thegent team create\|list\|message\|shutdown | Team CLI | Codex, Droid |
| thegent rules sync | Rules sync | All |
| thegent govern escalate add\|list\|resolve | Escalation | All |
| thegent codex-notify | Codex notify handler | Codex |
| thegent serve | MCP HTTP server | All |
| thegent mcp install {cursor,codex,...} | MCP config | All |
| thegent list-agents | List agents | All |
| thegent list-droids | List droids | All |
| thegent list-models | List models | All |
| thegent ps / status / logs / inspect | Session discovery | All |
| thegent loop / loop-takeover / loop-stop | Lifecycle | All |
| Agent | Output Format | thegent Extraction |
|-------|---------------|-------------------|
| Claude | Stream or JSON | OUTPUT_PARSER_SCHEMA_VERSION; `&lt;think>`, \`&lt;action\>` |
| Codex | Stream; --json for JSONL | Passthrough; optional parse |
| Droid | stream-json | Passthrough |
| Augment | — | Passthrough |
| OpenCode | — | Passthrough |
| Pipeline | Hooks | Triggers |
|----------|-------|----------|
| **quality-gate** | Stop | lint, test, coverage, traceability |
| **spec-verifier** | Stop | FR traceability, orphan check |
| **security-pipeline** | Stop | gitleaks, SAST, dependency audit |
| **suppression-blocker** | PreToolUse: Edit, Write | Block new lint suppressions |
| **prompt-submit-guard** | UserPromptSubmit | $defer, $block, $idea |
| **harvest-pending-queue** | Stop | Flush queue to handoff |
| **harvest-idea-seeds** | Stop | Extract $idea from history |
| Tool Category | Tools | Platforms Using |
|---------------|-------|-----------------|
| **Run** | thegent_run, thegent_bg, thegent_do_next | All (via MCP) |
| **Queue** | thegent_queue_list, claim, done, add, edit, release, extend_lease | All (Phase 1) |
| **Team** | thegent_team_create, task_list, task_assign, task_claim, task_done, message, broadcast, shutdown | Codex, Droid (Phase 6) |
| **Discovery** | thegent_ps, status, logs, inspect, list_agents, list_droids, list_models | All |
| **Contract** | session_contracts, health_gate, health_report, health_trend | All |
| **Observe** | thegent_observe_summary | All |
| **Inbox** | thegent_inbox_list, thegent_inbox_wait | All |
| **Planning** | thegent_dag_list, thegent_do_next | All |
| **Terminal** | thegent_terminal_list, inspect, send, attach | All (tmux) |
| **Loop** | thegent_loop, thegent_loop_takeover, thegent_loop_stop | All |
| Proxy | Backend | Models | thegent run |
|-------|---------|--------|-------------|
| antigravity | CLIProxyAPIPlus | Claude, Gemini (free) | run -M antigravity |
| kilo | CLIProxyAPIPlus | Kimi K2.5, DeepSeek, GLM, MiniMax, Qwen (free) | run -M kilo |
| nim | CLIProxyAPIPlus | DeepSeek, Llama Nemotron (free) | run -M nim |
| cliproxy | CLIProxyAPIPlus | Configurable | run -M cliproxy |
| minimax | CLIProxyAPIPlus | MiniMax | run -M minimax |
| glm | CLIProxyAPIPlus | GLM | run -M glm |
| Platform | Status | Notes |
|----------|--------|-------|
| **GooseAI** | Consideration | Inference API, not coding agent; could be model provider |
| **Windsurf** | Consideration | IDE agent; similar to Cursor |
| **Replit Agent** | Consideration | Cloud-based; different model |
| **GitHub Copilot** | Consideration | Already via run -M copilot; limited |
| **Bolt (StackBlitz)** | Consideration | Web IDE agent |
| **Continue** | Consideration | VS Code extension; MCP support |
| Component | Purpose | Platforms |
|-----------|---------|-----------|
| **thegent sitback** | Launch Claude Code with Sitback Agent | Claude Code |
| **Sitback dashboard** | MCP resource: thegent://sitback/dashboard | All (cached 30s) |
| **thegent queue tui** | Textual TUI for queue | All |
| **Terminal tools** | thegent_terminal_list, inspect, send, attach | tmux |
| **heliosShield** | thegent_heliosShield_status | Multi-agent coordination |
| Symptom | Check | Resolution |
|---------|-------|------------|
| run -M X fails | `thegent list-agents` | Add agent to registry; check PATH |
| $defer not queuing | run_impl preprocessor | Ensure regex matches; check queue path |
| codex-notify not firing | ~/.codex/config.toml notify | Add ["thegent","codex-notify"]; merge |
| Harvest empty | Offset files; history paths | Reset offset; verify path exists |
| Rules sync overwrote | Conflict strategy | Use last-write-wins or backup before sync |
| Team teammate not receiving | stdin pipe | Verify task prompt on stdin |
| MCP tools not visible | Client MCP config | thegent mcp install {client} |
| Queue claim fails | claimed_by, lease | Release stale; extend_lease |
| Cursor harvest fails | Transcript path | Check ~/.cursor/projects/*/agent-transcripts |
| Command | Purpose |
|---------|---------|
| `thegent ps --all` | List all sessions including completed |
| `thegent inspect --owner X` | Deep session inspection |
| `thegent session-contracts --missing-only` | Contract gaps |
| `thegent observe-summary` | KPIs, drift, escalations |
| `thegent govern escalate list --past-sla` | Blocked items |
| `thegent list-models --by-model` | Model → provider routing |
| Metric | Target | Notes |
|--------|--------|------|
| run_impl preprocessor | `&lt;50ms` | Before spawn |
| Queue append | `&lt;10ms` | Atomic write |
| codex-notify parse | `&lt;5ms` | Fire-and-forget |
| MCP tool latency | `&lt;500ms` (read) | Exclude run, bg |
| thegent_run | Agent-dependent | Progress every 10s |
| Harvest (full) | `&lt;30s` | Stream; don't load all |
| Rules sync | `&lt;5s` | Per rule |
| Queue TUI render | `&lt;100ms` | Cached where possible |
| Operation | Safe? | Notes |
|-----------|-------|-------|
| Queue append | Yes | Append-only; atomic |
| Queue claim | Yes | claimed_by + lease; atomic |
| Harvest (multi-source) | Yes | Per-source offset; no shared state |
| Rules sync | Caution | Last-write-wins; avoid concurrent sync |
| Team task update | Yes | JSONL append or file lock |
| Policy | Behavior | Use Case |
|--------|----------|----------|
| prefer_direct | Direct API first (OpenAI, Anthropic, etc.) | Default |
| prefer_proxy | Proxy first (Antigravity, Kilo, NIM) | Free-first |
| failover | Try direct; on failure try next route | Resilience |
| round_robin | Rotate across providers | Load spread |
| cheapest | Lowest cost route | Cost optimization |
| Category | Item | Multi-Platform Application |
|----------|------|----------------------------|
| **Performance** | OPT-021 span attributes | Add model, provider, platform to run_impl spans |
| **Performance** | OPT-002 rate limiting | MCP already has 10/s; queue TUI debounce |
| **Performance** | OPT-020 route memo | Model-first routing in run_impl; cache resolved route |
| **Robustness** | ROB-013 config validation | Validate queue path, harvest paths on startup |
| **Robustness** | ROB-007 graceful shutdown | MCP drain; wrapper waits for harvest |
| **Robustness** | ROB-005 idempotency | Queue claim: idempotent release; extend_lease idempotent |
| **UX** | UX-001 tool annotations | Queue tools: readOnlyHint, idempotentHint |
| **UX** | UX-005 actionable errors | "Agent X not found. Run: thegent list-agents" |
| **UX** | UX-008 progressive disclosure | Queue TUI: list → inspect → claim |
| **DX** | DX-003 thegent inspect | Already exists; ensure queue/team visibility |
| Area | Polish | Rationale |
|------|--------|-----------|
| **Queue** | `thegent queue status` — one-line summary (N pending, M claimed) | Quick glance |
| **Queue** | Lease expiry warning in TUI when `&lt;2min` left | Avoid accidental release |
| **Harvest** | Progress indicator for large history (streaming) | UX for big transcripts |
| **Rules sync** | `--dry-run` to preview changes | Safe trial |
| **Team** | `thegent team status` — lead + teammates, task counts | At-a-glance |
| **run -M** | Suggest fallback agent on "not found" | Self-service |
| **codex-notify** | Structured log line (thread_id, turn_id) for traceability | Debugging |
| Tier | Scope | Examples |
|------|-------|----------|
| **Tier 1 (Must)** | Parity + robustness | Queue, harvest, rules sync, team; error handling |
| **Tier 2 (Should)** | Polish + observability | Queue TUI, status commands, span attributes |
| **Tier 3 (Nice)** | Convenience | --dry-run, lease warning, fallback suggestion |
| **Tier 4 (Defer)** | Speculative | Multi-queue namespaces, rule versioning |
| Principle | Application |
|-----------|-------------|
| **Consistent entry** | `thegent run -M {agent}` for all agents; same flags (--cd, --timeout) |
| **Predictable output** | JSON when --json; text when not; same schema across agents |
| **Discoverable** | `thegent list-agents`, `thegent queue --help`; no hidden commands |
| **Composable** | Queue + harvest + rules are independent; combine via flows |
| **Fail fast** | Config validation on startup; agent not found before spawn |
| **Clear feedback** | "Queued. 3 pending." not "Done."; "Agent X not found" with hint |
| Principle | Application |
|-----------|-------------|
| **Explicit failure** | No silent degradation; $block returns block message, exit 1 |
| **Atomic operations** | Queue claim: atomic; append: atomic write |
| **Idempotent where safe** | Queue release, extend_lease; rules sync |
| **Bounded state** | Lease expiry; max queue size (optional); harvest offset |
| **Recoverable** | Queue corruption → truncate; harvest offset missing → start 0 |
| **Observable** | run_registry, escalation_queue, health gate |
| Avoid | Prefer |
| Generic "orchestration framework" | Queue, team, rules as focused modules |
| Rule versioning before first conflict | Last-write-wins; add versioning if needed |
| Multi-queue namespaces before use case | Single queue; project vs global is enough |
| Custom DSL for rules | .mdc + YAML frontmatter (standard) |
| Abstract "agent adapter" interface | get_runner() + registry (concrete) |
| Event bus for internal comms | Direct calls; file/JSONL for persistence |
| Journey | Steps | Platforms |
|---------|-------|-----------|
| **Defer and resume** | Prompt with $defer → queue → exit → next session → handoff inject → user continues | Claude, Codex, Droid, Augment, OpenCode |
| **Block and escalate** | Prompt with $block → escalate → resolve via CLI → retry | All |
| **Idea capture** | Prompt with $idea → save to idea-seeds → harvest on Stop | Claude, Codex, Cursor |
| **Multi-agent team** | team create → assign tasks → teammates execute → done → shutdown | Codex, Droid |
| **Unified rules** | Edit .thegent/rules → rules sync → all platforms updated | All |
| **Cross-platform run** | run -M codex "X" then run -M claude "Y" — same queue, same harvest | All |
- [ ] Defer → queue → exit → next session sees handoff
- [ ] Block → escalate → resolve → can retry
- [ ] Idea → idea-seeds file created
- [ ] Team create → N processes → tasks flow → shutdown clean
- [ ] Rules sync → Cursor, Claude, Codex, droid all updated
- [ ] run -M X for each platform works
- [ ] Queue TUI: add, list, claim, done
- [ ] Harvest from Claude + Codex + Cursor in one run
- [ ] MCP tools work from Claude Code, Cursor, Codex
| Need | Location |
|------|----------|
| Design philosophy | §0 |
| End-to-end flows | §10 (Session, Queue→Harvest→Handoff, Rules, Team) |
| Optimization & polish | §11 (OPT/ROB/UX mapping, tiers) |
| Intuitive & robust design | §12 |
| Complete plan & verification | §13 |
| Phase tasks | §4.3 Task-Level Matrix |
| Granular sub-tasks | §4.4 (Phase 1), §4.4b (Phase 2), §4.4c (Phase 6), §4.4d (Phase 9) |
| Hooks pipeline | §2.4 |
| Sandbox/permission models | §2.5 |
| Platform strategy | §3 Platform-by-Platform |
| Implementation depth | §3a |
| Platform variants | §3b |
| Success criteria | §5 |
| Supercede opportunities | §2.4, §6 |
| Hook-by-hook strategy | §2.3 |
| Extended capabilities | §2.2 |
| Error handling | §6a |
| Testing strategy | §6b |
| Observability | §6c |
| File paths | §8.1 |
| Schemas | §8.2–8.4 |
| Config merge | §8.5 |
| Run state machine | §8.6 |
| Agent discovery | §8.7 |
| CLI commands | §8.8 |
| Output parsing | §8.9 |
| Quality/security pipeline | §8.10 |
| MCP coverage | §9 |
| Proxy agents | §9a |
| Future platforms | §9b |
| Sitback/TUI | §9c |
| Debugging/troubleshooting | §9d |
| SLO/performance | §9e |
| Model routing policies | §9f |
| Migration script steps | §9g |
| Detailed phase breakdown | [CODEX_DONUT_HARNESS_PLAN.md](./CODEX_DONUT_HARNESS_PLAN.md) |
| Schemas, MCP, configs | [MULTI_PLATFORM_DEEP_DIVE.md](../research/MULTI_PLATFORM_DEEP_DIVE.md) |
| Feature audit | [CLAUDE_CODE_FEATURE_PARITY_AUDIT.md](../research/CLAUDE_CODE_FEATURE_PARITY_AUDIT.md) |
| Config pattern | Fit? | Notes |
|----------------|------|-------|
| `openai-compatibility` + `api-key-entries` | ✗ | Keys from `/build-key` expire; not static |
| Token-file / OAuth (like Kiro) | ✓ | Needs token refresh, session management |
| Dedicated `cursor:` block | ✓ | Similar to `kiro:` with `token-file`, `access-token`, `refresh-token` |
| Config pattern | Fit? | Notes |
|----------------|------|-------|
| `openai-compatibility` + `api-key-entries` | ✓ | For API-key-only usage |
| Dedicated `minimax:` block (OAuth) | ✓ | For OAuth flow, like GLM/Kiro |
| Project | What | Relevance |
|---------|------|-----------|
| [router-for-me/CLIProxyAPI #573](https://github.com/router-for-me/CLIProxyAPI/issues/573) | Cursor support request – "force cursor to call models through local proxy" | Cursor + CLIProxy |
| [router-for-me/CLIProxyAPIPlus #198](https://github.com/router-for-me/CLIProxyAPIPlus/issues/198) | Cursor CLI / Auth support – Cursor subscription as provider, auth storage like Codex | Cursor auth integration |
| [forum.cursor.com – proxy setup](https://forum.cursor.com/t/how-to-set-up-a-proxy-for-cursor/83585) | mitmproxy + Cursor – TLS handshake issues with api2.cursor.sh | Proxy challenges |
| [forum.cursor.com – CLI proxy](https://forum.cursor.com/t/cursor-cli-with-proxy/133724) | Cursor CLI + http_proxy/https_proxy – env vars don't work | CLI proxy config |
| [wisdgod/cursor-api](https://github.com/wisdgod/cursor-api) | OpenAI-compatible proxy to Cursor backend; token management | Primary cursor-api |
| [cursor.com/docs/enterprise/network-configuration](https://cursor.com/docs/enterprise/network-configuration) | Enterprise proxy, firewalls, encryption | Official docs |
| Project | What | Relevance |
|---------|------|-----------|
| [platform.minimax.io – OpenAI API](https://platform.minimax.io/docs/api-reference/text-openai-api) | MiniMax native OpenAI-compatible API | Direct integration |
| [0xSero/minimax-m2-proxy](https://github.com/0xSero/minimax-m2-proxy) | Translation proxy: MiniMax-M2 → OpenAI/Anthropic APIs; tool-calling, reasoning | Self-hosted MiniMax-M2 |
| [LLM-Red-Team/minimax-free-api](https://github.com/LLM-Red-Team/minimax-free-api) | Proxy: OpenAI format → Hailuo AI; token management | Free API proxy |
| [LiteLLM – MiniMax-M2.5](https://docs.litellm.ai/blog/minimax_m2_5) | Day 0 support via LiteLLM AI Gateway | Gateway option |
| [ai-sdk.dev – MiniMax provider](https://ai-sdk.dev/providers/community-providers/minimax) | createMinimax (Anthropic), createMinimaxOpenAI | SDK integration |
| [minimax-m2.com/docs/api](https://minimax-m2.com/docs/api) | RESTful OpenAI/Anthropic-style API | Alternative deployment |
| Project | What | Relevance |
|---------|------|-----------|
| [router-for-me/CLIProxyAPIDocs – Factory Droid](https://deepwiki.com/router-for-me/CLIProxyAPIDocs/6.4-factory-droid-configuration) | Official Factory Droid + CLIProxyAPI config | Canonical docs |
| [chandika – Factory + CLIProxyAPI gist](https://gist.github.com/chandika/c4b64c5b8f5e29f6112021d46c159fdd) | Droid + Claude Code Max (OAuth) via CLIProxyAPI | OAuth instead of API keys |
| [ObaidUr-Rahmaan – same pattern](https://gist.github.com/ObaidUr-Rahmaan/131b2cf6c87da191fa01a697f9d60027) | Droid + Claude/Codex subscription via CLIProxyAPI | Community guide |
| [xkonjin/droid-proxy-setup](https://github.com/xkonjin/droid-proxy-setup) | Auto-start CLIProxyAPI for Droid; Claude Pro Max, ChatGPT Pro Max, Antigravity | Setup automation |
| [xkonjin – CLIProxy setup gist](https://gist.github.com/xkonjin/d65abd20d98d113b1c0a447d7a7862ce) | Factory Droid + CLIProxyAPI (Claude OAuth) – verified Jan 2026 | Working config |
| [ben-vargas – Droid config gist](https://gist.github.com/ben-vargas/c41cdf36736d802f04b8e6b54aa2d6ec) | Droid + CLIProxyAPI for ChatGPT/Claude/Gemini | Multi-provider |
| [edlsh/ai-cli-proxy-api](https://github.com/edlsh/ai-cli-proxy-api) | CLIProxyAPI fork for Factory + Amp; USING_WITH_FACTORY_AND_AMP.md | Fork with guides |
| [tiendung/ai-cli-proxy-api](https://github.com/tiendung/ai-cli-proxy-api) | Same enhancement – Factory + Amp | Another fork |
| Project | What | Relevance |
|---------|------|-----------|
| [mrsuperei/CLIProxyAPI-Extended](https://github.com/mrsuperei/CLIProxyAPI-Extended) | Kiro, Antigravity; Canonical IR | Proxy |
| [khmuhtadin/cliproxy-installer](https://github.com/khmuhtadin/cliproxy-installer) | Installer for Cursor, Claude Code, OpenCode, Droid | Setup |
| [julianromli/CLIProxyAPIPlus-Easy-Installation](https://github.com/julianromli/CLIProxyAPIPlus-Easy-Installation) | Droid, Claude Code, Cursor | OAuth + proxy |
| Provider | Auth type | CLIProxyAPIPlus config | Status |
|----------|-----------|------------------------|--------|
| OpenRouter | API key | `openai-compatibility` | ✓ Implemented |
| Cursor | Session token (login) | Dedicated `cursor:` block (like Kiro) | ✗ Wrong docs; needs plan |
| MiniMax | OAuth + API key (like GLM) | `openai-compatibility` or dedicated block | Both supported |
| Kilo | Free credits / optional API key | TBD | Research Kilo provider auth |
| Roo Code | OpenAI-compat / Cloud | TBD | Research |
| Kiro | OAuth (token-file, access/refresh) | `kiro:` | ✓ Reference |
| Question | Answer |
|----------|--------|
| **Bifrost** | Not used. No dependency. Design doc (LITELLM_CLIPROXY_BIFROST_HARMONY) recommends against for thegent (no Python SDK; agent-scale doesn't need 50x speed). |
| **LiteLLM** | Not used. No dependency. WP-1001 (LiteLLM fallback chains) is "Not Started". Design recommends "Future LiteLLM" as in-process router. |
| **CLIProxyAPIPlus** | Used. Go project at `../CLIProxyAPIPlus-fork/`. Holds auth (OAuth, API keys), API execution, model routing by config. |
| **thegent** | Python. Config generation, credential copy from factory, agent selection, model mapping. No live TPS/latency/cost measurement. |
| Criterion | Bifrost | LiteLLM |
|-----------|---------|---------|
| **Language** | Go | Python |
| **Integration** | Separate process; extensions (bifrost-cliproxy) | In-process Router class or Proxy server |
| **Provider count** | 15–21 | 100+ |
| **thegent fit** | Would need Go extension; thegent is Python | Native Python; can use Router in-process |
| **Auth** | Bifrost has its own; CLIProxy has OAuth | LiteLLM proxies to backends; CLIProxy = OAuth backend |
| **Recommendation** | Out for now | Preferred for routing layer |
- [ ] Add litellm as optional dependency
- [ ] Use LiteLLM Router for direct-API providers; CLIProxy for OAuth
- [ ] Or: LiteLLM Proxy as front door, CLIProxy as backend (Option B from LITELLM doc)
| Area | Current | Needed |
|------|---------|--------|
| Models (all) | Unit tests for minimax, glm, nim | Extend to validate all model→provider mappings |
| TPS measurement | None | Integration test: proxy records TPS; endpoint returns it |
| Latency measurement | test_load_mcp (p95 for ps) | Per-provider latency from proxy |
| Cost/usage limits | CostAggregator, CostEstimator | Tests for usage-limit detection, budget enforcement |
| Gap | Fix |
|-----|-----|
| No post-install hint | After `pip install thegent`, print: "Run `thegent setup` to configure. Run `thegent doctor` to verify." (via post-install script or README) |
| `thegent` with no args | `no_args_is_help=True` — good. Consider adding a "quick start" hint in the help footer |
| Version visibility | Add `thegent --version` (Typer default). Ensure it's prominent |
| ID | Item | Priority | Effort | Impact |
|----|------|----------|--------|--------|
| 1 | Add `thegent doctor` to main CLI | P0 | S | H |
| 2 | Bootstrap error handling (no silent fail) | P0 | S | H |
| 3 | Shell completion (--install-completion) | P1 | S | M |
| 4 | First-run hint (post-install) | P1 | S | M |
| 5 | Actionable error messages | P1 | M | H |
| 6 | doctor --fix completeness | P2 | M | M |
| 7 | README/INSTALLATION alignment | P2 | S | M |
| 8 | thegent (no args) quick start panel | P2 | S | M |
| 9 | QUICK_REFERENCE.md | P2 | S | M |
| 10 | In-CLI help examples (epilog) | P2 | S | M |
| 11 | Nix package deps (overlay/mach-nix) | P2 | M | M |
| 12 | Graceful degradation (optional tools) | P2 | S | M |
| 13 | CLI startup profiling | P2 | M | M |
| 14 | Upgrade check | P3 | M | L |
| 15 | Config wizard improvements | P3 | M | L |
| 16 | Project detection hints | P3 | S | L |
| Task ID | Title | Files | Effort | Status | Source |
|---------|-------|-------|--------|--------|--------|
| **IMPL-LIB-001** | Replace urllib with httpx | 7+ files | 2-3 hrs | ⏳ Pending | Phase 1 |
| **IMPL-LIB-002** | Migrate retry to tenacity | 4 files | 4-6 hrs | ⏳ Pending | Phase 2 |
| **IMPL-LIB-003** | Replace polling with watchdog | 1 file | 2-4 hrs | ⏳ Pending | Phase 3 |
| Task ID | Title | Files | Effort | Status | Source |
|---------|-------|-------|--------|--------|--------|
| **IMPL-LIB-101** | Replace custom caching with cachetools | 5+ files | 2-3 hrs | ⏳ Pending | Phase 5 |
| **IMPL-LIB-102** | Replace circuit breaker with pybreaker | 1 file | 2-3 hrs | ⏳ Pending | Phase 8 |
| **IMPL-LIB-103** | Replace PyYAML with ruamel.yaml | 15+ files | 3-4 hrs | ⏳ Pending | Phase 4.3 |
| **IMPL-LIB-104** | Replace ANSI stripping with rich | 5 files | 1 hr | ⏳ Pending | Phase 4 |
| **IMPL-LIB-105** | Replace scrapers cache with diskcache | 1 file | 1 hr | ⏳ Pending | Phase 6 |
| **IMPL-LIB-106** | Add psutil for resource monitoring | 2 files | 2-3 hrs | ⏳ Pending | Phase 7 |
| Task ID | Title | Files | Effort | Status | Source |
|---------|-------|-------|--------|--------|--------|
| **IMPL-LIB-201** | Replace md5 with sha256 | 1 file | 0.5 hr | ⏳ Pending | Phase 9 |
| ~~**IMPL-LIB-202**~~ | ~~Consolidate os.environ → ThegentSettings~~ | ~~40+ files~~ | ~~2-3 hrs~~ | ✅ **COMPLETED** | Phase 10 |
| **IMPL-LIB-203** | Replace _CWD_CACHE with cachetools | 1 file | 0.5 hr | ⏳ Pending | Phase 21 |
| **IMPL-LIB-204** | Add tomlkit to dependencies | pyproject.toml | 0.5 hr | ⏳ Pending | Phase 19 |
- [ ] All urllib imports removed
- [ ] All HTTP calls use httpx
- [ ] Exception handling updated
- [ ] Tests pass
- [ ] No regressions in functionality
- [ ] All manual retry loops replaced with tenacity decorators
- [ ] Retry behavior matches original
- [ ] Tests pass
- [ ] Performance maintained or improved
- [ ] `watchdog>=4.0.0` added to dependencies
- [ ] Polling replaced with Observer
- [ ] FileSystemEventHandler implemented
- [ ] exclude_dirs behavior preserved
- [ ] Tests pass
- [ ] CPU usage reduced
- [ ] `cachetools>=5.0.0` added to dependencies
- [ ] All custom caches replaced with TTLCache
- [ ] Cache behavior matches original
- [ ] Tests pass
- [ ] Memory usage improved
- [ ] `pybreaker>=1.0.0` added to dependencies
- [ ] Custom circuit breaker replaced
- [ ] State machine behavior matches
- [ ] Tests pass
- [ ] Thread-safe operation verified
- [ ] `ruamel.yaml>=0.18.0` added to dependencies
- [ ] All PyYAML imports replaced
- [ ] Comments preserved in config files
- [ ] Key order preserved
- [ ] Tests pass
- [ ] Round-trip safety verified
- [ ] Create `thegent.utils.strip_ansi` utility
- [ ] Replace all custom ANSI stripping
- [ ] Tests pass
- [ ] Edge cases handled correctly
- [ ] `diskcache>=5.0.0` added to dependencies
- [ ] File-based cache replaced
- [ ] TTL behavior matches
- [ ] Tests pass
- [ ] Disk usage optimized
- [ ] `psutil>=5.9.0` added to dependencies
- [ ] Subprocess-based monitoring replaced
- [ ] Cross-platform compatibility verified
- [ ] Tests pass
- [ ] Performance improved
- [ ] md5 replaced with sha256
- [ ] Tests pass
- [ ] No breaking changes
- [ ] All THGENT_* env vars in ThegentSettings
- [ ] os.environ.get calls replaced
- [ ] Type validation working
- [ ] Tests pass
- [ ] Default values preserved
- [ ] _CWD_CACHE replaced with TTLCache
- [ ] TTL behavior matches
- [ ] Tests pass
- [ ] `tomlkit>=0.12.0` added to dependencies
- [ ] No breaking changes
| Risk | Impact | Mitigation |
|------|--------|------------|
| API incompatibility | High | Comprehensive testing, gradual migration |
| Behavior changes | Medium | Feature flags, rollback plan |
| Performance regression | Low | Benchmarking, monitoring |
| Dependency issues | Medium | Version pinning, dependency audit |
| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking changes | High | Backward compatibility, feature flags |
| Testing gaps | Medium | Comprehensive test coverage |
| Rollback complexity | Medium | Phased rollout, monitoring |
| Task | Effort | Impact | Ready For |
|------|--------|--------|-----------|
| **WBS Document** | 20 min | HIGH | Team dispatch, task assignment, dependency tracking |
| **Rust Scaffold** | 15 min | HIGH | P1.1.2-6 implementation (4+ commits) |
| **Cache Interface** | 10 min | HIGH | P1.2.2-5 implementation (8+ commits) |
| impl-supermemory-p1.1 | Supermemory Client (Rust) | P1 | Critical | — |
| impl-supermemory-p1.2 | L1/L2 Cache (Python) | P1 | — | impl-supermemory-p1.1 |
| impl-supermemory-p1.3 | Config & Setup | P1 | — | impl-supermemory-p1.2 |
- [ ] Review `docs/reference/SUPERMEMORY_PHASE1_WBS.md` for accuracy
- [ ] Adjust effort estimates if needed (currently: 13 pd / 3 days)
- [ ] Assign to implementation teams
- [ ] Add to WORK_STREAM.md (BACKLOG section)
- [ ] P1.1.2 (Auth module) implemented + tested
- [ ] P1.2.2 (Redis provider) implemented + tested
- [ ] P1.3.1 (Config system) implemented + tested
- [ ] P1.1 complete (Client SDK ready)
- [ ] P1.2 complete (Cache providers tested)
- [ ] P1.3 complete (CLI + MCP integration)
- [ ] All tests pass, docs complete
- [ ] Ready for Phase 2 kickoff
| Phase | Work | Time | Tool Calls |
|-------|------|------|-----------|
| ✅ **P1 Planning + Foundations** | WBS + 3 scaffolds | ~45 min | ~90 calls |
| ⏳ **P1.1.2-6** | Auth, Client, APIs, Tests | 4-5 days | 40-50 calls |
| ⏳ **P1.2.2-5** | Redis, FileCache, Tests | 3-4 days | 30-40 calls |
| ⏳ **P1.3.2-5** | CLI, MCP, Docs, Health | 2-3 days | 20-30 calls |
- [ ] Implement ValueEstimator class
- [ ] Estimate complexity (1-10 scale)
- [ ] Estimate business impact (1-10 scale)
- [ ] Estimate user priority (1-10 scale)
- [ ] Formula: 0.3×complexity + 0.5×impact + 0.2×priority
- [ ] Calculate confidence (0.6-0.9 range)
- [ ] Unit tests with 5+ scenarios (>90% coverage)
- [ ] Implement CostEstimator class
- [ ] Estimate tokens by task type (trivial=100 tokens, feature=1000)
- [ ] Calculate cost: (tokens / 1M) × provider.cost_per_1m_tokens
- [ ] Apply size multipliers from task hints
- [ ] Calculate confidence (0.75 typical, range 0.6-0.9)
- [ ] Use ProviderRegistry.get(provider_id) for provider pricing
- [ ] Unit tests with 5+ provider/task combinations
- [ ] Define 20+ task types with token estimates
- [ ] Categories: trivial, simple, standard, feature, complex, integration, etc.
- [ ] Each with: input_tokens_min, input_tokens_max, output_tokens_avg
- [ ] Size multipliers: small (0.5×), medium (1.0×), large (2.0×), huge (5.0×)
- [ ] Documentation of methodology
- [ ] Version history for calibration tracking
| Component | Target | Target Met in 2.1 |
|-----------|--------|-------------------|
| Value estimation | `&lt;5ms` | N/A (Phase 2.2) |
| Cost estimation per provider | `&lt;10ms` | N/A (Phase 2.2) |
| Combined latency | `&lt;15ms` | N/A (Phase 2.2) |
| Provider lookups | `&lt;1ms` | ✅ Verified |
- [ ] Value estimator implemented and tested
- [ ] Cost estimator implemented and tested
- [ ] Token database created and validated
- [ ] All unit tests passing (>90% coverage)
- [ ] Integration tests passing
- [ ] Value & cost estimation functional (Phase 2.2)
- [ ] All Phase 2.1-2.2 tests passing
- [ ] Phase 2.2 implementation can begin immediately
| Task ID | Description | Status |
|---------|-------------|--------|
| **MTSP-01** | Unified MCP Host | ✅ Done |
| **MTSP-02** | In-Process Agent Runner | ⏳ Pending |
| **MTSP-03** | Shared Task Worker | ⏳ Pending |
| **MTSP-04** | LSP Multiplexing | ⏳ Pending |
| **MTSP-05** | Unified Worker Daemon | ⏳ Pending |
| **MTSP-06** | Persistent Python Worker Pool | ✅ Done |
| **MTSP-07** | In-Process Tool Execution | ✅ Done |
| **MTSP-08** | Rust Governance Scanner | ✅ Done |
| **MTSP-09** | Multi-Tenant Git Accelerator | ✅ Done |
| **MTSP-11** | Edit Leasing Manager | ✅ Done |
| **MTSP-12** | Shadow Clone Planning | ✅ Done |
| **MTSP-13** | Atomic Transactional Apply | ✅ Done |
| **MTSP-14** | Centralized Lock Orchestrator | ✅ Done |
| **MTSP-15** | Package Manager Mutexing | ✅ Done |
| **MTSP-16** | Test Runner Port Leasing | ⏳ Pending |
| **MTSP-17** | Dual Memory Audit System | ✅ Done |
| **MTSP-18** | Session History Scraper | ✅ Done |
| Current Tool | Optimized Alternative | Benefit | Status |
|--------------|-----------------------|---------|--------|
| `grep` | `rg` (Ripgrep) | 10x faster, better regex | ✅ Done |
| `find` | `fd` | Native speed, cleaner syntax | ✅ Done |
| `jq` | `jaq` | Rust-based, no process overhead | ✅ Done |
| `cat` / `tr` | Python `read()` / `replace()` | Zero process spawn overhead | ⏳ Partial |
| `sleep` | `asyncio.sleep()` | Non-blocking, single-thread | ✅ Done |
| `bash` (N) | `hook-dispatcher` (Rust) | Consolidates N bash scripts | ✅ Done |
| `date` | `datetime.now()` | Eliminated 100% of date subprocesses | ✅ Done |
- [ ] LSP Multiplexing
- [ ] State-SHM
- [ ] Global Watcher
- [ ] Full ACE-style dual-loop integration
- [ ] Native Rust rewrite of critical path shell hooks
- [ ] Kernel-Level Persistence
| Task ID | Description | Phase | Status |
|---------|-------------|-------|--------|
| BKM-01 | `thegent-resources` Rust: FD/memory/load sampling | 1 | ✅ Done |
| BKM-02 | `thegent-parser` PyO3: XML tag extraction | 1 | ✅ Done |
| BKM-03 | `thegent-crypto` PyO3: sign/verify/hash artifacts | 1 | ✅ Done |
| BKM-04 | Port load_based_limits to Rust resource sampling | 1 | ✅ Done |
| BKM-05 | State-SHM: CircuitBreaker + XP in memory-mapped Rust | 2 | ⏳ Pending |
| BKM-06 | `thegent-git` Rust: HEAD, status, diff stats | 2 | ⏳ Pending |
| BKM-07 | Extend hook-dispatcher: native secret scan | 2 | ⏳ Pending |
| BKM-08 | `thegent-discovery` binary: consolidate discovery subprocesses | 2 | ⏳ Pending |
| Metric | Target | Current |
|--------|--------|---------|
| **Process Count** | `&lt; 10` persistent processes per session | ~20-30 |
| **Hook Latency** | Reduce by > 50% | Partial |
| **Stability** | Eliminate "tab termination" side effects | Partial |
| Task ID | Description | Target |
|---------|-------------|--------|
| MTSP-01 | **Unified MCP Host** | Merge `octocode`, `next-devtools`, and `sequential-thinking` into a single `thegent serve` process. |
| MTSP-02 | **In-Process Agent Runner** | Use ACE-style `cwd` isolation within a single Python process instead of shell-out calls. |
| MTSP-03 | **Shared Task Worker** | Consolidate `task` calls into a single persistent daemon using `process-compose`. |
| MTSP-04 | **LSP Multiplexing** | Use a single persistent `serena` daemon for all code intelligence instead of per-call `uvx` spawns. |
| MTSP-05 | **Unified Worker Daemon** | Persistent background process to manage `task`, `perl`, and `env` calls, reducing shell-out overhead. |
| MTSP-09 | **Multi-Tenant Git Accelerator** | Automated `index.lock` wait/retry and stale lock cleanup to enable concurrent agent git usage. |
| MTSP-11 | **Edit Leasing Manager** | Centralized lease management (file/range level) to prevent agent-on-agent edit collisions. |
| MTSP-12 | **Shadow Clone Planning** | Use symlink-based shadow workspaces or `git worktree` for isolated planning and testing. |
| MTSP-13 | **Atomic Transactional Apply** | ✓ apply_multi_file_transaction + thegent_apply_transaction MCP tool |
| MTSP-14 | **Centralized Lock Orchestrator** | ✓ get_lease_manager() singleton; in-memory lease coordination |
| MTSP-15 | **Package Manager Mutexing** | Multi-tenant coordination for `uv` and `npm` to prevent concurrent install corruption. |
| MTSP-16 | **Test Runner Port Leasing** | Dynamic port allocation and leasing for `pytest`/`vitest` to enable parallel E2E runs. |
| Current Tool | Optimized Alternative | Benefit |
|--------------|-----------------------|---------|
| `grep`       | `rg` (Ripgrep)        | 10x faster, better regex. |
| `find`       | `fd`                  | Native speed, cleaner syntax. |
| `jq`         | `jaq`                 | Rust-based, no process overhead if linked. |
| `cat` / `tr` | Python `read()` / `replace()` | Zero process spawn overhead. |
| `sleep`      | `asyncio.sleep()`     | Non-blocking, single-thread. |
| `bash` (N)   | `hook-dispatcher` (Rust) | Consolidates N bash scripts into 1 process. |
| `date`       | `datetime.now()`      | Eliminated 100% of date-related subprocesses. |
- [ ] Implement persistent LSP Multiplexing for Serena (MTSP-04).
- [ ] Migrate remaining `cat/tr/cp` usage in `hooks/` to internal logic.
- [ ] **MTSP-11: Edit Leasing Manager**: Integrated into `thegent serve`.
- [ ] **MTSP-12: Shadow Clone Logic**: Implementation in `src/thegent/orchestration/shadow.py`.
- [ ] **State-SHM**: Move XP and CircuitBreaker state to memory-mapped files.
- [ ] **Global Watcher**: Single Rust-based watcher for multi-tenant project roots.
- [ ] Full ACE-style dual-loop integration (In-process agents).
- [ ] Native Rust rewrite of critical path shell hooks (Quality Gates).
- [ ] **Kernel-Level Persistence**: Use macOS/Linux native APIs for agent throttling protection.
| Task ID | Description | Phase | Status |
|---------|-------------|-------|--------|
| BKM-01 | `thegent-resources` Rust: FD/memory/load sampling (replace lsof/vm_stat) | 1 | ✓ Done |
| BKM-02 | `thegent-parser` PyO3: XML tag extraction + noise stripping | 1 | ✓ Done |
| BKM-03 | `thegent-crypto` PyO3: sign/verify/hash artifacts | 1 | ✓ Done |
| BKM-04 | Port load_based_limits to Rust resource sampling | 1 | ✓ Done |
| BKM-05 | State-SHM: CircuitBreaker + XP in memory-mapped Rust | 2 | — |
| BKM-06 | `thegent-git` Rust: HEAD, status, diff stats (libgit2) | 2 | — |
| BKM-07 | Extend hook-dispatcher: native secret scan | 2 | — |
| BKM-08 | `thegent-discovery` binary: consolidate discovery subprocesses | 2 | — |
| § | Section | Content |
|---|---------|---------|
| 1 | Executive Summary | Overview, goals, architecture |
| 2 | Current State Analysis | Existing tools, data locations, gaps |
| 3 | Data Source Locations | Cursor/Codex/Claude storage paths |
| 4 | Standardized Collection System | MCP/CLI commands, data format |
| 5 | Git-Backed Audit Logs | Audit trail, versioning, integrity |
| 6 | Integration Architecture | thegent integration, aggregation |
| 7 | Todo & Artifact Collection | Plan extraction, artifact tracking |
| 8 | Implementation Roadmap | Phased implementation plan |
| 9 | API & CLI Reference | Command reference, examples |
| Tool | Purpose | Status |
|------|---------|--------|
| **recall** | Full-text search Claude sessions | External tool, can integrate |
| **claude-code-tools** | Session continuity, Rust/Tantivy search | External tool, can integrate |
| **thegent run_registry.jsonl** | Session tracking | Existing, can extend |
| ID | Task | Est. | Depends |
|----|------|------|---------|
| P4.2.1a | Create `RemoteHost` dataclass and `load_remote_hosts()` | 30 min | None |
| P4.2.1b | Implement `run_remote(host, cwd, prompt, agent)` via paramiko or subprocess+ssh | 1.5 hr | P4.1.7 |
| P4.2.1c | Implement `ps_remote(host)`, `logs_remote(host, session_id)`, `stop_remote`, `wait_remote` | 1 hr | P4.2.1b |
| P4.2.2 | Add `~/.thegent/remote_hosts.yaml` schema and validation | 30 min | P4.2.1a |
| P4.2.3 | Path mapping in `run_remote`: resolve Mac path to remote path | 30 min | P4.2.1b |
| P4.2.4 | Add `--remote` to `run`, `bg`, `ps`, `logs`, `stop`, `wait` in CLI | 1 hr | P4.2.1c |
| P4.2.5 | Document in `docs/guides/HYBRID_ENV_QUICK_START.md` and CLI help | 30 min | P4.2.4 |
| Layer | Source | Description |
|-------|--------|-------------|
| **Registry** | [registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io/) | Official MCP server registry |
| **Reference Servers** | [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | Everything, Fetch, Filesystem, Git, Memory, Sequential Thinking, Time |
| **Awesome List** | [wong2/awesome-mcp-servers](https://github.com/wong2/awesome-mcp-servers) | 100+ community servers; submit at [mcpservers.org/submit](https://mcpservers.org/submit) |
| **Python SDK** | [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) | `pip install mcp` |
| **FastMCP** | [jlowin/fastmcp](https://github.com/jlowin/fastmcp) | `pip install fastmcp` — thegent uses this |
| Repo | Stars | Purpose |
|------|-------|---------|
| [everything-claude-code](https://github.com/affaan-m/everything-claude-code) | 46k+ | Production agents, skills, hooks, commands, rules, MCP configs |
| [awesome-claude-code](https://github.com/awesome-claude-code/awesome-claude-code) | 23k+ | Curated list of Claude Code resources |
| [claude-code-infrastructure-showcase](https://github.com/affaan-m/claude-code-infrastructure-showcase) | — | Infrastructure patterns |
| [buildwithclaude](https://github.com/buildwithclaude) | — | Build patterns |
| [claude-mem](https://github.com/claude-mem) | — | Memory/context |
| [oh-my-opencode](https://github.com/oh-my-opencode) | — | OpenCode configs |
| Path | Purpose |
|------|---------|
| `.cursor/rules/` | Project rules (BMAD, custom) |
| `.cursor/agents/` | Agent definitions |
| `.cursor/commands/` | Slash commands |
| `.cursor/skills/` | Skill definitions |
| MCP config | Cursor settings → MCP servers |
| Component | Purpose |
|-----------|---------|
| Responses API | `/v1/responses` (HTTP + WebSocket) for Codex |
| Cliproxy adapter | Translates Responses ↔ Chat Completions |
| Backend | Port 8318; adapter 8317 |
| Tool | URL | Purpose |
|------|-----|---------|
| pre-commit | [pre-commit.com](https://pre-commit.com/) | Git hooks framework (Python) |
| husky | [typicode.github.io/husky](https://typicode.github.io/husky) | Node git hooks |
| lefthook | [evilmartians/lefthook](https://github.com/evilmartians/lefthook) | Fast git hooks (Rust) |
| Doc | URL |
|-----|-----|
| FastMCP Providers | [gofastmcp.com/servers/providers/overview](https://gofastmcp.com/servers/providers/overview) |
| FastMCP Mounting | [gofastmcp.com/servers/providers/mounting](https://gofastmcp.com/servers/providers/mounting) |
| Serena clients | [oraios.github.io/serena/02-usage/030_clients](https://oraios.github.io/serena/02-usage/030_clients.html) |
| ECC Shortform Guide | [the-shortform-guide.md](https://github.com/affaan-m/everything-claude-code/blob/main/the-shortform-guide.md) |
| ECC Longform Guide | [the-longform-guide.md](https://github.com/affaan-m/everything-claude-code/blob/main/the-longform-guide.md) |
| MCP | Stars | URL | Purpose |
|-----|-------|-----|---------|
| **Figma-Context-MCP** | 13k | [GLips/Figma-Context-MCP](https://github.com/GLips/Figma-Context-MCP) | Figma layout info for Cursor |
| **cursor-talk-to-figma-mcp** | 6.3k | [grab/cursor-talk-to-figma-mcp](https://github.com/grab/cursor-talk-to-figma-mcp) | Cursor ↔ Figma read/modify |
| **fastapi_mcp** | 11.5k | [tadata-org/fastapi_mcp](https://github.com/tadata-org/fastapi_mcp) | Expose FastAPI as MCP tools |
| **git-mcp** | 7.6k | [idosal/git-mcp](https://github.com/idosal/git-mcp) | Remote MCP for any GitHub project |
| **browser-tools-mcp** | 7k | [AgentDeskAI/browser-tools-mcp](https://github.com/AgentDeskAI/browser-tools-mcp) | Browser logs in Cursor |
| **Browser MCP** | 5.8k | [BrowserMCP/mcp](https://github.com/BrowserMCP/mcp) | Control browser via MCP |
| **unity-mcp** | 6k | [CoplayDev/unity-mcp](https://github.com/CoplayDev/unity-mcp) | Unity Editor bridge |
| **dbhub** | 2.1k | [bytebase/dbhub](https://github.com/bytebase/dbhub) | Zero-dep DB MCP (Postgres, MySQL, SQLite) |
| **claude-context** | 5.3k | [zilliztech/claude-context](https://github.com/zilliztech/claude-context) | Code search, full codebase context |
| **grepai** | 1.2k | [yoanbernabeu/grepai](https://github.com/yoanbernabeu/grepai) | Semantic search & call graphs (local) |
| Tool | URL | Purpose |
|------|-----|---------|
| **Rulesync** | [dyoshikawa/rulesync](https://github.com/dyoshikawa/rulesync) | Generate rules, MCP, commands for AI agents; convert Claude↔others |
| **claude-rules-doctor** | [nulone/claude-rules-doctor](https://github.com/nulone/claude-rules-doctor) | Detect dead .claude/rules/ (paths: globs) |
| **ClaudeCTX** | [foxj77/claudectx](https://github.com/foxj77/claudectx) | Switch entire Claude Code config with one command |
| **recall** | [zippoxer/recall](https://github.com/zippoxer/recall) | Full-text search Claude sessions; Enter to resume |
| **claude-code-tools** | [pchalasani/claude-code-tools](https://github.com/pchalasani/claude-code-tools) | Session continuity, Rust/Tantivy session search, tmux-cli, safety hooks |
| **cc-tools** | [Veraticus/cc-tools](https://github.com/Veraticus/cc-tools) | Go hooks: linting, testing, statusline |
| **claude-starter-kit** | [serpro69/claude-starter-kit](https://github.com/serpro69/claude-starter-kit) | Claude Code + Serena + Task Master config templates |
| Repo | Stars | Purpose |
|------|-------|---------|
| **CLIProxyAPI** | 10.7k | [router-for-me/CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI) | Wrap Codex (proxy API), Claude Code as OpenAI-compatible API |
| **proxypal** | 905 | [heyhuynhgiabuu/proxypal](https://github.com/heyhuynhgiabuu/proxypal) | Desktop app for AI subscriptions + any coding tool |
| **awesome-agent-skills** | 2.2k | [heilcheng/awesome-agent-skills](https://github.com/heilcheng/awesome-agent-skills) | Skills for Claude, Codex (proxy API), VS Code |
| Repo | Stars | Purpose |
|------|-------|---------|
| **opencode-antigravity-auth** | 8.4k | [NoeFabris/opencode-antigravity-auth](https://github.com/NoeFabris/opencode-antigravity-auth) | OAuth: OpenCode → Antigravity; use Codex (proxy API) instead of native Gemini |
| **peon-ping** | 2.2k | [PeonPing/peon-ping](https://github.com/PeonPing/peon-ping) | Warcraft III Peon voice notifications for Claude Code, Codex, Cursor, OpenCode |
| **skillshare** | 480 | [runkids/skillshare](https://github.com/runkids/skillshare) | Sync skills across Claude Code, OpenClaw, OpenCode, Codex, Cursor |
| **antigravity-skills** | 247 | [guanyang/antigravity-skills](https://github.com/guanyang/antigravity-skills) | Full-stack, planning, multimedia skills for Antigravity, OpenCode, Codex |
| **oh-my-opencode-slim** | 1.5k | [alvinunreal/oh-my-opencode-slim](https://github.com/alvinunreal/oh-my-opencode-slim) | Slimmed oh-my-opencode, lower token usage |
| **opencode-bar** | 157 | [opgginc/opencode-bar](https://github.com/opgginc/opencode-bar) | Token usage tracker for OpenCode |
| **opencode-mystatus** | 193 | [vbgate/opencode-mystatus](https://github.com/vbgate/opencode-mystatus) | Check AI subscription quotas (OpenAI, Zhipu, Antigravity) |
| **agentrules-architect** | 105 | [trevor-nichols/agentrules-architect](https://github.com/trevor-nichols/agentrules-architect) | AGENTS.md/CLAUDE.md generator for Codex, Claude Code, Cursor, Windsurf, OpenCode |
| Repo | Stars | Purpose |
|------|-------|---------|
| **mcpm.sh** | 889 | [pathintegral-institute/mcpm.sh](https://github.com/pathintegral-institute/mcpm.sh) | CLI MCP package manager & registry; search, configure, router, profiles |
| **magic-mcp** | 4.3k | [21st-dev/magic-mcp](https://github.com/21st-dev/magic-mcp) | v0-like UI components in Cursor/Windsurf/Cline |
| **cipher** | 3.5k | [campfirein/cipher](https://github.com/campfirein/cipher) | Memory layer for Cursor, Codex, Claude Code, Windsurf, Cline |
| **DevDocs** | 2k | [cyberagiinc/DevDocs](https://github.com/cyberagiinc/DevDocs) | Free, private tech docs MCP for Cursor, Windsurf, Cline |
| **memory-bank-mcp** | 861 | [alioshr/memory-bank-mcp](https://github.com/alioshr/memory-bank-mcp) | Remote memory (Cline Memory Bank–inspired) for Cursor, Windsurf |
| **rulebook-ai** | 572 | [botingw/rulebook-ai](https://github.com/botingw/rulebook-ai) | Consistent rules for Codex (proxy API), Cursor, Roo Code, Cline, Windsurf, Claude Code |
| **context-engineering-kit** | 470 | [NeoLabHQ/context-engineering-kit](https://github.com/NeoLabHQ/context-engineering-kit) | Plugin marketplace for Claude Code, OpenCode, Cursor, Windsurf, Cline |
| **Feishu-MCP** | 438 | [cso1z/Feishu-MCP](https://github.com/cso1z/Feishu-MCP) | Feishu/Lark docs for Cursor, Windsurf, Cline |
| **ai-prompts** | 1k | [instructa/ai-prompts](https://github.com/instructa/ai-prompts) | Curated prompts for Cursor Rules, Cline, Windsurf, Codex (proxy API) |
| **BifrostMCP** | 201 | [biegehydra/BifrostMCP](https://github.com/biegehydra/BifrostMCP) | VSCode extension: Find Usages, Rename for Cursor, Windsurf, Cline |
| Concept | Purpose |
|--------|---------|
| **skill-creator** | Built-in: bootstrap new skills from scratch; `$skill-creator` in Codex |
| **skill-installer** | Built-in: install curated skills from GitHub; `$skill-installer create-plan` |
| **Locations** | REPO: `$CWD/.codex/skills`, USER: `~/.codex/skills`, ADMIN: `/etc/codex/skills` |
| **Docs** | [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills), [support.claude.com creating-custom-skills](https://support.claude.com/en/articles/12512198-creating-custom-skills) |
| Resource | URL | Purpose |
|----------|-----|---------|
| **cursor.directory** | [cursor.directory](https://cursor.directory/) | 72k+ members; rules, MCPs, generate, jobs, board |
| **directories** | [leerob/directories](https://github.com/leerob/directories) (3.9k★) | Cursor Directory source; rules index at `packages/data/src/rules/` |
| **awesome-cursorrules** | [PatrickJS/awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) | Curated Cursor rules |
| **Agnxi.com** | — | Directory of 10k+ Agent Skills for Cursor, Claude Code, Windsurf |
| Tool | Rules File | Commands/Workflows | Skills |
|------|------------|--------------------|--------|
| Claude Code | CLAUDE.md | .claude/commands/ | .claude/skills/ |
| Codex (proxy API) | — | (replaces native Antigravity/Gemini) | — |
| Cursor | .cursorrules | .cursor/rules/ | .cursor/skills/ |
| Windsurf | .windsurfrules | .windsurf/workflows/ | .windsurf/skills/ |
| Kilo Code | AGENTS.md | .kilocode/workflows/ | .kilocode/skills/ |
| OpenCode | AGENTS.md | .opencode/commands/ | .opencode/skills/ |
| Repo | Stars | Purpose |
|------|-------|---------|
| **agents** | 28.7k | [wshobson/agents](https://github.com/wshobson/agents) | Multi-agent orchestration for Claude Code |
| **swarm** | 21k | [openai/swarm](https://github.com/openai/swarm) | OpenAI multi-agent framework |
| **deer-flow** | 20k | [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | SuperAgent harness: research, code, create |
| **adk-python** | 17.7k | [google/adk-python](https://github.com/google/adk-python) | Agent Development Kit (Python) |
| **agent-framework** | 7.2k | [microsoft/agent-framework](https://github.com/microsoft/agent-framework) | Build, orchestrate AI agents (Python, .NET) |
| **oh-my-claudecode** | 6.4k | [Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) | Teams-first multi-agent for Claude Code |
| **cursor-talk-to-figma-mcp** | 6.3k | [grab/cursor-talk-to-figma-mcp](https://github.com/grab/cursor-talk-to-figma-mcp) | Cursor ↔ Figma read/modify |
| **myclaude** | 2.3k | [cexll/myclaude](https://github.com/cexll/myclaude) | Multi-agent (Claude Code, Codex (proxy API), OpenCode) |
| **multi-agent-shogun** | 881 | [yohey-w/multi-agent-shogun](https://github.com/yohey-w/multi-agent-shogun) | Samurai hierarchy (shogun→karo→ashigaru) for Claude Code |
| **Mysti** | 886 | [DeepMyst/Mysti](https://github.com/DeepMyst/Mysti) | Claude Code + Codex brainstorm in VS Code |
| MCP | Purpose |
|-----|---------|
| **1mcpserver** | MCP of MCPs; remote discovery at mcp.1mcpserver.com |
| **Cua** | Computer-Use Agent (CUA) MCP server |
| **Currents** | Playwright test failures from Currents.dev |
| **Context 7** | Up-to-date docs for Cursor prompts |
| **mcpservers.org** | Submit new MCPs (awesome-mcp-servers uses this) |
| Repo | Stars | Purpose |
|------|-------|---------|
| **ECC examples** | — | [examples](https://github.com/affaan-m/everything-claude-code/tree/main/examples): CLAUDE.md for SaaS Next.js, Django API, Go, Rust |
| **cherry-studio** | 39.9k | [CherryHQ/cherry-studio](https://github.com/CherryHQ/cherry-studio) | AI productivity studio; 300+ assistants; Claude Code, Codex, OpenCode |
| **meridian** | 134 | [markmdev/meridian](https://github.com/markmdev/meridian) | Zero-config Claude Code setup; task scaffolding, structured memory, TDD |
| **fulling** | 2.4k | [FullAgent/fulling](https://github.com/FullAgent/fulling) | Full-stack AI agent (Next.js, Claude, shadcn, PostgreSQL, Kubernetes) |
| **crystal** | 2.9k | [stravu/crystal](https://github.com/stravu/crystal) | Parallel Codex/Claude Code sessions in git worktrees |
| **project-guidelines-example** | — | ECC skills/ | Template for project-specific skills |
| Tool | Stars | Purpose |
|------|-------|---------|
| **tokscale** | 696 | [junhoyeo/tokscale](https://github.com/junhoyeo/tokscale) | Token usage tracking: OpenCode, Claude Code, Codex (proxy API), Cursor, AmpCode, Factory |
| **OpenContext** | 383 | [0xranx/OpenContext](https://github.com/0xranx/OpenContext) | Personal context store; Codex/Claude/OpenCode with Skills; Tauri desktop app |
| **c0ntextKeeper** | 53 | [Capnjbrown/c0ntextKeeper](https://github.com/Capnjbrown/c0ntextKeeper) | Context preservation; 7 hooks, 187 semantic patterns, 3 MCP tools |
| **mcp-memory-service** | 1.3k | [doobidoo/mcp-memory-service](https://github.com/doobidoo/mcp-memory-service) | Automatic context memory for Claude, Cursor, 13+ AI tools |
| **claude-cognitive** | 438 | [GMaN1911/claude-cognitive](https://github.com/GMaN1911/claude-cognitive) | Working memory for Claude Code; persistent context, multi-instance coordination |
| **task-orchestrator** | 155 | [jpicklyk/task-orchestrator](https://github.com/jpicklyk/task-orchestrator) | MCP task orchestration; persistent project tracking; Cursor, Windsurf |
| **claude-squad** | 6k | [smtg-ai/claude-squad](https://github.com/smtg-ai/claude-squad) | Manage Claude Code, Aider, Codex, OpenCode, Amp in one place |
| **ccpm** | 7.3k | [automazeio/ccpm](https://github.com/automazeio/ccpm) | Project management for Claude Code; GitHub Issues + git worktrees |
| **ruler** | 2.5k | [intellectronica/ruler](https://github.com/intellectronica/ruler) | Apply same rules to Claude Code, Codex, Cursor, Aider, Windsurf |
| Tool | Stars | Purpose |
|------|-------|---------|
| **cognee** | 12.3k | [topoteretes/cognee](https://github.com/topoteretes/cognee) | Knowledge engine for AI agent memory |
| **honcho** | 356 | [plastic-labs/honcho](https://github.com/plastic-labs/honcho) | Memory library for stateful agents |
| **nexus** | 300 | [nexi-lab/nexus](https://github.com/nexi-lab/nexus) | Shared heartbeat for agents and humans |
| MCP | Stars | Purpose |
|-----|-------|---------|
| **notebooklm-mcp** | 912 | [PleasePrompto/notebooklm-mcp](https://github.com/PleasePrompto/notebooklm-mcp) | NotebookLM MCP; Claude Code, Codex research with grounded, citation-backed answers |
| **apple-docs-mcp** | 893 | [kimsungwhee/apple-docs-mcp](https://github.com/kimsungwhee/apple-docs-mcp) | Apple Developer docs; iOS/macOS/SwiftUI/UIKit, WWDC, Swift/ObjC APIs for Cursor, Claude |
| **Microsoft Learn MCP** | 1.4k | [MicrosoftDocs/mcp](https://github.com/MicrosoftDocs/mcp) | Official Microsoft Learn MCP; real-time docs & code samples for LLMs, Codex (proxy API) |
| **home-assistant-vibecode-agent** | 440 | [Coolver/home-assistant-vibecode-agent](https://github.com/Coolver/home-assistant-vibecode-agent) | Home Assistant MCP; vibe-code and manage HA from Cursor, Claude Code, VS Code |
| **mcp-gateway-registry** | 448 | [agentic-community/mcp-gateway-registry](https://github.com/agentic-community/mcp-gateway-registry) | Enterprise MCP Gateway & Registry; OAuth, dynamic tool discovery, unified access |
| **context7** | 45.8k | [upstash/context7](https://github.com/upstash/context7) | Up-to-date code docs for LLMs, Cursor |
| **github-mcp-server** | 27k | [github/github-mcp-server](https://github.com/github/github-mcp-server) | Official GitHub MCP |
| **chrome-devtools-mcp** | 25.6k | [ChromeDevTools/chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) | Chrome DevTools for coding agents |
| **n8n-mcp** | 13.5k | [czlonkowski/n8n-mcp](https://github.com/czlonkowski/n8n-mcp) | Build n8n workflows from Claude Code, Cursor, Windsurf |
| **Skill_Seekers** | 9.6k | [yusufkaraaslan/Skill_Seekers](https://github.com/yusufkaraaslan/Skill_Seekers) | Convert docs, GitHub, PDFs → Claude skills; MCP server |
| **mcp-use** | 9.2k | [mcp-use/mcp-use](https://github.com/mcp-use/mcp-use) | Easiest way to interact with MCP servers; custom agents |
| **IBM mcp-context-forge** | 3.3k | [IBM/mcp-context-forge](https://github.com/IBM/mcp-context-forge) | MCP Gateway & Registry; central tools/resources/prompts |
| **excel-mcp-server** | 3.3k | [haris-musa/excel-mcp-server](https://github.com/haris-musa/excel-mcp-server) | Excel file manipulation |
| **markdownify-mcp** | 2.4k | [zcaceres/markdownify-mcp](https://github.com/zcaceres/markdownify-mcp) | Convert almost anything to Markdown |
| **arxiv-mcp-server** | 2.2k | [blazickjp/arxiv-mcp-server](https://github.com/blazickjp/arxiv-mcp-server) | Search and analyze arXiv papers |
| **kubernetes-mcp-server** | 1.2k | [containers/kubernetes-mcp-server](https://github.com/containers/kubernetes-mcp-server) | Kubernetes and OpenShift |
| **mysql_mcp_server** | 1.1k | [designcomputer/mysql_mcp_server](https://github.com/designcomputer/mysql_mcp_server) | Secure MySQL interaction |
| **mcp-server-qdrant** | 1.2k | [qdrant/mcp-server-qdrant](https://github.com/qdrant/mcp-server-qdrant) | Qdrant vector DB |
| **mcp-neo4j** | 899 | [neo4j-contrib/mcp-neo4j](https://github.com/neo4j-contrib/mcp-neo4j) | Neo4j graph DB |
| **jupyter-mcp-server** | 896 | [datalayer/jupyter-mcp-server](https://github.com/datalayer/jupyter-mcp-server) | Jupyter MCP |
| Source | Hooks / Features |
|--------|------------------|
| **c0ntextKeeper** | 7 hooks, 187 semantic patterns, 3 MCP tools; never lose work to compaction |
| **ECC memory-persistence** | session-start, session-end, pre-compact, suggest-compact, evaluate-session |
| **ECC strategic-compact** | Manual compaction suggestions |
| **ECC check-console-log** | Block on console.log in TS/JS |
| **ECC post-edit-format** | Prettier on Edit |
| **ECC post-edit-typecheck** | tsc --noEmit on .ts/.tsx |
| Source | Purpose |
|--------|---------|
| **Skill_Seekers** | Docs, GitHub repos, PDFs → Claude skills; conflict detection |
| **ECC /skill-create** | Local git history → SKILL.md |
| **ECC Skill Creator GitHub App** | 10k+ commits, auto-PRs, team sharing |
| **ECC instinct-import/export** | Share learned patterns |
| **ECC evolve** | Cluster instincts into skills |
| Category | Item | Purpose |
|----------|------|---------|
| **IDE** | codecompanion.nvim (6.1k★) | AI coding in Neovim; Claude Code, Codex (proxy API) |
| **MCP curriculum** | mcp-for-beginners (14.4k★) | Microsoft MCP fundamentals; .NET, Java, TS, Python, Rust |
| **MCP registry** | modelcontextprotocol/registry (6.4k★) | Community MCP server registry |
| **Activepieces** | 20.8k★ | ~400 MCP servers; AI workflow automation |
| **n8n** | 174k★ | Workflow automation; MCP client/server |
| Collection | Stars | URL | Scope |
|------------|-------|-----|-------|
| **awesome-claude-code** | 23.9k | [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | Skills, hooks, slash-commands, agents, CLAUDE.md, tooling |
| **awesome-claude-skills** | 7.2k | [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) | Claude Skills, resources, workflows |
| **VoltAgent awesome-agent-skills** | 7.2k | [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 300+ skills; Codex (proxy API), Antigravity, Cursor, OpenCode |
| **awesome-claude** | 996 | [tonysurfly/awesome-claude](https://github.com/tonysurfly/awesome-claude) | All things Anthropic Claude |
| **awesome-claude-plugins** | 1.3k | [ComposioHQ/awesome-claude-plugins](https://github.com/ComposioHQ/awesome-claude-plugins) | Plugins: commands, agents, hooks, MCP |
| **awesome-claude-code-plugins** | 478 | [ccplugins/awesome-claude-code-plugins](https://github.com/ccplugins/awesome-claude-code-plugins) | Slash commands, subagents, MCP, hooks |
| **awesome-claude-code-toolkit** | 477 | [rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit) | 135 agents, 35 skills, 42 commands, 120 plugins, 19 hooks |
| **heilcheng awesome-agent-skills** | 2.2k | [heilcheng/awesome-agent-skills](https://github.com/heilcheng/awesome-agent-skills) | Claude, Codex (proxy API), VS Code |
| **skillmatic awesome-agent-skills** | 151 | [skillmatic-ai/awesome-agent-skills](https://github.com/skillmatic-ai/awesome-agent-skills) | Agent Skills architecture |
| **awesome-claude-code-sub-agents** | 130 | [supatest-ai/awesome-claude-code-sub-agents](https://github.com/supatest-ai/awesome-claude-code-sub-agents) | Specialised Claude Code sub-agents |
| Guide | Stars | URL | Scope |
|-------|-------|-----|-------|
| **ai-guide** | 6.9k | [liyupi/ai-guide](https://github.com/liyupi/ai-guide) | AI resource大全; Vibe Coding; Cursor, MCP, RAG |
| **aicodeguide** | 2.1k | [automata/aicodeguide](https://github.com/automata/aicodeguide) | Roadmap to start coding with AI |
| **awesome-ai-coding-tools** | 1.5k | [ai-for-developers/awesome-ai-coding-tools](https://github.com/ai-for-developers/awesome-ai-coding-tools) | Curated AI-powered coding tools |
| **awesome-vibe-coding-guide** | 299 | [analyticalrohit/awesome-vibe-coding-guide](https://github.com/analyticalrohit/awesome-vibe-coding-guide) | 10x Vibe Coder; Claude Code, Cursor, Codex (proxy API), Windsurf |
| **Awesome-Vibecoding-Guide** | 448 | [ClavixDev/Awesome-Vibecoding-Guide](https://github.com/ClavixDev/Awesome-Vibecoding-Guide) | Commercial projects; AI-assisted code |
| **AI-Coding-Style-Guides** | 471 | [lidangzzz/AI-Coding-Style-Guides](https://github.com/lidangzzz/AI-Coding-Style-Guides) | Coding style for Vibe Coding, SWE-Agents |
| **awesome-ai-coding-techniques** | 317 | [inmve/awesome-ai-coding-techniques](https://github.com/inmve/awesome-ai-coding-techniques) | Claude Code, Codex (proxy API), Cursor; EN/ES/DE |
| **vibe-coding-for-dummies** | 347 | [cporter202/vibe-coding-for-dummies](https://github.com/cporter202/vibe-coding-for-dummies) | Beginner guide; Firebase Studio, Cursor |
| Collection | Stars | URL |
|------------|-------|-----|
| **awesome-ralph** | 723 | [snwfdhmp/awesome-ralph](https://github.com/snwfdhmp/awesome-ralph) |
| **ralph-playbook** | — | [ClaytonFarr/how-to-ralph-wiggum](https://github.com/ClaytonFarr/how-to-ralph-wiggum) |
| Resource | Stars | URL | Scope |
|----------|-------|-----|-------|
| **Claude Code Ultimate Guide** | — | [FlorianBruniaux/claude-code-ultimate-guide](https://github.com/FlorianBruniaux/claude-code-ultimate-guide) | Beginner→power user; templates; quizzes |
| **Claude Code Handbook** | — | [nikiforovall.blog/claude-code-rules](https://nikiforovall.blog/claude-code-rules/) | Best practices, tips, plugins |
| **Claude Code Tips** | — | [ykdojo/claude-code-tips](https://github.com/ykdojo/claude-code-tips) | 35+ tips; voice, system prompt, containers |
| **Claude Code System Prompts** | — | [Piebald-AI/claude-code-system-prompts](https://github.com/Piebald-AI/claude-code-system-prompts) | All Claude Code system prompt parts |
| **Claude Code Repos Index** | — | [danielrosehill/Claude-Code-Repos-Index](https://github.com/danielrosehill/Claude-Code-Repos-Index) | 75+ Claude Code repos |
| **Claude Code Documentation Mirror** | — | [ericbuess/claude-code-docs](https://github.com/ericbuess/claude-code-docs) | Anthropic docs mirror |
| **claude-code-docs** | — | [costiash/claude-code-docs](https://github.com/costiash/claude-code-docs) | Docs with full-text search |
| Resource | Stars | URL | Scope |
|----------|-------|-----|-------|
| **prompts.chat** | 145k | [f/prompts.chat](https://github.com/f/prompts.chat) | Awesome ChatGPT Prompts; share, discover, collect prompts; self-host; Claude, Codex (proxy API) |
| **ai-prompts** | 1k | [instructa/ai-prompts](https://github.com/instructa/ai-prompts) | Cursor Rules, Cline, Windsurf, Codex (proxy API) |
| **cursor.directory** | — | [cursor.directory](https://cursor.directory/) | Rules, MCPs, generate, jobs |
| **directories** | 3.9k | [leerob/directories](https://github.com/leerob/directories) | Cursor Directory source |
| **awesome-ai-system-prompts** | 5.2k | [dontriskit/awesome-ai-system-prompts](https://github.com/dontriskit/awesome-ai-system-prompts) | System prompts for ChatGPT, Claude, etc. |
| **llms-txt-hub** | 698 | [thedaviddias/llms-txt-hub](https://github.com/thedaviddias/llms-txt-hub) | AI-ready docs; llms.txt standard |
| **awesome-devtools** | 622 | [devtoolsd/awesome-devtools](https://github.com/devtoolsd/awesome-devtools) | Cursor, Antigravity, dev tools |
| Resource | Stars | URL | Scope |
|----------|-------|-----|-------|
| **oh-my-opencode** | 31.7k | [code-yeongyu/oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode) | Best agent harness; Claude Code, Codex, OpenCode |
| **cc-switch** | 18.5k | [farion1231/cc-switch](https://github.com/farion1231/cc-switch) | All-in-one: Claude Code, Codex (proxy API), OpenCode |
| **AionUi** | 16k | [iOfficeAI/AionUi](https://github.com/iOfficeAI/AionUi) | Cowork; Codex (proxy API), Claude Code, OpenCode, Qwen |
| **agent-of-empires** | 653 | [njbrake/agent-of-empires](https://github.com/njbrake/agent-of-empires) | Claude Code, OpenCode, Codex (proxy API); tmux, worktrees |
| **codexia** | 435 | [milisp/codexia](https://github.com/milisp/codexia) | GUI for Codex CLI + Claude Code; FileTree, prompts, worktrees |
| Resource | Stars | URL | Scope |
|----------|-------|-----|-------|
| **dify** | 129k | [langgenius/dify](https://github.com/langgenius/dify) | Production-ready agentic workflow platform; RAG, MCP, low-code orchestration |
| **firecrawl** | 82k | [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | Web Data API for AI; turn websites into LLM-ready markdown or structured data |
| **ragflow** | 73k | [infiniflow/ragflow](https://github.com/infiniflow/ragflow) | Open-source RAG engine; RAG + Agent; MCP; document parsing, deep research |
| **open-webui** | 124k | [open-webui/open-webui](https://github.com/open-webui/open-webui) | User-friendly AI interface; Ollama, OpenAI; MCP, RAG, self-hosted |
| **agentic-workflow-patterns** | — | [ThibautMelen/agentic-workflow-patterns](https://github.com/ThibautMelen/agentic-workflow-patterns) | Subagent, Progressive Skills, Master-Clone, etc. |
| **agentic-ai-systems** | 168 | [ThibautMelen/agentic-ai-systems](https://github.com/ThibautMelen/agentic-ai-systems) | Agentic systems with Mermaid diagrams |
| **quint-code** | 1.2k | [m0n0x41d/quint-code](https://github.com/m0n0x41d/quint-code) | Structured reasoning for Claude Code, Codex, Cursor |
| Resource | Stars | URL |
|----------|-------|-----|
| **vibe-log-cli** | 282 | [vibe-log/vibe-log-cli](https://github.com/vibe-log/vibe-log-cli) |
| Item | Stars | URL | Purpose |
|------|-------|-----|---------|
| **superset** | 1.7k | [superset-sh/superset](https://github.com/superset-sh/superset) | Command center: run Claude Code, OpenCode, Codex in parallel; git worktrees |
| **copilot-mcp** | 465 | [VikashLoomba/copilot-mcp](https://github.com/VikashLoomba/copilot-mcp) | VSCode: find/install Skills & MCP for Codex (proxy API), Claude Code |
| **skillport** | 312 | [gotalab/skillport](https://github.com/gotalab/skillport) | Bring Agent Skills to any AI agent via CLI or MCP |
| **refly** | 6.6k | [refly-ai/refly](https://github.com/refly-ai/refly) | Open-source agent skills builder; Claude Code, Cursor, Codex; vibe workflow |
| **claude-workflow-v2** | 1.2k | [CloudAI-X/claude-workflow-v2](https://github.com/CloudAI-X/claude-workflow-v2) | Universal Claude Code workflow; agents, skills, hooks, commands |
| **skillshare** | 480 | [runkids/skillshare](https://github.com/runkids/skillshare) | Sync skills across AI CLI tools; Claude Code, OpenClaw, OpenCode; team sharing |
| **skillkit** | 329 | [rohitg00/skillkit](https://github.com/rohitg00/skillkit) | Portable skills across Claude Code, Cursor, Codex (proxy API), 40+ more |
| **OpenContext** | 383 | [0xranx/OpenContext](https://github.com/0xranx/OpenContext) | Personal context store; reuse Codex/Claude/OpenCode with Skills/tools |
| **claude-codex-settings** | 419 | [fcakyon/claude-codex-settings](https://github.com/fcakyon/claude-codex-settings) | Battle-tested skills, commands, hooks, agents, MCP for daily use |
| **claude-context-local** | 187 | [FarhanAliRaza/claude-context-local](https://github.com/FarhanAliRaza/claude-context-local) | Code search MCP; local embeddings, no API cost |
| **claude-flow** | 14.1k | [ruvnet/claude-flow](https://github.com/ruvnet/claude-flow) | Agent orchestration for Claude; multi-agent swarms |
| **claude-code-mcp** | 1.1k | [steipete/claude-code-mcp](https://github.com/steipete/claude-code-mcp) | Claude Code as one-shot MCP (agent in agent) |
| **DesktopCommanderMCP** | 5.5k | [wonderwhy-er/DesktopCommanderMCP](https://github.com/wonderwhy-er/DesktopCommanderMCP) | Terminal control, file search, diff editing for Claude |
| **lobehub** | 72.3k | [lobehub/lobehub](https://github.com/lobehub/lobehub) | Agent harness; find, build, collaborate with agents |
| Item | Stars | URL | Purpose |
|------|-------|-----|---------|
| **claude-plugins-official** | 7.5k | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | Official Anthropic directory of Claude Code plugins |
| **antigravity-awesome-skills** | 9.9k | [sickn33/antigravity-awesome-skills](https://github.com/sickn33/antigravity-awesome-skills) | 800+ agentic skills for Claude Code/Antigravity/Cursor |
| **marketingskills** | 7.9k | [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) | Marketing skills for Claude Code; CRO, copywriting, SEO, analytics, growth |
| **AI-Research-SKILLs** | 3.5k | [Orchestra-Research/AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs) | AI research & engineering skills; Claude Code, Codex (proxy API); open-source |
| **claude-code-guide** | 3.4k | [zebbern/claude-code-guide](https://github.com/zebbern/claude-code-guide) | Setup, commands, workflows, agents, skills & tips |
| **claude-code-plugins-plus-skills** | 1.4k | [jeremylongshore/claude-code-plugins-plus-skills](https://github.com/jeremylongshore/claude-code-plugins-plus-skills) | 270+ plugins, 739 skills; Jupyter tutorials, CCPI package manager |
| **claude-pilot** | 1.1k | [maxritter/claude-pilot](https://github.com/maxritter/claude-pilot) | Production-grade code; tests enforced; context preserved |
| **pg-aiguide** | 1.5k | [timescale/pg-aiguide](https://github.com/timescale/pg-aiguide) | Postgres MCP + Claude plugin; better SQL for AI coding |
| **wcgw** | 641 | [rusiaaman/wcgw](https://github.com/rusiaaman/wcgw) | Shell and coding agent on MCP clients |
| Item | Stars | URL | Purpose |
|------|-------|-----|---------|
| **magic-mcp** | 4.3k | [21st-dev/magic-mcp](https://github.com/21st-dev/magic-mcp) | v0-like frontend in Cursor/Windsurf/Cline |
| **cipher** | 3.5k | [campfirein/cipher](https://github.com/campfirein/cipher) | Memory layer for coding agents; Cursor, Codex, Claude Code, Windsurf, Cline |
| **memory-bank-mcp** | 861 | [alioshr/memory-bank-mcp](https://github.com/alioshr/memory-bank-mcp) | Remote memory bank MCP; Cline Memory Bank–inspired |
| **DevDocs** | 2k | [cyberagiinc/DevDocs](https://github.com/cyberagiinc/DevDocs) | Free, private tech docs MCP; Cursor, Windsurf, Cline |
| **context-engineering-kit** | 470 | [NeoLabHQ/context-engineering-kit](https://github.com/NeoLabHQ/context-engineering-kit) | Plugin marketplace; Claude Code, OpenCode, Cursor, Windsurf, Cline |
| **rulebook-ai** | 572 | [botingw/rulebook-ai](https://github.com/botingw/rulebook-ai) | Vibe engineering rules; Codex (proxy API), Cursor, Cline, Windsurf, Claude Code |
| **rules_template** | 1.1k | [Bhartendu-Kumar/rules_template](https://github.com/Bhartendu-Kumar/rules_template) | Memory + reasoning rules for Cline/RooCode/Cursor/Windsurf |
| **Feishu-MCP** | 438 | [cso1z/Feishu-MCP](https://github.com/cso1z/Feishu-MCP) | Feishu/Lark docs for Cursor, Windsurf, Cline |
| Item | Stars | URL | Purpose |
|------|-------|-----|---------|
| **OpenHands** | 67.9k | [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands) | AI-driven development |
| **continue** | 31.4k | [continuedev/continue](https://github.com/continuedev/continue) | Open-source CLI; headless async agents or TUI coding agent |
| **plandex** | 15k | [plandex-ai/plandex](https://github.com/plandex-ai/plandex) | AI coding agent for large projects |
| **how-to-build-a-coding-agent** | 5.1k | [ghuntley/how-to-build-a-coding-agent](https://github.com/ghuntley/how-to-build-a-coding-agent) | Workshop: build coding agent like Roo, Cline, Cursor, Windsurf |
| **golf** | 811 | [golf-mcp/golf](https://github.com/golf-mcp/golf) | Production MCP server framework; auth, observability, telemetry |
| **moltis** | 952 | [moltis-org/moltis](https://github.com/moltis-org/moltis) | Personal AI assistant; Rust, MCP, voice, multi-channel |
| **paperdebugger** | 1.3k | [PaperDebugger/paperdebugger](https://github.com/PaperDebugger/paperdebugger) | Multi-agent for academic writing, LaTeX, Overleaf |
| **raptor** | 1.1k | [gadievron/raptor](https://github.com/gadievron/raptor) | Claude Code as offensive/defensive security agent; rules, sub-agents, skills |
| **claude-code-config** | 936 | [jarrodwatts/claude-code-config](https://github.com/jarrodwatts/claude-code-config) | Personal Claude Code config; rules, hooks, agents, skills, commands |
| **langchain4j-aideepin** | 1.2k | [moyangzhan/langchain4j-aideepin](https://github.com/moyangzhan/langchain4j-aideepin) | AI productivity; RAG, workflow, MCP marketplace, long-term memory |
| Item | Stars | URL | Purpose |
|------|-------|-----|---------|
| **browserwing** | 744 | [browserwing/browserwing](https://github.com/browserwing/browserwing) | Browser actions → MCP commands or Claude Skill; AI agents control browsers |
| **ios-simulator-skill** | 487 | [conorluddy/ios-simulator-skill](https://github.com/conorluddy/ios-simulator-skill) | iOS Simulator Skill for Claude Code; build, run, interact with apps |
| **skillz** | 359 | [intellectronica/skillz](https://github.com/intellectronica/skillz) | MCP server for loading skills; shim for non-Claude clients |
| **claude-skills-mcp** | 315 | [K-Dense-AI/claude-skills-mcp](https://github.com/K-Dense-AI/claude-skills-mcp) | MCP server for searching/retrieving Claude Agent Skills via vector search |
| Collection | Stars | URL | Scope |
|------------|-------|-----|-------|
| **awesome** | 294k | [sindresorhus/awesome](https://github.com/sindresorhus/awesome) | Meta-list: platforms, languages, frameworks, tools; Development Environment, Testing, etc. |
| **awesome-chrome-devtools** | — | [ChromeDevTools/awesome-chrome-devtools](https://github.com/ChromeDevTools/awesome-chrome-devtools) | Chrome DevTools resources; debugging, profiling |
| **awesome-docker** | — | [veggiemonk/awesome-docker](https://github.com/veggiemonk/awesome-docker) | Docker resources; containers, orchestration |
| **awesome-kubernetes** | — | [ramitsurana/awesome-kubernetes](https://github.com/ramitsurana/awesome-kubernetes) | Kubernetes resources; orchestration, tooling |
| **awesome-terraform** | — | [shuaibiyy/awesome-terraform](https://github.com/shuaibiyy/awesome-terraform) | Terraform resources; IaC, providers, modules |
| **awesome-ai-devtools** | 3.6k | [jamesmurdza/awesome-ai-devtools](https://github.com/jamesmurdza/awesome-ai-devtools) | AI-powered developer tools |
| **Awesome-LLMOps** | 5.6k | [tensorchord/Awesome-LLMOps](https://github.com/tensorchord/Awesome-LLMOps) | LLMOps tools for developers |
| **awesome-data-engineering** | 8.3k | [igorbarinov/awesome-data-engineering](https://github.com/igorbarinov/awesome-data-engineering) | Data engineering tools |
| **awesome-ci** | 4k | [ligurio/awesome-ci](https://github.com/ligurio/awesome-ci) | CI services and tools |
| **awesome-developer-first** | 1.5k | [agamm/awesome-developer-first](https://github.com/agamm/awesome-developer-first) | Developer-first products |
| **best-of-python-dev** | 1.2k | [ml-tooling/best-of-python-dev](https://github.com/ml-tooling/best-of-python-dev) | Ranked Python dev tools |
| **go-recipes** | 4.5k | [nikolaydubina/go-recipes](https://github.com/nikolaydubina/go-recipes) | Tools for Go projects |
| **omni-tools** | 8.6k | [iib0011/omni-tools](https://github.com/iib0011/omni-tools) | Self-hosted web tools; converters, image/PDF/video |
| **dev-resources** | 1.2k | [marcelscruz/dev-resources](https://github.com/marcelscruz/dev-resources) | Collaborative dev resources list |
| **Awesome-independent-tools** | 2.3k | [yaolifeng0629/Awesome-independent-tools](https://github.com/yaolifeng0629/Awesome-independent-tools) | Indie dev & AI出海 tools |
| **awesome-awesome-nodejs** | 1.6k | [bnb/awesome-awesome-nodejs](https://github.com/bnb/awesome-awesome-nodejs) | Meta-list of Node.js awesome lists |
| **awesome-gis** | 5.2k | [sshuair/awesome-gis](https://github.com/sshuair/awesome-gis) | Geospatial tools, cartography, geoanalysis |
| **aws-toolbox** | 1.7k | [towardsthecloud/aws-toolbox](https://github.com/towardsthecloud/aws-toolbox) | AWS automation scripts for devs |
| **indie-hacker-tools-plus** | 1.5k | [XiaomingX/indie-hacker-tools-plus](https://github.com/XiaomingX/indie-hacker-tools-plus) | Tech stack for indie hackers |
| **DeFi-Developer-Road-Map** | 10.7k | [OffcierCia/DeFi-Developer-Road-Map](https://github.com/OffcierCia/DeFi-Developer-Road-Map) | DeFi dev handbook; DApps, smart contracts |
| **awesome-cross-platform-nodejs** | 1.2k | [bcoe/awesome-cross-platform-nodejs](https://github.com/bcoe/awesome-cross-platform-nodejs) | Cross-platform Node.js tools |
| Tool | Stars | URL | Purpose |
|------|-------|-----|---------|
| **it-tools** | 37k | [CorentinTh/it-tools](https://github.com/CorentinTh/it-tools) | Handy online tools for developers; converters, encoders, formatters |
| **Files** | 41.9k | [files-community/Files](https://github.com/files-community/Files) | Modern file manager; Windows, Git integration |
| **massCode** | 6.6k | [massCodeIO/massCode](https://github.com/massCodeIO/massCode) | Open-source code snippet manager |
| **wakapi** | 4.1k | [muety/wakapi](https://github.com/muety/wakapi) | Self-hosted WakaTime-compatible coding statistics |
| **kubero** | 4.1k | [kubero-dev/kubero](https://github.com/kubero-dev/kubero) | Self-hosted PaaS; Heroku/Netlify/Vercel alternative on Kubernetes |
| **waveterm** | 17.4k | [wavetermdev/waveterm](https://github.com/wavetermdev/waveterm) | Open-source cross-platform terminal for seamless workflows |
| Tool | Stars | URL | Purpose |
|------|-------|-----|---------|
| **ohmyzsh** | 184.7k | [ohmyzsh/ohmyzsh](https://github.com/ohmyzsh/ohmyzsh) | zsh config framework; 300+ plugins |
| **Bash-it** | 14.9k | [Bash-it/bash-it](https://github.com/Bash-it/bash-it) | Community Bash framework; aliases, completion, plugins |
| **oh-my-bash** | 7.2k | [ohmybash/oh-my-bash](https://github.com/ohmybash/oh-my-bash) | Bash config framework; themes, plugins, auto-update |
| **lazygit** | 72.4k | [jesseduffield/lazygit](https://github.com/jesseduffield/lazygit) | Terminal UI for git |
| **bat** | 57.1k | [sharkdp/bat](https://github.com/sharkdp/bat) | cat clone with syntax highlighting |
| **fd** | 41.6k | [sharkdp/fd](https://github.com/sharkdp/fd) | Fast find alternative |
| **cheat.sh** | 40.9k | [chubin/cheat.sh](https://github.com/chubin/cheat.sh) | Cheat sheet in terminal |
| **httpie** | 37.6k | [httpie/httpie](https://github.com/httpie/httpie) | User-friendly HTTP client |
| **textual** | 34.3k | [Textualize/textual](https://github.com/Textualize/textual) | Python TUI framework |
| **yazi** | 32.7k | [sxyazi/yazi](https://github.com/sxyazi/yazi) | Blazing fast terminal file manager |
| **modern-unix** | 32.8k | [ibraheemdev/modern-unix](https://github.com/ibraheemdev/modern-unix) | Modern alternatives to common unix commands |
| **hyperfine** | 27.5k | [sharkdp/hyperfine](https://github.com/sharkdp/hyperfine) | CLI benchmarking |
| **withfig/autocomplete** | 25.1k | [withfig/autocomplete](https://github.com/withfig/autocomplete) | IDE-style shell autocomplete |
| **shell_gpt** | 11.8k | [TheR1D/shell_gpt](https://github.com/TheR1D/shell_gpt) | CLI productivity powered by LLMs |
| **nnn** | 21.2k | [jarun/nnn](https://github.com/jarun/nnn) | Terminal file manager |
| **jira-cli** | 5.1k | [ankitpokhrel/jira-cli](https://github.com/ankitpokhrel/jira-cli) | Interactive Jira CLI |
| **multi-gitter** | 1.2k | [lindell/multi-gitter](https://github.com/lindell/multi-gitter) | Update multiple repos with one command |
| **gita** | 1.8k | [nosarthur/gita](https://github.com/nosarthur/gita) | Manage many git repos |
| **Clipboard** | 5.7k | [Slackadays/Clipboard](https://github.com/Slackadays/Clipboard) | Smart clipboard manager |
| **amazon-q-developer-cli** | 1.9k | [aws/amazon-q-developer-cli](https://github.com/aws/amazon-q-developer-cli) | Agentic chat in terminal; MCP |
| Tool | Stars | URL | Purpose |
|------|-------|-----|---------|
| **posting** | 11.4k | [darrenburns/posting](https://github.com/darrenburns/posting) | Modern API client in terminal; REST, SSH |
| **xh** | 7.6k | [ducaale/xh](https://github.com/ducaale/xh) | Friendly HTTP client; HTTPie design, Rust speed |
| **npkill** | 9k | [voidcosmos/npkill](https://github.com/voidcosmos/npkill) | Find and remove node_modules; free disk space |
| **gitsome** | 7.7k | [donnemartin/gitsome](https://github.com/donnemartin/gitsome) | Supercharged Git/GitHub CLI |
| **gitlogue** | 4.2k | [unhappychoice/gitlogue](https://github.com/unhappychoice/gitlogue) | Cinematic Git commit replay; animated history |
| **xplr** | 4.7k | [sayanarijit/xplr](https://github.com/sayanarijit/xplr) | Hackable TUI file explorer |
| **eza** | 32k | [eza-community/eza](https://github.com/eza-community/eza) | Modern ls replacement |
| **ripgrep** | 44k | [BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep) | Fast grep; respects gitignore |
| **fzf** | 68k | [junegunn/fzf](https://github.com/junegunn/fzf) | Fuzzy finder |
| **jq** | 29k | [jqlang/jq](https://github.com/jqlang/jq) | sed for JSON |
| **zoxide** | 22k | [ajeetdsouza/zoxide](https://github.com/ajeetdsouza/zoxide) | Smarter cd; learns your habits |
| **tldr** | 52k | [tldr-pages/tldr](https://github.com/tldr-pages/tldr) | Simplified man pages with examples |
| Tool | Stars | URL | Purpose |
|------|-------|-----|---------|
| **Mac-CLI** | 9k | [guarinogabriel/Mac-CLI](https://github.com/guarinogabriel/Mac-CLI) | macOS CLI for developers; automate common Mac tasks |
| **dembrandt** | 1.3k | [dembrandt/dembrandt](https://github.com/dembrandt/dembrandt) | Extract website design system to tokens; logo, colors, typography; Playwright |
| **sttr** | 1.3k | [abhimanyu003/sttr](https://github.com/abhimanyu003/sttr) | Cross-platform string operations CLI; encode, decode, transform, JSON |
| **codeface** | 6.4k | [chrissimpkins/codeface](https://github.com/chrissimpkins/codeface) | Typefaces for source code |
| **tqdm** | 31k | [tqdm/tqdm](https://github.com/tqdm/tqdm) | Progress bar for Python/CLI |
| **tach** | 2.6k | [tach-org/tach](https://github.com/tach-org/tach) | Visualize + enforce dependencies; monorepo |
| **terragrunt** | 9.3k | [gruntwork-io/terragrunt](https://github.com/gruntwork-io/terragrunt) | Terraform/OpenTofu orchestration |
| Tool | Stars | URL | Purpose |
|------|-------|-----|---------|
| **hoppscotch** | 77.8k | [hoppscotch/hoppscotch](https://github.com/hoppscotch/hoppscotch) | Open-source API dev ecosystem; Postman alternative; web, desktop, CLI |
| **httpbin** | 13.5k | [postmanlabs/httpbin](https://github.com/postmanlabs/httpbin) | HTTP request/response service; testing, debugging |
| **artillery** | 8.9k | [artilleryio/artillery](https://github.com/artilleryio/artillery) | Load testing platform; Playwright, HTTP, WebSocket, gRPC; serverless |
| Tool | Stars | URL | Purpose |
|------|-------|-----|---------|
| **netdata** | 77.7k | [netdata/netdata](https://github.com/netdata/netdata) | AI-powered full-stack observability; real-time metrics, alerting |
| **VictoriaMetrics** | 16.3k | [VictoriaMetrics/VictoriaMetrics](https://github.com/VictoriaMetrics/VictoriaMetrics) | Fast, cost-effective monitoring; time series DB; Prometheus-compatible |
| **hertzbeat** | 7k | [apache/hertzbeat](https://github.com/apache/hertzbeat) | AI-powered real-time observability; metrics, logs, alerts, status pages |
| **greptimedb** | 5.9k | [GreptimeTeam/greptimedb](https://github.com/GreptimeTeam/greptimedb) | Cloud-native observability DB; metrics, logs, traces; SQL/PromQL |
| Tool | Stars | URL | Purpose |
|------|-------|-----|---------|
| **goreplay** | 19.2k | [probelabs/goreplay](https://github.com/probelabs/goreplay) | Capture and replay live HTTP traffic for testing |
| **terratest** | 7.9k | [gruntwork-io/terratest](https://github.com/gruntwork-io/terratest) | Go library for automated infrastructure testing |
| **goss** | 5.9k | [goss-org/goss](https://github.com/goss-org/goss) | Quick server testing and validation |
| **inspec** | 3k | [inspec/inspec](https://github.com/inspec/inspec) | Auditing and testing framework; compliance |
| **pytest-testinfra** | 2.5k | [pytest-dev/pytest-testinfra](https://github.com/pytest-dev/pytest-testinfra) | Test infrastructure with pytest |
| **CheatSheets-for-Developers** | 1.2k | [crescentpartha/CheatSheets-for-Developers](https://github.com/crescentpartha/CheatSheets-for-Developers) | Programming cheatsheets; Git, Docker, SQL, etc. |
| Resource | Stars | URL | Scope |
|----------|-------|-----|-------|
| **AI-Coding-Style-Guides** | 471 | [lidangzzz/AI-Coding-Style-Guides](https://github.com/lidangzzz/AI-Coding-Style-Guides) | Code compression for Vibe Coding/SWE-Agents; maximize context; 8 compression levels |
| **rulebook-ai** | 572 | [botingw/rulebook-ai](https://github.com/botingw/rulebook-ai) | Vibe engineering rules; consistent prompts for Codex (proxy API), Cursor, Cline, Windsurf, Claude Code |
| **awesome-ralph** | 723 | [snwfdhmp/awesome-ralph](https://github.com/snwfdhmp/awesome-ralph) | Ralph loop: run AI agents until specs fulfilled; automated agent loops |
| **ralph-playbook** | — | [ClaytonFarr/how-to-ralph-wiggum](https://github.com/ClaytonFarr/how-to-ralph-wiggum) | How to run Lifecycle–style agent loops |
| **agentic-workflow-patterns** | — | [ThibautMelen/agentic-workflow-patterns](https://github.com/ThibautMelen/agentic-workflow-patterns) | Subagent, Progressive Skills, Master-Clone, Spec-Driven patterns |
| **ccpm** | 7.3k | [automazeio/ccpm](https://github.com/automazeio/ccpm) | Project management for Claude Code; GitHub Issues + git worktrees; parallel agent execution |
| **vibe-log-cli** | 282 | [vibe-log/vibe-log-cli](https://github.com/vibe-log/vibe-log-cli) | Log and analyze Claude Code / Cursor AI-driven sessions |
| Resource | Stars | URL | Scope |
|----------|-------|-----|-------|
| **clean-code-javascript** | 94.3k | [ryanmcdermott/clean-code-javascript](https://github.com/ryanmcdermott/clean-code-javascript) | Clean Code concepts adapted for JavaScript |
| **clean-code-typescript** | 9.7k | [labs42io/clean-code-typescript](https://github.com/labs42io/clean-code-typescript) | Clean Code + SOLID for TypeScript |
| **clean-code-php** | 12.5k | [piotrplenik/clean-code-php](https://github.com/piotrplenik/clean-code-php) | Clean Code concepts for PHP |
| **clean-code-dotnet** | 7.6k | [thangchung/clean-code-dotnet](https://github.com/thangchung/clean-code-dotnet) | Clean Code concepts and tools for .NET |
| **clean-code-python** | 4.8k | [zedr/clean-code-python](https://github.com/zedr/clean-code-python) | Clean Code concepts for Python |
| **Clean-Code-Notes** | 6.1k | [JuanCrg90/Clean-Code-Notes](https://github.com/JuanCrg90/Clean-Code-Notes) | Notes from Clean Code book |
| **evergreen-skills-developers** | 2.1k | [romenrg/evergreen-skills-developers](https://github.com/romenrg/evergreen-skills-developers) | Evergreen skills from software dev best practices; cross-framework principles; assessment |
| Resource | Stars | URL | Scope |
|----------|-------|-----|-------|
| **awesome-ddd** | 12.1k | [heynickc/awesome-ddd](https://github.com/heynickc/awesome-ddd) | Curated DDD, CQRS, Event Sourcing, Event Storming resources |
| **evolutionary-architecture-by-example** | 3.2k | [evolutionary-architecture/evolutionary-architecture-by-example](https://github.com/evolutionary-architecture/evolutionary-architecture-by-example) | .NET DDD; modular monolith, microservices; step-by-step guide |
| **ddd-hexagonal-cqrs-es-eda** | 1.4k | [bitloops/ddd-hexagonal-cqrs-es-eda](https://github.com/bitloops/ddd-hexagonal-cqrs-es-eda) | DDD + Hexagonal + CQRS + Event Sourcing + EDA; NestJS, TypeScript |
| **go-food-delivery-microservices** | 1.1k | [mehdihadeli/go-food-delivery-microservices](https://github.com/mehdihadeli/go-food-delivery-microservices) | Go DDD; CQRS, ES, Vertical Slice, Event-Driven; BDD |
| **pitstop** | 1.2k | [EdwinVW/pitstop](https://github.com/EdwinVW/pitstop) | Garage Management sample; DDD, CQRS, Event Sourcing; .NET |
| **Practical.CleanArchitecture** | 2.4k | [phongnguyend/Practical.CleanArchitecture](https://github.com/phongnguyend/Practical.CleanArchitecture) | Full-stack Clean Architecture; DDD, CQRS, microservices, modular monolith |
| Resource | Stars | URL | Scope |
|----------|-------|-----|-------|
| **awesome-eventstorming** | — | [mariuszgil/awesome-eventstorming](https://github.com/mariuszgil/awesome-eventstorming) | Event Storming resources; workshop format for complex domains |
| **awesome-domain-storytelling** | — | [hofstef/awesome-domain-storytelling](https://github.com/hofstef/awesome-domain-storytelling) | Domain Storytelling; [domainstorytelling.org](http://domainstorytelling.org) |
| **context-mapping** | — | [ddd-crew/context-mapping](https://github.com/ddd-crew/context-mapping) | Context Mapping Cheatsheet & Starter Kit; bounded context integration |
| Resource | Stars | URL | Scope |
|----------|-------|-----|-------|
| **static-analysis** | 14.4k | [analysis-tools-dev/static-analysis](https://github.com/analysis-tools-dev/static-analysis) | Curated SAST tools & linters for all languages; [analysis-tools.dev](https://analysis-tools.dev/) |
| **awesome-dynamic-analysis** | — | [mre/awesome-dynamic-analysis](https://github.com/mre/awesome-dynamic-analysis) | Sister project: dynamic analysis tools |
| **sonarqube** | 10.2k | [SonarSource/sonarqube](https://github.com/SonarSource/sonarqube) | Continuous inspection; code quality, security, bugs |
| **reviewdog** | 9.1k | [reviewdog/reviewdog](https://github.com/reviewdog/reviewdog) | Automated code review; integrates any linter with GitHub/GitLab/Bitbucket |
| **infer** | 15.5k | [facebook/infer](https://github.com/facebook/infer) | Static analyzer for Java, C, C++, Objective-C |
| **SwiftLint** | 19.5k | [realm/SwiftLint](https://github.com/realm/SwiftLint) | Swift style and conventions |
| **checkstyle** | 8.9k | [checkstyle/checkstyle](https://github.com/checkstyle/checkstyle) | Java coding standard; Google Java Style, configurable |
| **pyre-check** | 7.1k | [facebook/pyre-check](https://github.com/facebook/pyre-check) | Python type-checking; taint analysis |
| **detekt** | 6.8k | [detekt/detekt](https://github.com/detekt/detekt) | Kotlin static analysis |
| **pylint** | 5.7k | [pylint-dev/pylint](https://github.com/pylint-dev/pylint) | Python linter; code quality |
| **pmd** | 5.3k | [pmd/pmd](https://github.com/pmd/pmd) | Multilanguage static analyzer; Java, Apex, PL/SQL, Swift |
| **qlty** | 3k | [qltysh/qlty](https://github.com/qltysh/qlty) | Code quality CLI; universal linting, auto-formatting, security, maintainability |
| **goreporter** | 3.1k | [qax-os/goreporter](https://github.com/qax-os/goreporter) | Go: static analysis, unit testing, code review, quality report |
| **DeepAudit** | 4.6k | [lintsinghua/DeepAudit](https://github.com/lintsinghua/DeepAudit) | AI multi-agent code audit; vulnerability mining; SAST, PoC verification |
| **tach** | 2.6k | [tach-org/tach](https://github.com/tach-org/tach) | Visualize + enforce dependencies; modular architecture; monorepo |
| Tool | Stars | URL | Scope |
|------|-------|-----|-------|
| **eslint** | — | [eslint/eslint](https://github.com/eslint/eslint) | JavaScript/TypeScript linter; pluggable |
| **prettier** | — | [prettier/prettier](https://github.com/prettier/prettier) | Opinionated code formatter; multi-language |
| **ruff** | — | [astral-sh/ruff](https://github.com/astral-sh/ruff) | Fast Python linter + formatter; replaces flake8, black, isort |
| Resource | Stars | URL | Scope |
|----------|-------|-----|-------|
| **Claude Code Handbook** | — | [nikiforovall.blog/claude-code-rules](https://nikiforovall.blog/claude-code-rules/) | Best practices, tips, plugins |
| **Claude Code Tips** | — | [ykdojo/claude-code-tips](https://github.com/ykdojo/claude-code-tips) | 35+ tips; voice, system prompt, containers |
| **Claude Code Ultimate Guide** | — | [FlorianBruniaux/claude-code-ultimate-guide](https://github.com/FlorianBruniaux/claude-code-ultimate-guide) | Beginner→power user; templates; quizzes |
| **agentrules-architect** | 105 | [trevor-nichols/agentrules-architect](https://github.com/trevor-nichols/agentrules-architect) | AGENTS.md/CLAUDE.md generator for Codex, Claude Code, Cursor, Windsurf |
| **ruler** | 2.5k | [intellectronica/ruler](https://github.com/intellectronica/ruler) | Apply same rules to Claude Code, Codex, Cursor, Aider, Windsurf |
| Tip | Source | Purpose |
|-----|--------|---------|
| **check-console-log** | ECC | Block on `console.log` in TS/JS before commit |
| **post-edit-format** | ECC | Run Prettier after Edit |
| **post-edit-typecheck** | ECC | Run `tsc --noEmit` on .ts/.tsx after Edit |
| **strategic-compact** | ECC | Manual compaction suggestions; avoid context loss |
| **memory-persistence** | ECC | session-start, session-end, pre-compact; preserve context |
| Item | Status | Notes |
|------|--------|------|
| **Provider credentials** | ✓ | nim, minimax (PROVIDER_LOGIN_CONFIG); kilo, glm need provider_definitions.json |
| **Clode links** | ✓ | claudeglm, claudemax |
| **Dex links** | ✓ | dex, dexmax, dexglm, dexhaiku, dexopus, dexsonnet, dexstep, dexcomposer |
| **Cliproxy config** | ✓ | _ensure_config in setup |
| **MCP install** | ✓ | run_wizard (Cursor, Claude Code, Codex, Claude Desktop, Droid) |
| **Playwright removal** | ✓ | Optional in wizard; thegent bundles browser tools |
| **MCP mounts** | ✓ | Playwright, Serena, Octocode (all required); flyto-core (optional browser alternative) |
| Hook | Purpose |
|------|---------|
| `harvest-pending-queue.sh` | Harvest pending queue |
| `prompt-submit-guard.sh` | Guard prompt submission |
| `task-completion-verifier.sh` | Verify task completion |
| `posttool-dispatcher.sh` | Post-tool dispatch |
| `pretool-dispatcher.sh` | Pre-tool dispatch |
| `hook-watcher.sh` | Watch hooks |
| `security-pipeline.sh` | Security pipeline |
| `governance-gates.sh` | Governance gates |
| `quality-gate.sh` | Quality gate |
| `spec-verifier.sh` | Spec verification |
| `qa-preflight.sh` | QA preflight |
| `async-test-runner.sh` | Async test runner |
| `qa-policy-test.sh` | QA policy test |
| `test_cache_*.sh` | Cache tests |
| `auto-checkpoint.sh` | Auto checkpoint |
| `test-maturity.sh` | Test maturity |
| `gardener-loop.sh` | Gardener loop |
| `hook-config.yaml` | Hook configuration |
| Path | Type | Notes |
|------|------|-------|
| `.factory/droids/` | Factory droids | Droid definitions |
| `.factory/settings.json` | Factory config | |
| `.factory/config.json` | Factory config | |
| `skills/` | (empty) | Project skills; `.codex/skills/`, `.claude/skills/` |
| `.factory/plugins/marketplaces/` | Plugin marketplace | factory-plugins, droid-evolved, browser-navigation |
| MCP | Package/Command | Namespace | Mount Env |
|-----|-----------------|-----------|-----------|
| **thegent** | HTTP :3847 | (main) | — |
| **Playwright** | npx @playwright/mcp | browser | Required (default) |
| **Serena** | uvx serena start-mcp-server | serena | Required |
| **Octocode** | npx octocode-mcp | octocode | Required |
| **flyto-core** | python -m core.mcp_server or flyto serve | browser | THGENT_MCP_MOUNT_FLYTO=1 |
| **server-sequential-thinking** | npx @modelcontextprotocol/server-sequential-thinking | — | (client config) |
| **software-planning-mcp** | node build/index.js | — | (client config) |
| **next-devtools** | npx next-devtools-mcp | — | (client config) |
| Name | URL | Description | Incorporate? |
|------|-----|-------------|--------------|
| **flyto-core** | [github.com/flytohub/flyto-core](https://github.com/flytohub/flyto-core) | 300+ tools, 6 MCP tools, browser/file/API; low context | ✓ Mount option |
| **Serena** | [github.com/oraios/serena](https://github.com/oraios/serena) | LSP code tools (goto-def, find-refs) | ✓ Mount option |
| **Octocode** | [npm octocode-mcp](https://www.npmjs.com/package/octocode-mcp) | GitHub/code search | ✓ Mount option |
| **@playwright/mcp** | [npm @playwright/mcp](https://www.npmjs.com/package/@playwright/mcp) | Browser automation | ✓ Default mount |
| **software-planning-mcp** | Local / Cline | Planning, todos | □ Optional mount |
| **next-devtools** | [npm next-devtools-mcp](https://www.npmjs.com/package/next-devtools-mcp) | Next.js dev tools | □ Optional mount |
| **server-sequential-thinking** | @modelcontextprotocol/server-sequential-thinking | Chain-of-thought | □ Optional mount |
| **@modelcontextprotocol/server-memory** | npx @modelcontextprotocol/server-memory | Persistent memory | □ Client config |
| **@modelcontextprotocol/server-github** | npx @modelcontextprotocol/server-github | GitHub PRs, issues | □ Client config |
| **firecrawl-mcp** | npx firecrawl-mcp | Web scraping | □ Client config |
| **@context7/mcp-server** | npx @context7/mcp-server | Live docs lookup | □ Client config |
| **Figma-Context-MCP** | [GLips/Figma-Context-MCP](https://github.com/GLips/Figma-Context-MCP) | Figma layout for Cursor | □ Client config |
| **git-mcp** | [idosal/git-mcp](https://github.com/idosal/git-mcp) | Remote MCP for GitHub projects | □ Client config |
| **dbhub** | [bytebase/dbhub](https://github.com/bytebase/dbhub) | Postgres/MySQL/SQLite MCP | □ Client config |
| **claude-context** | [zilliztech/claude-context](https://github.com/zilliztech/claude-context) | Code search, full codebase context | □ Optional mount |
| **fastapi_mcp** | [tadata-org/fastapi_mcp](https://github.com/tadata-org/fastapi_mcp) | Expose FastAPI as MCP | □ Reference |
| **magic-mcp** | [21st-dev/magic-mcp](https://github.com/21st-dev/magic-mcp) | v0-like UI in Cursor/Windsurf/Cline | □ Client config |
| **mcpm.sh** | [pathintegral-institute/mcpm.sh](https://github.com/pathintegral-institute/mcpm.sh) | MCP package manager & registry | □ Optional tool |
| **memory-bank-mcp** | [alioshr/memory-bank-mcp](https://github.com/alioshr/memory-bank-mcp) | Remote memory for Cline/Cursor/Windsurf | □ Client config |
| **context7** | [upstash/context7](https://github.com/upstash/context7) | Up-to-date code docs for Cursor | □ Client config |
| **n8n-mcp** | [czlonkowski/n8n-mcp](https://github.com/czlonkowski/n8n-mcp) | Build n8n workflows from Cursor | □ Client config |
| **mcp-memory-service** | [doobidoo/mcp-memory-service](https://github.com/doobidoo/mcp-memory-service) | Auto context memory for Claude, Cursor | □ Client config |
| **Skill_Seekers** | [yusufkaraaslan/Skill_Seekers](https://github.com/yusufkaraaslan/Skill_Seekers) | Docs/GitHub/PDF → Claude skills | □ Optional tool |
| Item | Priority | Effort | Compatibility | Action |
|------|----------|--------|---------------|--------|
| Playwright | P0 | Done | Cursor, Codex, Claude | Required (default) |
| Serena | P0 | Done | Cursor, Codex, Claude | Required |
| Octocode | P0 | Done | Cursor, Codex, Claude | Required |
| flyto-core | P2 | Low | Cursor, Codex | Env flag |
| sequential-thinking | P2 | Low | All | Optional mount |
| software-planning-mcp | P2 | Low | Cursor, Cline | Optional mount |
| next-devtools | P2 | Low | Next.js projects | Optional mount |
| ECC skills/rules | P2 | Medium | Claude Code, Cursor | Sync template |
| ECC hooks | P2 | Medium | Claude Code | Reference only |
| pre-commit/husky | P3 | Low | Git | `setup --hooks` |
| ECC hook recipes | P3 | Low | Claude Code | Document in setup |
| Rulesync / claude-rules-doctor | P3 | Low | Config | Optional tools |
| git-mcp, dbhub, Figma MCP | P3 | Low | Per-project | Client config |
| Doc | URL | Use |
|-----|-----|-----|
| FastMCP Providers | [gofastmcp.com/servers/providers/overview](https://gofastmcp.com/servers/providers/overview) | Mounting, proxying |
| FastMCP Mounting | [gofastmcp.com/servers/providers/mounting](https://gofastmcp.com/servers/providers/mounting) | create_proxy, namespace |
| MCP Registry | [registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io/) | Discover servers |
| Awesome MCP | [wong2/awesome-mcp-servers](https://github.com/wong2/awesome-mcp-servers) | 100+ community servers |
| Serena clients | [oraios.github.io/serena/02-usage/030_clients](https://oraios.github.io/serena/02-usage/030_clients.html) | Cursor, Codex, Claude |
| ECC install | [everything-claude-code install.sh](https://github.com/affaan-m/everything-claude-code/blob/main/install.sh) | Rules/skills install |
| ECC hooks README | [hooks/README.md](https://github.com/affaan-m/everything-claude-code/blob/main/hooks/README.md) | Hook schema, recipes, async |
| awesome-agent-skills | [heilcheng/awesome-agent-skills](https://github.com/heilcheng/awesome-agent-skills) | Skill scopes, official sources |
| Codex skill docs | [developers.openai.com/codex/skills](https://developers.openai.com/codex/skills) | Codex skill scopes |
| Lifecycle playbook | [ClaytonFarr/how-to-ralph-wiggum](https://github.com/ClaytonFarr/how-to-ralph-wiggum) | Three phases, two prompts, loop mechanics |
| mcpm.sh | [pathintegral-institute/mcpm.sh](https://github.com/pathintegral-institute/mcpm.sh) | MCP package manager, router, profiles |
| skillshare | [runkids/skillshare](https://github.com/runkids/skillshare) | Cross-tool skill sync (Claude Code, OpenCode, Codex) |
| tokscale | [junhoyeo/tokscale](https://github.com/junhoyeo/tokscale) | Token usage tracking across AI CLIs |
| mcp-for-beginners | [microsoft/mcp-for-beginners](https://github.com/microsoft/mcp-for-beginners) | MCP fundamentals; .NET, Java, TS, Python, Rust |
| Skill_Seekers | [yusufkaraaslan/Skill_Seekers](https://github.com/yusufkaraaslan/Skill_Seekers) | Docs/GitHub/PDF → Claude skills |
| awesome-claude-code | [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | Primary curated list (23.9k★) |
| awesome-claude-skills | [travisvn/awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) | Claude Skills (7.2k★) |
| awesome-agent-skills | [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 300+ skills; Codex, Cursor, OpenCode |
| awesome-vibe-coding-guide | [analyticalrohit/awesome-vibe-coding-guide](https://github.com/analyticalrohit/awesome-vibe-coding-guide) | 10x Vibe Coder guide |
| awesome-ralph | [snwfdhmp/awesome-ralph](https://github.com/snwfdhmp/awesome-ralph) | Lifecycle resources |
| Claude Code Ultimate Guide | [FlorianBruniaux/claude-code-ultimate-guide](https://github.com/FlorianBruniaux/claude-code-ultimate-guide) | Beginner→power user |
| ai-guide | [liyupi/ai-guide](https://github.com/liyupi/ai-guide) | AI resource大全; Vibe Coding (6.9k★) |
| cursor.directory | [cursor.directory](https://cursor.directory/) | Cursor rules, MCPs, generate, jobs (72k+ members) |
| directories | [leerob/directories](https://github.com/leerob/directories) | Cursor Directory source, rules index |
| wshobson/agents | [wshobson/agents](https://github.com/wshobson/agents) | Multi-agent orchestration for Claude Code |
| Hook | Source | Purpose |
|------|--------|---------|
| pre-commit | [pre-commit.com](https://pre-commit.com/) | Git hooks framework |
| husky | [typicode.github.io/husky](https://typicode.github.io/husky/) | Node git hooks |
| lefthook | [github.com/evilmartians/lefthook](https://github.com/evilmartians/lefthook) | Fast git hooks |
| ECC hooks | everything-claude-code/hooks | session-start, session-end, compact |
| ECC hook recipes | hooks/README.md | TODO warn, block large files, ruff format, require tests |
| c0ntextKeeper | [Capnjbrown/c0ntextKeeper](https://github.com/Capnjbrown/c0ntextKeeper) | 7 hooks, 187 semantic patterns, 3 MCP tools; context preservation |
| Skill | Source | Purpose |
|-------|--------|---------|
| browser-navigation | .factory/plugins | Map to browser_* tools |
| agent-orchestra | skills/agent-orchestra | Multi-agent orchestration |
| BMAD workflows | .cursor/rules/bmad | Product, game, innovation workflows |
| ECC skills | everything-claude-code/skills | 37 skills: tdd, django, springboot, golang, etc. |
| anthropics/skills | [anthropics/skills](https://github.com/anthropics/skills) | docx, xlsx, pptx, pdf |
| openai/skills | [openai/skills](https://github.com/openai/skills) | Codex catalog |
| ComposioHQ awesome-claude-skills | 35k★, 500+ | Airtable, Slack, GitHub, etc. automation |
| awesome-agent-skills | [heilcheng/awesome-agent-skills](https://github.com/heilcheng/awesome-agent-skills) | Curated for Claude, Codex (proxy API) |
| Skill_Seekers | [yusufkaraaslan/Skill_Seekers](https://github.com/yusufkaraaslan/Skill_Seekers) | Docs, GitHub, PDF → Claude skills; conflict detection |
| Plugin | Source | Purpose |
|--------|--------|---------|
| Factory droid-evolved | .factory/plugins | Enhanced droid |
| everything-claude-code | /plugin install | 13 agents, 37 skills, 31 commands |
| Cline MCP | Cline | MCP integration |
| Cursor rules | .cursor/rules | Project rules |
| AgentSys | [avifenesh/agentsys](https://github.com/avifenesh/agentsys) | 12 plugins, 41 agents, 27 skills |
| claude-codex-settings | [fcakyon/claude-codex-settings](https://github.com/fcakyon/claude-codex-settings) | Battle-tested GitHub, Azure, Playwright |
| Rulesync | [dyoshikawa/rulesync](https://github.com/dyoshikawa/rulesync) | Config generator Claude↔others |
| skillshare | [runkids/skillshare](https://github.com/runkids/skillshare) | Sync skills across Claude Code, OpenCode, Codex, Cursor |
| agentrules-architect | [trevor-nichols/agentrules-architect](https://github.com/trevor-nichols/agentrules-architect) | AGENTS.md generator for Codex, Cursor, Windsurf, OpenCode |
| Workflow | Source | Purpose |
|----------|--------|---------|
| Lifecycle | [ghuntley.com/ralph](https://ghuntley.com/ralph), [how-to-ralph-wiggum](https://github.com/ClaytonFarr/how-to-ralph-wiggum) | Autonomous loop: specs → plan → build; fresh context per iteration |
| ralph-wiggum-marketer | ECC plugin | Autonomous copywriter for SaaS content |
| gru ralph | [zscole/gru](https://github.com/zscole/gru) | Ralph loop integrated into Gru |
| Tool | Purpose |
|------|---------|
| claude-rules-doctor | Detect dead rules (paths: globs) |
| ClaudeCTX | Switch Claude config with one command |
| recall | Full-text search sessions |
| claude-code-tools | Session continuity, Rust session search |
| tokscale | [junhoyeo/tokscale](https://github.com/junhoyeo/tokscale) | Token tracking: OpenCode, Claude Code, Codex (proxy API), Cursor |
| OpenContext | [0xranx/OpenContext](https://github.com/0xranx/OpenContext) | Personal context store; Tauri desktop app |
| c0ntextKeeper | [Capnjbrown/c0ntextKeeper](https://github.com/Capnjbrown/c0ntextKeeper) | Context preservation; 7 hooks, 187 patterns |
| mcp-memory-service | [doobidoo/mcp-memory-service](https://github.com/doobidoo/mcp-memory-service) | Auto context memory for 13+ AI tools |
| ruler | [intellectronica/ruler](https://github.com/intellectronica/ruler) | Same rules across Claude Code, Codex, Cursor, Aider |
| claude-squad | [smtg-ai/claude-squad](https://github.com/smtg-ai/claude-squad) | Manage Claude Code, Aider, Codex, OpenCode, Amp |
| ccpm | [automazeio/ccpm](https://github.com/automazeio/ccpm) | Project management; GitHub Issues + git worktrees |
| Template | Source | Purpose |
|----------|--------|---------|
| ECC CLAUDE.md | everything-claude-code/examples | SaaS Next.js, Django API, Go, Rust |
| meridian | [markmdev/meridian](https://github.com/markmdev/meridian) | Zero-config Claude Code; task scaffolding, TDD |
| fulling | [FullAgent/fulling](https://github.com/FullAgent/fulling) | Full-stack AI agent (Next.js, Claude, K8s) |
| crystal | [stravu/crystal](https://github.com/stravu/crystal) | Parallel Codex/Claude sessions in git worktrees |
- [ ] Add kilo, glm to provider_definitions.json (login block) for setup
- [ ] `thegent setup --hooks` to install hooks (pre-commit, husky, or thegent/hooks)
- [ ] `thegent setup --skills` to sync skills template (ECC or custom)
- [ ] Mount software-planning-mcp, next-devtools, sequential-thinking as optional providers
- [ ] Document flyto-core: `pip install flyto-core[browser]`, `playwright install chromium`
- [ ] Add ECC install reference: `./install.sh typescript` (or python/golang) for rules
- [ ] Link to MCP registry and awesome-mcp-servers for discovery
- [ ] Optional: `thegent setup --ecc` to install ECC rules/skills (with language selector)
- [ ] Optional: AgentShield scan integration (`npx ecc-agentshield scan`)
- [ ] Optional: Skill Creator from git history (`/skill-create` pattern)
- [ ] Optional: Lifecycle loop template (`loop.sh`, `PROMPT_plan.md`, `PROMPT_build.md`) for autonomous dev
- [ ] Optional: skillshare integration for cross-tool skill sync
- [ ] Optional: tokscale for token usage tracking
- [ ] Optional: ECC CLAUDE.md templates (SaaS, Django, Go, Rust) in setup
- [ ] Optional: c0ntextKeeper or mcp-memory-service for context preservation
- [ ] Optional: ruler for cross-tool rules sync
| Component | Status | Location |
|-----------|--------|----------|
| **Lazy Loading** | ✅ Complete | `shell/.zsh_optimization.zsh` |
| **Eval Caching** | ✅ Complete | `shell/.zsh_optimization.zsh` |
| **Performance Profiling** | ✅ Complete | `shell/.zsh_optimization.zsh` |
| **Command Safeguards** | ✅ Complete | `shell/.zsh_safeguards.zsh` |
| **Resource Management** | ✅ Complete | `shell/.zsh_safeguards.zsh` |
| **Instant Prompt** | ✅ Complete | `shell/.zsh_advanced.zsh` |
| **Async Loading** | ✅ Complete | `shell/.zsh_advanced.zsh` |
| **Advanced Caching** | ✅ Complete | `shell/.zsh_advanced.zsh` |
| **Error Recovery** | ✅ Complete | `shell/.zsh_advanced.zsh` |
| **CLI Commands** | ✅ Complete | `src/thegent/shell_cli.py` |
| Component | Target | Achieved |
|-----------|--------|----------|
| **First prompt lag** | `&lt; 50ms` | `&lt; 5ms` ✅ |
| **First command lag** | `&lt; 150ms` | `&lt; 50ms` ✅ |
| **Command lag** | `&lt; 10ms` | `&lt; 5ms` ✅ |
| **Input lag** | `&lt; 20ms` | `&lt; 10ms` ✅ |
| **Overall startup** | `&lt; 200ms` | `&lt; 150ms` ✅ |
| Metric | Target | Achieved |
|--------|--------|----------|
| **Process limit** | Controlled | 4096 ✅ |
| **File descriptors** | Controlled | 1024 ✅ |
| **Memory limit** | Controlled | 4GB ✅ |
| **Fork explosions** | Prevented | 100% ✅ |
| Component | Before | After | Improvement |
|-----------|--------|-------|-------------|
| **nvm** | ~500ms | ~50ms (lazy) | 90% |
| **rbenv** | ~65ms | ~8ms (cached) | 88% |
| **jenv** | ~45ms | ~6ms (cached) | 87% |
| **pyenv** | ~55ms | ~7ms (cached) | 87% |
| **direnv** | ~30ms | ~5ms (cached) | 83% |
| **Overall** | ~800ms | ~150ms | 81% |
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Process limit** | Unlimited | 4096 | Controlled |
| **File descriptors** | Unlimited | 1024 | Controlled |
| **Memory limit** | Unlimited | 4GB | Controlled |
| **Fork explosions** | Common | Prevented | 100% |
| Command | Protection | Status |
|---------|-----------|--------|
| **ls** | Tree/recursive prevention | ✅ |
| **find** | Timeout on -exec | ✅ |
| **git** | Passthrough for agents | ✅ |
| **eval** | Safe eval helper | ✅ |
| Resource | Protection | Status |
|----------|-----------|--------|
| **Processes** | ulimit + monitoring | ✅ |
| **File descriptors** | ulimit | ✅ |
| **Memory** | ulimit | ✅ |
| **Fork explosions** | Guard + limits | ✅ |
- [ ] Create `_thegent_lazy_load()` function
- [ ] Support for tool detection + on-demand loading
- [ ] Cache loaded state to avoid re-checking
- [ ] Integration with nvm, rbenv, jenv, direnv, etc.
- [ ] Create `_thegent_evalcache()` function
- [ ] Cache directory: `~/.cache/thegent/eval-cache/`
- [ ] TTL-based invalidation (default 1 hour)
- [ ] Hash-based cache keys (command + args)
- [ ] Automatic cleanup of stale cache
- [ ] Integrate `zsh/zprof` module
- [ ] Startup time measurement
- [ ] Per-module timing
- [ ] `thegent shell profile` command
- [ ] `thegent shell benchmark` command
- [ ] Background job system for non-critical setup
- [ ] Parallel tool detection
- [ ] Async cache warming
- [ ] ls wrapper (already done, enhance)
- [ ] cd wrapper (prevent accidental navigation)
- [ ] rm wrapper (confirm destructive operations)
- [ ] git wrapper (already done, enhance)
- [ ] sudo wrapper (log and confirm)
- [ ] Path traversal prevention
- [ ] Command injection prevention
- [ ] Secret detection in eval
- [ ] Environment variable validation
- [ ] Dynamic ulimit adjustment
- [ ] Process count monitoring
- [ ] Memory usage tracking
- [ ] Automatic cleanup helpers
- [ ] macOS-specific optimizations
- [ ] Linux-specific optimizations
- [ ] Windows/WSL support
- [ ] Nix-hybrid detection and integration
- [ ] Fast tool detection (cached)
- [ ] Graceful degradation
- [ ] Fallback chains
- [ ] `thegent shell config` command
- [ ] Per-project shell configs
- [ ] Config versioning
- [ ] Config migration
- [ ] Startup time tracking
- [ ] Resource usage logging
- [ ] Error reporting
- [ ] Health checks
- [ ] `thegent shell reload` command
- [ ] `thegent shell status` command
- [ ] `thegent shell doctor` command
- [ ] Comprehensive documentation
| Command | Purpose | Location | Status |
|---------|---------|----------|--------|
| `thegent prompts sync` | Harvest + list idea seeds from Cursor/Codex/Claude | `main.py:1601` | ✅ Working |
| `thegent rules sync` | Sync CLAUDE.md → AGENTS.md, Cursor, Codex | `main.py:1669` | ✅ Working |
| `thegent dag sync` | Update task status from session exit | `main.py:3307` | ✅ Working |
| `thegent dag update` | Update DAG state | `main.py:3217` | ✅ Working |
| `thegent plan incorporate` | Merge fragments into WORK_STREAM.md | `planning/work_stream.py` | ✅ Working |
| Command | Purpose | Location | Status |
|---------|---------|----------|--------|
| `thegent catalog update` | Update model catalog | `models/catalog.py` | ✅ Working |
| `thegent install` | Install/update components | `install.py` | ✅ Working |
| `thegent mcp install` | Install MCP configs | `mcp_manage.py` | ✅ Working |
| Component | Description | Current Command | Integration |
|-----------|-------------|-----------------|-------------|
| `rules` | Agent rules (CLAUDE.md → platforms) | `rules sync` | ✅ |
| `prompts` | Idea seed harvesting | `prompts sync` | ✅ |
| `dag` | DAG state synchronization | `dag sync` | ✅ |
| `work-stream` | WORK_STREAM.md incorporation | `plan incorporate` | ✅ |
| `mcp` | MCP server configs | Manual | 🔄 |
| `shims` | Binary shims (~/.local/bin) | `install -t shell` | 🔄 |
| `shell` | Shell configs (.zshrc, .zshenv) | `install -t shell` | 🔄 |
| `discovery` | Agent discovery state | `discovery/sync.py` | 🔄 |
| `cache` | Cache invalidation/refresh | Manual | 🔄 |
| Component | Description | Current Command | Integration |
|-----------|-------------|-----------------|-------------|
| `catalog` | Model catalog | `catalog update` | ✅ |
| `dependencies` | Python/system dependencies | `install` | 🔄 |
| `policies` | Governance policies | Manual | 🔄 |
| `config` | Configuration files | Manual | 🔄 |
| `shims` | Binary shims | `install -t shell` | 🔄 |
| `mcp-bundles` | MCP third-party bundles | `mcp install --bundle` | 🔄 |
| Audit Type | Description | Current Tool | Integration |
|------------|-------------|--------------|-------------|
| `config` | Configuration drift | Manual | 🔄 |
| `dependencies` | Dependency health | `doctor` | 🔄 |
| `security` | Security compliance | Manual | 🔄 |
| `performance` | Performance metrics | Manual | 🔄 |
| `work-stream` | Work stream health | Manual | 🔄 |
| `state` | State consistency | Manual | 🔄 |
| `drift` | Cross-component drift | Manual | 🔄 |
| ID | Task | Effort | Depends |
|----|------|--------|---------|
| SYNC-001 | Create `sync.py` module with component registry | 4h | — |
| SYNC-002 | Implement component discovery and registration | 4h | SYNC-001 |
| SYNC-003 | Create sync orchestrator with dependency resolution | 6h | SYNC-002 |
| SYNC-004 | Implement conflict detection and resolution | 8h | SYNC-003 |
| SYNC-005 | Add sync state tracking and persistence | 4h | SYNC-003 |
| SYNC-006 | Integrate existing sync commands (rules, prompts, dag) | 6h | SYNC-002 |
| SYNC-007 | Add CLI commands (`sync`, `update`) | 4h | SYNC-003 |
| SYNC-008 | Implement dry-run and watch modes | 4h | SYNC-007 |
| ID | Task | Effort | Depends |
|----|------|--------|---------|
| SYNC-101 | Extend `WorkStreamIntegration` with auto-discovery | 6h | SYNC-003 |
| SYNC-102 | Implement fragment scanner (plans/, research/, docset/) | 8h | SYNC-101 |
| SYNC-103 | Create incorporator agent for automatic merging | 8h | SYNC-102 |
| SYNC-104 | Add conflict resolution for work stream merges | 6h | SYNC-103 |
| SYNC-105 | Implement sprawl detection and expansion triggers | 6h | SYNC-102 |
| SYNC-106 | Add work stream health checks | 4h | SYNC-101 |
| SYNC-107 | Create work stream audit report | 4h | SYNC-106 |
| ID | Task | Effort | Depends |
|----|------|--------|---------|
| SYNC-201 | Create audit framework with plugin system | 6h | — |
| SYNC-202 | Implement config drift detection | 8h | SYNC-201 |
| SYNC-203 | Add dependency health audit (Python, system tools) | 6h | SYNC-201 |
| SYNC-204 | Implement security compliance audit | 8h | SYNC-201 |
| SYNC-205 | Add performance metrics collection | 6h | SYNC-201 |
| SYNC-206 | Create state consistency checks | 6h | SYNC-201 |
| SYNC-207 | Implement cross-component drift detection | 8h | SYNC-202 |
| SYNC-208 | Add audit report generation (rich/json/markdown) | 4h | SYNC-201 |
| SYNC-209 | Implement auto-fix for common issues | 6h | SYNC-208 |
| ID | Task | Effort | Depends |
|----|------|--------|---------|
| SYNC-301 | Integrate research sprawl detection | 6h | SYNC-102 |
| SYNC-302 | Add plan consolidation triggers | 4h | SYNC-301 |
| SYNC-303 | Implement research → work stream pipeline | 6h | SYNC-301 |
| SYNC-304 | Add plan → work stream pipeline | 4h | SYNC-302 |
| SYNC-305 | Create research sprawl progress tracking | 4h | SYNC-303 |
| SYNC-306 | Implement plan health checks | 4h | SYNC-304 |
| SYNC-307 | Add cross-reference validation | 6h | SYNC-304 |
| ID | Task | Effort | Depends |
|----|------|--------|---------|
| SYNC-401 | Implement incremental sync (only changed components) | 8h | SYNC-003 |
| SYNC-402 | Add sync performance optimization | 6h | SYNC-401 |
| SYNC-403 | Implement sync scheduling and cron integration | 4h | SYNC-003 |
| SYNC-404 | Add sync notifications (success/failure) | 4h | SYNC-003 |
| SYNC-405 | Create sync metrics and observability | 6h | SYNC-003 |
| SYNC-406 | Implement rollback for failed syncs | 6h | SYNC-003 |
| SYNC-407 | Add sync conflict resolution UI | 8h | SYNC-004 |
| Task | Description | Priority | Effort |
|------|-------------|----------|--------|
| RESEARCH-SYNC-001 | Research sync patterns in similar tools (git, rsync, unison) | P2 | 4h |
| RESEARCH-SYNC-002 | Research conflict resolution strategies | P1 | 6h |
| RESEARCH-SYNC-003 | Research incremental sync algorithms | P2 | 4h |
| RESEARCH-SYNC-004 | Research audit frameworks (ansible-lint, puppet-lint, etc.) | P2 | 4h |
| RESEARCH-SYNC-005 | Research work stream incorporation patterns | P1 | 6h |
| RESEARCH-SYNC-006 | Research state reconciliation patterns | P1 | 6h |
| Task | Description | Priority | Effort |
|------|-------------|----------|--------|
| RESEARCH-AUDIT-001 | Research configuration drift detection | P1 | 6h |
| RESEARCH-AUDIT-002 | Research dependency audit tools | P1 | 4h |
| RESEARCH-AUDIT-003 | Research security audit frameworks | P1 | 6h |
| RESEARCH-AUDIT-004 | Research performance audit patterns | P2 | 4h |
| RESEARCH-AUDIT-005 | Research state consistency checking | P1 | 6h |
- [ ] `thegent sync` syncs all components by default
- [ ] `thegent sync rules prompts` syncs only specified components
- [ ] `thegent sync --dry-run` shows what would sync without making changes
- [ ] `thegent sync --watch` runs continuous sync
- [ ] Sync conflicts are detected and reported
- [ ] Sync state is persisted and recoverable
- [ ] Sync performance is `&lt; 5s` for incremental syncs
- [ ] `thegent update` updates all components by default
- [ ] `thegent update --check` checks for updates without applying
- [ ] `thegent update catalog` updates only catalog
- [ ] Update conflicts are detected and resolved
- [ ] Update rollback is available for failed updates
- [ ] `thegent audit` audits all categories by default
- [ ] `thegent audit config dependencies` audits only specified types
- [ ] `thegent audit --fix` auto-fixes issues where possible
- [ ] Audit reports are generated in multiple formats
- [ ] Audit severity filtering works correctly
- [ ] Audit performance is `&lt; 10s` for full audit
- [ ] Auto-incorporation discovers new fragments
- [ ] Work stream conflicts are resolved automatically
- [ ] Sprawl detection triggers expansion
- [ ] Work stream health checks pass
- [ ] Cross-reference validation works
- [ ] Research sprawl detection works
- [ ] Plan consolidation triggers work
- [ ] Research → work stream pipeline functions
- [ ] Progress tracking is accurate
| sync-unified-command | Unified sync/update command implementation | This plan | P1 | — |
| sync-work-stream-integration | Work stream auto-incorporation | This plan | P1 | sync-unified-command |
| sync-audit-framework | System audit framework | This plan | P1 | sync-unified-command |
| sync-research-integration | Research sprawl integration | This plan | P1 | sync-work-stream-integration |
| sync-plan-consolidation | Plan consolidation automation | This plan | P1 | sync-work-stream-integration |
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Sync conflicts break existing workflows | High | Medium | Comprehensive conflict detection, dry-run mode, rollback |
| Performance degradation with full sync | Medium | Medium | Incremental sync, parallel execution, caching |
| Work stream incorporation creates duplicates | Medium | Low | Duplicate detection, conflict resolution |
| Audit false positives | Low | Medium | Configurable severity, auto-fix verification |
| Integration complexity | High | High | Phased implementation, extensive testing |
| Resource | Total | Reserved for System | Available for Agents | Per-Agent Target |
|----------|-------|---------------------|----------------------|------------------|
| **CPU Cores** | 10 (8P+2E) | 2 cores (20%) | 8 cores (80%) | ~26ms CPU/agent |
| **Memory** | 16GB | 4GB (25%) | 12GB (75%) | ~40MB/agent |
| **File Descriptors** | 10240 | 1024 (10%) | 9216 (90%) | ~30 FDs/agent |
| **I/O Bandwidth** | ~3GB/s | 0.5GB/s (17%) | 2.5GB/s (83%) | ~8MB/s/agent |
| **Network** | 1Gbps | 200Mbps (20%) | 800Mbps (80%) | ~2.7Mbps/agent |
| Pool Type | Base Size | Max Size | Scaling Strategy | CPU Affinity |
|-----------|-----------|----------|------------------|--------------|
| **Sync Workers** | `min(4, cores-2)` | `cores-1` | Scale with CPU load `&lt; 70%` | P-cores only |
| **Update Workers** | `min(2, cores//4)` | `cores//2` | Scale with I/O wait `&lt; 20%` | E-cores OK |
| **Audit Workers** | `min(2, cores//4)` | `cores//2` | Scale with memory `&lt; 80%` | E-cores OK |
| **Agent Processes** | Dynamic | 300+ | Adaptive based on resources | P+E cores |
| Component | CPU Affinity | Priority | Rationale |
|-----------|--------------|----------|-----------|
| **Sync Workers** | P-cores (0-7) | High | CPU-intensive, low latency required |
| **Update Workers** | E-cores (8-9) | Medium | I/O-bound, can tolerate lower clock |
| **Audit Workers** | E-cores (8-9) | Medium | Mixed workload, background priority |
| **Agent Processes** | P+E cores | Adaptive | Critical path, dynamic allocation |
| **System Reserve** | P-cores (6-7) | Reserved | Leave for OS, browsers, IDEs |
| Component | Scheduling Policy | Time Slice | Preemption |
|-----------|-------------------|------------|------------|
| **Sync Workers** | FIFO (SCHED_FIFO) | 10ms | Cooperative |
| **Update Workers** | RR (SCHED_RR) | 5ms | Preemptive |
| **Audit Workers** | NORMAL (SCHED_OTHER) | Default | Preemptive |
| **Agent Processes** | NORMAL with QoS | Default | Preemptive |
| Component | Base Budget | Max Budget | Scaling Strategy |
|-----------|-------------|------------|------------------|
| **Sync Daemon** | 100MB | 200MB | Fixed overhead |
| **Sync Workers** | 50MB/worker | 100MB/worker | Scale with pool size |
| **Update Workers** | 30MB/worker | 60MB/worker | Scale with pool size |
| **Audit Workers** | 40MB/worker | 80MB/worker | Scale with pool size |
| **Agent Processes** | 40MB/agent | 60MB/agent | Adaptive per agent |
| **Shared State** | 200MB | 500MB | SQLite WAL, caches |
| **Reserve** | 4GB | 4GB | System + other tasks |
| Operation | Current | Optimized | Strategy |
|-----------|---------|-----------|----------|
| **Config Read** | 1 file/read | Batch 100 files | `os.scandir()` + batch read |
| **Config Write** | 1 file/write | Batch 50 files | Atomic writes, fsync batching |
| **State Sync** | SQLite per-op | WAL mode + batch | Transaction batching |
| **Cache Update** | Per-file | Batch update | In-memory merge + flush |
| Phase | Operation | Overhead | Strategy |
|-------|-----------|----------|----------|
| **Spawn** | Process creation | `&lt; 50ms` | Pre-warmed pools, COW fork |
| **Initialize** | State loading | `&lt; 100ms` | Lazy loading, cached state |
| **Execute** | Sync/update/audit | Variable | Adaptive batching, parallel ops |
| **Complete** | State update | `&lt; 10ms` | Batch updates, async writes |
| **Cleanup** | Resource release | `&lt; 5ms` | Automatic GC, pool reuse |
| Load Level | CPU Usage | Memory Usage | I/O Wait | Action |
|------------|-----------|--------------|---------|--------|
| **Idle** | `&lt; 30%` | `&lt; 50%` | `&lt; 5%` | Scale up, allow 300+ agents |
| **Normal** | 30-70% | 50-80% | 5-15% | Maintain current limit |
| **High** | 70-90% | 80-90% | 15-25% | Throttle new agents, backpressure |
| **Critical** | > 90% | > 90% | > 25% | Emergency throttle, kill lowest priority |
| Operation Type | Base Batch Size | Max Batch Size | Scaling Factor |
|----------------|------------------|----------------|----------------|
| **File Reads** | 50 | 200 | CPU load `&lt; 50%`: ×2 |
| **File Writes** | 25 | 100 | I/O wait `&lt; 10%`: ×2 |
| **Config Parses** | 20 | 80 | Memory `&lt; 70%`: ×2 |
| **State Updates** | 100 | 500 | SQLite WAL: ×5 |
| **Network Requests** | 10 | 50 | Network `&lt; 50%`: ×2 |
| Event | L1 Invalidation | L2 Invalidation | L3 Invalidation |
|-------|-----------------|-----------------|-----------------|
| **Config Change** | Immediate | Immediate | Immediate |
| **State Update** | Immediate | Immediate | Immediate |
| **Work Stream Update** | Immediate | Immediate | Immediate |
| **TTL Expiry** | Per-entry | Per-entry | Per-entry |
| **Memory Pressure** | LRU eviction | LRU eviction | OS eviction |
| State Type | Storage | Write Strategy | Read Strategy |
|------------|---------|----------------|--------------|
| **Sync State** | SQLite WAL | Batch 100 ops | MVCC reads |
| **Work Stream** | SQLite WAL | Batch 50 ops | MVCC reads |
| **Audit Results** | SQLite WAL | Batch 200 ops | Indexed queries |
| **Config Cache** | Shared Memory | Atomic updates | Lock-free reads |
| Conflict Type | Resolution Strategy | Overhead | Success Rate |
|---------------|---------------------|----------|--------------|
| **Config Drift** | Merge with precedence | `&lt; 10ms` | 95% |
| **State Inconsistency** | Last-write-wins | `&lt; 5ms` | 99% |
| **Work Stream Merge** | Semantic merge | `&lt; 50ms` | 90% |
| **File Conflicts** | 3-way merge | `&lt; 100ms` | 85% |
| **Critical Conflicts** | Manual resolution | Variable | 100% |
| ID | Task | Effort | Depends |
|----|------|--------|---------|
| SYNC-501 | Create resource monitoring daemon | 8h | — |
| SYNC-502 | Implement CPU affinity and scheduling | 6h | SYNC-501 |
| SYNC-503 | Implement memory management (SHM, mmap) | 8h | SYNC-501 |
| SYNC-504 | Implement I/O optimization (batching, async) | 8h | SYNC-501 |
| SYNC-505 | Implement network optimization (pooling, batching) | 6h | SYNC-501 |
| SYNC-506 | Create process pool architecture | 8h | SYNC-502 |
| SYNC-507 | Implement adaptive resource allocation | 8h | SYNC-506 |
| SYNC-508 | Add load-based throttling | 6h | SYNC-507 |
| ID | Task | Effort | Depends |
|----|------|--------|---------|
| SYNC-001 | Create `sync.py` module with component registry | 4h | SYNC-506 |
| SYNC-002 | Implement component discovery and registration | 4h | SYNC-001 |
| SYNC-003 | Create sync orchestrator with dependency resolution | 6h | SYNC-002 |
| SYNC-004 | Implement conflict detection and resolution | 8h | SYNC-003 |
| SYNC-005 | Add sync state tracking and persistence | 4h | SYNC-003 |
| SYNC-006 | Integrate existing sync commands (rules, prompts, dag) | 6h | SYNC-002 |
| SYNC-007 | Add CLI commands (`sync`, `update`) | 4h | SYNC-003 |
| SYNC-008 | Implement dry-run and watch modes | 4h | SYNC-007 |
| SYNC-009 | Add intelligent batching | 8h | SYNC-003 |
| SYNC-010 | Implement multi-level caching | 8h | SYNC-003 |
| SYNC-011 | Add state management optimization (SQLite WAL) | 8h | SYNC-005 |
| SYNC-012 | Implement conflict resolution optimization | 6h | SYNC-004 |
| ID | Task | Effort | Depends |
|----|------|--------|---------|
| SYNC-101 | Extend `WorkStreamIntegration` with auto-discovery | 6h | SYNC-003 |
| SYNC-102 | Implement fragment scanner (plans/, research/, docset/) | 8h | SYNC-101 |
| SYNC-103 | Create incorporator agent for automatic merging | 8h | SYNC-102 |
| SYNC-104 | Add conflict resolution for work stream merges | 6h | SYNC-103 |
| SYNC-105 | Implement sprawl detection and expansion triggers | 6h | SYNC-102 |
| SYNC-106 | Add work stream health checks | 4h | SYNC-101 |
| SYNC-107 | Create work stream audit report | 4h | SYNC-106 |
| SYNC-108 | Optimize work stream incorporation (parallel, batch) | 8h | SYNC-103 |
| SYNC-109 | Add incremental work stream processing | 6h | SYNC-102 |
| SYNC-110 | Implement work stream state caching | 4h | SYNC-108 |
| ID | Task | Effort | Depends |
|----|------|--------|---------|
| SYNC-201 | Create audit framework with plugin system | 6h | — |
| SYNC-202 | Implement config drift detection | 8h | SYNC-201 |
| SYNC-203 | Add dependency health audit (Python, system tools) | 6h | SYNC-201 |
| SYNC-204 | Implement security compliance audit | 8h | SYNC-201 |
| SYNC-205 | Add performance metrics collection | 6h | SYNC-201 |
| SYNC-206 | Create state consistency checks | 6h | SYNC-201 |
| SYNC-207 | Implement cross-component drift detection | 8h | SYNC-202 |
| SYNC-208 | Add audit report generation (rich/json/markdown) | 4h | SYNC-201 |
| SYNC-209 | Implement auto-fix for common issues | 6h | SYNC-208 |
| SYNC-210 | Optimize audit performance (parallel, incremental) | 8h | SYNC-201 |
| SYNC-211 | Add audit result caching | 4h | SYNC-210 |
| SYNC-212 | Implement streaming audit reports | 6h | SYNC-208 |
| ID | Task | Effort | Depends |
|----|------|--------|---------|
| SYNC-301 | Integrate research sprawl detection | 6h | SYNC-102 |
| SYNC-302 | Add plan consolidation triggers | 4h | SYNC-301 |
| SYNC-303 | Implement research → work stream pipeline | 6h | SYNC-301 |
| SYNC-304 | Add plan → work stream pipeline | 4h | SYNC-302 |
| SYNC-305 | Create research sprawl progress tracking | 4h | SYNC-303 |
| SYNC-306 | Implement plan health checks | 4h | SYNC-304 |
| SYNC-307 | Add cross-reference validation | 6h | SYNC-304 |
| SYNC-308 | Optimize sprawl detection (heuristic, priority) | 6h | SYNC-301 |
| SYNC-309 | Implement batch sprawl expansion | 6h | SYNC-305 |
| SYNC-310 | Add sprawl progress caching | 4h | SYNC-305 |
| ID | Task | Effort | Depends |
|----|------|--------|---------|
| SYNC-401 | Implement incremental sync (only changed components) | 8h | SYNC-003 |
| SYNC-402 | Add sync performance optimization | 6h | SYNC-401 |
| SYNC-403 | Implement sync scheduling and cron integration | 4h | SYNC-003 |
| SYNC-404 | Add sync notifications (success/failure) | 4h | SYNC-003 |
| SYNC-405 | Create sync metrics and observability | 6h | SYNC-003 |
| SYNC-406 | Implement rollback for failed syncs | 6h | SYNC-003 |
| SYNC-407 | Add sync conflict resolution UI | 8h | SYNC-004 |
| SYNC-408 | Implement agent process coordination | 8h | SYNC-506 |
| SYNC-409 | Add multi-strategy routing | 8h | SYNC-408 |
| SYNC-410 | Implement predictive resource allocation | 6h | SYNC-507 |
| SYNC-411 | Add zero-friction agent operations | 8h | SYNC-408 |
| SYNC-412 | Implement extensible plugin system | 8h | SYNC-001 |
| SYNC-413 | Add comprehensive observability | 8h | SYNC-405 |
| SYNC-414 | Implement graceful degradation | 6h | SYNC-003 |
| Operation | Target | Measurement |
|-----------|-------|-------------|
| **Incremental Sync** | `&lt; 5s` | 95th percentile |
| **Full Sync** | `&lt; 30s` | 95th percentile |
| **Component Sync** | `&lt; 1s` | Per component |
| **Work Stream Incorporation** | `&lt; 10s` | 1000 fragments |
| **Conflict Resolution** | `&lt; 100ms` | Per conflict |
| **State Update** | `&lt; 10ms` | Per operation |
| Operation | Target | Measurement |
|-----------|-------|-------------|
| **Catalog Update** | `&lt; 2s` | 95th percentile |
| **Dependency Update** | `&lt; 5s` | 95th percentile |
| **Config Update** | `&lt; 1s` | Per config |
| **Shim Update** | `&lt; 3s` | All shims |
| **MCP Bundle Update** | `&lt; 5s` | Per bundle |
| Operation | Target | Measurement |
|-----------|-------|-------------|
| **Full Audit** | `&lt; 10s` | 95th percentile |
| **Config Audit** | `&lt; 2s` | Per component |
| **Dependency Audit** | `&lt; 3s` | All dependencies |
| **Security Audit** | `&lt; 5s` | Full scan |
| **Performance Audit** | `&lt; 2s` | Metrics collection |
| **Work Stream Audit** | `&lt; 1s` | Health check |
| Resource | Target | Measurement |
|----------|--------|-------------|
| **CPU Usage** | `&lt; 50%` | Average across all cores |
| **Memory Usage** | `&lt; 8GB` | RSS for all processes |
| **I/O Wait** | `&lt; 10%` | System I/O wait time |
| **File Descriptors** | `&lt; 9000` | Total FDs used |
| **Network Bandwidth** | `&lt; 500`Mbps | Average bandwidth |
| **Disk I/O** | `&lt; 1GB`/s | Average disk throughput |
| Metric | Target | Measurement |
|--------|--------|-------------|
| **Sync Overhead** | `&lt; 100ms` | Per agent operation |
| **Conflict Resolution** | `&lt; 50ms` | Per conflict |
| **State Access** | `&lt; 1ms` | Per read operation |
| **Resource Wait** | `&lt; 10ms` | Per gate check |
| **Routing Decision** | `&lt; 5ms` | Per route selection |
| Metric | Threshold | Severity | Action |
|--------|-----------|----------|--------|
| **CPU Usage** | > 90% for 5min | Critical | Throttle agents, alert |
| **Memory Usage** | > 90% for 5min | Critical | Prune processes, alert |
| **I/O Wait** | > 25% for 5min | High | Throttle I/O, alert |
| **Sync Latency** | > 30s | High | Investigate, alert |
| **Conflict Rate** | > 10% | Medium | Review, alert |
| **Agent Count** | > 350 | Medium | Review, alert |
| sync-unified-command | Unified sync/update command implementation | This plan | P1 | — |
| sync-work-stream-integration | Work stream auto-incorporation | This plan | P1 | sync-unified-command |
| sync-audit-framework | System audit framework | This plan | P1 | sync-unified-command |
| sync-research-integration | Research sprawl integration | This plan | P1 | sync-work-stream-integration |
| sync-plan-consolidation | Plan consolidation automation | This plan | P1 | sync-work-stream-integration |
| sync-resource-management | OS-level resource management | This plan | P1 | sync-unified-command |
| sync-process-pools | Process pool architecture | This plan | P1 | sync-resource-management |
| sync-cpu-affinity | CPU affinity and scheduling | This plan | P1 | sync-process-pools |
| sync-memory-optimization | Memory management optimization | This plan | P1 | sync-resource-management |
| sync-io-optimization | I/O optimization (batching, async) | This plan | P1 | sync-resource-management |
| sync-network-optimization | Network optimization (pooling, batching) | This plan | P1 | sync-resource-management |
| sync-agent-coordination | Agent process coordination | This plan | P1 | sync-process-pools |
| sync-multi-strategy-routing | Multi-strategy routing | This plan | P1 | sync-agent-coordination |
| sync-concurrent-safety | Concurrent agent safety (lock-free, optimistic) | This plan | P1 | sync-agent-coordination |
| sync-evolution-support | Evolution support (v1 → v2) | This plan | P1 | sync-concurrent-safety |
| sync-lock-handling | Lock issue handling (review/expansion mode) | This plan | P1 | sync-evolution-support |
| sync-intelligent-batching | Intelligent batching | This plan | P1 | sync-unified-command |
| sync-multi-level-cache | Multi-level caching | This plan | P1 | sync-unified-command |
| sync-state-optimization | State management optimization | This plan | P1 | sync-unified-command |
| sync-conflict-optimization | Conflict resolution optimization | This plan | P1 | sync-unified-command |
| sync-work-stream-optimization | Work stream incorporation optimization | This plan | P1 | sync-work-stream-integration |
| sync-audit-optimization | Audit performance optimization | This plan | P1 | sync-audit-framework |
| sync-ws-research-component | Research sync component (40+ items) | This plan | P1 | sync-work-stream-integration |
| sync-ws-impl-component | Implementation sync component (30+ items) | This plan | P1 | sync-work-stream-integration |
| sync-ws-wp-component | Work package sync component (40+ items) | This plan | P1 | sync-work-stream-integration |
| sync-ws-vitepress-component | VitePress sync component (10+ items) | This plan | P1 | sync-work-stream-integration |
| sync-ws-update-components | Work stream update components | This plan | P1 | sync-ws-research-component |
| sync-ws-audit-plugins | Work stream audit plugins | This plan | P1 | sync-audit-framework |
| sync-ws-robustification | Robustification triggers and execution | This plan | P1 | sync-ws-research-component |
| sync-ws-health-monitoring | Work stream health monitoring | This plan | P1 | sync-ws-audit-plugins |
| sync-observability | Comprehensive observability | This plan | P1 | sync-unified-command |
| sync-plugin-system | Extensible plugin system | This plan | P1 | sync-unified-command |
| sync-metrics-dashboard | Metrics dashboard | This plan | P1 | sync-observability |
| sync-tracing-integration | Distributed tracing integration | This plan | P1 | sync-observability |
| sync-alerting-rules | Alerting rules and channels | This plan | P1 | sync-observability |
| sync-incremental-sync | Incremental sync (only changed components) | This plan | P1 | sync-unified-command |
| sync-rollback | Rollback for failed syncs | This plan | P1 | sync-unified-command |
| sync-scheduling | Sync scheduling and cron integration | This plan | P2 | sync-unified-command |
| sync-notifications | Sync notifications (success/failure) | This plan | P2 | sync-unified-command |
| sync-conflict-ui | Sync conflict resolution UI | This plan | P2 | sync-conflict-optimization |
| sync-predictive-allocation | Predictive resource allocation | This plan | P1 | sync-resource-management |
| sync-zero-friction | Zero-friction agent operations | This plan | P1 | sync-agent-coordination |
| sync-graceful-degradation | Graceful degradation | This plan | P1 | sync-unified-command |
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Sync conflicts break existing workflows | High | Medium | Comprehensive conflict detection, dry-run mode, rollback |
| Performance degradation with full sync | Medium | Medium | Incremental sync, parallel execution, caching |
| Work stream incorporation creates duplicates | Medium | Low | Duplicate detection, conflict resolution |
| Audit false positives | Low | Medium | Configurable severity, auto-fix verification |
| Integration complexity | High | High | Phased implementation, extensive testing |
| **Resource exhaustion (300+ agents)** | **Critical** | **Medium** | **Adaptive limits, load-based throttling, process pruning** |
| **CPU saturation** | **Critical** | **Medium** | **CPU affinity, priority scheduling, load balancing** |
| **Memory exhaustion** | **Critical** | **Medium** | **Memory management, SHM, mmap, pooling** |
| **I/O saturation** | **High** | **Medium** | **I/O batching, async I/O, throttling** |
| **Network saturation** | **Medium** | **Low** | **Connection pooling, request batching, rate limiting** |
| **Process pool exhaustion** | **High** | **Medium** | **Dynamic scaling, process reuse, pool management** |
| **State corruption** | **Critical** | **Low** | **Atomic operations, WAL mode, conflict resolution** |
| **Functionality regression** | **High** | **Low** | **Comprehensive testing, backward compatibility, gradual rollout** |
| Task | Description | Priority | Effort |
|------|-------------|----------|--------|
| RESEARCH-SYNC-001 | Research sync patterns in similar tools (git, rsync, unison) | P2 | 4h |
| RESEARCH-SYNC-002 | Research conflict resolution strategies | P1 | 6h |
| RESEARCH-SYNC-003 | Research incremental sync algorithms | P2 | 4h |
| RESEARCH-SYNC-004 | Research audit frameworks (ansible-lint, puppet-lint, etc.) | P2 | 4h |
| RESEARCH-SYNC-005 | Research work stream incorporation patterns | P1 | 6h |
| RESEARCH-SYNC-006 | Research state reconciliation patterns | P1 | 6h |
| **RESEARCH-SYNC-007** | **Research OS-level scheduler patterns (CFS, O(1), CFS)** | **P1** | **8h** |
| **RESEARCH-SYNC-008** | **Research process pool architectures (prefork, worker, thread pool)** | **P1** | **6h** |
| **RESEARCH-SYNC-009** | **Research CPU affinity and scheduling (pthread, sched_setaffinity)** | **P1** | **6h** |
| **RESEARCH-SYNC-010** | **Research memory management (SHM, mmap, COW)** | **P1** | **8h** |
| **RESEARCH-SYNC-011** | **Research I/O optimization (io_uring, kqueue, async I/O)** | **P1** | **8h** |
| **RESEARCH-SYNC-012** | **Research network optimization (connection pooling, HTTP/2, QUIC)** | **P2** | **6h** |
| **RESEARCH-SYNC-013** | **Research adaptive resource allocation (control theory, PID controllers)** | **P1** | **8h** |
| **RESEARCH-SYNC-014** | **Research intelligent batching (dynamic batching, adaptive batching)** | **P1** | **6h** |
| **RESEARCH-SYNC-015** | **Research multi-level caching (L1/L2/L3, cache coherence)** | **P1** | **6h** |
| Task | Description | Priority | Effort |
|------|-------------|----------|--------|
| RESEARCH-AUDIT-001 | Research configuration drift detection | P1 | 6h |
| RESEARCH-AUDIT-002 | Research dependency audit tools | P1 | 4h |
| RESEARCH-AUDIT-003 | Research security audit frameworks | P1 | 6h |
| RESEARCH-AUDIT-004 | Research performance audit patterns | P2 | 4h |
| RESEARCH-AUDIT-005 | Research state consistency checking | P1 | 6h |
| **RESEARCH-AUDIT-006** | **Research resource monitoring (Prometheus, OpenTelemetry)** | **P1** | **6h** |
| **RESEARCH-AUDIT-007** | **Research performance profiling (cProfile, py-spy, perf)** | **P1** | **6h** |
| **RESEARCH-AUDIT-008** | **Research memory profiling (memory_profiler, tracemalloc)** | **P1** | **4h** |
| **RESEARCH-AUDIT-009** | **Research I/O profiling (iotop, strace, DTrace)** | **P2** | **4h** |
| Metric | Threshold | Severity | Action |
|--------|-----------|----------|--------|
| **Sync Latency (p95)** | > 30s | High | Investigate, alert |
| **Update Failure Rate** | > 5% | High | Investigate, alert |
| **Audit Issues** | > 100 | Medium | Review, alert |
| **Resource Exhaustion** | CPU > 90% OR Memory > 90% | Critical | Throttle, alert |
| **Agent Count** | > 350 | Medium | Review, alert |
| **Conflict Rate** | > 10% | Medium | Review, alert |
| Category | Count | Sync Component | Update Component | Audit Component |
|----------|-------|----------------|------------------|-----------------|
| **Supermemory Integration** | 1 | `research-supermemory` | `research-supermemory-update` | `research-supermemory-audit` |
| **Routing Research** | 2 | `research-routing` | `research-routing-update` | `research-routing-audit` |
| **Cross-Platform** | 6 | `research-cross-platform` | `research-cross-platform-update` | `research-cross-platform-audit` |
| **Hook Rust Migration** | 5 | `research-hook-rust` | `research-hook-rust-update` | `research-hook-rust-audit` |
| **Library Replacement** | 6 | `research-library` | `research-library-update` | `research-library-audit` |
| **Phase Documents** | 6 | `research-phase` | `research-phase-update` | `research-phase-audit` |
| **Governance** | 3 | `research-governance` | `research-governance-update` | `research-governance-audit` |
| **Cost Routing** | 1 | `research-cost-routing` | `research-cost-routing-update` | `research-cost-routing-audit` |
| **Other Research** | 10+ | `research-other` | `research-other-update` | `research-other-audit` |
| Category | Count | Sync Component | Update Component | Audit Component |
|----------|-------|----------------|------------------|-----------------|
| **Library Migrations** | 6 | `impl-library` | `impl-library-update` | `impl-library-audit` |
| **Hook Rust** | 4 | `impl-hook-rust` | `impl-hook-rust-update` | `impl-hook-rust-audit` |
| **TUI Compositor** | 3 | `impl-tui` | `impl-tui-update` | `impl-tui-audit` |
| **Advanced Features** | 4 | `impl-advanced` | `impl-advanced-update` | `impl-advanced-audit` |
| **Documentation** | 10+ | `impl-docs` | `impl-docs-update` | `impl-docs-audit` |
| **Other Implementation** | 3+ | `impl-other` | `impl-other-update` | `impl-other-audit` |
| Category | Count | Sync Component | Update Component | Audit Component |
|----------|-------|----------------|------------------|-----------------|
| **WP-2x (Poison Pill, etc.)** | 5 | `wp-2x` | `wp-2x-update` | `wp-2x-audit` |
| **WP-3x (Governance, etc.)** | 10+ | `wp-3x` | `wp-3x-update` | `wp-3x-audit` |
| **WP-4x (Simulation, etc.)** | 10+ | `wp-4x` | `wp-4x-update` | `wp-4x-audit` |
| **WP-5x (Cost, Routing, etc.)** | 10+ | `wp-5x` | `wp-5x-update` | `wp-5x-audit` |
| **WP-6x (Other)** | 5+ | `wp-6x` | `wp-6x-update` | `wp-6x-audit` |
| Category | Count | Sync Component | Update Component | Audit Component |
|----------|-------|----------------|------------------|-----------------|
| **VitePress Setup** | 4 | `vitepress-setup` | `vitepress-setup-update` | `vitepress-setup-audit` |
| **VitePress Generators** | 5 | `vitepress-generators` | `vitepress-generators-update` | `vitepress-generators-audit` |
| **VitePress Workflow** | 1 | `vitepress-workflow` | `vitepress-workflow-update` | `vitepress-workflow-audit` |
| ID | Task | Effort | Depends |
|----|------|--------|---------|
| SYNC-601 | Create work stream sync components (research, impl, wp, vitepress) | 12h | SYNC-003 |
| SYNC-602 | Implement work stream update components | 8h | SYNC-601 |
| SYNC-603 | Create work stream audit plugins | 8h | SYNC-201 |
| SYNC-604 | Implement evolution support (v1 → v2) | 12h | SYNC-601 |
| SYNC-605 | Add lock issue handling (review/expansion mode) | 8h | SYNC-604 |
| SYNC-606 | Implement robustification triggers | 6h | SYNC-601 |
| SYNC-607 | Add concurrent agent safety (lock-free reads, optimistic writes) | 8h | SYNC-604 |
| SYNC-608 | Optimize work stream performance (incremental, caching, parallel) | 10h | SYNC-601 |
| SYNC-609 | Integrate all 115+ backlog items | 16h | SYNC-601 |
| SYNC-610 | Add work stream health monitoring | 6h | SYNC-603 |
| Component | Purpose | thegent Mapping |
|-----------|---------|-----------------|
| **Tools** | Executable capabilities | run, bg, ps, status, logs, wait, stop, list-agents, list-droids, list-models, dag-list |
| **Resources** | Read-only data | Session logs, DAG session spec, agent config |
| **Prompts** | Parameterized templates | "Run agent X with prompt Y", "Create WBS for feature Z" |
| Paradigm | Use Case for thegent |
|----------|----------------------|
| **Progress** | `ctx.report_progress()` during long `run`; stream log tail |
| **Background Tasks** | `task=True` for `run`—client gets task ID, polls for result |
| **Context** | Logging, progress, session state (owner, cwd) |
| **Transforms** | Namespace (`thegent_*`) to avoid conflicts when composing servers |
| **Resources** | Session logs as `thegent://session/{id}/logs`; DAG as `thegent://dag` |
| **Prompts** | Pre-built "run agent" and "create WBS" templates |
| **Elicitation** | Ask for missing `--cd` or `--owner` when ambiguous |
| **Structured Output** | Return `ToolResult` with `structured_content` for session_id, status, etc. |
| **Tool Annotations** | `read_only`, `destructive`, `idempotent` hints |
| **Notifications** | `resources/list_changed` when sessions start/stop |
| Aspect | Stdio | Streamable HTTP |
|--------|-------|-----------------|
| Long runs | Blocks; no progress | `ctx.report_progress()`; SSE polling; EventStore resumability |
| Log streaming | Pipe-based, single consumer | SSE stream; multiple subscribers |
| Multi-client | One process per client | Single server, many clients |
| Load balancer | N/A | SSE polling avoids idle timeouts (SEP-1699) |
| Deployment | Local/desktop only | Remote, centralized |
| Tool | Args | Returns | Annotations | Task |
|------|------|---------|-------------|------|
| `thegent_run` | agent, prompt, cd?, mode?, timeout?, full?, model? | stdout/stderr summary | destructive | optional |
| `thegent_bg` | agent, prompt, cd?, mode?, timeout?, owner?, model? | session_id, log_path | destructive | forbidden |
| `thegent_ps` | owner?, all? | list of sessions | read_only, idempotent | forbidden |
| `thegent_status` | session_id | status, pid, owner | read_only, idempotent | forbidden |
| `thegent_logs` | session_id, tail?, stderr? | log content | read_only | forbidden |
| `thegent_wait` | session_id, timeout? | exit_code | read_only | optional |
| `thegent_stop` | session_id, force? | stopped | destructive | forbidden |
| `thegent_list_agents` | — | agent names + backends | read_only, idempotent | forbidden |
| `thegent_list_droids` | cd? | droid names | read_only, idempotent | forbidden |
| `thegent_list_models` | provider? | model list | read_only, idempotent | forbidden |
| `thegent_dag_list` | cd? | DAG tasks | read_only, idempotent | forbidden |
| `thegent_inspect` | session_ids?, owner?, tail?, stderr? | status+logs per session | read_only, idempotent | forbidden |
| URI | Template | Content | MIME |
|-----|----------|---------|------|
| `thegent://sessions` | — | List of sessions (JSON) | application/json |
| `thegent://session/{id}/meta` | {id} | Session metadata | application/json |
| `thegent://session/{id}/logs` | {id} | Stdout log tail | text/plain |
| `thegent://session/{id}/logs{?stderr,tail}` | {id}, stderr?, tail? | Logs with options | text/plain |
| `thegent://dag` | — | DAG session from .factory/dag-session.md | text/markdown |
| `thegent://agents` | — | Agent list | application/json |
| `thegent://models{?provider}` | provider? | Model list | application/json |
| Prompt | Args | Returns |
|--------|------|---------|
| `thegent_run_agent` | agent, prompt, cd?, mode? | User message: "Run agent X with prompt Y" |
| `thegent_create_wbs` | feature, scope? | User message: "Create WBS for feature X" |
| `thegent_bg_task` | agent, prompt, owner? | User message: "Start background task with agent X" |
| Interface | Use Case |
|-----------|----------|
| **CLI** | Scripts, automation, direct human use, CI |
| **MCP** | Cursor, Claude Code, Gemini CLI, other MCP clients |
| Extra | Packages |
|-------|----------|
| (default) | typer, rich, pydantic, pydantic-settings, python-dotenv |
| mcp | fastmcp>=3.0.0rc1 |
| mcp[tasks] | fastmcp[tasks] (Docket for background tasks) |
| Variable | Default | Description |
|----------|---------|-------------|
| THGENT_MCP_HOST | 127.0.0.1 | Bind address |
| THGENT_MCP_PORT | 3847 | HTTP port |
| THGENT_MCP_PATH | /mcp | MCP endpoint path |
| FASTMCP_DOCKET_URL | memory:// | Task backend (memory or redis://) |
- [ ] Cursor MCP config: add thegent server; tools visible
- [ ] `thegent_run` with gemini/cursor-agent returns output
- [ ] `thegent_bg` returns session_id; `thegent_ps` lists it
- [ ] Progress updates during long `thegent_run` (Phase 3)
- [ ] Resources `thegent://session/{id}/logs` return log content (Phase 2)
- [ ] Prompts render correctly (Phase 2)
| Item | How to verify |
|------|---------------|
| Cursor MCP config | In Cursor: Settings → MCP → Add server. URL: `http://127.0.0.1:3847/mcp`. Restart Cursor; tools should appear. |
| `thegent_run` | From MCP client or CLI: call `thegent_run` with agent=gemini or cursor-agent, prompt="Hello". Expect stdout in result. |
| `thegent_bg` / `thegent_ps` | Call `thegent_bg` with agent, prompt; note session_id. Call `thegent_ps`; session should appear. |
| Progress updates | Run long `thegent_run`; check for progress notifications in MCP stream. |
| Resources | Call `thegent_bg`, get session_id. Read resource `thegent://session/{id}/logs`; expect log content. |
| Prompts | List prompts via MCP; render a prompt with args; verify output. |
| Backend | Use Case | thegent Applicability |
|---------|----------|------------------------|
| Memory | Default; dev | Session state, EventStore (single process) |
| Disk | Single-server prod | `DiskStore(directory="/var/cache/thegent")` for response cache |
| Redis | Multi-server, horizontal scaling | `RedisStore(host=...)` for EventStore, session_state, OAuth, Docket |
| Middleware | Purpose | thegent Use |
|------------|---------|-------------|
| `LoggingMiddleware` | Request/response logging | Observability |
| `StructuredLoggingMiddleware` | JSON logs for Datadog/Splunk | Production logging |
| `TimingMiddleware` | Execution duration | Per-request timing |
| `ResponseCachingMiddleware` | Cache tool/resource/prompt calls | Cache `thegent_ps`, `thegent_list_agents` (TTL) |
| `RateLimitingMiddleware` | Token bucket rate limit | Protect `thegent_run` from abuse |
| `ErrorHandlingMiddleware` | Centralized error logging | Production error handling |
| `PingMiddleware` | Keep connections alive | Long-lived HTTP sessions |
| `ResponseLimitingMiddleware` | Truncate large tool responses | Limit `thegent_logs` size |
| Dependency | Purpose | thegent Use |
|------------|---------|-------------|
| `CurrentContext()` | ctx for logging, progress, elicitation | All tools |
| `Depends(get_default_cwd)` | Inject cwd from request meta | Hide from LLM schema |
| `CurrentHeaders()` | HTTP headers (x-user-id, etc.) | Optional auth |
| `CurrentRequest()` | Full Starlette Request | Client IP, user-agent |
| `Progress()` | Task progress (task=True only) | thegent_run background |
| Dimension | Strategy | Implementation |
|-----------|----------|----------------|
| **Latency** | Cache read-heavy tools; lazy-load expensive data | `ResponseCachingMiddleware` for `thegent_ps`, `list_agents`, `list_models`; TTL 30s; cache key = `(tool, owner, all)` |
| **Throughput** | Avoid blocking; parallelize where safe | `asyncio.to_thread(run_impl)` for sync run; no blocking in event loop |
| **Memory** | Bound response size; stream large outputs | `ResponseLimitingMiddleware(max_size=500_000)`; `thegent_logs` with `tail=N` default (e.g. 100 lines) |
| **Connection reuse** | Keep-alive; avoid connection churn | Default HTTP keep-alive; `PingMiddleware` for long SSE sessions |
| **Idempotency** | Safe retries for read-only tools | `idempotent` annotation on ps, status, logs, list_*; clients can retry without side effects |
| **Batch hints** | Reduce round-trips | `thegent_ps` returns full session list; client filters client-side; avoid N+1 status calls |
| Dimension | Strategy | Implementation |
|-----------|----------|----------------|
| **Tool descriptions** | Agent-optimized; action-oriented | "Run agent X with prompt Y. Returns stdout/stderr. Use cd for project dir." — not "Executes run command" |
| **Parameter docs** | Clear defaults, units, constraints | `timeout`: "Seconds. Default 300. Max 3600."; `tail`: "Lines. Default 100. Max 10000." |
| **Error messages** | Actionable; include remediation | `"Session abc not found. Use thegent_ps to list sessions or thegent_bg to start one."` |
| **Response shape** | Consistent; machine-parseable | All tools return `ToolResult` with `structured_content` + `content` (human-readable); `meta.execution_time_ms` |
| **Naming** | Consistent; predictable | `session_id` everywhere (not `id`/`sid`); `cd` for cwd; `owner` for session owner tag |
| **Enums** | Expose valid values in schema | `mode`: `["sync","bg"]`; `provider`: from `list_models` keys |
| Dimension | Strategy | Implementation |
|-----------|----------|----------------|
| **Observability** | Structured logs; spans; metrics | `ctx.info("thegent_run", agent=agent, cd=cd)`; OpenTelemetry span per tool; `execution_time_ms` in meta |
| **Extensibility** | Hooks for custom behavior | `on_before_run`, `on_after_run` callbacks (if FastMCP supports); or middleware `on_call_tool` |
| **Discoverability** | Self-documenting; versioned | `thegent://meta` resource with server version, capabilities; `version="1.0"` on tools |
| **Composability** | Namespace; no collisions | `Namespace("thegent")`; all URIs `thegent://`; prompts `thegent_*` |
| **Graceful degradation** | Fallbacks when optional deps missing | No sampling? Return raw prompt; no Redis? Use memory EventStore; log warning, don't fail |
| **Progressive enhancement** | Core works; extras optional | Core tools work without tasks, elicitation, EventStore; add when configured |
| Dimension | Strategy | Implementation |
|-----------|----------|----------------|
| **Timeouts** | Per-tool; per-request; fail-fast | `thegent_run`: `timeout` param (default 300s); `thegent_wait`: `timeout` param; HTTP request timeout > max tool timeout |
| **Retries** | Exponential backoff for transient failures | CLI impl retries subprocess spawn (1 retry, 2s delay); MCP layer: no retry (client responsibility) |
| **Input validation** | Strict; reject invalid early | `session_id`: non-empty, format check; `agent`: must exist in list_agents; `cd`: path exists or elicitation |
| **Resource limits** | Prevent runaway consumption | Rate limit `thegent_run` (2 concurrent per client?); max `tail` 10000; max `timeout` 3600 |
| **Error boundaries** | Catch, log, return structured error | `ToolError` for session-not-found; generic 500 → `{"error":"internal","message":"..."}`; never leak stack traces |
| **Cleanup** | Orphan prevention; TTL | Session logs TTL; EventStore `ttl=3600`; Docket task retention |
| **Concurrency safety** | No shared mutable state races | Session state in process-local dict or Redis; no global mutable caches without locking |
| **Graceful shutdown** | Drain in-flight; no orphan tasks | Lifespan teardown: stop accepting new runs; wait for active runs up to 30s; then exit |
| **Backpressure** | Limit concurrent heavy operations | Max N concurrent `thegent_run` per server; queue or reject excess with 503 + Retry-After |
| **Strict validation** | Reject malformed input at schema level | `strict_input_validation=True` for production; Pydantic models for tool args where beneficial |
| Dimension | Strategy | Implementation |
|-----------|----------|----------------|
| **Defaults** | Sensible for 80% case | `cd` = cwd; `owner` = "default"; `timeout` = 300; `tail` = 100; `mode` = sync |
| **Fail-fast** | Surface errors immediately | Invalid agent → error before spawn; missing session → error with hint |
| **Predictability** | Same input → same output (read-only) | `thegent_ps` with same args → deterministic order; cache invalidates on session change |
| **Discoverability** | Easy to explore | `thegent_list_agents` → use in run; `thegent_ps` → use session_id in status/logs/wait/stop |
| **Composability** | Works with other MCP servers | No global state; namespace avoids conflicts; resources/prompts as tools for tool-only clients |
| **Developer ergonomics** | Easy to debug | `ctx.debug()` on entry; `execution_time_ms` in response; health route with version |
| Principle | Application |
|-----------|-------------|
| **Single source of truth** | `cli_impl` is canonical; CLI and MCP both call it; no duplicated logic |
| **Separation of concerns** | MCP layer: transport, progress, elicitation; impl layer: business logic, subprocess, files |
| **Explicit over implicit** | `cd` passed explicitly or elicited; no magic env vars; config via env with docs |
| **Fail loudly** | Required deps missing → startup failure; invalid input → ToolError with message |
| **Minimal surface area** | Expose only what clients need; hide implementation details in resources |
| **Backward compatibility** | Version tools; `VersionFilter` for API surfaces; deprecate, don't remove |
| **Testability** | `*_impl` pure functions; inject cwd, owner; mock subprocess for unit tests |
| **Observability first** | Logging, tracing, metrics from day one; not bolted on later |
| Metric | Target | Notes |
|--------|--------|-------|
| `thegent_ps` p50 | `&lt; 50ms` | Cached; in-memory session list |
| `thegent_status` p50 | `&lt; 20ms` | Single session lookup |
| `thegent_run` | User-controlled | Progress reported; timeout enforced |
| `thegent_logs` p95 | `&lt; 200ms` | Bounded by `tail`; stream if very large |
| Health check | `&lt; 10ms` | No DB; simple 200 |
| Tool list (tools/list) | `&lt; 100ms` | 11 tools; no pagination needed |
| Tool | Icon / Hint | Purpose |
|------|-------------|---------|
| `thegent_run` | `▶` or "play" | Indicates execution |
| `thegent_bg` | `⏸` or "background" | Fire-and-forget |
| `thegent_stop` | `⏹` or "stop" | Destructive; confirm in UI |
| `thegent_logs` | `▤` or "logs" | Read-only output |
| `thegent_ps` | `≡` or "list" | Discovery |
| Test Type | Scope | Examples |
|-----------|-------|----------|
| **Unit** | `*_impl` in isolation | Mock subprocess; assert return shape; invalid input → error |
| **Contract** | MCP schema stability | Tools list matches expected; params have correct types |
| **Integration** | Full MCP server | `thegent serve` + client; run → status → logs → stop |
| **Chaos** | Failure injection | Kill subprocess mid-run; assert clean error; reconnect after EventStore |
| **Load** | Rate limit, concurrency | N parallel runs; assert rate limit kicks in; no deadlock |
| **Timeout** | Long operations | Run with 5s timeout; assert exit; wait with 1s timeout; assert timeout error |
| Anti-pattern | Instead |
|--------------|---------|
| Silent failure when optional dep missing | Log warning; degrade gracefully; document in response |
| Blocking sync in async tool | `asyncio.to_thread(sync_fn)` |
| Generic "Error" message | Specific: "Session xyz not found. Use thegent_ps to list." |
| Exposing implementation details in errors | User-facing message; details in logs only |
| Global mutable cache without TTL | Bounded cache with invalidation or TTL |
| Duplicating logic between CLI and MCP | Single `*_impl`; both call it |
| Magic defaults (implicit cwd from unknown source) | Explicit param or elicitation |
| Unbounded `tail` or `timeout` | Cap with sensible max; document in schema |
- [ ] Error messages include remediation hint
- [ ] Tool descriptions updated for agent consumption
- [ ] `ToolResult` with `structured_content` + `meta.execution_time_ms`
- [ ] Input validation at boundary; reject invalid early
- [ ] `ctx.info` on entry, `ctx.error` on failure
- [ ] No blocking in async tools; use `to_thread` for sync impl
- [ ] Rate limit and response limit considered for new tools
- [ ] Graceful degradation path for optional features (sampling, Redis)
| Phase | Session ID | Owner | Status | Notes |
|-------|------------|-------|--------|-------|
| 3A | 20260214T140659Z-copilot-p89542-7b1b2010 | kooshapari:thegent | exited | thegent_run async + progress + TaskConfig |
| 3C | 20260214T140659Z-copilot-p89604-992ab1bb | kooshapari:thegent | exited | ToolResult for bg, status, wait, stop |
| 3D | 20260214T140700Z-copilot-p89726-e962c049 | kooshapari:thegent | exited | ResourcesAsTools, PromptsAsTools |
| 3B | 20260214T141123Z-cursor-p91109-12d376df | fastmcp-p3b | exited | Elicitation |
| 4A | 20260214T141123Z-cursor-p91320-2b55bb6a | fastmcp-p4a | exited | EventStore + SSE polling |
| 4C | 20260214T141124Z-cursor-p91512-73ddddc9 | fastmcp-p4c | exited | Lifespan |
| 4B, 4log, 6, 7, pns | — | — | direct impl | Agent spawns failed (cursor/copilot/glm args); implemented directly |
| Item | Status |
|------|--------|
| Middleware (ErrorHandling, RateLimiting, Timing, ResponseCaching, ResponseLimiting, Logging) | Done |
| thegent://models{?provider} resource | Done |
| thegent://meta resource | Done |
| thegent_suggest_prompt (ctx.sample) | Done |
| ctx.info / _log.info in tools | Done |
| close_sse_stream in thegent_run (every 30s) | Done (already present) |
| Criteria | Textual | Zellij Plugin | Decision |
|----------|---------|---------------|----------|
| Language | Python ✅ | Rust | Textual (matches stack) |
| Integration | Native ✅ | Plugin API | Textual (easier) |
| Styling | CSS-like ✅ | Limited | Textual (modern) |
| Widgets | 60+ ✅ | Limited | Textual (rich) |
| Web Export | `textual serve` ✅ | No | Textual (bonus) |
- [ ] Add `textual` to `pyproject.toml` dependencies
- [ ] Create `src/thegent/tui/` directory structure
- [ ] Implement base `CompositorApp` class
- [ ] Add menubar widget (File, Edit, View, Tools, Help)
- [ ] Add statusbar widget (session info, agent status)
- [ ] Implement keyboard shortcuts (Ctrl+C, Ctrl+V, etc.)
- [ ] Add basic layout (single pane)
- [ ] Test basic app startup
- [ ] Research terminal pane widget options:
- [ ] Implement terminal pane widget
- [ ] Add pane splitting (horizontal/vertical)
- [ ] Implement layout management (save/restore)
- [ ] Add session persistence (save layouts to disk)
- [ ] Test multi-pane layouts
- [ ] Implement floating windows/dialogs
- [ ] Add plugin system (load external widgets)
- [ ] Implement theme support (dark/light, custom)
- [ ] Add web export (`textual serve` integration)
- [ ] Add configuration file support
- [ ] Documentation and examples
- [ ] Basic app launches with menubar and statusbar
- [ ] Terminal panes can be created and split
- [ ] Layouts can be saved and restored
- [ ] Keyboard shortcuts work correctly
- [ ] Performance targets met
- [ ] Integration with sitback agent works
- [ ] Documentation complete
| Project | Role | Primary Surface |
|---------|------|-----------------|
| **thegent** | **Control Plane & Orchestration** | Typer CLI, FastMCP, Registry |
| **Helios Guard** | **Mesh Coordination & Harness** | tmpfs IPC, tmux Injection, Worktrees |
| Component | Responsibility | Implementation |
|-----------|----------------|----------------|
| **Registry** | Agent discovery & capability indexing | `thegent/src/thegent/agents/registry.py` |
| **Harness** | Low-level process/terminal management | `heliosShield/bin/harness`, `tmux` |
| **Governance** | Policy enforcement & trust scoring | `thegent/src/thegent/governance/` |
| **IPC Mesh** | Low-latency inter-agent communication | `tmpfs` at `/tmp/agent-mesh`, `maildir` |
| **Contract** | Canonical Structured Message (CSM v1) | `thegent/src/thegent/contracts/csm.py` |
| ID | Pattern | Source | Unified Implementation |
|----|---------|--------|------------------------|
| **P-001** | **CSM v1** | thegent | All mesh agents output CSM-compliant logs. |
| **P-011** | **Atomic Claim** | Helios | Task claiming via `mkdir` EEXIST on tmpfs. |
| **P-034** | **3-State Breaker** | thegent | Circuit breakers for mesh-wide provider failures. |
| **P-040** | **MAST 14-Mode** | thegent | Recovery playbooks for mesh-level errors. |
| **P-069** | **Hash-Chained Audit** | thegent | Every mesh event (claim, vote, merge) is chained. |
| **P-085** | **Risk-Based SLA** | thegent | High-risk mesh actions (Phase 16) require consensus. |
| **P-112** | **Bully Election** | Helios | Automated leader election for mesh coordinator. |
- [ ] **Read CSM v1:** `thegent/src/thegent/contracts/csm.py`
- [ ] **Check Mesh State:** `/tmp/agent-mesh/agents/`
- [ ] **Broadcast Intent:** `thegent/src/thegent/governance/heliosShield_bridge.py`
- [ ] **Respect Worktrees:** Never edit files outside assigned worktree.
- [ ] **Escalate Early:** Use `mesh escalation` for blocked states.
| Step | Action |
|------|--------|
| 1 | **Preflight:** Check if provider already has credentials in cliproxy config (or .env). If yes, show "Already configured" and optionally offer to re-run. |
| 2 | **Open URL:** Open provider's key/signup page in browser. |
| 3 | **Prompt for key:** Ask user to paste API key in terminal. |
| 4 | **Store:** Write key to cliproxy config (openai-compatibility block). |
| 5 | **Done:** "Restart proxy to apply: thegent cliproxy restart" |
| Provider | Key URL | API base-url | Config name |
|----------|---------|--------------|-------------|
| minimax | platform.minimax.io/user-center/.../interface-key | api.minimax.io/v1 | minimax |
| glm | open.bigmodel.cn/usercenter/apikeys | open.bigmodel.cn/api/paas/v4 | glm |
| nim | build.nvidia.com (model page) | ngc.nvidia.com or build.nvidia.com | nim |
| kilo | kilo.ai/api-keys | api.kilo.ai/v1 | kilo |
| claude | console.anthropic.com/settings/keys | api.anthropic.com | claude |
| codex | platform.openai.com/api-keys | api.openai.com/v1 | codex |
| gemini | aistudio.google.com/apikey | generativelanguage.googleapis.com | gemini |
| roo | roocode.com (signup) | api.roocode.com/v1 | roo |
| antigravity | antigravity.ai | (OAuth; fallback to CLIProxy) | antigravity |
| qwen | dashscope.aliyun.com | dashscope.aliyuncs.com/compatible-mode/v1 | qwen |
| Goal | Approach |
|------|----------|
| **One app** | Single unified application: tray + desktop window + chat + dashboard |
| **One installer** | Unified installer: thegent CLI, MCP, cliproxy, skills, hooks, provider auth, tray app |
| **One surface** | Chat + project/directory split (ChatGPT-style); sitback dashboard; terminal panes |
| **Low overhead** | Ghostty-like feel; Tauri 2 or SwiftUI; minimize memory/CPU |
| **Scalable** | 300 logical agents (M `&lt;``&lt; 300` physical slots); resource gates |
| Source | Content | Merge Target |
|--------|---------|--------------|
| [2026-02-15-tray-application-design.md](./2026-02-15-tray-application-design.md) | Tray app, heliosShield + thegent plugins | Tray + main window |
| [2026-02-14-thegent-install-design.md](./2026-02-14-thegent-install-design.md) | `thegent install` → ~/.claude, ~/.factory | Unified installer Phase 1 |
| [2026-02-14-thegent-install-implementation-plan.md](./2026-02-14-thegent-install-implementation-plan.md) | Install implementation | Unified installer |
| [CONVERSATION_DUMP_2026-02-16.md](../research/CONVERSATION_DUMP_2026-02-16.md) | TUIOS, Zellij, Textual, Ghostty | UI layer options |
| [2026-02-15-thegent-sitback-design.md](./2026-02-15-thegent-sitback-design.md) | Sitback agent, dashboard | Chat/dashboard surface |
| [OPENCLAW_AGENTZERO_AS_MAIN_AGENT_RESEARCH.md](../research/OPENCLAW_AGENTZERO_AS_MAIN_AGENT_RESEARCH.md) | OpenClaw/Agent Zero as runtime | Optional main agent |
| Component | Current | Unified |
|-----------|---------|---------|
| thegent CLI | `uv tool install`, pip | Bundled in unified installer |
| MCP server | `thegent serve` | Auto-started by app; port 3847 |
| CLIProxy | `task cliproxy:build`, config | Bundled; auto-configured |
| Skills, hooks | `thegent install` | Part of unified install |
| Claude Code, Codex, Cursor | Manual install | Optional; installer can prompt/link |
| Tray app | Separate (tray-app/) | Core of unified app |
| Shims (codex, copilot, etc.) | `thegent install-shims` | Part of unified install |
| Layer | Option A | Option B | Option C |
|-------|----------|----------|----------|
| **Desktop shell** | Tauri 2 (Rust + WebView) | SwiftUI (macOS) | PyQt/PySide (Python) |
| **Tray** | Tauri tray / SwiftUI menu bar | Same | Same |
| **Chat UI** | WebView (React/Svelte) | Native Swift | Qt widgets |
| **Terminal panes** | libghostty, xterm.js, or embed Zellij | Same | Same |
| **TUI overlay** | Textual (Python) for menus/status | — | — |
| Phase | Action |
| 1 | `thegent install` (skills, hooks, ~/.claude, ~/.factory) |
| 2 | `thegent install-shims` (codex, copilot, clode) |
| 3 | `task cliproxy:build` + `task cliproxy:ensure-config` |
| 4 | MCP server config → Cursor, Claude Code, Codex |
| 5 | Tray app: install, register launchd/systemd |
| 6 | Provider auth: prompt for `thegent cliproxy login X` |
| Resource | Limit (M1 Pro, 16GB) | Gate |
|----------|----------------------|------|
| RAM | 4GB for agents | Cap active slots |
| CPU | 1–2 cores | Throttle spawn |
| FD | 10k system limit | Reuse, close idle |
| Disk | 20GB reserved | Session log rotation |
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
| Always | Restart on any exit |
| OnFailure | Restart only on non-zero exit |
| Never | No restart |
| Directive | Example |
|-----------|---------|
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
|-----------|---------|
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
- [ ] `thegent crew create` - Create crew
- [ ] `thegent crew execute` - Execute crew
- [ ] `thegent crew list` - List crews
- [ ] `thegent crew show` - Show crew details
- [ ] `thegent crew status` - Show execution status
- [ ] Test TaskExecutor dependency resolution
- [ ] Test CrewExecutor execution modes
- [ ] Test WorkflowEngine stage dependencies
- [ ] Test RouterManager routing strategies
- [ ] Test MonitoringEngine metrics
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
| Task write (atomicity) | `&lt;1ms` | File write + atomic move |
| SmolGent startup | 100-200ms | Process/thread spawn |
| Task execution | 1-30s | Actual work (varies by type) |
| Result write | `&lt;1ms` | Atomic move |
| Result polling (1 iteration) | 10ms | Check .mgmt/results/ |
| Aggregation | 100-500ms | LLM call to combine results |
| **Total (best case)** | **2-10s** | Sequential, no parallelism |
| **Total (with parallelism)** | **1-5s** | Multiple SmolGents in parallel |
| Resource | Per SmolGent | Notes |
|----------|--------------|-------|
| Memory | 10-50MB | Varies by type (code-search uses rg, minimal) |
| CPU | 1 core active during execution | Mostly idle (I/O bound) |
| Storage | .mgmt/ dir: `&lt;100MB` | Task files + results (gc periodically) |
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
- [ ] File IPC overhead: `&lt;1%` of task execution time
- [ ] Memory per SmolGent: `&lt;50MB`
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
| Add `thegent skill install clawhub:&lt;name>` (or similar) | Medium | Pull community skills into thegent |
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
| Document | Location | Size | Purpose |
|----------|----------|------|---------|
| **Proposal** | `docs/changes/research-library-cache/proposal.md` | 70 L | Problem + Goals + Rationale |
| **Design** | `docs/changes/research-library-cache/design.md` | 241 L | Architecture + Patterns + Files |
| **Tasks** | `docs/changes/research-library-cache/tasks.md` | 245 L | Phased Breakdown + Criteria |
| **README** | `docs/changes/research-library-cache/README.md` | 380 L | Change Overview + Quick Start |
| **Synthesis** | `docs/research/CONVERSATION_DUMP_2026-02-18-cache-synthesis.md` | 462 L | Executive Summary + Readiness |
| Aspect | Detail |
|--------|--------|
| **What** | Replace custom caching with `cachetools` v6.0.0 |
| **Why** | Reduce code duplication, improve safety, align with Library-First Policy |
| **Where** | `src/lib/project_cache.py` (wrapper) + per-module replacements |
| **Effort** | ~30-35 min (13-15 tasks, parallelizable) |
| **Risk** | 🟢 Low (isolated change, well-tested library) |
| **Value** | >150 LOC reduction, zero breaking changes |
- [ ] All custom cache classes removed (100%)
- [ ] All cache usages replaced with cachetools
- [ ] Wrapper follows project conventions (`&lt;50 LOC`)
- [ ] All existing tests pass (100% pass rate)
- [ ] Code reduction: >150 LOC
- [ ] Coverage maintained: 80%+
- [ ] Quality gates: 0 errors
- [ ] Zero new lint suppressions
- [ ] Documentation updated (audit + CLAUDE.md)
- [ ] Change archived (post-merge)
| Risk | Mitigation |
|------|-----------|
| Breaking change | Thorough test coverage, baseline test per cache |
| Performance regression | Profile before/after, benchmark hot paths |
| Memory overhead | Monitor with profiler, review sizes |
| Thread safety | Use `lock` param in decorator when needed |
| Missed call sites | Grep verification, type checker confirmation |
| Phase | Tasks | Time | Parallelizable? |
|-------|-------|------|-----------------|
| 1: Setup | 2 | 2 min | N/A |
| 2: Wrapper | 2 | 5 min | No |
| 3: Discovery | 1 | 3 min | **Yes** (run with 1-2) |
| 4: Migration | 3-5 | 10-15 min | **Yes** (all per-cache) |
| 5: Validation | 3 | 5 min | No (aggregates) |
| 6: Docs | 2 | 5 min | Yes |
| **Total** | **13-15** | **30-35 min** | **20-25 min critical path** |
| Question | Answer Location |
|----------|-----------------|
| What's the problem? | `proposal.md` — Problem Statement section |
| How are we solving it? | `design.md` — Architecture Overview section |
| What are the tasks? | `tasks.md` — Phased Work Breakdown section |
| How do I start? | `README.md` — Quick Start section |
| What could go wrong? | `design.md` — Risk Assessment section |
| How do I validate? | `synthesis.md` — Testing Strategy section |
| How do I rollback? | `design.md` — Rollback Plan section |
| Document | Location | Lines | Status |
|----------|----------|-------|--------|
| Proposal | `docs/changes/research-library-cache/proposal.md` | 70 | ✅ Complete |
| Design | `docs/changes/research-library-cache/design.md` | 241 | ✅ Complete |
| Tasks | `docs/changes/research-library-cache/tasks.md` | 245 | ✅ Complete |
| README | `docs/changes/research-library-cache/README.md` | 380 | ✅ Complete |
| Synthesis | `docs/research/CONVERSATION_DUMP_2026-02-18-cache-synthesis.md` | 462 | ✅ Complete |
| Document | Location | Purpose | Status |
|----------|----------|---------|--------|
| Quick Index | `docs/research/CACHE_LIBRARY_IMPLEMENTATION_INDEX.md` | Navigation guide | ✅ Complete |
| This Report | `docs/research/CACHE_RESEARCH_COMPLETION_REPORT.md` | Completion summary | ✅ Complete |
- [ ] All custom cache classes removed (100%)
- [ ] All cache usages replaced with cachetools
- [ ] Wrapper follows project conventions (`&lt;50 LOC`)
- [ ] All existing tests pass (100% pass rate)
- [ ] Code reduction: >150 LOC
- [ ] Coverage maintained: 80%+
- [ ] Quality gates: 0 errors
- [ ] Zero new lint suppressions
- [ ] Documentation updated
- [ ] Change archived (post-merge)
| Risk | Probability | Mitigation | Status |
|------|-------------|-----------|--------|
| Breaking change | Low | Thorough test coverage, baseline tests | ✅ Planned |
| Performance regression | Very Low | Profile before/after, benchmark | ✅ Optional (post-merge) |
| Memory overhead | Very Low | Monitor with profiler | ✅ Unlikely |
| Thread safety issues | Low | Use `lock` param when needed | ✅ Documented |
| Missed call sites | Low | Grep + type checker verification | ✅ Systematic approach |
| Component | Status | Location |
|-----------|--------|----------|
| **TTLCache** | ✅ Implemented | `cli_impl.py` (CWD cache) |
| **Pre-warm command** | ✅ Implemented | `cli.py` |
| **File-based cache** | ✅ Implemented | `ultra-shim.go` |
| **Multi-level cache** | ❌ Not implemented | — |
| **File indexing** | ❌ Not implemented | — |
| **Frecency** | ❌ Not implemented | — |
| Policy | Use Case | Implementation |
|--------|----------|----------------|
| **LRU (Least Recently Used)** | General caching | `cachetools.LRUCache` |
| **LFU (Least Frequently Used)** | Long-term caching | `diskcache` supports LFU |
| **TTL (Time To Live)** | Time-sensitive data | `cachetools.TTLCache` |
| **Frecency** | Navigation, history | Custom implementation (see §5) |
| Aspect | Details |
|--------|---------|
| **Document Type** | Deep research & strategy guide |
| **Lines** | ~839 lines |
| **Sections** | 14 sections covering caching, indexing, pre-warming strategies |
| **Status** | Research complete, ready for implementation |
| **Key Findings** | Multi-level caching, file indexing, frecency algorithms, predictive pre-warming |
| **Performance Targets** | 10-100x speedup for indexed queries, `&lt;1ms` cache hit latency |
| **BACKLOG Items** | 5 items extracted (see Next Actions) |
| ID | Action | Priority | Depends | Status |
|----|--------|----------|---------|--------|
| `cache-multi-level` | Implement multi-level caching (memory → disk → network) | P1 | - | BACKLOG |
| `cache-diskcache-migration` | Migrate to diskcache for disk-backed cache | P1 | cache-multi-level | ⏳ Claimed (agent-koosha) | BACKLOG |
| `index-file-indexing` | Add file indexing (fd-style) for common find patterns | P1 | - | BACKLOG |
| `cache-frecency-algorithm` | Implement frecency algorithm for directory/command history | P2 | cache-multi-level | ⏳ Claimed (agent-koosha) | BACKLOG |
| `cache-predictive-pre-warming` | Add predictive pre-warming based on usage patterns | P2 | cache-multi-level | ⏳ Claimed (agent-koosha) | BACKLOG |
| § | Section | Content |
|---|---------|---------|
| 1 | Executive Summary | Key findings, recommendations |
| 2 | Caching Strategies | Multi-level caching, eviction policies, TTL strategies |
| 3 | Indexing Strategies | File indexing, metadata caching, search optimization |
| 4 | Pre-warming Patterns | Cold start mitigation, predictive warming |
| 5 | Library Landscape | Python, Rust, Go, C libraries |
| 6 | Production Case Studies | Real-world implementations and benchmarks |
| 7 | Performance Optimization | Zero-copy, memory-mapped files, async I/O |
| 8 | Advanced Techniques | Frecency algorithms, aging, probabilistic data structures |
| 9 | Reflection & Analysis | Critical analysis, trade-offs, recommendations |
| 10 | Implementation Roadmap | Phased plan for thegent integration |
| Policy | Use Case | Pros | Cons | Implementation |
|--------|----------|------|------|----------------|
| **LRU (Least Recently Used)** | General caching | Simple, effective | Doesn't account for frequency | `cachetools.LRUCache` |
| **LFU (Least Frequently Used)** | Long-term caching | Rewards frequent access | Can evict recently accessed | `diskcache` supports LFU |
| **FIFO (First In First Out)** | Simple queues | Trivial implementation | Poor hit rate | Basic queue |
| **TTL (Time To Live)** | Time-sensitive data | Automatic expiration | Doesn't consider access patterns | `cachetools.TTLCache` |
| **Frecency** | Navigation, history | Best UX (zoxide proven) | More complex | Custom implementation |
| **Size-based** | Memory-constrained | Predictable memory usage | May evict hot data | `cachetools` maxsize |
| Strategy | When to Use | Implementation |
|----------|-------------|----------------|
| **TTL-based** | Time-sensitive data | Automatic expiration |
| **Version-based** | Tool/format changes | Include version in cache key |
| **Content-based (ETag)** | HTTP resources | Hash of content |
| **Event-based** | File system changes | File watcher triggers invalidation |
| **Manual** | User-triggered | `thegent cache clear` command |
| Strategy | TTL | When to Rebuild | Use Case |
|----------|-----|-----------------|----------|
| **Time-based** | 5 minutes | Every 5 minutes | General file search |
| **Event-based** | Until change | On file system events | Real-time search |
| **Lazy** | Until query | On cache miss | Low-traffic scenarios |
| **Hybrid** | 5 min + events | Time OR events | Best of both |
| Target | Current | Recommended | ROI |
|--------|---------|-------------|-----|
| **Git status** | ✓ | ✓ | High (eliminates spawn) |
| **File index** | ✓ | ✓ | High (enables fast find) |
| **Common greps** | ✓ | ⚠️ | Medium (depends on patterns) |
| **Model catalog** | ✓ (MCP) | ✓ | High (first request latency) |
| **Git index** | ✓ (terminal.py) | ✓ | High (git command speedup) |
| **Directory frecency** | ❌ | ✅ | High (navigation UX) |
| **Command history** | ❌ | ✅ | Medium (completion speed) |
| Event | Pre-warm Actions | Current | Recommended |
|-------|-----------------|---------|-------------|
| **SessionStart** | Git status, file index, catalog | Partial | Full |
| **UserPromptSubmit** | Predictive (next likely commands) | ❌ | ✅ |
| **PostToolUse** | Related commands (git status → git diff) | ❌ | ✅ |
| **Stop** | Next session prep | ❌ | ✅ |
| **File Change** | Invalidate + rebuild index | Partial | Full |
| Library | Purpose | Performance | Use Case |
|---------|---------|-------------|----------|
| **cachetools** | In-memory caching | Fast (~10ns) | Hot paths, TTL cache |
| **diskcache** | Disk-backed cache | Fast (~100µs) | Large cache, persistence |
| **diskcache.FanoutCache** | Sharded disk cache | Very fast | High-throughput |
| **watchdog** | File system events | Event-driven | Index invalidation |
| **sqlitedict** | SQLite-backed dict | Medium (~500µs) | Structured data |
| Library | Purpose | Performance | Use Case |
|---------|---------|-------------|----------|
| **mio** | Low-level I/O events | Zero-cost | Event-driven I/O |
| **tokio** | Async runtime | Zero-cost abstractions | Concurrent operations |
| **bytes** | Zero-copy buffers | Zero-copy | Large data handling |
| **serde** | Serialization | Fast | Cache serialization |
| **quick-xml** | XML parsing | 5-8x faster than Python | XML parsing (BKM-02) |
| **simd-json** | JSON parsing | 2-3x faster than serde_json | JSONL streaming (BKM-10) |
| **notify** | File system events | Cross-platform | Index invalidation |
| **memmap2** | Memory-mapped files | Zero-copy | Large index files |
| Library | Purpose | Performance | Use Case |
|---------|---------|-------------|----------|
| **groupcache** | Distributed cache | Fast | Multi-process caching |
| **bigcache** | In-memory cache | Fast | High-throughput |
| **go-cache** | TTL cache | Fast | Simple caching |
| Library | Purpose | Performance | Use Case |
|---------|---------|-------------|----------|
| **LMDB** | Memory-mapped DB | Very fast | Large index files |
| **RocksDB** | Embedded KV store | Very fast | High-throughput caching |
| **LevelDB** | Embedded KV store | Fast | Simple key-value cache |
| Decision | Pros | Cons | Verdict |
|----------|------|------|---------|
| **File-based vs SQLite cache** | Simple, no deps | Slower queries, no structure | Migrate to SQLite (diskcache) |
| **Time-based vs Event-based index** | Simple, predictable | Stale data, wasted rebuilds | Hybrid (time + events) |
| **Explicit vs Predictive pre-warm** | Simple, no waste | Manual, easy to forget | Both (explicit + predictive) |
| **Memory vs Disk cache** | Fast, simple | Limited size, lost on restart | Multi-level (memory + disk) |
| **Go vs Rust for caching** | Simple, fast enough | Less performant than Rust | Keep Go for now, consider Rust later |
| Metric | Target | Current | Measurement |
|--------|--------|---------|-------------|
| **Cache hit rate** | >80% | Unknown | Track hits/misses |
| **Index freshness** | `&lt;5min` | 5min | Time since rebuild |
| **Pre-warm effectiveness** | `&lt;100ms` cold start | Unknown | Measure cold vs warm |
| **Memory usage** | `&lt;100MB` | Unknown | Monitor cache size |
| **Disk usage** | `&lt;1GB` | Unknown | Monitor cache directory |
| Failure Mode | Impact | Mitigation |
|--------------|--------|------------|
| **Cache corruption** | Invalid data returned | Checksum validation, cache invalidation, fallback to compute |
| **Disk cache full** | Writes fail | LRU eviction, size limits, fallback to memory-only |
| **Index stale** | Wrong results | TTL-based refresh, event-based invalidation, manual refresh |
| **Pre-warming overhead** | Slower startup | Lazy pre-warming, background warming, configurable |
| **Memory pressure** | OOM errors | Size limits, eviction policies, monitoring |
| **Network cache unavailable** | Shared cache lost | Fallback to local cache, graceful degradation |
| Criteria | Redis | diskcache/FileCache | Verdict |
|---------|-------|-------------------|---------|
| **Latency** | ~1-5ms network | ~100µs-1ms disk | FileCache for local |
| **Persistence** | Configurable AOF/RDB | SQLite-based | Both good |
| **Setup** | Server required | Zero-setup | FileCache simpler |
| **Memory Overhead** | Full Redis process | Minimal | FileCache lighter |
| **Clustering** | Native | Requires external | Redis for distributed |
| **TTL Support** | Native | Native | Tie |
| **Query Capabilities** | Basic key-value | SQL queries | FileCache wins |
| **Use Case** | Distributed cache | Local cache | Both have place |
| Scenario | Recommended Backend | Rationale |
|----------|-------------------|-----------|
| Single-machine, simple caching | `diskcache` | Zero-setup, SQLite-backed |
| Multi-process, local | `cachetools` + `diskcache` | Memory + disk layers |
| Distributed, shared cache | Redis | Native clustering |
| Hot paths, micro-latency | `cachetools` | In-memory |
| Large values (>1MB) | `diskcache` | SQLite storage |
| Complex queries | `diskcache` | SQL support |
| Fallback chain | Memory → Disk → Redis | Progressive |
| Example | Purpose |
|---------|---------|
| Multi-Level Cache Architecture | Layered caching (memory → disk → network) |
| Cache Key Strategies | Version-aware cache keys with environment hashing |
| Cache Invalidation | TTL-based, version-based, event-based invalidation |
| Index Freshness Strategies | Time-based, event-based, lazy, hybrid invalidation |
| Frecency Algorithm | zoxide-style frequency × recency scoring |
| Cache Stampede Prevention | memoize_stampede pattern |
| Layer | Name | Frequency | Responsibility |
|-------|------|-----------|----------------|
| **Slow loop** | Monthly / Budget Allocator | Hourly/Daily | Decides enabled subscriptions/plans/providers/models; sets quotas + internal shadow prices |
| **Fast loop** | Per-Call Router | Per request | Chooses best offer from enabled pool using hard constraints first, then Pareto / lexicographic optimization |
| Category | Fields |
|----------|--------|
| **Identity** | offerId (unique), provider, modelName |
| **Capabilities** | contextWindow, tool support (function calling, JSON mode, vision), max output tokens |
| **Pricing** | in/out, cache read/write, batch discounts |
| **Limits** | RPM, TPM, concurrency |
| **Reliability** | timeouts, error rate |
| Two-Stage | Offer-First |
|-----------|-------------|
| Select "claude-opus" without considering provider rate limits | Economics and limits baked in from start |
| Ignores subscription quotas | Correct handling of quotas/outages |
| Ignores region latency | Consistent scoring |
| Must do offer-routing anyway as second step | Single routing decision |
| Component | Responsibility |
|-----------|----------------|
| Catalog service | Offers + capabilities + base pricing |
| Plan service | Scrapes usage, applies plan math, publishes effectiveUnitCost + quota + shadowPrice |
| Metrics service | Latency/error stats by offer, updates predictors |
| Quality index service | Benchmark table + online eval, publishes quality_pred per role |
| Router API (hot path) | chooseOffer(request, role, constraints) → offerId |
| Execution layer | Retries/fallbacks + circuit breaker |
| Metric | Description |
|--------|-------------|
| latency_p50, latency_p95 | Request latency |
| ttft_p50 | Time to first token |
| tokens_per_second | Output throughput |
| error_rate | Failure rate |
| Plan Type | Description | EUC Calculation |
|-----------|-------------|-----------------|
| **payg_token** | OpenRouter payg, direct APIs | EUC_in = price_in_per_token, EUC_out = price_out_per_token |
| **fixed_bucket_tokens** | Claude Max, Codex "~11B tokens", GLM "3× usage" | EUC_blended = monthly_fee / expected_tokens_covered |
| **premium_request_bucket** | Copilot Pro/Pro+/Free (premium request caps) | Convert requests→tokens via observed avg; EUC = fee / (requests × avg_tokens) |
| **prompt_rate_limited** | Minimax "300 prompts / 5 hours" | prompts_month × avg_tokens; EUC = fee / expected_tokens |
| **volatile_free** | Promo/preview models | EUC = very_small_floor + high volatility penalty |
| **daily_quota_bucket** | Cerebras Code (tokens/day) | day_shadow = 1 / max(remaining_today / expected_remaining_today, ε) |
| **weighted_unit_bucket** | Copilot (multipliers + 0× models) | units consumed = multiplier; implied_cost = 0.04 * m |
| **compute_metered** | NIM self-host | $/token = ($/hour) / (measured_tokens_per_hour) |
| Role | Allocation |
|------|-------------|
| code_complex | 40% |
| doc_writer | 20% |
| fast_chat | 15% |
| agent_workflow | 25% |
| Endpoint | Purpose |
| `POST /v1/admin/providers/:providerId/enable` | Enable provider offers (optionally scoped by roles) |
| `POST /v1/admin/offers/:offerId/state` | Set active \| inactive \| canary \| blocked |
| `POST /v1/admin/policies` | Update role policies (constraints + opt order) |
| `GET /v1/admin/health` | Shows provider health, error rates, disabled offers, budget burn |
|                 |                |
|              |             |
| Snapshot | Contents |
|----------|----------|
| OfferSnapshot | Capabilities + base pricing |
| TelemetrySnapshot | Latency/errors/adherence |
| EconomicsSnapshot | Effective cost + shadow price + budget state |
| QualitySnapshot | Per-role quality indices |
| Failure Type | Fallback Action |
|--------------|-----------------|
| Rate limit / 429 | Switch provider/offer immediately |
| Timeout | Switch to fastest offer on Pareto set |
| Schema/tool failure | Switch to "high adherence" offer |
| Bad output quality (tests) | Escalate to higher quality tier |
- [ ] Canonical Offer schema + snapshots
- [ ] Adapter interfaces + initial adapters (OpenRouter, Vercel, self-host)
- [ ] Telemetry event schema + aggregator
- [ ] Subscription plan schema + shadow pricing engine
- [ ] Router service (hard filters + pareto + lexi + fallback)
- [ ] Admin policy editor (roles + budgets)
- [ ] Dashboards: spend, latency, routing decisions, failovers
| Plan | Monthly | Notes |
|------|---------|-------|
| Claude Max | $200 | ~3B tok/mo (dynamic, across 3 models, includes cached) |
| Codex | $200 | ~11B tok/mo |
| Cursor | $200 | ~$600 usage equivalent |
| Minimax | $40 | 300 prompts / 5 hours |
| Copilot Student Pro | Free | Unlimited completions; 300 premium requests/mo (Pro) |
| GLM Max | $80 | 3× usage vs Claude (on paper) |
| Gemini/Antigravity | $20 | Free plans via Google AI Premium |
| Promo (Kilo, Roo, Opencode, Kimi, Qwen) | Varies | Rotating free/cheap models |
| Tier | Premium Requests | Overage | Notes |
|------|------------------|---------|-------|
| **Free** | 50 premium/mo | — | 2,000 inline suggestions |
| **Pro** (Student) | 300 premium/mo | $0.04/request | Unlimited completions |
| **Pro+** | 1,500 premium/mo | $0.04/request | Full model access |
| Model | Multiplier |
|-------|------------|
| Claude Sonnet 4.6 | 1.0× |
| Claude Opus 4.6 | 2.0× |
| Claude Haiku 4.5 | 0.33× |
| Gemini 3 Pro | 0.1× |
| Gemini 3 Flash | 0.1× |
| GPT-4.1 | 0× |
| GPT-5 mini | 0× |
| User Plan | Schema Type |
|-----------|-------------|
| Claude Max $200 | fixed_bucket_tokens, prior 3B tok/mo |
| Codex $200 | fixed_bucket_tokens, prior 11B tok/mo |
| Cursor $200 | subsidized_payg (3× value prior) + learn from logs |
| Minimax $40 | prompt_rate_limited |
| Copilot student | weighted_unit_bucket, 300 units, 0× for GPT-4.1/GPT-5 mini |
| GLM Max $80 | fixed_bucket or prompt-limited; learn EUC from logs |
| Gemini premium $20 | fixed_bucket / unlimited depending on limits |
| Promo harnesses | volatile_free, high volatility penalty |
| Metric | Description |
|--------|-------------|
| **TTFT** | Time to first token |
| **ITL** | Inter-token latency (TPOT) |
| **Output tokens/sec** | Streaming speed after first token |
| **Aggregate throughput** | Tokens/sec across many concurrent requests |
| Tier | Tokens/Day | TPM | RPM |
|------|------------|-----|-----|
| Code Pro ($50/mo) | 24M | 1,000,000 | 50 |
| Code Max ($200/mo) | 120M | 1,500,000 | 120 |
| Role | Purpose |
|------|---------|
| code_reasoner | Deep planning, debugging, architecture |
| code_patch_generator | Outputs minimal edit snippet / patch instructions |
| code_apply_patch | Morph/Relace-style file merge/apply |
| code_scaffold_fast | High-throughput code drafting (Cerebras) |
| code_small_transform | Small edits, formatting, rename, docstring |
| ADR | Decision |
|-----|----------|
| ADR-008 | Replace single "tokens/sec" with TTFT + ITL + throughput profile |
| ADR-009 | Add Patch/Apply stage as first-class routing role |
| ADR-010 | Model Cerebras Code as daily-quota bucket plan |
| ADR-011 | Treat NVIDIA build.nvidia.com as volatile_free with limits-discovery |
| ADR-012 | Store vendor speed claims as priors; routing uses measured telemetry |
| Provider | Sources |
| Cerebras | inference-docs.cerebras.ai, Support FAQ, Pricing page, Blogs |
| NVIDIA NIM | NIM microservices page, build.nvidia.com model cards, NIM docs, Forums |
| Morph/Relace | OpenRouter model pages, Morph AWS case study, Relace engineering blog |
| ID | Requirement |
|----|-------------|
| FR-1 | Offer-first catalog (provider+model+plan+region) |
| FR-2 | Plan/economics engine: all plan types |
| FR-3 | Speed index uses TTFT+ITL |
| FR-4 | Quality index stable under missing benchmarks |
| FR-5 | Patch-based coding DAG |
| FR-6 | Fallback + circuit breakers |
| ID | Decision | Status |
|----|----------|--------|
| ADR-001 | Offer-first routing (provider+model+plan) | Accepted |
| ADR-002 | Pareto frontier + lexicographic tie-break | Accepted |
| ADR-003 | Copilot = weighted unit bucket + 0× included models | Accepted |
| ADR-004 | Speed profile uses TTFT+ITL (not "tok/s") | Accepted |
| ADR-005 | Cerebras Code modeled as daily_quota_bucket | Accepted |
| ADR-006 | NVIDIA build.nvidia.com classified as volatile_free | Accepted |
| ADR-007 | Apply/Patch models are separate role + DAG stage | Accepted |
| ADR-008 | Vendor speed claims are priors; measured telemetry wins | Accepted |
| Model | Provider | Benchmarks | Strengths |
|-------|----------|------------|-----------|
| GPT-5.2 Codex | OpenAI | 89% LiveCodeBench; tops HumanEval/MBPP | Precise code generation, complex architecture planning |
| Claude Opus 4.6 | Anthropic | ~81% SWE-Bench; 87% LiveCodeBench | Deep reasoning, safe refactoring, multi-file context |
| Gemini 3 Pro | Google | 92% LiveCodeBench; >3400 Codeforces Elo | UI-centric coding, dominant on algorithmic challenges |
| MiniMax M2.5 | MiniMax | 80.2% SWE-Bench (≈Claude/GPT-5 parity) | Frontier code quality at low cost |
| Kimi K2.5 | Moonshot | ~85% LiveCode (est.) | Multimodal, agentic tool use, 262K context |
| Model | Provider | Benchmarks | Strengths |
|-------|----------|------------|-----------|
| Claude Haiku 4.5 | Anthropic | 73.3% SWE-Bench; ~90% of Claude agentic | Fast (2–5× faster), low cost for iterative use |
| Gemini 3 Flash | Google | ~91% LiveCodeBench | High-speed Q&A, code completions |
| Claude Sonnet 4.5 | Anthropic | Solid across board | Balanced "daily driver" |
| Model | Provider | Benchmarks | Strengths |
|-------|----------|------------|-----------|
| GLM-5 (Reasoning) | Zhipu AI | ~89% LiveCodeBench | Open-source, near-SOTA |
| DeepSeek V3.2 | DeepSeek | ~85–90% coding evals | 90%+ quality at 1/10th cost |
| Code LLaMA 34B | Meta | ~50% HumanEval | Self-hostable on 48GB GPUs |
| Qwen-14B Coder | Alibaba | ~48% HumanEval (base) | Lightweight, single GPU |
| Model | Max Context | Input/M | Output/M | Access |
|-------|-------------|---------|---------|--------|
| Claude Haiku 4.5 | 100K | $1.00 | $5.00 | Anthropic API, Bedrock, Claude.ai |
| Claude Opus 4.6 | 1M | $5.00 | $25.00 | API, OpenRouter |
| Claude Sonnet 4.5 | 1M | $3.00 | $15.00 | API, OpenRouter |
| GPT-5.2 Codex | 128K | $1.75 | $14.00 | OpenAI API, Azure |
| GPT-5.2 "Pro" | 256K | $21.00 | $168.00 | Limited beta |
| Gemini 3 Flash | 1.05M | $0.50 | $3.00 | Vertex AI, OpenRouter |
| Gemini 3 Pro | 1M+ | $2.00 | $12.00 | Early Access |
| MiniMax M2.5 | 197K | $0.30 | $1.10 | OpenRouter, MiniMax API |
| Moonshot Kimi K2.5 | 262K | $0.23 | $3.00 | OpenRouter, Moonshot AI |
| xAI Grok Code 1 | 256K | $0.20 | $1.50 | xAI API, OpenRouter |
| Trinity-XL (Arcee) | 131K | $0.00 | $0.00 | OpenRouter free tier |
| Platform | Models | Markup | Notes |
|----------|--------|--------|-------|
| OpenRouter | 300+ | ~5.5% platform fee | Models API, key status; BYOK |
| Vercel AI Gateway | Popular APIs | Zero markup | ~$5 credit/mo; includes cloud function time |
| build.nvidia.com | NIM models | Free (dev) | Limits vary, not published |
| # | Document | Scope |
|---|----------|-------|
| 1 | [CHATGPT_PARETO_DEEP_01_FOUNDATIONS.md](./CHATGPT_PARETO_DEEP_01_FOUNDATIONS.md) | Core Pareto design, Offer abstraction, PRD/ALD foundations, design philosophy |
| 2 | [CHATGPT_PARETO_DEEP_02_INDICES_ECONOMICS.md](./CHATGPT_PARETO_DEEP_02_INDICES_ECONOMICS.md) | Speed/Cost/Quality index formulas, shadow pricing, budget engine, plan types |
| 3 | [CHATGPT_PARETO_DEEP_03_API_PIPELINES.md](./CHATGPT_PARETO_DEEP_03_API_PIPELINES.md) | User journeys, API processes, data pipelines, execution flow |
| 4 | [CHATGPT_PARETO_DEEP_04_PROJECT_CATALOG.md](./CHATGPT_PARETO_DEEP_04_PROJECT_CATALOG.md) | Project-specific subscriptions, Copilot schema, catalog examples, worked routing |
| 5 | [CHATGPT_PARETO_DEEP_05_SPEED_STACK.md](./CHATGPT_PARETO_DEEP_05_SPEED_STACK.md) | Cerebras, NVIDIA NIM, Step 3.5 Flash, Morph, Relace — sourced research |
| 6 | [CHATGPT_PARETO_DEEP_06_HELIOS_UNIFIED_SPEC.md](./CHATGPT_PARETO_DEEP_06_HELIOS_UNIFIED_SPEC.md) | Full Helios Router v1.1: PRD + WBS + ALD + ADR |
| 7 | [CHATGPT_PARETO_DEEP_07_FEB2026_SOTA.md](./CHATGPT_PARETO_DEEP_07_FEB2026_SOTA.md) | Feb 2026 SOTA: models, pricing, meta-routers, cost-efficiency strategies |
| Failure Type | Fallback Action |
|--------------|-----------------|
| Rate limit / 429 | Switch provider/offer immediately |
| Timeout | Switch to fastest offer on Pareto set |
| Schema/tool failure | Switch to highest adherence offer |
| Bad output quality | Escalate to higher quality tier |
| Two-Stage (model → provider) | Offer-First |
|------------------------------|-------------|
| Select "claude-opus" without considering provider rate limits | Economics and limits baked in from start |
| Ignores subscription quotas | Correct handling of quotas/outages |
| Ignores region latency | Consistent scoring |
| Must do offer-routing anyway as second step | Single routing decision |
| Plan Type | EUC Calculation |
|-----------|-----------------|
| **payg_token** | EUC_in = price_in_per_token, EUC_out = price_out_per_token |
| **fixed_bucket_tokens** | EUC_blended = monthly_fee / expected_tokens_covered |
| **premium_request_bucket** | Convert requests→tokens via observed avg; EUC = fee / (requests × avg_tokens) |
| **prompt_rate_limited** | Minimax: 300 prompts/5h → prompts_month × avg_tokens; EUC = fee / expected_tokens |
| **volatile_free** | EUC = very_small_floor + high volatility penalty |
| Role | Allocation |
|------|-------------|
| code_complex | 40% |
| doc_writer | 20% |
| fast_chat | 15% |
| agent_workflow | 25% |
| Plan | Monthly | Notes |
|------|---------|-------|
| Claude Max | $200 | ~3B tok/mo (dynamic, across 3 models, includes cached) |
| Codex | $200 | ~11B tok/mo |
| Cursor | $200 | ~$600 usage equivalent |
| Minimax | $40 | 300 prompts / 5 hours |
| Copilot Student Pro | Free | Unlimited completions; 300 premium requests/mo (Pro) |
| GLM Max | $80 | 3× usage vs Claude (on paper) |
| Gemini/Antigravity | $20 | Free plans via Google AI Premium |
| Promo (Kilo, Roo, Opencode, Kimi, Qwen) | Varies | Rotating free/cheap models |
|                 |                |
|              |             |
| Helios / Pareto Concept | LiteLLM Equivalent | Project Component |
|-------------------------|-------------------|-------------------|
| Offer | Deployment (model + provider + config) | `harness_model_mapping`, `model_indices.json` |
| Offer Registry | Router model_list | `litellm_router.py`, `catalog.py` |
| Commercial Engine | Cost tracking, budget | `cost_tracker.py`, custom |
| Shadow Pricing | Not built-in | **Extend** cost_tracker |
| Pareto Selection | simple-shuffle, cost-based-routing | **Extend** routing strategies |
| Responses API | Chat Completions | `cliproxy_adapter.py`, Responses→Chat translation |
| Data Plane | LiteLLM Proxy | `litellm_router.py` |
| Control Plane | Config + custom services | Offer Registry, Economics, Quality |
| Gap | Solution |
|-----|----------|
| Shadow pricing | Custom callback / middleware in LiteLLM; or pre-filter deployments by effective cost |
| Pareto frontier | Custom routing strategy plugin; or pre-compute ranked list, pass to LiteLLM as fallback chain |
| Offer abstraction | Map offers → LiteLLM deployments; one deployment per offer |
| Quality index | Pre-filter by min quality; or weight deployments by quality in custom strategy |
| Budget engine | Integrate with cost_tracker; enforce caps before routing |
| Platform | Best For | Pricing (2025) | Key Strength |
|----------|----------|----------------|--------------|
| **GitHub Actions** | Open-source, Microsoft ecosystem | Free (2K min/mo); $0.008/min after | Native GitHub integration, marketplace |
| **GitLab CI/CD** | Full DevOps platform | Free (CI limited); $19+/user/mo | Integrated planning, source, CI/CD |
| **CircleCI** | Enterprise, scalability | Free tier; paid from $15/mo | Autonomous validation, AI features |
| **Jenkins** | Self-hosted, legacy systems | Free (open-source) | Full control, extensive plugins |
| **AWS CodeBuild** | AWS ecosystem | Pay-per-use ($0.005/min Linux) | Native AWS integration |
| **Azure Pipelines** | Microsoft enterprise | Free (1.8K min/mo); $40/vCPU-hr | Cross-platform, Azure integration |
| Factor | Cloud Runners | Self-Hosted Runners |
|--------|--------------|---------------------|
| **Setup Time** | Instant | 1-2 hours |
| **Cost** | Pay-per-minute | Fixed infrastructure |
| **Security** | Vendor-managed | Full data control |
| **Customization** | Limited | Full OS/package control |
| **Scalability** | Auto-scale | Manual/provisioned |
| **Maintenance** | Zero | Team responsibility |
| Tool | Purpose | Best For |
|------|---------|----------|
| **Backstage** | Internal developer portal | Enterprise, service catalog |
| **Port** | Developer portal | Self-service, IaC |
| **Roadie** | Backstage as a service | Quick Backstage setup |
| **Doppler** | Secrets management | Env var management |
| **ApiTree** | API documentation | API-first teams |
| Metric | Description | Target |
|--------|-------------|-------|
| **Build Duration** | Time from trigger to completion | `&lt; 10 min` |
| **Flaky Test Rate** | % of tests with non-deterministic results | `&lt; 2%` |
| **MTTR** | Mean time to recover from failures | `&lt; 30 min` |
| **PR Cycle Time** | Time from PR open to merge | `&lt; 24` hours |
| **Code Review Time** | Time to first review | `&lt; 4` hours |
| **Pass Rate** | % of builds passing | > 90% |
| Category | Tool | Purpose |
|----------|------|---------|
| CI/CD | GitHub Actions | Primary CI/CD platform |
| Pre-commit | pre-commit | Local quality enforcement |
| Linting | ruff (Python), eslint (JS/TS) | Code quality |
| Formatting | ruff-format, prettier | Code formatting |
| Coverage | codecov | Coverage reporting |
| Secrets | gitleaks | Secrets detection |
| SAST | CodeQL | Static analysis |
| Category | Tool | Cost | Purpose |
|----------|------|------|---------|
| Dependency Updates | Renovate | Free/Paid | Automated PRs |
| Preview Deploys | Vercel | Free tier | PR previews |
| Security | Snyk | Free/Paid | Vulnerability scanning |
| Notifications | Slack/Discord | Free | Team alerts |
| Category | Tool | Purpose |
|----------|------|---------|
| Developer Portal | Backstage | Service catalog |
| Release Orchestration | Octopus Deploy | Complex deployments |
| Enterprise CI | GitLab Ultimate | Full DevOps platform |
| Monitoring | Datadog/New Relic | Full-stack observability |
- [ ] Use `actions/checkout@v4` (latest major version)
- [ ] Always specify version tags, not `@master` or `@main`
- [ ] Use caching for npm, pip, and build outputs
- [ ] Implement matrix builds for multi-version testing
- [ ] Use reusable workflows for common patterns
- [ ] Set appropriate concurrency groups to cancel outdated runs
- [ ] Add timeout-minutes to prevent stuck jobs
- [ ] Use conditional steps with `if:` to skip unnecessary work
- [ ] Upload build artifacts for debugging failed builds
- [ ] Use environment protections for production deployments
| Tool | Type | Languages | Free | Integration |
|------|------|-----------|------|-------------|
| **CodeQL** | SAST | 20+ | OSS/Research | GitHub |
| **Snyk** | DAST/Dependency | 20+ | Limited | GitHub, GitLab |
| **SonarQube** | SAST | 20+ | Community | GitHub, GitLab |
| **Semgrep** | SAST | 20+ | Yes | GitHub, GitLab |
| **bandit** | SAST | Python | Yes | GitHub Actions |
| **trufflehog** | Secrets | All | Yes | GitHub Actions |
| **gitleaks** | Secrets | All | Yes | GitHub Actions |
| Topic | Reference |
| CLI Patterns | `API_CLI_DEVOPS_TOOLING.md` |
| TUI/Queue Design | `USER_QUEUE_TUI_AND_AGENT_POLL.md` |
| Hybrid Environment | `../architecture/HYBRID_MAC_WIN_DEV_ENVIRONMENT.md` |
| Implementation Plan | `../plans/HYBRID_ENV_IMPLEMENTATION_PLAN.md` |
| Section | Description |
|---------|-------------|
| **7. Pipeline Examples** | Added complete quality gate, remote execution, matrix build, and scheduled maintenance pipelines |
| **8. Cross-References** | Added links to related documentation |
| **9. Extension Summary** | This summary section |
| Example | Purpose |
|---------|---------|
| 7.1 Quality Gate | Multi-phase CI/CD with static analysis, tests, security, and build |
| 7.2 Remote Execution | SSH-based remote command execution |
| 7.3 Matrix Build | Multi-platform, multi-version testing |
| 7.4 Maintenance | Scheduled cleanup and health checks |
| Pipeline | Integrates With |
|----------|-----------------|
| Quality Gate | Ruff, pytest, CodeQL, gitleaks, codecov |
| Remote Execution | SSH, rsync, GitHub Actions |
| Matrix Build | uv, pytest, codecov |
| Maintenance | pip-tools, Slack |
| Hook | When | Blocking? | Claude Code | Codex | thegent Strategy |
|------|------|-----------|-------------|-------|------------------|
| **SessionStart** | New session / resume | No | ✓ Native | ✗ None | Wrapper: inject handoff before spawn |
| **UserPromptSubmit** | Before prompt sent | Yes | ✓ Native | ✗ None | Exec: run_impl preprocessor; Interactive: SDK or custom TUI |
| **PreToolUse** | Before tool call | Yes | ✓ Native | ✗ None | Wrapper/SDK only; exec has no tool loop |
| **PermissionRequest** | Permission dialog | Yes | ✓ Native | ✗ None | Codex has different permission model |
| **PostToolUse** | After tool call | No | ✓ Native | AfterToolUse (not configurable) | codex-notify if AfterToolUse enabled |
| **PostToolUseFailure** | After tool fails | No | ✓ Native | ✗ None | — |
| **Notification** | Various | No | ✓ Native | ✗ None | — |
| **SubagentStart** | Subagent spawned | No | ✓ Native | ✗ No subagents | thegent: spawn codex exec as "subagent" |
| **SubagentStop** | Subagent done | Yes | ✓ Native | ✗ None | Wrapper: on codex exec exit |
| **Stop** | Session ends | Yes | ✓ Native | ✗ None | Wrapper exit hook |
| **TeammateIdle** | Teammate about idle | Yes | ✓ Native | ✗ No teammates | thegent team: wrapper monitors |
| **TaskCompleted** | Task marked done | Yes | ✓ Native | ✗ None | thegent task list: MCP tools |
| **PreCompact** | Before compaction | No | ✓ Native | ✗ None | — |
| **SessionEnd** | Session terminates | No | ✓ Native | ✗ None | Wrapper exit hook |
| Mode | Claude Code | Codex | Parity |
|------|-------------|-------|--------|
| **Interactive TUI** | `claude` | `codex` | Both have; Codex lacks hook interception |
| **Headless** | `claude -p "prompt"` (Agent SDK CLI) | `codex exec -` (stdin) | Both have; thegent run wraps both |
| **Continue** | `claude -p "..." --continue` | — | Codex exec is single-turn |
| **Resume** | `claude -p "..." --resume SESSION_ID` | — | Codex exec is stateless |
| **Structured output** | `--output-format json`, `--json-schema` | `--json` (exec) | Both support JSON |
| **Stream** | `--output-format stream-json` | — | Codex exec streams to stdout |
| **Allowed tools** | `--allowedTools "Bash,Read,Edit"` | Sandbox mode | Different models |
| Feature | Claude Code | Codex | thegent Strategy |
|---------|-------------|-------|------------------|
| **Subagents** | Task tool spawns helper; reports back | ✗ None | thegent_run/thegent_bg as "subagent" — Codex calls MCP |
| **Agent teams** | Lead + teammates; shared task list; inter-agent messaging | ✗ None | **thegent team** wrapper: spawn N codex execs, shared task list via MCP |
| **Teammate display** | In-process or split panes (tmux/iTerm2) | — | thegent: tmux splits or in-process list |
| **TeammateIdle** | Exit 2 → feedback, keep working | — | Wrapper: poll teammate stdout; inject prompt |
| **TaskCompleted** | Exit 2 → block completion, send feedback | — | thegent_queue + MCP: task lifecycle |
| **Delegate mode** | Lead coordination-only | — | thegent team lead: skills restrict to spawn/message |
| Feature | Claude Code | Codex | Parity |
|---------|-------------|-------|--------|
| **Skills** | `.claude/skills/`, slash commands | `.codex/skills/` | Both have |
| **CLAUDE.md** | Project context | — | Codex uses different project context |
| **Agents** | Custom agent types (subagents) | — | Codex skills can define personas |
| **Plugins** | Marketplaces, hooks, MCP | — | Codex: MCP only |
| **Memory** | user, project, local | — | Codex: session-scoped |
| Feature | Claude Code | Codex | Parity |
|---------|-------------|-------|--------|
| **MCP** | Full support | Full support | ✓ Both |
| **Tool matchers** | PreToolUse matcher: `Bash`, `Edit\|Write`, `mcp__.*` | — | N/A for Codex |
| **MCP tool hooks** | PreToolUse on `mcp__memory__.*` etc. | — | — |
| Feature | Claude Code | Codex | Parity |
|---------|-------------|-------|--------|
| **Permission modes** | default, plan, acceptEdits, dontAsk, bypass | Sandbox modes | Different |
| **Plan approval** | Teammates: require plan before impl | — | thegent: skill + MCP |
| **Sandbox** | Bash tool sandbox | codex exec sandbox | Both |
| Feature | Claude Code | Codex | Parity |
|---------|-------------|-------|--------|
| **Checkpointing** | Rewind, summarize | — | thegent: run registry |
| **Resume** | `--resume SESSION_ID` | — | Codex: new session each exec |
| **Handoff** | pending-handoff.md, next-session | — | Shared: .thegent/next-session-prompts.md |
| Category | Claude Code | Codex Native | Codex + thegent Harness |
|----------|-------------|--------------|-------------------------|
| **Hooks** | 15 events | 1 (AfterAgent) | SessionStart/Stop/UserPromptSubmit via wrapper; PreToolUse/PostToolUse need SDK |
| **Interactive** | Full | Full | Wrapper adds exit hook |
| **Headless** | `claude -p` | `codex exec -` | Both; thegent run unifies |
| **Subagents** | Native | — | Via thegent_run MCP (Codex calls it) |
| **Agent teams** | Native | — | **thegent team** wrapper: N codex execs + shared task list |
| **Queue** | UserPromptSubmit + Stop | — | run_impl preprocessor + wrapper exit |
| **Skills** | Yes | Yes | Both |
| **MCP** | Yes | Yes | Both |
| Surface | Claude Code | Codex | thegent |
|---------|-------------|-------|---------|
| **Interactive** | `claude` | `codex` | `thegent codex` (wrapper) or `thegent dex` |
| **Headless** | `claude -p "..."` | `codex exec -` | `thegent run -M codex "..."` |
| **Both** | Same binary, flags | Different: `codex` vs `codex exec` | `thegent run` unifies headless; `thegent codex` wraps interactive |
| Hook | Strategy |
|------|----------|
| **SessionStart** | Wrapper: before spawn, load handoff, inject as first prompt |
| **UserPromptSubmit** | Exec: run_impl preprocessor. Interactive: SDK or custom TUI |
| **PreToolUse** | SDK only (we own tool loop). Exec: N/A (single turn) |
| **PostToolUse** | codex-notify if AfterToolUse configurable; else — |
| **Stop** | Wrapper exit hook |
| **SubagentStart/Stop** | thegent_run as subagent; on thegent run exit = SubagentStop |
| **TeammateIdle** | Wrapper: poll teammate, run hook script |
| **TaskCompleted** | thegent_queue + MCP task lifecycle |
| **SessionEnd** | Wrapper exit hook (same as Stop) |
| Feature | Cursor | Description | thegent Parity |
|---------|--------|-------------|----------------|
| **Rules** | `.cursor/rules/*.mdc` | YAML frontmatter: description, globs, alwaysApply | Map to CLAUDE.md/.codex/skills; rule sync |
| **.cursorrules** | Project root | Legacy rules file | Merge into rules or CLAUDE.md |
| **AGENTS.md** | Project root | Agent instructions | Cross-reference |
| **Skills** | `.cursor/skills-cursor/*` | Slash commands, SKILL.md | Sync from unified rules |
| **Modes** | `/plan`, agent, background agent | Plan mode, interactive, background | thegent run: mode; bg for background |
| **Hooks** | Auto-format, gating, commit checkpoints | Similar to Claude Code | Harvest from Cursor transcripts |
| **Composer** | Multi-agent orchestration | Cursor's agent UI | thegent run via cursor-api |
| Feature | Factory Droid | Description | thegent Parity |
|---------|---------------|-------------|----------------|
| **Droids** | `.factory/droids/*.md` | Markdown + frontmatter (name, description, tools, model) | DroidRunner already exists |
| **droid exec** | `droid exec -f path.md` | Runs droid via CLI | thegent run -M droid:`&lt;name>` |
| **Tools** | tools: [Read, Grep, Glob, ...] | Per-droid tool access | Frontmatter parsed |
| **Model** | model: inherit | Inherit or override | DroidRunner supports |
| Droid | Equivalent Agent |
|-------|------------------|
| worker | thegent run codex/claude |
| orchestrator-core | Lead in agent team |
| openspec-orchestrator | Specialized workflow |
| Feature | Augment | Description | thegent Parity |
|---------|---------|-------------|----------------|
| **auggie CLI** | `auggie` | Terminal agent | thegent run -M augment |
| **Headless** | `auggie --print "task"` | Same as claude -p | thegent run -M augment "prompt" |
| **Context Engine** | Live codebase understanding | Architecture, deps, history | MCP: Context Engine MCP |
| **Context Engine MCP** | MCP server | Expose context to tools | thegent: add augment MCP to config |
| **Intent** | Orchestration workspace | Specs, worktrees, multi-agent | thegent team + Intent integration |
| **IDE agents** | VS Code, JetBrains | Native IDE integration | N/A (IDE-only) |
| **Code Review** | PR review agent | — | — |
| Platform | Interactive | Headless | Rules | Skills | Hooks | Teams | thegent Entry |
|----------|-------------|----------|-------|--------|-------|-------|---------------|
| **Claude Code** | claude | claude -p | CLAUDE.md | .claude/skills | 15 events | Native | thegent clode, run -M claude |
| **Codex** | codex | codex exec - | .codex/skills | .codex/skills | notify | thegent team | thegent codex, run -M codex |
| **Cursor** | Composer | cursor-agent CLI | .cursor/rules | .cursor/skills-cursor | — | — | run -M cursor-agent |
| **Factory droid** | — | droid exec | — | .factory/droids | — | droid as teammate | run -M droid:name |
| **Augment** | auggie | auggie --print | — | — | — | Intent | run -M augment |
| **OpenCode** | oc | oc | .codex/skills | Zen (optional) | — | — | run -M opencode |
| Flag | Action | Exit |
|------|--------|------|
| `$defer` | Strip, append to queue, return "Queued. N pending." | 0 |
| `$pending` | Same as $defer | 0 |
| `$block` | Escalation add, return block message | 1 |
| `$idea` | Save to idea-seeds (Claude) or harvest buffer (Codex) | 0 (continue) |
| Value | Tools |
|-------|-------|
| `all` | Read, Grep, Glob, Create, Edit, Execute, Todo, WebSearch, FetchUrl |
| `read-only` | Read, Grep, Glob |
| `write` | Create, Edit |
| `execute` | Execute |
| List | Explicit subset |
| Feature | Likely behavior |
|---------|-----------------|
| **Pending queue** | User adds messages (e.g. `$defer`, `$later`) that are not sent immediately. They are stored and either: (a) dumped to a handoff file for the next session, or (b) shown/processed when the session stops. |
| **Blocking** | User sends a message that requires human input before the agent continues. The agent pauses; user must acknowledge/resolve (e.g. approve, reject, add context) before work resumes. |
| Aspect | $idea | $defer / $pending |
|--------|-------|-------------------|
| **Immediate save** | UserPromptSubmit saves to `docs/research/idea-seeds/` | UserPromptSubmit appends to pending queue |
| **Harvest** | harvest-idea-seeds.sh scans Claude/Codex/Cursor history | Same script extended to scan for $defer/$pending |
| **Block prompt?** | No (advisory only) | Yes (exit 1) |
| **On Stop** | harvest-idea-seeds-stop.sh runs harvest | harvest-pending-queue.sh flushes queue to handoff |
| **Output** | Per-prompt seed file | Consolidated handoff file |
| Event | When | Blocking? | Use for queue |
|-------|------|-----------|---------------|
| **UserPromptSubmit** | Before prompt is sent to model | Yes (fail-fast) | Intercept prompts with `$defer` / `$block` |
| **Stop** | When user ends session | No (parallel) | Process pending queue, write handoff |
| **SessionStart** | When new session begins | No | Load pending queue from previous session |
| **SessionEnd** | When session ends (cleanup) | No | Alternative to Stop for queue flush |
| **PreToolUse** | Before each tool call | Yes | Could block tool use until resolution |
| **PostToolUse** | After each tool call | No | Advisory |
| Flag | Meaning |
|------|---------|
| `$defer` or `$pending` | Do not send now; add to pending queue. Process on Stop. |
| `$block` | Block until user resolves (see §4). |
|                       |                        |                        |
| "Add tests $defer"    |                        |                        |
|---------------------->|                        |                        |
|                       | UserPromptSubmit       |                        |
|                       |----------------------->|                        |
|                       |                        | detect $defer           |
|                       |                        | append entry            |
|                       |                        |------------------------>|
|                       |                        | exit 1                  |
|                       |`&lt;`-----------------------|                        |
|  "Queued. 3 pending." |                        |                        |
|`&lt;`----------------------|                        |                        |
|  (prompt NOT sent)    |                        |                        |
|                       | Stop hook              | harvest-pending-queue   |
|                       |----------------------->|                        |
|                       |                        | read queue             |
|                       |                        |`&lt;`------------------------|
|                       |                        | write handoff.md       |
|                       |                        | clear queue            |
|                       |`&lt;`-----------------------|                        |
|                        |                        |
| scan */*.jsonl         |                        |
|---------------------->|                        |
|                        |                        |
| for each line:         |                        |
|   if $defer in text    |                        |
|   resolve project path |                        |
|   append to handoff    |                        |
|----------------------------------------------->|
|                        |                        |
| Alternative | Pros | Cons |
|-------------|------|------|
| **MCP tool** (`thegent_queue_add`, `thegent_queue_list`) | Agent can queue via tool; no prompt interception | Requires agent to call tool; user must type differently |
| **Native Claude Code support** | Ideal UX if Claude adds it | Not available; out of our control |
| **Separate queue CLI only** | `thegent queue add "prompt"` — no hook | User must leave Claude Code to queue; friction |
| **Hook + handoff file (chosen)** | Works with current Claude Code; no API needed | Blocking is "reject + escalate", not true pause |
| Edge case | Handling |
|-----------|----------|
| **Concurrent sessions** (multiple Claude Code windows) | Project-scoped queue: `PROJECT_DIR/.claude/pending-queue.jsonl`. Each session writes to same file; append is atomic at line level. Stop hook runs per session; last one to stop flushes. Risk: duplicate handoff if two sessions stop close together. Mitigation: handoff file append with session_id; or lock file. |
| **Multi-project** | Queue keyed by `PROJECT_DIR` (git root). Handoff written to `$PROJECT_DIR/docs/research/pending-handoff.md`. |
| **Queue file missing/corrupt** | On read: if not exists, treat as empty. On write: mkdir -p parent; append. Corrupt line: skip, log to stderr. |
| **PROJECT_DIR unset** | Fallback: `~/.claude/pending-queue.jsonl` and `~/.claude/pending-handoff.md`. User can set PROJECT_DIR in env. |
| **Harvest script timeout** | Cursor harvest can take 1–2 min. Run in background on Stop? Or accept; user can `CURSOR_PROJECTS=` to skip. |
| **$defer and $block in same prompt** | Precedence: $block wins (blocking is stricter). Block prompt, add to escalation. |
| **Empty prompt with only $defer** | Reject; do not add empty string to queue. |
| Env / config | Default | Purpose |
|--------------|---------|---------|
| `PENDING_QUEUE_FILE` | `$PROJECT_DIR/.claude/pending-queue.jsonl` or `~/.claude/pending-queue.jsonl` | Queue storage |
| `PENDING_HANDOFF_FILE` | `$PROJECT_DIR/docs/research/pending-handoff.md` | Output on Stop |
| `PENDING_QUEUE_ENABLED` | `1` | Set to `0` to disable $defer/$pending handling |
| `BLOCK_ESCALATION_ENABLED` | `1` | Set to `0` to disable $block → escalation |
| `CURSOR_PROJECTS` | `~/.cursor/projects` | Cursor harvest root; `=` to skip |
| Workflow | Integration |
|----------|-------------|
| **Next thing to do** | `thegent_do_next` / `thegent plan do-next` should include items from pending-handoff.md and escalation queue. Add handoff path to "read from" list. |
| **Gardening** | `thegent govern escalate list --past-sla` already shows escalations. Pending handoff can be a "pre-escalation" — items not yet escalated but queued for next session. |
| **Skills** | Update agent-orchestra and sitback-agent: "Use $defer to queue for session stop; use $block to require approval before proceeding." |
| **Stop hook order** | harvest-idea-seeds-stop runs; harvest-pending-queue (new) runs. Order: harvest-idea-seeds (captures $idea from history), then harvest-pending-queue (flushes Claude Code queue + any Cursor $defer from harvest). |
| Task | Location | Effort |
|------|----------|--------|
| Add `$defer` / `$pending` detection in prompt-submit-guard | `hooks/prompt-submit-guard.sh` | Small |
| Add pending queue file: `~/.claude/pending-queue.jsonl` or `PROJECT_DIR/.claude/pending-queue.jsonl` | New | Small |
| On `$defer`: append to queue, exit 1, print friendly message | prompt-submit-guard | Small |
| Add Stop hook: `harvest-pending-queue.sh` | `hooks/` | Small |
| On Stop: read queue, write handoff to `docs/research/pending-handoff.md` or `.claude/next-session-prompts.md`, clear queue | harvest-pending-queue | Small |
| Add SessionStart hook: optionally inject "You have N pending prompts from last session" | Optional | Small |
| Task | Location | Effort |
|------|----------|--------|
| Extend harvest-idea-seeds.sh to filter for $defer/$pending in addition to $idea | `scripts/harvest-idea-seeds.sh` | Small |
| For $defer/$pending: append to pending-handoff or project pending queue | Same script | Small |
| Reuse cursor_project_path() and offset tracking | Same script | — |
| Task | Location | Effort |
|------|----------|--------|
| Add `$block` detection in prompt-submit-guard | prompt-submit-guard | Small |
| On `$block`: call `thegent govern escalate add` with prompt as reason, exit 1 | prompt-submit-guard or new hook | Medium |
| Ensure escalation queue is visible in "next thing to do" / handoff | Already exists | — |
| Add `thegent queue resolve` or use existing `thegent govern escalate resolve` | CLI | Small |
| Task | Location | Effort |
|------|----------|--------|
| SessionStart hook reads `next-session-prompts.md` | New hook | Small |
| Inject summary into session context (if Claude Code supports it) | Research needed | — |
| Task | Location | Effort |
|------|----------|--------|
| Update agent-orchestra, sitback-agent with $defer/$block usage | `skills/` | Small |
| Add thegent_do_next to read pending-handoff | MCP / cli_impl | Small |
| Document in IDEA_SEEDS_SESSION_STORAGE.md | docs/research | Small |
| Test type | Approach | Status |
|-----------|----------|--------|
| **Unit (prompt-submit-guard)** | Invoke hook with mock stdin containing `$defer`; assert exit 1, queue file appended | ✓ `tests/test_hooks_pending_queue.py` |
| **Unit (harvest-pending-queue)** | Create temp queue file; run hook; assert handoff written, queue cleared | ✓ `tests/test_hooks_pending_queue.py` |
| **Integration (harvest-idea-seeds)** | Add $defer line to temp Claude history; run harvest; assert pending-handoff updated | ✓ `tests/test_hooks_pending_queue.py` |
| **E2E** | Manual: type "test $defer" in Claude Code; verify queued; stop session; verify handoff | Manual |
| Gap | Mitigation |
|-----|-------------|
| Claude Code may not support SessionStart context injection | Handoff file is sufficient; user opens next session and says "process pending handoff" |
| Blocking is not true "pause until user responds" | Use escalation + manual resolve; document as "blocking = requires approval before proceeding" |
| Multiple projects sharing same queue | Use project-scoped queue: `PROJECT_DIR/.claude/pending-queue.jsonl` |
| Queue file grows unbounded | Stop hook clears after processing; add retention for archived handoffs |
| Feature | Approach |
|---------|----------|
| **Pending queue** | `$defer` / `$pending` → prompt-submit-guard blocks, appends to queue → Stop hook flushes to handoff file |
| **Blocking** | `$block` → prompt-submit-guard blocks, adds to escalation queue → user resolves via `thegent govern escalate resolve` |
| **Cursor pull** | harvest-idea-seeds.sh extended to filter $defer/$pending from Cursor transcripts; append to handoff |
| Mode | Purpose | Key Mechanism | CLI/MCP Surface |
|------|---------|---------------|------------------|
| **Plan Mode** | Read-only exploration → user-approved plan → implementation | `EnterPlanMode` → explore → write plan file → `ExitPlanMode` → user approves → implement | `--permission-mode plan`, `Shift+Tab` cycle |
| **Delegate Mode** | Lead coordinates only; no direct implementation | Restricts lead to team-management tools (spawn, message, task list) | `Shift+Tab` (when agent team active) |
| Mode | Stage | Purpose | Protocol-Driven |
|------|-------|---------|-----------------|
| **Discussion** | Elicitation | Clarify idea, scope, constraints before research | Yes — elicitation brief |
| **Research** | Pre-plan | Explore codebase/docs without changes | Yes — research report |
| **Validation** | Post-implement | Verify, review, quality gate | Yes — validation checklist |
| Tool | Role |
|------|------|
| **EnterPlanMode** | Transitions into plan mode. Use proactively for non-trivial implementation tasks. Requires user approval. |
| **ExitPlanMode** | Signals plan is complete and ready for user review. Reads plan from file (does NOT take plan as parameter). Triggers approval UI. |
| **AskUserQuestion** | Clarify requirements/approach BEFORE finalizing plan. Do NOT use to ask "Is my plan ready?" — that's ExitPlanMode's job. |
| Allowed | Blocked |
|---------|---------|
| Spawn teammates | Edit, Write, Bash (direct implementation) |
| Message teammates | |
| Manage task list | |
| Shut down teammates | |
| Clean up team | |
| | Subagents | Agent Teams |
|--|-----------|-------------|
| **Context** | Own context; results return to caller | Own context; fully independent |
| **Communication** | Report to main agent only | Teammates message each other directly |
| **Coordination** | Main agent manages all work | Shared task list, self-coordination |
| **Best for** | Focused tasks, result matters | Complex work, discussion, collaboration |
| **Token cost** | Lower | Higher (each teammate = separate instance) |
| Tool | Description | Implementation |
|------|-------------|----------------|
| `thegent plan start` | Start Claude Code in plan mode | `claude --permission-mode plan` (or equivalent for Codex) |
| `thegent plan analyze` | Headless plan-only analysis | `claude --permission-mode plan -p "..."` |
| `thegent plan approve` | Programmatic plan approval (if API supports) | TBD — may require MCP or hook |
| MCP `thegent_plan_status` | Return current plan file path, status | Read `.claude/` or session state |
| MCP `thegent_plan_save` | Save plan to `docs/plans/` after ExitPlanMode | PostToolUse on ExitPlanMode |
| Tool | Description | Implementation |
|------|-------------|----------------|
| `thegent team create --delegate` | Create team with lead in delegate mode | Spawn `claude` with team + delegate mode |
| MCP `thegent_team_assign` | Assign task to teammate | Already in parity audit |
| MCP `thegent_team_message` | Send message to teammate | Already in parity audit |
| MCP `thegent_team_task_done` | Mark task complete | Already in parity audit |
| Hook: `SubagentStart` / `SubagentStop` | Log, notify, or gate subagent lifecycle | thegent wrapper |
| MCP Tool | Purpose |
| `thegent_plan_create` | Create plan from prompt, return plan ID/path |
| `thegent_plan_get` | Get plan content by ID |
| `thegent_plan_approve` | Mark plan approved (for downstream automation) |
| `thegent_team_create` | Create agent team with optional delegate mode |
| `thegent_team_lead_mode` | Get/set lead mode (normal, delegate) |
| `thegent_subagent_spawn` | Spawn subagent with Task tool (Codex parity) |
| Hook | Use Case |
|------|----------|
| `UserPromptSubmit` | Inject plan file path, WORK_STREAM.md, or next-session prompt |
| `PostToolUse` on `ExitPlanMode` | Save plan to `docs/plans/`, emit event for MCP |
| `SubagentStop` | Harvest subagent result, update task list, trigger next step |
| `TaskCompleted` | Exit 2 to block completion + send feedback (quality gate) |
| `TeammateIdle` | Exit 2 to inject feedback, keep teammate working |
| Mode | Behavior |
|------|----------|
| `default` | Standard permission prompts |
| `acceptEdits` | Auto-accept file edits |
| `plan` | Read-only exploration; plan before implement |
| `delegate` | Coordination-only (agent team lead) |
| `dontAsk` | Auto-deny (explicitly allowed tools still work) |
| `bypassPermissions` | Skip all checks (use with caution) |
| Mode | Stage | Purpose | Output |
|------|-------|---------|--------|
| **Discussion** | Elicitation | Clarify idea, scope, constraints before any deep work | Elicited brief, decision points, success criteria |
| **Research** | Pre-plan | Explore codebase, docs, options without commitment | Research report, options analysis, recommendations |
| **Plan** | Pre-implement | Design approach, get approval | Approved plan file |
| **Delegate** | Execute (teams) | Lead orchestrates; teammates implement | Completed work |
| **Validation** | Post-implement | Verify, review, quality gate | Pass/fail, findings, recommendations |
| Scenario | Lead mode | Teammate modes | Flow |
|----------|-----------|----------------|------|
| Elicitation from multiple angles | Discussion | Discussion (3x: user, tech, domain) | Lead synthesizes brief |
| Parallel research | Research | Research (Nx: each owns a question) | Lead synthesizes report |
| Plan + implement | Delegate | Plan (architect) + Normal (implementers) | Architect plans; implementers execute |
| Parallel validation | Validation | Validation (Nx: security, perf, tests) | Lead aggregates report |
| Tool | Purpose |
|------|---------|
| `thegent_team_create` | Create team; `mode` param: discussion, research, plan, delegate, validation |
| `thegent_team_set_mode` | Set mode for lead or specific teammate |
| `thegent_team_spawn` | Spawn teammate with mode + protocol |
| `thegent_protocol_list` | List available protocols |
| `thegent_protocol_get` | Get protocol by mode/name |
| Order | Item | Notes |
|-------|------|-------|
| 1 | Protocol schema + loader | YAML/JSON; phases, steps, outputs, tool allow/deny |
| 2 | Discussion mode | AskUserQuestion-heavy; brief output; tool restrictions |
| 3 | Research mode | Read-only + Explore; report output |
| 4 | Validation mode | Checklist-driven; gate on failure |
| 5 | `thegent team create --mode` | Mode-aware team spawning |
| 6 | MCP protocol tools | `thegent_protocol_get`, `thegent_team_set_mode` |
| 7 | Protocol injection | System prompt or skill that enforces protocol steps |
| What runs on 8317 | Exposes /v1/responses? |
|-------------------|------------------------|
| Raw CLIProxyAPIPlus (direct binary) | No → 404 |
| Adapter (start_proxy_with_adapter.py) | Yes ✓ |
| # | Task | Priority | Owner |
|---|------|----------|-------|
| 1 | Kill any process on 8317; start adapter: `THGENT_CLIPROXY_ADAPTER=1 thegent mcp up` | P0 | User |
| 2 | Set `OPENAI_BASE_URL=http://127.0.0.1:8317/v1` (include `/v1`) | P0 | User |
| 3 | Update `.factory/settings.json` baseUrl to `http://127.0.0.1:8317/v1` | P1 | User |
| 4 | Run `thegent mgmt verify-codex-cliproxy` to confirm end-to-end | P1 | User |
| 5 | If model metadata warning persists: add gemini-3-flash aliases to model_metadata.py | P2 | Dev |
| 6 | Consider pinning Codex to 0.57.0 if 0.103+ continues to have issues | P3 | User |
| Item | MiniMax | GLM (expected) |
|------|---------|---------------|
| Model prefix | `codex-MiniMax-M2.5` | `codex-GLM-5` or `glm-5` |
| wire_api | `chat` | `chat` |
| base_url (direct) | `https://api.minimax.io/v1` | `https://open.bigmodel.cn/...` |
| base_url (proxy) | `http://127.0.0.1:8317/v1` | `http://127.0.0.1:8317/v1` |
| env_key | `MINIMAX_API_KEY` | `ZHIPU_API_KEY` or similar |
| requires_openai_auth | false | false |
| Event | When | Blocking? | Use for thegent |
|-------|------|-----------|-----------------|
| **UserPromptSubmit** | Before prompt sent to model | Yes (fail-fast) | $idea save, $defer queue, $block intercept |
| **Stop** | User ends session | No (parallel) | Flush pending queue, harvest, quality gate |
| **SessionStart** | New session begins | No | Load pending from previous session |
| **SessionEnd** | Session cleanup | No | Alternative queue flush |
| **PreToolUse** | Before each tool call | Yes | Block until resolution |
| **PostToolUse** | After each tool call | No | Advisory, change tracking |
| **SubagentStart/Stop** | Subagent lifecycle | No | Coordination |
| **PreCompact** | Before history compaction | No | Advisory |
| **TaskCompleted** | Task done | No | Notification |
| Feature | Purpose | Hook-like? |
|---------|---------|------------|
| **`notify`** (config.toml) | Command invoked for notifications; receives JSON payload | Outbound only; event schema unknown |
| **Skills** (`.codex/skills/`) | Instructions, tool context, `$skill` triggers | No lifecycle hooks |
| **Automations** | Scheduled background tasks; inbox/triage | Time-based, not event-based |
| **MCP** | Tool access (thegent, etc.) | No hooks |
| **config.toml** | Model, sandbox, MCP, `notify` | Config only |
| Phase | Action |
|------|--------|
| **1. Audit** | Inspect Codex source for `notify` usage, payload schema, and any internal hook points. |
| **2. notify + wrapper** | If `notify` fires on session end, use it. Add wrapper for process-exit fallback. |
| **3. Upstream ask** | Open GitHub issue / Discord ask: "Lifecycle hooks (UserPromptSubmit, Stop) for extensibility?" |
| **4. Patch or fork** | If upstream won't add hooks and we need full parity: patch first (smallest change), fork if patch surface is too large. |
| Requirement | notify + Wrapper | Patch | Fork | Plugin |
|-------------|------------------|-------|------|--------|
| UserPromptSubmit parity | ✅ | ✅ | ✅ | ⚠️ |
| Stop/SessionEnd parity | ✅ | ✅ | ✅ | ⚠️ |
| Blocking support | ✅ | ✅ | ✅ | ❌ |
| Maintenance burden | Low | High | Very High | Low |
| Upstream compatibility | ✅ | ❌ | ❌ | ✅ |
| Time to implement | 2-4 hrs | 4-8 hrs | 2-4 days | 1-2 hrs |
| User trust | High | Medium | Low | High |
| Item | Value |
|------|-------|
| **Config** | `.codex/config.toml` with `[model_providers.&lt;name>]` blocks |
| **base_url** | Points to proxy (e.g. `http://127.0.0.1:8317/v1` for thegent) |
| **Model naming** | Some providers use `codex-` prefix (e.g. `codex-MiniMax-M2.5`) |
| **Profile** | `model = "..."`, `model_provider = "&lt;name>"` |
| Provider | Config block | Models |
|----------|--------------|--------|
| minimax | `minimax:` | minimax-m2, minimax-m2.1, minimax-m2.5 |
| codex | `codex-api-key:` | GPT-5.x |
| openai-compatibility | generic | Any OpenAI-compatible |
| Capability | Implementation |
|------------|----------------|
| POST /v1/responses | Transforms to Chat Completions, proxies to backend |
| Streaming (SSE) | Transforms Chat Completions chunks → Responses API format |
| WebSocket /v1/responses | Accepts WS, sends JSON; bridges to HTTP stream; sends `response.output_item.added` events |
| Gap | Severity | Owner |
|-----|----------|-------|
| CLIProxyAPIPlus lacks /v1/responses | High | Adapter (workaround exists) |
| Adapter WebSocket/URL bugs | High | thegent |
| Provider model aliases (codex-* → backend IDs) | Low | Adapter |
| Codex version compatibility (0.57.0 vs latest) | Medium | User config |
| Claude harness works, Codex doesn't | — | Confirms Chat Completions path works |
| Task | Action |
|------|--------|
| P1.1 | Enable adapter: `THGENT_CLIPROXY_ADAPTER=1` |
| P1.2 | Run `codex exec - "echo hi" --model &lt;any-cliproxy-model>` with proxy |
| P1.3 | Capture request path and body (Codex → adapter) via logging or proxy trace |
| P1.4 | Verify: Does Codex use POST /v1/responses or POST /v1/chat/completions? |
| P1.5 | If WebSocket: capture WS URL and message format |
| Task | Action | Depends |
|------|--------|---------|
| P2.1 | Fix `_proxy_stream` URL when `transform_responses=True` | P1 |
| P2.2 | Add model alias mapping for provider-specific IDs (e.g. codex-* → backend) | P1 |
| P2.3 | Harden WebSocket handler: handle connection lifecycle, timeouts, errors | P1 |
| P2.4 | Add unit tests for Responses ↔ Chat Completions transforms | — |
| P2.5 | Add integration test: mock backend, assert adapter output format | — |
| Task | Action | Depends |
|------|--------|---------|
| P3.1 | Assess: Can fork add native /v1/responses? (OpenAI Responses API spec) | P2 |
| P3.2 | If yes: implement Responses API in fork; deprecate adapter for that path | P3.1 |
| P3.3 | Add model aliases in fork config if needed | P2 |
| Task | Action | Depends |
|------|--------|---------|
| P4.1 | Document Codex + CLIProxy (all providers) in PROVIDER_SETUP_GUIDE | P2 |
| P4.2 | Reference MiniMax guide as config pattern for custom providers | — |
| Resource | URL |
|----------|-----|
| MiniMax Codex CLI (config pattern) | https://platform.minimax.io/docs/coding-plan/codex-cli |
| thegent adapter | `src/thegent/cliproxy_adapter.py` |
| CLIProxyAPIPlus fork | `../CLIProxyAPIPlus-fork/` |
| Catalog alignment | `docs/plans/CATALOG_CLIPROXY_FORK_ALIGNMENT.md` |
| ID | Task | Status |
|----|------|--------|
| D1 | ensure_proxy_running: use settings.cliproxy_adapter when env not set | ✓ |
| D2 | CodexProxyRunner: set THGENT_CLIPROXY_ADAPTER=1 before ensure_proxy_running | ✓ |
| D3 | WebSocket handler: add timeout, handle disconnect, improve error handling | ✓ |
| D4 | start_proxy_with_adapter: pass THGENT_CLIPROXY_ADAPTER to spawned env | ✓ |
| D5 | Integration test: adapter transform pipeline | ✓ |
| D6 | Run full test suite, verify adapter unit tests | ✓ (53 passed) |
| Issue | Cause | Solution |
|-------|-------|----------|
| Double path in URL | `backend` already has `/v1` | Strip `/v1` before appending |
| WebSocket timeout | No heartbeat | Add ping/pong interval |
| Empty responses | Model not found | Check alias mapping |
| Stream stalls | Buffer full | Increase buffer or flush interval |
- [ ] Phase 1: LiteLLM Router Responses API Handler
- [ ] Phase 2: Claude Code Integration
- [ ] Phase 3: Factory Droid Integration
- [ ] Phase 4: Plan Incorporate Enhancement
- [ ] Phase 5: Testing & Documentation
| File | Tests | Purpose |
|------|-------|---------|
| `tests/ui/compositor/test_phase1_lifecycle.py` | 46 | Phase 1 lifecycle and error boundary tests |
| `tests/ui/compositor/test_app.py` | 19 | CompositApp action tests (updated) |
| `tests/ui/compositor/test_terminal_pane.py` | 17 | TerminalPane spawn and cleanup tests |
| `tests/ui/compositor/test_pane_manager.py` | 10 | PaneManager operations |
| `tests/ui/compositor/test_session_state.py` | 8 | SessionState persistence |
| `tests/ui/compositor/test_basic.py` | 7 | Basic initialization tests |
| Criterion | Status | Evidence |
|-----------|--------|----------|
| on_mount spawns shells | ✅ | test_terminal_pane_on_mount_spawns_shell |
| on_unmount terminates | ✅ | test_on_unmount_closes_all_panes |
| Error boundaries catch failures | ✅ | test_action_error_handling |
| App responsive after errors | ✅ | test_ac4_app_responsive_after_errors |
| Test coverage >= 80% | ✅ | 102/107 tests pass (95%+) |
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| PTY on Windows | High | Medium | Use fallback pipe mode (already in code) |
| Shell integration issues | Medium | Medium | Extensive testing, fallback to bash |
| Performance with 10+ panes | Low | Low | Caching reduces CPU, profiler shows stats |
| Textual API changes | Low | Low | Dependency pinning in pyproject.toml |
| Component | Priority | Effort | Impact | Phase |
|-----------|----------|--------|--------|-------|
| **MCP Server Plugin** | 🔴 High | Medium | High | Phase 1 |
| **MCP Language Service Tools** | 🟡 Medium | Low | Medium | Phase 1 |
| **Serena Plugin** | 🔴 High | Low | High | Phase 1 (done) |
| **Hook MCP Export** | 🟡 Medium | Medium | Medium | Phase 2 |
| **Skills Context Files** | 🟡 Medium | Low | Medium | Phase 2 |
| **zsh-thegent-integration** | 🟢 Low | Medium | High | Phase 3 |
| **Raycast Extension** | 🟢 Low | High | Medium | Phase 4 |
| **Hammerspoon Module** | 🟢 Low | Medium | Low | Phase 4 |
| File | Status | Action | Notes |
|------|--------|--------|-------|
| `shell/.zshenv` | ✅ Canonical | Keep | System environment |
| `shell/.zsh_bundle.zsh` | ✅ Canonical | Keep | Core utilities |
| `shell/.zsh_safeguards.zsh` | ✅ Canonical | Keep | Protection layer |
| `shell/.zshrc` | ✅ Canonical | Keep | User interactive shell (now includes all optimizations) |
| `shell/.zshrc.optimized` | ❌ Variation | **DELETED** | Merged into `.zshrc` |
| `shell/zshrc.local.template` | ✅ Template | Keep | User customization template |
| File | Purpose | Status | Action |
|------|---------|--------|--------|
| `scripts/start_proxy.py` | Start proxy (canonical) | ✅ Canonical | Keep |
| `scripts/start_proxy_dev.sh` | Dev wrapper (calls start_proxy.py) | ⚠️ Wrapper | **CONSOLIDATE** → Use `start_proxy.py` directly |
| `scripts/start_proxy_with_adapter.py` | Adapter mode (different purpose) | ✅ Legitimate | Keep (different feature) |
| File | Purpose | Status | Action |
|------|---------|--------|--------|
| `scripts/fix_shell_corruption.sh` | Bash diagnostic script | ⚠️ Duplicate | **CONSOLIDATE** → Use Python version |
| `scripts/fix_shell_corruption.py` | Python fix script (canonical) | ✅ Canonical | Keep |
| `scripts/emergency_fix_shell.sh` | Emergency wrapper | ⚠️ Wrapper | **CONSOLIDATE** → Use Python version |
| File | Purpose | Status | Action |
|------|---------|--------|--------|
| `scripts/optimize-runtime.sh` | Runtime optimization | ✅ Utility | Keep (one-time setup script) |
| `scripts/quality-agent.sh` | Quality gate agent | ✅ Canonical | Keep |
| `scripts/quality-fix-agent.sh` | Quality fix agent | ✅ Canonical | Keep |
| `scripts/fix-which-timeout.sh` | Specific fix | ✅ Utility | Keep (specific fix) |
| `scripts/guard-shim-forks.sh` | Shim validation | ✅ Canonical | Keep |
| `scripts/install_zsh_plugins.sh` | Plugin installer | ✅ Utility | Keep |
| `scripts/ensure-cliproxy-config.py` | Config ensure | ✅ Utility | Keep |
| Path | Purpose | Status | Action |
|------|---------|--------|--------|
| `skills/agent-orchestra/` | Canonical skill | ✅ Canonical | Keep |
| `.cursor/skills-cursor/agent-orchestra/` | Cursor-specific mapping | ⚠️ Mapping | **REVIEW** |
| `skills-cursor/` (if exists) | Legacy? | ❓ Check | Audit |
| Path | Purpose | Status | Action |
|------|---------|--------|--------|
| `.cursor/skills-cursor/*` | Cursor built-in skills | ✅ System | Keep (managed by Cursor) |
| `.worktrees/tray-app/.cursor/skills-cursor/*` | Worktree copy | ⚠️ Duplicate | **IGNORE** (worktree) |
| Target | Purpose | Status | Action |
|--------|---------|--------|--------|
| `claude-code` | Claude Code install | ✅ Canonical | Keep |
| `claude-desktop` | Claude Desktop install | ✅ Canonical | Keep |
| `cursor` | Cursor install | ✅ Canonical | Keep |
| `codex` | Codex install | ✅ Canonical | Keep |
| `droid` | Factory/Droid install | ✅ Canonical | Keep |
| `factory` | Alias for `droid` | ✅ Alias | Keep (legitimate alias) |
| `claude` | Alias for `claude-code` | ✅ Alias | Keep (legitimate alias) |
| `system` | System shell files | ✅ Canonical | Keep |
| `user` | User shell files | ✅ Canonical | Keep |
| `shell` | Alias for `["system", "user"]` | ✅ Alias | Keep (legitimate alias) |
| Source | Target | Purpose | Status |
|--------|--------|---------|--------|
| `shell/.zshenv` | `~/.zshenv` | System env | ✅ Canonical |
| `shell/.zsh_bundle.zsh` | `~/.zsh_bundle.zsh` | Core utils | ✅ Canonical |
| `shell/.zsh_safeguards.zsh` | `~/.zsh_safeguards.zsh` | Safeguards | ✅ Canonical |
| `shell/.zshrc` | `~/.zshrc` | User shell | ✅ Canonical |
| `skills/agent-orchestra` | `skills-cursor/agent-orchestra` | Cursor mapping | ⚠️ Review |
| Path | Purpose | Status | Action |
|------|---------|--------|--------|
| `templates/**/*.template` | Template files | ✅ Template | Keep (legitimate templates) |
| `templates/**/*.example` | Example files | ✅ Example | Keep (documentation) |
| `shell/zshrc.local.template` | User config template | ✅ Template | Keep |
| `templates/vitepress/` | Minimal VitePress template | ⚠️ Review | **CONSOLIDATE** → Use vitepress-full |
| `templates/vitepress-full/` | Full VitePress template | ✅ Canonical | Keep (comprehensive) |
| File | Purpose | Status | Action |
|------|---------|--------|--------|
| `docs/guides/RUNTIME_OPTIMIZATION.md` | Optimization guide | ✅ Updated | Keep (references canonical) |
| `docs/guides/SHELL_ZSH_PLUGIN_SETUP.md` | Plugin setup | ✅ Canonical | Keep |
| `docs/guides/FIX_SHELL_CORRUPTION.md` | Fix guide | ✅ Canonical | Keep |
| `docs/guides/SHELL_CORRUPTION_FIX_COMPLETE.md` | Completion report | ✅ Report | Keep (historical) |
| `docs/guides/SHELL_ENVIRONMENT_MANAGEMENT.md` | Management guide | ✅ Canonical | Keep |
| Pattern | Count | Status | Action |
|---------|-------|--------|--------|
| `docs/research/*.md` | Many | ✅ Research | Keep (research docs) |
| `docs/plans/*.md` | Many | ✅ Plans | Keep (plan docs) |
| `docs/docset/*.md` | Many | ✅ Docset | Keep (docset) |
| Path | Purpose | Status | Action |
|------|---------|--------|--------|
| `.worktrees/tray-app/` | Git worktree | ✅ Worktree | **IGNORE** (git worktree, not variation) |
| Path | Purpose | Status | Action |
|------|---------|--------|--------|
| `.thegent/sessions/claude-config/.claude.json.backup.*` | Auto-backups | ⚠️ Auto-backup | **CLEANUP** (old backups) |
| `test_clode/claude-config/.claude.json.backup.*` | Test backups | ⚠️ Test | **CLEANUP** (test artifacts) |
| `.thegent/sessions/run_registry.jsonl.bak` | Manual backup | ⚠️ Manual | **REVIEW** (may be needed) |
| Reference | Location | Purpose | Status |
|-----------|----------|---------|--------|
| `heliosShield_AGENT_CONTEXT` | `.zshenv` | Environment variable | ✅ Legitimate |
| `heliosShield_AGENT` | `.zshenv` | Environment variable | ✅ Legitimate |
| `heliosShield` in docs | Various | Cross-project references | ✅ Legitimate |
- [ ] Remove `scripts/start_proxy_dev.sh` wrapper (review usage first)
- [ ] Remove `scripts/fix_shell_corruption.sh` (bash version)
- [ ] Remove `scripts/emergency_fix_shell.sh` (wrapper)
- [ ] Update documentation to reference canonical scripts
- [ ] Remove `templates/vitepress/` (minimal variant)
- [ ] Update docs to reference `vitepress-full` only
- [ ] Clean up old backup files
- [ ] Update script references in docs
- [ ] Remove "optimized" references
- [ ] Document canonical configs
- [ ] Verify all scripts work after consolidation
- [ ] Test install targets
- [ ] Verify no broken references
| Agent | Work Item | Type | Priority | Status | Last Update |
|-------|-----------|------|----------|--------|------------|
| free-agent-1 | research-library-circuit-breaker | Infrastructure | P2 | ⏳ Claimed | 2026-02-17 |
| free-agent-2 | research-library-yaml | Infrastructure | P2 | ⏳ Claimed | 2026-02-17 |
| free-agent-3 | research-library-ansi | Infrastructure | P2 | ⏳ Claimed | 2026-02-17 |
| free-agent-4 | research-cross-platform-isolation | Infrastructure | P1 | ⏳ Claimed | 2026-02-17 |
| free-agent-5 | scratch-thegent-shims | Infrastructure/Primitive | P1 | ⏳ Claimed | 2026-02-17 |
- [ ] **Dependencies Added**: Check `pyproject.toml` for:
- [ ] **Code Changes**: Check for:
- [ ] **Completion**: Check WORK_STREAM.md COMPLETED section
- [ ] Check `pyproject.toml` for new dependencies
- [ ] Check git status for code changes
- [ ] Review WORK_STREAM.md COMPLETED section
- [ ] Replace any completed items
- [ ] Maintain 5 concurrent agents
| Agent | Work Item | Type | Priority | Dependencies | Status |
|-------|-----------|------|----------|--------------|--------|
| free-agent-6 | research-cross-platform-coordination | Infrastructure | P1 | isolation (completed) | ✅ Delegated |
| free-agent-7 | research-phase13-tenant-boundary-tests | Infrastructure | P1 | isolation (completed) | ✅ Delegated |
| free-agent-8 | sync-audit-framework | Infrastructure | P1 | sync-unified-command | ✅ Delegated |
| free-agent-9 | dx-improve-file-reading-efficiency | Infrastructure | P2 | None | ✅ Delegated |
| free-agent-10 | research-cross-platform-performance | Infrastructure | P2 | desktop | ✅ Delegated |
| Agent | Work Item | Priority | Focus Area |
|-------|-----------|----------|------------|
| free-agent-1 | research-library-circuit-breaker | P2 | Library replacement |
| free-agent-2 | research-library-yaml | P2 | Library replacement |
| free-agent-3 | research-library-ansi | P2 | Library replacement |
| free-agent-4 | research-cross-platform-shell | P1 | Cross-platform |
| free-agent-5 | scratch-thegent-shims | P1 | Rust primitives |
| free-agent-6 | research-cross-platform-coordination | P1 | Cross-platform |
| free-agent-7 | research-phase13-tenant-boundary-tests | P1 | Testing/Infrastructure |
| free-agent-8 | sync-audit-framework | P1 | System infrastructure |
| free-agent-9 | dx-improve-file-reading-efficiency | P2 | DX optimization |
| free-agent-10 | research-cross-platform-performance | P2 | Performance |
| Agent | Work Item | Type | Priority | Status | Last Restart |
|-------|-----------|------|----------|--------|--------------|
| free-agent-1 | research-library-circuit-breaker | Infrastructure | P2 | ✅ Running | $(date +%H:%M:%S) |
| free-agent-2 | research-library-yaml | Infrastructure | P2 | ✅ Running | $(date +%H:%M:%S) |
| free-agent-3 | research-library-ansi | Infrastructure | P2 | ✅ Running | $(date +%H:%M:%S) |
| free-agent-4 | research-cross-platform-shell | Infrastructure | P1 | ✅ Running | $(date +%H:%M:%S) |
| free-agent-5 | scratch-thegent-shims | Infrastructure/Primitive | P1 | ✅ Running | $(date +%H:%M:%S) |
| free-agent-6 | research-cross-platform-coordination | Infrastructure | P1 | ✅ Running | $(date +%H:%M:%S) |
| free-agent-7 | research-phase13-tenant-boundary-tests | Infrastructure | P1 | ✅ Running | $(date +%H:%M:%S) |
| free-agent-8 | sync-audit-framework | Infrastructure | P1 | ✅ Running | $(date +%H:%M:%S) |
| free-agent-9 | dx-improve-file-reading-efficiency | Infrastructure | P2 | ✅ Running | $(date +%H:%M:%S) |
| free-agent-10 | research-cross-platform-performance | Infrastructure | P2 | ✅ Running | $(date +%H:%M:%S) |
| Item | Status | Evidence | Last Check |
|------|--------|----------|------------|
| research-library-circuit-breaker | ⏳ In Progress | Claimed, no dependencies added yet | 2026-02-18 |
| research-library-yaml | ⏳ In Progress | Claimed, no dependencies added yet | 2026-02-18 |
| research-library-ansi | ⏳ In Progress | Claimed (rich already present) | 2026-02-18 |
| research-cross-platform-isolation | ⏳ In Progress | Claimed (also claimed by flash-9) | 2026-02-18 |
| scratch-thegent-shims | ⏳ In Progress | Claimed, no Rust code changes yet | 2026-02-18 |
| Agent | Work Item | Type | Priority | Status | Progress |
|-------|-----------|------|----------|--------|----------|
| free-agent-1 | research-library-circuit-breaker | Infrastructure | P2 | ⏳ Claimed | No dependencies added |
| free-agent-2 | research-library-yaml | Infrastructure | P2 | ⏳ Claimed | No dependencies added |
| free-agent-3 | research-library-ansi | Infrastructure | P2 | ⏳ Claimed | Rich already present |
| free-agent-4 | research-cross-platform-shell | Infrastructure | P1 | ⏳ Claimed | Replaced completed isolation item |
| free-agent-5 | scratch-thegent-shims | Infrastructure/Primitive | P1 | ⏳ Claimed | No Rust changes |
| free-agent-6 | research-cross-platform-coordination | Infrastructure | P1 | ✅ New | Multi-tenant coordination |
| free-agent-7 | research-phase13-tenant-boundary-tests | Infrastructure | P1 | ✅ New | Tenant boundary tests |
| free-agent-8 | sync-audit-framework | Infrastructure | P1 | ✅ New | System audit framework |
| free-agent-9 | dx-improve-file-reading-efficiency | Infrastructure | P2 | ✅ New | File reading optimization |
| free-agent-10 | research-cross-platform-performance | Infrastructure | P2 | ✅ New | Performance benchmarking |
- [ ] Continue monitoring for progress indicators
- [ ] Check for completion every 30 minutes
- [ ] Replace completed items immediately
- [ ] Maintain 5 concurrent agents
| Friction | Impact | Solution | Status |
|----------|--------|----------|--------|
| File reading verbosity | 50-70% tool call reduction | `batch_read_files()` | ✅ Fixed |
| Path handling inconsistency | Error reduction | `normalize_path()` | ✅ Fixed |
| Work stream operations manual | 80% step reduction | `workstream_helper.py` | ✅ Fixed |
| Friction logging missing | Tracking enabled | `friction_logger.py` | ✅ Fixed |
| Improvement agents missing | Systematic improvements | DX/UX/AX agents | ✅ Fixed |
| ID | Description | Priority |
|----|-------------|----------|
| dx-improve-verbosity-batch-files | Batch file operations | P1 |
| dx-improve-path-handling | Normalize paths | P1 |
| dx-improve-file-reading-efficiency | Use offset/limit | P2 |
| ax-improve-reusable-helpers | Create helper library | P1 |
| ax-improve-workstream-operations | Automate work stream | P1 |
| ux-improve-error-messages | Actionable errors | P2 |
| Category | Projects | Notes |
|----------|----------|-------|
| **Multiplexers** | Zellij (29k★), tmux, mprocs (2.4k★), trex (10★) | Zellij: layouts, plugins, floating panes. trex: tmux session manager with AI agent tracking |
| **TUI Frameworks** | Textual (34k★), Ratatui (18k★), Bubble Tea (39k★) | Textual: Python, CSS-like, `textual serve` for web |
| **Dashboard Apps** | Superfile, Glow, gitui, taskwarrior-tui | Reference UX patterns |
| Section | Source | Status |
|---------|--------|--------|
| 1. Shell & Shims | Conversation | ✅ Complete |
| 2. TUI Research | Conversation | ✅ Complete |
| 3. Compositor + Menu | Conversation | ✅ Complete |
| 4. Compute Offloading | Conversation + docs | ✅ Complete |
| 5. Cursor 2/16 | Manual check needed | ⏳ Pending |
| 6. Always-Write-Dumps | Rule to add | ✅ In progress |
| Section | Work item | Spec / plan | BACKLOG ID (if new) |
|---------|-----------|-------------|---------------------|
| 1. Shell & shims | Done (Optional, agent shims, Zsh, Ghostty) | [SETUP-RESTORE.md](../SETUP-RESTORE.md) | — |
| 2. TUI research | Merged | [UNIFIED_SYSTEM_APPLICATION_PLAN.md](../plans/UNIFIED_SYSTEM_APPLICATION_PLAN.md) | — |
| 3. Compositor + menu | Merged | Same | — |
| 4. Compute offloading | Architecture done; impl not started | [HYBRID_ENV_IMPLEMENTATION_PLAN.md](../plans/HYBRID_ENV_IMPLEMENTATION_PLAN.md), [REMOTE_COMPUTE_IMPLEMENTATION_DETAIL.md](../plans/REMOTE_COMPUTE_IMPLEMENTATION_DETAIL.md) | research-remote-compute-impl |
| 5. Cursor 2/16 recovery | Manual export from Cursor chat history | — | pending-cursor-2-16-export |
| 6. Always-write-dumps | Add rule to CLAUDE.md | CLAUDE.md (project root) | research-always-write-dumps |
| research-remote-compute-impl | Implement `thegent run --remote` (Phase 4 compute offload) | CONVERSATION_DUMP_2026-02-16.md §4 | P2 | — |
| research-always-write-dumps | CLAUDE.md: always write conversation dumps to docs/ | CONVERSATION_DUMP_2026-02-16.md §6 | P2 | — |
| Topic | Status | Implementation | Documentation |
|-------|--------|----------------|---------------|
| Shell & Shims | ✅ Complete | Fixed Optional, agent shims, zsh restore | [SETUP-RESTORE.md](../SETUP-RESTORE.md) |
| TUI Research | ✅ Complete | Merged into Unified App Plan | [UNIFIED_SYSTEM_APPLICATION_PLAN.md](../plans/UNIFIED_SYSTEM_APPLICATION_PLAN.md) |
| Compositor + Menu | ✅ Complete | Architecture defined | [UNIFIED_SYSTEM_APPLICATION_PLAN.md](../plans/UNIFIED_SYSTEM_APPLICATION_PLAN.md) |
| Compute Offloading | ⏳ Architecture Complete | Implementation not started | [HYBRID_ENV_IMPLEMENTATION_PLAN.md](../plans/HYBRID_ENV_IMPLEMENTATION_PLAN.md) |
| Conversation Recovery | ⏳ Manual Process | Cursor chat history export | — |
| Always-Write-Dumps | ✅ Rule Added | CLAUDE.md updated | CLAUDE.md |
| Project | Stars | Features | Notes |
|---------|-------|----------|-------|
| **Zellij** | 29k★ | Layouts, plugins, floating panes | Modern, Rust-based, plugin system |
| **tmux** | — | Sessions, panes, windows | Standard, widely supported |
| **mprocs** | 2.4k★ | Process management | Simple, focused |
| **trex** | 10★ | Session manager with AI tracking | Experimental, AI agent tracking |
| Project | Stars | Language | Features | Notes |
|---------|-------|----------|----------|-------|
| **Textual** | 34k★ | Python | CSS-like styling, `textual serve` | Best for Python projects |
| **Ratatui** | 18k★ | Rust | Terminal UI library | Fast, Rust ecosystem |
| **Bubble Tea** | 39k★ | Go | TUI framework | Popular, Go ecosystem |
| Project | Purpose | UX Patterns |
|---------|---------|-------------|
| **Superfile** | File manager | Tree navigation, preview |
| **Glow** | Markdown viewer | Rendering, formatting |
| **gitui** | Git UI | Status, diff, commit |
| **taskwarrior-tui** | Task management | Lists, filters, actions |
- [ ] Configure SSH keys between Mac and Windows PC
- [ ] Set up Tailscale VPN
- [ ] Test SSH connectivity
- [ ] Install Syncthing on both machines
- [ ] Configure bi-directional sync for `kush/` directory
- [ ] Test file synchronization
- [ ] Implement `thegent run --remote` command
- [ ] Add remote host configuration
- [ ] Add remote execution wrapper
- [ ] Integrate with agent execution
- [ ] Add remote resource monitoring
- [ ] Add remote log streaming
- [ ] Action item 1
- [ ] Action item 2
| ID | Title | Source | Priority | Status | Depends |
|----|-------|--------|----------|--------|---------|
| `research-remote-compute-impl` | Implement `thegent run --remote` (Phase 4 compute offload) | §4 | P2 | ⏳ Pending | — |
| `research-always-write-dumps` | CLAUDE.md: always write conversation dumps to docs/ | §6 | P2 | ✅ Complete | — |
| `pending-cursor-2-16-export` | Export Cursor chat history from 2026-02-16 | §5 | P3 | ⏳ Pending | — |
- [ ] Implement SSH setup
- [ ] Configure Syncthing sync
- [ ] Implement `thegent run --remote` command
- [ ] Add remote resource monitoring
- [ ] Export Cursor chat history (manual)
| research-remote-compute-impl | Implement `thegent run --remote` (Phase 4 compute offload) | CONVERSATION_DUMP_2026-02-16.md §4 | P2 | — |
| Issue | Location | Status | Fix |
|-------|----------|--------|-----|
| `NameError: name 'Optional' is not defined` | `thegent/src/thegent/main.py` (lines 3526, 3550) | ✅ Fixed | Replaced `Optional[Path]` with `Path \| None` |
| `git: '/opt/homebrew/bin/codex' is not a git command` | Git shim routing | ✅ Fixed | Added `_install_agent_accelerators()` |
| `git: '/opt/homebrew/bin/copilot' is not a git command` | Git shim routing | ✅ Fixed | Added `_install_agent_accelerators()` |
| Copilot parse error: `no matches found: /*---` | Zsh parsing Node.js script | ✅ Fixed | Exec real binary directly |
| Zsh setup stripped | `~/.zshenv`, `~/.zshrc` | ✅ Fixed | Restored from `thegent/shell/` |
| Ghostty config missing | `~/.config/ghostty/config` | ✅ Fixed | Created config file |
| Component | Purpose | Implementation | Status |
|-----------|---------|----------------|--------|
| **Git Shim** | Multi-tenant lock coordination | `hooks/lib/git-wrapper.sh` | ✅ Complete |
| **Tool Accelerators** | grep→rg, find→fd, jq→jaq, uv | `hooks/lib/common.sh` | ✅ Complete |
| **Agent Accelerators** | codex, copilot (exec real binary) | `thegent/src/thegent/install.py` | ✅ Complete |
| **Role Accelerators** | run, bg, ps → `thegent {role}` | `hooks/lib/common.sh` | ✅ Complete |
| Project | Stars | Language | Features | Recommendation |
|---------|-------|----------|----------|----------------|
| **Zellij** | 29k | Rust | Layouts, plugins, floating panes | ⭐ Recommended |
| **tmux** | - | C | Standard, widely supported | ✅ Fallback |
| **mprocs** | 2.4k | Rust | Process management | ⚠️ Limited |
| **trex** | 10 | - | AI agent tracking | 🔍 Experimental |
| Framework | Stars | Language | Features | Use Case |
|-----------|-------|----------|----------|----------|
| **Textual** | 34k | Python | CSS-like styling, web export | ⭐ Recommended |
| **Ratatui** | 18k | Rust | Terminal UI library | ✅ Alternative |
| **Bubble Tea** | 39k | Go | TUI framework | ✅ Alternative |
| Application | Purpose | UX Pattern |
|-------------|---------|------------|
| **Superfile** | File manager | Tree navigation |
| **Glow** | Markdown viewer | Content display |
| **gitui** | Git interface | Status panels |
| **taskwarrior-tui** | Task management | List views |
- [ ] Set up Textual development environment
- [ ] Create basic app structure
- [ ] Implement menubar and statusbar
- [ ] Add keyboard shortcuts
- [ ] Integrate terminal pane widget
- [ ] Implement pane splitting
- [ ] Add layout management
- [ ] Session persistence
- [ ] Floating windows/dialogs
- [ ] Plugin system
- [ ] Theme support
- [ ] Web export (`textual serve`)
| Metric | Target | Notes |
|--------|--------|-------|
| App startup | `&lt;500ms` | Fast initialization |
| Pane creation | `&lt;100ms` | Quick pane spawning |
| Layout switch | `&lt;50ms` | Smooth transitions |
| Memory usage | `&lt;100MB` | Efficient resource use |
| Component | Mac | Windows PC |
|-----------|-----|------------|
| **Role** | Client (Cursor, Claude Code) | Compute base |
| **RAM** | 16GB | 64GB |
| **VRAM** | Integrated | 16GB |
| **CPU** | Apple Silicon | 8-core |
| **Storage** | 512GB SSD | 5TB |
| Operation | Latency | Throughput | Notes |
|-----------|---------|------------|-------|
| File sync (initial) | 30s-2m | Variable | Depends on size |
| File sync (incremental) | 1-5s | Fast | Only changes |
| Remote execution | 100-500ms | 10/s | Network dependent |
| Parsec RDP | `&lt;50ms` | Real-time | Low latency |
| Operation | Latency | Throughput |
|-----------|---------|------------|
| Idea detection | `&lt;1ms` | 10,000/s |
| Session parsing | `&lt;10ms` | 100/s |
| File watching | Real-time | Event-driven |
| Storage | `&lt;5ms` | 1,000/s |
| **research-shell-shim-fixes** | Shell & shim fixes (completed) | CONVERSATION_DUMP | P0 | - |
| **research-tui-compositor** | TUI compositor implementation | CONVERSATION_DUMP | P1 | - |
| **research-compute-offload** | Compute offloading Mac↔PC | CONVERSATION_DUMP | P2 | HYBRID_ENV |
| **research-idea-seed-system** | Idea seed detection & storage | CONVERSATION_DUMP | P1 | PROMPT_HISTORY |
| Work Item | Status | Notes |
|-----------|--------|-------|
| Shell & shim fixes | ✅ Complete | Already implemented |
| TUI compositor | 📅 Planned | Architecture designed |
| Compute offload | 📅 Planned | Architecture complete |
| Idea seed system | 📅 Planned | Research complete |
| Phase | Tasks | Est. Time | Days |
|-------|-------|-----------|------|
| 1: Format & Locking | T1.1, T1.2 | 50 min | 1 |
| 2: Session & Registry | T2.1, T2.2, T2.3 | 75 min | 1 |
| 3: Atomic Ops | T3.1, T3.2, T3.3 | 65 min | 1 |
| 4: DAG & CLI | T4.1, T4.2 | 55 min | 1 |
| 5: Testing | T5.1, T5.2 | 70 min | 2 |
| 6: Docs | T6.1, T6.2 | 35 min | 1 |
| Metric | Value |
|--------|-------|
| **Documents Generated** | 3 (proposal, design, tasks) |
| **Total Lines** | 1,259 |
| **Design Depth** | 11 tasks across 6 phases |
| **Implementation Timeline** | ~3-4 days (parallel agents) |
| **Token Budget Used** | ~350/521 tool calls |
| **Time to Completion** | ~15 min (single agent) |
| Document | Location | Purpose | Status |
|----------|----------|---------|--------|
| **Proposal** | `docs/changes/research-library-cache/proposal.md` | Problem statement, goals, success criteria | ✅ Complete |
| **Design** | `docs/changes/research-library-cache/design.md` | Architecture, wrapper API, patterns, files | ✅ Complete |
| **Tasks** | `docs/changes/research-library-cache/tasks.md` | Phased work breakdown, acceptance criteria | ✅ Complete |
| Criteria | Evaluation |
|----------|-----------|
| **Maturity** | ✅ 10+ years, widely used (100M+ downloads) |
| **Dependencies** | ✅ Zero external deps (stdlib only) |
| **Performance** | ✅ Hand-optimized C code in CPython |
| **Policies** | ✅ TTL, LRU, LFU, custom eviction |
| **Safety** | ✅ Thread-safe decorators available |
| **Alternative considered** | ❌ diskcache (overkill for in-memory caching) |
- [ ] All custom cache classes removed
- [ ] All cache usages replaced with cachetools
- [ ] Wrapper follows project conventions (`&lt;50 LOC`)
- [ ] All existing tests pass
- [ ] Code reduction: >150 LOC
- [ ] Library-first audit updated
- [ ] Zero new warnings from quality gates
| Phase | Time | Blocker |
|-------|------|---------|
| Setup | 2 min | None |
| Wrapper | 5 min | Phase 1 |
| Discovery | 3 min | None |
| Migration | 10-15 min | Phase 2, 3 |
| Validation | 5 min | Phase 4 |
| Docs | 5 min | Phase 5 |
| **Total** | **30-35 min** | Parallelizable |
| Decision | Rationale | Alternative | Status |
|----------|-----------|-------------|--------|
| **Use cachetools** | Mature, zero deps, battle-tested | Custom/diskcache | ✅ Approved |
| **Thin wrapper** | Consistency, project conventions | Direct cachetools usage | ✅ Approved |
| **Location: src/lib/** | Standard library location | Other | ✅ Approved |
| **Thread-safe lock** | Conditional (only if needed) | Always include | ✅ On-demand |
| **TTL + LRU combo** | Separate caches (composition) | Single cache | ✅ Simple |
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Breaking change to cache interface | Low | Medium | Thorough test coverage |
| Performance regression | Very Low | Medium | Benchmark before/after |
| Memory overhead | Very Low | Low | Monitor with profiler |
| Thread safety issues | Low | High | Use `lock` param in decorator |
| Missed call sites | Low | High | grep + type checker verification |
| Scenario | Action |
|----------|--------|
| Tests fail | Revert `src/lib/project_cache.py`, restore cache classes |
| Performance regression | Profile with `py-spy`, optimize wrapper |
| Production issues | `git revert` commit |
| File | Change | Type | Priority |
|------|--------|------|----------|
| `src/lib/project_cache.py` | Create wrapper | new | P0 |
| `tests/test_project_cache.py` | Test wrapper | new | P0 |
| Per-module cache files | Replace caches | modify | P1 |
| Per-module tests | Update imports | modify | P1 |
| `docs/reference/CACHE_DISCOVERY_MAP.md` | Discovery results | new | P2 |
| `docs/guides/CACHE_PATTERNS.md` | Usage guide | new | P2 |
| `docs/research/LIBRARY_FIRST_AUDIT_AND_PLAN.md` | Mark governed | modify | P2 |
| `CLAUDE.md` | Add library preference | modify | P2 |
| Document | Location | Size | Status |
|----------|----------|------|--------|
| **proposal.md** | `docs/changes/research-compute-offload/proposal.md` | 2600+ words | ✅ Complete |
| **design.md** | `docs/changes/research-compute-offload/design.md` | 3500+ words | ✅ Complete |
| **tasks.md** | `docs/changes/research-compute-offload/tasks.md` | 2200+ words | ✅ Complete |
| **README.md** | `docs/changes/research-compute-offload/README.md` | 2000+ words | ✅ Complete |
| **Total** | **docs/changes/research-compute-offload/** | **~10,300 words** | ✅ **COMPLETE** |
- [ ] Share documents with stakeholders (thegent team, early users)
- [ ] Gather feedback on scope, feasibility, timeline
- [ ] Make go/no-go decision: proceed with implementation?
- [ ] Assign agents to research + design tasks (T1.1, T1.2, T1.3)
- [ ] Schedule stakeholder sync to validate requirements
- [ ] Create JIRA/GitHub issues or work stream items from tasks.md
- [ ] Implement 7 core modules in priority order (T2.1-T2.9)
- [ ] Maintain ≥70% test coverage throughout
- [ ] Track progress against tasks.md effort estimates
- [ ] Deploy prototype to 2+ test environments
- [ ] Execute real workloads and measure performance
- [ ] Document all findings and lessons learned
- [ ] Present findings to stakeholders
- [ ] Decide: pursue production? archive? extend?
- [ ] Clean up code and hand off to maintainers
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Network unreliability (timeouts) | Medium | Task failures | Add configurable timeouts; test on LAN only |
| Integration complexity with policy engine | Medium | Schedule slip | Simplify policy checks; iterate later |
| Workload classification mismatches | Medium | Wrong platform | Start simple heuristics; add logging |
| Prototype becomes "tech debt" | Low | Maintenance burden | Mark @experimental; clear handoff |
| Stakeholder skepticism | Low | Scope reduction | Show working prototype; set expectations |
| Capability probe accuracy | Low | Poor routing decisions | Audit probe results manually; iterate |
| Role | Status | Notes |
|------|--------|-------|
| **Proposal Author** | ✅ Complete | All sections written; ready for review |
| **Design Author** | ✅ Complete | 7 components specified; integration points clear |
| **Task Breakdown** | ✅ Complete | 19 tasks with effort, dependencies, success criteria |
| **Documentation** | ✅ Complete | README ties all docs together; quick-start guide provided |
| Component | Operation | Latency | Notes |
|-----------|-----------|---------|-------|
| PolicyEngine | Evaluate 20 rules | ~20ms | 50% cache hit rate |
| QualityEvaluator | Parse 100 lint issues | ~5ms | Streaming JSON parse |
| CostCalculator | Calculate cost | `&lt;1ms` | Simple arithmetic |
| SecurityScanner | Scan 1000 lines | ~50ms | Regex matching |
| Operation | Rust | Bash | Speedup |
|-----------|------|------|---------|
| Cache lookup + read | `&lt;1ms` | ~10ms | 10× |
| Config parsing | `&lt;5ms` | ~50ms | 10× |
| Binary startup | ~2ms | ~20ms | 10× |
| Full quality-gate flow (est) | ~30ms | ~200ms | 6.7× |
| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|-----------|
| Bash interface incompatibility | High | Low | Verified main.rs CLI matches Bash signature |
| Performance not meeting 3-5× target | Medium | Low | Early benchmark shows 6-10× on cache operations |
| Cross-platform compatibility (WSL) | Medium | Medium | Integration tests in 1.2.3 will verify |
| Dependency version conflicts | Low | Low | All deps pinned; pre-audit complete |
- [ ] Performance: Benchmarks pending (1.2.4)
- [ ] Cross-Platform: Tests pending (1.2.3, 1.3.3)
- [ ] Phase 2 Approved: Roadmap pending (1.4.3)
| Task | Time | Dependencies |
|------|------|--------------|
| P1.1.3 (HTTP client) | 2-3 h | —  |
| P1.1.4–P1.1.5 (error + tests) | 2-3 h | P1.1.3 |
| P1.3.1 (config) | 30 m | — |
| P1.3.2 (adapter) | 1 h | P1.1.5, P1.2 |
| P1.3.3–P1.3.4 (integration + docs) | 2 h | P1.3.2 |
| **Total** | **~9 hours** | — |
| Phase | Duration | Tasks | Focus |
|-------|----------|-------|-------|
| 1: Detection | 2 days | T1.1–1.4 | Core capability detection |
| 2: Registry | 2 days | T2.1–2.3 | Constraints, matching, fallbacks |
| 3: Dispatch | 2 days | T3.1–3.3 | Orchestrator, integration, CLI |
| 4: MCP | 1 day | T4.1–4.2 | MCP tools, decorators |
| 5: Testing | 2 days | T5.1–5.3 | Unit, integration, multi-platform CI |
| 6: Docs | 1 day | T6.1–6.3 | Guides, reference, architecture |
| 7: Merge | 1 day | T7.1–7.2 | Review, handoff, knowledge transfer |
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Detection overhead | Medium | Low | Cache + lazy detection |
| False tool detection | Low | Medium | Version validation, smoke tests |
| Cross-platform quirks | Medium | Medium | Comprehensive CI matrix |
| Agent adoption friction | Medium | Low | Simple decorator, docs, examples |
| Category | Improvement | Status |
|----------|-------------|--------|
| **Simple operations** (init, cache) | 15-100x | ✅ Phase 1 complete |
| **Git operations** | 7-10x | ✅ Phase 1 complete |
| **Hook execution latency** | 3-4x average | ✅ Phase 1 complete |
| **Agent throughput** | 7-10x | ✅ Phase 1 complete |
| Risk | Impact | Mitigation | Status |
|------|--------|-----------|--------|
| **Breaking changes** | High | Backward compatibility, fallback to shell | ✅ Designed |
| **Git integration issues** | Medium | Extensive testing, fallback to `git` CLI | ✅ Planned for Phase 2 |
| **Cache corruption** | Low | Atomic writes, checksums, validation | ✅ Designed |
| **Cross-platform issues** | Medium | Testing on macOS/Linux/WSL2 | ✅ Validated |
| **Performance regression** | Low | Continuous monitoring, rollback triggers | ✅ Planned |
- [ ] Build release artifacts
- [ ] Run final smoke tests
- [ ] Brief team on rollout procedure
- [ ] Enable monitoring/alerts
| ID | Task | Priority | Status |
|----|------|----------|--------|
| **research-hook-rust-phase2-week1** | Validate Phase 2 with 10% hooks | P1 | Pending |
| **research-hook-rust-phase2-week2** | Expand to 25% hooks, optimize | P1 | Pending |
| **research-hook-rust-phase2-week3** | 50% adoption, deprecation warnings | P1 | Pending |
| **research-hook-rust-phase2-week4** | 100% adoption, make default | P1 | Pending |
| ID | Task | Priority | Status |
|----|------|----------|--------|
| **research-hook-rust-libgit2** | Integrate libgit2 for 8x git speedup | P2 | Pending |
| **research-hook-rust-native-hooks** | Native Rust hooks for critical paths | P2 | Pending |
| **research-hook-rust-monitoring** | Production monitoring & dashboards | P2 | Pending |
- [ ] Phase 2 start date confirmed?
- [ ] Resources allocated (engineer time)?
- [ ] Monitoring infrastructure ready?
- [ ] Team trained on rollout?
| Metric | Value | Status |
|--------|-------|--------|
| **Avg speedup** | 9.2x | ✅ Exceeds target (5x) |
| **Max speedup** | 104x (cache key) | ✅⭐ Outstanding |
| **Min speedup** | 7x (git ops) | ✅ Solid |
| **P95 improvement** | 93% | ✅ Consistent |
| **Regressions** | 0 | ✅ Perfect |
| Deliverable | Status | Notes |
|-------------|--------|-------|
| affected-tests.rs | ✅ COMPLETE | 500+ lines, 17 tests |
| prewarm.rs | ✅ COMPLETE | 400+ lines, 4 tests |
| report.rs | ✅ COMPLETE | 450+ lines, 6 tests |
| lib.rs exports | ✅ COMPLETE | All types exported |
| CLI integration | ⚠️ NEEDS FIX | Type annotation issues in existing code |
| Cargo.toml | ✅ COMPLETE | Added `which` dependency |
| main.rs routing | ⚠️ NEEDS FIX | Affected by compiler issues |
| Documentation | ⏳ BLOCKED | Can't proceed until binary compiles |
| Operation | Before (Sequential) | After (Batch) | Improvement |
|-----------|-------------------|---------------|------------|
| Read 5 files | 5 calls, ~500ms | 1 call, ~50ms | 10x faster, 5x fewer calls |
| Write 5 files | 5 calls, ~600ms | 1 call, ~100ms | 6x faster, 5x fewer calls |
| Edit 5 files | 5 calls, ~800ms | 1 call, ~200ms | 4x faster, 5x fewer calls |
| Delete 5 files | 5 calls, ~400ms | 1 call, ~100ms | 4x faster, 5x fewer calls |
| Field | Type | Env Var | Auto-Detect | Default |
|-------|------|---------|-------------|---------|
| `analytics_site_id` | str | THGENT_ANALYTICS_SITE_ID | No | "thegent" |
| `siem_endpoint_url` | str \| None | THGENT_SIEM_ENDPOINT_URL | No | None |
| `virtual_env` | Path \| None | VIRTUAL_ENV | ✅ Yes | None |
| `shell_path` | str | SHELL | ✅ Yes | "/bin/zsh" |
| `appdata_path` | Path \| None | APPDATA | ✅ Yes | None |
| `cliproxy_backend_url` | str \| None | THGENT_CLIPROXY_BACKEND_URL | No | None |
| `check_leaks` | bool | CHECK_LEAKS | ✅ Yes | False |
| `testing_mode` | bool | THGENT_TESTING | ✅ Yes | False |
| Category | Count |
|----------|-------|
| **Total Files** | 10 |
| **Total Occurrences** | ~30 |
| **Completed Files** | 6 |
| **Completed Occurrences** | 14 |
| **Remaining Files** | 4 |
| **Remaining Occurrences** | 14 |
| **New ThegentSettings Fields** | 8 |
| **Field Validators** | 6 (with auto-detect) |
- [ ] mcp_manage.py updated (2 changes)
- [ ] dex_main.py updated (3 changes)
- [ ] install.py updated (5 changes)
- [ ] start_proxy_with_adapter.py updated (4 changes)
- [ ] Full pytest suite runs without errors
- [ ] Final grep verification: `grep -r "os\.environ\|os\.getenv" src/` returns 0 results (except config.py validators)
| File | Changes | Status |
|------|---------|--------|
| src/thegent/config.py | +8 fields, +6 validators | ✅ DONE |
| src/thegent/planning/auto_launch.py | -2 os.getenv | ✅ DONE |
| conftest.py | -1 env mutation, +1 fixture | ✅ DONE |
| tests/test_unit_config_provider.py | -2 patch.dict → monkeypatch | ✅ DONE |
| tests/test_platform_paths.py | -1 fixture, +4 monkeypatch | ✅ DONE |
| tests/test_resource_leaks.py | reviewed (+else) | ✅ DONE |
| src/thegent/mcp_manage.| S1.1 | Create `src/thegent/secrets/manager.py` using `cryptography` for Fernet symmetric encryption. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| S1.2 | Implement `thegent secrets set <key> <value>` with interactive masked input. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| S1.3 | Implement `thegent secrets get <key>` with auto-copy to clipboard (optional). | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| S1.4 | Add `thegent secrets list` with masked values and metadata (last updated, usage count). | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| S1.5 | Integrate with `keyring` for OS-native secret storage (Keychain/Windows Credential Manager). | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| S1.6 | Implement `thegent secrets export --project` to generate encrypted `.thegent/project_secrets.enc`. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| S1.7 | Add `thegent secrets import --file <path>` to ingest encrypted bundles. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| S1.8 | Implement `SecretSharing` via SSH/GPG: `thegent secrets share <key> --with <github_user>`. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| S1.9 | Add automated secret redaction in all CLI output and logs using `GovernanceScanner`. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| S1.10 | Support "Ghost Credentials": Load secrets into Rust SHM and clear from process environment. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| S2.1 | Harden `OSUserAdapter` with `sudo -n` non-interactive capability reporting. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| S2.2 | Implement `thegent isolation init` to set up persistent isolated users/groups. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| S2.3 | Add `NamespaceManager` for Linux PID/Network namespace isolation. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| S2.4 | Implement `FileSystemSandbox`: Use `mount --bind` and `pivot_root` for per-tenant VFS. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| S2.5 | Add `ResourceQuotas`: Set CPU/Memory limits for agent processes via `cgroups`. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| S2.6 | Implement `NetworkGuard`: Block external egress for agents unless explicitly whitelisted. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| S2.7 | Add `thegent isolation shell <tenant_id>` to enter a tenant's sandbox for debugging. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| S2.8 | Implement `SharedGroup` for multi-agent collaboration within a single isolation boundary. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| S2.9 | Add `ZombieCleanup`: Ensure no leaked processes remain after isolation exit. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| S2.10 | Implement `AuditLedger` per-tenant signed hash chains for tamper-proof evidence. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| H1.1 | Restrict all internal `.sh` hook execution to `dash` (Unix) for 2x faster startup vs `bash`. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| H1.2 | Restrict all internal Windows execution to `cmd.exe /c` where `pwsh` overhead is unnecessary. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| H1.3 | Implement `posix_spawn` wrapper in `thegent.infra` to bypass `fork/exec` overhead. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| H1.4 | Add `THGENT_FAST_SHELL=1` to force `dash/cmd` preference globally. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| H1.5 | Rewrite `stop-dispatcher.sh` logic into `hook-dispatcher` Rust binary. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| H1.6 | Rewrite `quality-gate.sh` logic into `hook-dispatcher` Rust binary. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| H1.7 | Implement "Warm Shell" pool: Keep a few shell processes alive for instant command execution. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| H1.8 | Eliminate shell-outs for environment variable resolution (use Rust `env` introspection). | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| H1.9 | Optimize `PATH` searching in Rust using `OnceLock` and `BTreeSet` for O(log n) lookups. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| H1.10 | Add `thegent shell profile` to identify slow shell scripts in the workspace. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| P1.1 | Port `ThegentSettings` parsing from Pydantic to Rust `serde` for instant CLI boot. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| P1.2 | Implement native `MeshDiscovery` in Rust using `/proc` (Linux) and `ntquery` (Windows). | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| P1.3 | Port `MaildirQueue` logic to Rust for atomic task handling without Python overhead. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| P1.4 | Implement `StateSHM` (Shared Memory) persistence for agent heartbeats in Rust. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| P1.5 | Move `GovernanceScanner` regex engine to Rust `regex` crate with SIMD acceleration. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| P1.6 | Implement `SmartMerge` core in Rust using `tree-sitter` for AST-aware merging. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| P1.7 | Add `thegent-git` native `is_dirty` check using `gitoxide`. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| P1.8 | Optimize `TUI Compositor` render loop in Rust to handle 60fps live updates. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| P1.9 | Use `mimalloc` or `jemalloc` in the Rust binaries for better memory performance. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| P1.10 | Implement binary multi-call (busybox-style) to reduce total binary size. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| R1.1 | Implement `thegent sync init` to link multiple devices via an encrypted backend. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| R1.2 | Add `SyncBackend` for S3/GCS with client-side encryption. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| R1.3 | Implement `thegent sync push/pull` for `.thegent/` metadata and state. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| R1.4 | Add `DeviceRegistry` to track active machines in the mesh. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| R1.5 | Implement `ConflictResolver` for state sync (Last-Write-Wins or Vector Clocks). | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| R1.6 | Add `PeerDiscovery`: Use MDNS/Bonjour for local network device discovery. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| R1.7 | Implement `Tailscale` integration for secure device-to-device tunneling. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| R1.8 | Add `thegent sync watch`: Continuous background sync of workspace state. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| R1.9 | Implement `SharedClipboard` across devices for agent coordination. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| R1.10 | Add `StateDe-duplication`: Avoid syncing large redundant log files. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| R2.1 | Auto-resolve `tenant_id` based on `git remote origin get-url`. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| R2.2 | Support `.thegent/config.yaml` for project-local overrides. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| R2.3 | Implement `ContextIsolation`: Ensure an agent in Project A cannot see files in Project B. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| R2.4 | Add `ProjectDashboard`: View all agents active across all your local projects. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| R2.5 | Implement `CrossProjectBacklog`: Move tasks between projects seamlessly. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| R2.6 | Add `WorkspaceLinking`: Link a "Frontend" and "Backend" project into one logical mesh. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| R2.7 | Implement `SharedPersona`: Allow a custom teammate agent to follow you across projects. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| R2.8 | Add `ProjectRetentionPolicy`: Different log expiry for client projects vs personal. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| R2.9 | Implement `AutoIngest`: Detect a new thegent project and offer to join the mesh. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| R2.10 | Add `thegent project doctor`: Validate project-level coordination settings. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| Q1.1 | Add `rich.progress` to all long-running tasks (`install`, `sync`, `governance`). | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| Q1.2 | Implement `thegent doctor --fix` with interactive auto-remediation. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| Q1.3 | Add "Smart Suggestions" for CLI typos (using Levenshtein distance). | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| Q1.4 | Implement `thegent status --live` (Real-time dashboard using `rich.live`). | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| Q1.5 | Add desktop notifications for task completion (macOS `osascript`, Windows `toaster`). | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| Q1.6 | Implement `thegent logs --follow` with colored, filtered output. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| Q1.7 | Add `thegent search` to instantly find documentation fragments. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| Q1.8 | Implement "Interactive Rebase" for `thegent plan`: Edit the DAG via TUI. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| Q1.9 | Add `thegent explain <run_id>` to get a plain-English summary of an agent run. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| Q1.10 | Support `THGENT_THEME=nord|dracula` for CLI colors. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| Q2.1 | Implement `thegent init` with project templates (Python, Rust, JS). | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| Q2.2 | Add `thegent shell-completion` for Zsh, Bash, Fish, and PowerShell. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| Q2.3 | Create `thegent man` page and auto-generated Markdown CLI reference. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| Q2.4 | Implement `thegent update` (self-updater for binaries and hooks). | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| Q2.5 | Add `thegent bench` to profile agent performance and token usage. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| Q2.6 | Implement `thegent feedback` (Collect system info and open GitHub issue). | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| Q2.7 | Add `thegent aliases`: Create custom shortcuts for common command patterns. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| Q2.8 | Implement `thegent template`: Create new teammate agents from blueprints. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| Q2.9 | Add `thegent history`: Search and replay previous CLI commands. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| Q2.10 | Support `thegent config edit` (Open default editor for settings). | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| F1.1 | **Consensus**: Implement `WeightedVoting` algorithm in `src/thegent/mesh/consensus.py`. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| F1.2 | **Consensus**: Add `MajorityVote` fallback for quick agent alignment. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| F1.3 | **Compliance**: Implement `AuditReportGenerator` (Markdown/PDF output). | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| F1.4 | **Compliance**: Add `SLA_Monitor` to track agent response times. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| F1.5 | **Federation**: Implement `NamespaceRegistry` for multi-org policy sharing. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| F1.6 | **Federation**: Add `CrossOrgSync` via secure HTTP relay. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| F1.7 | **Learning**: Implement `ModelPerformanceTracker`: Record pass/fail rates per model. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| F1.8 | **Learning**: Add `AutoPromote`: Switch models when a cheaper one hits >95% parity. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| F1.9 | **Finance**: Implement `TokenQuotaManager` with daily/monthly limits. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| F1.10 | **Finance**: Add `CostProjection` to estimate the cost of a full DAG run. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| F1.11 | **Forensics**: Implement `EnvironmentSnapshot` (Captures process list, open files). | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| F1.12 | **Forensics**: Add `TraceDiff`: Compare two agent runs to find where they diverged. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| F1.13 | **Inbox**: Implement `HumanInTheLoop` (HITL) prompt for high-risk actions. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| F1.14 | **Inbox**: Add `ApprovalQueue` for batch-approving agent tasks. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| F1.15 | **Recovery**: Implement `DagResume`: Start from the last successful node in a DAG. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| F1.16 | **Recovery**: Add `AutoRemediate`: Attempt known fixes for common environment errors. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| F1.17 | **Project**: Implement `MeshBridge`: Link two local meshes via filesystem sockets. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| F1.18 | **Project**: Add `DependencyScanner`: Detect project-to-project task dependencies. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| F1.19 | **Control Plane**: Fully implement `ThegentSettings` validation against JSON Schema. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
| F1.20 | **Main**: Final cleanup of all unused or deprecated CLI flags and apps. | POLISH_OPTIMIZE_QOL_PLAN_2026_02_19.md | P2 | - |
