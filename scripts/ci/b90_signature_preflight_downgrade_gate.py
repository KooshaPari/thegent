#!/usr/bin/env python3
import argparse, csv, json, pathlib, sys


def parse_csv(path: pathlib.Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text().splitlines()))


p = argparse.ArgumentParser()
g = p.add_mutually_exclusive_group(required=True)
g.add_argument("--json")
g.add_argument("--csv")
p.add_argument("--total-key", default="preflight_total")
p.add_argument("--downgrade-key", default="preflight_downgraded")
p.add_argument("--max-downgrade-rate", type=float, default=0.0)
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
    total = float(record.get(a.total_key, 0.0) or 0.0)
    downgraded = float(record.get(a.downgrade_key, 0.0) or 0.0)
    downgrade_rate = (downgraded / total) if total > 0 else 0.0
    if downgrade_rate > a.max_downgrade_rate:
        breaches += 1

if breaches > a.max_breaches:
    print("B90 signature preflight downgrade gate failed", file=sys.stderr)
    raise SystemExit(2)
