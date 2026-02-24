"""MCP configuration and service management for thegent."""

from __future__ import annotations

import orjson as json
import os
import platform
import shutil
from thegent.infra.shim_subprocess import run as shim_run
import time
from pathlib import Path
from typing import Any

from thegent.config import ThegentSettings
from thegent.infra import run_subprocess_optimized

# MCP server URL (HTTP transport)
DEFAULT_MCP_URL = "http://127.0.0.1:3847/mcp"
MCP_SERVER_KEYS: tuple[str, ...] = ("thegent", "codex_apps")

# Client config paths (config dir or file)
MCP_CLIENT_PATHS: dict[str, list[Path]] = {
    "cursor": [
        Path.home() / ".cursor" / "mcp.json",
        Path.cwd() / ".cursor" / "mcp.json",
    ],
    "claude-code": [
        Path.home() / ".claude.json",
    ],
    "codex": [
        Path.home() / ".codex" / "mcp.json",
        Path.home() / ".config" / "codex" / "mcp.json",
        Path.home() / ".codex" / "config.json",
    ],
    "claude-desktop": [
        Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",
    ],
    "droid": [
        Path.cwd() / ".factory" / "mcp.json",
    ],
}


def _get_mcp_url(settings: ThegentSettings) -> str:
    """Build MCP URL from config."""
    host = settings.mcp_host or "127.0.0.1"
    port = settings.mcp_port or 3847
    return f"http://{host}:{port}/mcp"


def _remote_config(url: str) -> dict[str, Any]:
    """Build RemoteMCPServer config dict."""
    return {
        "url": url,
        "transport": "http",
        "description": "Thegent agent orchestration (run, bg, ps, logs, dag, etc.)",
    }


def _ensure_mcp_servers(config: dict[str, Any]) -> dict[str, Any]:
    """Ensure mcpServers key exists; create if missing."""
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    return config


def _set_compatible_mcp_servers(config: dict[str, Any], url: str) -> dict[str, Any]:
    """Write canonical and compatibility MCP server aliases."""
    config = _ensure_mcp_servers(config)

    # Preserve existing settings if present while still ensuring both compatibility aliases exist.
    mcp_servers = config["mcpServers"]
    reference_entry: dict[str, Any] | None = None
    for name in MCP_SERVER_KEYS:
        candidate = mcp_servers.get(name)
        if isinstance(candidate, dict):
            reference_entry = candidate
            break

    # Use the first discovered alias URL as source of truth when available.
    existing_url = url
    for name in MCP_SERVER_KEYS:
        candidate = mcp_servers.get(name)
        if not isinstance(candidate, dict):
            continue
        candidate_url = candidate.get("url")
        if isinstance(candidate_url, str) and candidate_url:
            existing_url = candidate_url
            break

    # Start from a stable remote template and overlay existing fields where present.
    base = dict(_remote_config(existing_url))
    if reference_entry:
        base.update(reference_entry)

    for name in MCP_SERVER_KEYS:
        existing = mcp_servers.get(name)
        merged = dict(base)
        if isinstance(existing, dict):
            merged.update(existing)
        merged.setdefault("url", existing_url)
        mcp_servers[name] = merged
    return config


def install_to_cursor(
    url: str = DEFAULT_MCP_URL,
    workspace: Path | None = None,
) -> bool:
    """Add thegent to Cursor MCP config. Prefers workspace .cursor/mcp.json if present."""
    config_path = workspace.resolve() / ".cursor" / "mcp.json" if workspace else Path.home() / ".cursor" / "mcp.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config: dict[str, Any] = json.loads(config_path.read_text()) if config_path.exists() else {"mcpServers": {}}
    config = _set_compatible_mcp_servers(config, url=url)
    config_path.write_text(json.dumps(config, indent=2))
    return True


def install_to_claude_code(url: str = DEFAULT_MCP_URL) -> bool:
    """Add thegent to Claude Code config (~/.claude.json)."""
    config_path = Path.home() / ".claude.json"
    config: dict[str, Any] = json.loads(config_path.read_text()) if config_path.exists() else {}
    config = _set_compatible_mcp_servers(config, url=url)
    config_path.write_text(json.dumps(config, indent=2))
    return True


def install_to_codex(url: str = DEFAULT_MCP_URL) -> bool:
    """Add thegent to Codex MCP config."""
    config_paths = [
        Path.home() / ".codex" / "mcp.json",
        Path.home() / ".codex" / "config.json",
        Path.home() / ".config" / "codex" / "mcp.json",
    ]
    for config_path in config_paths:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config: dict[str, Any] = json.loads(config_path.read_text()) if config_path.exists() else {"mcpServers": {}}
        config = _set_compatible_mcp_servers(config, url=url)
        config_path.write_text(json.dumps(config, indent=2))
    return True


def install_to_claude_desktop(url: str = DEFAULT_MCP_URL) -> bool:
    """Add thegent to Claude Desktop config (macOS)."""
    config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    if not config_path.parent.exists():
        return False
    config: dict[str, Any] = json.loads(config_path.read_text()) if config_path.exists() else {}
    config = _set_compatible_mcp_servers(config, url=url)
    config_path.write_text(json.dumps(config, indent=2))
    return True


def install_to_droid(url: str, workspace: Path | None = None) -> bool:
    """Add thegent to .factory/mcp.json (project-level, for droids/scripts)."""
    base = (workspace or Path.cwd()).resolve()
    config_path = base / ".factory" / "mcp.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config: dict[str, Any] = json.loads(config_path.read_text()) if config_path.exists() else {"mcpServers": {}}
    config = _set_compatible_mcp_servers(config, url=url)
    config_path.write_text(json.dumps(config, indent=2))
    return True


def install_to_client(
    client: str,
    url: str,
    workspace: Path | None = None,
    replace_all: bool = False,
    force_http: bool = False,
) -> tuple[bool, str]:
    """Install thegent to given MCP client. Returns (success, message)."""
    if client == "cursor":
        try:
            install_to_cursor(url=url, workspace=workspace)
            loc = f"workspace {workspace}" if workspace else "global ~/.cursor"
            return True, f"Installed thegent to cursor ({loc})"
        except Exception as e:
            return False, str(e)
    if client == "droid":
        try:
            install_to_droid(url=url, workspace=workspace)
            loc = f"workspace {workspace or Path.cwd()}" if workspace else "cwd"
            return True, f"Installed thegent to droid config ({loc}/.factory/mcp.json)"
        except Exception as e:
            return False, str(e)
    installers = {
        "claude-code": install_to_claude_code,
        "codex": install_to_codex,
        "claude-desktop": install_to_claude_desktop,
    }
    if client not in installers:
        return False, f"Unknown client: {client}. Use: cursor, claude-code, codex, claude-desktop, droid, all"
    try:
        installers[client](url=url)
        return True, f"Installed thegent to {client}"
    except Exception as e:
        return False, str(e)


# --- Service management (launchd on macOS) ---


def _launchd_plist_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / "com.thegent.mcp.plist"


def _python_exe(settings: ThegentSettings) -> str:
    """Resolve Python executable for thegent."""
    if settings.virtual_env:
        venv = settings.virtual_env
        exe = venv / "bin" / "python"
        if exe.exists():
            return str(exe)
    return shutil.which("python3") or shutil.which("python") or "python3"


def _thegent_serve_cmd(settings: ThegentSettings) -> list[str]:
    """Command to run thegent serve. Prefer sys.executable so launchd uses same Python as CLI."""
    import sys

    python = sys.executable
    if not python or not Path(python).exists():
        python = _python_exe(settings)
    return [python, "-m", "thegent.main", "serve"]


def service_install() -> tuple[bool, str]:
    """Install thegent MCP as launchd service (macOS)."""
    settings = ThegentSettings()
    if platform.system() != "Darwin":
        return False, "launchd only supported on macOS. Use systemd on Linux."
    plist_path = _launchd_plist_path()
    plist_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = _thegent_serve_cmd(settings)
    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
<key>Label</key>
<string>com.thegent.mcp</string>
<key>ProgramArguments</key>
<array>
<string>{cmd[0]}</string>
<string>{cmd[1]}</string>
<string>{cmd[2]}</string>
<string>{cmd[3]}</string>
</array>
<key>RunAtLoad</key>
<true/>
<key>KeepAlive</key>
<true/>
<key>StandardOutPath</key>
<string>{Path.home()}/.cache/thegent/mcp.log</string>
<key>StandardErrorPath</key>
<string>{Path.home()}/.cache/thegent/mcp.err</string>
</dict>
</plist>
"""
    plist_path.write_text(plist)
    Path.home().joinpath(".cache/thegent").mkdir(parents=True, exist_ok=True)
    return True, f"Installed to {plist_path}. Run: launchctl load {plist_path}"


def service_uninstall() -> tuple[bool, str]:
    """Remove launchd service."""
    if platform.system() != "Darwin":
        return False, "launchd only on macOS"
    plist_path = _launchd_plist_path()
    run_subprocess_optimized(["launchctl", "unload", str(plist_path)], check=False, capture_output=True)
    if plist_path.exists():
        plist_path.unlink()
    return True, "Uninstalled"


def service_start() -> tuple[bool, str]:
    """Start thegent MCP service."""
    if platform.system() != "Darwin":
        return False, "launchd only on macOS"
    plist_path = _launchd_plist_path()
    if not plist_path.exists():
        return False, "Service not installed. Run: thegent mcp service install"
    run_subprocess_optimized(["launchctl", "load", str(plist_path)], capture_output=True, check=True)
    return True, "Started"


def service_stop() -> tuple[bool, str]:
    """Stop thegent MCP service."""
    if platform.system() != "Darwin":
        return False, "launchd only on macOS"
    plist_path = _launchd_plist_path()
    if not plist_path.exists():
        return False, "Service not installed"
    run_subprocess_optimized(["launchctl", "unload", str(plist_path)], check=False, capture_output=True)
    return True, "Stopped"


def service_status(settings: ThegentSettings | None = None) -> tuple[bool, str]:
    """Check if thegent MCP service is running (launchd loaded + HTTP reachable)."""
    settings = settings or ThegentSettings()
    url = f"http://{settings.mcp_host}:{settings.mcp_port}/health"
    try:
        import httpx

        resp = httpx.get(url, timeout=2)
        if resp.status_code == 200:
            return True, "Running (HTTP OK)"
    except Exception:
        pass
    if platform.system() == "Darwin":
        result = run_subprocess_optimized(
            ["launchctl", "list", "com.thegent.mcp"],
            check=False,
            capture_output=True,
            text=True,
        )
        stdout_text = (
            result.stdout
            if isinstance(result.stdout, str)
            else (result.stdout.decode("utf-8", errors="replace") if result.stdout else "")
        )
        if result.returncode == 0 and stdout_text and "com.thegent.mcp" in stdout_text:
            return False, "Loaded but HTTP not reachable (check logs)"
    return False, "Not running"


# --- Process-compose (MCP + proxy bundled) ---


def _process_compose_path() -> Path | None:
    """Path to process-compose.yaml in thegent project."""
    try:
        import thegent

        # thegent.__file__ = .../thegent/src/thegent/__init__.py -> parent.parent = project root
        pkg = Path(thegent.__file__).resolve().parent
        root = pkg.parent.parent  # src -> thegent project root
        pc = root / "process-compose.yaml"
        return pc if pc.exists() else None
    except Exception:
        return None


def _http_ok(url: str, timeout: float = 1.0) -> bool:
    try:
        import httpx

        response = httpx.get(url, timeout=timeout)
        return response.status_code < 500
    except Exception:
        return False


def _services_healthy(settings: ThegentSettings) -> bool:
    mcp_url = f"http://{settings.mcp_host}:{settings.mcp_port}/health"
    proxy_port = int(os.getenv("THGENT_CLIPROXY_PORT", "8317"))
    proxy_url = f"http://127.0.0.1:{proxy_port}/v1/models"
    return _http_ok(mcp_url) and _http_ok(proxy_url)


def _wait_for_services_healthy(settings: ThegentSettings, timeout_seconds: float = 20.0) -> bool:
    deadline = time.monotonic() + max(0.1, timeout_seconds)
    while time.monotonic() < deadline:
        if _services_healthy(settings):
            return True
        time.sleep(0.5)
    return _services_healthy(settings)


def mcp_up(reload: bool = False) -> tuple[bool, str]:
    """Start MCP + proxy via process-compose. Returns (success, message)."""
    from thegent.errors import ConfigError, get_install_hint

    settings = ThegentSettings()
    pc = _process_compose_path()
    if pc is None:
        return False, "process-compose.yaml not found. Run from thegent project root."
    proc = shutil.which("process-compose")
    if not proc:
        raise ConfigError("process-compose not installed.", get_install_hint("process-compose"))

    if not reload and _services_healthy(settings):
        return True, "MCP + proxy already healthy; skipping duplicate startup."

    # Handle reload: if True, stop first
    if reload:
        mcp_down()

    result = run_subprocess_optimized(
        [proc, "-f", str(pc), "up", "-D"],
        check=False,
        cwd=pc.parent,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        stderr_text = (
            result.stderr
            if isinstance(result.stderr, str)
            else (result.stderr.decode("utf-8", errors="replace") if result.stderr else "")
        )
        stdout_text = (
            result.stdout
            if isinstance(result.stdout, str)
            else (result.stdout.decode("utf-8", errors="replace") if result.stdout else "")
        )
        return False, stderr_text or stdout_text or "process-compose up failed"
    if not _wait_for_services_healthy(settings):
        return False, "process-compose up completed but health probes did not converge in time."
    return True, f"MCP + proxy {'restarted' if reload else 'started'} (process-compose). MCP: {pc.parent}"


def mcp_down() -> tuple[bool, str]:
    """Stop MCP + proxy via process-compose. Returns (success, message)."""
    pc = _process_compose_path()
    if pc is None:
        return False, "process-compose.yaml not found."
    proc = shutil.which("process-compose")
    if not proc:
        return False, "process-compose not installed"
    # down connects to running server; must run from project dir
    result = run_subprocess_optimized(
        [proc, "-f", str(pc), "down"],
        check=False,
        cwd=pc.parent,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        stderr_text = (
            result.stderr
            if isinstance(result.stderr, str)
            else (result.stderr.decode("utf-8", errors="replace") if result.stderr else "")
        )
        stdout_text = (
            result.stdout
            if isinstance(result.stdout, str)
            else (result.stdout.decode("utf-8", errors="replace") if result.stdout else "")
        )
        return False, stderr_text or stdout_text or "process-compose down failed"
    return True, "MCP + proxy stopped"


def mcp_restart() -> tuple[bool, str]:
    """Restart MCP + proxy via process-compose. Returns (success, message)."""
    return mcp_up(reload=True)


def serve_delegate_or_run(settings) -> tuple[bool, str]:
    """
    Check if MCP server should be delegated to a service (launchd/Homebrew) or run directly.

    Returns:
        (run_foreground, message) - If run_foreground=True, run in foreground;
        otherwise, message indicates delegation success.
    """
    # Check if we should use launchd/Homebrew service
    # For now, always run foreground since service integration is not fully configured
    return True, "Running MCP server directly (service delegation not configured)"


# --- Known failing MCP servers ---

FAILING_MCP_SERVERS: frozenset[str] = frozenset({"playwright"})


def _resolve_client_paths(
    client: str,
    workspace: Path | None = None,
) -> list[Path]:
    """Resolve possible MCP config paths for a client.

    Returns all known candidate paths, with workspace paths first.
    """
    normalized_client = client.strip().lower()
    resolved_workspace = workspace.resolve() if workspace else None

    if normalized_client == "cursor":
        return ([resolved_workspace / ".cursor" / "mcp.json"] if resolved_workspace else []) + [
            Path.home() / ".cursor" / "mcp.json"
        ]
    if normalized_client == "droid":
        return [(resolved_workspace or Path.cwd()) / ".factory" / "mcp.json"]
    if normalized_client == "claude-code":
        return [Path.home() / ".claude.json"]
    if normalized_client == "codex":
        return MCP_CLIENT_PATHS["codex"]
    if normalized_client == "claude-desktop":
        return [Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"]
    return []


# --- Server removal helpers ---


def remove_servers_from_client(
    client: str,
    server_names: list[str],
    workspace: Path | None = None,
) -> tuple[bool, str]:
    """Remove named MCP servers from a client's config. Returns (success, message)."""
    try:
        config_paths = _resolve_client_paths(client=client, workspace=workspace)
        if not config_paths:
            return False, f"Unknown client: {client}"

        total_removed = 0
        touched = 0
        normalized_client = client.strip().lower()
        for config_path in config_paths:
            if not config_path.exists():
                continue
            config: dict[str, Any] = json.loads(config_path.read_text())
            mcp_servers = config.get("mcpServers", {})
            pre_count = len(mcp_servers)
            for name in server_names:
                if name in mcp_servers:
                    del mcp_servers[name]
            if len(mcp_servers) != pre_count:
                touched += 1
                total_removed += pre_count - len(mcp_servers)
                config["mcpServers"] = mcp_servers
                config_path.write_text(json.dumps(config, indent=2))

        if total_removed == 0:
            return True, f"No matching servers found for {normalized_client}"
        return True, f"Removed {total_removed} server(s) from {normalized_client} ({touched} file(s) updated)"
    except FileNotFoundError:
        return True, "No matching servers found"
    except Exception as e:
        return False, str(e)


# --- Uni-mount migration ---


def migrate_to_unimount(
    client: str,
    mcp_url: str,
    workspace: Path | None = None,
) -> tuple[bool, str]:
    """Ensure uni-mount MCP keys are set while keeping existing MCP entries. Returns (success, message)."""
    try:
        config_paths = _resolve_client_paths(client=client, workspace=workspace)
        if not config_paths:
            return False, f"Unknown client: {client}"

        normalized_client = client.strip().lower()
        for config_path in config_paths:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config = json.loads(config_path.read_text()) if config_path.exists() else {}
            mcp_servers = config.get("mcpServers")
            if not isinstance(mcp_servers, dict):
                mcp_servers = {}
            config["mcpServers"] = mcp_servers
            config = _set_compatible_mcp_servers(config, url=mcp_url)
            config_path.write_text(json.dumps(config, indent=2))
        return True, f"Migrated {normalized_client} to uni-mount"
    except Exception as e:
        return False, str(e)


# --- Periodic prune daemon ---

_PRUNE_LAUNCHD_LABEL = "com.thegent.mcp.prune"
_PRUNE_PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / f"{_PRUNE_LAUNCHD_LABEL}.plist"
_PRUNE_SYSTEMD_UNIT = "thegent-mcp-prune.service"
_PRUNE_SYSTEMD_PATH = Path.home() / ".config" / "systemd" / "user" / _PRUNE_SYSTEMD_UNIT


def prune_periodic_install() -> tuple[bool, str]:
    """Install a periodic prune daemon. Returns (success, message)."""
    try:
        system = platform.system()
        if system == "Darwin":
            _PRUNE_PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
            plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
<key>Label</key>
<string>{_PRUNE_LAUNCHD_LABEL}</string>
<key>ProgramArguments</key>
<array>
<string>thegent</string>
<string>mcp</string>
<string>prune</string>
</array>
<key>StartInterval</key>
<integer>3600</integer>
<key>RunAtLoad</key>
<false/>
</dict>
</plist>
"""
            _PRUNE_PLIST_PATH.write_text(plist)
            shim_run(
                ["launchctl", "load", str(_PRUNE_PLIST_PATH)],
                check=False,
                capture_output=True,
            )
            return True, "Periodic prune installed"
        if system == "Linux":
            _PRUNE_SYSTEMD_PATH.parent.mkdir(parents=True, exist_ok=True)
            unit = """[Unit]
Description=Thegent MCP periodic prune

[Service]
Type=oneshot
ExecStart=thegent mcp prune

[Install]
WantedBy=default.target
"""
            _PRUNE_SYSTEMD_PATH.write_text(unit)
            shim_run(
                ["systemctl", "--user", "enable", _PRUNE_SYSTEMD_UNIT],
                check=False,
                capture_output=True,
            )
            return True, "Periodic prune installed"
        return False, f"Unsupported platform: {system}"
    except Exception as e:
        return False, str(e)


def prune_periodic_start() -> tuple[bool, str]:
    """Start the periodic prune daemon. Returns (success, message)."""
    try:
        system = platform.system()
        if system == "Darwin":
            shim_run(
                ["launchctl", "start", _PRUNE_LAUNCHD_LABEL],
                check=False,
                capture_output=True,
            )
            return True, "Periodic prune started"
        if system == "Linux":
            shim_run(
                ["systemctl", "--user", "start", _PRUNE_SYSTEMD_UNIT],
                check=False,
                capture_output=True,
            )
            return True, "Periodic prune started"
        return False, f"Unsupported platform: {system}"
    except Exception as e:
        return False, str(e)


def prune_periodic_stop() -> tuple[bool, str]:
    """Stop the periodic prune daemon. Returns (success, message)."""
    try:
        system = platform.system()
        if system == "Darwin":
            shim_run(
                ["launchctl", "stop", _PRUNE_LAUNCHD_LABEL],
                check=False,
                capture_output=True,
            )
            return True, "Periodic prune stopped"
        if system == "Linux":
            shim_run(
                ["systemctl", "--user", "stop", _PRUNE_SYSTEMD_UNIT],
                check=False,
                capture_output=True,
            )
            return True, "Periodic prune stopped"
        return False, f"Unsupported platform: {system}"
    except Exception as e:
        return False, str(e)


def prune_periodic_status() -> tuple[bool, str]:
    """Return status of the periodic prune daemon. Returns (success, message)."""
    try:
        system = platform.system()
        if system == "Darwin":
            result = shim_run(
                ["launchctl", "list", _PRUNE_LAUNCHD_LABEL],
                check=False,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return True, f"Periodic prune loaded: {result.stdout.strip()}"
            return False, "Periodic prune not loaded"
        if system == "Linux":
            result = shim_run(
                ["systemctl", "--user", "is-active", _PRUNE_SYSTEMD_UNIT],
                check=False,
                capture_output=True,
                text=True,
            )
            status = result.stdout.strip()
            return result.returncode == 0, f"Periodic prune: {status}"
        return False, f"Unsupported platform: {system}"
    except Exception as e:
        return False, str(e)


def prune_periodic_uninstall() -> tuple[bool, str]:
    """Remove the periodic prune daemon. Returns (success, message)."""
    try:
        system = platform.system()
        if system == "Darwin":
            shim_run(
                ["launchctl", "unload", str(_PRUNE_PLIST_PATH)],
                check=False,
                capture_output=True,
            )
            if _PRUNE_PLIST_PATH.exists():
                _PRUNE_PLIST_PATH.unlink()
            return True, "Periodic prune uninstalled"
        if system == "Linux":
            shim_run(
                ["systemctl", "--user", "disable", "--now", _PRUNE_SYSTEMD_UNIT],
                check=False,
                capture_output=True,
            )
            if _PRUNE_SYSTEMD_PATH.exists():
                _PRUNE_SYSTEMD_PATH.unlink()
            return True, "Periodic prune uninstalled"
        return False, f"Unsupported platform: {system}"
    except Exception as e:
        return False, str(e)


# --- Playwright shorthand ---


def remove_playwright_from_client(
    client: str,
    workspace: Path | None = None,
) -> tuple[bool, str]:
    """Shorthand to remove playwright from a single client."""
    return remove_servers_from_client(client, ["playwright"], workspace=workspace)


__all__ = ["DEFAULT_MCP_URL", "MCP_CLIENT_PATHS", "_get_mcp_url"]
