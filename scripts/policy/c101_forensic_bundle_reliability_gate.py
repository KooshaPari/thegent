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
    return str(r.get('id') or r.get('artifact') or r.get('path') or '?').strip()


p = argparse.ArgumentParser()
p.add_argument('--bundle', required=True)
p.add_argument('--reliability-csv', required=True)
p.add_argument('--min-reliability-score', type=float, default=0.95)
p.add_argument('--max-reliability-breaches', type=int, default=0)
p.add_argument('--max-missing-required', type=int, default=0)
p.add_argument('--max-duplicate-artifacts', type=int, default=0)
p.add_argument('--max-drift-ms', type=float, default=150.0)
p.add_argument('--max-drift-count', type=int, default=0)
p.add_argument('--require-sha256', action='store_true')
a = p.parse_args()

try:
    bundle = json.loads(pathlib.Path(a.bundle).read_text())
except Exception:
    print('C101 invalid bundle JSON', file=sys.stderr)
    raise SystemExit(2)

try:
    rows = sorted(
        list(csv.DictReader(pathlib.Path(a.reliability_csv).read_text().splitlines())),
        key=lambda r: json.dumps(r, sort_keys=True),
    )
except Exception:
    print('C101 invalid reliability CSV', file=sys.stderr)
    raise SystemExit(2)

if isinstance(bundle, dict):
    artifacts = bundle.get('artifacts', [])
    required = set(x for x in bundle.get('required_artifacts', []) if str(x).strip())
else:
    artifacts = []
    required = set()

for item in artifacts if isinstance(artifacts, list) else []:
    if _truthy(item.get('required', True)) and str(item.get('path', '')).strip():
        required.add(str(item['path']).strip())

seen = set()
duplicates = set()
missing_hash = []
missing_required = []
reliability_breaches = set()
drift_breaches = set()

for row in rows:
    aid = _oid(row)
    if not aid:
        continue
    if aid in seen:
        duplicates.add(aid)
    seen.add(aid)

    status = str(row.get('status', '')).strip().lower()
    if status in {'missing', 'failed', 'drift', 'invalid', 'mismatch', 'error'}:
        reliability_breaches.add(aid)
        continue

    score = _num(row.get('reliability_score', row.get('score', 1.0)))
    drift = _num(row.get('drift_ms', row.get('timing_drift_ms', 0.0)))
    if score < a.min_reliability_score:
        reliability_breaches.add(aid)
    if drift > a.max_drift_ms:
        drift_breaches.add(aid)

    if a.require_sha256 and not str(row.get('sha256', row.get('checksum', ''))).strip():
        missing_hash.append(aid)

missing_required = sorted(required - seen)
issues = []

if missing_required:
    issues.append('missing='+','.join(sorted(missing_required)))
if len(missing_required) > a.max_missing_required:
    issues.append(f'missing_count={len(missing_required)}')

if duplicates:
    issues.append('duplicate='+','.join(sorted(duplicates)))
if len(duplicates) > a.max_duplicate_artifacts:
    issues.append(f'duplicate_count={len(duplicates)}')

if reliability_breaches:
    issues.append('reliability='+','.join(sorted(reliability_breaches)))
if len(reliability_breaches) > a.max_reliability_breaches:
    issues.append(f'reliability_count={len(reliability_breaches)}')

if drift_breaches:
    issues.append('drift='+','.join(sorted(drift_breaches)))
if len(drift_breaches) > a.max_drift_count:
    issues.append(f'drift_count={len(drift_breaches)}')

if missing_hash:
    issues.append('missing_sha256='+','.join(sorted(set(missing_hash))))

if issues:
    print('C101 forensic bundle reliability breach: ' + '; '.join(sorted(issues)), file=sys.stderr)
    raise SystemExit(2)
