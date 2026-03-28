#!/usr/bin/env python3
import argparse, csv, json, pathlib, sys


def _truthy(v):
    return str(v).strip().lower() in {'1', 'true', 't', 'yes', 'y'}


def _num(v, default=0.0):
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return float(default)


def _pid(r):
    return str(r.get('id') or r.get('playbook_id') or r.get('name') or '?').strip()


p = argparse.ArgumentParser()
p.add_argument('--playbooks', required=True)
p.add_argument('--stability-csv', required=True)
p.add_argument('--min-stability-margin', type=float, default=0.75)
p.add_argument('--max-unstable-playbooks', type=int, default=0)
p.add_argument('--max-missing-playbooks', type=int, default=0)
p.add_argument('--max-duplicate-playbooks', type=int, default=0)
p.add_argument('--max-flap-rate', type=float, default=0.0)
a = p.parse_args()

try:
    playbooks = json.loads(pathlib.Path(a.playbooks).read_text())
except Exception:
    print('C103 invalid playbooks JSON', file=sys.stderr)
    raise SystemExit(2)

try:
    rows = sorted(
        list(csv.DictReader(pathlib.Path(a.stability_csv).read_text().splitlines())),
        key=lambda r: json.dumps(r, sort_keys=True),
    )
except Exception:
    print('C103 invalid stability CSV', file=sys.stderr)
    raise SystemExit(2)

if isinstance(playbooks, dict):
    playbooks = playbooks.get('playbooks', playbooks.get('items', []))

required = []
for p in playbooks if isinstance(playbooks, list) else []:
    if _truthy(p.get('required', True)) and str(p.get('id') or p.get('name') or '').strip():
        required.append(str(p.get('id') or p.get('name')).strip())
required = sorted(set(required))

seen = set()
duplicates = set()
unstable = set()

for row in rows:
    pid = _pid(row)
    if not pid:
        continue
    if pid in seen:
        duplicates.add(pid)
    seen.add(pid)

    margin = _num(row.get('stability_margin', row.get('margin', row.get('score', 1.0))))
    status = str(row.get('status', '')).strip().lower()
    if margin < a.min_stability_margin:
        unstable.add(pid)
    if status in {'unstable', 'failed', 'degraded', 'timeout', 'error', 'missing'}:
        unstable.add(pid)

missing = sorted(x for x in required if x not in seen)
unstable_unique = sorted(unstable)
unstable_rate = len(unstable_unique) / max(len(required), 1)

issues = []
if missing:
    issues.append('missing='+','.join(missing))
if len(missing) > a.max_missing_playbooks:
    issues.append(f'missing_count={len(missing)}')
if duplicates:
    issues.append('duplicate='+','.join(sorted(duplicates)))
if len(duplicates) > a.max_duplicate_playbooks:
    issues.append(f'duplicate_count={len(duplicates)}')
if unstable_unique:
    issues.append('unstable='+','.join(unstable_unique))
if len(unstable_unique) > a.max_unstable_playbooks:
    issues.append(f'unstable_count={len(unstable_unique)}')
if unstable_rate > a.max_flap_rate:
    issues.append(f'unstable_rate={unstable_rate:.6f}')

if issues:
    print('C103 playbook stability margin breach: ' + '; '.join(sorted(issues)), file=sys.stderr)
    raise SystemExit(2)
