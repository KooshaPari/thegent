"""Execution helpers for clode CLI.

Split from clode_main.py for maintainability. Contains provider resolution,
environment setup, and Claude Code execution functions.
"""

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
    if provider in ("glm", "auto") or settings.sitback:
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

