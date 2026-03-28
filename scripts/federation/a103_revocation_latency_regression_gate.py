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


def fail(message):
    print(f"A103 revocation latency regression gate failed: {message}", file=sys.stderr)
    raise SystemExit(2)


parser = argparse.ArgumentParser()
parser.add_argument("--latency", required=True)
parser.add_argument("--baseline", required=False)
parser.add_argument("--max-p95-ms", type=float, default=250.0)
parser.add_argument("--max-p99-ms", type=float, default=500.0)
parser.add_argument("--max-p95-regression", type=float, default=20.0)
parser.add_argument("--max-p99-regression", type=float, default=40.0)
args = parser.parse_args()

try:
    data = load_data(args.latency)
except Exception as exc:
    fail(f"invalid input ({exc})")

current_p95 = to_float(data.get("p95_ms", data.get("revocation_p95_ms", 0.0)))
current_p99 = to_float(data.get("p99_ms", data.get("revocation_p99_ms", 0.0)))

if current_p95 > args.max_p95_ms:
    fail(f"revocation_p95_ms={current_p95} exceeds max_p95_ms={args.max_p95_ms}")
if current_p99 > args.max_p99_ms:
    fail(f"revocation_p99_ms={current_p99} exceeds max_p99_ms={args.max_p99_ms}")

if args.baseline:
    try:
        baseline = load_data(args.baseline)
    except Exception as exc:
        fail(f"invalid baseline input ({exc})")

    base_p95 = to_float(baseline.get("p95_ms", baseline.get("revocation_p95_ms", current_p95)))
    base_p99 = to_float(baseline.get("p99_ms", baseline.get("revocation_p99_ms", current_p99)))

    if current_p95 - base_p95 > args.max_p95_regression:
        fail(
            f"p95 regression={(current_p95 - base_p95)} exceeds max_p95_regression={args.max_p95_regression}"
        )
    if current_p99 - base_p99 > args.max_p99_regression:
        fail(
            f"p99 regression={(current_p99 - base_p99)} exceeds max_p99_regression={args.max_p99_regression}"
        )
