#!/usr/bin/env python3
import argparse
import csv
import json
import pathlib
import sys


def _fail(message: str) -> None:
    print(f"D104 escalation latency regression gate failed: {message}", file=sys.stderr)
    raise SystemExit(2)


def _require_file(path: pathlib.Path, label: str) -> None:
    if not path.is_file():
        _fail(f"D104 missing {label} file: {path}")


def _load_json(path: pathlib.Path) -> dict:
    try:
        payload = json.loads(path.read_text())
    except Exception as exc:
        _fail(f"D104 invalid report JSON {path}: {exc}")
    if not isinstance(payload, dict):
        _fail(f"D104 report must be an object: {path}")
    return payload


def _load_csv(path: pathlib.Path, required_headers: set[str]) -> list[dict[str, str]]:
    try:
        with path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            missing = sorted(required_headers - set(reader.fieldnames or []))
            if missing:
                _fail(f"D104 CSV missing headers {missing}: {path}")
            return list(reader)
    except SystemExit:
        raise
    except Exception as exc:
        _fail(f"D104 invalid escalations CSV {path}: {exc}")


def _to_float(value: str, path: pathlib.Path, field: str) -> float:
    try:
        return float((value or "").strip())
    except ValueError as exc:
        _fail(f"D104 invalid {field} in {path}: {exc}")


def _to_int(value: str, path: pathlib.Path, field: str) -> int:
    try:
        return int(round(float((value or "").strip())))
    except ValueError as exc:
        _fail(f"D104 invalid {field} in {path}: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--escalations-csv", required=True)
    parser.add_argument("--time-field", default="window_start")
    parser.add_argument("--status-field", default="status")
    parser.add_argument("--latency-field", default="latency_ms")
    parser.add_argument("--max-latency-regressions", type=int, default=0)
    parser.add_argument("--max-latency-increase", type=float, default=0.0)
    parser.add_argument("--max-latency-variance", type=float, default=0.0)
    args = parser.parse_args()

    report_path = pathlib.Path(args.report)
    csv_path = pathlib.Path(args.escalations_csv)
    _require_file(report_path, "report")
    _require_file(csv_path, "escalations")

    report = _load_json(report_path)
    rows = _load_csv(
        csv_path,
        {args.time_field, args.status_field, args.latency_field},
    )
    if not rows:
        _fail("D104 escalation latency regression gate failed: empty escalations csv")

    ordered_rows = sorted(rows, key=lambda row: (row.get(args.time_field) or "").strip())
    active_states = {"open", "active", "in_progress"}
    latencies = [
        _to_float(row.get(args.latency_field), csv_path, args.latency_field)
        for row in ordered_rows
        if (row.get(args.status_field) or "").strip().lower() in active_states
    ]

    if len(latencies) < 2:
        _fail("D104 escalation latency regression gate failed: insufficient latency points")

    regressions = _to_int(
        str(report.get("escalation_latency_regressions", 0)),
        report_path,
        "escalation_latency_regressions",
    )
    max_increase = 0.0

    for previous, current in zip(latencies, latencies[1:]):
        increase = current - previous
        if increase > max_increase:
            max_increase = increase
        if increase > args.max_latency_increase:
            regressions += 1

    report_increase = float(report.get("escalation_latency_increase", 0.0))
    if max_increase < report_increase:
        max_increase = report_increase

    if len(latencies) > 1:
        mean = sum(latencies) / len(latencies)
        variance = sum((value - mean) ** 2 for value in latencies) / len(latencies)
    else:
        variance = 0.0

    if max_increase > args.max_latency_increase:
        _fail(
            f"D104 escalation latency regression gate failed: "
            f"max_latency_increase={max_increase}"
        )
    if regressions > args.max_latency_regressions:
        _fail(
            f"D104 escalation latency regression gate failed: "
            f"regressions={regressions}"
        )
    if variance > args.max_latency_variance:
        _fail(f"D104 escalation latency regression gate failed: variance={variance}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
