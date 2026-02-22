# Unified System Application Plan

**Purpose:** Merge desktop app, tray app, and all thegent installations into a single unified system application with one installer, one tray, and one chat/dashboard surface.

**Date:** 2026-02-16
**Status:** Complete
**Version:** 1.0
**Supersedes:** Tray app design, install design, desktop app concept (scattered)

---

## 1. Executive Summary

| Goal | Approach |
|------|----------|
| **One app** | Single unified application: tray + desktop window + chat + dashboard |
| **One installer** | Unified installer: thegent CLI, MCP, cliproxy, skills, hooks, provider auth, tray app |
| **One surface** | Chat + project/directory split (ChatGPT-style); sitback dashboard; terminal panes |
| **Low overhead** | Ghostty-like feel; Tauri 2 or SwiftUI; minimize memory/CPU |
| **Scalable** | 300 logical agents (M << 300 physical slots); resource gates |

---

## 2. Merged Components

### 2.1 Source Plans Merged

| Source | Content | Merge Target |
|--------|---------|--------------|
| [2026-02-15-tray-application-design.md](./2026-02-15-tray-application-design.md) | Tray app, heliosShield + thegent plugins | Tray + main window |
| [2026-02-14-thegent-install-design.md](./2026-02-14-thegent-install-design.md) | `thegent install` → ~/.claude, ~/.factory | Unified installer Phase 1 |
| [2026-02-14-thegent-install-implementation-plan.md](./2026-02-14-thegent-install-implementation-plan.md) | Install implementation | Unified installer |
| [CONVERSATION_DUMP_2026-02-16.md](../research/CONVERSATION_DUMP_2026-02-16.md) | TUIOS, Zellij, Textual, Ghostty | UI layer options |
| [2026-02-15-thegent-sitback-design.md](./2026-02-15-thegent-sitback-design.md) | Sitback agent, dashboard | Chat/dashboard surface |
| [OPENCLAW_AGENTZERO_AS_MAIN_AGENT_RESEARCH.md](../research/OPENCLAW_AGENTZERO_AS_MAIN_AGENT_RESEARCH.md) | OpenClaw/Agent Zero as runtime | Optional main agent |

### 2.2 Installations Unified

| Component | Current | Unified |
|-----------|---------|---------|
| thegent CLI | `uv tool install`, pip | Bundled in unified installer |
| MCP server | `thegent serve` | Auto-started by app; port 3847 |
| CLIProxy | `task cliproxy:build`, config | Bundled; auto-configured |
| Skills, hooks | `thegent install` | Part of unified install |
| Claude Code, Codex, Cursor | Manual install | Optional; installer can prompt/link |
| Tray app | Separate (tray-app/) | Core of unified app |
| Shims (codex, copilot, etc.) | `thegent install-shims` | Part of unified install |

---

## 3. Architecture

### 3.1 Layered Model

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Unified System Application                                              │
├─────────────────────────────────────────────────────────────────────────┤
│  Tray (always-on)  │  Main Window (chat + dashboard + project split)     │
├─────────────────────────────────────────────────────────────────────────┤
│  Chat surface      │  Sitback dashboard │  Terminal panes (Zellij/tmux) │
├─────────────────────────────────────────────────────────────────────────┤
│  MCP client        │  thegent CLI       │  Agent runtime (CC/Codex/A0) │
├─────────────────────────────────────────────────────────────────────────┤
│  MCP server (3847) │  CLIProxy (8317)   │  Hooks, skills, contracts     │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Tech Stack Options

| Layer | Option A | Option B | Option C |
|-------|----------|----------|----------|
| **Desktop shell** | Tauri 2 (Rust + WebView) | SwiftUI (macOS) | PyQt/PySide (Python) |
| **Tray** | Tauri tray / SwiftUI menu bar | Same | Same |
| **Chat UI** | WebView (React/Svelte) | Native Swift | Qt widgets |
| **Terminal panes** | libghostty, xterm.js, or embed Zellij | Same | Same |
| **TUI overlay** | Textual (Python) for menus/status | — | — |

**Recommendation:** Tauri 2 for cross-platform, low overhead, native tray. Embed terminal via libghostty or xterm.js. Reuse tray-app plugin architecture (heliosShield + thegent) as main window tabs.

### 3.3 Directory Structure (Unified)

```
thegent/
├── src/thegent/           # CLI, MCP, agents (existing)
├── tray-app/             # Tray + main window (merged)
│   ├── core/             # App shell, plugin host
│   ├── plugins/
│   │   ├── heliosShield/     # heliosShield (existing)
│   │   ├── thegent/      # Projects, Agents, Runs, Gardener, Costs, Gamification
│   │   └── chat/         # NEW: Chat + sitback dashboard
│   └── run_unified.py    # Entry: tray + window
├── install/              # Unified installer
│   ├── unified_install.py
│   └── bundles/         # thegent, cliproxy, skills, hooks, shims
└── ...
```

---

## 4. Unified Installer

### 4.1 Single Command

```bash
thegent setup
# or
thegent unified-install [OPTIONS]
```

**Options:**
- `--tray` — Install and start tray app (default: yes)
- `--mcp` — Install MCP server config for Cursor/Claude/Codex (default: yes)
- `--cliproxy` — Build and configure CLIProxy (default: yes)
- `--skills` — Sync skills to ~/.claude (default: yes)
- `--shims` — Install codex, copilot, clode shims (default: yes)
- `--providers` — Run OAuth for minimax, glm, etc. (interactive)
- `--editable` — Symlink install for dev
- `--dry-run` — Show what would be installed

### 4.2 Install Phases

| Phase | Action |
|-------|--------|
| 1 | `thegent install` (skills, hooks, ~/.claude, ~/.factory) |
| 2 | `thegent install-shims` (codex, copilot, clode) |
| 3 | `task cliproxy:build` + `task cliproxy:ensure-config` |
| 4 | MCP server config → Cursor, Claude Code, Codex |
| 5 | Tray app: install, register launchd/systemd |
| 6 | Provider auth: prompt for `thegent cliproxy login X` |

### 4.3 Post-Install

- Tray icon appears
- MCP server starts on app launch (or `thegent serve` in background)
- User can open main window → Chat tab or Dashboard tab

---

## 5. Main Window: Chat + Dashboard + Project Split

### 5.1 Layout (ChatGPT-Style)

```
┌──────────────────────────────────────────────────────────────────┐
│  [≡] thegent                                    [−] [□] [×]       │
├─────────────┬────────────────────────────────────────────────────┤
│             │                                                     │
│  Projects   │  Chat / Sitback Dashboard                           │
│  ─────────  │  ─────────────────────────────────────────────────│
│  • kush/    │  Sessions: 3 running, 0 failed                      │
│  • thegent  │  Terminals: 5 panes (2 Claude Code)                │
│  • repo-x   │  Budget: $12.50 MTD                                │
│             │                                                     │
│  + New      │  [Chat input: "garden" / "status" / "run X"]       │
│             │                                                     │
├─────────────┴────────────────────────────────────────────────────┤
│  Terminal panes (optional): Zellij/tmux embed or link            │
└──────────────────────────────────────────────────────────────────┘
```

### 5.2 Chat Tab

- Connects to MCP (thegent serve)
- Uses sitback skill: dashboard, never-idle, gardening
- MCP tools: `thegent_sitback_dashboard`, `thegent_run`, `thegent_bg`, `thegent_do_next`, etc.
- Optional: Embed OpenClaw WebChat or Agent Zero as chat runtime (see research)

### 5.3 Dashboard Tab

- Same as tray thegent plugin: Projects, Agents, Runs, Gardener, Costs, Gamification
- REST calls to MCP server `/api/v1/*`

### 5.4 Terminal Panes

- **Option A:** Embed Zellij or tmux via PTY
- **Option B:** Link to external terminal (Ghostty, iTerm) with session attach
- **Option C:** Textual app with embedded terminal widgets

---

## 6. Scalability (300 Agents)

### 6.1 Model

- **300 agents** = logical agents (Codex, Claude, Cursor slots)
- **M physical slots** << 300 (e.g. M = 10–20 active)
- Shared: single MCP server, single CLIProxy, LSP multiplexing

### 6.2 Resource Gates

| Resource | Limit (M1 Pro, 16GB) | Gate |
|----------|----------------------|------|
| RAM | 4GB for agents | Cap active slots |
| CPU | 1–2 cores | Throttle spawn |
| FD | 10k system limit | Reuse, close idle |
| Disk | 20GB reserved | Session log rotation |

### 6.3 Implementation

- Active slot cap in run registry
- `thegent run` / `thegent bg` respect cap; queue excess
- See: `docs/research/MEMORY_OPTIMIZATION_LONG_TERM_PLAN.md`, `docs/research/SYSTEM_RESOURCES_FD_CPU_DEEP_RESEARCH.md`

---

## 7. Implementation Phases

### Phase 1: Unified Installer (4–6 tool calls)

- Add `thegent setup` or `thegent unified-install`
- Orchestrate: install + install-shims + cliproxy + MCP config
- Document in README

### Phase 2: Tray + Main Window Merge (8–12 tool calls)

- Integrate tray-app into thegent repo (or keep as subproject)
- Add Chat tab plugin (sitback dashboard + chat input)
- Main window = tray "show" target

### Phase 3: Chat Runtime (6–10 tool calls)

- Wire chat tab to MCP tools
- Optional: Add Agent Zero or OpenClaw as embedded runtime
- Validate sitback flow in unified app

### Phase 4: Terminal Embed (Optional, 8–15 tool calls)

- Evaluate libghostty, xterm.js, Zellij embed
- Add terminal pane to main window or link to external

### Phase 5: Scalability Gates (4–6 tool calls)

- Add active slot cap to run registry
- Resource monitoring and backpressure

---

## 8. Acceptance Criteria

1. **Unified install:** `thegent setup` installs CLI, MCP config, cliproxy, skills, shims, tray app
2. **Tray:** Icon appears; left-click shows main window; right-click menu
3. **Main window:** Chat tab + Dashboard tab (Projects, Agents, Runs, Gardener, Costs, Gamification)
4. **Chat:** User can type "status", "garden", "run X"; gets sitback dashboard + responses
5. **Dashboard:** All tray thegent plugin features work
6. **heliosShield:** Existing heliosShield tabs work (backward compatible)
7. **Scalability:** 300 logical agents; M active slots; no OOM under normal load

---

## 9. Detailed Implementation

### 9.1 Unified Installer Implementation

**File: `src/thegent/cli/unified_install.py`**

```python
"""Unified installer for thegent system application."""

import typer
from pathlib import Path
from typing import Optional
import subprocess
import json

app = typer.Typer(name="setup", help="Unified installer for thegent")

@app.command()
def unified_install(
    tray: bool = typer.Option(True, "--tray/--no-tray", help="Install tray app"),
    mcp: bool = typer.Option(True, "--mcp/--no-mcp", help="Install MCP server config"),
    cliproxy: bool = typer.Option(True, "--cliproxy/--no-cliproxy", help="Build CLIProxy"),
    skills: bool = typer.Option(True, "--skills/--no-skills", help="Sync skills"),
    shims: bool = typer.Option(True, "--shims/--no-shims", help="Install shims"),
    providers: bool = typer.Option(False, "--providers/--no-providers", help="Run OAuth"),
    editable: bool = typer.Option(False, "--editable", help="Symlink install for dev"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be installed"),
):
    """Unified installer for thegent system application."""

    if dry_run:
        typer.echo("DRY RUN MODE - No changes will be made")
        typer.echo(f"Would install: tray={tray}, mcp={mcp}, cliproxy={cliproxy}, skills={skills}, shims={shims}")
        return

    typer.echo("Starting unified installation...")

    # Phase 1: Core thegent install
    if skills:
        typer.echo("Phase 1: Installing core thegent components...")
        subprocess.run(["thegent", "install", "--target", "all"], check=True)

    # Phase 2: Install shims
    if shims:
        typer.echo("Phase 2: Installing shims...")
        subprocess.run(["thegent", "install-shims"], check=True)

    # Phase 3: Build and configure CLIProxy
    if cliproxy:
        typer.echo("Phase 3: Building CLIProxy...")
        subprocess.run(["task", "cliproxy:build"], check=True)
        subprocess.run(["task", "cliproxy:ensure-config"], check=True)

    # Phase 4: Configure MCP server
    if mcp:
        typer.echo("Phase 4: Configuring MCP server...")
        _configure_mcp_server()

    # Phase 5: Install tray app
    if tray:
        typer.echo("Phase 5: Installing tray app...")
        _install_tray_app()

    # Phase 6: Provider authentication
    if providers:
        typer.echo("Phase 6: Setting up provider authentication...")
        _setup_providers()

    typer.echo("✅ Unified installation complete!")
    typer.echo("Tray icon should appear in your menu bar.")
    typer.echo("Run 'thegent setup --help' for more options.")

def _configure_mcp_server():
    """Configure MCP server for Cursor, Claude Code, Codex."""
    mcp_configs = {
        "cursor": Path.home() / ".cursor" / "mcp.json",
        "claude-code": Path.home() / ".claude" / "mcp.json",
        "codex": Path.home() / ".codex" / "mcp.json",
    }

    mcp_config = {
        "mcpServers": {
            "thegent": {
                "command": "thegent",
                "args": ["serve"],
                "env": {}
            }
        }
    }

    for app_name, config_path in mcp_configs.items():
        if config_path.parent.exists():
            config_path.write_text(json.dumps(mcp_config, indent=2))
            typer.echo(f"  ✓ Configured MCP for {app_name}")

def _install_tray_app():
    """Install and register tray app."""
    # Build tray app
    subprocess.run(["task", "tray-app:build"], check=True)

    # Register launch agent (macOS) or systemd service (Linux)
    if _is_macos():
        _register_launchd()
    elif _is_linux():
        _register_systemd()

def _register_launchd():
    """Register tray app with launchd (macOS)."""
    plist_path = Path.home() / "Library" / "LaunchAgents" / "com.thegent.tray.plist"
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.thegent.tray</string>
    <key>ProgramArguments</key>
    <array>
        <string>{Path.home() / '.local' / 'bin' / 'thegent-tray'}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>"""
    plist_path.write_text(plist_content)
    subprocess.run(["launchctl", "load", str(plist_path)], check=True)

def _register_systemd():
    """Register tray app with systemd (Linux)."""
    service_path = Path.home() / ".config" / "systemd" / "user" / "thegent-tray.service"
    service_content = f"""[Unit]
Description=thegent Tray Application
After=graphical-session.target

[Service]
Type=simple
ExecStart={Path.home() / '.local' / 'bin' / 'thegent-tray'}
Restart=always

[Install]
WantedBy=default.target"""
    service_path.write_text(service_content)
    subprocess.run(["systemctl", "--user", "enable", "thegent-tray.service"], check=True)
    subprocess.run(["systemctl", "--user", "start", "thegent-tray.service"], check=True)

def _setup_providers():
    """Interactive provider authentication setup."""
    providers = ["minimax", "glm", "openai", "anthropic"]
    for provider in providers:
        if typer.confirm(f"Set up authentication for {provider}?"):
            subprocess.run(["thegent", "cliproxy", "login", provider], check=True)

def _is_macos() -> bool:
    """Check if running on macOS."""
    import platform
    return platform.system() == "Darwin"

def _is_linux() -> bool:
    """Check if running on Linux."""
    import platform
    return platform.system() == "Linux"
```

### 9.2 Main Window Architecture

**File: `tray-app/core/main_window.py`**

```python
"""Main window for unified system application."""

from typing import Optional
import asyncio
from dataclasses import dataclass

@dataclass
class WindowState:
    """State of the main window."""
    current_tab: str = "chat"  # "chat" | "dashboard" | "terminal"
    current_project: Optional[str] = None
    chat_history: list = None
    dashboard_data: dict = None

class MainWindow:
    """Main window with chat, dashboard, and terminal panes."""

    def __init__(self):
        self.state = WindowState()
        self.mcp_client = None
        self.terminal_panes = []

    def show(self):
        """Show the main window."""
        # Platform-specific implementation
        # Tauri: window.show()
        # SwiftUI: NSWindow.makeKeyAndOrderFront()
        pass

    def switch_tab(self, tab: str):
        """Switch to a different tab."""
        self.state.current_tab = tab
        self._update_ui()

    def set_project(self, project_path: str):
        """Set the current project."""
        self.state.current_project = project_path
        self._update_ui()

    async def send_chat_message(self, message: str):
        """Send a chat message via MCP."""
        if not self.mcp_client:
            self.mcp_client = await self._connect_mcp()

        # Use sitback skill for dashboard commands
        if message.startswith("status") or message.startswith("garden"):
            tool = "thegent_sitback_dashboard"
        elif message.startswith("run"):
            tool = "thegent_run"
        else:
            tool = "thegent_sitback_dashboard"

        result = await self.mcp_client.call_tool(tool, {"query": message})
        return result

    def _update_ui(self):
        """Update UI based on current state."""
        # Platform-specific UI update
        pass

    async def _connect_mcp(self):
        """Connect to MCP server."""
        # Connect to thegent serve on port 3847
        pass
```

### 9.3 Chat Tab Implementation

**File: `tray-app/plugins/chat/chat_tab.py`**

```python
"""Chat tab plugin for unified system application."""

from typing import Optional
import asyncio

class ChatTab:
    """Chat tab with sitback dashboard integration."""

    def __init__(self, mcp_client):
        self.mcp_client = mcp_client
        self.history = []

    async def handle_message(self, message: str) -> dict:
        """Handle a chat message."""
        # Route to appropriate MCP tool
        if message.startswith("status"):
            return await self._get_status()
        elif message.startswith("garden"):
            return await self._garden()
        elif message.startswith("run"):
            return await self._run_command(message)
        else:
            return await self._sitback_dashboard(message)

    async def _get_status(self) -> dict:
        """Get system status."""
        result = await self.mcp_client.call_tool("thegent_status", {})
        return {
            "type": "status",
            "data": result
        }

    async def _garden(self) -> dict:
        """Run gardener."""
        result = await self.mcp_client.call_tool("thegent_garden", {})
        return {
            "type": "garden",
            "data": result
        }

    async def _run_command(self, message: str) -> dict:
        """Run a command."""
        command = message.replace("run", "").strip()
        result = await self.mcp_client.call_tool("thegent_run", {
            "command": command
        })
        return {
            "type": "run",
            "data": result
        }

    async def _sitback_dashboard(self, query: str) -> dict:
        """Get sitback dashboard."""
        result = await self.mcp_client.call_tool("thegent_sitback_dashboard", {
            "query": query
        })
        return {
            "type": "dashboard",
            "data": result
        }
```

### 9.4 Terminal Pane Integration

**File: `tray-app/core/terminal_pane.py`**

```python
"""Terminal pane integration for unified system application."""

from typing import Optional
import subprocess

class TerminalPane:
    """Terminal pane with Zellij/tmux integration."""

    def __init__(self, mode: str = "zellij"):
        self.mode = mode  # "zellij" | "tmux" | "embedded"
        self.session_name: Optional[str] = None

    def create_session(self, name: str):
        """Create a new terminal session."""
        if self.mode == "zellij":
            subprocess.run(["zellij", "new-session", "-s", name])
        elif self.mode == "tmux":
            subprocess.run(["tmux", "new-session", "-d", "-s", name])
        self.session_name = name

    def attach_session(self, name: str):
        """Attach to an existing session."""
        if self.mode == "zellij":
            subprocess.run(["zellij", "attach", name])
        elif self.mode == "tmux":
            subprocess.run(["tmux", "attach", "-t", name])
        self.session_name = name

    def send_command(self, command: str):
        """Send a command to the terminal session."""
        if self.mode == "tmux" and self.session_name:
            subprocess.run([
                "tmux", "send-keys", "-t", self.session_name, command, "Enter"
            ])
```

## 10. Testing Strategy

### 10.1 Unit Tests

**Test Unified Installer**:
```python
def test_unified_install_dry_run():
    """Test unified installer in dry-run mode."""
    result = subprocess.run(
        ["thegent", "setup", "--dry-run"],
        capture_output=True,
        text=True
    )
    assert "DRY RUN MODE" in result.stdout
    assert result.returncode == 0

def test_mcp_config_creation():
    """Test MCP server configuration creation."""
    config_path = Path.home() / ".cursor" / "mcp.json"
    # Run installer
    # Verify config file exists and is valid JSON
    assert config_path.exists()
    config = json.loads(config_path.read_text())
    assert "mcpServers" in config
    assert "thegent" in config["mcpServers"]
```

### 10.2 Integration Tests

**Test Tray App Launch**:
```python
def test_tray_app_launch():
    """Test tray app launches successfully."""
    # Start tray app
    process = subprocess.Popen(["thegent-tray"])
    # Wait for initialization
    time.sleep(2)
    # Verify process is running
    assert process.poll() is None
    # Cleanup
    process.terminate()
```

**Test Main Window**:
```python
def test_main_window_chat():
    """Test main window chat functionality."""
    window = MainWindow()
    window.show()
    # Send test message
    result = asyncio.run(window.send_chat_message("status"))
    assert result is not None
    assert "success" in result or "data" in result
```

### 10.3 End-to-End Tests

**Test Full Installation Flow**:
```python
def test_full_installation():
    """Test complete installation flow."""
    # Run unified installer
    subprocess.run(["thegent", "setup"], check=True)

    # Verify components installed
    assert Path.home() / ".local" / "bin" / "thegent-tray").exists()
    assert Path.home() / ".cursor" / "mcp.json").exists()

    # Verify tray app starts
    process = subprocess.Popen(["thegent-tray"])
    time.sleep(2)
    assert process.poll() is None
    process.terminate()
```

## 11. Performance Considerations

### 11.1 Memory Usage

**Target**: < 200MB for tray app + main window

**Optimization Strategies**:
- Lazy load chat history
- Virtual scrolling for dashboard
- Unload unused terminal panes
- Cache MCP responses

### 11.2 Startup Time

**Target**: < 2s for tray app, < 1s for main window

**Optimization Strategies**:
- Async initialization
- Background MCP connection
- Defer terminal pane loading
- Cache UI state

### 11.3 Resource Management

**Active Slot Management**:
- Cap active agent slots (M = 10-20)
- Queue excess requests
- Monitor resource usage
- Implement backpressure

## 12. Troubleshooting

### 12.1 Installation Issues

**Tray app doesn't appear**:
1. Check launchd/systemd registration
2. Verify tray app binary exists
3. Check logs: `~/.local/share/thegent/tray.log`
4. Reinstall: `thegent setup --tray`

**MCP server not starting**:
1. Check port 3847 is available
2. Verify MCP config files
3. Test manually: `thegent serve`
4. Check logs: `~/.local/share/thegent/mcp.log`

### 12.2 Runtime Issues

**Main window doesn't open**:
1. Check tray app is running
2. Verify window permissions
3. Check logs for errors
4. Restart tray app

**Chat not responding**:
1. Verify MCP server is running
2. Check MCP connection
3. Test MCP tools manually
4. Check network connectivity

### 12.3 Performance Issues

**High memory usage**:
1. Check active agent count
2. Monitor terminal panes
3. Clear chat history
4. Restart tray app

**Slow startup**:
1. Check for blocking operations
2. Verify async initialization
3. Profile startup time
4. Optimize dependencies

## 13. Migration Path

### 13.1 From Separate Components

**Step 1: Backup Current Setup**
```bash
# Backup existing configs
cp ~/.cursor/mcp.json ~/.cursor/mcp.json.backup
cp ~/.claude/mcp.json ~/.claude/mcp.json.backup
```

**Step 2: Run Unified Installer**
```bash
thegent setup
```

**Step 3: Verify Installation**
```bash
# Check tray app
thegent-tray --version

# Check MCP server
thegent serve --help

# Check CLIProxy
thegent cliproxy status
```

**Step 4: Test Functionality**
```bash
# Open tray app
# Click tray icon → Open Main Window
# Test chat: type "status"
# Test dashboard: switch to Dashboard tab
```

### 13.2 Rollback Plan

If issues occur:
1. Stop tray app: `killall thegent-tray`
2. Restore backups: `cp ~/.cursor/mcp.json.backup ~/.cursor/mcp.json`
3. Reinstall components individually
4. Report issue with logs

## 14. Success Metrics

### 14.1 Installation Metrics

- ✅ Unified installer completes in < 60s
- ✅ All components install successfully
- ✅ Tray app appears in menu bar
- ✅ MCP server starts automatically

### 14.2 Runtime Metrics

- ✅ Tray app memory < 200MB
- ✅ Main window opens in < 1s
- ✅ Chat responds in < 500ms
- ✅ Dashboard loads in < 2s

### 14.3 Scalability Metrics

- ✅ Supports 300 logical agents
- ✅ Manages M active slots (10-20)
- ✅ No OOM under normal load
- ✅ Resource gates prevent exhaustion

## 15. References

- [Tray Application Design](./2026-02-15-tray-application-design.md)
- [thegent Install Design](./2026-02-14-thegent-install-design.md)
- [thegent Install Implementation](./2026-02-14-thegent-install-implementation-plan.md)
- [Sitback Design](./2026-02-15-thegent-sitback-design.md)
- [Conversation Dump (TUI research)](../research/CONVERSATION_DUMP_2026-02-16.md)
- [OpenClaw/Agent Zero as Main Agent](../research/OPENCLAW_AGENTZERO_AS_MAIN_AGENT_RESEARCH.md)
- [Multi-Platform Parity](./MULTI_PLATFORM_PARITY_MASTER_PLAN.md)
- [Cross-Platform Research Complete](../research/CROSS_PLATFORM_RESEARCH_COMPLETE.md)
- [Shell Environment Complete](../guides/SHELL_ENVIRONMENT_COMPLETE.md)

---

*Generated: 2026-02-16 | Version: 1.0 | Status: Complete*
