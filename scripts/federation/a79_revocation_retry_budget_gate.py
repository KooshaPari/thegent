#!/usr/bin/env python3
import argparse, csv, json, pathlib, sys

def load(p):
    t = pathlib.Path(p).read_text()
    if str(p).lower().endswith('.csv'):
        r = list(csv.DictReader(t.splitlines()))
        return r[0] if r else {}
    return json.loads(t)

p = argparse.ArgumentParser()
p.add_argument('--health', required=True)
p.add_argument('--min-retry-budget', type=float, default=0.0)
a = p.parse_args()
h = load(a.health)
remaining = float(h.get('retry_budget_remaining', h.get('remaining_retry_budget', 0.0)))
used = float(h.get('retry_budget_used', h.get('used_retry_budget', 0.0)))
if remaining < 0 or used < 0 or remaining < a.min_retry_budget:
    print('A79 revocation retry budget gate failed', file=sys.stderr)
    raise SystemExit(2)
