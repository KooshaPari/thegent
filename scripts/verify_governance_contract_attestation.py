#!/usr/bin/env python3
"""Verify governance contract report attestation integrity."""

from __future__ import annotations

import argparse
import hashlib
import orjson as json
from pathlib import Path


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify governance contract report attestation.")
    parser.add_argument("--report-json", required=True, help="Path to governance contract report JSON")
    parser.add_argument("--attestation-json", required=True, help="Path to attestation JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report_path = Path(args.report_json)
    attestation_path = Path(args.attestation_json)
    attestation = json.loads(attestation_path.read_text(encoding="utf-8"))

    if attestation.get("attestation_version") != 1:
        print("invalid attestation_version")
        return 2
    if not isinstance(attestation.get("generated_at"), str) or not attestation["generated_at"]:
        print("missing generated_at")
        return 2

    reported_sha = attestation.get("report_sha256")
    actual_sha = _sha256_file(report_path)
    if reported_sha != actual_sha:
        print(f"report digest mismatch: expected={reported_sha} actual={actual_sha}")
        return 2

    provenance = attestation.get("provenance", {})
    for key in ("repository", "workflow", "run_id", "run_attempt", "ref", "sha", "job"):
        if key not in provenance:
            print(f"missing provenance field: {key}")
            return 2

    print("governance contract attestation verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
