#!/usr/bin/env python3
"""Create signed attestation for governance contract report JSON."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate governance contract report attestation.")
    parser.add_argument("--report-json", required=True, help="Path to governance contract report JSON")
    parser.add_argument("--attestation-out", required=True, help="Path to write attestation JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report_path = Path(args.report_json)
    attestation_path = Path(args.attestation_out)
    report_sha256 = _sha256_file(report_path)

    payload = {
        "attestation_version": 1,
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "report_path": str(report_path),
        "report_sha256": report_sha256,
        "provenance": {
            "repository": os.environ.get("GITHUB_REPOSITORY", ""),
            "workflow": os.environ.get("GITHUB_WORKFLOW", ""),
            "run_id": os.environ.get("GITHUB_RUN_ID", ""),
            "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", ""),
            "ref": os.environ.get("GITHUB_REF", ""),
            "sha": os.environ.get("GITHUB_SHA", ""),
            "job": os.environ.get("GITHUB_JOB", ""),
        },
    }

    attestation_path.parent.mkdir(parents=True, exist_ok=True)
    attestation_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(attestation_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
