#!/usr/bin/env python3
import argparse, csv, json, pathlib, sys


def parse_csv(path: pathlib.Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text().splitlines()))


def completion_rate(completed: float, expected: float) -> float:
    return (completed - expected) / expected if expected > 0 else 0.0


p = argparse.ArgumentParser()
g = p.add_mutually_exclusive_group(required=True)
g.add_argument("--json")
g.add_argument("--csv")
p.add_argument("--completed-key", default="completed")
p.add_argument("--expected-key", default="expected_completed")
p.add_argument("--drift-key", default="completion_drift")
p.add_argument("--max-drift-rate", type=float, default=0.0)
p.add_argument("--max-breaches", type=int, default=0)
a = p.parse_args()

records: list[dict[str, str]]
if a.json:
    payload = json.loads(pathlib.Path(a.json).read_text())
    if isinstance(payload, dict):
        payload = [payload]
    records = payload
else:
    rows = parse_csv(pathlib.Path(a.csv))
    records = rows

breaches = 0
for record in records:
    if a.drift_key in record:
        drift = float(record.get(a.drift_key, 0.0) or 0.0)
    else:
        completed = float(record.get(a.completed_key, 0.0) or 0.0)
        expected = float(record.get(a.expected_key, 0.0) or 0.0)
        drift = completion_rate(completed, expected)
    if drift > a.max_drift_rate:
        breaches += 1

if breaches > a.max_breaches:
    print("B89 scheduler completion drift gate failed", file=sys.stderr)
    raise SystemExit(2)
