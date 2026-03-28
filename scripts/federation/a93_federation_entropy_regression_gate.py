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


parser = argparse.ArgumentParser()
parser.add_argument("--entropy", required=True)
parser.add_argument("--min-entropy", type=float, default=0.8)
parser.add_argument("--max-regression", type=float, default=0.0)
parser.add_argument("--baseline-entropy", type=float, default=None)
args = parser.parse_args()

data = load(args.entropy)

current_entropy = to_float(
    data.get("entropy", data.get("current_entropy", data.get("federation_entropy", 0.0)))
)
if args.baseline_entropy is None:
    baseline = to_float(data.get("baseline_entropy", data.get("previous_entropy", current_entropy)))
else:
    baseline = args.baseline_entropy

regression = baseline - current_entropy
if current_entropy < args.min_entropy or regression > args.max_regression:
    print("A93 federation entropy regression gate failed", file=sys.stderr)
    raise SystemExit(2)
