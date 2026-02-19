# Process and Tool Optimization Plan

> **Status**: Draft | **Version**: 1.0 | **Generated**: 2026-02-15
> **Goal**: Optimize process footprint, enable multi-tenant execution, and maximize tool efficiency.

---

## 1. Problem Statement
Current sessions exhibit significant process bloat, with dozens of short-lived `bash`, `node`, `python`, and `task` processes. This leads to high context-switch overhead, memory fragmentation, and risk of process leakage.

### Redundant Processes Detected:
- **Redundant MCPs**: `context7-mcp` (superseded by `octocode`).
- **Short-lived Shell Tools**: `cat`, `tr`, `cp`, `dirname`, `basename`, `perl`.
- **Duplicate Node Instances**: Multiple `npm exec` calls for different MCP servers.
- **Process Sprawl**: 64+ `bash` processes, 9+ `task` processes in a single session.
- **Per-CC full stack**: Each Claude Code instance spawns python, clangd, gopls (×2), uv, sourcekit-lsp, rust-analyzer, caffeinate. Closing tab terminates all. **Multi-project × multi-tenant** = N× duplication.

---

## 2. Optimization Streams

### 2.1 Multi-Tenant Single Process (MTSP)
Instead of spawning isolated processes for each agent or tool, `thegent` will move towards a shared execution environment.

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

### 2.2 Efficient Tool Migration
Replace expensive shell-outs with efficient Rust-based or internal Python equivalents.

| Current Tool | Optimized Alternative | Benefit |
|--------------|-----------------------|---------|
| `grep`       | `rg` (Ripgrep)        | 10x faster, better regex. |
| `find`       | `fd`                  | Native speed, cleaner syntax. |
| `jq`         | `jaq`                 | Rust-based, no process overhead if linked. |
| `cat` / `tr` | Python `read()` / `replace()` | Zero process spawn overhead. |
| `sleep`      | `asyncio.sleep()`     | Non-blocking, single-thread. |
| `bash` (N)   | `hook-dispatcher` (Rust) | Consolidates N bash scripts into 1 process. |
| `date`       | `datetime.now()`      | Eliminated 100% of date-related subprocesses. |

### 2.3 Persistence & Resilience
To solve the "Terminating this tab kills processes" issue:
- **Service Management**: Promote `thegent mcp service install` (launchd/systemd) as the primary mode for production work.
- **Daemonization**: Ensure all background tasks use `process-compose` with `is_daemon: true` and are detached from the TTY.
- **Session Continuity**: Map `thegent` sessions to persistent state IDs so they can be re-attached after terminal crashes.

---

## 3. Implementation Roadmap

### Phase 1: Immediate Efficiency (Today)
- [x] Eliminate redundant `date` subprocesses in `sharecli_bridge.py`.
- [x] Consolidate MCP configurations in `mcp_server.py`.
- [x] Mount `sequential-thinking` and `next-devtools` within `thegent serve`.
- [x] Port trivial shell hooks to Rust in `hook-dispatcher`.
- [x] Consolidate hook-dispatcher PostToolUse hooks into combined execution.
- [x] **Global Command Accelerators**: Migrated `grep/find/jq/wc/tr/date` to faster replacements via `common.sh`.
- [x] **Consolidated Server**: Unified `process-compose` into a single process tree.
- [x] **MTSP-09: Multi-Tenant Git Accelerator**: Automated lock coordination in `common.sh`.
- [x] **MTSP-11: Edit Leasing Manager**: Advisory file-level leasing in MCP.
- [x] **MTSP-12: Shadow Clone Logic**: Isolated planning via `git worktree`.
- [x] **MTSP-15: Package Manager Mutexing**: Coordinated `uv`/`npm` sync/install.
- [x] **MTSP-17: Dual Memory Audit System**: Add-only observation log + synthesis.
- [x] **MTSP-18: Session History Scraper**: Automatic prompt/intent collection.
- [ ] Implement persistent LSP Multiplexing for Serena (MTSP-04).
- [ ] Migrate remaining `cat/tr/cp` usage in `hooks/` to internal logic.
- [x] Deprecate standalone `npm exec` processes by bundling tools.

### Phase 2: Structural Depth (Next)
- [x] **MTSP-06: Persistent Python Worker Pool**: Reduce interpreter startup latency by 100%. (Implemented in `src/thegent/orchestration/worker_pool.py` and `mcp_server.py`)
- [x] **MTSP-07: In-Process Tool Execution**: Port CLI commands to library calls. (Largely done with RunRegistry SQLite migration)
- [x] **MTSP-08: Rust Governance Scanner**: Native 8-dimension codebase scanning. (Implemented in `hook-dispatcher`)
- [ ] **MTSP-11: Edit Leasing Manager**: Integrated into `thegent serve`.
- [ ] **MTSP-12: Shadow Clone Logic**: Implementation in `src/thegent/orchestration/shadow.py`.
- [ ] **State-SHM**: Move XP and CircuitBreaker state to memory-mapped files.
- [ ] **Global Watcher**: Single Rust-based watcher for multi-tenant project roots.
- [x] **SQLite WAL Migration**: Consolidate `.jsonl` state into an optimized local DB.

### Phase 3: Total MTSP
- [ ] Full ACE-style dual-loop integration (In-process agents).
- [ ] Native Rust rewrite of critical path shell hooks (Quality Gates).
- [ ] **Kernel-Level Persistence**: Use macOS/Linux native APIs for agent throttling protection.

### 2.4 Python Frontmatter + Native Backmatter (BKM)
See [PYTHON_FRONTMATTER_NATIVE_BACKMATTER_AUDIT_PLAN](../research/PYTHON_FRONTMATTER_NATIVE_BACKMATTER_AUDIT_PLAN.md).

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

**Usage**: `THGENT_USE_NATIVE_RESOURCES=1` for load_based_limits; `THGENT_USE_NATIVE_CRYPTO=1` for signatures. Run `task build:rust` to build crates.

---

## 4. Verification Metrics
- **Process Count**: Target < 10 persistent processes per session.
- **Latency**: Reduce hook overhead by > 50%.
- **Stability**: Eliminate "tab termination" side effects by using persistent daemons.

---

## See also

- [WORK_STREAM.md](../reference/WORK_STREAM.md) — canonical backlog
- [00-MASTER-INDEX.md](./00-MASTER-INDEX.md) — plan index
- [FULL_SHELL_TO_RUST_WHERE_BENEFICIAL.md](./FULL_SHELL_TO_RUST_WHERE_BENEFICIAL.md) — shell → Rust (thegent-shims, hook runtime)
- [PYTHON_FRONTMATTER_NATIVE_BACKMATTER_AUDIT_PLAN.md](../research/PYTHON_FRONTMATTER_NATIVE_BACKMATTER_AUDIT_PLAN.md) — BKM tasks
