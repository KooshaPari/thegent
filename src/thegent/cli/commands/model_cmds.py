"""Thegent CLI model/agent commands domain - extracted from cli.py (WL-124)."""

# @trace WL-124
from __future__ import annotations

import json
import re
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

import typer

from rich.table import Table

from thegent.cli.commands._cli_shared import (
    ThegentSettings,
    _bootstrap_metric_contracts,
    _get_run_subprocess_optimized,
    _normalize_output_format,
    _resolve_cwd,
    _resolve_droids_dir,
    console,
    list_agent_names,
    list_droid_names,
    resolve_agent,
)
from thegent.cli.commands.model_cmds_agents_helpers import render_agents_table, render_droids_table
from thegent.cli.commands.model_cmds_catalog_helpers import (
    emit_by_model_view,
    emit_contract_view,
    provider_sequence,
    run_provider_listings,
)
from thegent.cli.commands.model_cmds_metrics_helpers import (
    build_index_data,
    collect_metrics_rows,
    emit_cost_values_output,
    emit_index_output,
    emit_metrics_output,
    flatten_cost_values,
)
from thegent.cli.commands.model_cmds_route_helpers import build_available_routes, build_resolved_route
from thegent.cli.commands.model_cmds_setup_helpers import (
    build_provider_list,
    configure_providers,
    set_env_line,
)


def _assert_str(value: str | None) -> str:
    """Assert yaml.dump returned str (always true when stream=None)."""
    assert value is not None, "yaml.dump returned None unexpectedly"
    return value


_CLIPROXYCTL_SCHEMA_VERSION = "cliproxyctl.machine.v1"
_CLIPROXYCTL_NOT_FOUND_MSG = (
    "cliproxyctl not found. Install cliproxyctl and ensure it is on PATH, "
    "or set THGENT_CLIPROXYCTL_BINARY=/path/to/cliproxyctl"
)


def _resolve_cliproxyctl_binary() -> str:
    """Resolve cliproxyctl binary path from env or PATH."""
    configured = os.environ.get("THGENT_CLIPROXYCTL_BINARY", "cliproxyctl").strip() or "cliproxyctl"
    if "/" in configured or "~" in configured:
        return str(Path(configured).expanduser())
    found = shutil.which(configured)
    return found if found else configured


def _binary_exists(binary: str) -> bool:
    return Path(binary).exists() or shutil.which(binary) is not None


def _coerce_subprocess_output(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return "" if value is None else str(value)


def _parse_cliproxyctl_envelope(stdout_text: str, *, expected_command: str) -> dict[str, Any]:
    """Parse and validate cliproxyctl machine JSON envelope."""
    try:
        payload = json.loads(stdout_text)
    except json.JSONDecodeError as exc:  # pragma: no cover - explicit error branch in tests
        raise ValueError(f"Invalid cliproxyctl JSON envelope: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("Invalid cliproxyctl JSON envelope: expected top-level object")
    schema_version = payload.get("schema_version")
    if not isinstance(schema_version, str):
        raise ValueError("Invalid cliproxyctl JSON envelope: missing schema_version")
    if schema_version != _CLIPROXYCTL_SCHEMA_VERSION:
        raise ValueError(
            "Unsupported cliproxyctl schema_version: "
            f"{schema_version} (expected {_CLIPROXYCTL_SCHEMA_VERSION})"
        )
    command = payload.get("command")
    if not isinstance(command, str):
        raise ValueError("Invalid cliproxyctl JSON envelope: missing command")
    if command != expected_command:
        raise ValueError(f"cliproxyctl command mismatch: expected '{expected_command}', got '{command}'")
    ok = payload.get("ok")
    if not isinstance(ok, bool):
        raise ValueError("Invalid cliproxyctl JSON envelope: missing boolean 'ok'")
    return payload


def _run_cliproxyctl_machine_command(command: str, *, args: list[str] | None = None) -> dict[str, Any]:
    """Run cliproxyctl command with --json and enforce envelope validation."""
    binary = _resolve_cliproxyctl_binary()
    if not _binary_exists(binary):
        raise FileNotFoundError(_CLIPROXYCTL_NOT_FOUND_MSG)
    argv = [binary, command, *(args or []), "--json"]
    run_subprocess_optimized = _get_run_subprocess_optimized()
    proc = run_subprocess_optimized(argv, check=False, capture_output=True, text=True)
    stdout_text = _coerce_subprocess_output(getattr(proc, "stdout", ""))
    stderr_text = _coerce_subprocess_output(getattr(proc, "stderr", ""))
    envelope = _parse_cliproxyctl_envelope(stdout_text, expected_command=command)
    if proc.returncode != 0:
        error = envelope.get("error")
        error_message = ""
        if isinstance(error, dict):
            code = error.get("code")
            message = error.get("message")
            error_message = f"{code}: {message}" if code or message else str(error)
        if not error_message:
            error_message = stderr_text.strip() or envelope.get("message", "")
        raise RuntimeError(f"cliproxyctl {command} failed with exit code {proc.returncode}: {error_message}".strip())
    if not envelope["ok"]:
        error = envelope.get("error")
        detail = error if isinstance(error, str) else json.dumps(error) if error is not None else ""
        message = str(envelope.get("message", "")).strip()
        combined = ": ".join([part for part in [message, detail] if part]).strip()
        raise RuntimeError(f"cliproxyctl {command} reported failure{': ' + combined if combined else ''}")
    return envelope


# Copilot: only gpt-5-mini and haiku (no gemini-3.1-pro).
_COPILOT_ALLOWED_MODELS: tuple[str, ...] = (
    "claude-haiku-4.5",
    "gpt-5-mini",
)


def _models_table(title: str) -> Table:
    t = Table(title=title)
    t.add_column("Model ID", style="cyan")
    t.add_column("Display Name", style="dim")
    return t


def list_agents_cmd() -> None:
    """List available agents."""
    agents = list_agent_names()
    render_agents_table(agents, resolve_agent=resolve_agent, console=console)


def list_droids_cmd(cd: Path | None = None) -> None:
    """List available droids."""
    settings = ThegentSettings()
    resolved_cd = _resolve_cwd(cd)
    droids_dir = _resolve_droids_dir(resolved_cd, settings)
    droids = list_droid_names(droids_dir)
    if not droids:
        console.print("[yellow]No droids found.[/yellow]")
        return
    render_droids_table(droids, console=console)


def list_models_cmd(
    provider: str | None = None,
    by_model: bool = False,
    refresh: bool = False,
    include_contract: bool = False,
) -> None:
    """List available models (scraped from CLIs/config)."""
    if include_contract:
        emit_contract_view(provider=provider, refresh=refresh, console=console)
        return

    if by_model:
        emit_by_model_view(refresh=refresh, console=console)
        return
    providers = provider_sequence(provider)
    run_provider_listings(
        providers,
        handlers={
            "minimax": _list_minimax_models,
            "glm": _list_glm_models,
            "cursor": _list_cursor_api_models,
            "gemini": _list_gemini_models,
            "copilot": _list_copilot_models,
            "interactive_agent": _list_claude_models,
            "claude": _list_claude_models,
            "headless_agent": _list_codex_models,
            "codex": _list_codex_models,
            "antigravity": _list_antigravity_models,
            "kiro": _list_kiro_models,
        },
    )


def speed_index_cmd(
    format: str | None = None,
    no_cache: bool = False,
) -> None:
    """Show speed index (0-1, higher=faster) for all model-provider pairs.

    Uses CLIProxyAPIPlus metrics (tps_1m, latency_p50_ms, success_rate) when reachable;
    falls back to Route.latency_ms.
    """
    from thegent.models.speed_values import (
        get_model_provider_speed_indices,
        invalidate_speed_index_cache,
    )

    if no_cache:
        invalidate_speed_index_cache()
    indices = get_model_provider_speed_indices(use_cache=not no_cache)
    data = build_index_data(indices)

    fmt = _normalize_output_format(format)
    emit_index_output(
        data=data,
        fmt=fmt,
        title="Model-Provider Speed Index (0-1, higher=faster)",
        value_label="Speed Index",
        console=console,
    )


def quality_index_cmd(
    format: str | None = None,
    no_cache: bool = False,
) -> None:
    """Show quality index (0-1) for all models.

    Uses benchmarks.json (Terminal Bench 2.0, SWE-Bench, AIME) when available;
    falls back to Route.accuracy_score.
    """
    from thegent.models.quality_values import (
        get_model_provider_quality_indices,
        invalidate_quality_index_cache,
    )

    if no_cache:
        invalidate_quality_index_cache()
    indices = get_model_provider_quality_indices(use_cache=not no_cache)
    data = build_index_data(indices)

    fmt = _normalize_output_format(format)
    emit_index_output(
        data=data,
        fmt=fmt,
        title="Model-Provider Quality Index (0-1, higher=better)",
        value_label="Quality Index",
        console=console,
    )


def metrics_cmd(
    format: str | None = None,
    no_cache: bool = False,
    limit: int = 50,
) -> None:
    """Show cost, speed, and quality indices for all model-provider pairs (unified view)."""
    from thegent.models.cost_values import get_model_provider_costs
    from thegent.models.quality_values import (
        get_model_provider_quality_indices,
        invalidate_quality_index_cache,
    )
    from thegent.models.speed_values import (
        get_model_provider_speed_indices,
        invalidate_speed_index_cache,
    )

    if no_cache:
        invalidate_speed_index_cache()
        invalidate_quality_index_cache()
    costs = get_model_provider_costs()
    speed = get_model_provider_speed_indices(use_cache=not no_cache)
    quality = get_model_provider_quality_indices(use_cache=not no_cache)

    rows = collect_metrics_rows(costs=costs, speed=speed, quality=quality, limit=limit)

    fmt = _normalize_output_format(format)
    emit_metrics_output(rows=rows, limit=limit, fmt=fmt, console=console)


def cost_values_cmd(format: str | None = None) -> None:
    """Show cost values ($/1k tokens) for all model-provider pairs.

    Uses CLIProxyAPIPlus metrics when reachable; falls back to static values.
    """
    from thegent.models.cost_values import get_model_provider_costs

    costs = get_model_provider_costs()
    data = flatten_cost_values(costs)

    fmt = _normalize_output_format(format)
    emit_cost_values_output(data=data, fmt=fmt, console=console)


def resolve_model_route_cmd(
    model: str,
    provider: str | None = None,
    policy: str = "prefer_direct",
    quality_floor: float = 0.0,
    lane: str | None = None,
) -> None:
    """Resolve a model to a preferred route and emit contract-style output."""
    from thegent.models import (
        ModelCatalog,
        normalize_model_id,
        normalize_route_policy,
        resolve_route_contract,
    )
    from thegent.models.quality_values import get_model_provider_quality_indices
    from thegent.models.speed_values import get_model_provider_speed_indices

    try:
        policy_value = normalize_route_policy(policy)
    except ValueError:
        console.print(
            "[red]Invalid routing policy. Use prefer_direct, prefer_proxy, failover, cheapest, cost_quality, pareto.[/red]"
        )
        raise typer.Exit(1)

    normalized = normalize_model_id(model)
    route = resolve_route_contract(
        model,
        provider_hint=provider,
        policy=policy_value,
    )
    speed_map = get_model_provider_speed_indices().get(normalized, {})
    quality_map = get_model_provider_quality_indices().get(normalized, {})
    routes = sorted(
        ModelCatalog.routes_for(model),
        key=lambda r: (r.provider, r.priority, r.model_alias),
    )
    available_routes = build_available_routes(routes=routes, speed_map=speed_map, quality_map=quality_map)

    payload: dict[str, Any] = {
        "model": model,
        "normalized_model": normalized,
        "policy": policy_value,
        "provider_hint": provider,
        "route_found": route is not None,
        "available_routes": available_routes,
    }
    if route is None:
        if available_routes:
            console.print("[yellow]No route matched the provided hint. Showing available routes below.[/yellow]")
        else:
            console.print(f"[red]No route for model '{model}'.[/red]")
        console.print_json(data=payload)
        raise typer.Exit(1)

    resolved = build_resolved_route(route=route, speed_map=speed_map, quality_map=quality_map)
    payload["resolved_route"] = resolved
    console.print_json(data=payload)


def list_model_contract_schema_cmd() -> None:
    """Print the route contract schema metadata used by contract views."""
    from thegent.models import route_contract

    console.print_json(data=route_contract())


def _list_minimax_models() -> None:
    """List Minimax models (via CLIProxyAPIPlus minimax: block in config)."""
    console.print("\n[bold]Minimax models (via CLIProxyAPIPlus)[/bold]")
    console.print("  minimax-m2.5 (default)")
    console.print("  [dim]Add minimax: block to config; run thegent cliproxy login minimax for instructions[/dim]")


def _list_glm_models() -> None:
    """List GLM models (via CLIProxyAPIPlus iflow channel)."""
    console.print("\n[bold]GLM models (via CLIProxyAPIPlus)[/bold]")
    console.print("  glm-5 (default)")
    console.print("  [dim]OAuth: thegent cliproxy login iflow (or glm)[/dim]")


def _list_cursor_models() -> None:
    """List cursor models via cursor agent --list-models."""
    try:
        run_subprocess_optimized = _get_run_subprocess_optimized()
        proc = run_subprocess_optimized(
            ["cursor", "agent", "--list-models"],
            check=False,
            capture_output=True,
            timeout=10,
        )
        if proc.returncode == 0 and proc.stdout:
            stdout_text = proc.stdout if isinstance(proc.stdout, str) else proc.stdout.decode("utf-8", errors="replace")
            console.print("\n[bold]Cursor models[/bold]")
            for line in stdout_text.splitlines():
                line = line.strip()
                if line and not line.startswith("Tip:"):
                    console.print(f"  {line}")
        else:
            console.print("[dim]cursor agent --list-models failed[/dim]")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        console.print("[dim]Cursor CLI not found or timed out[/dim]")


def _list_cursor_api_models() -> None:
    """List cursor-api models via GET /v1/models (wisdgod cursor-api)."""
    from thegent.models.scrapers import scrape_cursor_api

    settings = ThegentSettings()
    models = scrape_cursor_api(settings)
    console.print("\n[bold]Cursor-api models (wisdgod)[/bold]")
    if models:
        for m in models:
            console.print(f"  {m}")
        console.print("  [dim]Requires cursor-api at THGENT_CURSOR_API_URL; set THGENT_CURSOR_API_TOKEN[/dim]")
    else:
        console.print(f"  [dim]cursor-api not reachable at {settings.cursor_api_url}[/dim]")


def _list_gemini_models() -> None:
    """Scrape gemini models from gemini --help (has -m/--model)."""
    console.print("\n[bold]Gemini models[/bold]")
    console.print("  gemini-3-flash (default)")
    console.print("  gemini-2.0-flash")
    console.print("  [dim]Use gemini -m <model> or THGENT_GEMINI_MODEL[/dim]")


def _list_copilot_models() -> None:
    """Scrape copilot models from copilot --help --model choices."""
    try:
        run_subprocess_optimized = _get_run_subprocess_optimized()
        proc = run_subprocess_optimized(
            ["copilot", "--help"],
            check=False,
            capture_output=True,
            timeout=8,
        )
        stdout_text = (
            proc.stdout
            if isinstance(proc.stdout, str)
            else (proc.stdout.decode("utf-8", errors="replace") if proc.stdout else "")
        )
        if proc.returncode == 0 and stdout_text and "--model" in stdout_text:
            console.print("\n[bold]Copilot models[/bold]")
            # Extract quoted model names after "choices:"
            start = stdout_text.find("--model")
            chunk = stdout_text[start : start + 600] if start >= 0 else ""
            choices = re.findall(r'"([a-zA-Z0-9.-]+)"', chunk)
            seen = set()
            for c in choices:
                if c not in seen and ("claude" in c or "gpt" in c or "gemini" in c):
                    seen.add(c)
                    console.print(f"  {c}")
            if not seen:
                _list_copilot_models_fallback()
        else:
            _list_copilot_models_fallback()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        _list_copilot_models_fallback()


def _list_copilot_models_fallback() -> None:
    """Fallback copilot model list (matches copilot --model allowed choices)."""
    console.print("\n[bold]Copilot models[/bold]")
    for m in _COPILOT_ALLOWED_MODELS:
        default = " (default)" if m == "gpt-5-mini" else ""
        console.print(f"  {m}{default}")


def _list_claude_models() -> None:
    """Scrape claude models from claude --help (--model aliases)."""
    console.print("\n[bold]Claude models[/bold]")
    console.print("  haiku, sonnet, sonnet-1m, opus")
    console.print("  claude-haiku-4.5, claude-sonnet-4.5, claude-sonnet-4.5-1m (1M context), claude-opus-4.6")
    console.print("  [dim]Use claude --model <alias> or THGENT_CLAUDE_MODEL[/dim]")


def _list_codex_models() -> None:
    """List codex models (from cursor --list-models, codex variants)."""
    try:
        run_subprocess_optimized = _get_run_subprocess_optimized()
        proc = run_subprocess_optimized(
            ["cursor", "agent", "--list-models"],
            check=False,
            capture_output=True,
            timeout=10,
        )
        stdout_text = (
            proc.stdout
            if isinstance(proc.stdout, str)
            else (proc.stdout.decode("utf-8", errors="replace") if proc.stdout else "")
        )
        if proc.returncode == 0 and stdout_text and "codex" in stdout_text.lower():
            console.print("\n[bold]Codex models[/bold]")
            for line in stdout_text.splitlines():
                line = line.strip()
                if "codex" in line.lower():
                    console.print(f"  {line}")
            console.print(
                "  [dim]Default: gpt-5.3-codex-spark-xhigh; high-power: gpt-5.3-codex-high, gpt-5.3-codex-xhigh[/dim]"
            )
        else:
            _list_codex_models_fallback()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        _list_codex_models_fallback()


def _list_codex_models_fallback() -> None:
    """Fallback codex model list."""
    console.print("\n[bold]Codex models[/bold]")
    for m in [
        "gpt-5.3-codex-spark-xhigh (default)",
        "gpt-5.3-codex",
        "gpt-5.3-codex-low",
        "gpt-5.3-codex-high",
        "gpt-5.3-codex-xhigh",
    ]:
        console.print(f"  {m}")


def _list_antigravity_models() -> None:
    """List antigravity models (via CLIProxyAPIPlus)."""
    settings = ThegentSettings()
    console.print("\n[bold]Antigravity models (via CLIProxyAPIPlus)[/bold]")
    console.print(f"  {settings.default_antigravity_model} (default)")
    console.print("  [dim]OAuth: thegent cliproxy login antigravity[/dim]")
    console.print("  [dim]Other: gemini-3.1-pro-high, gemini-3.1-pro-image, tstars2.0 (iflow)[/dim]")


def _list_kiro_models() -> None:
    """List kiro models (claude-haiku-4.5, claude-opus-4.6 via CLIProxyAPIPlus)."""
    settings = ThegentSettings()
    console.print("\n[bold]Kiro models (via CLIProxyAPIPlus)[/bold]")
    console.print("  claude-haiku-4.5")
    console.print("  claude-haiku-4.5 (default)")
    console.print(f"  [dim]Default: {settings.default_kiro_model}[/dim]")
    console.print("  [dim]OAuth: thegent cliproxy login kiro[/dim]")


def cliproxy_login_cmd(provider: str, force: bool = False) -> None:
    """Run provider login by delegating to cliproxyctl machine JSON surface."""
    try:
        console.print(f"\n[bold cyan]Delegating provider login to cliproxyctl ({provider})...[/bold cyan]")
        args = [provider]
        if force:
            args.append("--force")
        envelope = _run_cliproxyctl_machine_command("login", args=args)
        message = str(envelope.get("message", "")).strip() or f"Delegated login completed for provider '{provider}'."
        console.print(f"[green]{message}[/green]")
        raise typer.Exit(0)
    except typer.Exit:
        raise
    except (ValueError, RuntimeError, FileNotFoundError) as e:
        console.print(f"[red]Delegated login failed: {e}[/red]")
        raise typer.Exit(1)


def setup_cmd(
    api_key: str = typer.Option(None, "--api-key", "-k", help="NVIDIA NIM API key"),
    model: str = typer.Option(None, "--model", "-m", help="NVIDIA NIM model (default: z-ai/glm-5)"),
    openrouter_key: str = typer.Option(None, "--openrouter-key", help="OpenRouter API key"),
    kilo_key: str = typer.Option(None, "--kilo-key", help="Kilo.ai API key"),
    zai_key: str = typer.Option(None, "--zai-key", help="Z.AI (Zhipu) API key"),
    minimax_key: str = typer.Option(None, "--minimax-key", help="MiniMax API key"),
    wizard: bool = typer.Option(True, "--wizard/--no-wizard", help="Run interactive setup wizard"),
    links: bool = typer.Option(True, "--links/--no-links", help="Install claudeglm/claudemax shortcuts"),
    hooks: bool = typer.Option(
        False, "--hooks/--no-hooks", help="Install git hooks (pre-commit, pre-push) into .git/hooks"
    ),
    skills: bool = typer.Option(
        False, "--skills/--no-skills", help="Sync thegent-skills template to ~/.claude, ~/.cursor, project"
    ),
    harness: bool = typer.Option(False, "--harness/--no-harness", help="Install/update heliosShield harness"),
    full: bool = typer.Option(
        False,
        "--full",
        "-f",
        help="Full setup: install -t all, install-shims, lock-cleanup service, MCP service, and harness",
    ),
    agents: str = typer.Option(
        None,
        "--agents",
        "-a",
        help="Comma-separated agents to configure (e.g. claude,codex,cursor). Skips others in wizard.",
    ),
) -> None:
    """Unified setup: configure providers (same flow as cliproxy login) and install shortcuts.

    Examples:
      thegent setup                    # Interactive wizard
      thegent setup --full             # Full setup: install, shims, services, harness
      thegent setup --harness          # Install/update heliosShield harness only
      thegent setup --hooks --skills   # Project: git hooks + skills
    """
    import platform
    from pathlib import Path

    from thegent.agents.cliproxy_manager import (
        _LOGIN_FLAGS,
        PROVIDER_LOGIN_CONFIG,
        _ensure_config,
        _inject_api_key_into_cliproxy,
        run_login,
    )
    from thegent.infra import yaml_dump, yaml_load

    settings = ThegentSettings()
    env_path = Path(".env")

    from rich.prompt import Confirm

    # Harness setup
    if harness or full:
        console.print("\n[bold cyan]Setting up heliosShield Harness...[/bold cyan]")
        try:
            from thegent.install import setup_harness

            if setup_harness(verbose=True):
                console.print("[green]✓[/green] heliosShield Harness setup complete.")
            else:
                console.print("[yellow]! heliosShield Harness setup skipped or failed.[/yellow]")
        except Exception as e:
            console.print(f"[yellow]Harness setup error: {e}[/yellow]")

    run_install_actions = full
    if not full and wizard:
        run_install_actions = Confirm.ask(
            "Run install/bootstrap actions too (install targets, shims, services)?",
            default=False,
        )

    # Install/bootstrap actions: install, shims, lock-cleanup, MCP service
    if run_install_actions:
        run_subprocess_optimized = _get_run_subprocess_optimized()

        console.print("\n[bold cyan]Setup: installing to all targets...[/bold cyan]")
        try:
            from thegent.install import run_install

            run_install(target="all", install_service=True, verbose=True)
        except Exception as e:
            console.print(f"[yellow]Install: {e}[/yellow]")

        console.print("\n[bold cyan]Installing tool accelerators (shims)...[/bold cyan]")
        try:
            run_subprocess_optimized([sys.executable, "-m", "thegent", "install-shims"], check=False)
        except Exception as e:
            console.print(f"[yellow]Install-shims: {e}[/yellow]")

        if platform.system() in ("Darwin", "Linux"):
            if Confirm.ask("Install git wrapper to system path (requires sudo)?", default=False):
                try:
                    run_subprocess_optimized(
                        [sys.executable, "-m", "thegent", "install-shims", "--system"],
                        check=False,
                    )
                except Exception as e:
                    console.print(f"[yellow]Install-shims --system: {e}[/yellow]")

        console.print("\n[bold cyan]Installing lock-cleanup service...[/bold cyan]")
        try:
            from thegent.git_lock_manage import lock_cleanup_install, lock_cleanup_start

            ok, msg = lock_cleanup_install()
            if ok:
                console.print(f"[green]{msg}[/green]")
                lock_cleanup_start()
            else:
                console.print(f"[yellow]{msg}[/yellow]")
        except Exception as e:
            console.print(f"[yellow]Lock-cleanup: {e}[/yellow]")

        console.print("\n[bold green]Install/bootstrap actions complete.[/bold green]")
    lines = env_path.read_text().splitlines() if env_path.exists() else []

    def prompt_key(msg: str) -> str:
        from rich.prompt import Prompt

        return Prompt.ask(msg, default="", show_default=False).strip()

    # CLI overrides: if user passed --api-key etc., inject into config directly
    overrides = {
        "nim": api_key,
        "kilo": kilo_key,
        "glm": zai_key,
        "minimax": minimax_key,
    }

    all_providers = build_provider_list(
        provider_login_config=PROVIDER_LOGIN_CONFIG,
        login_flags=_LOGIN_FLAGS,
        agents=agents,
        console=console,
    )
    should_delegate_setup = (
        wizard
        and os.environ.get("THGENT_SETUP_USE_CLIPROXY", "1") == "1"
        and not any(v for v in overrides.values())
    )
    if should_delegate_setup:
        delegation_args: list[str] = []
        selected_agents = (agents or "").strip()
        if selected_agents:
            delegation_args.extend(["--providers", selected_agents])
        try:
            console.print("\n[bold cyan]Delegating provider setup to cliproxyctl...[/bold cyan]")
            envelope = _run_cliproxyctl_machine_command("setup", args=delegation_args)
        except (ValueError, RuntimeError, FileNotFoundError) as exc:
            console.print(f"[red]Delegated setup failed: {exc}[/red]")
            raise typer.Exit(1)
        any_configured = bool(envelope.get("ok"))
    else:
        any_configured = configure_providers(
            providers=all_providers,
            overrides=cast("dict[str, str | None]", overrides),
            wizard=wizard,
            settings=settings,
            provider_login_config=PROVIDER_LOGIN_CONFIG,
            ensure_config=_ensure_config,
            inject_api_key=_inject_api_key_into_cliproxy,
            run_login=run_login,
            yaml_load=yaml_load,
            yaml_dump=lambda data, **kw: _assert_str(yaml_dump(data, **kw)),
            prompt_key=prompt_key,
            console=console,
        )

    env_updated = False
    if model:
        set_env_line(lines, key="THGENT_NIM_MODEL", value=model)
        env_updated = True

    if any_configured:
        console.print("\n[green]Provider credentials saved to cliproxy config.[/green]")
        console.print("[dim]The proxy has been restarted automatically to apply changes.[/dim]")

    # Ensure cliproxy config exists (cursor block, etc.)
    try:
        from thegent.agents.cliproxy_manager import _ensure_config

        _ensure_config(settings)
    except Exception as e:
        console.print(f"[yellow]Cliproxy config: {e}[/yellow]")
    if env_updated:
        env_path.write_text("\n".join(lines) + "\n")
        console.print(f"[green]Updated {env_path}[/green]")

    if links:
        console.print("\n[bold cyan]Installing interactive shortcuts...[/bold cyan]")
        bin_dir = Path.home() / ".local" / "bin"
        if not bin_dir.exists():
            bin_dir.mkdir(parents=True, exist_ok=True)
        try:
            from thegent.clode_main import install_links as clode_install_links

            clode_install_links(bin_dir=bin_dir, force=True)
        except Exception as e:
            console.print(f"[red]Clode links: {e}[/red]")
        try:
            from thegent.dex_main import install_links as dex_install_links

            dex_install_links(bin_dir=bin_dir, force=True)
        except Exception as e:
            console.print(f"[red]Dex links: {e}[/red]")

    if hooks:
        console.print("\n[bold cyan]Installing git hooks...[/bold cyan]")
        try:
            from thegent.install import setup_hooks

            counts = setup_hooks(cwd=Path.cwd(), verbose=True)
            if counts.get("installed", 0) > 0:
                console.print(f"[green]✓[/green] Installed {counts['installed']} hook(s) into .git/hooks")
            elif counts.get("skipped", 0) > 0:
                console.print("[dim]Not a git repo; skipped hooks.[/dim]")
        except Exception as e:
            console.print(f"[yellow]Hooks: {e}[/yellow]")

    if skills:
        console.print("\n[bold cyan]Syncing skills template...[/bold cyan]")
        try:
            from thegent.install import setup_skills

            counts = setup_skills(cwd=Path.cwd(), verbose=True)
            if counts.get("copied", 0) > 0:
                console.print(f"[green]✓[/green] Synced {counts['copied']} file(s) to ~/.claude, ~/.cursor")
        except Exception as e:
            console.print(f"[yellow]Skills: {e}[/yellow]")

    # Bootstrap hard metric contracts and quality gate config for governance.
    try:
        created_contract, updated_quality = _bootstrap_metric_contracts(Path.cwd())
        if created_contract:
            console.print("[green]✓[/green] Bootstrapped contracts/metric-contracts.json")
        if updated_quality:
            console.print("[green]✓[/green] Enabled governance.metric_contracts.enforce_gate in .claude/quality.json")
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    if wizard:
        from rich.prompt import Confirm

        if Confirm.ask(
            "\nWould you like to integrate thegent with your AI agents (Cursor, Claude Code, Codex, etc.)?",
            default=True,
        ):
            from thegent.install import run_wizard

            run_wizard()

        if Confirm.ask(
            "\nRemove manual playwright from MCP configs (use thegent-bundled browser tools)?", default=True
        ):
            try:
                from thegent.mcp.manage import remove_playwright_from_client

                for c in ["cursor", "claude-code", "codex", "claude-desktop"]:
                    ok, msg = remove_playwright_from_client(c)
                    if ok and "Removed" in msg:
                        console.print(f"[dim]{msg}[/dim]")
                console.print("[dim]Start MCP: thegent mcp up[/dim]")
            except Exception as e:
                console.print(f"[yellow]Playwright removal: {e}[/yellow]")

    console.print("\n[bold cyan]Running doctor checks...[/bold cyan]")
    try:
        from thegent.doctor import run_doctor

        doctor_ok = run_doctor(fix=False, dry_run=False)
        if doctor_ok:
            console.print("[green]✓[/green] Doctor checks passed.")
        else:
            console.print("[yellow]! Doctor reported issues. Run: thegent doctor --fix[/yellow]")
    except Exception as e:
        console.print(f"[yellow]Doctor run failed: {e}[/yellow]")

    console.print("\n[bold green]Setup complete![/bold green]")
    console.print("Try: [blue]claudeglm[/blue] | [blue]claudemax[/blue] | [blue]dex[/blue] | [blue]dexmax[/blue]")


def rules_sync_cmd(
    force: bool = typer.Option(False, "--force", "-f", help="Force overwrite even if identical"),
    check: bool = typer.Option(False, "--check", help="Check for drift without syncing"),
    cd: Path | None = typer.Option(None, "--cd", "-d", help="Project directory"),
) -> None:
    """Sync CLAUDE.md to other platform-specific rule files (AGENTS.md, Cursor, Codex)."""
    from thegent.cli.commands.impl import rules_sync_impl

    result = rules_sync_impl(cd=cd, force=force, check=check)
    if not result["success"]:
        console.print(f"[red]{result['error']}[/red]")
        raise typer.Exit(1)

    if check:
        if result["in_sync"]:
            console.print("[green]Rules are in sync.[/green]")
            raise typer.Exit(0)
        console.print("[red]Drift detected in rule files:[/red]")
        for target in result["drift"]:
            console.print(f"  - {target}")
        raise typer.Exit(1)

    if not result["synced"]:
        console.print("[yellow]Rules are already in sync.[/yellow]")
    else:
        for target in result["synced"]:
            console.print(f"[green]Synced: {target}[/green]")


__all__ = [
    "_list_antigravity_models",
    "_list_claude_models",
    "_list_codex_models",
    "_list_codex_models_fallback",
    "_list_copilot_models",
    "_list_copilot_models_fallback",
    "_list_cursor_api_models",
    "_list_cursor_models",
    "_list_gemini_models",
    "_list_glm_models",
    "_list_kiro_models",
    "_list_minimax_models",
    "_models_table",
    "cliproxy_login_cmd",
    "cost_values_cmd",
    "list_agents_cmd",
    "list_droids_cmd",
    "list_model_contract_schema_cmd",
    "list_models_cmd",
    "metrics_cmd",
    "quality_index_cmd",
    "resolve_model_route_cmd",
    "rules_sync_cmd",
    "setup_cmd",
    "speed_index_cmd",
]
