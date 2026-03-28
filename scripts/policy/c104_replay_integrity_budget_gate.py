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
p.add_argument('--replay-csv', required=True)
p.add_argument('--max-missing-required', type=int, default=0)
p.add_argument('--max-integrity-failures', type=int, default=0)
p.add_argument('--max-sha-mismatches', type=int, default=0)
p.add_argument('--max-duplicate-replays', type=int, default=0)
p.add_argument('--max-integrity-budget', type=float, default=0.0)
p.add_argument('--require-sha256', action='store_true')
a = p.parse_args()

try:
    bundle = json.loads(pathlib.Path(a.bundle).read_text())
except Exception:
    print('C104 invalid bundle JSON', file=sys.stderr)
    raise SystemExit(2)

try:
    rows = sorted(
        list(csv.DictReader(pathlib.Path(a.replay_csv).read_text().splitlines())),
        key=lambda r: json.dumps(r, sort_keys=True),
    )
except Exception:
    print('C104 invalid replay CSV', file=sys.stderr)
    raise SystemExit(2)

bundle_obj = bundle if isinstance(bundle, dict) else {}
if isinstance(bundle, dict):
    bundle_items = bundle.get('artifacts', [])
    required = set(x for x in bundle.get('required_artifacts', []) if str(x).strip())
    budget = _num(
        bundle.get('replay_integrity_budget', bundle.get('integrity_budget', 0.0))
    )
else:
    bundle_items = []
    required = set()
    budget = 0.0
if a.max_integrity_budget > 0:
    budget = a.max_integrity_budget

for item in bundle_items if isinstance(bundle_items, list) else []:
    if _truthy(item.get('required', True)) and str(item.get('path', '')).strip():
        required.add(str(item['path']).strip())

expected = {
    str(k).strip(): str(v).strip()
    for k, v in (bundle_obj.get('checksums', {}) or {}).items()
    if str(k).strip() and str(v).strip()
}

seen = set()
duplicates = set()
integrity_fail = set()
sha_mismatch = set()
missing_hash = set()

spend = 0.0

for row in rows:
    aid = _oid(row)
    if not aid:
        continue
    if aid in seen:
        duplicates.add(aid)
    seen.add(aid)

    status = str(row.get('status', '')).strip().lower()
    replayed = _truthy(row.get('replayed', row.get('present', True)))
    if status in {'missing', 'failed', 'mismatch', 'drift', 'error'} or not _truthy(row.get('passed', True)):
        integrity_fail.add(aid)

    checksum = str(row.get('sha256', row.get('checksum', '')).strip())
    if a.require_sha256 and replayed and not checksum:
        missing_hash.add(aid)
    expected_checksum = expected.get(aid)
    if expected_checksum and checksum and checksum != expected_checksum:
        sha_mismatch.add(aid)

    if aid in integrity_fail or aid in sha_mismatch or aid in missing_hash:
        spend += _num(row.get('integrity_cost', row.get('weight', 1.0)), default=1.0)

missing = sorted(x for x in sorted(required) if x not in seen)
issues = []
if missing:
    issues.append('missing='+','.join(missing))
if len(missing) > a.max_missing_required:
    issues.append(f'missing_count={len(missing)}')
if duplicates:
    issues.append('duplicate='+','.join(sorted(duplicates)))
if len(duplicates) > 0:
    issues.append(f'duplicate_count={len(duplicates)}')
if integrity_fail:
    issues.append('integrity_fail='+','.join(sorted(integrity_fail)))
if len(integrity_fail) > a.max_integrity_failures:
    issues.append(f'integrity_fail_count={len(integrity_fail)}')
if sha_mismatch:
    issues.append('sha_mismatch='+','.join(sorted(sha_mismatch)))
if len(sha_mismatch) > a.max_sha_mismatches:
    issues.append(f'sha_mismatch_count={len(sha_mismatch)}')
if missing_hash:
    issues.append('missing_sha256='+','.join(sorted(missing_hash)))
if len(duplicates) > a.max_duplicate_replays:
    issues.append(f'duplicate_count={len(duplicates)}')
if budget > 0 and spend > budget:
    issues.append(f'integrity_budget_used={spend:.6f}>{budget:.6f}')

if issues:
    print('C104 replay integrity budget breach: ' + '; '.join(sorted(issues)), file=sys.stderr)
    raise SystemExit(2)
