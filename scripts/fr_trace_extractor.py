#!/usr/bin/env python3
"""Dedicated FR traceability extractor entrypoint.

Builds pytest requirement mapping artifacts:
- requirement -> [tests]
- test -> [requirements]
- coverage gaps from FR tracker
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.test_pytest_wave_artifacts import DEFAULT_INPUT_DIR
from scripts.test_pytest_wave_artifacts import REQUIREMENTS_MAP_DIAGRAM_MAX_REQUIREMENTS
from scripts.test_pytest_wave_artifacts import ROOT
from scripts.test_pytest_wave_artifacts import parse_fr_tracker
from scripts.test_pytest_wave_artifacts import run_requirements_map
from scripts.test_pytest_wave_artifacts import scan_tests


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    parser.add_argument("--fr-tracker", default=str(ROOT / "docs/reference/FR_TRACKER.md"))
    parser.add_argument("--output", required=True)
    parser.add_argument("--csv-output")
    parser.add_argument("--summary")
    parser.add_argument("--diagram-output")
    parser.add_argument("--diagram-max-nodes", type=int, default=REQUIREMENTS_MAP_DIAGRAM_MAX_REQUIREMENTS)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    input_dir = Path(args.input_dir).resolve()
    fr_tracker = Path(args.fr_tracker)
    output = Path(args.output)
    csv_output = Path(args.csv_output) if args.csv_output else None
    summary = Path(args.summary) if args.summary else None
    diagram_output = Path(args.diagram_output) if args.diagram_output else None

    records = scan_tests(input_dir)
    req_ids = parse_fr_tracker(fr_tracker)
    run_requirements_map(
        records,
        output,
        req_ids,
        csv_output,
        summary=summary,
        diagram_output=diagram_output,
        diagram_max_nodes=args.diagram_max_nodes,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
