"""Claude-backed interactive agent CLI (clode)."""

import contextlib
import os
import shutil
import subprocess
from thegent.infra.shim_subprocess import run as shim_run
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import typer

from thegent.agents.cliproxy_manager import fetch_provider_metrics
from thegent.clode_args import clode_passthrough_args as _clode_passthrough_args_impl
from thegent.clode_binary_discovery import find_claude as _find_claude_impl
from thegent.clode_config_isolation import ensure_claude_config_isolation as _ensure_claude_config_isolation_impl
from thegent import clode_glm_policy as _clode_glm_policy
from thegent import clode_model_routing as _clode_model_routing
from thegent.clode_glm_policy import (
    InvalidPolicyError,
    resolve_clode_token as _resolve_clode_token_impl,
)
from thegent.clode_model_routing import (
    model_for_provider as _model_for_provider_impl,
    resolve_provider_for_model as _resolve_provider_for_model_impl,
)

# Import thegent CLI commands to reuse them.
# Lazy imports used in commands to speed up CLI startup.
from thegent.cli import bg_cmd, history_cmd, inspect_cmd, logs_cmd, ps_cmd, run_cmd, status_cmd, stop_cmd, wait_cmd
from thegent.infra.power import wrap_with_caffeinate


def _is_triggered_by_agent_process():
    from thegent.discovery import _is_triggered_by_agent_process as impl

    return impl()


# Lazy imports for better startup performance
def _get_settings():
    from thegent.config import ThegentSettings

    return ThegentSettings()


class LazyConsole:
    def __getattr__(self, name) -> Any:
        from rich.console import Console

        global console
        console = Console()
        return getattr(console, name)


console = LazyConsole()
app = typer.Typer(help="Claude-backed interactive agent CLI (clode)")

_GLM_OFFER_SET = _clode_glm_policy.GLM_OFFER_SET
_GLM_OFFER_COST = _clode_glm_policy.GLM_OFFER_COST
_GLM_PREFERRED_BACKENDS = _clode_glm_policy.GLM_PREFERRED_BACKENDS
_MODEL_ALIAS = _clode_model_routing.MODEL_ALIAS
_MODEL_PROVIDER_SETS = _clode_model_routing.MODEL_PROVIDER_SETS
_MODEL_COUNTER = _clode_model_routing.MODEL_COUNTER
_MODEL_PROVIDERS = _clode_model_routing.MODEL_PROVIDERS
_CLODE_PROVIDER_MODEL = _clode_model_routing.CLODE_PROVIDER_MODEL
_GLM_POLICY_COUNTER: Counter[str] = Counter()
_CLODE_BYPASS_FLAG = "--dangerously-skip-permissions"
_SITBACK_CLODE_YOLO_FLAG = "--yolo"
_SITBACK_CLODE_BYPASS_FLAG = "--dangerously-bypass-approvals-and-sandbox"


@app.callback(invoke_without_command=True)
def default_clode(
    ctx: typer.Context,
    native: bool = typer.Option(
        False,
        "--native",
        help="Bypass cliproxy/thegent routing and run native claude directly",
    ),
) -> None:
    """Start Claude Code with model-first routing. Default: flash (Gemini 3 Flash)."""
    if native:
        claude_path = _ensure_claude_installed(require_native=True)
        passthrough = [arg for arg in sys.argv[1:] if arg != "--native"]
        cmd = [claude_path, *passthrough]
        console.print("[bold green]Starting native Claude (proxy bypass)...[/bold green]")
        os.execvpe(cmd[0], cmd, os.environ.copy())

    if ctx.invoked_subcommand is None:
        _run_model_interactive("flash")


def _install_harness_link(bin_dir: Path, harness: str, force: bool = False) -> bool:
    """Install a harness symlink to thegent-shims. Returns True when link is created/updated."""
    shims_path = shutil.which("thegent-shims")
    if not shims_path:
        candidate = bin_dir / "thegent-shims"
        if candidate.exists():
            shims_path = str(candidate)
    if not shims_path:
        console.print(
            "[red]thegent-shims not found.[/red] Install it first with: [dim]thegent install-shims --all[/dim]"
        )
        raise typer.Exit(1)

    target = bin_dir / harness
    if target.exists() or target.is_symlink():
        if not force:
            return False
        if target.is_dir() and not target.is_symlink():
            from thegent.errors import print_error

            print_error(f"{target} is a directory. Remove it before reinstalling.")
            raise typer.Exit(1)
        target.unlink()

    target.symlink_to(Path(shims_path))
    return True


def _resolve_provider_for_model(model_alias: str) -> str:
    """Resolve provider for model-first routing. Round-robin across available providers."""
    return _resolve_provider_for_model_impl(model_alias)


def _resolve_clode_token(provider: str, prefer: str, policy: str) -> str:
    """Resolve provider token for ANTHROPIC_API_KEY."""
    try:
        return _resolve_clode_token_impl(
            provider,
            prefer,
            policy,
            _GLM_POLICY_COUNTER,  # type: ignore[arg-type]
            fetch_provider_metrics,
        )
    except InvalidPolicyError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc


# Minimax clode guidance: only when model-router-harness pairing aligns (clode + minimax/kilo + MiniMax-M2.5)
MINIMAX_CLODE_GUIDANCE_URL = "https://platform.minimax.io/docs/coding-plan/claude-code"


def _model_for_provider(provider: str) -> str:
    """Default model for a provider (derived from model->provider mapping)."""
    return _model_for_provider_impl(provider)


def _ensure_claude_config_isolation(config_dir: Path) -> None:
    _ensure_claude_config_isolation_impl(config_dir)


def _get_claude_env(provider: str, model_override: str | None = None) -> dict[str, str]:
    """Get environment variables for Claude Code pointing to thegent proxy.

    Aligns with Minimax clode guidance (MINIMAX_CLODE_GUIDANCE_URL) and
    z.ai docs (docs.z.ai/devpack/tool/claude): use provider-native model names
    (MiniMax-M2.5, glm-5) so the model "turns into" the provider correctly.
    No Claude ID mapping needed.
    """
    settings = _get_settings()

    # WP-Y15: Ensure proxy is running (adapter optional for clode but good for consistency)
    from thegent.agents.cliproxy_manager import ensure_proxy_running

    ensure_proxy_running(settings)

    env = os.environ.copy()
    base = f"http://{settings.mcp_host}:{settings.cliproxy_port}"
    env["ANTHROPIC_BASE_URL"] = base
    env["ANTHROPIC_API_KEY"] = provider
    # WP-Y12: Use isolated config dir to avoid "Auth conflict" with global claude.ai login
    config_dir = settings.cache_dir / "claude-config"
    config_dir.mkdir(parents=True, exist_ok=True)
    env["CLAUDE_CONFIG_DIR"] = str(config_dir)

    model = model_override or _CLODE_PROVIDER_MODEL.get(provider) or _model_for_provider(provider)

    env["ANTHROPIC_MODEL"] = model
    env["ANTHROPIC_SONNET_MODEL"] = model
    env["ANTHROPIC_HAIKU_MODEL"] = model
    env["ANTHROPIC_OPUS_MODEL"] = model
    env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = model
    env["ANTHROPIC_DEFAULT_SONNET_MODEL"] = model
    env["ANTHROPIC_DEFAULT_OPUS_MODEL"] = model
    env["ANTHROPIC_SMALL_FAST_MODEL"] = model
    env["CLAUDE_MODEL"] = model
    env["API_TIMEOUT_MS"] = "300000"
    if provider in ("glm", "auto") or settings.sitback_harness:
        env["THGENT_ROUTING"] = "round_robin"
    env["PATH"] = os.environ.get("PATH", "")
    return env


def _clode_passthrough_args(
    *,
    cd: Path | None = None,
    debug: bool = False,
    add_dir: list[str] | None = None,
    output_format: str | None = None,
    continue_session: bool = False,
) -> list[str]:
    return _clode_passthrough_args_impl(
        cd=cd,
        debug=debug,
        add_dir=add_dir,
        output_format=output_format,
        continue_session=continue_session,
    )


def _find_claude(*, require_native: bool = False) -> str | None:
    return _find_claude_impl(require_native=require_native)


def _ensure_claude_installed(suggest_dex: bool = False, require_native: bool = False) -> str:
    """Auto-install Claude Code via brew or bun if missing. Returns path or raises."""
    p = _find_claude(require_native=require_native)
    if p:
        return p
    # Try brew first
    brew = shutil.which("brew")
    if brew:
        console.print("[dim]Installing Claude Code via Homebrew...[/dim]")
        r = shim_run([brew, "install", "--cask", "claude-code"], capture_output=True, text=True, check=False)
        if r.returncode == 0:
            p = _find_claude(require_native=require_native)
            if p:
                return p
    # Try bun
    bun = shutil.which("bun")
    if bun:
        console.print("[dim]Installing Claude Code via Bun...[/dim]")
        r = shim_run(
            [bun, "install", "-g", "@anthropic-ai/claude-code"], capture_output=True, text=True, check=False
        )
        if r.returncode == 0:
            p = _find_claude(require_native=require_native)
            if p:
                return p
    if require_native:
        console.print(
            "[red]Error: native 'claude' CLI not found (or only thegent-shims was found).[/red]\n"
            "[dim]Set THGENT_NATIVE_CLAUDE_BIN=/absolute/path/to/claude to force a specific binary.[/dim]"
        )
    else:
        console.print("[red]Error: 'claude' (Claude Code) CLI not found.[/red]")
    if suggest_dex:
        console.print("[dim]Or use: thegent sitback --dex (Codex)[/dim]")
    raise typer.Exit(1)


def _run_claude_print(
    provider: str,
    prompt: str,
    *,
    cd: Path | None = None,
    add_dir: list[str] | None = None,
    output_format: str | None = None,
    model_override: str | None = None,
) -> None:
    """Run Claude Code in headless mode (-p/--print)."""
    _ensure_provider_configured(provider)
    env = _get_claude_env(provider, model_override=model_override)
    _ensure_claude_config_isolation(Path(env["CLAUDE_CONFIG_DIR"]))

    claude_path = _ensure_claude_installed()

    cmd = [claude_path, "-p", prompt]
    if not _is_triggered_by_agent_process():
        cmd.insert(1, _CLODE_BYPASS_FLAG)
    extra = _clode_passthrough_args(cd=cd, add_dir=add_dir, output_format=output_format)
    cmd.extend(extra)

    if cd:
        os.chdir(cd)

    # Wrap with caffeinate to prevent sleep on macOS
    cmd = wrap_with_caffeinate(cmd, "claude")

    console.print(f"[bold green]Claude print (headless) via {provider}...[/bold green]")
    timeout_seconds = int(env.get("THGENT_CLODE_PRINT_TIMEOUT", "15"))
    try:
        result = shim_run(cmd, env=env, check=False, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        console.print(f"[red]Error: clode print timed out after {timeout_seconds}s.[/red]")
        raise typer.Exit(124)
    raise typer.Exit(result.returncode)


def _ensure_provider_configured(provider: str) -> None:
    """Check if provider is configured in cliproxy; offer to run setup if not."""
    if provider == "auto":
        return
    settings = _get_settings()
    config_path = settings.cliproxy_config_path.expanduser().resolve()
    if not config_path.exists():
        return
    import yaml

    try:
        config = yaml.safe_load(config_path.read_text())
        if not isinstance(config, dict):
            return
        from thegent.agents.cliproxy_manager import _LOGIN_FLAGS, _has_provider_credentials

        if _has_provider_credentials(config, provider) or provider in _LOGIN_FLAGS:
            return
        console.print(f"[yellow]Warning: Provider '{provider}' may not be configured in cliproxy.[/yellow]")
        if sys.stdin.isatty():
            try:
                resp = input("  Run setup now? [Y/n]: ").strip().lower()
                if resp in ("", "y", "yes"):
                    shim_run(
                        [sys.executable, "-m", "thegent.main", "cliproxy", "login", provider],
                        check=False,
                    )
                    config = yaml.safe_load(config_path.read_text()) if config_path.exists() else {}
                    if not isinstance(config, dict) or not (
                        _has_provider_credentials(config, provider) or provider in _LOGIN_FLAGS
                    ):
                        console.print(f"[dim]Run manually: thegent cliproxy login {provider}[/dim]\n")
                else:
                    console.print(f"[dim]Run manually: thegent cliproxy login {provider}[/dim]\n")
            except (EOFError, KeyboardInterrupt):
                console.print(f"[dim]Run manually: thegent cliproxy login {provider}[/dim]\n")
        else:
            console.print(f"[dim]Run: thegent cliproxy login {provider}[/dim]\n")
    except Exception:
        pass


def _run_claude_interactive(
    provider: str,
    extra_args: list[str] | None = None,
    model_override: str | None = None,
) -> None:
    """Start an interactive Claude Code session."""
    _ensure_provider_configured(provider)
    env = _get_claude_env(provider, model_override=model_override)

    _ensure_claude_config_isolation(Path(env["CLAUDE_CONFIG_DIR"]))

    claude_path = _ensure_claude_installed()

    console.print(f"[bold green]Starting interactive Claude session via {provider} proxy...[/bold green]")
    console.print(f"[dim]Proxy URL: {env['ANTHROPIC_BASE_URL']}[/dim]")
    # Minimax guidance only when model-router-harness pairing aligns (clode + minimax/kilo + MiniMax-M2.5)
    model = _CLODE_PROVIDER_MODEL.get(provider) or model_override
    if provider in ("minimax", "kilo") and model and "minimax" in model.lower():
        console.print(f"[dim]Minimax clode guidance: {MINIMAX_CLODE_GUIDANCE_URL}[/dim]")
    # WP-Y11: Human-driven runs get bypass by default; agent-triggered runs never do
    cmd = [claude_path]
    if not _is_triggered_by_agent_process():
        cmd.append(_CLODE_BYPASS_FLAG)
    if extra_args:
        for arg in extra_args:
            if arg not in {"--force", _CLODE_BYPASS_FLAG}:
                cmd.append(arg)

    # Wrap with caffeinate to prevent sleep on macOS
    cmd = wrap_with_caffeinate(cmd, "claude")

    # WP-Y15: Use os.execvpe for native interactive experience (better signal handling)
    # This replaces the Python process with the Claude process.
    import os

    os.execvpe(cmd[0], cmd, env)


def create_provider_app(provider: str) -> typer.Typer:
    """Create a subcommand group for a provider."""
    provider_app = typer.Typer(help=f"{provider.upper()} Claude-backed operations")

    @provider_app.callback(invoke_without_command=True)
    def main(ctx: typer.Context) -> None:
        """Default to interactive shell if no subcommand is given."""
        if ctx.invoked_subcommand is None:
            env = _get_claude_env(provider)
            model = env["ANTHROPIC_MODEL"]
            extra = ["--model", model]
            if not _is_triggered_by_agent_process():
                extra.append(_CLODE_BYPASS_FLAG)
            _run_claude_interactive(
                provider,
                model_override=model,
                extra_args=extra,
            )

    @provider_app.command("run")
    def clode_run(
        prompt: str,
        cd: str | None = typer.Option(None, "--cd", "-d", help="Working directory"),
        mode: str = typer.Option("write", "--mode", "-m", help="write | read-only"),
        timeout: int = typer.Option(90, "--timeout", "-t", help="Timeout in seconds"),
        model: str = typer.Option(
            _CLODE_PROVIDER_MODEL.get(provider, "MiniMax-M2.5"),
            "--model",
            help="Model override (provider-native: MiniMax-M2.5, glm-5)",
        ),
    ) -> None:
        """Run a task via Claude Code using the proxy (synchronous)."""
        from thegent.cli import run_cmd

        os.environ.update(_get_claude_env(provider, model_override=model))
        run_cmd(
            prompt=prompt,
            agent="interactive_agent",
            cd=Path(cd) if cd else None,
            mode=mode,
            timeout=timeout,
            model=model,
        )

    @provider_app.command("bg")
    def clode_bg(
        prompt: str,
        cd: str | None = typer.Option(None, "--cd", "-d", help="Working directory"),
        mode: str = typer.Option("write", "--mode", "-m", help="write | read-only"),
        timeout: int = typer.Option(90, "--timeout", "-t", help="Timeout in seconds"),
        owner: str | None = typer.Option(None, "--owner", "-o", help="Owner tag"),
        model: str = typer.Option(
            _CLODE_PROVIDER_MODEL.get(provider, "MiniMax-M2.5"),
            "--model",
            help="Model override (provider-native: MiniMax-M2.5, glm-5)",
        ),
    ) -> None:
        """Start a background task via Claude Code using the proxy."""
        from thegent.cli import bg_cmd

        os.environ.update(_get_claude_env(provider, model_override=model))
        bg_cmd(
            prompt=prompt,
            agent="interactive_agent",
            cd=Path(cd) if cd else None,
            mode=mode,
            timeout=timeout,
            full=False,
            model=model,
            owner=owner,
        )

    @provider_app.command("ps")
    def clode_ps(
        all_sessions: bool = typer.Option(False, "--all", help="Show sessions for all owners"),
        owner: str | None = typer.Option(None, "--owner", help="Override owner filter"),
        format: str | None = typer.Option(
            None,
            "--format",
            "-f",
            help="Output format: json | rich (default) | md (agent-friendly)",
        ),
        include_contract: bool = typer.Option(
            False, "--include-contract", help="Include resolved route contract metadata in list payload"
        ),
    ) -> None:
        """List registered background sessions."""
        from thegent.cli import ps_cmd

        ps_cmd(all_sessions=all_sessions, owner=owner, format=format, include_contract=include_contract)

    @provider_app.command("logs")
    def clode_logs(
        session_id: str = typer.Argument(..., help="Session id"),
        follow: bool = typer.Option(False, "--follow", "-F", help="Follow log output"),
        stderr: bool = typer.Option(False, "--stderr", help="Show stderr log instead of stdout"),
        tail: int = typer.Option(200, "--tail", help="Initial tail lines"),
        timeout: int = typer.Option(0, "--timeout", help="Max follow timeout seconds (0=unbounded)"),
    ) -> None:
        """Print session logs."""
        from thegent.cli import logs_cmd

        logs_cmd(session_id=session_id, follow=follow, stderr=stderr, tail=tail, timeout=timeout)

    @provider_app.command("status")
    def clode_status(
        session_id: str = typer.Argument(..., help="Session id"),
        format: str | None = typer.Option(None, "--format", "-f", help="Output format: json or rich"),
        include_contract: bool = typer.Option(
            False, "--include-contract", help="Include resolved route contract metadata in output"
        ),
    ) -> None:
        """Show one session status."""
        from thegent.cli import status_cmd

        status_cmd(session_id=session_id, format=format, include_contract=include_contract)

    @provider_app.command("stop")
    def clode_stop(
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

    @provider_app.command("wait")
    def clode_wait(
        session_id: str = typer.Argument(..., help="Session id"),
        timeout: int = typer.Option(0, "--timeout", "-t", help="Max wait seconds (0=unbounded)"),
    ) -> None:
        """Wait for session completion and return session exit code."""
        from thegent.cli import wait_cmd

        wait_cmd(session_id=session_id, timeout=timeout)

    @provider_app.command("inspect")
    def clode_inspect(
        session_ids: list[str] = typer.Argument(
            default=[], help="Session ID(s). Use --owner to inspect all for owner."
        ),
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

    @provider_app.command("history")
    def clode_history(
        limit: int = typer.Option(50, "--limit", "-l", help="Number of runs to show"),
        format: str | None = typer.Option(
            None,
            "--format",
            help="Output format: json | rich (default) | md",
        ),
    ) -> None:
        """List execution run history (sync and background)."""
        from thegent.cli import history_cmd

        history_cmd(limit=limit, format=format)

    _ = (
        main,
        clode_run,
        clode_bg,
        clode_ps,
        clode_logs,
        clode_status,
        clode_stop,
        clode_wait,
        clode_inspect,
        clode_history,
    )
    return provider_app


app.add_typer(create_provider_app("nim"), name="nim")
app.add_typer(create_provider_app("openrouter"), name="openrouter")
app.add_typer(create_provider_app("kilo"), name="kilo")
app.add_typer(create_provider_app("minimax"), name="minimax")


def _run_model_interactive(
    model_alias: str,
    provider: str | None = None,
    resume: str | None = None,
    prompt: str | None = None,
    *,
    cd: Path | None = None,
    print_mode: bool = False,
    debug: bool = False,
    add_dir: list[str] | None = None,
    output_format: str | None = None,
    continue_session: bool = False,
) -> None:
    """Start Claude Code with model-first routing. Provider optional to lock backend."""
    canonical = _MODEL_ALIAS.get(model_alias.lower(), model_alias)
    if provider:
        provider = provider.strip().lower()
        providers = _MODEL_PROVIDER_SETS.get(canonical)
        if providers and provider not in providers:
            console.print(
                f"[yellow]Provider '{provider}' not in set for {canonical}. "
                f"Valid: {', '.join(providers)}. Using {provider} anyway.[/yellow]"
            )
    else:
        provider = _resolve_provider_for_model(model_alias)
    model = _CLODE_PROVIDER_MODEL.get(provider) or canonical

    if print_mode:
        if not prompt:
            console.print("[red]Error: --print requires a prompt.[/red]")
            raise typer.Exit(1)
        _run_claude_print(provider, prompt, cd=cd, add_dir=add_dir, output_format=output_format, model_override=model)
        return

    extra: list[str] = ["--model", model]
    if not _is_triggered_by_agent_process():
        extra.append(_CLODE_BYPASS_FLAG)
    extra.extend(
        _clode_passthrough_args(
            cd=cd, debug=debug, add_dir=add_dir, output_format=output_format, continue_session=continue_session
        )
    )
    if resume:
        extra.extend(["--resume", resume])
    if prompt:
        extra.append(prompt)
    if cd:
        os.chdir(cd)
    _run_claude_interactive(provider, extra_args=extra, model_override=model)


def _provider_opt() -> str | None:
    return typer.Option(
        None,
        "--provider",
        "-x",
        help="Optional: lock to provider (nim, kilo, minimax, glm, claude, kiro, etc.)",
    )


@app.command("comp")
def clode_comp(
    provider: str | None = _provider_opt(),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(
        None, "--output-format", help="Output format when --print: text, json, stream-json"
    ),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Composer 1 (via Cursor). Use -x cursor to lock."""
    _run_model_interactive(
        "comp",
        provider=provider,
        resume=resume,
        prompt=prompt,
        cd=cd,
        print_mode=print_mode,
        debug=debug,
        add_dir=add_dir or None,
        output_format=output_format,
        continue_session=continue_session,
    )


@app.command("composer")
def clode_composer(
    provider: str | None = _provider_opt(),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(
        None, "--output-format", help="Output format when --print: text, json, stream-json"
    ),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Composer 1.5 (via Cursor). Use -x cursor to lock."""
    _run_model_interactive(
        "composer",
        provider=provider,
        resume=resume,
        prompt=prompt,
        cd=cd,
        print_mode=print_mode,
        debug=debug,
        add_dir=add_dir or None,
        output_format=output_format,
        continue_session=continue_session,
    )


@app.command("haiku")
def clode_haiku(
    provider: str | None = _provider_opt(),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(
        None, "--output-format", help="Output format when --print: text, json, stream-json"
    ),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Claude Haiku 4.5 balanced across claude, antigravity, codex (proxy API), kiro."""
    _run_model_interactive(
        "haiku",
        provider=provider,
        resume=resume,
        prompt=prompt,
        cd=cd,
        print_mode=print_mode,
        debug=debug,
        add_dir=add_dir or None,
        output_format=output_format,
        continue_session=continue_session,
    )


@app.command("opus")
def clode_opus(
    provider: str | None = _provider_opt(),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(
        None, "--output-format", help="Output format when --print: text, json, stream-json"
    ),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Claude Opus 4.6 balanced across claude, antigravity, kiro."""
    _run_model_interactive(
        "opus",
        provider=provider,
        resume=resume,
        prompt=prompt,
        cd=cd,
        print_mode=print_mode,
        debug=debug,
        add_dir=add_dir or None,
        output_format=output_format,
        continue_session=continue_session,
    )


@app.command("opus1m")
def clode_opus1m(
    provider: str | None = _provider_opt(),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(
        None, "--output-format", help="Output format when --print: text, json, stream-json"
    ),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Claude Opus 4.6 with 1M context. Balanced across claude, antigravity, kiro."""
    _run_model_interactive(
        "opus1m",
        provider=provider,
        resume=resume,
        prompt=prompt,
        cd=cd,
        print_mode=print_mode,
        debug=debug,
        add_dir=add_dir or None,
        output_format=output_format,
        continue_session=continue_session,
    )


@app.command("sonnet")
def clode_sonnet(
    provider: str | None = _provider_opt(),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(
        None, "--output-format", help="Output format when --print: text, json, stream-json"
    ),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Claude Sonnet 4.6 via OpenRouter."""
    _run_model_interactive(
        "sonnet",
        provider=provider,
        resume=resume,
        prompt=prompt,
        cd=cd,
        print_mode=print_mode,
        debug=debug,
        add_dir=add_dir or None,
        output_format=output_format,
        continue_session=continue_session,
    )


@app.command("step")
def clode_step(
    provider: str | None = _provider_opt(),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(
        None, "--output-format", help="Output format when --print: text, json, stream-json"
    ),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Step 3.5 Flash via NIM. Fast, cheap."""
    _run_model_interactive(
        "step",
        provider=provider,
        resume=resume,
        prompt=prompt,
        cd=cd,
        print_mode=print_mode,
        debug=debug,
        add_dir=add_dir or None,
        output_format=output_format,
        continue_session=continue_session,
    )


@app.command("flash")
def clode_flash(
    provider: str | None = _provider_opt(),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(
        None, "--output-format", help="Output format when --print: text, json, stream-json"
    ),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Gemini 3 Flash via cliproxy. Fast, cheap."""
    _run_model_interactive(
        "flash",
        provider=provider,
        resume=resume,
        prompt=prompt,
        cd=cd,
        print_mode=print_mode,
        debug=debug,
        add_dir=add_dir or None,
        output_format=output_format,
        continue_session=continue_session,
    )


@app.command("mini")
def clode_mini(
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(
        None, "--output-format", help="Output format when --print: text, json, stream-json"
    ),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """GPT-5 mini / Copilot (free tier). Alias for clode free."""
    _run_model_interactive(
        "mini",
        provider="copilot",
        resume=resume,
        prompt=prompt,
        cd=cd,
        print_mode=print_mode,
        debug=debug,
        add_dir=add_dir or None,
        output_format=output_format,
        continue_session=continue_session,
    )


@app.command("high")
def clode_high(
    provider: str | None = _provider_opt(),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(
        None, "--output-format", help="Output format when --print: text, json, stream-json"
    ),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Codex 5.3 high."""
    _run_model_interactive(
        "high",
        provider=provider,
        resume=resume,
        prompt=prompt,
        cd=cd,
        print_mode=print_mode,
        debug=debug,
        add_dir=add_dir or None,
        output_format=output_format,
        continue_session=continue_session,
    )


@app.command("xhigh")
def clode_xhigh(
    provider: str | None = _provider_opt(),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(
        None, "--output-format", help="Output format when --print: text, json, stream-json"
    ),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Codex 5.3 xhigh."""
    _run_model_interactive(
        "xhigh",
        provider=provider,
        resume=resume,
        prompt=prompt,
        cd=cd,
        print_mode=print_mode,
        debug=debug,
        add_dir=add_dir or None,
        output_format=output_format,
        continue_session=continue_session,
    )


@app.command("free")
def clode_free(
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(
        None, "--output-format", help="Output format when --print: text, json, stream-json"
    ),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Base free tier: Copilot gpt-5-mini via cliproxy. Alias for clode mini."""
    _run_model_interactive(
        "mini",
        provider="copilot",
        resume=resume,
        prompt=prompt,
        cd=cd,
        print_mode=print_mode,
        debug=debug,
        add_dir=add_dir or None,
        output_format=output_format,
        continue_session=continue_session,
    )


app.command("ps")(ps_cmd)
app.command("logs")(logs_cmd)
app.command("status")(status_cmd)
app.command("stop")(stop_cmd)
app.command("wait")(wait_cmd)
app.command("inspect")(inspect_cmd)
app.command("history")(history_cmd)


@app.command("run")
def clode_run_global(
    model_alias: str = typer.Argument(
        ..., help="Model: dex, high, xhigh, comp, composer, max, glm, haiku, opus, opus1m, sonnet, step, flash, mini"
    ),
    prompt: str = typer.Argument(..., help="Task prompt"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    mode: str = typer.Option("write", "--mode", "-m", help="write | read-only"),
    timeout: int = typer.Option(90, "--timeout", "-t", help="Timeout in seconds"),
    remote: str | None = typer.Option(
        None,
        "--remote",
        help="Execute on remote node by hostname/IP (e.g. remote.example.com)",
    ),
) -> None:
    """Run a task via Claude Code. Model-first, no provider filter."""
    canonical = _MODEL_ALIAS.get(model_alias.lower(), model_alias)
    provider = _resolve_provider_for_model(model_alias)
    os.environ.update(_get_claude_env(provider, model_override=canonical))
    run_cmd(
        prompt=prompt,
        agent="interactive_agent",
        cd=cd,
        mode=mode,
        timeout=timeout,
        model=canonical,
        remote=remote,
    )


@app.command("bg")
def clode_bg_global(
    model_alias: str = typer.Argument(
        ..., help="Model: dex, high, xhigh, comp, composer, max, glm, haiku, opus, opus1m, sonnet, step, flash, mini"
    ),
    prompt: str = typer.Argument(..., help="Task prompt"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    mode: str = typer.Option("write", "--mode", "-m", help="write | read-only"),
    timeout: int = typer.Option(90, "--timeout", "-t", help="Timeout in seconds"),
    owner: str | None = typer.Option(None, "--owner", "-o", help="Owner tag"),
    remote: str | None = typer.Option(
        None,
        "--remote",
        help="Execute on remote node by hostname/IP (e.g. remote.example.com)",
    ),
) -> None:
    """Start a background task via Claude Code. Model-first, no provider filter."""
    canonical = _MODEL_ALIAS.get(model_alias.lower(), model_alias)
    provider = _resolve_provider_for_model(model_alias)
    os.environ.update(_get_claude_env(provider, model_override=canonical))
    bg_cmd(
        prompt=prompt,
        agent="interactive_agent",
        cd=cd,
        mode=mode,
        timeout=timeout,
        full=False,
        model=canonical,
        owner=owner,
        remote=remote,
    )


@app.command("glm")
def clode_glm(
    policy: str = typer.Option(
        "round_robin",
        "--policy",
        "-P",
        help="Routing policy: round_robin, cheapest, prefer_proxy, prefer_direct, failover",
    ),
    prefer: str = typer.Option(
        "auto",
        "--prefer",
        "-x",
        help="Backend lock: auto|nim|kilo|minimax|openrouter",
    ),
    force: bool = typer.Option(
        True,
        "--force",
        help="Pass through to Claude Code: skip permission prompts (default: True)",
    ),
    resume: str | None = typer.Option(
        None,
        "--resume",
        "-r",
        help="Pass through to Claude Code: resume session by ID",
    ),
    cd: Path | None = typer.Option(None, "--cd", "-C", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(
        None, "--output-format", help="Output format when --print: text, json, stream-json"
    ),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    model: str | None = typer.Option(None, "--model", help="Model override (glm-5, MiniMax-M2.5)"),
    prompt: str | None = typer.Argument(None, help="Startup prompt (interactive) or prompt for headless when -p used"),
) -> None:
    """Start an interactive GLM session with policy-based balancing."""
    token = _resolve_clode_token("glm", prefer=prefer, policy=policy)
    model = model or _CLODE_PROVIDER_MODEL.get(token, "MiniMax-M2.5")
    _run_model_interactive(
        model,
        provider=token,
        resume=resume,
        prompt=prompt,
        cd=cd,
        print_mode=print_mode,
        debug=debug,
        add_dir=add_dir or None,
        output_format=output_format,
        continue_session=continue_session,
    )


@app.command("max")
def clode_max(
    provider: str | None = _provider_opt(),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(
        None, "--output-format", help="Output format when --print: text, json, stream-json"
    ),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    force: bool = typer.Option(
        True,
        "--force",
        help="Pass through to Claude Code: skip permission prompts (default: True)",
    ),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """MiniMax-M2.5 balanced across minimax and kilo."""
    _run_model_interactive(
        "max",
        provider=provider,
        resume=resume,
        prompt=prompt,
        cd=cd,
        print_mode=print_mode,
        debug=debug,
        add_dir=add_dir or None,
        output_format=output_format,
        continue_session=continue_session,
    )


_SITBACK_STARTUP_PROMPT = """You are the Sitback Agent (THGENT_SITBACK=1): a lightweight orchestrator for thegent. You monitor terminals, sessions, and governance; present dashboards; and route tasks efficiently.

## Lifecycle

**Startup (now):**
1. Call thegent_sitback_dashboard (MCP) or run: thegent sitback-dashboard (CLI fallback).
2. Present the summary: sessions (N running, M failed), terminals (X panes, Y Claude Code), budget ($Z MTD).
3. Say: Sitback ready.
4. **Immediately begin the never-idle loop** (see below). Do not wait for user input.

**Operational:** Route user requests, attach to sessions, run/bg tasks; between requests, run the never-idle loop.
**Never idle:** When no user request, meander into gardening subprocesses (gov health, traceability, plan items, quality). Do not sit waiting.
**Shutdown:** No special action; user exits when done.

## Never-idle loop (run continuously)

There are **no push notifications** from thegent to the agent. Hooks run in the IDE context and do not notify the Sitback Agent. Session updates are written to run_registry.jsonl; you must **poll** to detect them.

**Pattern (never sit idle):**
1. **Check** — Call thegent_sitback_dashboard (or thegent_ps) to get current state.
2. **Manage** — If state changed (failures, drift, circuits) → summarize and optionally alert. If user asked "status" → present dashboard.
3. **Meander** — When no user request and no urgent session change: pick one gardening subprocess and run it. Rotate through:
   - `thegent govern go health` (8 dimensions)
   - `task quality` or spec-verifier; FR traceability
   - Read PLAN_STATUS.md, FR_TRACKER.md, docs/plans/
   - `thegent govern escalate list --past-sla`
   - Dispatch thegent_run/thegent_bg for failing dimensions or pending items
   - `task quality-a-r` until green
   - `thegent govern go cycle`
4. **Brief pause** — 30–60s between meander steps (or until user message). Then repeat.

**When to refresh immediately:** After thegent_run, thegent_bg, thegent_stop; when user says "status", "refresh", "what's running"; when you suspect state changed.

**Blocking on a specific session:** Use thegent_wait(session_id) when the user wants to wait for a bg run. Blocks until done or timeout; no polling needed for that run.

## Task flow

1. **Receive request** → Classify: run task, attach to session, status/dashboard, research, wait for session, other.
2. **Route decision:**
   - Run/bg: thegent_run or thegent_bg (MCP) or `thegent run`/`thegent bg` (CLI).
   - Attach to existing: thegent_terminal_attach or `thegent terminal attach`.
   - Status: thegent_sitback_dashboard or thegent_ps.
   - Wait for session: thegent_wait(session_id).
   - Research: thegent_ddg_search.
3. **Execute** → Call tool or CLI. On failure, try CLI fallback.
4. **Respond** → Verbose if user asked for detail; rich summary otherwise.
5. **Resume never-idle loop** — After responding, continue check → manage → meander.

## Role

- **Light terminal manager:** Prefer routing to existing sessions over spawning new ones. Use thegent_terminal_list to see panes; thegent_terminal_attach to send work.
- **Summarizer:** Full outputs when user needs detail; rich summaries for dashboard-style view.
- **Router:** thegent_run (sync), thegent_bg (async), thegent_terminal_attach (send to pane), thegent_wait (block on session).
- **Dashboard steward:** Re-run thegent_sitback_dashboard on request, after run/bg/stop, and in the never-idle loop.

## Tools (MCP first, CLI fallback)

Primary: thegent_sitback_dashboard, thegent_run, thegent_bg, thegent_ps, thegent_wait, thegent_do_next, thegent_terminal_list, thegent_terminal_inspect, thegent_terminal_send, thegent_terminal_attach, thegent_ddg_search, thegent_observe_summary.
CLI: thegent cockpit, thegent terminal list|inspect|attach, thegent ps, thegent wait, thegent sitback-dashboard, thegent run, thegent bg, thegent plan do-next.

## Output modes

- **Verbose:** Full tool output when user needs detail.
- **Rich:** Summarized tables and panels for dashboard view.
- **Structured:** Use structured_content from ToolResult when available.

## Fallbacks

- MCP unavailable → Use CLI: `thegent sitback-dashboard`, `thegent run`, `thegent bg`, `thegent wait`, `thegent plan do-next`, `thegent terminal list -a`, `thegent ps`.
- Tool error → Retry once; then CLI equivalent.
- Ambiguous request → Ask: "Run in background (bg) or wait for completion (run)?"
"""


def _run_sitback_claude(
    claude_path: str,
    env: dict[str, str],
    tmux: bool,
    startup_path: str | None = None,
) -> None:
    """Run Claude with startup prompt as positional arg in current terminal or tmux."""
    # WP-Y11: Human-driven runs get bypass by default; agent-triggered runs never do
    # Use model from env (provider-native: MiniMax-M2.5, glm-5)
    model = env.get("ANTHROPIC_MODEL", "MiniMax-M2.5")
    cmd = [claude_path, "--model", model]
    if not _is_triggered_by_agent_process():
        cmd.insert(1, _CLODE_BYPASS_FLAG)
    if startup_path:
        prompt = Path(startup_path).read_text()
        cmd.append(prompt)

    if tmux:
        session_name = f"sitback-{os.getpid()}"
        run_args = ["tmux", "new-session", "-s", session_name, *cmd]

        # Wrap with caffeinate to prevent sleep on macOS
        run_args = wrap_with_caffeinate(run_args, "claude")

        with contextlib.suppress(KeyboardInterrupt):
            shim_run(
                run_args,
                check=False,
                env=env,
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
    else:
        # Wrap with caffeinate to prevent sleep on macOS
        cmd = wrap_with_caffeinate(cmd, "claude")

        # WP-Y15: Use os.execvpe for native interactive experience (better signal handling)
        os.execvpe(cmd[0], cmd, env)


# Model aliases for sitback --model (claude and dex)
_SITBACK_MODEL_ALIAS: dict[str, str] = {
    "dex": "gpt-5.3-codex",
    "codex": "gpt-5.3-codex",
    "comp": "composer-1",
    "composer": "composer-1.5",
    "max": "minimax-m2.5",
    "m2.5": "minimax-m2.5",
    "glm": "glm-5",
    "glm5": "glm-5",
    "haiku": "claude-haiku-4.5",
    "opus": "claude-opus-4.6",
    "opus1m": "claude-opus-4.6-1m",
    "sonnet": "anthropic/claude-sonnet-4-20250514",
    "step": "step-3.5-flash",
    "flash": "gemini-3-flash",
    "high": "gpt-5.3-codex-high",
    "xhigh": "gpt-5.3-codex-xhigh",
    "mini": "gpt-5-mini",
    "free": "gpt-5-mini",
}
# Provider-native names for Claude Code (ANTHROPIC_MODEL)
_CLAUDE_NATIVE_MODEL: dict[str, str] = {
    "gpt-5.3-codex": "gpt-5.3-codex",
    "gpt-5.3-codex-high": "gpt-5.3-codex-high",
    "gpt-5.3-codex-xhigh": "gpt-5.3-codex-xhigh",
    "composer-1": "composer-1",
    "composer-1.5": "composer-1.5",
    "minimax-m2.5": "MiniMax-M2.5",
    "glm-5": "glm-5",
    "claude-haiku-4.5": "claude-haiku-4.5",
    "claude-opus-4.6": "claude-opus-4.6",
    "claude-opus-4.6-1m": "claude-opus-4.6-1m",
    "anthropic/claude-sonnet-4-20250514": "anthropic/claude-sonnet-4-20250514",
    "step-3.5-flash": "step-3.5-flash",
    "gemini-3-flash": "gemini-3-flash",
    "gpt-5-mini": "gpt-5-mini",
}


def _run_sitback_codex(
    model_alias: str,
    env: dict[str, str],
    tmux: bool,
    startup_path: str | None = None,
) -> None:
    """Run Codex with Sitback Agent persona."""
    from thegent.dex_main import _get_codex_env, _resolve_provider_for_model

    canonical = _SITBACK_MODEL_ALIAS.get(model_alias.lower(), model_alias)
    provider = _resolve_provider_for_model(model_alias)
    codex_env = _get_codex_env(provider, canonical)
    codex_env.update(env)

    codex_path = shutil.which("codex")
    if not codex_path:
        local = Path.home() / ".local" / "bin" / "codex"
        codex_path = str(local) if local.exists() else None
    if not codex_path:
        console.print("[red]Error: 'codex' CLI not found in PATH.[/red]")
        console.print("[dim]Install it via: npm i -g @openai/codex[/dim]")
        raise typer.Exit(1)

    cmd = [codex_path]
    if not _is_triggered_by_agent_process():
        cmd.extend([_SITBACK_CLODE_YOLO_FLAG, _SITBACK_CLODE_BYPASS_FLAG])
    cmd.extend(["--model", canonical])
    if startup_path:
        cmd.append(Path(startup_path).read_text())

    if tmux:
        session_name = f"sitback-dex-{os.getpid()}"
        run_args = ["tmux", "new-session", "-s", session_name, *cmd]
        # Wrap with caffeinate for macOS
        run_args = wrap_with_caffeinate(run_args, "codex")
        with contextlib.suppress(KeyboardInterrupt):
            shim_run(run_args, check=False, env=codex_env, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    else:
        # Wrap with caffeinate for macOS
        cmd = wrap_with_caffeinate(cmd, "codex")
        os.execvpe(cmd[0], cmd, codex_env)


def _run_sitback_droid(
    model_alias: str,
    env: dict[str, str],
    tmux: bool,
    startup_path: str | None = None,
) -> None:
    """Run Factory Droid with Sitback Agent persona."""
    canonical = _SITBACK_MODEL_ALIAS.get(model_alias.lower(), model_alias)
    droid_path = shutil.which("droid")
    if not droid_path:
        local = Path.home() / ".local" / "bin" / "droid"
        droid_path = str(local) if local.exists() else None
    if not droid_path:
        console.print("[red]Error: 'droid' CLI not found in PATH.[/red]")
        console.print("[dim]Install it via: curl -fsSL https://app.factory.ai/Union[cli, sh][/dim]")
        raise typer.Exit(1)

    cmd = [droid_path, "--model", canonical]
    if startup_path:
        cmd.append(Path(startup_path).read_text())

    if tmux:
        session_name = f"sitback-droid-{os.getpid()}"
        run_args = ["tmux", "new-session", "-s", session_name, *cmd]
        # Wrap with caffeinate for macOS
        run_args = wrap_with_caffeinate(run_args, "droid")
        with contextlib.suppress(KeyboardInterrupt):
            shim_run(run_args, check=False, env=env, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    else:
        # Wrap with caffeinate for macOS
        cmd = wrap_with_caffeinate(cmd, "droid")
        os.execvpe(cmd[0], cmd, env)


def _run_sitback_anen(
    model_alias: str,
    env: dict[str, str],
    tmux: bool = False,
    startup_path: str | None = None,
) -> None:
    canonical = _SITBACK_MODEL_ALIAS.get(model_alias.lower(), model_alias)
    resolved_bin_name = ""
    anen_path = None
    for bin_name in ("fanta", "antigma", "anen", "ante"):
        resolved = shutil.which(bin_name)
        if resolved:
            anen_path = resolved
            resolved_bin_name = bin_name
            break
        local = Path.home() / ".local" / "bin" / bin_name
        if local.exists():
            anen_path = str(local)
            resolved_bin_name = bin_name
            break
    if not anen_path:
        console.print("[red]Error: none of 'fanta', 'antigma', 'anen', or 'ante' found in PATH.[/red]")
        raise typer.Exit(1)

    cmd = [anen_path, "--model", canonical]
    if startup_path:
        startup_prompt = Path(startup_path).read_text()
        if resolved_bin_name in {"fanta", "antigma", "ante"}:
            cmd.extend(["--prompt", startup_prompt])
        else:
            # anen harness expects startup prompt as positional argument.
            cmd.append(startup_prompt)

    if tmux:
        session_name = f"sitback-anen-{os.getpid()}"
        run_args = ["tmux", "new-session", "-s", session_name, *cmd]
        run_args = wrap_with_caffeinate(run_args, "anen")
        with contextlib.suppress(KeyboardInterrupt):
            shim_run(run_args, check=False, env=env, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    else:
        cmd = wrap_with_caffeinate(cmd, "anen")
        os.execvpe(cmd[0], cmd, env)


def sitback_cmd(
    agent: str = typer.Option(
        "claude",
        "--agent",
        "-a",
        help="Harness: claude (default), codex, droid, antigma. Aliases: clode, dex, roid, anen, fanta.",
    ),
    provider: str | None = typer.Option(
        None,
        "--provider",
        "-P",
        help="Optional backend provider for claude harness (e.g. nim, kilo, minimax, glm, openrouter).",
    ),
    model: str | None = typer.Option(
        None,
        "--model",
        "-M",
        help="Shared model alias: dex, high, xhigh, composer, max, glm, haiku, opus, sonnet, step, flash, mini, free.",
    ),
    dex: bool = typer.Option(
        False,
        "--dex",
        "-x",
        help="Deprecated alias for --agent codex.",
    ),
    cd: Path | None = typer.Option(
        None,
        "--cd",
        "-d",
        help="Working directory (default: cwd)",
    ),
    skill: str | None = typer.Option(
        None,
        "--skill",
        "-s",
        help="Override skill: sitback-agent (default), thegent-skills, or custom name",
    ),
    profile: str = typer.Option(
        "medium",
        "--profile",
        "-p",
        help="Dashboard tier: light, medium (default), full",
    ),
    tmux: bool = typer.Option(
        False,
        "--tmux",
        "-t",
        help="Run inside a dedicated tmux session (tmux-native mode)",
    ),
    no_dashboard: bool = typer.Option(
        False,
        "--no-dashboard",
        help="Skip auto-dashboard on startup (manual mode)",
    ),
    tui: bool = typer.Option(
        False,
        "--tui",
        "-u",
        help="Launch TUI compositor instead of dashboard",
    ),
) -> None:
    """Start a Sitback harness (claude/codex/droid/antigma) with Sitback Agent persona.

    Examples:
      thegent sitback                    # claude harness, flash model
      thegent sitback -a codex -M glm    # codex harness with GLM-5
      thegent sitback -a droid -M free   # droid harness with gpt-5-mini
      thegent sitback -a fanta -M max    # antigma harness with MiniMax-M2.5
      thegent sitback -M haiku -P kiro   # claude harness with provider override
      thegent sitback --skill thegent-skills
      thegent sitback --profile full
      thegent sitback --tmux
      thegent sitback --no-dashboard
      thegent sitback --tui             # Launch TUI compositor
    """
    harness_aliases = {
        "claude": "claude",
        "clode": "claude",
        "codex": "codex",
        "dex": "codex",
        "droid": "droid",
        "roid": "droid",
        "antigma": "antigma",
        "anen": "antigma",
        "fanta": "antigma",
    }
    resolved_harness = harness_aliases.get(agent.strip().lower())
    if resolved_harness is None:
        console.print(
            "[red]Invalid --agent. Allowed: claude, codex, droid, antigma (aliases: clode, dex, roid, anen, fanta).[/red]"
        )
        raise typer.Exit(1)
    if dex:
        resolved_harness = "codex"

    valid_profiles = ("light", "medium", "full")
    prof = profile.strip().lower() if profile else "medium"
    if prof not in valid_profiles:
        console.print(f"[red]Invalid profile '{profile}'. Allowed: {', '.join(valid_profiles)}[/red]")
        raise typer.Exit(1)

    default_model = "dex" if resolved_harness == "codex" else "flash"
    model_alias = (model or default_model).strip().lower()
    canonical = _SITBACK_MODEL_ALIAS.get(model_alias, model_alias)
    env = os.environ.copy()
    env["THGENT_SITBACK"] = "1"
    env["THGENT_SITBACK_AGENT"] = resolved_harness
    env["THGENT_SITBACK_PROFILE"] = prof
    if skill is not None:
        env["THGENT_SITBACK_SKILL"] = skill.strip()
    if tmux:
        env["THGENT_SITBACK_TMUX"] = "1"
    if no_dashboard:
        env["THGENT_SITBACK_NO_DASHBOARD"] = "1"
    if cd is not None:
        env["THGENT_SITBACK_CD"] = str(cd.resolve())

    if resolved_harness == "claude":
        provider_token = provider.strip().lower() if provider else _resolve_provider_for_model(model_alias)
        model_override = _CLAUDE_NATIVE_MODEL.get(canonical, canonical)
        env.update(_get_claude_env(provider_token, model_override=model_override))
        config_dir = Path(env["CLAUDE_CONFIG_DIR"])
        _ensure_claude_config_isolation(config_dir)

    # MCP precondition: ask when server not reachable (Sitback uses FastMCP tools)
    settings = _get_settings()
    try:
        import httpx

        health_url = f"http://{settings.mcp_host}:{settings.mcp_port}/health"
        resp = httpx.get(health_url, timeout=2)
        if not resp.is_success:
            raise RuntimeError("MCP not reachable")
    except Exception:
        console.print("[yellow]MCP server not reachable. Start with: thegent serve (or thegent mcp up)[/yellow]")
        console.print("[dim]Sitback will fall back to CLI (cockpit, terminal list, ps).[/dim]")
        if not typer.confirm("Start Sitback anyway?", default=False):
            raise typer.Exit(0)
        console.print()

    if resolved_harness == "codex":
        console.print(f"[bold green]Starting Sitback Agent via Codex (model={model_alias})...[/bold green]")
    elif resolved_harness == "droid":
        console.print(f"[bold green]Starting Sitback Agent via Droid (model={model_alias})...[/bold green]")
    elif resolved_harness == "antigma":
        console.print(f"[bold green]Starting Sitback Agent via Antigma (model={model_alias})...[/bold green]")
    else:
        claude_path = _ensure_claude_installed(suggest_dex=True)
        console.print(f"[bold green]Starting Sitback Agent via Claude (provider={provider_token})...[/bold green]")

    startup_prompt = _SITBACK_STARTUP_PROMPT
    try:
        from thegent.sitback_plugins import get_registry

        for step in get_registry().get_startup_steps():
            startup_prompt += "\n" + step
    except Exception:
        pass

    if no_dashboard:
        console.print("[dim]Manual mode: no startup prompt injected.[/dim]")
        if resolved_harness == "codex":
            _run_sitback_codex(model_alias, env, tmux)
        elif resolved_harness == "droid":
            _run_sitback_droid(model_alias, env, tmux)
        elif resolved_harness == "antigma":
            _run_sitback_anen(model_alias, env, tmux)
        else:
            _run_sitback_claude(claude_path, env, tmux)
        return

    if tui:
        console.print("[bold green]Launching TUI Compositor...[/bold green]")
        import asyncio
        from pathlib import Path as PathCls

        from thegent.tui.compositor import run_tui

        session_id = f"sitback-{resolved_harness}"
        cwd = str(cd.resolve()) if cd else str(PathCls.cwd())

        async def launch_tui():
            await run_tui(
                session_id=session_id,
                agent_name=f"sitback-{resolved_harness}",
                cwd=PathCls(cwd),
                headless=False,
            )

        try:
            asyncio.run(launch_tui())
        except KeyboardInterrupt:
            console.print("[dim]TUI compositor closed.[/dim]")
        except Exception as e:
            console.print(f"[red]Error launching TUI: {e}[/red]")
        return

    # Phase 2: Startup prompt injection — try stdin first, always show paste fallback
    console.print("[dim]Injecting startup prompt as positional argument...[/dim]")
    if resolved_harness == "codex":
        client_name = "Codex"
    elif resolved_harness == "droid":
        client_name = "Droid"
    elif resolved_harness == "antigma":
        client_name = "Antigma"
    else:
        client_name = "Claude Code"
    console.print(f"[dim]{client_name} will process this as the first message in the session.[/dim]\n")
    console.print("[yellow]Fallback (copy/paste if needed):[/yellow]")
    console.print("[bold]--- Startup Prompt ---[/bold]")
    console.print(startup_prompt)
    console.print("[bold]--- End Prompt ---[/bold]\n")

    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(startup_prompt + "\n")
        tmp_path = f.name
    try:
        if resolved_harness == "codex":
            _run_sitback_codex(model_alias, env, tmux, startup_path=tmp_path)
        elif resolved_harness == "droid":
            _run_sitback_droid(model_alias, env, tmux, startup_path=tmp_path)
        elif resolved_harness == "antigma":
            _run_sitback_anen(model_alias, env, tmux, startup_path=tmp_path)
        else:
            _run_sitback_claude(claude_path, env, tmux, startup_path=tmp_path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            Path(tmp_path).unlink()


@app.command("doctor")
def clode_doctor(
    fix: bool = typer.Option(False, "--fix", "-f", help="Attempt to fix issues"),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-n", help="Show what fixes would be applied without making changes"
    ),
) -> None:
    """Run thegent doctor (harness-equiv)."""
    import sys

    from thegent.doctor import run_doctor

    success = run_doctor(fix=fix, dry_run=dry_run)
    sys.exit(0 if success else 1)


@app.command("config")
def clode_config(
    legacy: bool = typer.Option(
        False,
        "--legacy",
        help="Use legacy provider form instead of the interactive TUI translation layer.",
    ),
) -> None:
    """Open interactive config manager (translation layer for existing config backends)."""
    if legacy:
        from thegent.provider_model_manager import run_provider_form

        run_provider_form()
        return

    from thegent.ux.models_providers_tui import run_models_providers_tui

    run_models_providers_tui()


@app.command("install-links")
def install_links(
    bin_dir: Path = typer.Option(
        Path.home() / ".local" / "bin",
        "--bin-dir",
        help="Directory to install harness shim symlink",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
) -> None:
    """Install/update clode harness aliases -> thegent-shims under ~/.local/bin."""
    if not bin_dir.exists():
        from thegent.errors import print_error

        print_error(f"{bin_dir} does not exist.")
        raise typer.Exit(1)

    harness_aliases = ("clode", "roid", "droid", "fanta", "anen")
    for harness in harness_aliases:
        if _install_harness_link(bin_dir, harness, force=force):
            console.print(f"[green]Installed[/green] {bin_dir / harness} -> thegent-shims")
            continue
        console.print(f"[yellow]Skipping {bin_dir / harness} (already exists). Use --force to overwrite.[/yellow]")


if __name__ == "__main__":
    app()
