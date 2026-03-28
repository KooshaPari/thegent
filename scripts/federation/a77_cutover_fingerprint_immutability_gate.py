#!/usr/bin/env python3
import argparse, csv, json, pathlib, sys

def load(p):
    t = pathlib.Path(p).read_text()
    if str(p).lower().endswith('.csv'):
        r = list(csv.DictReader(t.splitlines()))
        return r[0] if r else {}
    return json.loads(t)

p = argparse.ArgumentParser()
p.add_argument('--fingerprint', required=True)
p.add_argument('--expected-fingerprint')
p.add_argument('--require-immutable', action='store_true', default=True)
a = p.parse_args()
f = load(a.fingerprint)
current = str(f.get('fingerprint', f.get('current_fingerprint', '')))
baseline = str(f.get('baseline_fingerprint', f.get('expected_fingerprint', '')))
immutable = bool(f.get('fingerprint_immutable', f.get('immutable', False)))
if a.expected_fingerprint:
    baseline = a.expected_fingerprint
if a.require_immutable and not immutable:
    print('A77 cutover fingerprint immutability gate failed', file=sys.stderr)
    raise SystemExit(2)
if baseline and current and baseline != current:
    print('A77 cutover fingerprint changed unexpectedly', file=sys.stderr)
    raise SystemExit(2)
