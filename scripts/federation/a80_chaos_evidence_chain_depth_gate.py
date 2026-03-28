#!/usr/bin/env python3
import argparse, csv, json, pathlib, sys

def load(p):
    t = pathlib.Path(p).read_text()
    if str(p).lower().endswith('.csv'):
        r = list(csv.DictReader(t.splitlines()))
        return r[0] if r else {}
    return json.loads(t)

p = argparse.ArgumentParser()
p.add_argument('--evidence', required=True)
p.add_argument('--min-chain-depth', type=int, default=1)
p.add_argument('--max-chain-depth', type=int, default=64)
a = p.parse_args()
e = load(a.evidence)
chain = e.get('evidence_chain', e.get('chain', []))
if isinstance(chain, list):
    depth = len(chain)
else:
    depth = int(e.get('chain_depth', 0))
if depth < a.min_chain_depth or depth > a.max_chain_depth or not bool(e.get('chain_complete', True)):
    print('A80 chaos evidence chain depth gate failed', file=sys.stderr)
    raise SystemExit(2)
