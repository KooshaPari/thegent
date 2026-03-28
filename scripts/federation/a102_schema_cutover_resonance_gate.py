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
    data = src.read_text()
    if src.suffix.lower() == ".csv":
        rows = list(csv.DictReader(data.splitlines()))
        if not rows:
            return {}
        return rows[0]
    return json.loads(data)


def to_float(value):
    return float(value) if str(value).strip() else 0.0


def to_int(value):
    return int(to_float(value))


def fail(message):
    print(f"A102 schema cutover resonance gate failed: {message}", file=sys.stderr)
    raise SystemExit(2)


parser = argparse.ArgumentParser()
parser.add_argument("--cutover", required=True)
parser.add_argument("--max-resonance-drift", type=float, default=0.2)
parser.add_argument("--max-unmatched-schema", type=int, default=0)
parser.add_argument("--max-cutover-mismatch-rate", type=float, default=0.05)
args = parser.parse_args()

try:
    report = load_data(args.cutover)
except Exception as exc:
    fail(f"invalid input ({exc})")

drift = to_float(
    report.get("schema_drift", report.get("cutover_schema_drift", report.get("resonance_drift", 0.0)))
)
unmatched = to_int(
    report.get("unmatched_schema_events", report.get("unmatched_events", 0))
)
total = to_int(
    report.get("schema_events_total", report.get("cutover_events_total", 0))
)
matched = to_int(report.get("matched_schema_events", report.get("matched_events", 0)))
if total <= 0:
    total = unmatched + matched
rate = (unmatched / total) if total else 0.0

if drift > args.max_resonance_drift:
    fail(f"schema_drift={drift} exceeds max_resonance_drift={args.max_resonance_drift}")
if unmatched > args.max_unmatched_schema:
    fail(
        f"unmatched_schema_events={unmatched} exceeds max_unmatched_schema={args.max_unmatched_schema}"
    )
if rate > args.max_cutover_mismatch_rate:
    fail(
        f"schema_mismatch_rate={rate} exceeds max_cutover_mismatch_rate={args.max_cutover_mismatch_rate}"
    )
