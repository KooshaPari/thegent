#!/usr/bin/env python3
"""Deep verification for Antigma docs, auth flow, and CLI drift.

Outputs:
  - docs/research/antigma/antigma_inventory.json
  - docs/research/antigma/antigma_drift_report.md
"""

from __future__ import annotations

import argparse
import orjson as json
import re
import shlex
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "research" / "antigma"

DOCS_BASE = "https://docs.antigma.ai"
INSTALL_SCRIPT_URL = "https://anen.ai/install.sh"
INSTALL_MANIFEST_URL = "https://anen.ai/install-manifest"
PAGES = [
    "/start/overview",
    "/start/quickstart",
    "/usage/headless",
    "/usage/tui",
    "/concepts/core-concepts",
    "/concepts/architecture",
    "/configuration/catalog",
    "/configuration/preference",
    "/configuration/third-party-provider",
    "/tools",
    "/extend/skills",
    "/extend/subagents",
    "/memory",
]

FLAG_RE = re.compile(r"--[a-z][a-z0-9-]*")
ENV_RE = re.compile(r"\b[A-Z][A-Z0-9_]{2,}\b")
ANTE_CMD_RE = re.compile(r"\bante(?:\s+[^\n\"]+)")


def _run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def _run_checked(cmd: list[str], *, cwd: Path | None = None, timeout: int = 120) -> str:
    proc = _run(cmd, cwd=cwd, timeout=timeout)
    if proc.returncode != 0:
        joined = shlex.join(cmd)
        raise RuntimeError(f"Command failed ({proc.returncode}): {joined}\n{proc.stderr.strip()}")
    return proc.stdout


def _curl_text(url: str) -> str:
    return _run_checked(["curl", "-fsSL", url], timeout=120)


def _curl_headers(url: str) -> str:
    return _run_checked(["curl", "-sSIL", url], timeout=120)


def _extract_snapshot_path(output: str) -> Path:
    match = re.search(r"\[Snapshot\]\(([^)]+)\)", output)
    if not match:
        raise RuntimeError(f"No snapshot path found in output:\n{output}")
    rel = match.group(1)
    path = Path.home() / rel
    if not path.exists():
        raise RuntimeError(f"Snapshot file not found: {path}")
    return path


def _extract_network_path(output: str) -> Path:
    match = re.search(r"\[Network\]\(([^)]+)\)", output)
    if not match:
        raise RuntimeError(f"No network path found in output:\n{output}")
    rel = match.group(1)
    path = Path.home() / rel
    if not path.exists():
        raise RuntimeError(f"Network log not found: {path}")
    return path


def _playwright_cmd() -> list[str]:
    script = Path.home() / ".codex" / "skills" / "playwright" / "scripts" / "playwright_cli.sh"
    if not script.exists():
        raise RuntimeError(f"Playwright skill wrapper not found: {script}")
    return ["bash", str(script)]


def _pw(session: str, *args: str, timeout: int = 120) -> str:
    cmd = _playwright_cmd() + ["--session", session, *args]
    return _run_checked(cmd, timeout=timeout)


def _find_ante_bin() -> Path:
    candidates = [
        Path.home() / ".ante" / "bin" / "ante",
        Path("/opt/homebrew/bin/ante"),
        Path("/usr/local/bin/ante"),
    ]
    for path in candidates:
        if path.exists() and path.is_file():
            return path
    which = _run(["which", "ante"], timeout=20)
    if which.returncode == 0 and which.stdout.strip():
        return Path(which.stdout.strip())
    raise RuntimeError("Could not locate ante binary")


def _parse_runtime_flags(help_text: str) -> set[str]:
    flags = set(FLAG_RE.findall(help_text))
    return {f for f in flags if f not in {"--help", "--version"}}


def _parse_runtime_providers(help_text: str) -> set[str]:
    match = re.search(r"one of:\s*([^)]+)\)", help_text)
    if not match:
        return set()
    return {part.strip() for part in match.group(1).split(",") if part.strip()}


def _parse_snapshot(snapshot_path: Path) -> dict[str, Any]:
    text = snapshot_path.read_text(encoding="utf-8", errors="ignore")
    return {
        "path": str(snapshot_path),
        "flags": sorted(set(FLAG_RE.findall(text))),
        "env_vars": sorted(set(ENV_RE.findall(text))),
        "ante_commands": sorted({m.strip() for m in ANTE_CMD_RE.findall(text)}),
    }


def _extract_provider_ids_from_catalog(snapshot_path: Path) -> set[str]:
    text = snapshot_path.read_text(encoding="utf-8", errors="ignore")
    providers = set()
    for match in re.finditer(r"code \[ref=.*?\]: ([a-z][a-z0-9-]*)", text):
        token = match.group(1)
        if token in {"anthropic", "openai", "openai-response", "gemini", "open-router", "xai", "local"}:
            providers.add(token)
    return providers


def _extract_auth_endpoints(network_log: Path) -> list[str]:
    lines = network_log.read_text(encoding="utf-8", errors="ignore").splitlines()
    endpoints = []
    for line in lines:
        if "login/callback/password" in line or "_mintlify" in line:
            endpoints.append(line.strip())
    return endpoints


def _run_verification(access_code: str, session: str) -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    install_headers = _curl_headers(INSTALL_SCRIPT_URL)
    install_script = _curl_text(INSTALL_SCRIPT_URL)
    manifest_headers = _curl_headers(INSTALL_MANIFEST_URL)
    manifest_text = _curl_text(INSTALL_MANIFEST_URL)
    manifest = json.loads(manifest_text)

    # Reset session (best effort).
    _run(_playwright_cmd() + ["--session", session, "close"], timeout=30)

    login_url = f"{DOCS_BASE}/login?redirect=%2F"
    _pw(session, "open", login_url, "--headed", timeout=120)
    login_snapshot_output = _pw(session, "snapshot", timeout=120)
    login_snapshot = _extract_snapshot_path(login_snapshot_output)

    # These refs are stable on the login page after snapshot.
    _pw(session, "fill", "e15", access_code, timeout=120)
    _pw(session, "click", "e17", timeout=120)

    # Capture network right after auth click.
    network_output = _pw(session, "network", timeout=120)
    network_log = _extract_network_path(network_output)

    page_artifacts: dict[str, dict[str, Any]] = {}
    for page in PAGES:
        full_url = f"{DOCS_BASE}{page}"
        _pw(session, "goto", full_url, timeout=120)
        snap_out = _pw(session, "snapshot", timeout=120)
        snap_path = _extract_snapshot_path(snap_out)
        parsed = _parse_snapshot(snap_path)
        parsed["url"] = full_url
        page_artifacts[page] = parsed

    ante_bin = _find_ante_bin()
    ante_version = _run_checked([str(ante_bin), "--version"], timeout=30).strip()
    ante_help = _run_checked([str(ante_bin), "--help"], timeout=30)
    runtime_flags = _parse_runtime_flags(ante_help)
    runtime_providers = _parse_runtime_providers(ante_help)

    headless_page = page_artifacts["/usage/headless"]
    doc_headless_flags = {f for f in headless_page["flags"] if f.startswith("--")}
    catalog_provider_ids = _extract_provider_ids_from_catalog(Path(page_artifacts["/configuration/catalog"]["path"]))

    missing_in_runtime = sorted(doc_headless_flags - runtime_flags)
    undocumented_runtime = sorted(runtime_flags - doc_headless_flags)
    provider_missing_in_runtime = sorted(catalog_provider_ids - runtime_providers)
    provider_undocumented = sorted(runtime_providers - catalog_provider_ids)

    inventory = {
        "generated_at": datetime.now(UTC).isoformat(),
        "docs_base": DOCS_BASE,
        "install_script_url": INSTALL_SCRIPT_URL,
        "install_manifest_url": INSTALL_MANIFEST_URL,
        "install_script_headers": install_headers,
        "manifest_headers": manifest_headers,
        "manifest": manifest,
        "login_page": str(login_snapshot),
        "auth_endpoints": _extract_auth_endpoints(network_log),
        "network_log": str(network_log),
        "pages": page_artifacts,
        "runtime": {
            "ante_bin": str(ante_bin),
            "version": ante_version,
            "help": ante_help,
            "flags": sorted(runtime_flags),
            "providers": sorted(runtime_providers),
        },
        "drift": {
            "doc_headless_flags": sorted(doc_headless_flags),
            "missing_in_runtime": missing_in_runtime,
            "undocumented_runtime": undocumented_runtime,
            "catalog_provider_ids": sorted(catalog_provider_ids),
            "provider_missing_in_runtime": provider_missing_in_runtime,
            "provider_undocumented": provider_undocumented,
        },
    }
    return inventory


def _write_outputs(inventory: dict[str, Any]) -> tuple[Path, Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / "antigma_inventory.json"
    md_path = OUT_DIR / "antigma_drift_report.md"
    json_path.write_text(json.dumps(inventory, indent=2).decode().decode(), encoding="utf-8")

    drift = inventory["drift"]
    lines = [
        "# Antigma Docs vs Runtime Drift Report",
        "",
        f"- Generated: {inventory['generated_at']}",
        f"- Runtime binary: `{inventory['runtime']['ante_bin']}`",
        f"- Runtime version: `{inventory['runtime']['version']}`",
        "",
        "## Auth Flow Evidence",
        "",
        "- Login endpoint evidence:",
    ]
    for endpoint in inventory["auth_endpoints"]:
        lines.append(f"  - `{endpoint}`")

    lines.extend(
        [
            "",
            "## Headless Flag Drift",
            "",
            f"- Docs flags count: `{len(drift['doc_headless_flags'])}`",
            f"- Runtime flags count: `{len(inventory['runtime']['flags'])}`",
            f"- Missing in runtime: `{', '.join(drift['missing_in_runtime']) or 'none'}`",
            f"- Undocumented runtime flags: `{', '.join(drift['undocumented_runtime']) or 'none'}`",
            "",
            "## Provider Drift",
            "",
            f"- Docs provider IDs: `{', '.join(drift['catalog_provider_ids'])}`",
            f"- Runtime providers: `{', '.join(inventory['runtime']['providers'])}`",
            f"- In docs but not runtime: `{', '.join(drift['provider_missing_in_runtime']) or 'none'}`",
            f"- In runtime but not docs: `{', '.join(drift['provider_undocumented']) or 'none'}`",
            "",
            "## Artifacts",
            "",
            f"- Inventory JSON: `{json_path}`",
            f"- Network log: `{inventory['network_log']}`",
        ]
    )

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Deep DRP verification for Antigma docs and CLI.")
    parser.add_argument("--access-code", default="ante-preview-discord", help="Docs access code")
    parser.add_argument("--session", default="antigma-verify", help="Playwright session name")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when any drift is detected",
    )
    args = parser.parse_args()

    inventory = _run_verification(args.access_code, args.session)
    json_path, md_path = _write_outputs(inventory)

    drift = inventory["drift"]
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    print("Missing flags in runtime:", ", ".join(drift["missing_in_runtime"]) or "none")
    print("Missing providers in runtime:", ", ".join(drift["provider_missing_in_runtime"]) or "none")

    has_drift = bool(drift["missing_in_runtime"] or drift["provider_missing_in_runtime"])
    if args.strict and has_drift:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
