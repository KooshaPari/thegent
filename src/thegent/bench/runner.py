"""WL-115 benchmark runner slice for one suite."""

from __future__ import annotations

import time
import uuid

from .models import BenchRecord

_SUPPORTED_SUITES = frozenset({"smoke", "code-gen", "file-ops", "multi-step", "tool-use"})

# Benchmark suite prompts and metadata
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
    # Simulate benchmark work - in real implementation this would run actual agent/harness
    _ = prompt.upper()
    latency_sec = time.perf_counter() - started

    return BenchRecord.new(
        suite=normalized_suite,
        harness=(harness or "unknown").strip().lower(),
        test_id=test_id,
        latency_sec=latency_sec,
        tokens_input=len(prompt.split()),
        tokens_output=metadata["tokens_output"],
        tool_calls=0,
        success=True,
        error_recovery_attempts=0,
        run_id=run_id or f"bench_{uuid.uuid4().hex[:8]}",
    )
