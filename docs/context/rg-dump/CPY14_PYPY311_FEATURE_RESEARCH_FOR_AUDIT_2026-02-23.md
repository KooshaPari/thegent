# CPython 3.14 + PyPy 3.11 Feature Research for Better Audits

Date: 2026-02-23
Goal: turn language/runtime features into concrete code-audit checks.

## 1) CPython 3.14: what changes audit decisions

Primary checks:
1. Annotation runtime behavior:
- prefer `annotationlib.get_annotations` patterns over direct `__annotations__` assumptions.
2. New template string surfaces (`templatelib`):
- audit for sanitize/validate-before-render patterns.
3. `finally` control-flow warnings:
- treat `return/break/continue` from `finally` as explicit audit violations or documented exceptions.
4. Track 3.14 deprecations:
- identify/remove APIs scheduled for removal in upcoming versions.

Primary sources:
- https://docs.python.org/3.14/whatsnew/3.14.html
- https://docs.python.org/3.14/library/string.templatelib.html

## 2) PyPy 3.11: differences that must be audited

Primary checks:
1. JIT warmup-sensitive workloads:
- do not conclude performance from short benchmarks.
2. GC/finalizer timing assumptions:
- ensure explicit resource cleanup, avoid CPython refcount timing assumptions.
3. cpyext dependency risk:
- audit C-extension heavy dependencies for PyPy compatibility/perf impact.
4. JIT de-optimization triggers:
- minimize tracing/debug hooks in hot paths.

Primary sources:
- https://doc.pypy.org/en/latest/release-v7.3.20.html
- https://doc.pypy.org/en/latest/cpython_differences.html
- https://doc.pypy.org/en/latest/jit_help.html
- https://pypy.org/performance.html

## 3) Typing and model design audit rules (3.11+)

Primary checks:
1. Use `Protocol` for structural interfaces with explicit runtime intent.
2. Use `TypedDict` for fixed-key payload contracts (especially request/response envelopes).
3. Use `Self` for fluent APIs and avoid fragile `TypeVar` self-patterns.
4. Audit `typing_extensions` imports and migrate to stdlib `typing` where available.

Primary sources:
- https://peps.python.org/pep-0544/
- https://peps.python.org/pep-0589/
- https://peps.python.org/pep-0673/
- https://docs.python.org/3/whatsnew/3.12.html

## 4) Async/concurrency audit rules

Primary checks:
1. Require `TaskGroup` for structured sibling-task lifecycles.
2. Require `ExceptionGroup` + `except*` handling where concurrent failures are possible.
3. Ensure `CancelledError` is not swallowed in task internals unless explicitly justified.
4. Prefer `asyncio.timeout()` for deadline semantics and audit timeout-vs-cancel separation.
5. Use `contextvars` over globals/thread-local for per-task context propagation.

Primary sources:
- https://docs.python.org/3.11/library/asyncio-task.html
- https://docs.python.org/3.12/library/asyncio-task.html
- https://peps.python.org/pep-0654/
- https://docs.python.org/3.11/library/contextvars.html

## 5) Packaging/runtime-matrix audit rules (CPython + PyPy)

Primary checks:
1. enforce PEP 508 markers for impl-specific deps (`implementation_name`).
2. validate wheel tags and ABI intent (PEP 425).
3. ensure `pyproject.toml` build-system metadata is complete.
4. run matrix builds/tests with `uv` for CPython and PyPy.

Primary sources:
- https://packaging.python.org/en/latest/specifications/dependency-specifiers/
- https://peps.python.org/pep-0425/
- https://packaging.python.org/specifications/declaring-build-dependencies.html
- https://docs.astral.sh/uv/concepts/python-versions/
- https://docs.astral.sh/uv/pip/compatibility/

## 6) Measurement rubric for audits

Collect these for both interpreters:
1. latency distribution (p50/p95/p99)
2. throughput after warmup and steady-state
3. memory growth and GC behavior under long runs
4. cancellation/failure propagation correctness
5. serialization and hot-loop CPU attribution

Guard against false conclusions:
1. short-run PyPy benchmarks without warmup
2. profiler modes that alter JIT behavior
3. comparing debug-attached runs against normal production runs

Primary sources:
- https://pypy.org/performance.html
- https://docs.python.org/3.14/howto/remote_debugging.html

## 7) Immediate repo-audit application checklist

1. Find and classify all hard Python pins (`==3.12.*`, `<3.14`) in active repos.
2. Audit CPython-only dependency usage in shared business logic.
3. Audit async paths for cancellation handling and TaskGroup adoption.
4. Audit contract DTOs for `TypedDict`/Protocol consistency.
5. Establish CPython 3.14 + PyPy 3.11 matrix jobs before further optimization work.
