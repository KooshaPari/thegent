"""Agent browser command helpers and journey registry."""

from __future__ import annotations

import orjson as json
import os
import subprocess
from thegent.infra.shim_subprocess import run as shim_run
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def _default_profile_dir() -> Path:
    """Default persistent profile directory for agent-browser."""
    return Path.home() / "Library" / "Application Support" / "thegent" / "agent-browser-profile"


def _app_bundle_dir() -> Path:
    """Path to generated local Agent Browser app bundle."""
    return Path.home() / "Library" / "Application Support" / "thegent" / "Agent Browser.app"


def _app_symlink_path() -> Path:
    """Path to visible Agent Browser symlink in ~/Library/Applications."""
    return Path.home() / "Library" / "Applications" / "Agent Browser.app"


def _agent_browser_bin() -> str:
    """Resolve configured agent-browser launcher path."""
    return os.environ.get("THGENT_AGENT_BROWSER_BIN", str(Path.home() / "bin" / "agent-browser"))


def _journeys_path() -> Path:
    """Path to persisted browser journeys registry."""
    return Path(".thegent") / "browser" / "journeys.json"


def _load_journeys() -> list[dict[str, Any]]:
    path = _journeys_path()
    if not path.exists():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        console.print(f"[red]Invalid journeys file: {path} ({exc})[/red]")
        raise typer.Exit(1) from exc
    if not isinstance(raw, list):
        console.print(f"[red]Invalid journeys file format at {path}; expected a list.[/red]")
        raise typer.Exit(1)
    return [item for item in raw if isinstance(item, dict)]


def _save_journeys(journeys: list[dict[str, Any]]) -> None:
    path = _journeys_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(journeys, indent=2), sort_keys=True).decode() + "\n", encoding="utf-8")


def _launcher_script_content() -> str:
    """Portable launcher with Edge-first policy and observable/headless support."""
    return """#!/usr/bin/env bash
set -euo pipefail

BROWSER="auto"
HEADLESS=0
CDP_PORT="${AGENT_BROWSER_DEBUG_PORT:-9222}"
URL=""
ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --browser)
      BROWSER="${2:-auto}"
      shift 2
      ;;
    --headless)
      HEADLESS=1
      shift
      ;;
    --show)
      HEADLESS=0
      shift
      ;;
    --cdp-port)
      CDP_PORT="${2:-9222}"
      shift 2
      ;;
    --url)
      URL="${2:-}"
      shift 2
      ;;
    --version)
      echo "agent-browser 1"
      exit 0
      ;;
    --)
      shift
      ARGS+=("$@")
      break
      ;;
    *)
      ARGS+=("$1")
      shift
      ;;
  esac
done

PROFILE_DIR="${AGENT_BROWSER_PROFILE_DIR:-$HOME/Library/Application Support/thegent/agent-browser-profile}"
PROFILE_NAME="${AGENT_BROWSER_PROFILE_NAME:-Default}"
LOG_FILE="${AGENT_BROWSER_LOG_FILE:-$HOME/Library/Logs/agent-browser.log}"
mkdir -p "$(dirname "$PROFILE_DIR")" "$(dirname "$LOG_FILE")"
mkdir -p "$PROFILE_DIR"

EDGE_BIN="/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
CHROME_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

resolve_bin() {
  case "$1" in
    edge|msedge)
      [[ -x "$EDGE_BIN" ]] && { echo "$EDGE_BIN"; return 0; }
      ;;
    chrome)
      [[ -x "$CHROME_BIN" ]] && { echo "$CHROME_BIN"; return 0; }
      ;;
    auto|*)
      if [[ -x "$EDGE_BIN" ]]; then echo "$EDGE_BIN"; return 0; fi
      if [[ -x "$CHROME_BIN" ]]; then echo "$CHROME_BIN"; return 0; fi
      ;;
  esac
  return 1
}

BIN="$(resolve_bin "$BROWSER")" || {
  echo "No supported browser found (need Microsoft Edge or Google Chrome)." >&2
  exit 1
}

CMD=(
  "$BIN"
  "--user-data-dir=$PROFILE_DIR"
  "--profile-directory=$PROFILE_NAME"
  "--remote-debugging-port=$CDP_PORT"
  "--no-first-run"
  "--no-default-browser-check"
)
if [[ $HEADLESS -eq 1 ]]; then
  CMD+=("--headless=new")
fi
if [[ -n "$URL" ]]; then
  CMD+=("$URL")
fi
CMD+=("${ARGS[@]}")

echo "Executing: ${CMD[*]}" >> "$LOG_FILE"
exec "${CMD[@]}"
"""


def _app_launcher_content() -> str:
    """Agent Browser app wrapper that delegates to launcher script."""
    launcher = Path(_agent_browser_bin()).expanduser()
    return f"""#!/usr/bin/env bash
set -euo pipefail
export AGENT_BROWSER_PROFILE_DIR="${{AGENT_BROWSER_PROFILE_DIR:-{_default_profile_dir()}}}"
export AGENT_BROWSER_PROFILE_NAME="${{AGENT_BROWSER_PROFILE_NAME:-Default}}"
export AGENT_BROWSER_DEBUG_PORT="${{AGENT_BROWSER_DEBUG_PORT:-9222}}"
exec "{launcher}" --browser auto --show "$@"
"""


def browser_install_cmd(force: bool = False) -> None:
    """Install or update the universal agent-browser launcher and app symlink."""
    launcher = Path(_agent_browser_bin()).expanduser()
    launcher.parent.mkdir(parents=True, exist_ok=True)
    if launcher.exists() and not force:
        console.print(f"[dim]Launcher already exists: {launcher} (use --force to overwrite)[/dim]")
    else:
        launcher.write_text(_launcher_script_content(), encoding="utf-8")
        launcher.chmod(0o755)
        console.print(f"[green]Installed launcher:[/green] {launcher}")

    profile_dir = _default_profile_dir()
    profile_dir.mkdir(parents=True, exist_ok=True)
    console.print(f"[green]Ensured profile dir:[/green] {profile_dir}")

    app_bundle = _app_bundle_dir()
    app_macos = app_bundle / "Contents" / "MacOS"
    app_macos.mkdir(parents=True, exist_ok=True)
    app_launcher = app_macos / "agent-browser-app"
    app_launcher.write_text(_app_launcher_content(), encoding="utf-8")
    app_launcher.chmod(0o755)

    app_symlink = _app_symlink_path()
    app_symlink.parent.mkdir(parents=True, exist_ok=True)
    if app_symlink.exists() or app_symlink.is_symlink():
        app_symlink.unlink()
    app_symlink.symlink_to(app_bundle)
    console.print(f"[green]Installed app symlink:[/green] {app_symlink} -> {app_bundle}")


def browser_doctor_checks() -> list[tuple[str, bool, str]]:
    """Collect doctor checks for launcher/app/profile health."""
    bin_path = Path(_agent_browser_bin()).expanduser()
    profile_dir = _default_profile_dir()
    log_dir = Path.home() / "Library" / "Logs"
    app_symlink = _app_symlink_path()

    return [
        ("Launcher", bin_path.exists(), str(bin_path)),
        ("Launcher executable", os.access(bin_path, os.X_OK), str(bin_path)),
        ("Default profile", profile_dir.exists(), str(profile_dir)),
        ("App symlink", app_symlink.exists(), str(app_symlink)),
        ("Log directory", log_dir.exists(), str(log_dir)),
    ]


def browser_doctor_cmd() -> None:
    """Check whether agent-browser prerequisites are installed."""
    table = Table(title="Agent Browser Doctor")
    table.add_column("Check", style="cyan")
    table.add_column("Status")
    table.add_column("Value", style="dim")

    checks = browser_doctor_checks()
    for name, ok, value in checks:
        table.add_row(name, "[green]OK[/green]" if ok else "[red]MISSING[/red]", value)

    console.print(table)
    if not all(ok for _, ok, _ in checks):
        raise typer.Exit(1)


def browser_launch_cmd(
    browser: str = "auto",
    headless: bool = False,
    cdp_port: int = 9222,
    url: str | None = None,
) -> None:
    """Launch the agent browser wrapper."""
    bin_path = Path(_agent_browser_bin()).expanduser()
    if not bin_path.exists():
        console.print(f"[red]agent-browser launcher not found at {bin_path}[/red]")
        raise typer.Exit(1)
    if not os.access(bin_path, os.X_OK):
        console.print(f"[red]agent-browser is not executable: {bin_path}[/red]")
        raise typer.Exit(1)

    cmd = [str(bin_path), "--browser", browser, "--cdp-port", str(cdp_port)]
    cmd.append("--headless" if headless else "--show")
    if url:
        cmd.extend(["--url", url])

    console.print(f"[cyan]Launching:[/cyan] {' '.join(cmd)}")
    shim_run(cmd, check=True)


def browser_journey_add_cmd(
    name: str,
    url: str,
    kind: str = "auth",
    notes: str | None = None,
) -> None:
    """Add or replace a named browser journey."""
    if kind not in {"auth", "task"}:
        console.print("[red]kind must be one of: auth, task[/red]")
        raise typer.Exit(1)

    journeys = _load_journeys()
    now = datetime.now(UTC).isoformat()
    record = {
        "name": name,
        "url": url,
        "kind": kind,
        "notes": notes or "",
        "updated_at": now,
    }

    replaced = False
    for idx, item in enumerate(journeys):
        if item.get("name") == name:
            journeys[idx] = record
            replaced = True
            break
    if not replaced:
        journeys.append(record)

    _save_journeys(journeys)
    action = "Updated" if replaced else "Added"
    console.print(f"[green]{action} journey:[/green] {name} -> {url}")
    console.print(f"[dim]Registry: {_journeys_path()}[/dim]")


def browser_journey_list_cmd() -> None:
    """List registered browser journeys."""
    journeys = _load_journeys()
    if not journeys:
        console.print("[yellow]No browser journeys registered.[/yellow]")
        console.print("[dim]Use: thegent browser journey add <name> --url <url>[/dim]")
        return

    table = Table(title="Agent Browser Journeys")
    table.add_column("Name", style="cyan")
    table.add_column("Kind", style="green")
    table.add_column("URL", style="blue")
    table.add_column("Updated", style="dim")
    table.add_column("Notes")

    for item in sorted(journeys, key=lambda x: str(x.get("name", ""))):
        table.add_row(
            str(item.get("name", "")),
            str(item.get("kind", "")),
            str(item.get("url", "")),
            str(item.get("updated_at", "")),
            str(item.get("notes", "")),
        )
    console.print(table)


def browser_journey_open_cmd(
    name: str,
    browser: str = "auto",
    headless: bool = False,
    cdp_port: int = 9222,
) -> None:
    """Launch a named journey in agent browser."""
    journeys = _load_journeys()
    selected = next((item for item in journeys if item.get("name") == name), None)
    if selected is None:
        console.print(f"[red]Journey not found:[/red] {name}")
        raise typer.Exit(1)
    url = str(selected.get("url", "")).strip()
    if not url:
        console.print(f"[red]Journey has empty URL:[/red] {name}")
        raise typer.Exit(1)
    browser_launch_cmd(browser=browser, headless=headless, cdp_port=cdp_port, url=url)
