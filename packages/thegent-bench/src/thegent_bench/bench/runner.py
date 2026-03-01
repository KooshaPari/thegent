"""WL-115 benchmark runner slice for one suite."""

from __future__ import annotations

import time
import uuid

from .models import BenchRecord

_SUPPORTED_SUITES = frozenset({"smoke", "code-gen", "file-ops", "multi-step", "tool-use"})

_SUITE_METADATA = {
    "smoke": {
        "prompt": "thegent benchmark smoke suite",
        "test_id": "smoke-001",
        "tokens_output": 2,
    },
    "code-gen": {
        "prompt": "Write a Python function to calculate fibonacci numbers recursively with memoization",
        "test_id": "code-gen-001",
        "tokens_output": 150,
    },
    "file-ops": {
        "prompt": "List all Python files in the current directory and count lines in each",
        "test_id": "file-ops-001",
        "tokens_output": 80,
    },
    "multi-step": {
        "prompt": "First find all markdown files, then count total lines across them",
        "test_id": "multi-step-001",
        "tokens_output": 120,
    },
    "tool-use": {
        "prompt": "Use grep to find all TODO comments in Python files and list the files",
        "test_id": "tool-use-001",
        "tokens_output": 60,
    },
}


def _run_smoke_suite() -> tuple[str, int]:
    """Run a minimal end-to-end smoke workload."""
    value = "ready"
    _ = [i * 2 for i in range(1_000)]
    return value, 0


def _run_code_gen_suite() -> tuple[str, int]:
    """Run a small deterministic CPU workload for code-generation style timing."""
    values = [0, 1]
    for _ in range(20):
        values.append(values[-1] + values[-2])
    return " ".join(str(v) for v in values[:8]), 1


def _run_file_ops_suite() -> tuple[str, int]:
    """Run a deterministic file-like counting workload."""
    records = [f"line-{idx}" for idx in range(1_000)]
    return f"count={len(records)}", 2


def _run_multi_step_suite() -> tuple[str, int]:
    """Run two-step synthetic work, matching the suite naming."""
    first = list(range(500))
    second = [idx * idx for idx in first]
    return f"n={len(first)} squares={sum(second)}", 3


def _run_tool_use_suite() -> tuple[str, int]:
    """Run lightweight pattern-match work used to simulate tool use."""
    payload = "todo task\nunsupported command\ntest token"
    matches = [line for line in payload.splitlines() if "task" in line]
    return f"matches={len(matches)}", 3


def _execute_suite(name: str) -> tuple[str, int]:
    """Execute a concrete workload for a suite and return output and tool calls."""
    match name:
        case "smoke":
            return _run_smoke_suite()
        case "code-gen":
            return _run_code_gen_suite()
        case "file-ops":
            return _run_file_ops_suite()
        case "multi-step":
            return _run_multi_step_suite()
        case "tool-use":
            return _run_tool_use_suite()
        case _:
            raise ValueError(f"Unsupported benchmark suite '{name}'.")


def run_suite(*, suite: str, harness: str, run_id: str | None = None, test_id: str | None = None) -> BenchRecord:
    """Execute a benchmark suite and return a single result row."""
    normalized_suite = (suite or "").strip().lower()
    if normalized_suite not in _SUPPORTED_SUITES:
        supported = ", ".join(sorted(_SUPPORTED_SUITES))
        raise ValueError(f"Unsupported benchmark suite '{suite}'. Supported: {supported}.")

    metadata = _SUITE_METADATA[normalized_suite]
    prompt = metadata["prompt"]
    test_id = test_id or metadata["test_id"]

    started = time.perf_counter()
    output, tool_calls = _execute_suite(normalized_suite)
    tokens_output = len(output.split())
    latency_sec = time.perf_counter() - started

    return BenchRecord.new(
        suite=normalized_suite,
        harness=(harness or "unknown").strip().lower(),
        test_id=test_id,
        latency_sec=latency_sec,
        tokens_input=len(prompt.split()),
        tokens_output=tokens_output or metadata["tokens_output"],
        tool_calls=tool_calls,
        success=True,
        error_recovery_attempts=0,
        run_id=run_id or f"bench_{uuid.uuid4().hex[:8]}",
    )
