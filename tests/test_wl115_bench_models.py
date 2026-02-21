"""WL-115 benchmark model slice tests."""

from __future__ import annotations

import pytest

from thegent.bench.models import BenchRecord


def test_bench_record_round_trip_dict() -> None:
    record = BenchRecord.new(
        suite="code-gen",
        harness="codex",
        test_id="cg-001",
        latency_sec=1.25,
        tokens_input=123,
        tokens_output=456,
        tool_calls=2,
        success=True,
        error_recovery_attempts=0,
        run_id="run-1",
        ts_utc="2026-02-21T00:00:00+00:00",
    )

    rehydrated = BenchRecord.from_dict(record.to_dict())
    assert rehydrated == record


def test_bench_record_from_dict_requires_schema_fields() -> None:
    with pytest.raises(ValueError, match="Missing benchmark fields"):
        BenchRecord.from_dict({"suite": "code-gen"})

