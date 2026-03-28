#!/usr/bin/env python3
import argparse
import csv
import json
import pathlib
import sys


def _fail(message: str) -> None:
    print(f"D102 recurrence regression gate failed: {message}", file=sys.stderr)
    raise SystemExit(2)


def _require_file(path: pathlib.Path, label: str) -> None:
    if not path.is_file():
        _fail(f"D102 missing {label} file: {path}")


def _load_json(path: pathlib.Path) -> dict:
    try:
        payload = json.loads(path.read_text())
    except Exception as exc:
        _fail(f"D102 invalid report JSON {path}: {exc}")
    if not isinstance(payload, dict):
        _fail(f"D102 report must be an object: {path}")
    return payload


def _load_csv(path: pathlib.Path, required_headers: set[str]) -> list[dict[str, str]]:
    try:
        with path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            missing = sorted(required_headers - set(reader.fieldnames or []))
            if missing:
                _fail(f"D102 CSV missing headers {missing}: {path}")
            return list(reader)
    except SystemExit:
        raise
    except Exception as exc:
        _fail(f"D102 invalid recurrence CSV {path}: {exc}")


def _to_float(value: str, path: pathlib.Path, field: str) -> float:
    try:
        return float((value or "").strip())
    except ValueError as exc:
        _fail(f"D102 invalid {field} in {path}: {exc}")


def _to_int(value: str, path: pathlib.Path, field: str) -> int:
    try:
        return int(round(float((value or "").strip())))
    except ValueError as exc:
        _fail(f"D102 invalid {field} in {path}: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--recurrence-csv", required=True)
    parser.add_argument("--time-field", default="window_start")
    parser.add_argument("--value-field", default="recurrence_rate")
    parser.add_argument("--max-recurrence-regressions", type=int, default=0)
    parser.add_argument("--max-recurrence-drop", type=float, default=0.0)
    parser.add_argument("--max-recurrence-variance", type=float, default=0.0)
    args = parser.parse_args()

    report_path = pathlib.Path(args.report)
    csv_path = pathlib.Path(args.recurrence_csv)
    _require_file(report_path, "report")
    _require_file(csv_path, "recurrence")

    report = _load_json(report_path)
    rows = _load_csv(csv_path, {args.time_field, args.value_field})
    if not rows:
        _fail("D102 recurrence regression gate failed: empty recurrence csv")

    ordered_rows = sorted(rows, key=lambda row: (row.get(args.time_field) or "").strip())
    values = [
        _to_float(row.get(args.value_field, ""), csv_path, args.value_field)
        for row in ordered_rows
    ]
    if len(values) < 2:
        _fail("D102 recurrence regression gate failed: insufficient recurrence points")

    regression_events = _to_int(
        str(report.get("recurrence_regression_events", 0)),
        report_path,
        "recurrence_regression_events",
    )
    max_drop = 0.0

    for previous, current in zip(values, values[1:]):
        drop = previous - current
        if drop > max_drop:
            max_drop = drop
        if drop > args.max_recurrence_drop:
            regression_events += 1

    report_drop = float(report.get("recurrence_regression_drop", 0.0))
    if max_drop < report_drop:
        max_drop = report_drop

    if len(values) > 1:
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
    else:
        variance = 0.0

    if max_drop > args.max_recurrence_drop:
        _fail(f"D102 recurrence regression gate failed: max_recurrence_drop={max_drop}")
    if regression_events > args.max_recurrence_regressions:
        _fail(
            f"D102 recurrence regression gate failed: "
            f"recurrence_regressions={regression_events}"
        )
    if variance > args.max_recurrence_variance:
        _fail(f"D102 recurrence regression gate failed: variance={variance}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
