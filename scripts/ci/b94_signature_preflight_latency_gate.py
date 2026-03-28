#!/usr/bin/env python3
import argparse, csv, json, pathlib, sys


def parse_csv(path: pathlib.Path) -> list[dict[str, str]]:
    try:
        return list(csv.DictReader(path.read_text().splitlines()))
    except OSError as exc:
        print(f"B94 failed to read CSV input: {exc}", file=sys.stderr)
        raise SystemExit(2)


def to_float(raw: str | None, *, context: str, label: str) -> float:
    try:
        return float(raw or 0.0)
    except (TypeError, ValueError):
        print(
            f"B94 invalid numeric value for {label} ({context}): {raw!r}",
            file=sys.stderr,
        )
        raise SystemExit(2)


p = argparse.ArgumentParser()
g = p.add_mutually_exclusive_group(required=True)
g.add_argument("--json")
g.add_argument("--csv")
p.add_argument("--latency-key", default="preflight_latency_ms")
p.add_argument("--max-latency-ms", type=float, default=0.0)
p.add_argument("--max-breaches", type=int, default=0)
a = p.parse_args()

if a.json:
    try:
        payload = json.loads(pathlib.Path(a.json).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"B94 invalid JSON input: {exc}", file=sys.stderr)
        raise SystemExit(2)
    if isinstance(payload, dict):
        rows = [payload]
    elif isinstance(payload, list):
        rows = payload
    else:
        print("B94 invalid JSON payload type for --json", file=sys.stderr)
        raise SystemExit(2)
else:
    rows = parse_csv(pathlib.Path(a.csv))

breaches = 0
for row in rows:
    latency = to_float(row.get(a.latency_key), context="row", label=a.latency_key)
    if latency > a.max_latency_ms:
        breaches += 1

if breaches > a.max_breaches:
    print("B94 signature preflight latency gate failed", file=sys.stderr)
    raise SystemExit(2)
