#!/usr/bin/env python3
import argparse
import csv
import json
import pathlib
import sys


def _fail(message: str) -> None:
    print(f"D103 suppression decay plateau gate failed: {message}", file=sys.stderr)
    raise SystemExit(2)


def _require_file(path: pathlib.Path, label: str) -> None:
    if not path.is_file():
        _fail(f"D103 missing {label} file: {path}")


def _load_json(path: pathlib.Path) -> dict:
    try:
        payload = json.loads(path.read_text())
    except Exception as exc:
        _fail(f"D103 invalid report JSON {path}: {exc}")
    if not isinstance(payload, dict):
        _fail(f"D103 report must be an object: {path}")
    return payload


def _load_csv(path: pathlib.Path, required_headers: set[str]) -> list[dict[str, str]]:
    try:
        with path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            missing = sorted(required_headers - set(reader.fieldnames or []))
            if missing:
                _fail(f"D103 CSV missing headers {missing}: {path}")
            return list(reader)
    except SystemExit:
        raise
    except Exception as exc:
        _fail(f"D103 invalid suppressions CSV {path}: {exc}")


def _to_float(value: str, path: pathlib.Path, field: str) -> float:
    try:
        return float((value or "").strip())
    except ValueError as exc:
        _fail(f"D103 invalid {field} in {path}: {exc}")


def _to_int(value: str, path: pathlib.Path, field: str) -> int:
    try:
        return int(round(float((value or "").strip())))
    except ValueError as exc:
        _fail(f"D103 invalid {field} in {path}: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--suppressions-csv", required=True)
    parser.add_argument("--time-field", default="window_start")
    parser.add_argument("--status-field", default="status")
    parser.add_argument("--decay-field", default="suppression_decay")
    parser.add_argument("--max-plateau-events", type=int, default=0)
    parser.add_argument("--max-consecutive-plateau", type=int, default=0)
    parser.add_argument("--plateau-threshold", type=float, default=0.0)
    args = parser.parse_args()

    report_path = pathlib.Path(args.report)
    csv_path = pathlib.Path(args.suppressions_csv)
    _require_file(report_path, "report")
    _require_file(csv_path, "suppressions")

    report = _load_json(report_path)
    rows = _load_csv(
        csv_path, {args.time_field, args.status_field, args.decay_field}
    )
    if not rows:
        _fail("D103 suppression decay plateau gate failed: empty suppressions csv")

    ordered_rows = sorted(rows, key=lambda row: (row.get(args.time_field) or "").strip())
    active_states = {"open", "active", "in_progress"}
    decay = [
        _to_float(row.get(args.decay_field), csv_path, args.decay_field)
        for row in ordered_rows
        if (row.get(args.status_field) or "").strip().lower() in active_states
    ]
    if len(decay) < 2:
        _fail("D103 suppression decay plateau gate failed: insufficient decay points")

    deltas = [current - previous for previous, current in zip(decay, decay[1:])]
    plateau_events = _to_int(
        str(report.get("suppression_decay_plateau_events", 0)),
        report_path,
        "suppression_decay_plateau_events",
    )
    max_consecutive_plateau = 0
    current_run = 0
    plateau_score = float(report.get("suppression_decay_plateau", 0.0))

    for delta in deltas:
        if abs(delta) <= args.plateau_threshold:
            current_run += 1
            max_consecutive_plateau = max(max_consecutive_plateau, current_run)
            plateau_events += 1
        else:
            current_run = 0

    if max_consecutive_plateau > plateau_score:
        plateau_score = float(max_consecutive_plateau)

    if max_consecutive_plateau > args.max_consecutive_plateau:
        _fail(
            "D103 suppression decay plateau gate failed: "
            f"max_consecutive_plateau={max_consecutive_plateau}"
        )
    if plateau_events > args.max_plateau_events:
        _fail(f"D103 suppression decay plateau gate failed: plateau_events={plateau_events}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
