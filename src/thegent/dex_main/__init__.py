"""Stub module for thegent.dex_main.

This module provides the CLI entry points for interacting with various AI coding assistants
(Codex, Gemini, Claude, etc.) through the thegent shim layer.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import typer

app = typer.Typer(help="thegent AI coding assistant CLI")

_DEX_BYPASS_FLAG = "--dangerously-bypass-approvals-and-sandbox"
_DEX_YOLO_FLAG = "--dangerously-enable-yolo-mode"

# Model alias mapping
_MODEL_ALIAS: dict[str, str] = {
    "dex": "gpt-5.3-codex",
    "codex": "gpt-5.3-codex",
    "composer": "composer-1.5",
    "max": "minimax-m2.5",
    "glm": "glm-5",
    "haiku": "claude-haiku-4.5",
    "opus": "claude-opus-4.6",
    "sonnet": "claude-sonnet-4.5",
    "step": "step-3.5-flash",
    "flash": "gemini-2.5-flash",
    "high": "gpt-5.3-codex-high",
    "xhigh": "gpt-5.3-codex-xhigh",
    "mini": "gpt-5-mini",
    "ultra": "llama-nemotron-ultra",
}


def _get_codex_env() -> dict[str, Any]:
    """Get the Codex environment variables.

    Returns:
        Dictionary of Codex-related environment variables.
    """
    import os
    return {
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY", ""),
        "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY", ""),
        "GOOGLE_API_KEY": os.environ.get("GOOGLE_API_KEY", ""),
    }


def resolve_codex_cli_path() -> str:
    """Resolve the path to the Codex CLI binary.

    Returns:
        Path to the codex CLI executable.
    """
    import shutil
    path = shutil.which("codex") or shutil.which("openai-codex")
    return path or "/usr/local/bin/codex"


def wrap_with_caffeinate(cmd: list[str], session_id: str) -> list[str]:
    """Wrap command with caffeinate to prevent idle sleep.

    Args:
        cmd: Command to wrap.
        session_id: Session identifier.

    Returns:
        Wrapped command list.
    """
    return ["caffeinate", "-i", "-s", "-m"] + cmd


def _resolve_provider_for_model(model_alias: str) -> str:
    """Resolve the provider for a model alias.

    Args:
        model_alias: The model alias to resolve.

    Returns:
        Provider name.
    """
    if model_alias in ("dex", "high", "xhigh"):
        return "codex"
    elif model_alias == "composer":
        return "cursor"
    elif model_alias == "step":
        return "nim"
    elif model_alias == "mini":
        return "copilot"
    elif model_alias == "flash":
        return "gemini"
    elif model_alias in ("haiku", "opus", "sonnet"):
        providers = ["claude", "antigravity"]
        import os
        idx = int(os.environ.get("THGGENT_ROUND_ROBIN_INDEX", "0")) % len(providers)
        return providers[idx]
    elif model_alias in ("glm",):
        providers = ["nim", "kilo", "minimax", "glm"]
        import os
        idx = int(os.environ.get("THGGENT_ROUND_ROBIN_INDEX", "0")) % len(providers)
        return providers[idx]
    elif model_alias in ("max",):
        providers = ["nim", "kilo", "minimax"]
        import os
        idx = int(os.environ.get("THGGENT_ROUND_ROBIN_INDEX", "0")) % len(providers)
        return providers[idx]
    return "openai"


def _exec_native_codex(args: list[str]) -> None:
    """Execute native codex CLI directly.

    Args:
        args: Arguments to pass to codex.
    """
    import os
    codex_path = resolve_codex_cli_path()
    os.execvpe(codex_path, [codex_path] + args, os.environ.copy())


def _run_codex_interactive(
    model: str,
    *,
    dangerously_bypass: bool = False,
    extra_args: list[str] | None = None,
) -> None:
    """Run codex in interactive mode with the specified model.

    Args:
        model: Model alias to use.
        dangerously_bypass: Whether to bypass safety checks.
        extra_args: Additional arguments to pass to codex.
    """
    import os

    provider = _resolve_provider_for_model(model)
    canonical_model = _MODEL_ALIAS.get(model, model)

    env = _get_codex_env()

    if provider == "codex":
        env["OPENAI_BASE_URL"] = os.environ.get("OPENAI_BASE_URL", "http://127.0.0.1:8317")
    elif provider == "copilot":
        env["GITHUB_COPILOT_API_URL"] = os.environ.get("GITHUB_COPILOT_API_URL", "http://127.0.0.1:8317")

    codex_path = resolve_codex_cli_path()

    cmd = [codex_path]
    cmd.extend(extra_args or [])

    if dangerously_bypass:
        if _DEX_YOLO_FLAG not in cmd:
            cmd.append(_DEX_YOLO_FLAG)
        if _DEX_BYPASS_FLAG not in cmd:
            cmd.append(_DEX_BYPASS_FLAG)

    wrapped_cmd = wrap_with_caffeinate(cmd, os.environ.get("THGGENT_SESSION_ID", ""))

    os.execvpe(wrapped_cmd[0], wrapped_cmd, env)


def _run_model_cmd(model_alias: str, prompt: str) -> None:
    """Run a model command with the specified alias.

    Args:
        model_alias: Model alias to use.
        prompt: Prompt to send.
    """
    from thegent.cli import run_cmd
    canonical_model = _MODEL_ALIAS.get(model_alias, model_alias)
    run_cmd(model=canonical_model, prompt=prompt, remote=None)


@app.command()
def config() -> None:
    """Launch the configuration TUI."""
    from thegent.ux.models_providers_tui import run_models_providers_tui
    run_models_providers_tui()


@app.callback()
def default_dex(
    ctx: typer.Context,
    force: bool = False,
    native: bool = False,
) -> None:
    """Default command that runs flash model."""
    import os
    import sys

    if ctx.invoked_subcommand is not None:
        return

    model = "flash"
    extra_args: list[str] = []

    # Check for direct invocation
    if len(sys.argv) > 1 and sys.argv[1] != "dex":
        # Extract extra args
        extra_args = sys.argv[2:] if len(sys.argv) > 2 else []

    if native:
        _exec_native_codex(["--force-yolo", _DEX_YOLO_FLAG, _DEX_BYPASS_FLAG] if force else [])
        return

    _run_codex_interactive(model, dangerously_bypass=True, extra_args=extra_args)


# Also expose the subcommands as separate commands
@app.command()
def dex(
    ctx: typer.Context,
    force: bool = False,
    native: bool = False,
) -> None:
    """Run dex with default flash model."""
    if ctx.invoked_subcommand is not None:
        return
    default_dex(ctx, force=force, native=native)


@app.command()
def composer(
    ctx: typer.Context,
    force: bool = False,
    native: bool = False,
) -> None:
    """Run composer model."""
    if ctx.invoked_subcommand is not None:
        return
    _run_codex_interactive("composer", dangerously_bypass=True, extra_args=["--search"])


@app.command()
def max(
    ctx: typer.Context,
    force: bool = False,
    native: bool = False,
) -> None:
    """Run max model."""
    if ctx.invoked_subcommand is not None:
        return
    _run_codex_interactive("max", dangerously_bypass=force, extra_args=["--search"])


@app.command()
def glm(
    ctx: typer.Context,
    force: bool = False,
    native: bool = False,
) -> None:
    """Run GLM model."""
    if ctx.invoked_subcommand is not None:
        return
    _run_codex_interactive("glm", dangerously_bypass=force, extra_args=["--search"])


@app.command()
def haiku(
    ctx: typer.Context,
    force: bool = False,
    native: bool = False,
) -> None:
    """Run Haiku model."""
    if ctx.invoked_subcommand is not None:
        return
    _run_codex_interactive("haiku", dangerously_bypass=force, extra_args=["--search"])


@app.command()
def opus(
    ctx: typer.Context,
    force: bool = False,
    native: bool = False,
) -> None:
    """Run Opus model."""
    if ctx.invoked_subcommand is not None:
        return
    _run_codex_interactive("opus", dangerously_bypass=force, extra_args=["--search"])


@app.command()
def sonnet(
    ctx: typer.Context,
    force: bool = False,
    native: bool = False,
) -> None:
    """Run Sonnet model."""
    if ctx.invoked_subcommand is not None:
        return
    _run_codex_interactive("sonnet", dangerously_bypass=force, extra_args=["--search"])


@app.command()
def ultra(
    ctx: typer.Context,
    force: bool = False,
    native: bool = False,
) -> None:
    """Run Ultra model."""
    if ctx.invoked_subcommand is not None:
        return
    _run_codex_interactive("ultra", dangerously_bypass=force, extra_args=["--search"])


@app.command()
def high(
    ctx: typer.Context,
    force: bool = False,
    native: bool = False,
) -> None:
    """Run high model."""
    if ctx.invoked_subcommand is not None:
        return
    _run_codex_interactive("high", dangerously_bypass=force, extra_args=["--search"])


@app.command()
def xhigh(
    ctx: typer.Context,
    force: bool = False,
    native: bool = False,
) -> None:
    """Run xhigh model."""
    if ctx.invoked_subcommand is not None:
        return
    _run_codex_interactive("xhigh", dangerously_bypass=force, extra_args=["--search"])


@app.command()
def run(
    model_alias: str,
    prompt: str,
    remote: str | None = None,
) -> None:
    """Run a model with a prompt."""
    _run_model_cmd(model_alias, prompt)


@app.command()
def bg(
    model_alias: str,
    prompt: str,
    remote: str | None = None,
    owner: str | None = None,
) -> None:
    """Run a model in background."""
    from thegent.cli import bg_cmd
    canonical_model = _MODEL_ALIAS.get(model_alias, model_alias)
    bg_cmd(model=canonical_model, prompt=prompt, remote=remote, owner=owner)


@app.command()
def resume(
    ctx: typer.Context,
    args: list[str] = typer.Argument(["--last"]),
) -> None:
    """Resume previous codex session."""
    _exec_native_codex(["resume"] + args)


@app.command()
def fork(
    ctx: typer.Context,
) -> None:
    """Fork current codex session."""
    _exec_native_codex(["fork"])


__all__ = [
    "app",
    "_DEX_BYPASS_FLAG",
    "_DEX_YOLO_FLAG",
    "_MODEL_ALIAS",
    "_get_codex_env",
    "_resolve_provider_for_model",
    "_run_codex_interactive",
    "_run_model_cmd",
    "_exec_native_codex",
    "resolve_codex_cli_path",
    "wrap_with_caffeinate",
    "default_dex",
]
