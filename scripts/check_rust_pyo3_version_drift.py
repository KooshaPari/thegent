#!/usr/bin/env python3
"""Fail fast when Rust pyo3 dependency versions drift across crates."""

from __future__ import annotations

import orjson as json
import sys
from pathlib import Path
from typing import Any

import tomllib

DEPENDENCY_TABLE_KEYS = {"dependencies", "dev-dependencies", "build-dependencies"}
WORKSPACE_MANIFEST = Path("crates") / "Cargo.toml"


def _load_toml(path: Path) -> dict[str, Any]:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected TOML document object")
    return data


def _normalize_version(value: str) -> str:
    return " ".join(value.split())


def _extract_workspace_pyo3_version(workspace_doc: dict[str, Any]) -> str | None:
    workspace = workspace_doc.get("workspace")
    if not isinstance(workspace, dict):
        return None

    deps = workspace.get("dependencies")
    if not isinstance(deps, dict):
        return None

    pyo3_spec = deps.get("pyo3")
    if isinstance(pyo3_spec, str):
        return _normalize_version(pyo3_spec)
    if isinstance(pyo3_spec, dict):
        version = pyo3_spec.get("version")
        if isinstance(version, str) and version.strip():
            return _normalize_version(version)
    return None


def _workspace_member_manifests(workspace_root: Path, workspace_doc: dict[str, Any]) -> list[Path]:
    workspace = workspace_doc.get("workspace")
    if not isinstance(workspace, dict):
        raise ValueError(f"{workspace_root / 'Cargo.toml'}: missing [workspace] table")

    raw_members = workspace.get("members")
    if not isinstance(raw_members, list) or not all(isinstance(item, str) for item in raw_members):
        raise ValueError(f"{workspace_root / 'Cargo.toml'}: workspace.members must be a list[str]")

    raw_excludes = workspace.get("exclude", [])
    excludes = {item for item in raw_excludes if isinstance(item, str)}

    manifests: set[Path] = set()
    for member in raw_members:
        if member in excludes:
            continue
        if any(ch in member for ch in "*?[]"):
            for path in workspace_root.glob(f"{member}/Cargo.toml"):
                manifests.add(path.resolve())
            continue
        candidate = workspace_root / member / "Cargo.toml"
        if candidate.exists():
            manifests.add(candidate.resolve())
    return sorted(manifests)


def _iter_dependency_tables(node: dict[str, Any], path: tuple[str, ...] = ()):
    for key, value in node.items():
        if key in DEPENDENCY_TABLE_KEYS and isinstance(value, dict):
            yield path + (key,), value
            continue

        if isinstance(value, dict):
            yield from _iter_dependency_tables(value, path + (key,))


def _format_table_path(path_parts: tuple[str, ...]) -> str:
    if not path_parts:
        return "[dependencies]"
    return "[" + ".".join(path_parts) + "]"


def _extract_declared_version(spec: Any, workspace_pyo3_version: str | None) -> str:
    if isinstance(spec, str):
        if spec.strip() == "":
            raise ValueError("empty version constraint")
        return _normalize_version(spec)

    if not isinstance(spec, dict):
        raise ValueError(f"unsupported dependency spec type: {type(spec).__name__}")

    workspace = spec.get("workspace")
    if workspace is True:
        if workspace_pyo3_version is None:
            raise ValueError("workspace=true but workspace.dependencies.pyo3 has no version")
        return workspace_pyo3_version

    version = spec.get("version")
    if isinstance(version, str) and version.strip() != "":
        return _normalize_version(version)

    raise ValueError("missing version (expected explicit version or workspace=true)")


def collect_pyo3_requirements(repo_root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    workspace_path = repo_root / WORKSPACE_MANIFEST
    workspace_doc = _load_toml(workspace_path)
    workspace_pyo3_version = _extract_workspace_pyo3_version(workspace_doc)
    manifests = _workspace_member_manifests(workspace_path.parent, workspace_doc)

    records: list[dict[str, Any]] = []
    errors: list[str] = []

    for manifest in manifests:
        doc = _load_toml(manifest)
        for table_path, table in _iter_dependency_tables(doc):
            for dep_name, dep_spec in table.items():
                package_name = dep_name
                if isinstance(dep_spec, dict):
                    package_name = str(dep_spec.get("package", dep_name))

                if package_name != "pyo3":
                    continue

                try:
                    version = _extract_declared_version(dep_spec, workspace_pyo3_version)
                except ValueError as exc:
                    errors.append(
                        f"{manifest.relative_to(repo_root)} {_format_table_path(table_path)} {dep_name}: {exc}"
                    )
                    continue

                optional = bool(dep_spec.get("optional", False)) if isinstance(dep_spec, dict) else False
                records.append(
                    {
                        "manifest": str(manifest.relative_to(repo_root)),
                        "table": _format_table_path(table_path),
                        "dependency": dep_name,
                        "version": version,
                        "optional": optional,
                    }
                )

    records.sort(key=lambda item: (item["manifest"], item["table"], item["dependency"]))
    errors.sort()
    return records, errors


def build_report(repo_root: Path) -> dict[str, Any]:
    records, errors = collect_pyo3_requirements(repo_root)
    by_version: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        by_version.setdefault(str(record["version"]), []).append(record)

    drift = len(by_version) > 1
    ok = not errors and not drift
    return {
        "ok": ok,
        "drift": drift,
        "errors": errors,
        "versions": sorted(by_version),
        "total_references": len(records),
        "references": records,
    }


def _print_text_report(report: dict[str, Any]) -> None:
    print("Rust pyo3 version drift preflight")
    print(f"- ok: {report['ok']}")
    print(f"- total_references: {report['total_references']}")
    if report["versions"]:
        print(f"- versions: {', '.join(report['versions'])}")

    for error in report["errors"]:
        print(f"- error: {error}")

    for ref in report["references"]:
        print(
            "- ref: "
            f"{ref['manifest']} {ref['table']} {ref['dependency']}="
            f"{ref['version']} optional={str(ref['optional']).lower()}"
        )


def main(argv: list[str] | None = None) -> int:
    args = list(argv or sys.argv[1:])
    if args and args != ["--json"]:
        print("usage: check_rust_pyo3_version_drift.py [--json]", file=sys.stderr)
        return 2

    report = build_report(Path.cwd())
    if args == ["--json"]:
        print(json.dumps(report, indent=2, sort_keys=True).decode().decode())
    else:
        _print_text_report(report)

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
