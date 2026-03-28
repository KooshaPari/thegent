#!/usr/bin/env python3
import argparse, csv, json, pathlib, sys
p=argparse.ArgumentParser(); p.add_argument('--board', required=True); p.add_argument('--reviews-csv', required=True); p.add_argument('--max-integrity-violations', type=int, default=0); p.add_argument('--min-integrity-score', type=float, default=0.9); a=p.parse_args()
try:
    b=json.loads(pathlib.Path(a.board).read_text())
except Exception:
    print('F84 board review integrity gate failed: invalid board json', file=sys.stderr); raise SystemExit(2)
if not isinstance(b, dict) or bool(b.get('review_integrity_monitoring_enabled', True)) is not True:
    print('F84 board review integrity gate failed: review_integrity_monitoring_enabled != true', file=sys.stderr); raise SystemExit(2)
r=list(csv.DictReader(pathlib.Path(a.reviews_csv).read_text().splitlines()))
if not r or list(r[0].keys())!=['review_id','status','integrity_score']:
    print('F84 board review integrity gate failed: invalid reviews csv header', file=sys.stderr); raise SystemExit(2)
violations=sum(1 for x in r if (x.get('status') or '').strip().lower() not in {'complete','completed'} or float((x.get('integrity_score') or '0').strip())<a.min_integrity_score)
if violations>a.max_integrity_violations:
    print(f'F84 board review integrity gate failed: integrity_violations={violations} > {a.max_integrity_violations}', file=sys.stderr); raise SystemExit(2)
