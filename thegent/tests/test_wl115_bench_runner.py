"""Focused unit tests for benchmark suite execution."""

from __future__ import annotations

import pytest

from thegent.bench.runner import run_suite


def test_run_suite_records_smoke_results():
    """Smoke suite execution returns a concrete benchmark row."""
    record = run_suite(suite="smoke", harness="codex", run_id="run-1")

    assert record.suite == "smoke"
    assert record.harness == "codex"
    assert record.test_id == "smoke-001"
    assert record.run_id == "run-1"
    assert record.latency_sec >= 0.0
    assert record.tokens_input > 0
    assert record.tokens_output > 0
    assert record.tool_calls >= 0
    assert record.success is True


def test_run_suite_unknown_suite_raises():
    """Unknown suites are rejected with a stable error."""
    with pytest.raises(ValueError, match="Unsupported benchmark suite"):
        run_suite(suite="unknown-suite", harness="codex")


def test_run_suite_harness_name_is_normalized():
    """Harness names are normalized for deterministic row storage."""
    record = run_suite(suite="code-gen", harness="  CoDeX  ")

    assert record.harness == "codex"
