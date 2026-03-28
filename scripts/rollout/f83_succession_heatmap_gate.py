#!/usr/bin/env python3
import argparse, csv, json, pathlib, sys
p=argparse.ArgumentParser(); p.add_argument('--succession', required=True); p.add_argument('--heatmap-csv', required=True); p.add_argument('--max-critical-high-heat', type=int, default=0); p.add_argument('--max-heat-score', type=float, default=0.8); a=p.parse_args()
try:
    s=json.loads(pathlib.Path(a.succession).read_text())
except Exception:
    print('F83 succession heatmap gate failed: invalid succession json', file=sys.stderr); raise SystemExit(2)
if not isinstance(s, dict) or bool(s.get('heatmap_tracking_enabled', True)) is not True:
    print('F83 succession heatmap gate failed: heatmap_tracking_enabled != true', file=sys.stderr); raise SystemExit(2)
h=list(csv.DictReader(pathlib.Path(a.heatmap_csv).read_text().splitlines()))
if not h or list(h[0].keys())!=['role_id','criticality','heat_score','status']:
    print('F83 succession heatmap gate failed: invalid heatmap csv header', file=sys.stderr); raise SystemExit(2)
bad=sum(1 for x in h if (x.get('criticality') or '').strip().lower()=='critical' and (float((x.get('heat_score') or '999').strip())>a.max_heat_score or (x.get('status') or '').strip().lower() not in {'stable','mitigated','watch'}))
if bad>a.max_critical_high_heat:
    print(f'F83 succession heatmap gate failed: high_heat_critical_roles={bad} > {a.max_critical_high_heat}', file=sys.stderr); raise SystemExit(2)
