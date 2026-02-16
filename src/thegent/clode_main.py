"""Claude-backed interactive agent CLI (clode)."""

import contextlib
import os
import shutil
import subprocess
from collections import Counter
from collections.abc import Iterator
from pathlib import Path

import typer
from rich.console import Console

# Import thegent CLI commands to reuse them.
from thegent.cli import bg_cmd, history_cmd, inspect_cmd, logs_cmd, ps_cmd, run_cmd, status_cmd, stop_cmd, wait_cmd
from thegent.config import ThegentSettings

console = Console()
app = typer.Typer(help="Claude-backed interactive agent CLI (clode)")

_GLM_OFFER_SET: tuple[str, ...] = ("nim", "kilo", "zai", "minimax", "glm")
_GLM_OFFER_COST: dict[str, float] = {
    "nim": 0.22,
    "kilo": 0.28,
    "zai": 0.34,
    "minimax": 0.36,
    "glm": 0.80,
}
_GLM_PREFERRED_BACKENDS: frozenset[str] = frozenset({"glm", "zai", "kilo", "nim", "minimax", "openrouter"})
_GLM_POLICY_COUNTER: Counter[str] = Counter()


def _glm_offer_backends() -> tuple[str, ...]:
    """Return GLM offer set in deterministic order."""
    return _GLM_OFFER_SET


@app.callback(invoke_without_command=True)
def default_clode(ctx: typer.Context) -> None:
    """Start an interactive Nim-backed Claude session when no provider command is provided."""
    if ctx.invoked_subcommand is None:
        _run_claude_interactive("nim")


def _iter_install_targets() -> Iterator[tuple[str, str, str]]:
    """Return shim targets and their backing commands."""
    yield ("clode", "thegent clode", "clode")
    yield ("claudeglm", "thegent clode glm", "claudeglm")
    yield ("claudemax", "thegent clode max", "claudemax")


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
        return min(_glm_offer_backends(), key=lambda backend: (_GLM_OFFER_COST.get(backend, 999.0), backend))
    return f"glm:{policy_name}"


def _write_wrapper(path: Path, command: str, force: bool = False) -> bool:
    """Write/update a shim wrapper. Returns True if a write occurred."""
    if path.exists() and not force:
        return False

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'#!/usr/bin/env sh\nset -e\nexec {command} "$@"\n')
    path.chmod(0o755)
    return True


def _get_claude_env(provider: str) -> dict[str, str]:
    """Get environment variables for Claude Code pointing to thegent proxy."""
    settings = ThegentSettings()
    env = os.environ.copy()
    env["ANTHROPIC_BASE_URL"] = f"http://{settings.mcp_host}:{settings.mcp_port}/v1"
    env["ANTHROPIC_API_KEY"] = provider
    return env


def _run_claude_interactive(provider: str) -> None:
    """Start an interactive Claude Code session."""
    env = _get_claude_env(provider)
    claude_path = shutil.which("claude")
    if not claude_path:
        console.print("[red]Error: 'claude' (Claude Code) CLI not found in PATH.[/red]")
        console.print("[dim]Install it via: npm install -g @anthropic-ai/claude-code[/dim]")
        raise typer.Exit(1)

    console.print(f"[bold green]Starting interactive Claude session via {provider} proxy...[/bold green]")
    console.print(f"[dim]Proxy URL: {env['ANTHROPIC_BASE_URL']}[/dim]")
    with contextlib.suppress(KeyboardInterrupt):
        subprocess.run([claude_path], env=env, check=False)


def create_provider_app(provider: str) -> typer.Typer:
    """Create a subcommand group for a provider."""
    provider_app = typer.Typer(help=f"{provider.upper()} Claude-backed operations")

    @provider_app.callback(invoke_without_command=True)
    def main(ctx: typer.Context) -> None:
        """Default to interactive shell if no subcommand is given."""
        if ctx.invoked_subcommand is None:
            _run_claude_interactive(provider)

    @provider_app.command("run")
    def clode_run(
        prompt: str,
        cd: str | None = typer.Option(None, "--cd", "-d", help="Working directory"),
        mode: str = typer.Option("write", "--mode", "-m", help="write | read-only"),
        timeout: int = typer.Option(90, "--timeout", "-t", help="Timeout in seconds"),
    ) -> None:
        """Run a task via Claude Code using the proxy (synchronous)."""
        os.environ.update(_get_claude_env(provider))
        run_cmd(
            prompt=prompt,
            agent="claude",
            cd=Path(cd) if cd else None,
            mode=mode,
            timeout=timeout,
        )

    @provider_app.command("bg")
    def clode_bg(
        prompt: str,
        cd: str | None = typer.Option(None, "--cd", "-d", help="Working directory"),
        mode: str = typer.Option("write", "--mode", "-m", help="write | read-only"),
        timeout: int = typer.Option(90, "--timeout", "-t", help="Timeout in seconds"),
        owner: str | None = typer.Option(None, "--owner", "-o", help="Owner tag"),
    ) -> None:
        """Start a background task via Claude Code using the proxy."""
        os.environ.update(_get_claude_env(provider))
        bg_cmd(
            prompt=prompt,
            agent="claude",
            cd=Path(cd) if cd else None,
            mode=mode,
            timeout=timeout,
            full=False,
            model=None,
            owner=owner,
        )

    provider_app.command("ps")(ps_cmd)
    provider_app.command("logs")(logs_cmd)
    provider_app.command("status")(status_cmd)
    provider_app.command("stop")(stop_cmd)
    provider_app.command("wait")(wait_cmd)
    provider_app.command("inspect")(inspect_cmd)
    provider_app.command("history")(history_cmd)

    return provider_app


app.add_typer(create_provider_app("nim"), name="nim")
app.add_typer(create_provider_app("openrouter"), name="openrouter")
app.add_typer(create_provider_app("kilo"), name="kilo")
app.add_typer(create_provider_app("zai"), name="zai")
app.add_typer(create_provider_app("minimax"), name="minimax")


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
        help="Backend lock: auto|nim|kilo|minimax|zai|openrouter",
    ),
) -> None:
    """Start an interactive GLM session with policy-based balancing."""
    token = _resolve_clode_token("glm", prefer=prefer, policy=policy)
    _run_claude_interactive(token)


@app.command("max")
def clode_max() -> None:
    """Legacy shortcut for OpenRouter-backed Claude sessions."""
    _run_claude_interactive("openrouter")


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
