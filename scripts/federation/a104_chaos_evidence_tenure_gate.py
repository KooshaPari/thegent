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
    print(f"A104 chaos evidence tenure gate failed: {message}", file=sys.stderr)
    raise SystemExit(2)


parser = argparse.ArgumentParser()
parser.add_argument("--evidence", required=True)
parser.add_argument("--min-tenant-confidence-days", type=float, default=3.0)
parser.add_argument("--min-tenure-days", type=float, default=1.0)
parser.add_argument("--max-gap-days", type=float, default=2.0)
args = parser.parse_args()

try:
    evidence = load_data(args.evidence)
except Exception as exc:
    fail(f"invalid input ({exc})")

tenure = to_float(evidence.get("evidence_tenure_days", evidence.get("tenure_days", 0.0)))
confidence = to_float(
    evidence.get("tenant_confidence_days", evidence.get("confidence_days", 0.0))
)
gap = to_float(
    evidence.get("evidence_gap_days", evidence.get("tenure_gap_days", 0.0))
)
integrity_ok = bool(
    evidence.get("tenure_complete", evidence.get("evidence_tenure_complete", True))
)

if tenure < args.min_tenure_days:
    fail(f"evidence_tenure_days={tenure} below min_tenure_days={args.min_tenure_days}")
if confidence < args.min_tenant_confidence_days:
    fail(
        f"tenant_confidence_days={confidence} below min_tenant_confidence_days={args.min_tenant_confidence_days}"
    )
if gap > args.max_gap_days:
    fail(f"evidence_gap_days={gap} exceeds max_gap_days={args.max_gap_days}")
if not integrity_ok:
    fail("evidence tenure integrity flag is false")
