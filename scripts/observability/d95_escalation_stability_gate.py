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
        _fail(f"D95 missing {label} file: {path}")


def _load_json(path: pathlib.Path) -> dict:
    try:
        data = json.loads(path.read_text())
    except Exception as exc:
        _fail(f"D95 invalid JSON {path}: {exc}")
    if not isinstance(data, dict):
        _fail(f"D95 JSON must be an object: {path}")
    return data


def _load_csv(path: pathlib.Path, required_headers: set[str]) -> list[dict[str, str]]:
    try:
        with path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            missing = sorted(required_headers - set(reader.fieldnames or []))
            if missing:
                _fail(f"D95 CSV missing headers {missing}: {path}")
            rows = list(reader)
    except SystemExit:
        raise
    except Exception as exc:
        _fail(f"D95 invalid CSV {path}: {exc}")
    return rows


def _to_float(value: str, path: pathlib.Path, field: str) -> float:
    try:
        return float((value or "").strip())
    except ValueError as exc:
        _fail(f"D95 invalid {field} in {path}: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--escalations-csv", required=True)
    parser.add_argument("--stability-field", default="stability_score")
    parser.add_argument("--time-field", default="window_start")
    parser.add_argument("--max-instability-score", type=float, default=1.0)
    parser.add_argument("--max-instability-events", type=int, default=0)
    args = parser.parse_args()

    report_path = pathlib.Path(args.report)
    csv_path = pathlib.Path(args.escalations_csv)
    _require_file(report_path, "report")
    _require_file(csv_path, "escalations")

    report = _load_json(report_path)
    rows = _load_csv(
        csv_path,
        {"escalation_id", "status", args.stability_field, args.time_field},
    )

    max_instability = float(report.get("escalation_instability_score", 0.0))
    instability_events = int(report.get("escalation_instability_events", 0))
    active_states = {"open", "active", "in_progress"}

    sorted_rows = sorted(rows, key=lambda row: (row.get(args.time_field) or "").strip())
    values: list[float] = []
    for row in sorted_rows:
        status = (row.get("status") or "").strip().lower()
        if status not in active_states:
            continue
        value = _to_float(row.get(args.stability_field), csv_path, args.stability_field)
        values.append(value)
        max_instability = max(max_instability, value)
        if value > args.max_instability_score:
            instability_events += 1

    if values:
        # Keep deterministic ranking by window when provided.
        sorted_values = sorted(values)
        for previous, current in zip(sorted_values, sorted_values[1:]):
            if current > previous and (current - previous) > args.max_instability_score:
                instability_events += 1

    if max_instability > args.max_instability_score:
        _fail(
            f"D95 escalation stability gate failed: max_instability_score={max_instability}"
        )
    if instability_events > args.max_instability_events:
        _fail(
            f"D95 escalation stability gate failed: instability_events={instability_events}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
