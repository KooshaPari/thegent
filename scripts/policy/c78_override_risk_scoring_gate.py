#!/usr/bin/env python3
import argparse, csv, json, pathlib, sys


def _num(v, default=0.0):
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return float(default)


def _truthy(v):
    return str(v).strip().lower() in {'1', 'true', 't', 'yes', 'y'}


def _oid(r):
    return str(r.get('id') or r.get('override_id') or r.get('name') or '?').strip()


p = argparse.ArgumentParser()
p.add_argument('--overrides', required=True)
p.add_argument('--risk-csv', required=True)
p.add_argument('--max-high-risk-overrides', type=int, default=0)
p.add_argument('--max-risk-score', type=float, default=0.9)
a = p.parse_args()

overrides = json.loads(pathlib.Path(a.overrides).read_text())
rows = sorted(
    list(csv.DictReader(pathlib.Path(a.risk_csv).read_text().splitlines())),
    key=lambda r: json.dumps(r, sort_keys=True),
)

if isinstance(overrides, dict):
    overrides = overrides.get('overrides', overrides.get('items', []))

risk_by_id = {}
required = []
for item in overrides:
    oid = _oid(item)
    if not _truthy(item.get('active', True)):
        continue
    required.append(oid)
    risk_by_id[oid] = _num(item.get('risk_score', item.get('score', 0.0)))

seen = set()
duplicates = set()
issues = []
high = []

for row in rows:
    oid = _oid(row)
    if not oid:
        continue
    if oid in seen:
        duplicates.add(oid)
    seen.add(oid)
    score = _num(row.get('risk_score', row.get('score', 0.0)))
    if score > a.max_risk_score:
        high.append(oid)

for oid in required:
    if oid not in seen:
        issues.append(f'missing:{oid}')
        continue
    score = risk_by_id.get(oid, 0.0)
    if score > a.max_risk_score:
        high.append(oid)

high_unique = sorted(set(high))
if len(high_unique) > a.max_high_risk_overrides:
    issues.append(f'high_risk_count={len(high_unique)}')
if duplicates:
    issues.append('duplicate='+','.join(sorted(duplicates)))
if high_unique:
    issues.append('high_risk='+','.join(high_unique))

if issues:
    print('C78 override risk scoring breach: ' + '; '.join(issues), file=sys.stderr)
    raise SystemExit(2)
