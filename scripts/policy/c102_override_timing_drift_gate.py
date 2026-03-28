#!/usr/bin/env python3
import argparse, csv, json, pathlib, sys


def _truthy(v):
    return str(v).strip().lower() in {'1', 'true', 't', 'yes', 'y'}


def _num(v, default=0.0):
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return float(default)


def _oid(r):
    return str(r.get('id') or r.get('override_id') or r.get('name') or '?').strip()


p = argparse.ArgumentParser()
p.add_argument('--overrides', required=True)
p.add_argument('--timing-drift-csv', required=True)
p.add_argument('--max-drift-ms', type=float, default=200.0)
p.add_argument('--max-drift-breaches', type=int, default=0)
p.add_argument('--max-missing-overrides', type=int, default=0)
p.add_argument('--max-duplicate-overrides', type=int, default=0)
p.add_argument('--max-drift-rate', type=float, default=0.0)
a = p.parse_args()

try:
    overrides = json.loads(pathlib.Path(a.overrides).read_text())
except Exception:
    print('C102 invalid overrides JSON', file=sys.stderr)
    raise SystemExit(2)

try:
    rows = sorted(
        list(csv.DictReader(pathlib.Path(a.timing_drift_csv).read_text().splitlines())),
        key=lambda r: json.dumps(r, sort_keys=True),
    )
except Exception:
    print('C102 invalid timing drift CSV', file=sys.stderr)
    raise SystemExit(2)

if isinstance(overrides, dict):
    overrides = overrides.get('overrides', overrides.get('items', []))

required = []
for ov in overrides if isinstance(overrides, list) else []:
    if _truthy(ov.get('active', True)) and str(ov.get('id') or ov.get('name') or '').strip():
        required.append(str(ov.get('id') or ov.get('name')).strip())
required = sorted(set(required))

seen = set()
duplicates = set()
missing = []
drift_breaches = []

for row in rows:
    oid = _oid(row)
    if not oid:
        continue
    if oid in seen:
        duplicates.add(oid)
    seen.add(oid)

    drift = _num(row.get('drift_ms', row.get('timing_drift_ms', row.get('delta_ms', 0.0))))
    if drift > a.max_drift_ms:
        drift_breaches.append(oid)

    if str(row.get('status', '')).strip().lower() in {'failed', 'missing', 'drift', 'timeout', 'error'}:
        drift_breaches.append(oid)

missing = sorted(x for x in required if x not in seen)
drift_unique = sorted(set(drift_breaches))
drift_rate = len(drift_unique) / max(len(required), 1)

issues = []
if missing:
    issues.append('missing='+','.join(missing))
if len(missing) > a.max_missing_overrides:
    issues.append(f'missing_count={len(missing)}')
if duplicates:
    issues.append('duplicate='+','.join(sorted(duplicates)))
if len(duplicates) > a.max_duplicate_overrides:
    issues.append(f'duplicate_count={len(duplicates)}')
if drift_unique:
    issues.append('drift='+','.join(drift_unique))
if len(drift_unique) > a.max_drift_breaches:
    issues.append(f'drift_count={len(drift_unique)}')
if drift_rate > a.max_drift_rate:
    issues.append(f'drift_rate={drift_rate:.6f}')

if issues:
    print('C102 override timing drift breach: ' + '; '.join(sorted(issues)), file=sys.stderr)
    raise SystemExit(2)
