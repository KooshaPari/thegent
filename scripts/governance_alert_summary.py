#!/usr/bin/env python3
"""Emit GitHub Step Summary markdown for governance selector logs."""

from __future__ import annotations

import argparse
from pathlib import Path

from thegent.governance_alert_parser import render_markdown_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render governance selector markdown summary from log text.")
    parser.add_argument("--log", required=True, help="Path to governance selector log file")
    parser.add_argument("--title", required=True, help="Markdown section title")
    parser.add_argument("--max-signal-lines", type=int, default=40, help="Max fail-closed signal lines to include")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    log_path = Path(args.log)
    log_text = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    print(render_markdown_summary(args.title, log_text, max_signal_lines=args.max_signal_lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

