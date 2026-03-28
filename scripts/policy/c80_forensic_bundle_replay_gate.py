#!/usr/bin/env python3
import argparse, csv, json, pathlib, sys


def _truthy(v):
    return str(v).strip().lower() in {'1', 'true', 't', 'yes', 'y'}


def _path_id(r):
    return str(r.get('path') or r.get('artifact') or r.get('id') or '').strip()


p = argparse.ArgumentParser()
p.add_argument('--bundle', required=True)
p.add_argument('--replay-csv', required=True)
p.add_argument('--max-replay-failures', type=int, default=0)
p.add_argument('--require-sha256', action='store_true')
a = p.parse_args()

bundle = json.loads(pathlib.Path(a.bundle).read_text())
rows = sorted(
    list(csv.DictReader(pathlib.Path(a.replay_csv).read_text().splitlines())),
    key=lambda r: json.dumps(r, sort_keys=True),
)

required = sorted(
    {str(x).strip() for x in bundle.get('required_artifacts', []) if str(x).strip()}
)
for item in bundle.get('artifacts', []):
    if _truthy(item.get('required', False)) and str(item.get('path', '')).strip():
        required.append(str(item.get('path')).strip())
required = sorted(set(required))

expected_hash = {
    str(k).strip(): str(v).strip()
    for k, v in (bundle.get('checksums', {}) or {}).items()
    if str(k).strip() and str(v).strip()
}

seen = set()
replayed = set()
duplicates = set()
failures = []

for row in rows:
    key = _path_id(row)
    if not key:
        continue
    if key in seen:
        duplicates.add(key)
    seen.add(key)
    status = str(row.get('status', '')).strip().lower()
    replayed_here = _truthy(row.get('replayed', row.get('present', True)))
    if replayed_here:
        replayed.add(key)
    if status in {'missing', 'mismatch', 'failed', 'drift'} or not _truthy(row.get('passed', True)):
        failures.append(key)
    checksum = str(row.get('sha256', row.get('checksum', '')).strip())
    if a.require_sha256 and replayed_here and not checksum:
        failures.append(key)
    expected = expected_hash.get(key)
    if expected and checksum and checksum != expected:
        failures.append(key)

missing = sorted([x for x in required if x not in replayed])
failed_unique = sorted(set(failures))

issues = []
if missing:
    issues.append('missing='+','.join(missing))
if duplicates:
    issues.append('duplicate='+','.join(sorted(duplicates)))
if failed_unique:
    issues.append('replay_fail='+','.join(failed_unique))
if len(failed_unique) > a.max_replay_failures:
    issues.append(f'failure_count={len(failed_unique)}')

if issues:
    print('C80 forensic bundle replay breach: ' + '; '.join(issues), file=sys.stderr)
    raise SystemExit(2)
