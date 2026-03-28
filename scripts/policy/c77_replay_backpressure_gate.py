#!/usr/bin/env python3
import argparse, csv, json, pathlib, sys


def _truthy(v):
    return str(v).strip().lower() in {'1', 'true', 't', 'yes', 'y'}


def _num(v, default=0.0):
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return float(default)


def _rid(r):
    return str(r.get('id') or r.get('replay_id') or r.get('name') or '?').strip()


p = argparse.ArgumentParser()
p.add_argument('--replays-json', required=True)
p.add_argument('--backpressure-csv', required=True)
p.add_argument('--max-backpressure-events', type=float, default=0.0)
p.add_argument('--max-backpressure-rate', type=float, default=0.0)
a = p.parse_args()

replays = json.loads(pathlib.Path(a.replays_json).read_text())
rows = sorted(
    list(csv.DictReader(pathlib.Path(a.backpressure_csv).read_text().splitlines())),
    key=lambda r: json.dumps(r, sort_keys=True),
)

if isinstance(replays, dict):
    replays = replays.get('replays', replays.get('items', []))

configured = {}
required = []
for replay in replays:
    rid = _rid(replay)
    if not _truthy(replay.get('active', True)):
        continue
    required.append(rid)
    configured[rid] = _num(
        replay.get('backpressure_events', replay.get('backpressure_count', 0.0))
    )

seen = set()
totals = {}
backpressured = {}
duplicates = set()
issues = []

for row in rows:
    rid = _rid(row)
    if not rid:
        continue
    if rid in seen:
        duplicates.add(rid)
    seen.add(rid)
    totals[rid] = totals.get(rid, 0) + 1
    if _truthy(row.get('backpressured', row.get('blocked', False))):
        backpressured[rid] = backpressured.get(rid, 0) + 1
    if _num(row.get('backpressure_events', row.get('event_count', 0.0))) > a.max_backpressure_events:
        issues.append(f'event:{rid}')

for rid in required:
    if rid in configured and configured[rid] > a.max_backpressure_events:
        issues.append(f'configured:{rid}')
    if rid not in seen:
        issues.append(f'missing:{rid}')
        continue
    total = totals.get(rid, 0)
    if total and (backpressured.get(rid, 0) / total) > a.max_backpressure_rate:
        issues.append(f'rate:{rid}')

if duplicates:
    issues.append('duplicate='+','.join(sorted(duplicates)))

if issues:
    print(
        'C77 replay backpressure breach: ' + '; '.join(sorted(set(issues))),
        file=sys.stderr,
    )
    raise SystemExit(2)
