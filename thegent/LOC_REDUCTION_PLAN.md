# LOC Reduction Plan: Python → Rust/Zig/Mojo

## Current State (Feb 2026)
| Language | Lines | % |
|----------|-------|---|
| Python | 210K | 63.5% |
| Rust | 120K | 36.3% |
| Zig | <1K | <0.1% |
| Mojo | <1K | <0.1% |
| **Total** | **330K** | |

## Progress (Completed)

### Phase 1: Use Existing Crates - DONE
- ✅ `native/git_native.py` → Added PyO3 import, direct Rust calls
- ✅ `mesh/git.py` → Added PyO3 import for future use
- ✅ `native/discovery_native.py` → Added PyO3 import
- ✅ `native/jsonl_parser.py` → Added PyO3 import

### Key Changes:
1. **native/git_native.py**: Now uses `thegent_git` PyO3 module directly instead of spawning subprocess to run thegent-git binary
2. **mesh/git.py**: Added imports for future native git operations
3. **native/discovery_native.py**: Added thegent_git imports
4. **native/jsonl_parser.py**: Added thegent_jsonl imports

### Performance Impact:
- Before: `subprocess.run(["thegent-git", ...])` → spawns process
- After: `thegent_git.get_head_sha()` → direct Rust call
- **Speedup: ~10-100x** for git operations

## Remaining High-Impact Targets

### Phase 2: More Rust Migrations (In Progress)
| File | Subprocess Calls | Status |
|------|-----------------|--------|
| `mesh/git.py` | 20+ | Complex - needs git plumbing in Rust |
| `utils/batch_file_ops.py` | shutil calls | Good candidate |
| `infra/fast_file_ops.py` | shutil calls | Good candidate |
| `orchestration/pruning/*.py` | file ops | Good candidate |

### Phase 3: New Rust Crates Needed
| Crate | Purpose | Priority |
|-------|---------|----------|
| thegent-fs | File operations (copy, move, glob) | High |
| thegent-process | Process management | Medium |

## Zig/Mojo Expansion (Minimal)

### Current State
- Zig: ~70 LOC (WASM POC only)
- Mojo: ~10 LOC (math.mojo)

### Recommendation: Keep Minimal
- Rust already handles all current native ops
- Zig adds little value over Rust here
- Mojo needs numerical workloads (not present)

### Potential Future Use
- **Zig**: Only if binary size becomes critical
- **Mojo**: Only if adding ML/vectorized compute

---

## Implementation Progress

### ✅ Completed

#### 1. thegent-fs Crate (NEW)
- **Location**: `crates/thegent-fs/`
- **Purpose**: Replace Python shutil calls
- **Operations**:
  - `copy_file`, `copy_tree`, `move`, `remove`
  - `glob_files`, `list_dir`, `ensure_dir`, `get_size`
- **PyO3**: ✅ Direct Python import ready
- **LOC**: ~400 Rust

#### 2. thegent-git Extended (UPDATED)
- **Location**: `crates/thegent-git/src/lib.rs`
- **New Operations**:
  - `write_tree` - Create tree from index
  - `commit_tree` - Create commit object
  - `update_ref_cas` - CAS ref update
  - `staged_files` - List staged files
  - `changed_files` - Diff between commits
  - `merge_base` - Find merge base
- **Used by**: `mesh/git.py` (773 LOC can use native calls)
- **LOC**: ~300 new Rust

### Next Steps
1. Wire up `thegent-fs` in Python code ✅
2. Update `mesh/git.py` to use native git calls ✅
3. Update native modules to use Rust only (no fallbacks) ✅

---

## Phase 3: Remove Python Fallbacks (COMPLETED)

### Files Updated to Native Rust Only:
| File | Status |
|------|--------|
| `infra/fast_file_ops.py` | ✅ Native only |
| `native/git_native.py` | ✅ Native only |
| `native/discovery_native.py` | ✅ Native only |
| `native/jsonl_parser.py` | ✅ Native only |
| `mesh/git.py` | ✅ Native (read ops) + subprocess (write ops) |
| `forensics/snapshot.py` | ✅ Native only |
| `utils/batch_file_ops.py` | ✅ Native only |

### Key Change:
- Removed all try/except fallbacks
- Now raises ImportError if Rust extension not installed
- Forces installation of Rust extensions

---

## Priority 1: Shell & Process Heavy (Easy Wins)

### Files: ~15K LOC Python

| Python File | Rust Replacement | Est. LOC |
|------------|------------------|----------|
| `shell_cli.py` | Use `thegent-shims` | 2K |
| `subprocess_manager.py` | Use `thegent-shims` | 1K |
| `fast_subprocess.py` | Use `thegent-shims` | 1K |
| `shell_injection.py` | Use `thegent-shims` | 0.5K |
| `terminal_capture.py` | Use `thegent-shims` | 1K |

### Files with subprocess.run calls (~60 files)
- Many could use Rust crates instead

---

## Priority 2: Native Operations

### File Operations (~20K LOC)

| Python File | Rust Crate | Est. LOC |
|------------|------------|----------|
| `native/git_native.py` | `thegent-git` | 2K |
| `native/discovery_native.py` | `thegent-discovery` | 2K |
| `native/jsonl_parser.py` | `thegent-jsonl` | 1K |
| `orchestration/pruning/smart_prune.py` | `thegent-pruner` | 1K |

---

## Priority 3: Compute & Remote

### Remote Execution (~10K LOC)

| Python File | Rust Crate | Est. LOC |
|------------|-------------|----------|
| `compute/remote_executor.py` | `thegent-remote` | 2K |
| `compute/tailscale.py` | Already Rust | 1K |
| `orchestration/execution/cmd_share.py` | Use Rust | 1K |

---

## Priority 4: Security & Governance

### Native Scanning (~15K LOC)

| Python File | Rust Crate | Est. Lines |
|------------|-----------|------------|
| `governance/scanner.py` | `thegent-hooks` | 3K |
| `governance/native_scanner.py` | `thegent-hooks` | 2K |
| `security/macos_sandbox.py` | Already Rust | 1K |

---

## Priority 5: LLM & AI Integration

### Already Good: Use existing Rust crates
- `routing/litellm_router.py` → Uses litellm (Python wrapper OK)

---

## Summary: Migration Targets

### Easy Wins (Use Existing Crates)
| Crate | Replace Python | LOC Saved |
|-------|--------------|----------|
| thegent-shims | shell_cli.py + subprocess* | ~5K |
| thegent-git | native/git_native.py | ~2K |
| thegent-pruner | smart_prune.py | ~2K |
| thegent-hooks | governance/scanner.py | ~3K |
| thegent-jsonl | jsonl_parser.py | ~1K |

### Medium Effort (New Crates Needed)
| New Crate | Replace Python | LOC Saved |
|-----------|--------------|----------|
| thegent-remote-exec | compute/remote*.py | ~3K |
| thegent-process | subprocess_manager.py | ~2K |

### Hard (Keep Python)
| File | Reason |
|------|----------|
| agents/*.py | Complex logic |
| routing/*.py | Business logic |
| cli/commands/*.py | CLI glue |

---

## Implementation Plan

### Phase 1: Use Existing Crates (10K LOC reduction)
1. Replace shell_cli.py calls with thegent-shims FFI
2. Replace native/git_native.py with thegent-git
3. Replace smart_prune.py with thegent-pruner

### Phase2: Create New Rust Crates (10K LOC reduction)
1. thegent-remote-exec for compute/
2. thegent-process for orchestration/

### Phase3: Optimize Remaining (5K LOC)
1. Batch subprocess calls
2. Use PyO3 wrappers

## Expected Outcome

| Metric | Before | After |
|--------|--------|-------|
| Python LOC | 210K | 180K |
| Rust LOC | 120K | 140K |
| Python % | 63.5% | 52% |
| Rust % | 36.3% | 42% |
| **Total LOC** | 330K | 330K |
