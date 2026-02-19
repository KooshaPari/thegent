"""Codex-backed interactive agent CLI (dex). Model-only routing (no provider filter)."""

import os
import shutil
import subprocess
from collections import Counter
from collections.abc import Iterator
from pathlib import Path

import typer

from thegent.agents.routing_contracts import GEMINI_FLASH_MODEL, GEMINI_FLASH_PROVIDER
from thegent.infra.power import wrap_with_caffeinate


class LazyConsole:
    def __getattr__(self, name):
        from rich.console import Console

        global console
        console = Console()
        return getattr(console, name)


console = LazyConsole()
app = typer.Typer(help="Codex-backed interactive agent CLI. Model-only routing (no provider filter).")

# Global flag for force YOLO mode (-f)
_force_yolo: bool = False


@app.callback(invoke_without_command=True)
def _dex_global_callback(
    force: bool = typer.Option(
        False,
        "-f",
        "--force-yolo",
        help="Force YOLO mode: skip permissions, disable sandbox and approvals",
    ),
) -> None:
    """Global callback for dex - handles -f flag for force YOLO mode."""
    global _force_yolo
    _force_yolo = force
    if force:
        # Update settings instance
        settings = _get_settings()
        settings.dex_force_yolo = True


def _get_settings():
    from thegent.config import ThegentSettings

    return ThegentSettings()


def _is_triggered_by_agent_process() -> bool:
    from thegent.discovery import _is_triggered_by_agent_process as impl

    return impl()


def _should_bypass_approvals() -> bool:
    """Check if approvals/sandbox should be bypassed (agent-triggered runs never bypass unless -f flag is used)."""
    return _force_yolo or not _is_triggered_by_agent_process()


# Model alias -> canonical model ID. Routing is model-first, not provider.
# Lazy imports used in commands to speed up CLI startup.
_MODEL_ALIAS: dict[str, str] = {
    "composer": "composer-1.5",
    "composer1.5": "composer-1.5",
    "comp": "composer-1.5",
    "max": "minimax-m2.5",
    "m2.5": "minimax-m2.5",
    "glm": "glm-5",
    "glm5": "glm-5",
    "haiku": "claude-haiku-4.5",
    "opus": "claude-opus-4.6",
    "sonnet": "claude-sonnet-4.5",
    "sonnet1m": "claude-sonnet-4.5-1m",
    "step": "step-3.5-flash",
    "step3.5": "step-3.5-flash",
    "flash": GEMINI_FLASH_MODEL,
    "mini": "gpt-5-mini",
    "gpt5mini": "gpt-5-mini",
}

# M2.5 providers (max): model-appropriate only (nim does not serve minimax-m2.5)
_M2_OFFER_SET: tuple[str, ...] = ("minimax", "kilo")
_M2_COST: dict[str, float] = {"minimax": 0.36, "kilo": 0.28}
_M2_COUNTER: Counter[str] = Counter()

# GLM5 providers: model-appropriate only (nim does not serve glm-5)
_GLM_OFFER_SET: tuple[str, ...] = ("glm", "minimax", "kilo")
_GLM_COST: dict[str, float] = {"glm": 0.80, "minimax": 0.36, "kilo": 0.28}
_GLM_COUNTER: Counter[str] = Counter()

# Claude providers (haiku/opus/sonnet): balanced across CC plan, antigravity, etc.
_CLAUDE_OFFER_SET: tuple[str, ...] = ("claude", "antigravity")
_CLAUDE_COUNTER: Counter[str] = Counter()

# Composer 1.5: Cursor (cursor-api / wisdgod)
_CURSOR_OFFER_SET: tuple[str, ...] = ("cursor",)

# Codex uses --dangerously-bypass-approvals-and-sandbox (or --yolo) per Codex CLI reference
_DEX_BYPASS_FLAG = "--dangerously-bypass-approvals-and-sandbox"


def _resolve_provider_for_model(model_alias: str) -> str:
    """Resolve provider for model-first routing. Round-robin across available providers."""
    canonical = _MODEL_ALIAS.get(model_alias.lower(), model_alias)

    if canonical == "composer-1.5":
        return _CURSOR_OFFER_SET[0]
    if canonical == "minimax-m2.5":
        idx = _M2_COUNTER["max"]
        providers = _M2_OFFER_SET
        selected = providers[idx % len(providers)]
        _M2_COUNTER["max"] = (idx + 1) % len(providers)
        return selected
    if canonical == "glm-5":
        idx = _GLM_COUNTER["glm"]
        providers = _GLM_OFFER_SET
        selected = providers[idx % len(providers)]
        _GLM_COUNTER["glm"] = (idx + 1) % len(providers)
        return selected
    if canonical in ("claude-haiku-4.5", "claude-opus-4.6", "claude-sonnet-4.5", "claude-sonnet-4.5-1m"):
        idx = _CLAUDE_COUNTER["claude"]
        providers = _CLAUDE_OFFER_SET
        selected = providers[idx % len(providers)]
        _CLAUDE_COUNTER["claude"] = (idx + 1) % len(providers)
        return selected
    if canonical == "step-3.5-flash":
        return "nim"
    if canonical == "gpt-5-mini":
        return "copilot"
    if canonical == GEMINI_FLASH_MODEL:
        return GEMINI_FLASH_PROVIDER

    # Fallback: nim for other proxy models
    return "nim"


def _iter_install_targets() -> Iterator[tuple[str, str, str]]:
    """Return shim targets: model-only, no provider filter."""
    yield ("dex", "thegent dex", "dex")
    yield ("dexcomposer", "thegent dex composer", "dexcomposer")
    yield ("dexmax", "thegent dex max", "dexmax")
    yield ("dexglm", "thegent dex glm", "dexglm")
    yield ("dexhaiku", "thegent dex haiku", "dexhaiku")
    yield ("dexopus", "thegent dex opus", "dexopus")
    yield ("dexsonnet", "thegent dex sonnet", "dexsonnet")
    yield ("dexstep", "thegent dex step", "dexstep")
    yield ("dexflash", "thegent dex flash", "dexflash")
    yield ("dexmini", "thegent dex mini", "dexmini")
    yield ("dexfree", "thegent dex free", "dexfree")


def _write_wrapper(path: Path, command: str, force: bool = False) -> bool:
    """Write/update a shim wrapper. Returns True if a write occurred."""
    if path.exists() and not force:
        return False

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'#!/usr/bin/env sh\nset -e\nexport THGENT_HARNESS="codex"\nexec {command} "$@"\n')
    path.chmod(0o755)
    return True


def _get_codex_env(provider: str, model: str) -> dict[str, str]:
    """Get environment variables for Codex CLI pointing to thegent proxy."""
    settings = _get_settings()

    # Check if provider (e.g. 'cursor') is actually configured
    from thegent.agents.cliproxy_manager import _ensure_config, _has_provider_credentials, ensure_proxy_running

    _ensure_config(settings)
    try:
        ensure_proxy_running(settings)
    except (RuntimeError, FileNotFoundError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # If using 'cursor' but no credentials, fallback to 'minimax' or 'glm'
    import yaml

    config_path = settings.cliproxy_config_path.expanduser().resolve()
    if config_path.exists():
        try:
            config = yaml.safe_load(config_path.read_text())
            if isinstance(config, dict) and not _has_provider_credentials(config, provider):
                # Fallback for dex: if cursor not configured, use minimax or glm
                # Composer 1.5 is a generic alias for MiniMax-M2.5/GLM-5 in our proxy
                if provider == "cursor":
                    fallback = "minimax" if _has_provider_credentials(config, "minimax") else "glm"
                    if _has_provider_credentials(config, fallback):
                        console.print(
                            f"[yellow]Warning: Cursor not configured. Falling back to {fallback} for composer.[/yellow]"
                        )
                        provider = fallback
                elif provider == "zen":
                    console.print(
                        "[red]Zen not configured for gemini-3-flash.[/red] "
                        "Set THGENT_ZEN_API_KEY or run: thegent cliproxy login zen"
                    )
                    raise typer.Exit(1)
        except Exception:
            pass

    env = os.environ.copy()
    # WP-Y15: Enable Responses API adapter for Codex compatibility
    env["THGENT_CLIPROXY_ADAPTER"] = "1"
    if settings.cliproxy_backend_url:
        env["THGENT_CLIPROXY_BACKEND_URL"] = settings.cliproxy_backend_url
    base = f"http://{settings.mcp_host}:{settings.cliproxy_port}/v1"
    env["OPENAI_BASE_URL"] = base
    env["OPENAI_API_KEY"] = provider
    env["API_TIMEOUT_MS"] = "300000"
    # Prepend ~/.local/bin so codex's internal git invocations use thegent git shim
    # (avoids "git: '/opt/homebrew/bin/codex' is not a git command")
    local_bin = str(Path.home() / ".local" / "bin")
    path = os.environ.get("PATH", "")
    first_in_path = path.split(os.pathsep)[0] if path else ""
    env["PATH"] = f"{local_bin}{os.pathsep}{path}" if first_in_path != local_bin else path
    return env


def _dex_passthrough_args(
    *,
    cd: Path | None = None,
    print_mode: bool = False,
    debug: bool = False,
    add_dir: list[str] | None = None,
    sandbox: str | None = None,
    full_auto: bool = False,
    search: bool = False,
    no_alt_screen: bool = False,
) -> list[str]:
    """Build extra args for codex from passthrough options."""
    args: list[str] = []
    if cd:
        args.extend(["-C", str(cd.resolve())])
    if debug:
        args.append("--debug")
    if add_dir:
        for d in add_dir:
            args.extend(["--add-dir", d])
    if sandbox:
        args.extend(["--sandbox", sandbox])
    if full_auto:
        args.append("--full-auto")
    if search:
        args.append("--search")
    if no_alt_screen:
        args.append("--no-alt-screen")
    return args


def _run_codex_exec(
    model_alias: str,
    prompt: str,
    *,
    cd: Path | None = None,
    add_dir: list[str] | None = None,
    sandbox: str | None = None,
    full_auto: bool = False,
    dangerously_bypass: bool = True,
) -> None:
    """Run Codex non-interactively (headless) via exec subcommand."""
    canonical = _MODEL_ALIAS.get(model_alias.lower(), model_alias)
    provider = _resolve_provider_for_model(model_alias)
    env = _get_codex_env(provider, canonical)

    codex_path = shutil.which("codex")
    if not codex_path:
        local = Path.home() / ".local" / "bin" / "codex"
        codex_path = str(local) if local.exists() else None
    if not codex_path:
        console.print("[red]Error: 'codex' CLI not found in PATH.[/red]")
        console.print("[dim]Install it via: npm i -g @openai/codex[/dim]")
        raise typer.Exit(1)

    cmd = [codex_path, "exec", "--skip-git-repo-check"]
    if dangerously_bypass and _should_bypass_approvals():
        cmd.append(_DEX_BYPASS_FLAG)
    cmd.extend(["--model", canonical])
    if cd:
        cmd.extend(["-C", str(cd.resolve())])
    if add_dir:
        for d in add_dir:
            cmd.extend(["--add-dir", d])
    if sandbox:
        cmd.extend(["--sandbox", sandbox])
    if full_auto:
        cmd.append("--full-auto")
    cmd.append(prompt)

    # Wrap with caffeinate to prevent sleep on macOS
    cmd = wrap_with_caffeinate(cmd, "codex")

    console.print(f"[bold green]Codex exec (headless): model={canonical}[/bold green]")
    result = subprocess.run(
        cmd,
        env=env,
        cwd=str(cd.resolve()) if cd else None,
        timeout=300,
    )
    raise typer.Exit(result.returncode)


def _run_codex_interactive(
    model_alias: str,
    extra_args: list[str] | None = None,
    dangerously_bypass: bool = True,
) -> None:
    """Start an interactive Codex session. Model-first routing."""
    canonical = _MODEL_ALIAS.get(model_alias.lower(), model_alias)
    provider = _resolve_provider_for_model(model_alias)

    env = _get_codex_env(provider, canonical)
    codex_path = shutil.which("codex")
    if not codex_path:
        local = Path.home() / ".local" / "bin" / "codex"
        codex_path = str(local) if local.exists() else None
    if not codex_path:
        console.print("[red]Error: 'codex' (Codex) CLI not found in PATH.[/red]")
        console.print("[dim]Install it via: npm i -g @openai/codex[/dim]")
        raise typer.Exit(1)

    console.print(f"[bold green]Starting Codex session: model={canonical} (via {provider})[/bold green]")
    console.print(f"[dim]Proxy URL: {env['OPENAI_BASE_URL']}[/dim]")

    cmd = [codex_path]
    if dangerously_bypass and _should_bypass_approvals():
        cmd.append(_DEX_BYPASS_FLAG)
    cmd.extend(["--model", canonical])
    if extra_args:
        for arg in extra_args:
            if arg not in (_DEX_BYPASS_FLAG, "--yolo") and not arg.startswith("--model"):
                cmd.append(arg)

    # Wrap with caffeinate to prevent sleep on macOS
    cmd = wrap_with_caffeinate(cmd, "codex")

    # WP-Y15: Use os.execvpe for native interactive experience (better signal handling)
    os.execvpe(cmd[0], cmd, env)


def _run_model_cmd(
    model_alias: str,
    prompt: str,
    cd: Path | None = None,
    mode: str = "write",
    timeout: int = 90,
) -> None:
    """Run model-first (no provider). Uses thegent run -M <model>."""
    from thegent.cli import run_cmd

    canonical = _MODEL_ALIAS.get(model_alias.lower(), model_alias)
    run_cmd(agent=None, prompt=prompt, cd=cd, mode=mode, timeout=timeout, model=canonical)


def _bg_model_cmd(
    model_alias: str,
    prompt: str,
    cd: Path | None = None,
    mode: str = "write",
    timeout: int = 90,
    owner: str | None = None,
) -> None:
    """Bg model-first (no provider). Uses thegent bg -M <model>."""
    from thegent.cli import bg_cmd

    canonical = _MODEL_ALIAS.get(model_alias.lower(), model_alias)
    bg_cmd(
        agent=None,
        prompt=prompt,
        cd=cd,
        mode=mode,
        timeout=timeout,
        full=False,
        model=canonical,
        owner=owner,
    )


@app.callback(invoke_without_command=True)
def default_dex(ctx: typer.Context) -> None:
    """Default: flash (gemini-3-flash) or model from first argument. Model-only, no provider filter.

    Usage:
        dex              # Uses flash model (default)
        dex flash        # Uses flash model (via subcommand)
        dex max          # Uses max model (via subcommand or positional)
        dex [model]      # Uses specified model (max, glm, haiku, opus, sonnet, ultra, flash, mini, composer, step)
        dex [model] [prompt]  # Uses model with prompt
    """
    if ctx.invoked_subcommand is None:
        # Get arguments from typer context
        # Typer stores unparsed args in ctx.params or we need to get them differently
        import sys

        # Find 'dex' in sys.argv and get remaining args
        cmd_args = []
        try:
            # Look for 'dex' command in argv
            for i, arg in enumerate(sys.argv):
                if "dex" in arg and (arg.endswith("dex") or arg == "dex" or "/dex" in arg):
                    # Get everything after 'dex'
                    if i + 1 < len(sys.argv):
                        cmd_args = sys.argv[i + 1 :]
                    break
        except Exception:
            pass

        # If no args, use default flash model
        if not cmd_args:
            _run_codex_interactive("flash", extra_args=[_DEX_BYPASS_FLAG])
            return

        # Check if first argument is a model alias
        first_arg = cmd_args[0].lower()
        model_alias = "flash"  # Default

        if first_arg in _MODEL_ALIAS:
            # First argument is a recognized model alias
            model_alias = first_arg
            remaining_args = cmd_args[1:]
        else:
            # First argument is not a recognized model, treat entire args as prompt with default model
            remaining_args = cmd_args

        # Run with the model and remaining arguments (prompt, flags, etc.)
        extra_args = [_DEX_BYPASS_FLAG, *remaining_args]
        _run_codex_interactive(model_alias, extra_args=extra_args)


@app.command("composer")
def dex_composer(
    dangerously_bypass: bool = typer.Option(
        True,
        "--dangerously-bypass-approvals-and-sandbox",
        help="Bypass Codex approval prompts (default: True)",
    ),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option(None, "--add-dir", help="Additional directories (repeatable)"),
    sandbox: str | None = typer.Option(
        None, "--sandbox", "-s", help="Sandbox: read-only, workspace-write, danger-full-access"
    ),
    full_auto: bool = typer.Option(False, "--full-auto", help="Convenience: -a on-request, --sandbox workspace-write"),
    search: bool = typer.Option(True, "--search", help="Enable web search"),
    no_alt_screen: bool = typer.Option(False, "--no-alt-screen", help="Disable alternate screen mode"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Start Codex with Composer 1.5 (Cursor). Use 'dex max' for minimax-m2.5."""
    if print_mode:
        if not prompt:
            console.print("[red]Error: --print requires a prompt.[/red]")
            raise typer.Exit(1)
        _run_codex_exec(
            "composer",
            prompt,
            cd=cd,
            add_dir=add_dir or None,
            sandbox=sandbox,
            full_auto=full_auto,
            dangerously_bypass=dangerously_bypass,
        )
        return
    extra: list[str] = _dex_passthrough_args(
        cd=cd,
        debug=debug,
        add_dir=add_dir or None,
        sandbox=sandbox,
        full_auto=full_auto,
        search=search,
        no_alt_screen=no_alt_screen,
    )
    if resume:
        extra.extend(["--resume", resume])
    if prompt:
        extra.append(prompt)
    _run_codex_interactive("composer", extra_args=extra, dangerously_bypass=dangerously_bypass)


@app.command("max")
def dex_max(
    dangerously_bypass: bool = typer.Option(
        True,
        "--dangerously-bypass-approvals-and-sandbox",
        "--yolo",
        help="Bypass approvals and sandbox (default: True)",
    ),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option(None, "--add-dir", help="Additional directories (repeatable)"),
    sandbox: str | None = typer.Option(
        None, "--sandbox", "-s", help="Sandbox: read-only, workspace-write, danger-full-access"
    ),
    full_auto: bool = typer.Option(False, "--full-auto", help="Convenience: -a on-request, --sandbox workspace-write"),
    search: bool = typer.Option(True, "--search", help="Enable web search"),
    no_alt_screen: bool = typer.Option(False, "--no-alt-screen", help="Disable alternate screen mode"),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """M2.5 model. Balanced across nim, kilo, minimax."""
    _run_codex_interactive_with_opts(
        "max",
        dangerously_bypass,
        resume,
        cd,
        print_mode,
        debug,
        add_dir,
        sandbox,
        full_auto,
        search,
        no_alt_screen,
        continue_session,
        prompt,
    )


@app.command("glm")
def dex_glm(
    dangerously_bypass: bool = typer.Option(
        True,
        "--dangerously-bypass-approvals-and-sandbox",
        "--yolo",
        help="Bypass approvals and sandbox (default: True)",
    ),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option(None, "--add-dir", help="Additional directories (repeatable)"),
    sandbox: str | None = typer.Option(
        None, "--sandbox", "-s", help="Sandbox: read-only, workspace-write, danger-full-access"
    ),
    full_auto: bool = typer.Option(False, "--full-auto", help="Convenience: -a on-request, --sandbox workspace-write"),
    search: bool = typer.Option(True, "--search", help="Enable web search"),
    no_alt_screen: bool = typer.Option(False, "--no-alt-screen", help="Disable alternate screen mode"),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """GLM-5 model. Balanced across glm, kilo, nim, minimax."""
    _run_codex_interactive_with_opts(
        "glm",
        dangerously_bypass,
        resume,
        cd,
        print_mode,
        debug,
        add_dir,
        sandbox,
        full_auto,
        search,
        no_alt_screen,
        continue_session,
        prompt,
    )


def _run_codex_interactive_with_opts(
    model_alias,
    dangerously_bypass,
    resume,
    cd,
    print_mode,
    debug,
    add_dir,
    sandbox,
    full_auto,
    search,
    no_alt_screen,
    continue_session,
    prompt,
):
    if print_mode:
        if not prompt:
            console.print("[red]Error: --print requires a prompt.[/red]")
            raise typer.Exit(1)
        _run_codex_exec(
            model_alias,
            prompt,
            cd=cd,
            add_dir=add_dir or None,
            sandbox=sandbox,
            full_auto=full_auto,
            dangerously_bypass=dangerously_bypass,
        )
        return
    extra: list[str] = _dex_passthrough_args(
        cd=cd,
        debug=debug,
        add_dir=add_dir or None,
        sandbox=sandbox,
        full_auto=full_auto,
        search=search,
        no_alt_screen=no_alt_screen,
    )
    if resume:
        extra.extend(["--resume", resume])
    if continue_session:
        from thegent.execution import RunRegistry

        reg = RunRegistry(_get_settings().session_dir)
        latest = reg.get_latest_session_id()
        if latest:
            extra.extend(["--resume", latest])
    if prompt:
        extra.append(prompt)
    _run_codex_interactive(model_alias, extra_args=extra, dangerously_bypass=dangerously_bypass)


@app.command("haiku")
def dex_haiku(
    dangerously_bypass: bool = typer.Option(
        True,
        "--dangerously-bypass-approvals-and-sandbox",
        "--yolo",
        help="Bypass approvals and sandbox (default: True)",
    ),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option(None, "--add-dir", help="Additional directories (repeatable)"),
    sandbox: str | None = typer.Option(
        None, "--sandbox", "-s", help="Sandbox: read-only, workspace-write, danger-full-access"
    ),
    full_auto: bool = typer.Option(False, "--full-auto", help="Convenience: -a on-request, --sandbox workspace-write"),
    search: bool = typer.Option(True, "--search", help="Enable web search"),
    no_alt_screen: bool = typer.Option(False, "--no-alt-screen", help="Disable alternate screen mode"),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Claude Haiku. Balanced across CC plan, antigravity, etc."""
    _run_codex_interactive_with_opts(
        "haiku",
        dangerously_bypass,
        resume,
        cd,
        print_mode,
        debug,
        add_dir,
        sandbox,
        full_auto,
        search,
        no_alt_screen,
        continue_session,
        prompt,
    )


@app.command("opus")
def dex_opus(
    dangerously_bypass: bool = typer.Option(
        True,
        "--dangerously-bypass-approvals-and-sandbox",
        "--yolo",
        help="Bypass approvals and sandbox (default: True)",
    ),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option(None, "--add-dir", help="Additional directories (repeatable)"),
    sandbox: str | None = typer.Option(
        None, "--sandbox", "-s", help="Sandbox: read-only, workspace-write, danger-full-access"
    ),
    full_auto: bool = typer.Option(False, "--full-auto", help="Convenience: -a on-request, --sandbox workspace-write"),
    search: bool = typer.Option(True, "--search", help="Enable web search"),
    no_alt_screen: bool = typer.Option(False, "--no-alt-screen", help="Disable alternate screen mode"),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Claude Opus. Balanced across CC plan, antigravity, etc."""
    _run_codex_interactive_with_opts(
        "opus",
        dangerously_bypass,
        resume,
        cd,
        print_mode,
        debug,
        add_dir,
        sandbox,
        full_auto,
        search,
        no_alt_screen,
        continue_session,
        prompt,
    )


@app.command("sonnet")
def dex_sonnet(
    dangerously_bypass: bool = typer.Option(
        True,
        "--dangerously-bypass-approvals-and-sandbox",
        "--yolo",
        help="Bypass approvals and sandbox (default: True)",
    ),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option(None, "--add-dir", help="Additional directories (repeatable)"),
    sandbox: str | None = typer.Option(
        None, "--sandbox", "-s", help="Sandbox: read-only, workspace-write, danger-full-access"
    ),
    full_auto: bool = typer.Option(False, "--full-auto", help="Convenience: -a on-request, --sandbox workspace-write"),
    search: bool = typer.Option(True, "--search", help="Enable web search"),
    no_alt_screen: bool = typer.Option(False, "--no-alt-screen", help="Disable alternate screen mode"),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Claude Sonnet. Balanced across CC plan, antigravity, etc."""
    _run_codex_interactive_with_opts(
        "sonnet",
        dangerously_bypass,
        resume,
        cd,
        print_mode,
        debug,
        add_dir,
        sandbox,
        full_auto,
        search,
        no_alt_screen,
        continue_session,
        prompt,
    )


@app.command("ultra")
def dex_ultra(
    dangerously_bypass: bool = typer.Option(
        True,
        "--dangerously-bypass-approvals-and-sandbox",
        "--yolo",
        help="Bypass approvals and sandbox (default: True)",
    ),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option(None, "--add-dir", help="Additional directories (repeatable)"),
    sandbox: str | None = typer.Option(
        None, "--sandbox", "-s", help="Sandbox: read-only, workspace-write, danger-full-access"
    ),
    full_auto: bool = typer.Option(False, "--full-auto", help="Convenience: -a on-request, --sandbox workspace-write"),
    search: bool = typer.Option(True, "--search", help="Enable web search"),
    no_alt_screen: bool = typer.Option(False, "--no-alt-screen", help="Disable alternate screen mode"),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Llama Nemotron Ultra. NIM (FREE)."""
    _run_codex_interactive_with_opts(
        "ultra",
        dangerously_bypass,
        resume,
        cd,
        print_mode,
        debug,
        add_dir,
        sandbox,
        full_auto,
        search,
        no_alt_screen,
        continue_session,
        prompt,
    )


@app.command("flash")
def dex_flash(
    dangerously_bypass: bool = typer.Option(
        True,
        "--dangerously-bypass-approvals-and-sandbox",
        "--yolo",
        help="Bypass approvals and sandbox (default: True)",
    ),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option(None, "--add-dir", help="Additional directories (repeatable)"),
    sandbox: str | None = typer.Option(
        None, "--sandbox", "-s", help="Sandbox: read-only, workspace-write, danger-full-access"
    ),
    full_auto: bool = typer.Option(False, "--full-auto", help="Convenience: -a on-request, --sandbox workspace-write"),
    search: bool = typer.Option(True, "--search", help="Enable web search"),
    no_alt_screen: bool = typer.Option(False, "--no-alt-screen", help="Disable alternate screen mode"),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Gemini 3 Flash via cliproxy. Fast, cheap."""
    _run_codex_interactive_with_opts(
        "flash",
        dangerously_bypass,
        resume,
        cd,
        print_mode,
        debug,
        add_dir,
        sandbox,
        full_auto,
        search,
        no_alt_screen,
        continue_session,
        prompt,
    )


@app.command("mini")
def dex_mini(
    dangerously_bypass: bool = typer.Option(
        True,
        "--dangerously-bypass-approvals-and-sandbox",
        "--yolo",
        help="Bypass approvals and sandbox (default: True)",
    ),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option(None, "--add-dir", help="Additional directories (repeatable)"),
    sandbox: str | None = typer.Option(
        None, "--sandbox", "-s", help="Sandbox: read-only, workspace-write, danger-full-access"
    ),
    full_auto: bool = typer.Option(False, "--full-auto", help="Convenience: -a on-request, --sandbox workspace-write"),
    search: bool = typer.Option(True, "--search", help="Enable web search"),
    no_alt_screen: bool = typer.Option(False, "--no-alt-screen", help="Disable alternate screen mode"),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """GPT-5 mini / Copilot (free tier)."""
    _run_codex_interactive_with_opts(
        "mini",
        dangerously_bypass,
        resume,
        cd,
        print_mode,
        debug,
        add_dir,
        sandbox,
        full_auto,
        search,
        no_alt_screen,
        continue_session,
        prompt,
    )


@app.command("free")
def dex_free(
    dangerously_bypass: bool = typer.Option(
        True,
        "--dangerously-bypass-approvals-and-sandbox",
        "--yolo",
        help="Bypass approvals and sandbox (default: True)",
    ),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option(None, "--add-dir", help="Additional directories (repeatable)"),
    sandbox: str | None = typer.Option(
        None, "--sandbox", "-s", help="Sandbox: read-only, workspace-write, danger-full-access"
    ),
    full_auto: bool = typer.Option(False, "--full-auto", help="Convenience: -a on-request, --sandbox workspace-write"),
    search: bool = typer.Option(True, "--search", help="Enable web search"),
    no_alt_screen: bool = typer.Option(False, "--no-alt-screen", help="Disable alternate screen mode"),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """GPT-5 mini / Copilot (free tier). Alias for dex mini."""
    _run_codex_interactive_with_opts(
        "mini",
        dangerously_bypass,
        resume,
        cd,
        print_mode,
        debug,
        add_dir,
        sandbox,
        full_auto,
        search,
        no_alt_screen,
        continue_session,
        prompt,
    )


_DEX_RUN_MODELS: frozenset[str] = frozenset(set(_MODEL_ALIAS.keys()) | set(_MODEL_ALIAS.values()))


@app.command("run")
def dex_run(
    model_alias: str = typer.Argument(..., help="Model: max, glm, haiku, opus, sonnet, ultra, flash, mini"),
    prompt: str = typer.Argument(..., help="Task prompt"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    mode: str = typer.Option("write", "--mode", "-m", help="Union[write, read]-only"),
    timeout: int = typer.Option(90, "--timeout", "-t", help="Timeout in seconds"),
) -> None:
    """Run a task. Model-first, no provider filter."""
    canonical = _MODEL_ALIAS.get(model_alias.lower(), model_alias)
    if canonical not in _DEX_RUN_MODELS and model_alias.lower() not in _DEX_RUN_MODELS:
        console.print(
            f"[red]Unknown model '{model_alias}'. Allowed: max, glm, haiku, opus, sonnet, ultra, flash, mini[/red]"
        )
        raise typer.Exit(1)
    _run_model_cmd(model_alias, prompt, cd=cd, mode=mode, timeout=timeout)


@app.command("bg")
def dex_bg(
    model_alias: str = typer.Argument(..., help="Model: max, glm, haiku, opus, sonnet, ultra, flash, mini"),
    prompt: str = typer.Argument(..., help="Task prompt"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    mode: str = typer.Option("write", "--mode", "-m", help="Union[write, read]-only"),
    timeout: int = typer.Option(90, "--timeout", "-t", help="Timeout in seconds"),
    owner: str | None = typer.Option(None, "--owner", "-o", help="Owner tag"),
) -> None:
    """Start a background task. Model-first, no provider filter."""
    canonical = _MODEL_ALIAS.get(model_alias.lower(), model_alias)
    if canonical not in _DEX_RUN_MODELS and model_alias.lower() not in _DEX_RUN_MODELS:
        console.print(
            f"[red]Unknown model '{model_alias}'. Allowed: max, glm, haiku, opus, sonnet, ultra, flash, mini[/red]"
        )
        raise typer.Exit(1)
    _bg_model_cmd(model_alias, prompt, cd=cd, mode=mode, timeout=timeout, owner=owner)


@app.command("ps")
def dex_ps(
    all_sessions: bool = typer.Option(False, "--all", help="Show sessions for all owners"),
    owner: str | None = typer.Option(None, "--owner", help="Override owner filter"),
    format: str | None = typer.Option(
        None,
        "--format",
        "-f",
        help="Output format: Union[json, rich] (default) | md (agent-friendly)",
    ),
    include_contract: bool = typer.Option(
        False, "--include-contract", help="Include resolved route contract metadata in list payload"
    ),
) -> None:
    """List registered background sessions."""
    from thegent.cli import ps_cmd

    ps_cmd(all_sessions=all_sessions, owner=owner, format=format, include_contract=include_contract)


@app.command("logs")
def dex_logs(
    session_id: str = typer.Argument(..., help="Session id"),
    follow: bool = typer.Option(False, "--follow", "-F", help="Follow log output"),
    stderr: bool = typer.Option(False, "--stderr", help="Show stderr log instead of stdout"),
    tail: int = typer.Option(200, "--tail", help="Initial tail lines"),
    timeout: int = typer.Option(0, "--timeout", help="Max follow timeout seconds (0=unbounded)"),
) -> None:
    """Print session logs."""
    from thegent.cli import logs_cmd

    logs_cmd(session_id=session_id, follow=follow, stderr=stderr, tail=tail, timeout=timeout)


@app.command("status")
def dex_status(
    session_id: str = typer.Argument(..., help="Session id"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json or rich"),
    include_contract: bool = typer.Option(
        False, "--include-contract", help="Include resolved route contract metadata in output"
    ),
) -> None:
    """Show one session status."""
    from thegent.cli import status_cmd

    status_cmd(session_id=session_id, format=format, include_contract=include_contract)


@app.command("stop")
def dex_stop(
    session_id: str = typer.Argument(..., help="Session id"),
    force: bool = typer.Option(False, "--force", help="Use SIGKILL instead of SIGTERM"),
    wind_down: bool = typer.Option(
        False,
        "--wind-down",
        help="Send SIGTERM and wait up to --grace seconds before returning",
    ),
    grace: int = typer.Option(
        20,
        "--grace",
        min=0,
        help="Wind-down grace window in seconds",
    ),
) -> None:
    """Stop a running session."""
    from thegent.cli import stop_cmd

    stop_cmd(session_id=session_id, force=force, wind_down=wind_down, grace=grace)


@app.command("wait")
def dex_wait(
    session_id: str = typer.Argument(..., help="Session id"),
    timeout: int = typer.Option(0, "--timeout", "-t", help="Max wait seconds (0=unbounded)"),
) -> None:
    """Wait for session completion and return session exit code."""
    from thegent.cli import wait_cmd

    wait_cmd(session_id=session_id, timeout=timeout)


@app.command("inspect")
def dex_inspect(
    session_ids: list[str] = typer.Argument(None, help="Session ID(s). Use --owner to inspect all for owner."),
    owner: str | None = typer.Option(None, "--owner", "-o", help="Inspect all sessions for this owner"),
    tail: int = typer.Option(50, "--tail", "-n", help="Log lines per session"),
    stderr: bool = typer.Option(False, "--stderr", help="Show stderr instead of stdout"),
    format: str | None = typer.Option(None, "--format", "-f", help="Output format: json or rich"),
    include_contract: bool = typer.Option(
        False, "--include-contract", help="Include resolved route contract metadata in status payload"
    ),
) -> None:
    """Show status and logs for one or more sessions."""
    from thegent.cli import inspect_cmd

    inspect_cmd(
        session_ids=session_ids,
        owner=owner,
        tail=tail,
        stderr=stderr,
        format=format,
        include_contract=include_contract,
    )


@app.command("history")
def dex_history(
    limit: int = typer.Option(50, "--limit", "-l", help="Number of runs to show"),
    format: str | None = typer.Option(
        None,
        "--format",
        help="Output format: Union[json, rich] (default) | md",
    ),
) -> None:
    """List execution run history (sync and background)."""
    from thegent.cli import history_cmd

    history_cmd(limit=limit, format=format)


@app.command("doctor")
def dex_doctor(
    fix: bool = typer.Option(False, "--fix", "-f", help="Attempt to fix issues"),
) -> None:
    """Run thegent doctor (harness-equiv)."""
    import sys

    from thegent.doctor import run_doctor

    success = run_doctor(fix=fix)
    sys.exit(0 if success else 1)


@app.command("install-links")
def install_links(
    bin_dir: Path = typer.Option(
        Path.home() / ".local" / "bin",
        "--bin-dir",
        help="Directory to install command wrappers",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
) -> None:
    """Install dex shims: dex, dexmax, dexglm, dexhaiku, dexopus, dexsonnet, dexstep (model-only)."""
    if not bin_dir.exists():
        console.print(f"[red]Error: {bin_dir} does not exist.[/red]")
        raise typer.Exit(1)

    installed = 0
    for target_name, command, label in _iter_install_targets():
        target = bin_dir / target_name
        if _write_wrapper(target, command, force=force):
            installed += 1
            console.print(f"[green]Installed[/green] {target} -> {label}")
        else:
            console.print(f"[yellow]Skipping {target} (already exists). Use --force to overwrite.[/yellow]")

    if installed:
        console.print("[bold]Wrappers installed successfully.[/bold]")
    elif not force:
        console.print("[yellow]No wrappers updated.[/yellow]")


if __name__ == "__main__":
    app()
