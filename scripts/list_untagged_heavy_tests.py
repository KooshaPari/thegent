#!/usr/bin/env python3
"""Generate migration-focused list of untagged heavy tests above LOC threshold."""

from __future__ import annotations

import argparse
import orjson as json
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_SOURCE = Path("artifacts/pytest/traceability/untagged-heavy-tests.json")
DEFAULT_OUTPUT = Path("artifacts/pytest/traceability/untagged-heavy-tests-migration.json")
SCHEMA_VERSION = "untagged-heavy-migration/v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Filter untagged heavy tests from an artifact by source LOC threshold."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_SOURCE),
        help="Path to heavy-untagged artifact.",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Path to write filtered migration artifact.",
    )
    parser.add_argument(
        "--min-source-loc",
        type=int,
        default=80,
        help="Minimum source_loc to include in migration list.",
    )
    parser.add_argument(
        "--max-count",
        type=int,
        default=200,
        help="Limit the number of records in the migration list.",
    )

    return parser.parse_args()


def load_records(path: Path) -> list[dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} does not contain a JSON object")

    raw_tests = payload.get("tests")
    if not isinstance(raw_tests, list):
        raise TypeError(f"{path} is missing a tests array")

    records: list[dict[str, object]] = []
    for item in raw_tests:
        if not isinstance(item, dict):
            continue
        source_loc = item.get("source_loc")
        if not isinstance(source_loc, int):
            continue
        records.append(item)
    return records


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()

    records = load_records(input_path)
    threshold = args.min_source_loc
    max_count = max(0, args.max_count)

    filtered = [item for item in records if isinstance(item.get("source_loc"), int) and item["source_loc"] >= threshold]
    filtered.sort(key=lambda item: item.get("source_loc", 0), reverse=True)
    if max_count:
        filtered = filtered[:max_count]

    payload = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "min_source_loc": threshold,
        "max_count": max_count,
        "count": len(filtered),
        "tests": [
            {
                "file": item.get("file"),
                "nodeid": item.get("nodeid"),
                "line": item.get("line"),
                "source_loc": item.get("source_loc"),
                "markers": item.get("markers"),
                "migration_hint": "Add @pytest.mark.requirement or heavy marker",
                "status": "needs_review",
            }
            for item in filtered
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2).decode().decode() + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
