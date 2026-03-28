#!/usr/bin/env python3
import argparse
import csv
import json
import pathlib
import sys


def _fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(2)


def _require_file(path: pathlib.Path, label: str) -> None:
    if not path.is_file():
        _fail(f"D93 missing {label} file: {path}")


def _load_json(path: pathlib.Path) -> dict:
    try:
        data = json.loads(path.read_text())
    except Exception as exc:
        _fail(f"D93 invalid JSON {path}: {exc}")
    if not isinstance(data, dict):
        _fail(f"D93 JSON must be an object: {path}")
    return data


def _load_csv(path: pathlib.Path, required_headers: set[str]) -> list[dict[str, str]]:
    try:
        with path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            missing = sorted(required_headers - set(reader.fieldnames or []))
            if missing:
                _fail(f"D93 CSV missing headers {missing}: {path}")
            rows = list(reader)
    except SystemExit:
        raise
    except Exception as exc:
        _fail(f"D93 invalid CSV {path}: {exc}")
    return rows


def _to_float(value: str, path: pathlib.Path, field: str) -> float:
    try:
        return float((value or "").strip())
    except ValueError as exc:
        _fail(f"D93 invalid {field} in {path}: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--overrides-csv", required=True)
    parser.add_argument("--debt-field", default="override_debt")
    parser.add_argument("--time-field", default="period")
    parser.add_argument("--max-ramp", type=float, default=0.0)
    parser.add_argument("--max-ramp-events", type=int, default=0)
    args = parser.parse_args()

    report_path = pathlib.Path(args.report)
    csv_path = pathlib.Path(args.overrides_csv)
    _require_file(report_path, "report")
    _require_file(csv_path, "overrides")

    report = _load_json(report_path)
    rows = _load_csv(csv_path, {args.time_field, args.debt_field})
    if not rows:
        _fail("D93 override debt ramp gate failed: empty overrides csv")

    sorted_rows = sorted(rows, key=lambda row: (row.get(args.time_field) or "").strip())
    debts = [
        _to_float(row.get(args.debt_field), csv_path, args.debt_field)
        for row in sorted_rows
    ]

    max_ramp = float(report.get("override_debt_ramp", 0.0))
    ramp_events = int(report.get("override_debt_ramp_events", 0))

    for previous, current in zip(debts, debts[1:]):
        ramp = current - previous
        max_ramp = max(max_ramp, ramp)
        if ramp > args.max_ramp:
            ramp_events += 1

    if max_ramp > args.max_ramp:
        _fail(f"D93 override debt ramp gate failed: max_ramp={max_ramp}")
    if ramp_events > args.max_ramp_events:
        _fail(f"D93 override debt ramp gate failed: ramp_events={ramp_events}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
