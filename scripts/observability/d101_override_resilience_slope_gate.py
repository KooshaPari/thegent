#!/usr/bin/env python3
import argparse
import csv
import json
import pathlib
import sys


def _fail(message: str) -> None:
    print(f"D101 override resilience slope gate failed: {message}", file=sys.stderr)
    raise SystemExit(2)


def _require_file(path: pathlib.Path, label: str) -> None:
    if not path.is_file():
        _fail(f"D101 missing {label} file: {path}")


def _load_json(path: pathlib.Path) -> dict:
    try:
        payload = json.loads(path.read_text())
    except Exception as exc:
        _fail(f"D101 invalid report JSON {path}: {exc}")
    if not isinstance(payload, dict):
        _fail(f"D101 report must be an object: {path}")
    return payload


def _load_csv(path: pathlib.Path, required_headers: set[str]) -> list[dict[str, str]]:
    try:
        with path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            missing = sorted(required_headers - set(reader.fieldnames or []))
            if missing:
                _fail(f"D101 CSV missing headers {missing}: {path}")
            return list(reader)
    except SystemExit:
        raise
    except Exception as exc:
        _fail(f"D101 invalid overrides CSV {path}: {exc}")


def _to_float(value: str, path: pathlib.Path, field: str) -> float:
    try:
        return float((value or "").strip())
    except ValueError as exc:
        _fail(f"D101 invalid {field} in {path}: {exc}")


def _to_int(value: str, path: pathlib.Path, field: str) -> int:
    try:
        return int(round(float((value or "").strip())))
    except ValueError as exc:
        _fail(f"D101 invalid {field} in {path}: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--overrides-csv", required=True)
    parser.add_argument("--time-field", default="window_start")
    parser.add_argument("--status-field", default="status")
    parser.add_argument("--resilience-field", default="override_resilience")
    parser.add_argument("--max-resilience-slope", type=float, default=0.0)
    parser.add_argument("--max-resilience-regressions", type=int, default=0)
    parser.add_argument("--max-resilience-variance", type=float, default=0.0)
    args = parser.parse_args()

    report_path = pathlib.Path(args.report)
    csv_path = pathlib.Path(args.overrides_csv)
    _require_file(report_path, "report")
    _require_file(csv_path, "overrides")

    report = _load_json(report_path)
    rows = _load_csv(
        csv_path,
        {args.time_field, args.status_field, args.resilience_field},
    )
    if not rows:
        _fail("D101 override resilience slope gate failed: empty overrides csv")

    ordered_rows = sorted(rows, key=lambda row: (row.get(args.time_field) or "").strip())
    active_states = {"open", "active", "in_progress"}
    resilience = [
        _to_float(row.get(args.resilience_field), csv_path, args.resilience_field)
        for row in ordered_rows
        if (row.get(args.status_field) or "").strip().lower() in active_states
    ]

    if len(resilience) < 2:
        _fail("D101 override resilience slope gate failed: insufficient resilience points")

    slope_regressions = _to_int(
        str(report.get("override_resilience_slope_regressions", 0)),
        report_path,
        "override_resilience_slope_regressions",
    )
    max_slope = float(report.get("override_resilience_slope", 0.0))

    for prior, current in zip(resilience, resilience[1:]):
        regression = prior - current
        if regression > 0:
            if regression > max_slope:
                max_slope = regression
            if regression > args.max_resilience_slope:
                slope_regressions += 1

    report_slope = float(report.get("override_resilience_slope", 0.0))
    if max_slope < report_slope:
        max_slope = report_slope

    if len(resilience) > 1:
        mean = sum(resilience) / len(resilience)
        variance = sum((value - mean) ** 2 for value in resilience) / len(resilience)
    else:
        variance = 0.0

    if max_slope > args.max_resilience_slope:
        _fail(f"D101 override resilience slope gate failed: max_slope={max_slope}")
    if slope_regressions > args.max_resilience_regressions:
        _fail(
            f"D101 override resilience slope gate failed: "
            f"regressions={slope_regressions}"
        )
    if variance > args.max_resilience_variance:
        _fail(f"D101 override resilience slope gate failed: variance={variance}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
