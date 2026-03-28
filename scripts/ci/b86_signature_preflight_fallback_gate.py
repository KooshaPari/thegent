#!/usr/bin/env python3
import argparse, json, pathlib, sys

p = argparse.ArgumentParser()
p.add_argument("--stats", required=True)
p.add_argument("--fallback-key", default="preflight_fallbacks")
p.add_argument("--total-key", default="preflight_total")
p.add_argument("--max-fallback-rate", type=float, default=0.0)
a = p.parse_args()

s = json.loads(pathlib.Path(a.stats).read_text())
fallbacks = float(s.get(a.fallback_key, 0.0) or 0.0)
total = float(s.get(a.total_key, 0.0) or 0.0)
rate = (fallbacks / total) if total > 0 else 0.0

if rate > a.max_fallback_rate:
    print("B86 signature preflight fallback gate failed", file=sys.stderr)
    raise SystemExit(2)

