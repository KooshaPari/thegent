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
        _fail(f"D96 missing {label} file: {path}")


def _load_json(path: pathlib.Path) -> dict:
    try:
        data = json.loads(path.read_text())
    except Exception as exc:
        _fail(f"D96 invalid JSON {path}: {exc}")
    if not isinstance(data, dict):
        _fail(f"D96 JSON must be an object: {path}")
    return data


def _load_csv(path: pathlib.Path, required_headers: set[str]) -> list[dict[str, str]]:
    try:
        with path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            missing = sorted(required_headers - set(reader.fieldnames or []))
            if missing:
                _fail(f"D96 CSV missing headers {missing}: {path}")
            rows = list(reader)
    except SystemExit:
        raise
    except Exception as exc:
        _fail(f"D96 invalid CSV {path}: {exc}")
    return rows


def _to_float(value: str, path: pathlib.Path, field: str) -> float:
    try:
        return float((value or "").strip())
    except ValueError as exc:
        _fail(f"D96 invalid {field} in {path}: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--recurrence-csv", required=True)
    parser.add_argument("--recurrence-field", default="open_recurrence")
    parser.add_argument("--time-field", default="window_start")
    parser.add_argument("--max-acceleration", type=float, default=0.0)
    parser.add_argument("--max-acceleration-spikes", type=int, default=0)
    args = parser.parse_args()

    report_path = pathlib.Path(args.report)
    csv_path = pathlib.Path(args.recurrence_csv)
    _require_file(report_path, "report")
    _require_file(csv_path, "recurrence")

    report = _load_json(report_path)
    rows = _load_csv(csv_path, {args.time_field, args.recurrence_field})
    if not rows:
        _fail("D96 recurrence acceleration gate failed: empty recurrence csv")

    sorted_rows = sorted(rows, key=lambda row: (row.get(args.time_field) or "").strip())
    values = [
        _to_float(row.get(args.recurrence_field), csv_path, args.recurrence_field)
        for row in sorted_rows
    ]

    acceleration = float(report.get("recurrence_acceleration", 0.0))
    acceleration_spikes = int(report.get("recurrence_acceleration_spikes", 0))

    velocities: list[float] = []
    for previous, current in zip(values, values[1:]):
        velocities.append(current - previous)
    for previous, current in zip(velocities, velocities[1:]):
        step = current - previous
        acceleration = max(acceleration, step)
        if step > args.max_acceleration:
            acceleration_spikes += 1

    if acceleration > args.max_acceleration:
        _fail(f"D96 recurrence acceleration gate failed: max_acceleration={acceleration}")
    if acceleration_spikes > args.max_acceleration_spikes:
        _fail(
            f"D96 recurrence acceleration gate failed: "
            f"acceleration_spikes={acceleration_spikes}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
