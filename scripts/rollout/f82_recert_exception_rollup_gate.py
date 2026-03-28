#!/usr/bin/env python3
import argparse, csv, json, pathlib, sys
p=argparse.ArgumentParser(); p.add_argument('--recert', required=True); p.add_argument('--rollup-csv', required=True); p.add_argument('--max-unresolved-rollups', type=int, default=0); a=p.parse_args()
try:
    r=json.loads(pathlib.Path(a.recert).read_text())
except Exception:
    print('F82 recert exception rollup gate failed: invalid recert json', file=sys.stderr); raise SystemExit(2)
if not isinstance(r, dict) or bool(r.get('exception_rollup_enabled', True)) is not True:
    print('F82 recert exception rollup gate failed: exception_rollup_enabled != true', file=sys.stderr); raise SystemExit(2)
d=list(csv.DictReader(pathlib.Path(a.rollup_csv).read_text().splitlines()))
if not d or list(d[0].keys())!=['exception_id','rollup_status','owner','days_open']:
    print('F82 recert exception rollup gate failed: invalid rollup csv header', file=sys.stderr); raise SystemExit(2)
unresolved=sum(1 for x in d if (x.get('rollup_status') or '').strip().lower() in {'open','pending','active'} or int((x.get('days_open') or '9999').strip())>90)
if unresolved>a.max_unresolved_rollups:
    print(f'F82 recert exception rollup gate failed: unresolved_rollups={unresolved} > {a.max_unresolved_rollups}', file=sys.stderr); raise SystemExit(2)
