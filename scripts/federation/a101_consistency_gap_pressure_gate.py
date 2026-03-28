#!/usr/bin/env python3
import argparse
import csv
import json
import pathlib
import sys


def load_data(path):
    src = pathlib.Path(path)
    if src.suffix.lower() not in {".json", ".csv"}:
        raise ValueError(f"unsupported input format: {src.suffix}")
    content = src.read_text()
    if src.suffix.lower() == ".csv":
        rows = list(csv.DictReader(content.splitlines()))
        if not rows:
            return {}
        return rows[0]
    return json.loads(content)


def to_float(value):
    return float(value) if str(value).strip() else 0.0


def to_int(value):
    return int(to_float(value))


def fail(message):
    print(f"A101 consistency gap pressure gate failed: {message}", file=sys.stderr)
    raise SystemExit(2)


parser = argparse.ArgumentParser()
parser.add_argument("--gap-report", required=True)
parser.add_argument("--max-gap-count", type=int, default=0)
parser.add_argument("--max-gap-pressure", type=float, default=0.5)
parser.add_argument("--max-stale-gap-percent", type=float, default=0.05)
args = parser.parse_args()

try:
    report = load_data(args.gap_report)
except Exception as exc:
    fail(f"invalid input ({exc})")

gap_count = to_int(report.get("consistency_gap_count", report.get("gap_count", 0)))
pressure = to_float(
    report.get("consistency_gap_pressure", report.get("gap_pressure", 0.0))
)
stale_percent = to_float(
    report.get(
        "stale_gap_percent",
        report.get("stale_consistency_gap_percent", report.get("gap_stale_percent", 0.0)),
    )
)

if gap_count > args.max_gap_count:
    fail(f"gap_count={gap_count} exceeds max_gap_count={args.max_gap_count}")
if pressure > args.max_gap_pressure:
    fail(f"gap_pressure={pressure} exceeds max_gap_pressure={args.max_gap_pressure}")
if stale_percent > args.max_stale_gap_percent:
    fail(
        f"stale_gap_percent={stale_percent} exceeds max_stale_gap_percent={args.max_stale_gap_percent}"
    )
