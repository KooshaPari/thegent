#!/usr/bin/env python3
import argparse, csv, pathlib, sys

p = argparse.ArgumentParser()
p.add_argument("--csv", required=True)
p.add_argument("--predict-col", default="predicted_days_left")
p.add_argument("--min-days-left", type=float, default=0.0)
p.add_argument("--max-breaches", type=int, default=0)
a = p.parse_args()

rows = list(csv.DictReader(pathlib.Path(a.csv).open()))
breaches = sum(
    1 for r in rows if float(r.get(a.predict_col, 0.0) or 0.0) < a.min_days_left
)

if breaches > a.max_breaches:
    print("B87 attestation expiry predict gate failed", file=sys.stderr)
    raise SystemExit(2)

