"""WL-115 benchmark store slice tests."""

from __future__ import annotations

from pathlib import Path

from thegent.bench.models import BenchRecord
from thegent.bench.store import append_bench_record, load_bench_records


def _sample(run_id: str, test_id: str) -> BenchRecord:
    return BenchRecord.new(
        suite="file-ops",
        harness="claude",
        test_id=test_id,
        latency_sec=0.42,
        tokens_input=11,
        tokens_output=22,
        tool_calls=1,
        success=True,
        error_recovery_attempts=0,
        run_id=run_id,
        ts_utc="2026-02-21T00:00:00+00:00",
    )


def test_append_and_load_bench_records(tmp_path: Path) -> None:
    target = tmp_path / "results.jsonl"

    append_bench_record(_sample("run-1", "fo-1"), path=target)
    append_bench_record(_sample("run-1", "fo-2"), path=target)

    records = load_bench_records(path=target)
    assert [r.test_id for r in records] == ["fo-1", "fo-2"]
    assert records[0].suite == "file-ops"


def test_load_bench_records_missing_file_is_empty(tmp_path: Path) -> None:
    missing = tmp_path / "missing.jsonl"
    assert load_bench_records(path=missing) == []

