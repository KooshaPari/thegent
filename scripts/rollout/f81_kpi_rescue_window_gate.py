#!/usr/bin/env python3
import argparse, csv, json, pathlib, sys
p=argparse.ArgumentParser(); p.add_argument('--kpi', required=True); p.add_argument('--rescue-csv', required=True); p.add_argument('--max-rescue-windows', type=int, default=0); p.add_argument('--max-days-open', type=int, default=30); a=p.parse_args()
try:
    k=json.loads(pathlib.Path(a.kpi).read_text())
except Exception:
    print('F81 KPI rescue window gate failed: invalid kpi json', file=sys.stderr); raise SystemExit(2)
if not isinstance(k, dict) or bool(k.get('kpi_rescue_window_monitoring_enabled', True)) is not True:
    print('F81 KPI rescue window gate failed: kpi_rescue_window_monitoring_enabled != true', file=sys.stderr); raise SystemExit(2)
r=list(csv.DictReader(pathlib.Path(a.rescue_csv).read_text().splitlines()))
if not r or list(r[0].keys())!=['window_id','status','days_open']:
    print('F81 KPI rescue window gate failed: invalid rescue csv header', file=sys.stderr); raise SystemExit(2)
open_windows=sum(1 for x in r if (x.get('status') or '').strip().lower() not in {'closed','resolved'} and int((x.get('days_open') or '9999').strip())>a.max_days_open)
if open_windows>a.max_rescue_windows:
    print(f'F81 KPI rescue window gate failed: open_rescue_windows={open_windows} > {a.max_rescue_windows}', file=sys.stderr); raise SystemExit(2)
