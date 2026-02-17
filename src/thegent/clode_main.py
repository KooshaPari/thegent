"""Claude-backed interactive agent CLI (clode)."""

import contextlib
import json
import os
import shutil
import subprocess
import sys
from collections import Counter
from collections.abc import Iterator
from pathlib import Path

import typer
from rich.console import Console

# Import thegent CLI commands to reuse them.
# Lazy imports used in commands to speed up CLI startup.
from thegent.cli import bg_cmd, history_cmd, inspect_cmd, logs_cmd, ps_cmd, run_cmd, status_cmd, stop_cmd, wait_cmd
from thegent.agents.cliproxy_manager import fetch_provider_metrics
def _is_triggered_by_agent_process():
    from thegent.discovery import _is_triggered_by_agent_process as impl
    return impl()

# Lazy imports for better startup performance
def _get_settings():
    from thegent.config import ThegentSettings
    return ThegentSettings()

class LazyConsole:
    def __getattr__(self, name):
        from rich.console import Console
        global console
        console = Console()
        return getattr(console, name)

console = LazyConsole()
app = typer.Typer(help="Claude-backed interactive agent CLI (clode)")

_GLM_OFFER_SET: tuple[str, ...] = ("nim", "kilo", "minimax", "glm")
_GLM_OFFER_COST: dict[str, float] = {
    "nim": 0.22,
    "kilo": 0.28,
    "minimax": 0.36,
    "glm": 0.80,
}

# Model-first aliases: pick model → auto-balance across providers
_MODEL_ALIAS: dict[str, str] = {
    "composer": "composer-1.5",
    "haiku": "claude-haiku-4.5",
    "opus": "claude-opus-4.6",
    "sonnet": "anthropic/claude-sonnet-4",
    "glm": "glm-5",
    "glm5": "glm-5",
    "max": "minimax-m2.5",
    "m2.5": "minimax-m2.5",
    "step": "step-3.5-flash",
    "flash": "gemini-3-flash",
    "mini": "gpt-5-mini",
}
_MODEL_PROVIDER_SETS: dict[str, tuple[str, ...]] = {
    "composer-1.5": ("cursor",),
    "glm-5": ("glm", "kilo", "nim", "minimax"),
    "minimax-m2.5": ("minimax", "kilo"),
    "claude-haiku-4.5": ("claude", "antigravity", "codex", "kiro"),
    "claude-opus-4.6": ("claude", "antigravity", "kiro"),
    "anthropic/claude-sonnet-4": ("openrouter",),
    "step-3.5-flash": ("nim",),
    "gemini-3-flash": ("gemini",),
    "gpt-5-mini": ("copilot",),
}
_MODEL_COUNTER: Counter[str] = Counter()


_GLM_PREFERRED_BACKENDS: frozenset[str] = frozenset({"glm", "kilo", "nim", "minimax", "openrouter"})
_GLM_POLICY_COUNTER: Counter[str] = Counter()


def _glm_offer_backends() -> tuple[str, ...]:
    """Return GLM offer set in deterministic order."""
    return _GLM_OFFER_SET


@app.callback(invoke_without_command=True)
def default_clode(ctx: typer.Context) -> None:
    """Start Claude Code with model-first routing. Default: flash (Gemini 3 Flash)."""
    if ctx.invoked_subcommand is None:
        _run_model_interactive("flash")


def _iter_install_targets() -> Iterator[tuple[str, str, str]]:
    """Return shim targets and their backing commands."""
    yield ("clode", "thegent clode", "clode")
    yield ("clodecomposer", "thegent clode composer", "clodecomposer")
    yield ("clodehaiku", "thegent clode haiku", "clodehaiku")
    yield ("clodeopus", "thegent clode opus", "clodeopus")
    yield ("clodesonnet", "thegent clode sonnet", "clodesonnet")
    yield ("clodeglm", "thegent clode glm", "clodeglm")
    yield ("clodemax", "thegent clode max", "clodemax")
    yield ("clodeflash", "thegent clode flash", "clodeflash")
    yield ("clodemini", "thegent clode mini", "clodemini")
    yield ("clodefree", "thegent clode free", "clodefree")
    yield ("claudeglm", "thegent clode glm", "claudeglm")
    yield ("claudemax", "thegent clode max", "claudemax")


def _resolve_provider_for_model(model_alias: str) -> str:
    """Resolve provider for model-first routing. Round-robin across available providers."""
    canonical = _MODEL_ALIAS.get(model_alias.lower(), model_alias)
    providers = _MODEL_PROVIDER_SETS.get(canonical)
    if not providers:
        return "nim"  # fallback
    idx = _MODEL_COUNTER[canonical]
    selected = providers[idx % len(providers)]
    _MODEL_COUNTER[canonical] = (idx + 1) % len(providers)
    return selected


def _validate_policy(policy: str) -> str:
    normalized = (policy or "round_robin").strip().lower()
    allowed = {"round_robin", "cheapest", "prefer_proxy", "prefer_direct", "failover"}
    if normalized not in allowed:
        console.print(
            "[red]Invalid policy. Allowed: round_robin | cheapest | prefer_proxy | prefer_direct | failover.[/red]"
        )
        raise typer.Exit(1)
    return normalized


def _resolve_clode_token(provider: str, prefer: str, policy: str) -> str:
    """Resolve provider token for ANTHROPIC_API_KEY."""
    prefer_auth = (prefer or "auto").strip().lower()
    policy_name = _validate_policy(policy)

    if provider != "glm":
        return provider
    if prefer_auth in _GLM_PREFERRED_BACKENDS:
        return prefer_auth
    if policy_name == "round_robin":
        idx = _GLM_POLICY_COUNTER[provider]
        backends = _glm_offer_backends()
        selected_backend = backends[idx % len(backends)]
        _GLM_POLICY_COUNTER[provider] = (idx + 1) % len(_GLM_OFFER_SET)
        return selected_backend
    if policy_name == "cheapest":
        metrics = fetch_provider_metrics()
        backends = _glm_offer_backends()

        def cost_key(b: str) -> tuple[float, float, str]:
            fallback = _GLM_OFFER_COST.get(b, 999.0)
            m = (metrics or {}).get(b, {})
            cost = m.get("cost_per_1k_output") or m.get("cost_per_1k_input")
            if cost is None or cost <= 0:
                cost = fallback
            sr = m.get("success_rate", 1.0)
            return (cost, -sr, b)

        return min(backends, key=cost_key)
    return f"glm:{policy_name}"


def _write_wrapper(path: Path, command: str, force: bool = False) -> bool:
    """Write/update a shim wrapper. Returns True if a write occurred."""
    if path.exists() and not force:
        return False

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'#!/usr/bin/env sh\nset -e\nexec {command} "$@"\n')
    path.chmod(0o755)
    return True


# Model -> providers. Align with catalog and CLIProxyAPIPlus.
# NIM (NVIDIA NIM) provides glm-5 and step-3.5-flash, NOT minimax.
_MODEL_PROVIDERS: dict[str, tuple[str, ...]] = {
    "minimax-m2.5": ("minimax", "kilo"),
    "deepseek-v3.2": ("kilo", "nim"),
    "glm-5": ("glm", "kilo", "nim"),
    "step-3.5-flash": ("nim",),
    "claude-haiku-4.5": ("claude", "antigravity", "codex", "kiro"),
    "claude-opus-4.6": ("claude", "antigravity", "kiro"),
    "anthropic/claude-sonnet-4": ("openrouter",),
}


def _model_for_provider(provider: str) -> str:
    """Default model for a provider (derived from model->provider mapping)."""
    if provider == "kiro":
        return "claude-haiku-4.5"
    for model, providers in _MODEL_PROVIDERS.items():
        if provider in providers:
            return model
    return "minimax-m2.5"


# Provider-native model names. NIM serves glm-5 and step-3.5-flash, not MiniMax.
# free = copilot gpt-5-mini (base free tier). flash = gemini-3-flash.
_CLODE_PROVIDER_MODEL: dict[str, str] = {
    "cursor": "composer-1.5",
    "nim": "glm-5",
    "minimax": "MiniMax-M2.5",
    "kilo": "MiniMax-M2.5",
    "glm": "glm-5",
    "openrouter": "anthropic/claude-sonnet-4",
    "copilot": "gpt-5-mini",
    "gemini": "gemini-3-flash",
}


def _ensure_claude_config_isolation(config_dir: Path) -> None:
    """Ensure isolated config dir has links to global state to skip onboarding and persist sessions."""
    global_dir = Path.home() / ".claude"
    global_json = Path.home() / ".claude.json"

    # 1. Onboarding state (~/.claude.json)
    target_json = config_dir / ".claude.json"
    if global_json.exists() and not target_json.exists():
        try:
            target_json.symlink_to(global_json)
        except OSError:
            pass

    if global_dir.exists():
        # 2. Settings (Copy to isolate auth, but keep theme/permissions)
        target_settings = config_dir / "settings.json"
        if not target_settings.exists():
            global_settings = global_dir / "settings.json"
            if global_settings.exists():
                try:
                    import json
                    data = json.loads(global_settings.read_text())
                    target_settings.write_text(json.dumps(data, indent=2))
                except Exception:
                    pass

        # 3. All other state in ~/.claude/ (tasks, todos, projects, session-env, history, etc.)
        for item in global_dir.iterdir():
            if item.name == "settings.json":
                continue
            target = config_dir / item.name
            # If target exists and is NOT a symlink, it might be a partial state Claude created.
            # Wipe it so we can link the real global state.
            if target.exists() and not target.is_symlink():
                try:
                    if target.is_dir():
                        shutil.rmtree(target)
                    else:
                        target.unlink()
                except OSError:
                    pass
            
            if not target.exists():
                try:
                    target.symlink_to(item, target_is_directory=item.is_dir())
                except OSError:
                    pass


def _get_claude_env(provider: str, model_override: str | None = None) -> dict[str, str]:
    """Get environment variables for Claude Code pointing to thegent proxy.

    Aligns with Minimax docs (platform.minimax.io/docs/coding-plan/claude-code) and
    z.ai docs (docs.z.ai/devpack/tool/claude): use provider-native model names
    (MiniMax-M2.5, glm-5) so the model "turns into" the provider correctly.
    No Claude ID mapping needed.
    """
    settings = ThegentSettings()
    
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
    if provider == "glm" or os.environ.get("THGENT_SITBACK") == "1":
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
    """Build extra args for claude from passthrough options."""
    args: list[str] = []
    if cd:
        args.extend(["--add-dir", str(cd.resolve())])
    if debug:
        args.append("--debug")
    if add_dir:
        for d in add_dir:
            args.extend(["--add-dir", d])
    if output_format:
        args.extend(["--output-format", output_format])
    if continue_session:
        args.append("--continue")
    return args


def _find_claude() -> str | None:
    """Return path to claude CLI, or None. Checks PATH and common install dirs."""
    p = shutil.which("claude")
    if p:
        return p
    for d in ("/opt/homebrew/bin", "/usr/local/bin", os.path.expanduser("~/.bun/bin")):
        cand = os.path.join(d, "claude")
        if os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand
    return None


def _ensure_claude_installed(suggest_dex: bool = False) -> str:
    """Auto-install Claude Code via brew or bun if missing. Returns path or raises."""
    p = _find_claude()
    if p:
        return p
    # Try brew first
    brew = shutil.which("brew")
    if brew:
        console.print("[dim]Installing Claude Code via Homebrew...[/dim]")
        r = subprocess.run([brew, "install", "--cask", "claude-code"], capture_output=True, text=True)
        if r.returncode == 0:
            p = _find_claude()
            if p:
                return p
    # Try bun
    bun = shutil.which("bun")
    if bun:
        console.print("[dim]Installing Claude Code via Bun...[/dim]")
        r = subprocess.run([bun, "install", "-g", "@anthropic-ai/claude-code"], capture_output=True, text=True)
        if r.returncode == 0:
            p = _find_claude()
            if p:
                return p
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
    env = _get_claude_env(provider, model_override=model_override)
    _ensure_claude_config_isolation(Path(env["CLAUDE_CONFIG_DIR"]))

    claude_path = _ensure_claude_installed()

    cmd = [claude_path, "-p", prompt]
    if not _is_triggered_by_agent_process():
        cmd.insert(1, "--dangerously-skip-permissions")
    extra = _clode_passthrough_args(cd=cd, add_dir=add_dir, output_format=output_format)
    for arg in extra:
        cmd.append(arg)

    if cd:
        os.chdir(cd)
    console.print(f"[bold green]Claude print (headless) via {provider}...[/bold green]")
    os.execvpe(cmd[0], cmd, env)


def _run_claude_interactive(
    provider: str,
    extra_args: list[str] | None = None,
    model_override: str | None = None,
) -> None:
    """Start an interactive Claude Code session."""
    # Pre-flight: check if provider is configured in cliproxy
    settings = ThegentSettings()
    config_path = settings.cliproxy_config_path.expanduser().resolve()
    if config_path.exists():
        import yaml
        try:
            config = yaml.safe_load(config_path.read_text())
            if isinstance(config, dict):
                from thegent.agents.cliproxy_manager import _has_provider_credentials, _LOGIN_FLAGS
                is_configured = _has_provider_credentials(config, provider) or provider in _LOGIN_FLAGS
                if not is_configured:
                    console.print(f"[yellow]Warning: Provider '{provider}' may not be configured in cliproxy.[/yellow]")
                    console.print(f"[dim]Run: thegent cliproxy login {provider}[/dim]\n")
        except Exception:
            pass

    env = _get_claude_env(provider, model_override=model_override)
    
    _ensure_claude_config_isolation(Path(env["CLAUDE_CONFIG_DIR"]))

    claude_path = _ensure_claude_installed()

    console.print(f"[bold green]Starting interactive Claude session via {provider} proxy...[/bold green]")
    console.print(f"[dim]Proxy URL: {env['ANTHROPIC_BASE_URL']}[/dim]")
    # WP-Y11: Human-driven runs get bypass by default; agent-triggered runs never do
    cmd = [claude_path]
    if not _is_triggered_by_agent_process():
        cmd.append("--dangerously-skip-permissions")
    if extra_args:
        for arg in extra_args:
            if arg != "--dangerously-skip-permissions":
                cmd.append(arg)

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
                extra.append("--dangerously-skip-permissions")
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
        session_ids: list[str] = typer.Argument(default=[], help="Session ID(s). Use --owner to inspect all for owner."),
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
        extra.append("--dangerously-skip-permissions")
    extra.extend(_clode_passthrough_args(cd=cd, debug=debug, add_dir=add_dir, output_format=output_format, continue_session=continue_session))
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


@app.command("composer")
def clode_composer(
    provider: str | None = _provider_opt(),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(None, "--output-format", help="Output format when --print: text, json, stream-json"),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Composer 1.5 (via Cursor). Use -x cursor to lock."""
    _run_model_interactive("composer", provider=provider, resume=resume, prompt=prompt, cd=cd, print_mode=print_mode, debug=debug, add_dir=add_dir or None, output_format=output_format, continue_session=continue_session)


@app.command("haiku")
def clode_haiku(
    provider: str | None = _provider_opt(),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(None, "--output-format", help="Output format when --print: text, json, stream-json"),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Claude Haiku 4.5 balanced across claude, antigravity, codex (proxy API), kiro."""
    _run_model_interactive("haiku", provider=provider, resume=resume, prompt=prompt, cd=cd, print_mode=print_mode, debug=debug, add_dir=add_dir or None, output_format=output_format, continue_session=continue_session)


@app.command("opus")
def clode_opus(
    provider: str | None = _provider_opt(),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(None, "--output-format", help="Output format when --print: text, json, stream-json"),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Claude Opus 4.6 balanced across claude, antigravity, kiro."""
    _run_model_interactive("opus", provider=provider, resume=resume, prompt=prompt, cd=cd, print_mode=print_mode, debug=debug, add_dir=add_dir or None, output_format=output_format, continue_session=continue_session)


@app.command("sonnet")
def clode_sonnet(
    provider: str | None = _provider_opt(),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(None, "--output-format", help="Output format when --print: text, json, stream-json"),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Claude Sonnet 4.5 via OpenRouter."""
    _run_model_interactive("sonnet", provider=provider, resume=resume, prompt=prompt, cd=cd, print_mode=print_mode, debug=debug, add_dir=add_dir or None, output_format=output_format, continue_session=continue_session)


@app.command("step")
def clode_step(
    provider: str | None = _provider_opt(),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(None, "--output-format", help="Output format when --print: text, json, stream-json"),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Step 3.5 Flash via NIM. Fast, cheap."""
    _run_model_interactive("step", provider=provider, resume=resume, prompt=prompt, cd=cd, print_mode=print_mode, debug=debug, add_dir=add_dir or None, output_format=output_format, continue_session=continue_session)


@app.command("flash")
def clode_flash(
    provider: str | None = _provider_opt(),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(None, "--output-format", help="Output format when --print: text, json, stream-json"),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Gemini 3 Flash via cliproxy. Fast, cheap."""
    _run_model_interactive("flash", provider=provider, resume=resume, prompt=prompt, cd=cd, print_mode=print_mode, debug=debug, add_dir=add_dir or None, output_format=output_format, continue_session=continue_session)


@app.command("mini")
def clode_mini(
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(None, "--output-format", help="Output format when --print: text, json, stream-json"),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """GPT-5 mini / Copilot (free tier). Alias for clode free."""
    _run_model_interactive("mini", provider="copilot", resume=resume, prompt=prompt, cd=cd, print_mode=print_mode, debug=debug, add_dir=add_dir or None, output_format=output_format, continue_session=continue_session)


@app.command("free")
def clode_free(
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(None, "--output-format", help="Output format when --print: text, json, stream-json"),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Base free tier: Copilot gpt-5-mini via cliproxy. Alias for clode mini."""
    _run_model_interactive("mini", provider="copilot", resume=resume, prompt=prompt, cd=cd, print_mode=print_mode, debug=debug, add_dir=add_dir or None, output_format=output_format, continue_session=continue_session)


app.command("ps")(ps_cmd)
app.command("logs")(logs_cmd)
app.command("status")(status_cmd)
app.command("stop")(stop_cmd)
app.command("wait")(wait_cmd)
app.command("inspect")(inspect_cmd)
app.command("history")(history_cmd)


@app.command("run")
def clode_run_global(
    model_alias: str = typer.Argument(..., help="Model: composer, max, glm, haiku, opus, sonnet, step, flash, mini"),
    prompt: str = typer.Argument(..., help="Task prompt"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    mode: str = typer.Option("write", "--mode", "-m", help="write | read-only"),
    timeout: int = typer.Option(90, "--timeout", "-t", help="Timeout in seconds"),
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
    )


@app.command("bg")
def clode_bg_global(
    model_alias: str = typer.Argument(..., help="Model: composer, max, glm, haiku, opus, sonnet, step, flash, mini"),
    prompt: str = typer.Argument(..., help="Task prompt"),
    cd: Path | None = typer.Option(None, "--cd", "-C", "-d", help="Working directory"),
    mode: str = typer.Option("write", "--mode", "-m", help="write | read-only"),
    timeout: int = typer.Option(90, "--timeout", "-t", help="Timeout in seconds"),
    owner: str | None = typer.Option(None, "--owner", "-o", help="Owner tag"),
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
    )


def _free_extra_args(resume: str | None, prompt: str | None) -> list[str]:
    args: list[str] = []
    if not _is_triggered_by_agent_process():
        args.append("--dangerously-skip-permissions")
    if resume:
        args.extend(["--resume", resume])
    if prompt:
        args.append(prompt)
    return args


@app.command("glm")
def clode_glm(
    policy: str = typer.Option(
        "round_robin",
        "--policy",
        "-p",
        help="Routing policy: round_robin, cheapest, prefer_proxy, prefer_direct, failover",
    ),
    prefer: str = typer.Option(
        "auto",
        "--prefer",
        "-x",
        help="Backend lock: auto|nim|kilo|minimax|openrouter",
    ),
    dangerously_skip_permissions: bool = typer.Option(
        True,
        "--dangerously-skip-permissions",
        help="Pass through to Claude Code: skip permission prompts (default: True)",
    ),
    resume: str | None = typer.Option(
        None,
        "--resume",
        "-r",
        help="Pass through to Claude Code: resume session by ID",
    ),
    cd: Path | None = typer.Option(None, "--cd", "-C", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(None, "--output-format", help="Output format when --print: text, json, stream-json"),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    model: str | None = typer.Option(None, "--model", help="Model override (glm-5, MiniMax-M2.5)"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """Start an interactive GLM session with policy-based balancing."""
    token = _resolve_clode_token("glm", prefer=prefer, policy=policy)
    model = model or _CLODE_PROVIDER_MODEL.get(token, "MiniMax-M2.5")
    _run_model_interactive(model, provider=token, resume=resume, prompt=prompt, cd=cd, print_mode=print_mode, debug=debug, add_dir=add_dir or None, output_format=output_format, continue_session=continue_session)


@app.command("max")
def clode_max(
    provider: str | None = _provider_opt(),
    resume: str | None = typer.Option(None, "--resume", "-r", help="Resume session by ID"),
    cd: Path | None = typer.Option(None, "--cd", "-C", help="Working directory"),
    print_mode: bool = typer.Option(False, "--print", "-p", help="Headless: print response and exit"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    add_dir: list[str] = typer.Option([], "--add-dir", help="Additional directories (repeatable)"),
    output_format: str | None = typer.Option(None, "--output-format", help="Output format when --print: text, json, stream-json"),
    continue_session: bool = typer.Option(False, "--continue", "-c", help="Continue most recent conversation"),
    prompt: str | None = typer.Argument(None, help="Startup prompt"),
) -> None:
    """MiniMax-M2.5 balanced across minimax and kilo."""
    _run_model_interactive("max", provider=provider, resume=resume, prompt=prompt, cd=cd, print_mode=print_mode, debug=debug, add_dir=add_dir or None, output_format=output_format, continue_session=continue_session)


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
        cmd.insert(1, "--dangerously-skip-permissions")
    if startup_path:
        prompt = Path(startup_path).read_text()
        cmd.append(prompt)

    if tmux:
        session_name = f"sitback-{os.getpid()}"
        run_args = ["tmux", "new-session", "-s", session_name, *cmd]
        with contextlib.suppress(KeyboardInterrupt):
            subprocess.run(
                run_args,
                check=False,
                env=env,
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
    else:
        # WP-Y15: Use os.execvpe for native interactive experience (better signal handling)
        os.execvpe(cmd[0], cmd, env)


# Model aliases for sitback --model (claude and dex)
_SITBACK_MODEL_ALIAS: dict[str, str] = {
    "composer": "composer-1.5",
    "max": "minimax-m2.5",
    "m2.5": "minimax-m2.5",
    "glm": "glm-5",
    "glm5": "glm-5",
    "haiku": "claude-haiku-4.5",
    "opus": "claude-opus-4.6",
    "sonnet": "anthropic/claude-sonnet-4",
    "step": "step-3.5-flash",
    "flash": "gemini-3-flash",
    "mini": "gpt-5-mini",
}
# Provider-native names for Claude Code (ANTHROPIC_MODEL)
_CLAUDE_NATIVE_MODEL: dict[str, str] = {
    "composer-1.5": "composer-1.5",
    "minimax-m2.5": "MiniMax-M2.5",
    "glm-5": "glm-5",
    "claude-haiku-4.5": "claude-haiku-4.5",
    "claude-opus-4.6": "claude-opus-4.6",
    "anthropic/claude-sonnet-4": "anthropic/claude-sonnet-4",
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
        cmd.append("--dangerously-bypass-approvals-and-sandbox")
    cmd.extend(["--model", canonical])
    if startup_path:
        cmd.append(Path(startup_path).read_text())

    if tmux:
        session_name = f"sitback-dex-{os.getpid()}"
        run_args = ["tmux", "new-session", "-s", session_name, *cmd]
        with contextlib.suppress(KeyboardInterrupt):
            subprocess.run(run_args, check=False, env=codex_env, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    else:
        os.execvpe(cmd[0], cmd, codex_env)


def sitback_cmd(
    agent: str = typer.Option(
        "gemini",
        "--agent",
        "-a",
        help="Provider: gemini (default), nim, kilo, glm, openrouter (ignored when --dex)",
    ),
    model: str | None = typer.Option(
        None,
        "--model",
        "-M",
        help="Override model: composer, max, glm, haiku, opus, sonnet, step, flash, mini (works with both claude and dex)",
    ),
    dex: bool = typer.Option(
        False,
        "--dex",
        "-x",
        help="Use Codex CLI instead of Claude Code (fallback when claude not installed)",
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
        help="Override skill: sitback-agent (default), agent-orchestra, or custom name",
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
) -> None:
    """Start Claude Code or Codex with Sitback Agent persona (dashboard + terminal list + ps).

    Examples:
      thegent sitback                    # minimax, Claude Code
      thegent sitback --dex              # Codex (max model), use when claude not installed
      thegent sitback --dex -M glm       # Codex with GLM-5
      thegent sitback -M haiku           # Claude Code with Haiku
      thegent sitback -a kilo            # sibling via kilo
      thegent sitback --skill agent-orchestra
      thegent sitback --profile full
      thegent sitback --tmux
      thegent sitback --no-dashboard
    """
    valid_agents = {"minimax", "nim", "kilo", "glm", "openrouter", "gemini", "copilot"}
    resolved = agent.strip().lower()
    if resolved not in valid_agents:
        if resolved == "max":
            resolved = "openrouter"
        else:
            console.print(f"[red]Invalid agent '{agent}'. Allowed: {', '.join(sorted(valid_agents))}[/red]")
            raise typer.Exit(1)

    # Model override can imply provider: flash -> gemini, mini -> copilot
    if model:
        m = model.strip().lower()
        if m in ("flash", "gemini-3-flash"):
            resolved = "gemini"
        elif m in ("mini", "free", "gpt-5-mini"):
            resolved = "copilot"

    valid_profiles = ("light", "medium", "full")
    prof = profile.strip().lower() if profile else "medium"
    if prof not in valid_profiles:
        console.print(f"[red]Invalid profile '{profile}'. Allowed: {', '.join(valid_profiles)}[/red]")
        raise typer.Exit(1)

    model_override: str | None = None
    if model:
        canonical = _SITBACK_MODEL_ALIAS.get(model.strip().lower(), model.strip())
        model_override = _CLAUDE_NATIVE_MODEL.get(canonical, canonical)

    env = _get_claude_env(resolved, model_override=model_override)
    env["THGENT_SITBACK"] = "1"
    env["THGENT_SITBACK_AGENT"] = resolved
    env["THGENT_SITBACK_PROFILE"] = prof
    if skill is not None:
        env["THGENT_SITBACK_SKILL"] = skill.strip()
    if tmux:
        env["THGENT_SITBACK_TMUX"] = "1"
    if no_dashboard:
        env["THGENT_SITBACK_NO_DASHBOARD"] = "1"
    if cd is not None:
        env["THGENT_SITBACK_CD"] = str(cd.resolve())

    if not dex:
        env.update(_get_claude_env(resolved, model_override=model_override))
        config_dir = Path(env["CLAUDE_CONFIG_DIR"])
        _ensure_claude_config_isolation(config_dir)

    # MCP precondition: ask when server not reachable (Sitback uses FastMCP tools)
    settings = ThegentSettings()
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

    if dex:
        model_alias = (model or "max").strip().lower()
        console.print(f"[bold green]Starting Sitback Agent via Codex (model={model_alias})...[/bold green]")
    else:
        claude_path = _ensure_claude_installed(suggest_dex=True)
        console.print(f"[bold green]Starting Sitback Agent via {resolved} proxy...[/bold green]")

    startup_prompt = _SITBACK_STARTUP_PROMPT
    try:
        from thegent.sitback_plugins import get_registry

        for step in get_registry().get_startup_steps():
            startup_prompt += "\n" + step
    except Exception:
        pass

    if no_dashboard:
        console.print("[dim]Manual mode: no startup prompt injected.[/dim]")
        if dex:
            _run_sitback_codex((model or "max").strip().lower(), env, tmux)
        else:
            _run_sitback_claude(claude_path, env, tmux)
        return

    # Phase 2: Startup prompt injection — try stdin first, always show paste fallback
    console.print("[dim]Injecting startup prompt as positional argument...[/dim]")
    client_name = "Codex" if dex else "Claude Code"
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
        if dex:
            _run_sitback_codex((model or "max").strip().lower(), env, tmux, startup_path=tmp_path)
        else:
            _run_sitback_claude(claude_path, env, tmux, startup_path=tmp_path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            Path(tmp_path).unlink()


@app.command("install-links")
def install_links(
    bin_dir: Path = typer.Option(
        Path.home() / ".local" / "bin",
        "--bin-dir",
        help="Directory to install command wrappers",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
) -> None:
    """Install/update clode + claudeglm + claudemax shims under ~/.local/bin."""
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
