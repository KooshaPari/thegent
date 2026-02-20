"""Doctor module for comprehensive health and preflight checks of thegent environment."""

import os
import platform
import re
import shutil
import subprocess
import time
from pathlib import Path

import httpx
import psutil
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from thegent.config import ThegentSettings
from thegent.infra import run_subprocess_optimized
from thegent.infra.fast_process_monitor import ProcessInfo

console = Console()
_project_root_cache: Path | None = None


class CheckResult:
    def __init__(self, name: str, category: str) -> None:
        self.name = name
        self.category = category
        self.status: str = "pending"  # ok, warn, fail
        self.message: str = ""
        self.details: str | None = None
        self.fix_hint: str | None = None


def run_doctor(
    fix: bool = False,
    runtime: bool = False,
    network: bool = False,
    processes: bool = False,
    memory: bool = False,
    deps: bool = False,
) -> bool:
    """Run all health checks and report results.

    Args:
        fix: Attempt to fix detected issues
        runtime: Show multi-runtime diagnostics
        network: Check network connectivity
        processes: Check process health
        memory: Check memory usage
        deps: Check dependencies
    """
    console.print(Panel("[bold cyan]Thegent Doctor[/bold cyan]\n[dim]Comprehensive environment health check[/dim]"))

    # Project Root Detection
    project_root = Path.cwd()
    if not (project_root / "src" / "thegent").exists():
        # Try to find root by looking up
        curr = project_root
        while curr.parent != curr:
            if (curr / "src" / "thegent").exists():
                project_root = curr
                break
            curr = curr.parent

    if project_root != Path.cwd():
        console.print(f"[yellow]Note: Running from sub-directory. Detected project root at: {project_root}[/yellow]\n")
        os.chdir(project_root)

    # Store project_root for use in other functions
    global _project_root_cache
    _project_root_cache = project_root

    results: list[CheckResult] = []

    # Category: Dependencies
    results.extend(_check_dependencies())

    # Category: Configuration
    results.extend(_check_configuration())

    # Category: Isolation & Persistence
    results.extend(_check_isolation())

    # Category: Connectivity
    results.extend(_check_connectivity())

    # Category: Environment & Shims
    results.extend(_check_environment())

    # Category: Shim Binaries (thegent-hooks, thegent-shims)
    results.extend(_check_shim_binaries())

    # Category: Shell (full setup)
    results.extend(_check_shell())

    # Category: Nix Support
    results.extend(_check_nix())

    # Category: Providers & Headless (ROB-016)
    results.extend(_check_providers())
    results.extend(_check_headless())

    # Category: Runtime Infrastructure
    results.extend(_check_runtime_infrastructure())

    # Category: Process Analysis & Leak Detection
    results.extend(_check_process_leaks())

    # Category: MCP Tools & Sessions
    results.extend(_check_mcp_tools())
    results.extend(_check_sessions())

    # Category: Project hints
    results.extend(_check_project_hints())

    # Category: Performance
    results.extend(_check_performance())

    # Apply fixes if requested
    if fix:
        _apply_fixes(results)

    # Display results
    success = _display_results(results)

    # Show multi-runtime diagnostics if requested
    if runtime:
        try:
            from thegent.infra.multi_runtime_diagnostics import check_all_runtimes, display_runtime_status

            console.print("\n")
            statuses = check_all_runtimes()
            display_runtime_status(statuses)
        except Exception as e:
            console.print(f"[yellow]Could not run multi-runtime diagnostics: {e}[/yellow]")

    # Show network diagnostics if requested
    if network:
        console.print("\n[bold cyan]Network Diagnostics[/bold cyan]")
        # Network checks are already in _check_connectivity, but we can add more here
        console.print("[dim]Network diagnostics integrated into connectivity checks above[/dim]")

    # Show process diagnostics if requested
    if processes:
        console.print("\n[bold cyan]Process Diagnostics[/bold cyan]")
        # Process checks are already in _check_process_leaks, but we can add more here
        console.print("[dim]Process diagnostics integrated into process leak checks above[/dim]")

    # Show memory diagnostics if requested
    if memory:
        console.print("\n[bold cyan]Memory Diagnostics[/bold cyan]")
        try:
            import psutil

            mem = psutil.virtual_memory()
            console.print(f"Total Memory: {mem.total / (1024**3):.2f} GB")
            console.print(f"Available Memory: {mem.available / (1024**3):.2f} GB")
            console.print(f"Used Memory: {mem.used / (1024**3):.2f} GB ({mem.percent}%)")
        except Exception as e:
            console.print(f"[yellow]Could not get memory info: {e}[/yellow]")

    # Show dependency diagnostics if requested
    if deps:
        console.print("\n[bold cyan]Dependency Diagnostics[/bold cyan]")
        # Dependency checks are already in _check_dependencies, but we can add more here
        console.print("[dim]Dependency diagnostics integrated into dependency checks above[/dim]")

    if not success:
        if fix:
            console.print("\n[bold yellow]⚠ Some checks failed. Fixes were attempted where possible.[/bold yellow]")
        else:
            console.print("\n[bold red]✗ Some checks failed. See hints above to fix them.[/bold red]")
            console.print("[dim]Run with --fix to attempt automatic fixes[/dim]")
        console.print("[dim]See docs/guides/TROUBLESHOOTING.md for more help[/dim]")
    else:
        console.print("\n[bold green]✓ All essential checks passed![/bold green]")

    return success


def _check_dependencies() -> list[CheckResult]:
    res_list = []

    # Node.js
    r = CheckResult("Node.js", "Dependencies")
    node_path = shutil.which("node")
    if node_path:
        try:
            result = run_subprocess_optimized(["node", "--version"], capture_output=True, timeout=5)
            if result.returncode == 0 and result.stdout:
                ver = (
                    result.stdout.strip()
                    if isinstance(result.stdout, str)
                    else result.stdout.decode("utf-8", errors="replace").strip()
                )
                r.status = "ok"
                r.message = f"Found Node.js {ver} at {node_path}"
        except Exception as e:
            r.status = "warn"
            r.message = f"Node.js found but failed to get version: {e}"
    else:
        r.status = "fail"
        r.message = "Node.js not found in PATH"
        r.fix_hint = "Install Node.js (v18+) from https://nodejs.org/"
    res_list.append(r)

    # Claude Code
    r = CheckResult("Claude Code CLI", "Dependencies")
    claude_path = shutil.which("claude")
    if claude_path:
        try:
            # claude --version might be slow, just check existence for now
            r.status = "ok"
            r.message = f"Found 'claude' at {claude_path}"
        except Exception:
            r.status = "ok"
            r.message = f"Found 'claude' at {claude_path}"
    else:
        r.status = "fail"
        r.message = "Claude Code CLI ('claude') not found in PATH"
        r.fix_hint = "Install via: npm install -g @anthropic-ai/claude-code"
    res_list.append(r)

    # Codex
    r = CheckResult("Codex CLI", "Dependencies")
    codex_path = shutil.which("codex")
    if codex_path:
        r.status = "ok"
        r.message = f"Found 'codex' at {codex_path}"
    else:
        r.status = "warn"
        r.message = "Codex CLI ('codex') not found in PATH"
        r.fix_hint = "Install via: npm install -g @openai/codex"
    res_list.append(r)

    # CLIProxyAPIPlus
    r = CheckResult("CLIProxyAPIPlus", "Dependencies")
    proxy_path = shutil.which("cli-proxy-api-plus")
    if proxy_path:
        r.status = "ok"
        r.message = f"Found 'cli-proxy-api-plus' at {proxy_path}"
    else:
        r.status = "fail"
        r.message = "CLIProxyAPIPlus binary not found in PATH"
        r.fix_hint = "Download and install from thegent repository or releases."
    res_list.append(r)

    # Tools: git required; rg, fd, jq optional (install for 10x speedup)
    from thegent.errors import get_install_hint

    for tool, name, optional in [
        ("rg", "ripgrep", True),
        ("fd", "fd-find", True),
        ("git", "Git", False),
        ("jq", "jq", True),
    ]:
        r = CheckResult(name, "Dependencies")
        path = shutil.which(tool)
        if path:
            r.status = "ok"
            r.message = f"Found '{tool}' at {path}"
        else:
            r.status = "warn"  # All as warn for graceful degradation
            r.message = f"'{tool}' not found" + (" (optional — install for 10x speedup)" if optional else " in PATH")
            r.fix_hint = get_install_hint(tool)
        res_list.append(r)

    return res_list


def _check_configuration() -> list[CheckResult]:
    res_list = []
    settings = ThegentSettings()
    project_root = _project_root_cache or Path.cwd()

    # OAuth Providers (NO API keys needed - OAuth only)
    # Providers that support OAuth: claude, codex, gemini, copilot, antigravity, iflow, kiro, kilo, roo, qwen, kimi
    from thegent.agents.cliproxy_manager import _OAUTH_AUTH_PREFIXES, _has_oauth_credentials

    oauth_providers = list(_OAUTH_AUTH_PREFIXES.keys())
    oauth_providers.extend(["gemini"])  # gemini uses email-projectId.json pattern

    # Check OAuth credentials - at least ONE provider must be configured
    configured_providers = []
    for provider in sorted(set(oauth_providers)):
        if _has_oauth_credentials(settings, provider):
            configured_providers.append(provider)

    r = CheckResult("OAuth Providers", "Configuration")
    if configured_providers:
        r.status = "ok"
        r.message = f"OAuth credentials found for: {', '.join(configured_providers)}"
    else:
        r.status = "fail"  # Required - at least one OAuth provider must be configured
        r.message = "No OAuth providers configured (OAuth is required, API keys are not used)"
        r.fix_hint = "Run: thegent cliproxy login <provider> (e.g., claude, codex, gemini)"
    res_list.append(r)

    # Note: API keys are NOT checked for OAuth providers - OAuth is the only method

    # CLIProxy Config
    r = CheckResult("CLIProxy Config", "Configuration")
    config_path = settings.cliproxy_config_path.expanduser().resolve()
    if config_path.exists():
        try:
            with open(config_path) as f:
                cfg = yaml.safe_load(f)
            if isinstance(cfg, dict):
                r.status = "ok"
                r.message = f"Config found at {config_path}"
                # Check for OAuth providers (not API key providers)
                from thegent.agents.cliproxy_manager import _OAUTH_AUTH_PREFIXES, _has_oauth_credentials

                oauth_providers = list(_OAUTH_AUTH_PREFIXES.keys())
                configured_count = sum(1 for p in oauth_providers if _has_oauth_credentials(settings, p))
                if configured_count > 0:
                    r.message += f" ({configured_count} OAuth provider(s) configured)"
                else:
                    r.status = "fail"  # Required - at least one provider must be configured
                    r.message += " (no OAuth providers configured)"
                    r.fix_hint = "Run: thegent cliproxy login <provider> (e.g., claude, codex, gemini)"
            else:
                r.status = "fail"
                r.message = f"Config at {config_path} is invalid YAML"
        except Exception as e:
            r.status = "fail"
            r.message = f"Failed to read config at {config_path}: {e}"
    else:
        r.status = "fail"
        r.message = f"CLIProxy config not found: {config_path}"
        r.fix_hint = "Run: thegent setup (or create the config file manually)"
    res_list.append(r)

    return res_list


def _check_isolation() -> list[CheckResult]:
    res_list = []
    settings = ThegentSettings()

    # CLAUDE_CONFIG_DIR
    r = CheckResult("Claude Config Isolation", "Isolation")
    cache_dir = Path.home() / ".cache" / "thegent" / "claude-config"
    if cache_dir.exists() and cache_dir.is_dir():
        r.status = "ok"
        r.message = f"Isolated config directory exists: {cache_dir}"

        # Check for essential symlinks
        missing_links = []
        for item in [".claude.json", "__store.db"]:
            if not (cache_dir / item).exists():
                missing_links.append(item)

        if missing_links:
            r.status = "warn"
            r.message += f" (missing: {', '.join(missing_links)})"
            r.fix_hint = "Run 'clode' once to initialize symlinks."
    else:
        r.status = "warn"
        r.message = f"Isolated config directory not found: {cache_dir}"
        r.fix_hint = "It will be created automatically on first 'clode' run."
    res_list.append(r)

    return res_list


def _ensure_mcp_running(settings: ThegentSettings, timeout: int = 30) -> bool:
    """Ensure MCP server and CLIProxy are running. Returns True if started successfully."""
    mcp_url = f"http://{settings.mcp_host}:{settings.mcp_port}/health"
    try:
        resp = httpx.get(mcp_url, timeout=2.0)
        if resp.status_code == 200:
            return True  # Already running
    except Exception:
        pass

    # Try to start MCP + proxy via process-compose
    console.print("[yellow]MCP server not running. Starting automatically...[/yellow]")
    try:
        from thegent.mcp_manage import mcp_up

        success, msg = mcp_up()
        if success:
            # Wait for it to become ready
            for _ in range(timeout * 2):  # Check for timeout seconds
                time.sleep(0.5)
                try:
                    resp = httpx.get(mcp_url, timeout=1.0)
                    if resp.status_code == 200:
                        console.print("[green]MCP server started successfully.[/green]")
                        return True
                except Exception:
                    continue
            console.print("[red]Timeout waiting for MCP server to start.[/red]")
            return False
        console.print(f"[red]Failed to start MCP server: {msg}[/red]")
        return False
    except Exception as e:
        console.print(f"[red]Failed to start MCP server: {e}[/red]")
        return False


def _check_connectivity(auto_start: bool = True) -> list[CheckResult]:
    res_list = []
    settings = ThegentSettings()

    # MCP Server
    r = CheckResult("MCP Server", "Connectivity")
    mcp_url = f"http://{settings.mcp_host}:{settings.mcp_port}/health"
    try:
        resp = httpx.get(mcp_url, timeout=2.0)
        if resp.status_code == 200:
            r.status = "ok"
            r.message = f"MCP server reachable at {mcp_url}"
        else:
            r.status = "warn"
            r.message = f"MCP server returned {resp.status_code} at {mcp_url}"
            r.details = "Suspicion Level: LOW\nMCP server returned non-200 status."
            if auto_start:
                if _ensure_mcp_running(settings):
                    r.message = "MCP server started"
                    r.status = "ok"
                else:
                    r.fix_hint = "Run: thegent mcp up"
            else:
                r.fix_hint = "Run: thegent serve (or thegent mcp up)"
    except Exception as e:
        r.status = "warn"
        r.message = f"MCP server not reachable: {e}"
        r.details = "Suspicion Level: LOW\nMCP server is not running."
        if auto_start:
            if _ensure_mcp_running(settings):
                r.message = "MCP server started"
                r.status = "ok"
            else:
                r.fix_hint = "Run: thegent mcp up"
        else:
            r.fix_hint = "Run: thegent serve (or thegent mcp up)"
    res_list.append(r)

    # CLIProxy
    r = CheckResult("CLIProxy", "Connectivity")
    proxy_url = "http://127.0.0.1:8317/v1/models"
    try:
        resp = httpx.get(proxy_url, timeout=2.0)
        if resp.status_code == 200:
            r.status = "ok"
            r.message = "CLIProxy reachable at http://127.0.0.1:8317"
        else:
            r.status = "warn"
            r.message = f"CLIProxy returned {resp.status_code} at {proxy_url}"
            r.fix_hint = "Run: thegent mcp up (starts proxy + MCP)"
    except Exception:
        r.status = "warn"
        r.message = "CLIProxy not currently running"
        r.fix_hint = "Run: thegent mcp up (starts proxy + MCP)"
    res_list.append(r)

    return res_list


def _check_environment() -> list[CheckResult]:
    res_list = []

    # PATH check for ~/.local/bin
    r = CheckResult("Shim PATH", "Environment")
    local_bin = str(Path.home() / ".local" / "bin")
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    if local_bin in path_dirs:
        # Check if it's early in PATH
        if path_dirs.index(local_bin) < 5:
            r.status = "ok"
            r.message = "~/.local/bin is correctly placed early in PATH"
        else:
            r.status = "warn"
            r.message = "~/.local/bin is in PATH but late; shims might be overridden"
            r.fix_hint = "Move ~/.local/bin to the front of your PATH in your shell profile."
    else:
        r.status = "fail"
        r.message = "~/.local/bin not found in PATH"
        r.fix_hint = f"Add {local_bin} to your PATH."
    res_list.append(r)

    # Shims installation
    r = CheckResult("Tool Shims", "Environment")
    bin_dir = Path.home() / ".local" / "bin"
    installed_shims = []
    shim_details = {}  # Store shim details for version/binary checks

    for shim in ["git", "grep", "find", "jq", "uv", "clode", "codex", "copilot", "droid", "roid"]:
        shim_path = bin_dir / shim
        if shim_path.exists():
            installed_shims.append(shim)
            # Check shim type and resolve target binary
            try:
                content = shim_path.read_text()
                # Check if it's a symlink
                if shim_path.is_symlink():
                    target = shim_path.resolve()
                    shim_details[shim] = {"type": "symlink", "target": str(target), "exists": target.exists()}
                # Check if it's a shell script shim
                elif "thegent" in content.lower() or "shim" in content.lower():
                    # Try to extract target binary from script
                    lines = content.split("\n")
                    target_binary = None
                    for line in lines[:20]:  # Check first 20 lines
                        line_lower = line.lower()
                        # New format: REAL_GIT="$(resolve_real_binary git || true)"
                        # Or: REAL_BIN="$(PATH="$SEARCH_PATH" command -v codex ...)"
                        if "real_" in line_lower:
                            if "resolve_real_binary" in line_lower:
                                match = re.search(r"resolve_real_binary\s+([a-z-]+)", line_lower)
                                if match:
                                    target_binary = shutil.which(match.group(1))
                                    if target_binary:
                                        break
                            elif "command -v" in line_lower:
                                match = re.search(r"command -v\s+([a-z-]+)", line_lower)
                                if match:
                                    target_binary = shutil.which(match.group(1))
                                    if target_binary:
                                        break

                        if "exec" in line_lower or "which" in line_lower:
                            # Try to extract binary path
                            parts = line.split()
                            for i, part in enumerate(parts):
                                if part in ["exec", "which"] and i + 1 < len(parts):
                                    potential_binary = parts[i + 1].strip("'\"")
                                    if "/" in potential_binary or potential_binary in [
                                        "git",
                                        "grep",
                                        "find",
                                        "jq",
                                        "uv",
                                        "clode",
                                        "codex",
                                        "copilot",
                                        "droid",
                                        "roid",
                                    ]:
                                        target_binary = shutil.which(potential_binary)
                                        break
                            if target_binary:
                                break
                    shim_details[shim] = {
                        "type": "script",
                        "target": target_binary,
                        "exists": target_binary is not None and Path(target_binary).exists()
                        if target_binary
                        else False,
                    }
                else:
                    shim_details[shim] = {"type": "unknown", "target": None, "exists": False}
            except (OSError, UnicodeDecodeError):
                shim_details[shim] = {"type": "unknown", "target": None, "exists": False}

    # Codex/Copilot: must resolve to ~/.local/bin (avoids "git: 'X' is not a git command")
    for agent in ["codex", "copilot"]:
        agent_path = shutil.which(agent)
        if agent_path:
            r_agent = CheckResult(f"{agent} path", "Environment")
            if ".local/bin" in agent_path:
                r_agent.status = "ok"
                r_agent.message = f"{agent} -> {agent_path} (thegent shim)"
            else:
                r_agent.status = "warn"
                r_agent.message = f"{agent} -> {agent_path} (not thegent shim; may cause git errors)"
                r_agent.fix_hint = "Run: thegent install-shims --force  (ensure ~/.local/bin is first in PATH)"
            res_list.append(r_agent)

    # Harmful ps shim check (shadows system ps, causes 130s+ hangs)
    ps_shim = bin_dir / "ps"
    if ps_shim.exists():
        try:
            content = ps_shim.read_text()
            if "thegent" in content and "ps" in content:
                r_ps = CheckResult("ps Shim (harmful)", "Environment")
                r_ps.status = "fail"
                r_ps.message = "~/.local/bin/ps shadows system ps; causes 130s+ hangs when agents run 'ps aux'"
                r_ps.fix_hint = "Run: rm ~/.local/bin/ps  (or: thegent install-shims --force)"
                res_list.append(r_ps)
        except OSError:
            pass

    if len(installed_shims) >= 6:
        r.status = "ok"
        r.message = f"Installed shims: {', '.join(installed_shims)}"
    elif installed_shims:
        r.status = "warn"
        r.message = f"Only some shims installed: {', '.join(installed_shims)}"
        r.fix_hint = "Run: thegent install-shims --all"
    else:
        r.status = "fail"
        r.message = "No thegent tool shims found in ~/.local/bin"
        r.fix_hint = "Run: thegent install-shims --all"
    res_list.append(r)

    # Enhanced: Check shim versions and binary availability
    for shim_name, details in shim_details.items():
        if details.get("type") == "unknown":
            continue

        r_shim = CheckResult(f"{shim_name} Shim Details", "Environment")

        # Check if target binary exists
        target = details.get("target")
        exists = details.get("exists", False)

        if target and exists:
            # Try to get version if possible
            version_info = None
            try:
                if shim_name in ["git", "grep", "find", "jq", "uv"]:
                    # Try to get version from binary
                    if shim_name == "git":
                        result = run_subprocess_optimized(["git", "--version"], capture_output=True, timeout=2)
                        if result.returncode == 0 and result.stdout:
                            stdout_text = (
                                result.stdout
                                if isinstance(result.stdout, str)
                                else result.stdout.decode("utf-8", errors="replace")
                            )
                            version_info = stdout_text.strip()
                    elif shim_name == "grep":
                        result = run_subprocess_optimized(["grep", "--version"], capture_output=True, timeout=2)
                        if result.returncode == 0 and result.stdout:
                            stdout_text = (
                                result.stdout
                                if isinstance(result.stdout, str)
                                else result.stdout.decode("utf-8", errors="replace")
                            )
                            version_info = stdout_text.split("\n")[0] if stdout_text else None
                    elif shim_name == "uv":
                        result = run_subprocess_optimized(["uv", "--version"], capture_output=True, timeout=2)
                        if result.returncode == 0 and result.stdout:
                            stdout_text = (
                                result.stdout
                                if isinstance(result.stdout, str)
                                else result.stdout.decode("utf-8", errors="replace")
                            )
                            version_info = stdout_text.strip()
            except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
                pass

            if version_info:
                r_shim.status = "ok"
                r_shim.message = f"{shim_name} -> {target} ({version_info})"
            else:
                r_shim.status = "ok"
                r_shim.message = f"{shim_name} -> {target} (binary available)"
        elif target:
            r_shim.status = "warn"
            r_shim.message = f"{shim_name} -> {target} (target binary not found)"
            r_shim.fix_hint = f"Install {shim_name} or fix shim target"
        else:
            r_shim.status = "warn"
            r_shim.message = f"{shim_name} shim exists but target unclear"

        res_list.append(r_shim)

    return res_list


def _check_shim_binaries() -> list[CheckResult]:
    """Check thegent-hooks and thegent-shims (Rust) binary version and availability."""
    res_list: list[CheckResult] = []

    for name, candidates in [
        ("thegent-hooks", ["thegent-hooks", "crates/target/release/thegent-hooks"]),
        ("thegent-shims", ["thegent-shims", "crates/target/release/thegent-shims"]),
    ]:
        r = CheckResult(name, "Shim Binaries")
        bin_path = shutil.which(name)
        if not bin_path:
            # Try project-relative path
            root = _project_root_cache or Path.cwd()
            for rel in candidates[1:]:
                p = root / rel
                if p.exists() and p.is_file():
                    bin_path = str(p)
                    break
        if bin_path:
            bin_file = Path(bin_path)
            # Check binary exists and is executable
            if not bin_file.exists():
                r.status = "fail"
                r.message = f"{name} path {bin_path} does not exist"
                r.fix_hint = "Build with: cd crates && cargo build --release"
            elif not os.access(bin_path, os.X_OK):
                r.status = "warn"
                r.message = f"{name} at {bin_path} is not executable"
                r.fix_hint = f"Fix permissions: chmod +x {bin_path}"
            else:
                # Try to get version
                try:
                    out = run_subprocess_optimized(
                        [bin_path, "--version"],
                        capture_output=True,
                        timeout=2,
                        check=False,
                    )
                    stdout_text = (
                        out.stdout
                        if isinstance(out.stdout, str)
                        else (out.stdout.decode("utf-8", errors="replace") if out.stdout else "")
                    )
                    stderr_text = (
                        out.stderr
                        if isinstance(out.stderr, str)
                        else (out.stderr.decode("utf-8", errors="replace") if out.stderr else "")
                    )
                    ver = (stdout_text or stderr_text or "").strip().split("\n")[0] or "unknown"
                    r.status = "ok"
                    r.message = f"{name} at {bin_path}: {ver}"
                    # Add file size and modification time for additional info
                    try:
                        stat = bin_file.stat()
                        size_mb = stat.st_size / (1024 * 1024)
                        mtime = time.strftime("%Y-%m-%d", time.localtime(stat.st_mtime))
                        r.details = f"Size: {size_mb:.2f}MB, Modified: {mtime}"
                    except OSError:
                        pass
                except subprocess.TimeoutExpired:
                    r.status = "warn"
                    r.message = f"{name} at {bin_path} (version check timed out)"
                except Exception as e:
                    r.status = "warn"
                    r.message = f"{name} found at {bin_path} but --version failed: {e}"
        else:
            r.status = "info"
            r.message = f"{name} not found (optional Rust binary)"
            r.fix_hint = "Build with: cd crates && cargo build --release"
        res_list.append(r)

    return res_list


def _check_shell() -> list[CheckResult]:
    """Comprehensive shell setup checks: configs, plugins, prompt, runtime."""
    res_list: list[CheckResult] = []
    home = Path.home()

    # Core configs (thegent-managed)
    for name, path in [
        (".zshenv", home / ".zshenv"),
        (".zshrc", home / ".zshrc"),
        (".zsh_bundle.zsh", home / ".zsh_bundle.zsh"),
    ]:
        r = CheckResult(name, "Shell")
        if path.exists():
            try:
                content = path.read_text()
                if "thegent" in content or "THEGENT" in content:
                    r.status = "ok"
                    r.message = f"{name} present (thegent-managed)"
                else:
                    r.status = "warn"
                    r.message = f"{name} exists but may not be thegent-managed"
            except OSError:
                r.status = "warn"
                r.message = f"{name} exists (unreadable)"
        else:
            r.status = "fail"
            r.message = f"{name} missing"
            r.fix_hint = "Run: thegent install -t shell"
        res_list.append(r)

    # zshrc.local (user plugins — optional but recommended)
    r = CheckResult(".zshrc.local", "Shell")
    zshrc_local = home / ".zshrc.local"
    if zshrc_local.exists():
        r.status = "ok"
        r.message = "~/.zshrc.local present (plugins, prompt, runtime)"
    else:
        r.status = "warn"
        r.message = "~/.zshrc.local missing (no fnm/mise, fzf-tab, prompt)"
        r.fix_hint = "Run: thegent install -t shell  (creates from template)"
    res_list.append(r)

    # Plugins
    plugins_dir = home / ".zsh" / "plugins"
    for plugin in ["fzf-tab", "zsh-autosuggestions", "fast-syntax-highlighting"]:
        r = CheckResult(f"Plugin: {plugin}", "Shell")
        if (plugins_dir / plugin).exists():
            r.status = "ok"
            r.message = f"{plugin} installed"
        else:
            r.status = "warn"
            r.message = f"{plugin} not installed"
            r.fix_hint = "Run: thegent install -t shell  (or: ./scripts/install_zsh_plugins.sh)"
        res_list.append(r)

    # Prompt (starship or powerlevel10k)
    r = CheckResult("Prompt", "Shell")
    has_starship = shutil.which("starship") is not None
    has_p10k = (home / ".zsh" / "themes" / "powerlevel10k").exists()
    if has_starship or has_p10k:
        r.status = "ok"
        r.message = "starship" if has_starship else "powerlevel10k"
    else:
        r.status = "warn"
        r.message = "No prompt (starship/p10k)"
        r.fix_hint = "brew install starship  or  git clone powerlevel10k to ~/.zsh/themes/"
    res_list.append(r)

    # Runtime (mise or fnm)
    r = CheckResult("Runtime (Node)", "Shell")
    has_mise = shutil.which("mise") is not None
    has_fnm = shutil.which("fnm") is not None
    if has_mise or has_fnm:
        r.status = "ok"
        r.message = "mise" if has_mise else "fnm"
    else:
        r.status = "warn"
        r.message = "No Node version manager (mise/fnm)"
        r.fix_hint = "brew install mise  or  brew install fnm"
    res_list.append(r)

    return res_list


def _check_nix_daemon_status() -> tuple[bool, str]:
    """Check if Nix daemon is running. Returns (is_running, status_message)."""
    if platform.system() == "Darwin":
        # macOS: use launchctl
        try:
            result = run_subprocess_optimized(
                ["launchctl", "list"],
                check=False,
                capture_output=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout:
                output = (
                    result.stdout if isinstance(result.stdout, str) else result.stdout.decode("utf-8", errors="replace")
                )
                if "com.determinate.nix-daemon" in output or "nix-daemon" in output.lower():
                    return True, "Running (launchd)"
                # Also check for determinate-nixd process
                if "determinate-nixd" in output.lower():
                    return True, "Running (determinate-nixd)"
            return False, "Not running (launchd)"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, "Cannot check (launchctl not available)"
    elif platform.system() == "Linux":
        # Linux: use systemctl
        try:
            result = run_subprocess_optimized(
                ["systemctl", "--user", "status", "nix-daemon"],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return True, "Running (systemd)"
            return False, "Not running (systemd)"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False, "Cannot check (systemctl not available)"
    return False, "Unknown platform"


def _check_nix() -> list[CheckResult]:
    """Check Nix-related setup. Shows warnings (not failures) for optional Nix dependency."""
    res_list = []
    nix_path = shutil.which("nix")

    # Nix command
    r = CheckResult("Nix Installed", "Nix Support")
    if nix_path:
        try:
            result = run_subprocess_optimized(["nix", "--version"], capture_output=True, timeout=5)
            if result.returncode == 0 and result.stdout:
                ver = (
                    result.stdout.strip()
                    if isinstance(result.stdout, str)
                    else result.stdout.decode("utf-8", errors="replace").strip()
                )
                r.status = "ok"
                r.message = f"Found Nix: {ver}"
        except subprocess.TimeoutExpired:
            r.status = "warn"
            r.message = "Nix command timed out"
            r.fix_hint = "Nix may be initializing. Try again in a moment."
        except Exception:
            # Try alternative method to verify Nix
            if Path("/nix/var/nix/profiles/default/bin/nix").exists():
                r.status = "ok"
                r.message = "Found Nix (Determinate Systems)"
            else:
                r.status = "ok"
                r.message = "Found Nix in PATH"
    # Check if Nix is installed but not in PATH (may need shell reload)
    elif Path("/nix/var/nix/profiles/default/bin/nix").exists():
        r.status = "warn"
        r.message = "Nix installed but not in PATH"
        r.fix_hint = "Reload shell or run: . ~/.zshenv"
    else:
        r.status = "warn"  # Warning, not failure - Nix is optional
        r.message = "Nix not found (optional)"
        r.fix_hint = "Install Nix from https://nixos.org/ or use Determinate Systems installer."
    res_list.append(r)

    # Nix daemon status (only check if Nix is installed)
    if nix_path:
        r = CheckResult("Nix Daemon", "Nix Support")
        daemon_running, daemon_msg = _check_nix_daemon_status()
        if daemon_running:
            r.status = "ok"
            r.message = daemon_msg
        else:
            r.status = "warn"  # Warning, not failure
            r.message = daemon_msg
            r.fix_hint = "Nix daemon may start automatically when needed"
        res_list.append(r)

    # flake.nix (only checked if Nix is installed)
    r = CheckResult("Flake config", "Nix Support")
    project_root = _project_root_cache or Path.cwd()
    flake_path = project_root / "flake.nix"
    try:
        if flake_path.exists():
            r.status = "ok"
            r.message = "flake.nix exists"
        elif nix_path:
            # Only fail if Nix is installed but flake.nix is missing
            r.status = "fail"  # Required if Nix is installed
            r.message = "flake.nix missing (required for Nix development environment)"
            r.fix_hint = "Create flake.nix or remove Nix if not using it"
        else:
            # Nix not installed - this is fine, just skip the check
            r.status = "ok"
            r.message = "flake.nix not needed (Nix not installed)"
    except Exception:
        r.status = "fail"
        r.message = "Could not check flake.nix (permission error)"
    res_list.append(r)

    # direnv / .envrc
    r = CheckResult("direnv integration", "Nix Support")
    if Path(".envrc").exists():
        r.status = "ok"
        r.message = ".envrc exists"
        if not shutil.which("direnv"):
            r.status = "warn"  # Warning, not failure
            r.message += " but 'direnv' command not found"
            r.fix_hint = "Install direnv: brew install direnv"
    else:
        r.status = "warn"  # Warning, not failure
        r.message = ".envrc missing"
        r.fix_hint = "Run: thegent install (to regenerate environment files)"
    res_list.append(r)

    return res_list


def _get_configured_providers_from_cliproxy() -> set[str]:
    """Get provider names from cliproxy config (openai-compatibility + OAuth)."""
    configured: set[str] = set()
    try:
        from thegent.agents.cliproxy_manager import _ensure_config, _has_oauth_credentials
        from thegent.config import ThegentSettings

        settings = ThegentSettings()
        config_path = _ensure_config(settings)
        if not config_path.exists():
            return configured
        raw = yaml.safe_load(config_path.read_text()) or {}
        config = raw if isinstance(raw, dict) else {}
        compat = config.get("openai-compatibility") or []
        for entry in compat:
            if isinstance(entry, dict):
                name = entry.get("name", "").strip()
                if name:
                    configured.add(name.lower())
        for prov in [
            "claude",
            "codex",
            "gemini",
            "copilot",
            "antigravity",
            "iflow",
            "kiro",
            "kilo",
            "roo",
            "qwen",
            "kimi",
        ]:
            if _has_oauth_credentials(settings, prov):
                configured.add(prov)
    except Exception:
        pass
    return configured


def _check_providers() -> list[CheckResult]:
    """Validate all configured OAuth providers via proxy (ROB-016).

    REQUIRES OAuth credentials - API keys are NOT used for OAuth-capable providers.
    Checks providers from /v1/models AND cliproxy config so nothing is missed.
    """
    res_list: list[CheckResult] = []
    proxy_url = "http://127.0.0.1:8317/v1/models"
    providers_from_models: dict[str, list[str]] = {}
    configured_providers = _get_configured_providers_from_cliproxy()

    try:
        resp = httpx.get(proxy_url, timeout=5.0)
        if resp.status_code != 200:
            r = CheckResult("Models API", "Providers")
            r.status = "warn"  # Changed from fail to warn
            r.message = f"Could not fetch models from proxy (HTTP {resp.status_code})"
            r.details = "Suspicion Level: LOW\nCLIProxy returned non-200 status. This is OK if you're not using provider validation."
            r.fix_hint = "Ensure CLIProxy is running: thegent mcp up"
            res_list.append(r)
            return res_list
    except (httpx.ConnectError, httpx.ConnectTimeout) as e:
        # Connection refused or timeout - CLIProxy not running
        r = CheckResult("Providers", "Providers")
        r.status = "warn"  # Changed from fail to warn - CLIProxy may not be needed for all workflows
        r.message = f"CLIProxy not reachable: {e}"
        r.details = "Suspicion Level: LOW\nCLIProxy is not running. This is OK if you're not using provider validation."
        r.fix_hint = "Start CLIProxy if needed: thegent mcp up"
        res_list.append(r)
        return res_list

    try:
        data = resp.json()
        models = data.get("models", []) or data.get("data", [])

        for m in models:
            provider = m.get("owned_by", "unknown")
            mid = m.get("id")
            if provider not in providers_from_models:
                providers_from_models[provider] = []
            providers_from_models[provider].append(mid)

        all_providers = set(providers_from_models) | configured_providers
        for provider in sorted(all_providers):
            r = CheckResult(f"Provider: {provider}", "Providers")
            p_models = providers_from_models.get(provider, [])
            test_model = p_models[0] if p_models else None
            if not test_model:
                try:
                    from thegent.agents.cliproxy_manager import (
                        PROVIDER_LOGIN_CONFIG,
                        _get_provider_definitions,
                    )

                    # Try PROVIDER_LOGIN_CONFIG first (has model field for OAuth providers)
                    login_cfg = PROVIDER_LOGIN_CONFIG.get(provider.lower(), {})
                    if login_cfg.get("model"):
                        test_model = login_cfg["model"]
                    else:
                        # Fallback to provider_definitions.json
                        defs_ = _get_provider_definitions()
                        cfg = defs_.get(provider, {}) if isinstance(defs_.get(provider), dict) else {}
                        test_model = cfg.get("model")

                    # If still no model and provider has no models in /v1/models, skip validation
                    if not test_model and not p_models:
                        r.status = "warn"
                        r.message = "No models available (provider may need configuration)"
                        r.fix_hint = f"Run: thegent cliproxy login {provider}"
                        res_list.append(r)
                        continue

                    # Last resort: use provider name (may fail, but better than skipping)
                    if not test_model:
                        test_model = provider
                except Exception:
                    # If we can't get model info and no models from /v1/models, skip
                    if not p_models:
                        r.status = "warn"
                        r.message = "No models available (provider may need configuration)"
                        r.fix_hint = f"Run: thegent cliproxy login {provider}"
                        res_list.append(r)
                        continue
                    test_model = provider
            try:
                payload = {"model": test_model, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1}
                test_resp = httpx.post(
                    "http://127.0.0.1:8317/v1/chat/completions",
                    json=payload,
                    timeout=20.0,
                )
                if test_resp.status_code == 200:
                    r.status = "ok"
                    r.message = f"Validated ({len(p_models)} models)" if p_models else "Validated"
                else:
                    r.status = "fail"  # Required feature - providers must work
                    r.message = f"HTTP {test_resp.status_code}"
                    try:
                        err = test_resp.json()
                        msg = err.get("error", {}).get("message", test_resp.text[:100])
                        r.details = msg
                    except Exception:
                        r.details = test_resp.text[:100]
                    # Check if it's an auth error - suggest OAuth login
                    if test_resp.status_code in (401, 403):
                        r.fix_hint = f"OAuth authentication failed. Run: thegent cliproxy login {provider}"
                    else:
                        r.fix_hint = f"Check provider configuration: thegent cliproxy login {provider}"
            except Exception as e:
                r.status = "fail"  # Required feature
                r.message = f"Inaccessible: {e!s}"
                r.fix_hint = f"Check OAuth credentials: thegent cliproxy login {provider}"
            res_list.append(r)

        if not all_providers:
            r = CheckResult("Providers", "Providers")
            r.status = "fail"  # Required - at least one provider must be configured
            r.message = "No active providers found in proxy"
            r.fix_hint = "Run: thegent cliproxy login <provider> (e.g., claude, codex, gemini)"
            res_list.append(r)

    except Exception as e:
        r = CheckResult("Providers", "Providers")
        # Distinguish between connection errors (CLIProxy not running) and other errors
        if "Connection refused" in str(e) or "ConnectError" in str(type(e).__name__):
            r.status = "warn"  # Changed from fail to warn - CLIProxy may not be needed
            r.message = f"CLIProxy not reachable: {e}"
            r.details = (
                "Suspicion Level: LOW\nCLIProxy is not running. This is OK if you're not using provider validation."
            )
            r.fix_hint = "Start CLIProxy if needed: thegent mcp up"
        else:
            r.status = "fail"
            r.message = f"Failed to fetch providers: {e}"
            r.details = f"Error details: {str(e)[:200]}"
            r.fix_hint = "Ensure CLIProxy is running: thegent mcp up"
        res_list.append(r)

    return res_list


def _is_process_actively_working(pid: int, min_cpu_percent: float = 0.1, min_io_bytes: int = 1024) -> tuple[bool, str]:
    """
    Check if a process is actively working (not stuck) by monitoring CPU and I/O activity.

    Returns (is_active, reason) where is_active=True means process is working.
    A process is considered active if:
    - CPU usage > min_cpu_percent over a short interval, OR
    - I/O activity detected (read/write bytes), OR
    - Process has network connections, OR
    - Process is long-running (>1 hour) - assumed active (user's chats run for hours)
    """
    try:
        import psutil

        proc = psutil.Process(pid)

        # Check process status
        status = proc.status()
        if status == psutil.STATUS_ZOMBIE:
            return False, "zombie process"

        # Check if it's been running for a while - long-running sessions are OK
        create_time = proc.create_time()
        runtime = time.time() - create_time
        if runtime > 3600:  # Running for > 1 hour
            # For long-running processes, be more lenient - assume active unless clearly stuck
            # Check for network connections as a sign of activity
            try:
                connections = proc.connections()
                if connections:
                    return (
                        True,
                        f"long-running session ({runtime / 3600:.1f}h) with {len(connections)} network connections",
                    )
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
            # Long-running with no obvious activity - still assume active (user's chats run for hours)
            return True, f"long-running session ({runtime / 3600:.1f}h, assumed active)"

        # For shorter runs, check for actual activity
        # Sample CPU usage over short interval (0.5s)
        try:
            cpu_percent = proc.cpu_percent(interval=0.5)
            if cpu_percent > min_cpu_percent:
                return True, f"CPU active ({cpu_percent:.1f}%)"
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass

        # Check I/O counters
        try:
            io_counters = proc.io_counters()
            if io_counters:
                read_bytes = io_counters.read_bytes
                write_bytes = io_counters.write_bytes
                if read_bytes > min_io_bytes or write_bytes > min_io_bytes:
                    return True, f"I/O active (R:{read_bytes} W:{write_bytes})"
        except (psutil.AccessDenied, psutil.NoSuchProcess, AttributeError):
            pass

        # Check if process has network connections (indicates activity)
        try:
            connections = proc.connections()
            if connections:
                return True, f"network active ({len(connections)} connections)"
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass

        # If process is running/sleeping but no activity detected and runtime < 1 hour
        # Only flag as stuck if runtime > 5 minutes AND no activity
        if runtime > 300:  # > 5 minutes
            return False, "no recent activity detected (may be stuck)"

        # Very short runtime - assume active
        return True, f"recently started ({runtime:.0f}s, assumed active)"
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        return False, f"cannot access process: {e}"
    except Exception as e:
        return False, f"error checking process: {e}"


def _find_stuck_processes(command_patterns: list[str], max_age_seconds: int = 300) -> list[tuple[int, str, str]]:
    """
    Find processes matching command patterns that appear to be stuck (not actively working).

    Uses fast process monitor for better performance.

    Returns list of (pid, command, reason) for stuck processes.
    Only flags processes that:
    - Match the command pattern
    - Have been running > max_age_seconds
    - Show no recent activity (CPU, I/O, network)
    """
    stuck = []
    try:
        from thegent.infra.fast_process_monitor import get_fast_monitor

        monitor = get_fast_monitor()
        now = time.time()

        # Use fast process finder
        matching_processes = monitor.find_by_command(command_patterns)

        for info in matching_processes:
            try:
                runtime = now - info.create_time

                # Only check processes that have been running for a while
                if runtime < max_age_seconds:
                    continue

                # Check if process is actively working
                is_active, reason = _is_process_actively_working(info.pid)
                if not is_active:
                    stuck.append((info.pid, info.cmdline[:100], reason))
            except Exception:
                continue
    except ImportError:
        # Fallback to psutil if fast monitor not available
        try:
            import psutil

            for proc in psutil.process_iter(["pid", "name", "cmdline", "create_time"]):
                try:
                    cmdline = " ".join(proc.info["cmdline"] or [])
                    if not any(pattern in cmdline for pattern in command_patterns):
                        continue

                    pid = proc.info["pid"]
                    runtime = time.time() - proc.info["create_time"]

                    if runtime < max_age_seconds:
                        continue

                    is_active, reason = _is_process_actively_working(pid)
                    if not is_active:
                        stuck.append((pid, cmdline[:100], reason))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except ImportError:
            pass  # No monitoring available
    except Exception:
        pass  # Ignore errors in process enumeration

    return stuck


def _check_headless() -> list[CheckResult]:
    """Perform headless test runs for Claude and Codex (ROB-016).

    REQUIRES OAuth credentials (not API keys) for providers that support OAuth.
    Checks for stuck processes before running tests to avoid false failures.
    """
    res_list = []
    from thegent.agents.cliproxy_manager import _has_oauth_credentials

    # Check for stuck processes before running headless tests
    # Only flag processes that are > 5 minutes old AND show no activity
    # Long-running sessions (>1 hour) are assumed active (user's chats run for hours)
    stuck_claude = _find_stuck_processes(["claude", "clode"], max_age_seconds=300)
    stuck_codex = _find_stuck_processes(["codex", "dex", "codex flash"], max_age_seconds=300)
    stuck_droid = _find_stuck_processes(["droid", "roid"], max_age_seconds=300)

    # Claude Headless (requires OAuth, not API key)
    r = CheckResult("Claude Headless", "Headless Runs")
    if not shutil.which("clode"):
        r.status = "fail"  # Required feature
        r.message = "clode shim not found in PATH"
        r.fix_hint = "Run: thegent install-shims --all"
        res_list.append(r)
    # Check if OAuth credentials exist (required for headless runs)
    elif not _has_oauth_credentials(ThegentSettings(), "claude"):
        r.status = "fail"
        r.message = "Skipped (Claude OAuth credentials not found)"
        r.fix_hint = "Run: thegent cliproxy login claude"
        res_list.append(r)
    elif stuck_claude:
        # Warn about stuck processes but don't fail - long-running sessions are OK
        stuck_info = ", ".join([f"PID {pid}" for pid, _, _ in stuck_claude[:3]])
        r.status = "warn"
        r.message = f"Potential stuck processes detected: {stuck_info}"
        r.details = "Long-running sessions are OK if actively working. Doctor will skip headless test."
        r.fix_hint = "Check processes manually: ps aux | grep claude"
        res_list.append(r)
    else:
        try:
            # Try a very simple print run
            process = run_subprocess_optimized(
                ["clode", "haiku", "--print", "respond with 'pong'"],
                capture_output=True,
                timeout=90,  # Increased timeout
                env={**os.environ, "THGENT_DEBUG": "0", "THGENT_LOG_LEVEL": "ERROR"},
            )
            stdout_text = (
                process.stdout
                if isinstance(process.stdout, str)
                else (process.stdout.decode("utf-8", errors="replace") if process.stdout else "")
            )
            stderr_text = (
                process.stderr
                if isinstance(process.stderr, str)
                else (process.stderr.decode("utf-8", errors="replace") if process.stderr else "")
            )
            if process.returncode == 0 and stdout_text and "pong" in stdout_text.lower():
                r.status = "ok"
                r.message = "Claude Code headless run successful"
            else:
                r.status = "fail"  # Required feature
                r.message = f"Claude Code headless run failed (code {process.returncode})"
                # Capture last line or interesting part
                output = (stderr_text or stdout_text or "").strip()
                if output:
                    r.details = output.splitlines()[-1] if "\n" in output else output[:200]
                r.fix_hint = "Check OAuth credentials: thegent cliproxy login claude"
        except subprocess.TimeoutExpired:
            r.status = "warn"  # Changed from fail to warn - timeout might be due to active sessions
            r.message = "Claude Code headless run timed out (90s)"
            r.details = "This may be normal if other Claude sessions are actively running"
            r.fix_hint = "Check for active sessions: ps aux | grep claude"
        except Exception as e:
            r.status = "fail"  # Required feature
            r.message = f"Claude Code headless run error: {str(e)[:100]}"
            r.fix_hint = "Check OAuth credentials: thegent cliproxy login claude"
        res_list.append(r)

    # Codex Headless (requires OAuth, not API key)
    r = CheckResult("Codex Headless", "Headless Runs")
    if not shutil.which("dex"):
        r.status = "fail"  # Required feature
        r.message = "dex shim not found in PATH"
        r.fix_hint = "Run: thegent install-shims --all"
        res_list.append(r)
    # Check if OAuth credentials exist (required for headless runs)
    elif not _has_oauth_credentials(ThegentSettings(), "codex"):
        r.status = "fail"
        r.message = "Skipped (Codex OAuth credentials not found)"
        r.fix_hint = "Run: thegent cliproxy login codex"
        res_list.append(r)
    elif stuck_codex:
        # Warn about stuck processes but don't fail - long-running sessions are OK
        stuck_info = ", ".join([f"PID {pid}" for pid, _, _ in stuck_codex[:3]])
        r.status = "warn"
        r.message = f"Potential stuck processes detected: {stuck_info}"
        r.details = "Long-running sessions are OK if actively working. Doctor will skip headless test."
        r.fix_hint = "Check processes manually: ps aux | grep codex"
        res_list.append(r)
    else:
        try:
            process = run_subprocess_optimized(
                ["dex", "flash", "--print", "respond with 'pong'"],
                capture_output=True,
                timeout=90,  # Increased timeout
                env={**os.environ, "THGENT_DEBUG": "0", "THGENT_LOG_LEVEL": "ERROR"},
            )
            stdout_text = (
                process.stdout
                if isinstance(process.stdout, str)
                else (process.stdout.decode("utf-8", errors="replace") if process.stdout else "")
            )
            stderr_text = (
                process.stderr
                if isinstance(process.stderr, str)
                else (process.stderr.decode("utf-8", errors="replace") if process.stderr else "")
            )
            if process.returncode == 0 and stdout_text and "pong" in stdout_text.lower():
                r.status = "ok"
                r.message = "Codex headless run successful"
            else:
                r.status = "fail"  # Required feature
                r.message = f"Codex headless run failed (code {process.returncode})"
                output = (stderr_text or stdout_text or "").strip()
                if output:
                    r.details = output.splitlines()[-1] if "\n" in output else output[:200]
                r.fix_hint = "Check OAuth credentials: thegent cliproxy login codex"
        except subprocess.TimeoutExpired:
            r.status = "warn"  # Changed from fail to warn - timeout might be due to active sessions
            r.message = "Codex headless run timed out (90s)"
            r.details = "This may be normal if other Codex sessions are actively running"
            r.fix_hint = "Check for active sessions: ps aux | grep codex"
        except Exception as e:
            r.status = "fail"  # Required feature
            r.message = f"Codex headless run error: {str(e)[:100]}"
            r.fix_hint = "Check OAuth credentials: thegent cliproxy login codex"
        res_list.append(r)

    # Droid Headless (requires droid/roid shims)
    r = CheckResult("Droid Headless", "Headless Runs")
    droid_shim = shutil.which("droid")
    roid_shim = shutil.which("roid")

    if not droid_shim and not roid_shim:
        r.status = "warn"  # Warning, not failure - droids are optional
        r.message = "droid/roid shims not found in PATH"
        r.fix_hint = "Run: thegent install-shims --all"
        res_list.append(r)
    elif stuck_droid:
        # Warn about stuck processes but don't fail - long-running sessions are OK
        stuck_info = ", ".join([f"PID {pid}" for pid, _, _ in stuck_droid[:3]])
        r.status = "warn"
        r.message = f"Potential stuck processes detected: {stuck_info}"
        r.details = "Long-running sessions are OK if actively working. Doctor will skip headless test."
        r.fix_hint = "Check processes manually: ps aux | grep droid"
        res_list.append(r)
    else:
        try:
            # Try a simple droid exec test
            droid_cmd = droid_shim or roid_shim
            process = run_subprocess_optimized(
                [droid_cmd, "exec", "--help"],
                capture_output=True,
                timeout=10,
                env={**os.environ, "THGENT_DEBUG": "0", "THGENT_LOG_LEVEL": "ERROR"},
            )
            stdout_text = (
                process.stdout
                if isinstance(process.stdout, str)
                else (process.stdout.decode("utf-8", errors="replace") if process.stdout else "")
            )
            if process.returncode == 0 or (
                stdout_text and ("usage" in stdout_text.lower() or "help" in stdout_text.lower())
            ):
                r.status = "ok"
                r.message = f"Droid headless run successful ({droid_cmd})"
            else:
                r.status = "warn"
                r.message = f"Droid command available but test failed (code {process.returncode})"
                r.details = "Droid may need configuration or droids directory setup"
                r.fix_hint = "Check droid setup: thegent list-droids"
        except subprocess.TimeoutExpired:
            r.status = "warn"
            r.message = "Droid headless run timed out (10s)"
            r.details = "This may be normal if droid is initializing"
            r.fix_hint = "Check droid setup: thegent list-droids"
        except FileNotFoundError:
            r.status = "warn"
            r.message = "Droid command not found"
            r.fix_hint = "Run: thegent install-shims --all"
        except Exception as e:
            r.status = "warn"
            r.message = f"Droid headless run error: {str(e)[:100]}"
            r.fix_hint = "Check droid setup: thegent list-droids"
        res_list.append(r)

    return res_list


def _extract_process_info(proc: "psutil.Process") -> "ProcessInfo | None":
    """Extract ProcessInfo from psutil.Process. WP-P2: Fix PERF203."""
    import psutil

    from thegent.infra.fast_process_monitor import ProcessInfo

    try:
        info = proc.info
        return ProcessInfo(
            pid=info["pid"],
            name=info.get("name", "unknown"),
            cmdline=" ".join(info.get("cmdline", []) or []),
            create_time=info.get("create_time", 0),
            status=info.get("status", "unknown"),
        )
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


def _check_process_health_v2(
    info: "ProcessInfo",
    current_time: float,
    high_memory_processes: list,
    high_fd_processes: list,
    orphaned_processes: list,
) -> int:
    """Check health of a single process. Returns 1 if zombie, else 0. WP-P2: Fix PERF203."""
    import psutil

    try:
        # Get detailed info using psutil
        proc = psutil.Process(info.pid)

        # Check for zombies
        if proc.status() == psutil.STATUS_ZOMBIE:
            return 1

        # Check memory usage
        memory_mb = proc.memory_info().rss / 1024 / 1024
        if memory_mb > 500:  # > 500MB
            high_memory_processes.append((info.pid, info.name, memory_mb, info.cmdline[:80]))

        # Check file descriptors
        try:
            num_fds = proc.num_fds() if hasattr(proc, "num_fds") else len(proc.open_files()) + len(proc.connections())
            if num_fds > 100:  # > 100 FDs
                high_fd_processes.append((info.pid, info.name, num_fds, info.cmdline[:80]))
        except (psutil.AccessDenied, AttributeError):
            pass

        # Check for orphaned processes (parent is init/systemd)
        try:
            parent = proc.parent()
            if parent and parent.pid == 1:
                runtime = current_time - info.create_time
                if runtime > 3600:  # > 1 hour
                    # Check if it's a thegent-related process
                    cmdline_lower = info.cmdline.lower()
                    if any(keyword in cmdline_lower for keyword in ["thegent", "claude", "codex", "droid", "cliproxy"]):
                        orphaned_processes.append((info.pid, info.name, runtime / 3600, info.cmdline[:80]))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    return 0


def _check_process_leaks() -> list[CheckResult]:
    """Check for potential process leaks and optimization opportunities."""
    res_list = []

    # Process Leak Analysis
    r = CheckResult("Process Leak Analysis", "Process Analysis & Leak Detection")
    try:
        import psutil

        issues = []
        suspicious_processes = []
        zombie_count = 0
        high_memory_processes = []
        high_fd_processes = []
        orphaned_processes = []

        # Analyze processes
        try:
            from thegent.infra.fast_process_monitor import get_fast_monitor

            monitor = get_fast_monitor()
            process_infos = list(monitor.iter_processes(use_cache=False))
        except Exception:
            # Fallback to psutil
            process_infos = []
            for proc in psutil.process_iter(
                ["pid", "name", "cmdline", "status", "memory_info", "num_fds", "create_time"]
            ):
                info = _extract_process_info(proc)
                if info:
                    process_infos.append(info)

        current_time = time.time()

        for info in process_infos:
            zombie_count += _check_process_health_v2(
                info, current_time, high_memory_processes, high_fd_processes, orphaned_processes
            )

        # Build suspicion report
        suspicion_level = "low"
        suggestions = []

        if zombie_count > 0:
            issues.append(f"{zombie_count} zombie process(es)")
            suspicion_level = "medium" if suspicion_level == "low" else suspicion_level
            suggestions.append("Clean up zombies: ps aux | grep '<defunct>' | awk '{print $2}' | xargs kill -9")

        if len(high_memory_processes) > 5:
            top_memory = sorted(high_memory_processes, key=lambda x: x[2], reverse=True)[:5]
            issues.append(f"{len(high_memory_processes)} high-memory processes (>500MB)")
            suspicion_level = "high" if suspicion_level in ["low", "medium"] else suspicion_level
            suggestions.append(f"Top memory hogs: {', '.join([f'PID {p[0]} ({p[2]:.0f}MB)' for p in top_memory])}")
            suggestions.append("Investigate: ps aux --sort=-%mem | head -10")

        if len(high_fd_processes) > 3:
            top_fds = sorted(high_fd_processes, key=lambda x: x[2], reverse=True)[:3]
            issues.append(f"{len(high_fd_processes)} high-FD processes (>100 FDs)")
            suspicion_level = "high" if suspicion_level in ["low", "medium"] else suspicion_level
            suggestions.append(f"Top FD users: {', '.join([f'PID {p[0]} ({p[2]} FDs)' for p in top_fds])}")
            suggestions.append("Check FD leaks: lsof -p <PID> | wc -l")

        if len(orphaned_processes) > 0:
            issues.append(f"{len(orphaned_processes)} potentially orphaned thegent processes")
            suspicion_level = "medium" if suspicion_level == "low" else suspicion_level
            top_orphaned = sorted(orphaned_processes, key=lambda x: x[2], reverse=True)[:3]
            suggestions.append(f"Orphaned processes: {', '.join([f'PID {p[0]} ({p[2]:.1f}h)' for p in top_orphaned])}")
            suggestions.append("Review: ps aux | grep -E '(thegent|claude|codex|droid)' | grep -v grep")

        # Determine status and message
        if not issues:
            r.status = "ok"
            r.message = "No process leaks detected"
            r.details = "Suspicion Level: LOW\nAll processes appear healthy"
        else:
            if suspicion_level == "critical":
                r.status = "fail"
                status_icon = "🔴"
            elif suspicion_level == "high":
                r.status = "warn"
                status_icon = "🟡"
            elif suspicion_level == "medium":
                r.status = "warn"
                status_icon = "🟠"
            else:
                r.status = "ok"
                status_icon = "✓"

            r.message = f"{status_icon} {len(issues)} potential issue(s) detected"
            r.details = f"Suspicion Level: {suspicion_level.upper()}\n"
            r.details += f"Issues: {', '.join(issues)}\n\n"
            r.details += "Optimization Suggestions:\n"
            r.details += "\n".join(f"  • {s}" for s in suggestions[:8])  # Limit to 8 suggestions
            r.fix_hint = "; ".join(suggestions[:3])  # Top 3 suggestions

    except ImportError:
        r.status = "warn"
        r.message = "psutil not available for process analysis"
        r.fix_hint = "Install psutil: pip install psutil"
    except Exception as e:
        r.status = "warn"
        r.message = f"Could not analyze processes: {e}"
        r.details = f"Error details: {str(e)[:200]}"

    res_list.append(r)

    return res_list


def _check_runtime_infrastructure() -> list[CheckResult]:
    """Check runtime infrastructure (resource limits and monitoring)."""
    res_list = []

    # Runtime Infrastructure Initialization
    r = CheckResult("Runtime Infrastructure", "Runtime Infrastructure")
    try:
        from thegent.infra.runtime_init import is_initialized

        if is_initialized():
            r.status = "ok"
            r.message = "Runtime infrastructure initialized (resource limits and monitoring active)"
        else:
            r.status = "warn"
            r.message = "Runtime infrastructure not initialized"
            r.fix_hint = "Runtime infrastructure should initialize automatically on startup"
    except Exception as e:
        r.status = "warn"
        r.message = f"Could not check runtime infrastructure: {e}"
    res_list.append(r)

    # Resource Monitoring
    r = CheckResult("Resource Monitoring", "Runtime Infrastructure")
    try:
        from thegent.infra.runtime_init import get_resource_stats

        stats = get_resource_stats()
        if stats:
            suspicion_level, suggestions = stats.get_suspicion_level()

            # Determine status based on suspicion level
            if suspicion_level == "critical":
                r.status = "fail"
                status_icon = "🔴"
            elif suspicion_level == "high":
                r.status = "warn"
                status_icon = "🟡"
            elif suspicion_level == "medium":
                r.status = "warn"
                status_icon = "🟠"
            else:
                r.status = "ok"
                status_icon = "✓"

            r.message = (
                f"{status_icon} FDs: {stats.fd_count}/{stats.fd_limit} ({stats.fd_usage_percent:.1f}%), "
                f"Memory: {stats.memory_mb:.1f}MB, "
                f"CPU: {stats.cpu_percent:.1f}%, "
                f"Processes: {stats.process_count}"
            )

            # Add detailed report with suspicion level and suggestions
            if suspicion_level != "low":
                r.details = f"Suspicion Level: {suspicion_level.upper()}\n"
                r.details += f"Optimization Suggestions: {suggestions}"
                r.fix_hint = suggestions
        else:
            r.status = "warn"
            r.message = "Resource monitoring not active"
    except Exception as e:
        r.status = "warn"
        r.message = f"Could not get resource stats: {e}"
    res_list.append(r)

    # Process Registry
    r = CheckResult("Process Registry", "Runtime Infrastructure")
    try:
        import psutil

        from thegent.infra.process_registry import get_registry

        registry = get_registry()
        active_processes = registry.list_alive()  # Fixed: use list_alive() instead of list_all()
        count = len(active_processes)

        # Analyze tracked processes for potential issues
        dead_pids = []
        long_running = []
        high_resource = []

        for handle in active_processes:
            try:
                proc = psutil.Process(handle.pid)
                status = proc.status()

                # Check if process is actually dead
                if status == psutil.STATUS_ZOMBIE:
                    dead_pids.append(handle.pid)
                    continue

                # Check runtime
                try:
                    create_time = proc.create_time()
                    runtime = time.time() - create_time
                    if runtime > 86400:  # > 24 hours
                        memory_mb = proc.memory_info().rss / 1024 / 1024
                        long_running.append((handle.pid, runtime / 3600, memory_mb))
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass

                # Check resource usage
                try:
                    memory_mb = proc.memory_info().rss / 1024 / 1024
                    cpu_percent = proc.cpu_percent(interval=0.1)
                    if memory_mb > 1000 or cpu_percent > 50:
                        high_resource.append((handle.pid, memory_mb, cpu_percent))
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                dead_pids.append(handle.pid)

        # Build report
        issues = []
        suspicion_level = "low"
        suggestions = []

        if dead_pids:
            issues.append(f"{len(dead_pids)} dead/zombie process(es) in registry")
            suspicion_level = "medium"
            suggestions.append(f"Clean up dead processes: {', '.join([str(p) for p in dead_pids[:5]])}")

        if len(long_running) > 10:
            top_long = sorted(long_running, key=lambda x: x[1], reverse=True)[:5]
            issues.append(f"{len(long_running)} very long-running processes (>24h)")
            suspicion_level = "medium" if suspicion_level == "low" else suspicion_level
            suggestions.append(
                f"Long-running: {', '.join([f'PID {p[0]} ({p[1]:.1f}h, {p[2]:.0f}MB)' for p in top_long])}"
            )

        if len(high_resource) > 5:
            top_resource = sorted(high_resource, key=lambda x: x[1], reverse=True)[:5]
            issues.append(f"{len(high_resource)} high-resource processes")
            suspicion_level = "high" if suspicion_level in ["low", "medium"] else suspicion_level
            suggestions.append(
                f"High resource: {', '.join([f'PID {p[0]} ({p[1]:.0f}MB, {p[2]:.1f}% CPU)' for p in top_resource])}"
            )

        if count == 0:
            r.status = "ok"
            r.message = "No active tracked processes"
        elif count < 10:
            r.status = "ok"
            r.message = f"{count} active tracked process(es)"
            if issues:
                r.details = f"Suspicion Level: {suspicion_level.upper()}\n" + "\n".join(issues)
                r.fix_hint = "; ".join(suggestions[:2])
        elif count < 50:
            r.status = "ok"
            r.message = f"{count} active tracked processes (normal for active sessions)"
            if issues:
                r.details = f"Suspicion Level: {suspicion_level.upper()}\n" + "\n".join(issues)
                r.fix_hint = "; ".join(suggestions[:2])
        elif count < 100:
            r.status = "warn"
            r.message = f"{count} active tracked processes"
            if issues:
                suspicion_level = "high" if suspicion_level == "medium" else suspicion_level
            r.details = f"Suspicion Level: {suspicion_level.upper()}\n"
            if issues:
                r.details += "Issues: " + ", ".join(issues) + "\n"
            r.details += "Consider checking for processes that should have been cleaned up"
            r.fix_hint = (
                "; ".join(suggestions[:3])
                if suggestions
                else "Review tracked processes: Check if long-running sessions are expected"
            )
        else:
            r.status = "warn"
            r.message = f"{count} active tracked processes"
            suspicion_level = "high" if not issues else suspicion_level
            r.details = f"Suspicion Level: {suspicion_level.upper()}\n"
            if issues:
                r.details += "Issues: " + ", ".join(issues) + "\n"
            r.details += "May indicate process leak or many concurrent sessions"
            r.fix_hint = (
                "; ".join(suggestions[:3])
                if suggestions
                else "Investigate: Check for stuck processes or cleanup issues"
            )
    except Exception as e:
        r.status = "warn"
        r.message = f"Could not check process registry: {e}"
        r.details = f"Error details: {str(e)[:200]}"
    res_list.append(r)

    # psutil Availability
    r = CheckResult("psutil Library", "Runtime Infrastructure")
    try:
        import psutil

        version = psutil.__version__
        r.status = "ok"
        r.message = f"psutil {version} available"
    except ImportError:
        r.status = "fail"
        r.message = "psutil not installed"
        r.fix_hint = "Install psutil: pip install psutil>=5.9.0 or uv sync"
    except Exception as e:
        r.status = "warn"
        r.message = f"Could not check psutil: {e}"
    res_list.append(r)

    return res_list


def _check_mcp_tools() -> list[CheckResult]:
    """Check MCP tools availability and functionality."""
    res_list = []
    settings = ThegentSettings()

    # MCP Tools Availability
    r = CheckResult("MCP Tools", "MCP Tools & Sessions")
    try:
        # Check if MCP server is reachable (already checked in connectivity, but verify tools work)
        mcp_url = f"http://{settings.mcp_host}:{settings.mcp_port}/mcp"
        try:
            resp = httpx.get(f"http://{settings.mcp_host}:{settings.mcp_port}/health", timeout=2.0)
            if resp.status_code == 200:
                r.status = "ok"
                r.message = "MCP tools available"
            else:
                r.status = "warn"
                r.message = f"MCP server returned {resp.status_code}"
                r.fix_hint = "Run: thegent mcp up"
        except Exception:
            r.status = "warn"
            r.message = "MCP server not reachable (tools unavailable)"
            r.fix_hint = "Run: thegent mcp up"
    except Exception as e:
        r.status = "warn"
        r.message = f"Could not check MCP tools: {e}"
    res_list.append(r)

    return res_list


def _check_sessions() -> list[CheckResult]:
    """Check session directory and session management."""
    res_list = []
    settings = ThegentSettings()

    # Session Directory
    r = CheckResult("Session Directory", "MCP Tools & Sessions")
    session_dir = settings.session_dir.expanduser().resolve()
    try:
        if session_dir.exists():
            if os.access(session_dir, os.W_OK):
                r.status = "ok"
                r.message = f"Session directory writable: {session_dir}"

                # Check session count
                try:
                    session_count = len([d for d in session_dir.iterdir() if d.is_dir()])
                    if session_count > 0:
                        r.message += f" ({session_count} session(s))"
                except Exception:
                    pass
            else:
                r.status = "fail"
                r.message = f"Session directory not writable: {session_dir}"
                r.fix_hint = f"Fix permissions: chmod 755 {session_dir}"
        else:
            try:
                session_dir.mkdir(parents=True, exist_ok=True)
                r.status = "ok"
                r.message = f"Session directory created: {session_dir}"
            except Exception as e:
                r.status = "fail"
                r.message = f"Cannot create session directory: {e}"
                r.fix_hint = f"Create manually: mkdir -p {session_dir}"
    except Exception as e:
        r.status = "warn"
        r.message = f"Could not check session directory: {e}"
    res_list.append(r)

    return res_list


def _check_project_hints() -> list[CheckResult]:
    """Project-specific hints (git repo, hooks)."""
    res_list = []
    project_root = _project_root_cache or Path.cwd()

    # Git repo: suggest hooks if .git/hooks not configured
    git_dir = project_root / ".git"
    if git_dir.exists() and git_dir.is_dir():
        hooks_dir = git_dir / "hooks"
        pre_commit = hooks_dir / "pre-commit"
        if not pre_commit.exists() or not pre_commit.is_file():
            r = CheckResult("Git Hooks", "Project")
            r.status = "warn"
            r.message = "Git repo detected but no pre-commit hook"
            r.fix_hint = "Run: thegent setup --hooks"
            res_list.append(r)

    return res_list


def _check_performance() -> list[CheckResult]:
    """Check for performance optimizations."""
    res_list = []
    import sys

    # 1. Shell Strategy
    r = CheckResult("Shell Strategy", "Performance")
    settings = ThegentSettings()
    agent_shell = settings.agent_shell

    if sys.platform == "win32":
        if agent_shell == "cmd":
            r.status = "ok"
            r.message = "Using high-performance 'cmd' for Windows execution"
        else:
            r.status = "warn"
            r.message = f"Currently using '{agent_shell or 'default'}' shell; 'cmd' is faster for Windows"
            r.fix_hint = "Run: thegent config set agent_shell cmd"
    elif agent_shell == "dash":
        r.status = "ok"
        r.message = "Using high-performance 'dash' for Unix execution"
    elif shutil.which("dash"):
        r.status = "warn"
        r.message = f"Currently using '{agent_shell or 'default'}' shell; 'dash' is faster for Unix"
        r.fix_hint = "Run: thegent config set agent_shell dash"
    else:
        r.status = "info"
        r.message = "Dash not found; bash is used as fallback"
        r.fix_hint = "Install dash for 2x faster hook startup"

    res_list.append(r)
    return res_list


def _apply_fixes(results: list[CheckResult]) -> None:
    """Attempt to automatically fix issues based on fix_hint strings."""
    fixes_applied = 0
    fixes_failed = 0

    console.print("\n[bold cyan]Attempting automatic fixes...[/bold cyan]\n")

    for r in results:
        if r.status in ("fail", "warn") and r.fix_hint:
            # Parse fix hints and attempt fixes
            hint = r.fix_hint.strip()

            # Handle mkdir -p (e.g. "Create manually: mkdir -p /path")
            if "mkdir" in hint and "-p" in hint:
                m = re.search(r"mkdir\s+-p\s+(\S+)", hint)
                if m:
                    path = Path(m.group(1)).expanduser()
                    try:
                        path.mkdir(parents=True, exist_ok=True)
                        fixes_applied += 1
                        console.print(f"[green]  ✓ Fixed: {r.name} (created {path})[/green]")
                        r.status = "ok"
                        r.message = f"Created: {path}"
                    except Exception as e:
                        fixes_failed += 1
                        console.print(f"[red]  ✗ Failed: {r.name} - {e}[/red]")
                    continue

            # Skip hints that require manual intervention
            if any(
                skip in hint.lower()
                for skip in ["install", "download", "check", "ensure", "create manually", "move", "add"]
            ):
                if "run:" in hint.lower() or "thegent" in hint.lower():
                    # These are actionable commands
                    pass
                else:
                    continue

            # Extract command from fix hints
            if "run:" in hint.lower() or (
                ":" in hint and any(cmd in hint.lower() for cmd in ["thegent", "mkdir", "chmod"])
            ):
                # Extract command after "Run:" or "run:" or direct commands
                if "run:" in hint.lower():
                    parts = hint.split(":", 1)
                    cmd_str = parts[1].strip() if len(parts) > 1 else hint
                # Handle direct commands like "Fix permissions: chmod 755 ..."
                elif ":" in hint:
                    cmd_str = hint.split(":", 1)[1].strip()
                else:
                    cmd_str = hint

                # Handle multiple commands separated by semicolons
                commands = [c.strip() for c in cmd_str.split(";")]

                for cmd in commands:
                    if not cmd:
                        continue

                    # Parse command into parts
                    cmd_parts = cmd.split()
                    if not cmd_parts:
                        continue

                    # Skip dangerous commands, except for specific safe removals
                    dangerous = ["rm", "delete", "remove", "uninstall", "kill"]
                    is_safe_removal = False
                    if cmd_parts[0].lower() == "rm" and len(cmd_parts) == 2:
                        target_file = Path(cmd_parts[1]).expanduser()
                        safe_targets = [Path.home() / ".local" / "bin" / "ps"]
                        if any(target_file == safe for safe in safe_targets):
                            is_safe_removal = True

                    if any(d in cmd_parts[0].lower() for d in dangerous) and not is_safe_removal:
                        console.print(f"[yellow]⚠ Skipping potentially dangerous fix: {cmd}[/yellow]")
                        continue

                    # Execute safe commands
                    try:
                        console.print(f"[dim]  Fixing {r.name}: {cmd}[/dim]")

                        # Handle thegent commands specially
                        if cmd_parts[0] == "thegent":
                            result = run_subprocess_optimized(
                                cmd_parts,
                                capture_output=True,
                                timeout=30,
                                cwd=_project_root_cache or None,
                            )
                            if result.returncode == 0:
                                fixes_applied += 1
                                console.print(f"[green]  ✓ Fixed: {r.name}[/green]")
                            else:
                                fixes_failed += 1
                                stderr_text = (
                                    result.stderr
                                    if isinstance(result.stderr, str)
                                    else (result.stderr.decode("utf-8", errors="replace") if result.stderr else "")
                                )
                                console.print(f"[red]  ✗ Failed: {r.name} - {stderr_text[:100]}[/red]")
                        else:
                            # For other commands, check if they're safe to run
                            safe_commands = ["mkdir", "chmod", "touch"]
                            if cmd_parts[0] in safe_commands:
                                result = run_subprocess_optimized(
                                    cmd_parts,
                                    capture_output=True,
                                    timeout=10,
                                )
                                if result.returncode == 0:
                                    fixes_applied += 1
                                    console.print(f"[green]  ✓ Fixed: {r.name}[/green]")
                                else:
                                    fixes_failed += 1
                                    console.print(f"[red]  ✗ Failed: {r.name}[/red]")
                            else:
                                # For unknown commands, just log
                                console.print(f"[yellow]  ⚠ Manual fix required: {cmd}[/yellow]")
                    except subprocess.TimeoutExpired:
                        fixes_failed += 1
                        console.print(f"[red]  ✗ Timeout fixing: {r.name}[/red]")
                    except Exception as e:
                        fixes_failed += 1
                        console.print(f"[red]  ✗ Error fixing {r.name}: {e}[/red]")

    if fixes_applied > 0 or fixes_failed > 0:
        console.print(f"\n[bold]Fix Summary:[/bold] {fixes_applied} applied, {fixes_failed} failed\n")


def _display_results(results: list[CheckResult]) -> bool:
    table = Table(title="Doctor Results", box=None, show_header=True)
    table.add_column("Category", style="dim")
    table.add_column("Check", style="bold")
    table.add_column("Status")
    table.add_column("Message")

    # All failures count against success - no features are optional
    all_ok = True
    for r in results:
        status_str = "[green]ok[/green]"
        if r.status == "warn":
            status_str = "[yellow]warn[/yellow]"
        elif r.status == "fail":
            status_str = "[red]fail[/red]"
            all_ok = False

        table.add_row(r.category, r.name, status_str, r.message)
        if r.fix_hint:
            table.add_row("", "", "", f"[dim]Hint: {r.fix_hint}[/dim]")
        if r.details:
            table.add_row("", "", "", f"[dim]{r.details}[/dim]")

    console.print(table)

    # Provider Matrix Summary (ROB-016)
    providers = [r for r in results if r.category == "Providers"]
    if providers:
        matrix = Table(title="Provider Success Matrix", box=None, show_header=True)
        matrix.add_column("Provider", style="bold")
        matrix.add_column("Validated", justify="center")
        matrix.add_column("Models", justify="right")

        for p in providers:
            name = p.name.replace("Provider: ", "")
            status = "✅" if p.status == "ok" else "❌" if p.status == "fail" else "⚠️"
            if "(" in p.message and ")" in p.message:
                models_col = p.message.split("(")[-1].replace(")", "").replace(" models", "").strip()
            else:
                models_col = p.message if p.status != "ok" else "—"
            matrix.add_row(name, status, models_col)

        console.print(Panel(matrix, title="Governance Dashboard"))

    return all_ok
