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
        _fail(f"D94 missing {label} file: {path}")


def _load_json(path: pathlib.Path) -> dict:
    try:
        data = json.loads(path.read_text())
    except Exception as exc:
        _fail(f"D94 invalid JSON {path}: {exc}")
    if not isinstance(data, dict):
        _fail(f"D94 JSON must be an object: {path}")
    return data


def _load_csv(path: pathlib.Path, required_headers: set[str]) -> list[dict[str, str]]:
    try:
        with path.open(newline="") as handle:
            reader = csv.DictReader(handle)
            missing = sorted(required_headers - set(reader.fieldnames or []))
            if missing:
                _fail(f"D94 CSV missing headers {missing}: {path}")
            rows = list(reader)
    except SystemExit:
        raise
    except Exception as exc:
        _fail(f"D94 invalid CSV {path}: {exc}")
    return rows


def _to_float(value: str, path: pathlib.Path, field: str) -> float:
    try:
        return float((value or "").strip())
    except ValueError as exc:
        _fail(f"D94 invalid {field} in {path}: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--suppressions-csv", required=True)
    parser.add_argument("--tolerance-field", default="tolerance_score")
    parser.add_argument("--max-tolerance-score", type=float, default=1.0)
    parser.add_argument("--max-tolerance-breaches", type=int, default=0)
    args = parser.parse_args()

    report_path = pathlib.Path(args.report)
    csv_path = pathlib.Path(args.suppressions_csv)
    _require_file(report_path, "report")
    _require_file(csv_path, "suppressions")

    report = _load_json(report_path)
    rows = _load_csv(
        csv_path,
        {"suppression_id", "status", args.tolerance_field},
    )

    max_tolerance = float(report.get("suppression_tolerance_score", 0.0))
    breach_count = int(report.get("suppression_tolerance_breaches", 0))

    for row in rows:
        status = (row.get("status") or "").strip().lower()
        if status not in {"active", "open", "approved"}:
            continue
        tolerance = _to_float(row.get(args.tolerance_field), csv_path, args.tolerance_field)
        max_tolerance = max(max_tolerance, tolerance)
        if tolerance > args.max_tolerance_score:
            breach_count += 1

    if max_tolerance > args.max_tolerance_score:
        _fail(f"D94 suppression tolerance gate failed: max_tolerance_score={max_tolerance}")
    if breach_count > args.max_tolerance_breaches:
        _fail(f"D94 suppression tolerance gate failed: tolerance_breaches={breach_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
