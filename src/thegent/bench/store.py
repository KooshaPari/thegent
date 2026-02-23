"""WL-115 benchmark JSONL storage helpers."""

from __future__ import annotations

import orjson as json
from pathlib import Path

from .models import BenchRecord

DEFAULT_RESULTS_PATH = Path.home() / ".thegent" / "bench" / "results.jsonl"


def append_bench_record(record: BenchRecord, *, path: Path | None = None) -> Path:
    """Append one benchmark record to JSONL storage."""
    target = path or DEFAULT_RESULTS_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record.to_dict().decode().decode(), separators=(",", ":")))
        handle.write("\n")
    return target


def load_bench_records(*, path: Path | None = None) -> list[BenchRecord]:
    """Load benchmark records from JSONL; empty list when file is absent."""
    target = path or DEFAULT_RESULTS_PATH
    if not target.exists():
        return []

    rows: list[BenchRecord] = []
    with target.open(encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            rows.append(BenchRecord.from_dict(payload))
    return rows
