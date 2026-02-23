# Mojo + Zig Stack Audit and Optimization Plan (2026-02-20)

## 1. Objective

Move Mojo and Zig from partial/POC usage into production-grade accelerators with clear ownership, measurable performance targets, and low operational friction.

## 2. Current-State Audit

### Mojo

- Active integration exists via `src/thegent/infra/mojo_bridge.py`:
  - Availability detection, version check, script execution, compile hook, task dispatch.
- Current Mojo code is minimal:
  - `src/thegent/infra/mojo/math.mojo` contains only a simple scoring function + placeholder JSON output.
- Runtime diagnostics already include Mojo checks:
  - `src/thegent/infra/multi_runtime_diagnostics.py`.
- Test coverage exists, but mostly bridge-level behavior:
  - `tests/test_unit_mojo_bridge.py`.

#### Mojo Gaps

- No production workload currently offloaded to Mojo.
- No benchmarked before/after path for latency or CPU cost.
- No module registry/versioning for deployed Mojo kernels.
- No CI gate to validate Mojo availability and fallback behavior quality.

### Zig

- Zig is used in two narrow surfaces:
  - POC interop: `src/thegent/abi/zig_rust_poc/main.zig` (+ `build.rs` + Cargo wrapper).
  - Utility script: `scripts/max_lines_gate.zig`.
- Additional Zig files exist under `crates/thegent-wasm-tools/src/*.zig`, but they are not central runtime paths.

#### Zig Gaps

- `zig_rust_poc` is not promoted into a reusable FFI component consumed by runtime crates.
- No contract/ABI tests for Zig↔Rust boundaries.
- No standardized Zig build orchestration in the main Taskfile for runtime components.
- No explicit performance target tied to any production path.

## 3. Target Architecture

### Mojo Role (Numerical + Heuristic Kernels)

- Keep orchestration/control in Python.
- Move deterministic numeric hot loops into Mojo kernels (scoring, ranking, normalization).
- Call through `mojo_bridge` with stable task contracts and deterministic JSON schemas.

### Zig Role (Systems + Parsing + Interop)

- Keep business logic in Rust/Python.
- Use Zig for low-level, branch-predictable, memory-efficient primitives:
  - tight parsers/scanners,
  - ABI-safe interop with Rust,
  - optional wasm-focused tooling where Zig already exists.

## 4. Implementation Plan

## Phase M1 (Mojo foundation hardening)

1. Define Mojo kernel contract schema:
   - request/response envelopes, error envelope, version field.
2. Add `thegent` kernel registry:
   - module id, semantic version, checksum, compatibility flags.
3. Extend `mojo_bridge`:
   - cache key strategy by kernel version + args hash,
   - strict structured error mapping.
4. Add tests:
   - contract validation tests,
   - malformed payload and timeout behavior tests.

## Phase M2 (First production kernel)

1. Replace placeholder `math.mojo` with production scoring kernels:
   - provider scoring,
   - weighted ranking.
2. Integrate into one live route decision path behind feature flag.
3. Add benchmark harness:
   - Python baseline vs Mojo kernel,
   - p50/p95 latency + CPU profile.
4. Exit criteria:
   - >=20% latency reduction on scoring micro-bench,
   - no regression in route-quality tests.

## Phase Z1 (Zig interop promotion)

1. Upgrade `zig_rust_poc` from demo to reusable crate surface:
   - explicit C ABI header,
   - symbol versioning notes,
   - architecture matrix (darwin/linux arm64/x64).
2. Add Rust-side ABI tests:
   - correctness,
   - boundary values,
   - load/link failure diagnostics.
3. Add build task(s):
   - deterministic local build command and CI command.

## Phase Z2 (Production Zig workload)

1. Select one high-frequency systems path (candidate: file/path scanning utility).
2. Implement Zig kernel + Rust wrapper crate API.
3. Benchmark against existing implementation.
4. Exit criteria:
   - measurable throughput win (target >=1.3x),
   - no added crash/reliability regressions.

## 5. Operationalization

- Add `task polyglot:doctor`:
  - verifies mojo binary, zig toolchain, kernel build artifacts, ABI test health.
- Add release checklist entries:
  - kernel version bump policy,
  - rollback path for Mojo/Zig accelerated paths.
- Add observability:
  - per-kernel invocation count, error rate, p95 duration.

## 6. Work Packages

- `wp-76001-mojo-contracts`: Mojo kernel contract + registry + bridge hardening.
- `wp-76002-mojo-scoring-kernel`: Production scoring kernel + feature-flag integration.
- `wp-76003-zig-ffi-promotion`: Promote zig_rust_poc into reusable ABI component.
- `wp-76004-zig-prod-kernel`: First production Zig kernel with benchmarks.
- `wp-76005-polyglot-ops`: Doctor/CI/release guardrails for Mojo+Zig.

## 7. Risks and Controls

- Toolchain drift:
  - Pin versions in CI and preflight checks.
- Hidden latency regressions:
  - Require benchmark deltas in PR checks for accelerated paths.
- ABI instability:
  - enforce ABI tests and explicit compatibility matrix.
