#!/usr/bin/env python3
"""Fail fast when Rust workspace resolves conflicting native links providers."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


WORKSPACE_MANIFEST = Path("crates") / "Cargo.toml"


def _run_cargo_metadata(repo_root: Path) -> dict[str, Any]:
    manifest_path = repo_root / WORKSPACE_MANIFEST
    completed = subprocess.run(
        [
            "cargo",
            "metadata",
            "--format-version",
            "1",
            "--manifest-path",
            str(manifest_path),
        ],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    if not isinstance(payload, dict):
        raise ValueError("cargo metadata output was not a JSON object")
    return payload


def build_report_from_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    packages = metadata.get("packages")
    if not isinstance(packages, list):
        raise ValueError("cargo metadata missing packages list")

    links_to_providers: dict[str, set[str]] = {}
    links_to_package_ids: dict[str, list[str]] = {}

    for pkg in packages:
        if not isinstance(pkg, dict):
            continue
        links = pkg.get("links")
        if not isinstance(links, str) or links.strip() == "":
            continue

        name = pkg.get("name", "<unknown>")
        version = pkg.get("version", "<unknown>")
        package_id = pkg.get("id", f"{name} {version}")
        provider = f"{name}@{version}"

        links_to_providers.setdefault(links, set()).add(provider)
        links_to_package_ids.setdefault(links, []).append(str(package_id))

    conflicts: list[dict[str, Any]] = []
    for links, providers in sorted(links_to_providers.items()):
        if len(providers) <= 1:
            continue
        conflicts.append(
            {
                "links": links,
                "providers": sorted(providers),
                "package_ids": sorted(set(links_to_package_ids.get(links, []))),
            }
        )

    return {
        "ok": len(conflicts) == 0,
        "total_links_entries": len(links_to_providers),
        "conflicts": conflicts,
    }


def build_report(repo_root: Path) -> dict[str, Any]:
    metadata = _run_cargo_metadata(repo_root)
    return build_report_from_metadata(metadata)


def _print_text_report(report: dict[str, Any]) -> None:
    print("Rust native links conflict preflight")
    print(f"- ok: {report['ok']}")
    print(f"- total_links_entries: {report['total_links_entries']}")
    if not report["conflicts"]:
        return
    for conflict in report["conflicts"]:
        print(f"- conflict: links={conflict['links']}")
        for provider in conflict["providers"]:
            print(f"  - provider: {provider}")


def main(argv: list[str] | None = None) -> int:
    args = list(argv or sys.argv[1:])
    if args and args != ["--json"]:
        print("usage: check_rust_links_conflicts.py [--json]", file=sys.stderr)
        return 2

    report = build_report(Path.cwd())
    if args == ["--json"]:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _print_text_report(report)

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
