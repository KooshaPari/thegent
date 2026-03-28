#!/usr/bin/env python3
import argparse, csv, json, pathlib, sys


def parse_csv(path: pathlib.Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text().splitlines()))


p = argparse.ArgumentParser()
g = p.add_mutually_exclusive_group(required=True)
g.add_argument("--json")
g.add_argument("--csv")
p.add_argument("--actual-key", default="recovery_hours")
p.add_argument("--budget-key", default="recovery_budget_hours")
p.add_argument("--max-breaches", type=int, default=0)
a = p.parse_args()

if a.json:
    payload = json.loads(pathlib.Path(a.json).read_text())
    if isinstance(payload, dict):
        payload = [payload]
    rows = payload
else:
    rows = parse_csv(pathlib.Path(a.csv))

breaches = sum(
    1 for row in rows
    if float(row.get(a.actual_key, 0.0) or 0.0) > float(row.get(a.budget_key, 0.0) or 0.0)

if breaches > a.max_breaches:
    print("B92 CAPA recovery budget gate failed", file=sys.stderr)
    raise SystemExit(2)
