#!/usr/bin/env python3
import argparse, csv, json, pathlib, sys


def parse_csv(path: pathlib.Path) -> list[dict[str, str]]:
    try:
        return list(csv.DictReader(path.read_text().splitlines()))
    except OSError as exc:
        print(f"B93 failed to read CSV input: {exc}", file=sys.stderr)
        raise SystemExit(2)


def to_float(raw: str | None, *, context: str, label: str) -> float:
    try:
        return float(raw or 0.0)
    except (TypeError, ValueError):
        print(
            f"B93 invalid numeric value for {label} ({context}): {raw!r}",
            file=sys.stderr,
        )
        raise SystemExit(2)


p = argparse.ArgumentParser()
g = p.add_mutually_exclusive_group(required=True)
g.add_argument("--json")
g.add_argument("--csv")
p.add_argument("--total-key", default="preflight_total")
p.add_argument("--safety-key", default="preflight_safety_passed")
p.add_argument("--min-safety-ratio", type=float, default=1.0)
p.add_argument("--max-breaches", type=int, default=0)
a = p.parse_args()

if a.json:
    try:
        payload = json.loads(pathlib.Path(a.json).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"B93 invalid JSON input: {exc}", file=sys.stderr)
        raise SystemExit(2)
    if isinstance(payload, dict):
        rows = [payload]
    elif isinstance(payload, list):
        rows = payload
    else:
        print("B93 invalid JSON payload type for --json", file=sys.stderr)
        raise SystemExit(2)
else:
    rows = parse_csv(pathlib.Path(a.csv))

breaches = 0
for row in rows:
    total = to_float(row.get(a.total_key), context="row", label=a.total_key)
    safety = to_float(row.get(a.safety_key), context="row", label=a.safety_key)
    safety_ratio = (safety / total) if total > 0 else 1.0
    if safety_ratio < a.min_safety_ratio:
        breaches += 1

if breaches > a.max_breaches:
    print("B93 signature preflight safety gate failed", file=sys.stderr)
    raise SystemExit(2)
