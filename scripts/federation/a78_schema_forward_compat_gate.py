#!/usr/bin/env python3
import argparse, csv, json, pathlib, sys

def load(p):
    t = pathlib.Path(p).read_text()
    if str(p).lower().endswith('.csv'):
        r = list(csv.DictReader(t.splitlines()))
        return r
    return json.loads(t)

def truthy(v):
    return str(v).lower() in ('1', 'true', 'yes', 'on')

p = argparse.ArgumentParser()
p.add_argument('--report', required=True)
p.add_argument('--max-incompatible', type=int, default=0)
p.add_argument('--require-new-required-fields', action='store_true', default=False)
a = p.parse_args()
r = load(a.report)
if isinstance(r, list):
    items = r
else:
    items = r.get('forward_compat', r.get('compatibility', []))

bad = [x for x in items if not truthy(x.get('forward_compatible', x.get('compatible', True)))]
if a.require_new_required_fields:
    bad += [x for x in items if not truthy(x.get('new_required_supported', x.get('required_supported', True)))]
if len(bad) > a.max_incompatible:
    print(f'A78 schema forward compatibility gate failed: {len(bad)}', file=sys.stderr)
    raise SystemExit(2)
