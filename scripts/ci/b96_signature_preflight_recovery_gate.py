#!/usr/bin/env python3
import argparse, csv, json, pathlib, sys


def parse_csv(path: pathlib.Path) -> list[dict[str, str]]:
    try:
        return list(csv.DictReader(path.read_text().splitlines()))
    except OSError as exc:
        print(f"B96 failed to read CSV input: {exc}", file=sys.stderr)
        raise SystemExit(2)


def to_float(raw: str | None, *, context: str, label: str) -> float:
    try:
        return float(raw or 0.0)
    except (TypeError, ValueError):
        print(
            f"B96 invalid numeric value for {label} ({context}): {raw!r}",
            file=sys.stderr,
        )
        raise SystemExit(2)


p = argparse.ArgumentParser()
g = p.add_mutually_exclusive_group(required=True)
g.add_argument("--json")
g.add_argument("--csv")
p.add_argument("--actual-key", default="recovery_hours")
p.add_argument("--budget-key", default="recovery_budget_hours")
p.add_argument("--max-breaches", type=int, default=0)
a = p.parse_args()

if a.json:
    try:
        payload = json.loads(pathlib.Path(a.json).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"B96 invalid JSON input: {exc}", file=sys.stderr)
        raise SystemExit(2)
    if isinstance(payload, dict):
        rows = [payload]
    elif isinstance(payload, list):
        rows = payload
    else:
        print("B96 invalid JSON payload type for --json", file=sys.stderr)
        raise SystemExit(2)
else:
    rows = parse_csv(pathlib.Path(a.csv))

breaches = 0
for row in rows:
    actual = to_float(row.get(a.actual_key), context="row", label=a.actual_key)
    budget = to_float(row.get(a.budget_key), context="row", label=a.budget_key)
    if actual > budget:
        breaches += 1

if breaches > a.max_breaches:
    print("B96 signature preflight recovery gate failed", file=sys.stderr)
    raise SystemExit(2)
