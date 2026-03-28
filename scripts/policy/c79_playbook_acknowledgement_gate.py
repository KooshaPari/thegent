#!/usr/bin/env python3
import argparse, csv, json, pathlib, sys


def _truthy(v):
    return str(v).strip().lower() in {'1', 'true', 't', 'yes', 'y'}


def _pid(r):
    return str(r.get('id') or r.get('playbook_id') or r.get('playbook') or '?').strip()


p = argparse.ArgumentParser()
p.add_argument('--playbooks', required=True)
p.add_argument('--ack-csv', required=True)
p.add_argument('--max-unacknowledged', type=int, default=0)
p.add_argument('--max-ack-failure-rate', type=float, default=0.0)
a = p.parse_args()

playbooks = json.loads(pathlib.Path(a.playbooks).read_text())
rows = sorted(
    list(csv.DictReader(pathlib.Path(a.ack_csv).read_text().splitlines())),
    key=lambda r: json.dumps(r, sort_keys=True),
)

if isinstance(playbooks, dict):
    playbooks = playbooks.get('playbooks', playbooks.get('items', []))

required = []
for p in playbooks:
    if p.get('required', True) is False:
        continue
    required.append(_pid(p))

seen = set()
duplicates = set()
ack_fail = []
for row in rows:
    pid = _pid(row)
    if not pid:
        continue
    if pid in seen:
        duplicates.add(pid)
    seen.add(pid)
    ack = row.get('acknowledged', row.get('ack', False))
    if not _truthy(ack):
        ack_fail.append(pid)
    if str(row.get('status', '')).strip().lower() in {'missing', 'failed', 'timeout'}:
        ack_fail.append(pid)

missing = [pid for pid in required if pid not in seen]
fail_unique = sorted(set(ack_fail))
rate = len(fail_unique) / max(len(required), 1)

issues = []
if duplicates:
    issues.append('duplicate='+','.join(sorted(duplicates)))
if missing:
    issues.append('missing='+','.join(sorted(missing)))
if len(fail_unique) > a.max_unacknowledged:
    issues.append(f'unacknowledged_count={len(fail_unique)}')
if rate > a.max_ack_failure_rate:
    issues.append(f'failure_rate={rate:.6f}')
if fail_unique:
    issues.append('unacknowledged='+','.join(fail_unique))

if issues:
    print('C79 playbook acknowledgement breach: ' + '; '.join(issues), file=sys.stderr)
    raise SystemExit(2)
