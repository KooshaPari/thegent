"""MCP configuration and service management for thegent."""

import json
import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Any

from thegent.config import ThegentSettings

# MCP server URL (HTTP transport)
DEFAULT_MCP_URL = "http://127.0.0.1:3847/mcp"

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


def install_to_cursor(
    url: str = DEFAULT_MCP_URL,
    workspace: Path | None = None,
) -> bool:
    """Add thegent to Cursor MCP config. Prefers workspace .cursor/mcp.json if present."""
    config_path = workspace.resolve() / ".cursor" / "mcp.json" if workspace else Path.home() / ".cursor" / "mcp.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config: dict[str, Any] = json.loads(config_path.read_text()) if config_path.exists() else {"mcpServers": {}}
    config = _ensure_mcp_servers(config)
    config["mcpServers"]["thegent"] = _remote_config(url)
    config_path.write_text(json.dumps(config, indent=2))
    return True


def install_to_claude_code(url: str = DEFAULT_MCP_URL) -> bool:
    """Add thegent to Claude Code config (~/.claude.json)."""
    config_path = Path.home() / ".claude.json"
    config: dict[str, Any] = json.loads(config_path.read_text()) if config_path.exists() else {}
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    config["mcpServers"]["thegent"] = _remote_config(url)
    config_path.write_text(json.dumps(config, indent=2))
    return True


def install_to_codex(url: str = DEFAULT_MCP_URL) -> bool:
    """Add thegent to Codex MCP config."""
    config_path = Path.home() / ".codex" / "mcp.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config: dict[str, Any] = json.loads(config_path.read_text()) if config_path.exists() else {"mcpServers": {}}
    config = _ensure_mcp_servers(config)
    config["mcpServers"]["thegent"] = _remote_config(url)
    config_path.write_text(json.dumps(config, indent=2))
    return True


def install_to_claude_desktop(url: str = DEFAULT_MCP_URL) -> bool:
    """Add thegent to Claude Desktop config (macOS)."""
    config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    if not config_path.parent.exists():
        return False
    config: dict[str, Any] = json.loads(config_path.read_text()) if config_path.exists() else {}
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    config["mcpServers"]["thegent"] = _remote_config(url)
    config_path.write_text(json.dumps(config, indent=2))
    return True


def install_to_droid(url: str, workspace: Path | None = None) -> bool:
    """Add thegent to .factory/mcp.json (project-level, for droids/scripts)."""
    base = (workspace or Path.cwd()).resolve()
    config_path = base / ".factory" / "mcp.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config: dict[str, Any] = json.loads(config_path.read_text()) if config_path.exists() else {"mcpServers": {}}
    config = _ensure_mcp_servers(config)
    config["mcpServers"]["thegent"] = _remote_config(url)
    config_path.write_text(json.dumps(config, indent=2))
    return True


def install_to_client(
    client: str,
    url: str,
    workspace: Path | None = None,
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


def _python_exe() -> str:
    """Resolve Python executable for thegent."""
    if os.environ.get("VIRTUAL_ENV"):
        venv = Path(os.environ["VIRTUAL_ENV"])
        exe = venv / "bin" / "python"
        if exe.exists():
            return str(exe)
    return shutil.which("python3") or shutil.which("python") or "python3"


def _thegent_serve_cmd() -> list[str]:
    """Command to run thegent serve. Prefer sys.executable so launchd uses same Python as CLI."""
    import sys

    python = sys.executable
    if not python or not Path(python).exists():
        python = _python_exe()
    return [python, "-m", "thegent.main", "serve"]


def service_install() -> tuple[bool, str]:
    """Install thegent MCP as launchd service (macOS)."""
    if platform.system() != "Darwin":
        return False, "launchd only supported on macOS. Use systemd on Linux."
    plist_path = _launchd_plist_path()
    plist_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = _thegent_serve_cmd()
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
    subprocess.run(["launchctl", "unload", str(plist_path)], check=False, capture_output=True)
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
    subprocess.run(["launchctl", "load", str(plist_path)], capture_output=True, check=True)
    return True, "Started"


def service_stop() -> tuple[bool, str]:
    """Stop thegent MCP service."""
    if platform.system() != "Darwin":
        return False, "launchd only on macOS"
    plist_path = _launchd_plist_path()
    if not plist_path.exists():
        return False, "Service not installed"
    subprocess.run(["launchctl", "unload", str(plist_path)], check=False, capture_output=True)
    return True, "Stopped"


def service_status(settings: ThegentSettings | None = None) -> tuple[bool, str]:
    """Check if thegent MCP service is running (launchd loaded + HTTP reachable)."""
    settings = settings or ThegentSettings()
    url = f"http://{settings.mcp_host}:{settings.mcp_port}/health"
    try:
        import urllib.request

        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            if resp.status == 200:
                return True, "Running (HTTP OK)"
    except Exception:
        pass
    if platform.system() == "Darwin":
        result = subprocess.run(
            ["launchctl", "list", "com.thegent.mcp"],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and "com.thegent.mcp" in (result.stdout or ""):
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


def mcp_up() -> tuple[bool, str]:
    """Start MCP + proxy via process-compose. Returns (success, message)."""
    pc = _process_compose_path()
    if pc is None:
        return False, "process-compose.yaml not found. Run from thegent project root."
    proc = shutil.which("process-compose")
    if not proc:
        return False, "process-compose not installed. Install: brew install process-compose"
    result = subprocess.run(
        [proc, "-f", str(pc), "up", "-D"],
        check=False,
        cwd=pc.parent,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return False, result.stderr or result.stdout or "process-compose up failed"
    return True, f"MCP + proxy started (process-compose). MCP: {pc.parent}"


def mcp_down() -> tuple[bool, str]:
    """Stop MCP + proxy via process-compose. Returns (success, message)."""
    pc = _process_compose_path()
    if pc is None:
        return False, "process-compose.yaml not found."
    proc = shutil.which("process-compose")
    if not proc:
        return False, "process-compose not installed"
    # down connects to running server; must run from project dir
    result = subprocess.run(
        [proc, "down"],
        check=False,
        cwd=pc.parent,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return False, result.stderr or result.stdout or "process-compose down failed"
    return True, "MCP + proxy stopped"
