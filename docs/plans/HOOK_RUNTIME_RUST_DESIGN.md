# Hook Runtime: Full Rust Migration Design (Deep & Wide)

**Status:** Design  
**Scope:** Replace `hooks/lib/common.sh` and its sourced layers with a Rust binary + library.  
**Goals:** Performance, DX, AX, UX; effort and risk accepted.  
**See also:** [FULL_SHELL_TO_RUST_WHERE_BENEFICIAL.md](./FULL_SHELL_TO_RUST_WHERE_BENEFICIAL.md) for full shell inventory and phased migration.

---

## 1. Current State Summary

### 1.1 What Runs Today

- **Claude/Cursor** invokes hooks by event (SessionStart, PreToolUse, PostToolUse, Stop, etc.).
- **Invocation chain:**
  - Either **hook-dispatcher** (Rust) reads stdin JSON → builds env → spawns `bash hook.sh` for each hook, **or**
  - Shell dispatchers (e.g. `posttool-dispatcher.sh`) source `lib/common.sh` once, then `source` each hook script in a subshell.
- Every **hook script** that runs either:
  - Gets env from the Rust dispatcher (no common.sh in that process), or
  - Is run by a shell dispatcher that already sourced common.sh; the hook script itself may `source` common.sh again or rely on inherited env.

So today we have:
- **hook-dispatcher** (Rust): orchestration, env build, timeout, skip list, native prompt-submit + governance scan.
- **common.sh** (~1685 lines): init (stdin JSON → env), tool overrides (jq/grep/find), git-cache + git-wrapper, cache key/hash, shared changed files, circuit breaker, debounce, incremental, config, learning, prewarm, progress, report writers, affected-tests, etc.
- **git-cache.sh** / **git-wrapper.sh**: TTL cache for read-only git, agent passthrough, index.lock multi-tenant wait.
- **fd-wrapper.sh**, **grep-wrapper.sh**, **procs-wrapper.sh**, **builtin-wrapper.sh**, **pkg-wrapper.sh**: optional accelerators (fd/rg/procs).

### 1.2 Pain Points

- Any code path that **sources** common.sh pays for the whole stack (1600+ lines + 7 files). We removed that from the git **shim**; dispatcher-run hooks still run bash scripts that may source common.sh (e.g. when dispatcher runs `bash quality-gate.sh`, that script sources common.sh).
- Multiple chats/agents → many hook runs → repeated git/cache/hash work and shell startup cost.
- Hook logic is split across shell and Rust (dispatcher); no single place for caching, git, or config that is both fast and consistent.

---

## 2. Target Architecture

### 2.1 Single Binary: `thegent-hooks`

One Rust binary (and optionally a library crate for reuse) that provides **all** behavior today in common.sh + git-cache + git-wrapper + config + cache + prewarm, and that can **run** hook “actions” (either by invoking a tiny shell stub or by native implementation).

- **Name:** `thegent-hooks` (or keep `hook-dispatcher` and grow it).
- **Location:** `hooks/hook-dispatcher/` (extend existing) or new `crates/thegent-hooks/` + workspace member.
- **Output:** CLI subcommands; hooks call the binary instead of sourcing shell.

### 2.2 Subcommands (Surface Area)

Subcommands map 1:1 to the current common.sh + helpers surface, so hooks can be migrated incrementally.

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

Existing **hook-dispatcher** modes (pretool, posttool, stop, sessionstart, …) stay; they already build env and run scripts. The new surface allows each **script** to call `thegent-hooks <subcommand>` instead of sourcing common.sh and calling shell functions.

### 2.3 Git Layer in Rust

- **Cached read-only:** For `diff --name-only HEAD`, `status`, `rev-parse`, `ls-files`, etc., use a TTL cache (in-memory or file-based keyed by (cwd, cmd, HEAD, .git/config mtime)). On miss, run git (or libgit2/gix) and store result.
- **Agent passthrough:** If first argument is codex|copilot|dex|claude|cursor, exec the agent binary with rest of args (do not call git).
- **Write path:** For add/commit/checkout/..., wait for `.git/index.lock` (with timeout and stale-lock steal), then run git. Invalidate cache for write commands.
- **Binary:** Prefer **gix** (gitoxide) for read-only where possible (status, diff, rev-parse) for speed; fallback to `std::process::Command::new("git")` for compatibility.

### 2.4 Init Contract

- **Stdin:** JSON with `tool_name`, `tool_input`, `session_id`, `cwd`, `project_dir`, `stop_hook_active`, etc.
- **Output (init):** Either:
  - **Env file:** NUL-delimited or `KEY=VALUE` lines so shell can `source` or `export`; or
  - **Exec mode:** `thegent-hooks init --exec -- <child argv...>` which sets env and exec’s the child (no shell).
- **PROJECT_DIR resolution:** Same as today: cwd → git rev-parse --show-toplevel → script path heuristics (.claude/hooks) → pwd → HOME. Implement in Rust once.

### 2.5 Cache and Shared Dirs

- **HOOK_CACHE_DIR:** `$TMPDIR/claude-hook-cache-$UID` (or equivalent on Windows).
- **Shared dir:** `$HOOK_CACHE_DIR/shared` (changed_files, fr_ids, fr_index, arbitrary blobs).
- **Cache key:** Hash of (hook_name, head_sha, changed_files). Use fast hash (e.g. blake3) for keys; no need for cryptographic strength.
- **File hash:** For content-addressable cache, use blake3 or sha256 of file contents; optional mtime-based cache to avoid re-read.

### 2.6 Config

- **hook-config.yaml** lookup: hooks_dir parent, then PROJECT_DIR/.claude/hooks/hook-config.yaml. Parse YAML in Rust (serde_yaml); expose `config-get <key>` and `config-true <key>`.
- **qa-local.json** for skip list: PROJECT_DIR/.claude/qa-local.json, key `hooks.skip[]`.

### 2.7 Hook Execution Model (After Migration)

- **Option A – Thin shell:** Hook script is a small sh script that calls `thegent-hooks init` (or gets env from dispatcher), then calls `thegent-hooks cache-key`, `thegent-hooks cache-check`, `thegent-hooks git`, `thegent-hooks changed-files`, etc., and uses the results to decide what to run (e.g. ruff, pytest). No sourcing of common.sh.
- **Option B – Dispatcher runs Rust “hook runner”:** Dispatcher no longer spawns `bash hook.sh`. It calls `thegent-hooks run-hook quality-gate` with env. The Rust binary does cache check, changed-files, should-run, then either runs a **native** implementation of the hook (e.g. quality-gate = run ruff/semgrep/...) or spawns a **minimal** script that only contains the hook’s specific logic (and gets env from thegent-hooks). Option B is larger scope but gives maximum performance and one place for all policy.

Recommendation: **Phase 1 = Option A** (thin shell calling thegent-hooks). Phase 2 = optionally move hot hooks (quality-gate, security-pipeline, test-maturity) into Rust “run-hook” implementations.

---

## 3. Crate Layout

### 3.1 Workspace

- Add **thegent-hooks** (or rename/expand **hook-dispatcher**) under `crates/thegent-hooks` or keep under `hooks/hook-dispatcher`.
- If under crates/, depend on existing **thegent-git** (libgit2) for rev-parse, status, diff where we want native speed; and add **gix** for optional gitoxide path. thegent-hooks can remain a single binary crate with modules.

### 3.2 Suggested Modules (Rust)

- **cli** – Subcommands and argument parsing (clap).
- **init** – Stdin JSON parsing, PROJECT_DIR resolution, env build (align with hook-dispatcher’s `build_env` and common.sh’s hook_init_full).
- **cache** – Cache key (hash), check, read, write; shared dir (changed_files, blobs).
- **git** – Cached git, agent passthrough, lock wait; use thegent-git or gix for read-only.
- **config** – hook-config.yaml and qa-local.json read.
- **hash** – Content hashing (blake3/sha2), file-hash cache.
- **prewarm** – Prewarm shared data, ruff, shellcheck (spawn processes or write cache entries).
- **reports** – Write pass/fail/na JSON to VERIFY_DIR.
- **learning** – Learning-based skip (append to history, compute pass rate).
- **affected** – Affected-tests logic (pattern, coverage index, import-based for Python).
- **dispatcher** – Existing mode dispatch (pretool, posttool, stop, …) and run_hook; can stay in current hook-dispatcher and call into thegent-hooks lib for env/cache/git, or merge into thegent-hooks.

### 3.3 Dependencies (Cargo.toml)

- **serde**, **serde_json** – JSON.
- **serde_yaml** – hook-config.yaml.
- **clap** – CLI.
- **blake3** (or **sha2**) – Fast hashing for cache keys and file hashes.
- **git2** or **gix** – Git (reuse thegent-git or add gix for gitoxide).
- **regex** – Pattern matching for should-run, FR ids, etc.
- **directories** – Cache dir (e.g. `directories::ProjectDirs` or env TMPDIR).
- **anyhow** / **thiserror** – Errors.
- **tracing** – Logging (optional, for debug).

---

## 4. Data Structures and Contracts

### 4.1 Hook Input (Stdin JSON)

Mirror current schema (tool_name, tool_input.file_path, tool_input.content, session_id, cwd, stop_hook_active, etc.). Deserialize in Rust; use for init and for any subcommand that needs project/context.

### 4.2 Env Output (init)

Format suitable for shell: either

- `KEY=value` per line (escape newlines in value), or
- NUL-delimited `key\0value` for safe parsing.

Include all of: INPUT, CWD, SESSION_ID, TOOL_NAME, FILE_PATH, STOP_ACTIVE, PROJECT_DIR, VERIFY_DIR, QA_STATE, QUALITY_CONFIG, CHANGE_LOG, TOOL_CONTENT, TOOL_NEW_STRING, TOOL_OLD_STRING, HEAD_SHA, CHANGED_FILES (if precomputed), HOOK_CACHE_DIR, HOOK_SHARED_DIR, JQ_CMD, RG_CMD, FD_CMD, HASH_CMD, START_TIMESTAMP, HOOKS_DIR, HOOK_MODE, _HOOK_DISPATCHED, etc.

### 4.3 Cache Key

Input: hook name, optional extra key material.  
Internal: resolve HEAD_SHA and changed files list (from git or env); compute hash(hook_name, head_sha, changed_files[, extra]).  
Output: stable string key (e.g. hex) for cache file names.

### 4.4 Git Cached

Input: argv (e.g. `diff --name-only HEAD`).  
Behavior: if read-only command and cache hit (keyed by cwd + argv + HEAD + config mtime), return cached stdout and exit code; else run git (or gix), store result, return.  
Output: stdout of git; exit code = git exit code.

### 4.5 Changed Files

Input: project dir (and optional env CHANGED_FILES).  
Behavior: if shared file exists and fresh, return its contents; else compute `git diff --name-only HEAD` + `git ls-files --others --exclude-standard`, filter (node_modules, .git, …), sort -u, write to shared, return.  
Output: one path per line.

---

## 5. Migration Strategy

### 5.1 Phase 0 – Crate and CLI Skeleton

- New crate `thegent-hooks` (or extend hook-dispatcher) with clap subcommands: `init`, `cache-key`, `cache-check`, `cache-read`, `cache-write`, `git`, `changed-files`, `config-get`, `skip`, etc. Each subcommand can stub (e.g. call back to shell or return “not implemented”) so that the CLI surface is fixed early.

### 5.2 Phase 1 – Core in Rust

- **init:** Parse stdin JSON, resolve PROJECT_DIR (git + heuristics), compute VERIFY_DIR, QA_STATE, QUALITY_CONFIG, CHANGE_LOG, export list. Output env for shell.
- **cache-key / hash:** Blake3 of (hook_name, head_sha, changed_files). No jq/shasum.
- **cache-check / cache-read / cache-write:** File-based under HOOK_CACHE_DIR.
- **git:** Cached read-only (TTL file cache); agent passthrough (exec); write path with index.lock wait and steal. Use thegent-git or Command::new("git") for execution.
- **changed-files:** Build shared list; use git in Rust or subprocess; write to shared file, return contents.
- **config-get:** Read hook-config.yaml and qa-local.json; return value or true/false for config-true.

Hooks are then updated one-by-one to call `thegent-hooks init` (or rely on dispatcher env) and `thegent-hooks cache-key`, `thegent-hooks git`, etc., instead of sourcing common.sh. Shell scripts become thin wrappers.

### 5.3 Phase 2 – Should-Run, Breaker, Debounce, Incremental, Learning

- **should-run:** Changed files (from Rust) + regex pattern → exit 0/1.
- **breaker-check / record / reset:** File-based state under HOOK_CACHE_DIR/breakers.
- **debounce:** File-based pending list + flock; leader waits window, returns batch; follower exits 1.
- **incremental-check / record:** Manifest file (path:hash per line); check all paths unchanged.
- **learning-record / learning-should-skip:** Append to history; compute pass rate for (hook, pattern); return skip or run.

### 5.4 Phase 3 – FR Index, Affected Tests, Prewarm, Reports

- **fr-ids:** Parse FUNCTIONAL_REQUIREMENTS.md with regex; cache under shared.
- **fr-index:** Walk test dirs, grep FR-* (use rg or Rust regex); write shared file.
- **affected-tests:** Implement pattern-based (e.g. test_*.py for src/module.py), coverage-index read, import-based for Python; return list of test paths.
- **prewarm:** Spawn background tasks for shared changed_files, ruff cache, shellcheck dirs (or equivalent); wait or fire-and-forget.
- **report:** Write JSON to VERIFY_DIR for pass/fail/na.

### 5.5 Phase 4 – Optional Native Hook Implementations

- Implement **run-hook quality-gate** (and similar) in Rust: run ruff, semgrep, etc. via std::process or a task runner; respect timeout and config. Then dispatcher can call `thegent-hooks run-hook quality-gate` instead of `bash quality-gate.sh`. Remaining shell hooks stay as thin scripts that call thegent-hooks for everything else.

### 5.6 Deprecation of common.sh

- Once all hooks use thegent-hooks for init, cache, git, changed-files, config, and thegent-hooks is the single source of truth, mark common.sh and git-cache.sh / git-wrapper.sh as deprecated. Keep them only as fallback for environments where thegent-hooks is not installed, or remove once no caller remains.

---

## 6. Testing Strategy

- **Unit:** Each module (cache, git, config, hash, init) with temp dirs and mock git/repos.
- **Integration:** Run `thegent-hooks init` with JSON stdin; run cache-key, cache-check, cache-write, cache-read; run git diff; run changed-files in a real repo.
- **Compatibility:** Compare output of thegent-hooks cache-key vs shell hook_cache_key for same repo state; compare changed-files vs hook_shared_changed_files; compare init env vs hook_init_full export list.
- **Regression:** Existing hook-dispatcher tests (if any) and existing hook tests (e.g. test_maturity, quality_gate) should pass when hooks are switched to thegent-hooks.

---

## 7. Error Handling and Logging

- **Stderr:** Human-readable errors; exit codes: 0 = success, 1 = generic error, 2 = skip/sentinel where needed (e.g. TeammateIdle), 124 = timeout.
- **Logging:** Use `tracing` with env filter (e.g. RUST_LOG=thegent_hooks=debug) so production stays quiet; debug_timing in hook-config can enable more verbose output.
- **No secret logging:** Redact API keys and tokens in any logged env or input.

---

## 8. Performance Targets

- **init:** &lt; 5 ms (JSON parse + PROJECT_DIR from git or cache).
- **cache-key:** &lt; 2 ms (hash of small strings; head_sha and changed_files from env or one git call).
- **git cached (hit):** &lt; 1 ms (read from file).
- **git cached (miss):** One git (or gix) invocation; aim &lt; 50 ms for status/diff in typical repo.
- **changed-files (hit):** &lt; 1 ms (read shared file).
- **changed-files (miss):** One git diff + ls-files; aim &lt; 100 ms.

---

## 9. File and Dir Summary

| Concept | Current (shell) | Rust |
|--------|------------------|------|
| Cache root | HOOK_CACHE_DIR = $TMPDIR/claude-hook-cache-$UID | Same (env or directories crate) |
| Shared dir | HOOK_CACHE_DIR/shared | Same |
| Cache entry | HOOK_CACHE_DIR/{key}.out, .rc | Same |
| Git cache | GIT_CACHE_DIR (e.g. .git-cache) or project-local | File cache under HOOK_CACHE_DIR/git or per-repo |
| Config | hook-config.yaml, qa-local.json | Read via config module |
| Breakers | HOOK_CACHE_DIR/breakers | Same |
| Learning | HOOK_CACHE_DIR/learning/history.log | Same |

---

## 10. Summary

- **Full migration** of common.sh to Rust is done by implementing a **single binary** (`thegent-hooks`) with subcommands that cover every current shell function (init, cache, git, changed-files, config, breaker, debounce, incremental, learning, prewarm, reports, affected-tests). Hooks become thin callers of this binary; no more sourcing 1600+ lines of shell.
- **Deep:** Git layer uses cache + optional gix; init and cache key are native; config and skip list are parsed once in Rust.
- **Wide:** All hook helpers and hook-config.yaml semantics are in scope; dispatcher can keep running bash scripts that call thegent-hooks, or later call `thegent-hooks run-hook <name>` for native implementations.
- **Phased:** Phase 0 = CLI skeleton; Phase 1 = init, cache, git, changed-files, config; Phase 2 = should-run, breaker, debounce, incremental, learning; Phase 3 = FR index, affected-tests, prewarm, reports; Phase 4 = optional native run-hook. Deprecate common.sh when no caller remains.

This design gives a single, fast, testable hook runtime in Rust while preserving the current contract (stdin JSON, env, cache, git, config) and enabling incremental migration and better performance and DX/AX/UX.
