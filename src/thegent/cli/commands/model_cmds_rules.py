"""Thegent CLI model listing and rules sync - extracted from model_cmds_config.py.

Lists available models across providers (Claude, Codex, Cursor, Copilot, Gemini, etc.).
Provides cliproxy login delegation and model contract schema inspection.
"""

# @trace WL-124
from __future__ import annotations

import sys
import re
import subprocess

import typer

from thegent.cli.commands._cli_shared import (
    ThegentSettings,
    _get_run_subprocess_optimized,
    console,
)

# Copilot: only gpt-5-mini and haiku (no gemini-3.1-pro).
_COPILOT_ALLOWED_MODELS: tuple[str, ...] = (
    "claude-haiku-4.5",
    "gpt-5-mini",
)


def _run_cliproxyctl_machine_command(command: str, args: list[str] | None = None) -> dict[str, object]:
    """Run cliproxyctl's machine-readable surface and return a JSON object."""
    import orjson

    run_subprocess_optimized = _get_run_subprocess_optimized()
    cmd = ["cliproxyctl", command, "--json", *(args or [])]
    proc = run_subprocess_optimized(cmd, check=False, capture_output=True, timeout=30, text=True)
    stdout_text = proc.stdout if isinstance(proc.stdout, str) else ""
    stderr_text = proc.stderr if isinstance(proc.stderr, str) else ""
    if proc.returncode != 0:
        detail = stderr_text.strip() or stdout_text.strip() or f"cliproxyctl {command} failed"
        raise RuntimeError(detail)
    if not stdout_text.strip():
        return {}
    payload = orjson.loads(stdout_text)
    if not isinstance(payload, dict):
        raise ValueError("cliproxyctl returned a non-object JSON payload")
    return payload


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
    cli_module = sys.modules.get("thegent.cli")
    cli_subprocess = getattr(cli_module, "subprocess", subprocess)
    cursor_timeout = getattr(cli_subprocess, "TimeoutExpired", subprocess.TimeoutExpired)

    try:
        proc = cli_subprocess.run(
            ["cursor", "agent", "--list-models"],
            check=False,
            capture_output=True,
            timeout=10,
            text=True,
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
    except (FileNotFoundError, cursor_timeout):
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
    "cliproxy_login_cmd",
    "list_model_contract_schema_cmd",
]
