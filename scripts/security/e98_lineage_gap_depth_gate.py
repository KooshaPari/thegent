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
        return [], f"E98 invalid input: {exc}"

    if isinstance(data, list):
        return data, None
    if isinstance(data, dict):
        for key in ("lineage", "gaps", "items", "records", "entries", "chains"):
            rows = data.get(key)
            if isinstance(rows, list):
                return rows, None
    return (
        [],
        "E98 invalid input: expected list or dict with "
        "lineage/gaps/items/records/entries/chains",
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


def _is_depth_breach(row: dict, max_gap_depth: int) -> bool:
    status = str(row.get("status", "")).strip().lower()
    if status in {"broken", "missing", "invalid", "failed", "disconnected"}:
        return True
    if bool(
        row.get("lineage_gap")
        or row.get("gap_detected")
        or row.get("depth_breach")
        or row.get("discontinuity")
    ):
        return True

    depth = _parse_int(
        row.get("gap_depth")
        or row.get("lineage_gap_depth")
        or row.get("chain_depth")
        or row.get("missing_depth")
    )
    if depth is None:
        return True

    return depth > max_gap_depth


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lineage", required=True)
    parser.add_argument("--max-gap-depth", type=int, default=2)
    parser.add_argument("--max-depth-breaches", type=int, default=0)
    args = parser.parse_args()

    rows, err = _load_rows(pathlib.Path(args.lineage))
    if err:
        print(err, file=sys.stderr)
        return 2

    breaches = sorted(
        {
            _pick(r, ("id", "lineage_id", "artifact_id", "name"))
            for r in rows
            if _is_depth_breach(r, args.max_gap_depth)
        }
    )
    if len(breaches) > args.max_depth_breaches:
        print(
            f"E98 lineage gap depth breach: count={len(breaches)} "
            f"max={args.max_depth_breaches} max_gap_depth={args.max_gap_depth}",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

