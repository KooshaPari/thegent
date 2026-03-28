#!/usr/bin/env python3
import argparse
import csv
import json
import pathlib
import sys


def load(path):
    raw = pathlib.Path(path).read_text()
    if str(path).lower().endswith(".csv"):
        rows = list(csv.DictReader(raw.splitlines()))
        return rows[0] if rows else {}
    return json.loads(raw)


def to_float(value):
    return float(value) if str(value).strip() else 0.0


def to_int(value):
    return int(to_float(value))


parser = argparse.ArgumentParser()
parser.add_argument("--drift", required=True)
parser.add_argument("--max-drift-events", type=int, default=0)
parser.add_argument("--max-drift-ratio", type=float, default=0.1)
args = parser.parse_args()

data = load(args.drift)

drift_events = to_int(
    data.get("schema_drift_events", data.get("cutover_schema_drift_events", 0))
)
matched_events = to_int(
    data.get(
        "matched_schema_drift_events",
        data.get("schema_drift_matched_events", data.get("matched_drift_events", 0)),
    )
)
total_events = to_int(
    data.get("total_schema_events", data.get("total_events", drift_events))
)
if total_events <= 0:
    total_events = drift_events

unmatched = max(drift_events - matched_events, 0)
ratio = (unmatched / total_events) if total_events else 0.0

if drift_events > args.max_drift_events or ratio > args.max_drift_ratio:
    print("A94 cutover schema drift gate failed", file=sys.stderr)
    raise SystemExit(2)
