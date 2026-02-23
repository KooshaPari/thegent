# CPython 3.14 + PyPy 3.11 Audit and Plan

Date: 2026-02-23
Scope: workspace-level interpreter readiness with focus on `thegent`, `agentapi++`, `cliproxyapi-plusplus`, and new `contracts/provider-bridge` scaffold.

## 1) Audit Findings (Current State)

### Interpreter constraints found
- Root workspace `pyproject.toml`: `requires-python >=3.12`
- `thegent/pyproject.toml`: `requires-python >=3.10` with explicit impl split:
  - `orjson` for CPython
  - `ujson` for PyPy
- `agentapi++/atomsAgent/pyproject.toml`: pinned to `==3.12.*` (major blocker)
- Multiple projects are `<3.14` bounded (`>=3.11,<3.14` style), blocking CPython 3.14 rollout.

### Compatibility mechanisms already present
- Runtime interpreter checks in `thegent` (`sys.implementation.name == "pypy"`).
- Existing per-implementation dependency split in `thegent` pyproject.
- Widespread `dataclass(frozen=True)`/`slots=True` usage in hot-path models.

### Immediate blockers to whole-stack target
1. Hard Python version pins (`==3.12.*`, `<3.14`) in major repos.
2. Build toolchain assumptions in workspace root (`uv run` tries editable build with missing package dir in this environment).
3. Tests and tooling not consistently parametrized by interpreter matrix.

## 2) Target Runtime Policy

Define official runtime matrix:

```text
Tier A (primary): CPython 3.14
Tier B (secondary): PyPy 3.11
Tier C (legacy): CPython 3.12/3.13 transition only
```

Policy:
1. Core bridge/control-plane logic must run on both Tier A and Tier B.
2. CPython-only acceleration is allowed behind runtime dispatch.
3. Any C-extension dependency must have a tested PyPy fallback.

## 3) Architecture Pattern for Dual Optimization

```text
Business/Core Logic (shared, pure Python)
  -> Serialization facade
     -> CPython fast path (orjson/msgspec if supported)
     -> PyPy fast path (ujson/stdlib json fallback)
  -> Event loop facade
     -> CPython optional uvloop
     -> PyPy stdlib asyncio
  -> I/O facade
     -> same API, impl-specific tuning knobs
```

Use capability flags at startup:
- `IS_CPYTHON_314_PLUS`
- `IS_PYPY_311_PLUS`
- `HAS_ORJSON`
- `HAS_UVLOOP`

## 4) Required Refactors (High Priority)

1. Remove hard pins preventing matrix:
- `agentapi++/atomsAgent/pyproject.toml`: change from `==3.12.*` to matrix-compatible range.
- projects with `<3.14` caps: widen where deps permit.

2. Standardize implementation dispatch module across repos:
- one shared helper for interpreter/feature detection.
- eliminate ad-hoc per-file checks.

3. Normalize serialization strategy:
- central `json_codec` module with impl-specific backend selection.
- never import CPython-only libraries directly in business logic.

4. Ensure test matrix parity:
- run unit + contract tests on CPython 3.14 and PyPy 3.11.
- add skip markers only where explicit and documented.

## 5) `provider-bridge` Specific Optimizations

Current scaffold status:
- Schemas + Go/Python interfaces + tests are in place.
- Python stubs are pure Python and portable.

Optimize for both runtimes:
1. Keep contract DTO modules pure-stdlib typing/dataclasses.
2. Put optional fast serialization in adapter layer, not schema layer.
3. Add perf micro-bench scripts comparing CPython 3.14 vs PyPy 3.11 for:
- request envelope parse/serialize
- event streaming object creation
- route candidate scoring loops

## 6) Testing and CI Plan

Matrix jobs:
1. `cpython-3.14`:
- contract tests
- runtime tests
- perf smoke

2. `pypy-3.11`:
- same contract/runtime tests
- fallback-path assertions
- parity checks for serialized envelopes

Pass criteria:
- 100% contract fixture parity across runtimes.
- no unsupported dependency crashes on PyPy.
- <=10% behavioral divergence in retry/fallback outcomes.

## 7) 30/60/90 Execution Plan

30 days:
1. Relax/widen Python version ranges where safe.
2. Introduce shared runtime dispatch utility.
3. Convert all JSON operations in bridge path to a single codec facade.

60 days:
1. Add CI matrix for CPython 3.14 + PyPy 3.11.
2. Patch interpreter-specific failures and dependency gaps.
3. Add baseline perf comparison report.

90 days:
1. Declare CPython 3.14 primary support complete.
2. Declare PyPy 3.11 secondary support complete.
3. Remove deprecated interpreter assumptions and legacy guards.

## 8) Implementation Backlog (Actionable)

1. Update pyproject constraints in:
- `agentapi++/atomsAgent/pyproject.toml`
- capped repos (`<3.14`) that are in active path.

2. Add shared module:
- `runtime/interpreter_profile.py` (or equivalent per repo).

3. Add codec facade:
- `runtime/json_codec.py` with tested CPython/PyPy backend selection.

4. Add matrix test config:
- CI workflows for both interpreters.

5. Add runtime benchmark harness:
- parse/serialize/event-loop microbench for provider-bridge path.

## 9) Risk Notes

1. Some dependencies may lag PyPy wheels or CPython 3.14 support windows.
2. Forcing CPython-specific optimizations into core code will regress PyPy quickly.
3. Keeping business logic pure and dispatching at infra boundaries is the safest long-term shape.
