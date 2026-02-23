# Rust/Zig Migration Plan - Realistic Assessment

## Target: Reduce Python from 685K → 300K LOC

> **Assessment (Feb 2026):** The P0 candidates (execution.py, workstream_autosync.py) are 
> heavily integrated with Python-specific libraries (pydantic, httpx, asyncio) and are 
> business logic, not compute-intensive operations. Direct migration is not practical.

## What Already Exists in Rust (39K LOC)
- thegent-runtime: Unified tool shims (find, grep, git, cat, ls, du, node, npm, pip)
- thegent-cache: Caching layer
- thegent-fs: Filesystem operations
- thegent-git: Git integration
- thegent-hooks: Hook system
- thegent-crypto: Cryptographic utilities

## Realistic Migration Candidates

| Module | Python LOC | Rust Crate | Viability |
|--------|-----------|------------|-----------|
| execution_hash_helpers.py | ~20 | thegent-utils | ✅ Already simple |
| execution_coercion_helpers.py | ~50 | thegent-utils | ✅ Already simple |
| execution_run_scan_helpers.py | ~150 | thegent-utils | Medium |

## Practical Approach

### 1. Keep Python for Business Logic
The large Python files (execution.py, workstream_autosync.py) are:
- Heavy on Python async/httpx/pydantic
- Deeply integrated with thegent Python modules
- Business logic (metadata, sync) not compute (hashing, parsing)

### 2. Expand Cliproxy Package
Pure functions that don't need Python dependencies can be moved to cliproxy:
- Data transformation utilities
- String/text processing
- Validation helpers

### 3. Existing Rust Coverage is Good
Thegent-runtime already handles the expensive tool invocations:
- grep → rg with caching
- find → fd with indexing
- git read-only operations with caching
- bun/npm/pip/uv routing
