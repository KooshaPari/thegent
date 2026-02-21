from __future__ import annotations

import json
from pathlib import Path

from scripts.benchmark_python_suite import run_suite


def test_run_suite_emits_expected_shape() -> None:
    payload = run_suite(iterations=1000)
    assert payload["suite"] == "python-benchmark-suite-v1"
    assert isinstance(payload["benchmarks"], list)
    assert len(payload["benchmarks"]) >= 3
    for row in payload["benchmarks"]:
        assert row["iterations"] > 0
        assert row["elapsed_seconds"] >= 0
        assert row["avg_microseconds"] >= 0


def test_run_suite_can_be_serialized(tmp_path: Path) -> None:
    payload = run_suite(iterations=500)
    out = tmp_path / "bench.json"
    out.write_text(json.dumps(payload), encoding="utf-8")
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["suite"] == "python-benchmark-suite-v1"
