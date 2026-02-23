#!/usr/bin/env python3
"""Validate quality control-plane contract and enforce base invariants."""

from __future__ import annotations

import argparse
import orjson as json
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--contract",
        type=Path,
        default=Path("contracts/quality-control-plane-v1.json"),
        help="Control-plane policy contract path",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path("schemas/quality-control-plane-v1.schema.json"),
        help="JSON schema path",
    )
    parser.add_argument(
        "--strict-adr-match",
        action="store_true",
        help="Require selected plane to match ADR-017 decision",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.contract.exists():
        raise FileNotFoundError(f"missing contract: {args.contract}")
    if not args.schema.exists():
        raise FileNotFoundError(f"missing schema: {args.schema}")

    validator = subprocess.run(
        [
            "cargo",
            "run",
            "--manifest-path",
            "crates/thegent-hooks/Cargo.toml",
            "--quiet",
            "--bin",
            "thegent-hooks",
            "--",
            "schema-validate",
            str(args.schema),
            str(args.contract),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if validator.returncode != 0:
        sys.stderr.write(validator.stderr)
        return validator.returncode

    payload = json.loads(args.contract.read_text(encoding="utf-8"))
    selected = payload.get("selected_plane")

    if args.strict_adr_match and selected != "github_sarif_native":
        sys.stderr.write("ADR-017 mismatch: selected_plane must be github_sarif_native\n")
        return 1

    print(
        json.dumps(
            {
                "status": "ok",
                "contract": str(args.contract).decode(),
                "schema": str(args.schema),
                "selected_plane": selected,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
