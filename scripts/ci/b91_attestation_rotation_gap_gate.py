#!/usr/bin/env python3
import argparse
import csv
import pathlib
import sys
from datetime import datetime, timezone
import json


def parse_ts(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def parse_csv(path: pathlib.Path) -> list[dict[str, str]]:
    return list(csv.DictReader(path.read_text().splitlines()))


p = argparse.ArgumentParser()
g = p.add_mutually_exclusive_group(required=True)
g.add_argument("--json")
g.add_argument("--csv")
p.add_argument("--rotation-start-key", default="rotation_start")
p.add_argument("--rotation-end-key", default="rotation_end")
p.add_argument("--max-gap-hours", type=float, default=0.0)
p.add_argument("--max-breaches", type=int, default=0)
a = p.parse_args()

records: list[dict[str, str]]
if a.json:
    payload = json.loads(pathlib.Path(a.json).read_text())
    if isinstance(payload, dict):
        payload = [payload]
    records = payload
else:
    records = parse_csv(pathlib.Path(a.csv))

breaches = 0
for record in records:
    start_raw = record.get(a.rotation_start_key, "")
    end_raw = record.get(a.rotation_end_key, "")
    if not start_raw or not end_raw:
        continue
    gap_hours = (parse_ts(end_raw) - parse_ts(start_raw)).total_seconds() / 3600.0
    if gap_hours > a.max_gap_hours:
        breaches += 1

if breaches > a.max_breaches:
    print("B91 attestation rotation gap gate failed", file=sys.stderr)
    raise SystemExit(2)
