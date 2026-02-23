#!/usr/bin/env python3
"""Emit a WL-135 SLO metric stub payload.

Writes a JSON payload to stdout and optionally appends JSONL rows for local
report/dashboard prototyping.
"""

from __future__ import annotations

import argparse
import orjson as json
from pathlib import Path

from thegent.metrics.collector import MetricsCollector


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metric", required=True, help="SLO metric name, e.g. cli_help_p95_ms")
    parser.add_argument("--value", type=float, required=True, help="Observed metric value")
    parser.add_argument("--threshold", type=float, default=None, help="Optional pass/fail threshold")
    parser.add_argument("--lane", default="fast-lane", help="Lane label")
    parser.add_argument(
        "--jsonl",
        type=Path,
        default=None,
        help="Optional JSONL output path for appending payload rows",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    collector = MetricsCollector()
    payload = collector.emit_slo_stub(
        args.metric,
        args.value,
        threshold=args.threshold,
        lane=args.lane,
    )

    if args.jsonl is not None:
        args.jsonl.parent.mkdir(parents=True, exist_ok=True)
        with args.jsonl.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, sort_keys=True).decode().decode() + "\n")

    print(json.dumps(payload, sort_keys=True).decode().decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
