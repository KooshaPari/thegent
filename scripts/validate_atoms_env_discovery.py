#!/usr/bin/env python3
"""Validate Atoms env-discovery contract with explicit source ordering."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Final


ROOT: Final = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT: Final = ROOT


@dataclass(frozen=True)
class ContractRequirement:
    keys: tuple[str, ...]
    secrets_aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class RepoContract:
    repo_path: Path
    requirements: tuple[ContractRequirement, ...]
    secrets_path: Path


REPO_CONTRACTS: dict[str, RepoContract] = {
    "atoms-mcp-prod": RepoContract(
        repo_path=WORKSPACE_ROOT / "atoms-mcp-prod",
        requirements=(
            ContractRequirement(keys=("SUPABASE_URL",)),
            ContractRequirement(keys=("SUPABASE_KEY",)),
            ContractRequirement(keys=("FASTMCP_SERVER_AUTH_AUTHKITPROVIDER_AUTHKIT_DOMAIN",)),
            ContractRequirement(keys=("FASTMCP_SERVER_AUTHKITPROVIDER_BASE_URL",)),
            ContractRequirement(keys=("WORKOS_API_KEY",)),
            ContractRequirement(keys=("WORKOS_CLIENT_ID",)),
            ContractRequirement(keys=("CRON_SECRET",)),
        ),
        secrets_path=WORKSPACE_ROOT / "atoms-mcp-prod" / "config" / "secrets.yml",
    ),
    "atomsagent": RepoContract(
        repo_path=WORKSPACE_ROOT / "agentapi" / "atomsAgent",
        requirements=(
            ContractRequirement(keys=("ATOMS_SECRET_AUTHKIT_JWKS_URL",)),
            ContractRequirement(keys=("ATOMS_SECRET_SUPABASE_URL",)),
            ContractRequirement(
                keys=("ATOMS_SECRET_SUPABASE_KEY", "ATOMS_SECRET_SUPABASE_SERVICE_KEY"),
                secrets_aliases=("supabase_service_key", "supabase_key", "supabase_service_role_key"),
            ),
            ContractRequirement(
                keys=("ATOMS_SECRET_VERTEX_PROJECT_ID",),
                secrets_aliases=("vertex_project_id",),
            ),
            ContractRequirement(
                keys=("ATOMS_SECRET_VERTEX_LOCATION",),
                secrets_aliases=("vertex_location",),
            ),
        ),
        secrets_path=WORKSPACE_ROOT / "agentapi" / "atomsAgent" / "config" / "secrets.yml",
    ),
}


def parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def parse_yaml_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    try:
        import yaml
    except ModuleNotFoundError as exc:
        raise RuntimeError("PyYAML is required for config/secrets.yml parsing") from exc

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return {}

    flattened: dict[str, str] = {}

    def walk(prefix: str, value: object) -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                next_prefix = f"{prefix}.{key}" if prefix else key
                walk(next_prefix, nested)
        elif value is not None:
            flattened[prefix] = str(value)

    walk("", raw)
    return flattened


def discovery_paths(repo_root: Path) -> list[tuple[str, Path]]:
    candidate_paths = [
        ("repo/.env.local", repo_root / ".env.local"),
        ("repo/.env", repo_root / ".env"),
        (
            "clean/deploy/atoms.tech/.env.local",
            WORKSPACE_ROOT / "clean" / "deploy" / "atoms.tech" / ".env.local",
        ),
        (
            "clean/deploy/atoms.tech/.env",
            WORKSPACE_ROOT / "clean" / "deploy" / "atoms.tech" / ".env",
        ),
    ]

    for ancestor in repo_root.parents[:3]:
        candidate_paths.append((f"{ancestor}/atoms.tech/.env.local", ancestor / "atoms.tech" / ".env.local"))
        candidate_paths.append((f"{ancestor}/atoms.tech/.env", ancestor / "atoms.tech" / ".env"))

    return candidate_paths


def resolve_required_value(
    requirement: ContractRequirement,
    repo_root: Path,
    secret_values: dict[str, str],
) -> tuple[str, str] | None:
    for key in requirement.keys:
        if os.environ.get(key):
            return key, "environment"

    for source, path in discovery_paths(repo_root):
        values = parse_env_file(path)
        for key in requirement.keys:
            if values.get(key):
                return key, source

    for alias in requirement.secrets_aliases:
        if alias and secret_values.get(alias):
            return alias, "config/secrets.yml"

    return None


def build_findings(contract: RepoContract) -> tuple[bool, dict[str, object]]:
    needs_secrets = any(requirement.secrets_aliases for requirement in contract.requirements)
    secret_values = parse_yaml_file(contract.secrets_path) if needs_secrets else {}
    resolved = []
    missing = []

    for requirement in contract.requirements:
        result = resolve_required_value(requirement, contract.repo_path, secret_values)
        if result is None:
            missing.append({"required": list(requirement.keys), "aliases": list(requirement.secrets_aliases)})
            continue

        resolved_key, source = result
        resolved.append({"required": requirement.keys[0], "resolved_as": resolved_key, "source": source})

    return (not missing, {"resolved": resolved, "missing": missing})


def format_report(profile: str, findings: dict[str, object]) -> str:
    status = "passed" if not findings["missing"] else "failed"
    lines = [f"Env-discovery check for {profile}", f"status: {status}", ""]
    lines.append("resolved:")
    for item in findings["resolved"]:  # type: ignore[union-attr]
        resolved = item["resolved_as"]  # type: ignore[index]
        source = item["source"]  # type: ignore[index]
        lines.append(f"- {item['required']}: ok ({resolved} from {source})")  # type: ignore[index]

    lines.append("")
    if findings["missing"]:
        lines.append("missing:")
        for item in findings["missing"]:  # type: ignore[union-attr]
            required = ", ".join(item["required"])  # type: ignore[index]
            lines.append(f"- {required}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Atoms env-discovery contract")
    parser.add_argument(
        "--repo",
        required=True,
        choices=(*REPO_CONTRACTS.keys(), "atoms-agent"),
        help="Repository target (atoms-mcp-prod or atomsagent)",
    )
    parser.add_argument(
        "--strict",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="return non-zero when required variables are missing",
    )
    parser.add_argument("--output", default=None, help="optional JSON output path")
    args = parser.parse_args()

    repo_id = "atomsagent" if args.repo == "atoms-agent" else args.repo
    contract = REPO_CONTRACTS[repo_id]
    ok, findings = build_findings(contract)
    findings["status"] = "passed" if ok else "failed"
    print(format_report(args.repo, findings))

    if args.output:
        Path(args.output).write_text(
            json.dumps(
                {
                    "repo": args.repo,
                    "status": findings["status"],
                    "resolved": findings["resolved"],
                    "missing": findings["missing"],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    if not ok and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
