#!/usr/bin/env python3
"""Verify signed digest manifest for governance fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _aggregate_signature(items: list[dict]) -> str:
    lines = [f"{item['path']}:{item['sha256']}" for item in sorted(items, key=lambda x: x["path"])]
    payload = ("\n".join(lines)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify governance fixture signed digests.")
    parser.add_argument(
        "--manifest",
        default="tests/fixtures/governance/fixture_digests.json",
        help="Path to governance fixture digest manifest",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    root = manifest_path.parent

    files = data.get("files", [])
    for item in files:
        rel = item["path"]
        expected = item["sha256"]
        actual = _sha256_file(root / rel)
        if actual != expected:
            print(f"digest mismatch: {rel} expected={expected} actual={actual}")
            return 2

    expected_signature = data.get("signed_digest", "")
    actual_signature = _aggregate_signature(files)
    if actual_signature != expected_signature:
        print(f"signed digest mismatch: expected={expected_signature} actual={actual_signature}")
        return 2

    print("governance fixture digest verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
