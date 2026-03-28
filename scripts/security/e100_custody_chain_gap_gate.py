#!/usr/bin/env python3
import argparse
import csv
import json
import pathlib
import sys


def _load_rows(path: pathlib.Path) -> tuple[list[dict], str | None]:
    try:
        if path.suffix.lower() == ".csv":
            return list(csv.DictReader(path.open())), None
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return [], f"E100 invalid input: {exc}"

    if isinstance(data, list):
        return data, None
    if isinstance(data, dict):
        for key in ("custody", "chains", "lineage", "items", "records", "entries"):
            rows = data.get(key)
            if isinstance(rows, list):
                return rows, None
    return (
        [],
        "E100 invalid input: expected list or dict with "
        "custody/chains/lineage/items/records/entries",
    )


def _pick(row: dict, keys: tuple[str, ...]) -> str:
    for key in keys:
        value = row.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def _parse_int(value: object) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return int(float(text))
    except (TypeError, ValueError):
        return None


def _is_custody_gap(row: dict, max_gap_count: int) -> bool:
    status = str(row.get("status", "")).strip().lower()
    if status in {"missing", "broken", "invalid", "failed", "orphaned"}:
        return True
    if bool(
        row.get("custody_gap")
        or row.get("chain_gap")
        or row.get("broken_link")
        or row.get("missing_link")
    ):
        return True

    gap = _parse_int(
        row.get("gap_count")
        or row.get("missing_segments")
        or row.get("lineage_gap")
        or row.get("discontinuity_count")
    )
    if gap is None:
        return True

    return gap > max_gap_count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--custody", required=True)
    parser.add_argument("--max-gap-count", type=int, default=1)
    parser.add_argument("--max-chain-gaps", type=int, default=0)
    args = parser.parse_args()

    rows, err = _load_rows(pathlib.Path(args.custody))
    if err:
        print(err, file=sys.stderr)
        return 2

    gaps = sorted(
        {
            _pick(r, ("chain_id", "custody_chain_id", "artifact_id", "name"))
            for r in rows
            if _is_custody_gap(r, args.max_gap_count)
        }
    )
    if len(gaps) > args.max_chain_gaps:
        print(
            f"E100 custody chain gap breach: count={len(gaps)} "
            f"max={args.max_chain_gaps} max_gap_count={args.max_gap_count}",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
