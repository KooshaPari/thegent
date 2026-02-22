"""Roid CLI: Factory Droid-backed interactive harness with dex/clode-style aliases."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console

console = Console()
GEMINI_FLASH_MODEL = "gemini-3-flash"

app = typer.Typer(
    help="Factory Droid-backed interactive harness (roid).",
    invoke_without_command=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)

_MODEL_ALIAS: dict[str, str] = {
    "dex": "gpt-5.3-codex",
    "codex": "gpt-5.3-codex",
    "composer": "composer-1.5",
    "max": "MiniMax-M2.5",
    "glm": "zai-glm-5",
    "haiku": "claude-haiku-4.5",
    "opus": "claude-opus-4.6",
    "sonnet": "claude-sonnet-4.5",
    "step": "step-3.5-flash",
    "step3.5": "step-3.5-flash",
    "ultra": "nvidia/llama-3.1-nemotron-ultra-253b-v1",
    "flash": "gemini-3-flash",
    "high": "gpt-5.3-codex-high",
    "xhigh": "gpt-5.3-codex-xhigh",
    "mini": "gpt-5-mini",
    "free": "gpt-5-mini",
}


def _is_thegent_shim(path: str) -> bool:
    p = Path(path)
    if "thegent-shims" in p.name:
        return True
    try:
        if p.is_symlink() and "thegent-shims" in str(p.readlink()):
            return True
    except OSError:
        pass
    return False


def _resolve_native_droid_cmd() -> str | None:
    override = os.environ.get("THGENT_NATIVE_DROID_BIN")
    candidates: list[str] = []
    if override:
        candidates.append(override)
    candidates.extend(
        [
            str(Path.home() / ".factory" / "bin" / "droid"),
            str(Path.home() / ".local" / "bin" / "droid"),
            str(Path("/opt/homebrew/bin/droid")),
            str(Path("/usr/local/bin/droid")),
        ]
    )
    which_droid = shutil.which("droid")
    if which_droid:
        candidates.append(which_droid)

    for candidate in candidates:
        p = Path(candidate).expanduser()
        if p.is_file() and os.access(p, os.X_OK) and not _is_thegent_shim(str(p)):
            return str(p)
    return None


def _resolve_droid_cmd() -> str:
    candidates = [
        Path.home() / ".local" / "bin" / "droid",
        Path.home() / ".factory" / "bin" / "droid",
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return str(candidate)
    return shutil.which("droid") or "droid"


def _run_droid_with_alias(alias: str, passthrough_args: list[str]) -> None:
    model = _MODEL_ALIAS.get(alias.lower(), alias)
    droid_cmd = _resolve_droid_cmd()

    # Headless path: droid expects model on exec subcommand (-m/--model), not at top-level.
    if passthrough_args and passthrough_args[0] == "exec":
        cmd = [droid_cmd, "exec", "-m", model, *passthrough_args[1:]]
    else:
        cmd = [droid_cmd, "--model", model, *passthrough_args]
    try:
        proc = subprocess.run(cmd, check=False)
    except FileNotFoundError:
        console.print(
            "[red]droid CLI not found.[/red] Install via: [dim]curl -fsSL https://app.factory.ai/Union[cli, sh][/dim]"
        )
        raise typer.Exit(1) from None

    if proc.returncode != 0:
        raise typer.Exit(proc.returncode)


@app.callback(invoke_without_command=True)
def default_roid(
    ctx: typer.Context,
    native: bool = typer.Option(
        False,
        "--native",
        help="Bypass cliproxy/thegent routing and run native droid directly",
    ),
) -> None:
    """Default roid behavior: flash model (gemini-3-flash)."""
    if native:
        droid_cmd = _resolve_native_droid_cmd()
        if not droid_cmd:
            console.print(
                "[red]Error: native 'droid' CLI not found (or only thegent-shims was found).[/red]\n"
                "[dim]Set THGENT_NATIVE_DROID_BIN=/absolute/path/to/droid to force a specific binary.[/dim]"
            )
            raise typer.Exit(1)
        passthrough = [arg for arg in sys.argv[1:] if arg != "--native"]
        cmd = [droid_cmd, *passthrough]
        console.print("[bold green]Starting native Droid (proxy bypass)...[/bold green]")
        os.execvpe(cmd[0], cmd, os.environ.copy())

    if ctx.invoked_subcommand is None:
        _run_droid_with_alias("flash", list(ctx.args))


@app.command("composer", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def roid_composer(ctx: typer.Context) -> None:
    _run_droid_with_alias("composer", list(ctx.args))


@app.command("max", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def roid_max(ctx: typer.Context) -> None:
    _run_droid_with_alias("max", list(ctx.args))


@app.command("glm", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def roid_glm(ctx: typer.Context) -> None:
    _run_droid_with_alias("glm", list(ctx.args))


@app.command("haiku", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def roid_haiku(ctx: typer.Context) -> None:
    _run_droid_with_alias("haiku", list(ctx.args))


@app.command("opus", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def roid_opus(ctx: typer.Context) -> None:
    _run_droid_with_alias("opus", list(ctx.args))


@app.command("sonnet", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def roid_sonnet(ctx: typer.Context) -> None:
    _run_droid_with_alias("sonnet", list(ctx.args))


@app.command("step", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def roid_step(ctx: typer.Context) -> None:
    _run_droid_with_alias("step", list(ctx.args))


@app.command("ultra", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def roid_ultra(ctx: typer.Context) -> None:
    _run_droid_with_alias("ultra", list(ctx.args))


@app.command("flash", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def roid_flash(ctx: typer.Context) -> None:
    _run_droid_with_alias("flash", list(ctx.args))


@app.command("high", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def roid_high(ctx: typer.Context) -> None:
    _run_droid_with_alias("high", list(ctx.args))


@app.command("xhigh", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def roid_xhigh(ctx: typer.Context) -> None:
    _run_droid_with_alias("xhigh", list(ctx.args))


@app.command("mini", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def roid_mini(ctx: typer.Context) -> None:
    _run_droid_with_alias("mini", list(ctx.args))


@app.command("free", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def roid_free(ctx: typer.Context) -> None:
    _run_droid_with_alias("free", list(ctx.args))


def _install_harness_link(bin_dir: Path, harness: str, force: bool = False) -> bool:
    """Install a harness symlink to thegent-shims. Returns True when link is created/updated."""
    shims_path = shutil.which("thegent-shims")
    if not shims_path:
        candidate = bin_dir / "thegent-shims"
        if candidate.exists():
            shims_path = str(candidate)
    if not shims_path:
        console.print(
            "[red]thegent-shims not found.[/red] Install it first with: [dim]zsh scripts/install-thegent-shims.sh[/dim]"
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


@app.command("doctor")
def roid_doctor(
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
def roid_config(
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
    """Install/update roid -> thegent-shims harness shim under ~/.local/bin."""
    if not bin_dir.exists():
        from thegent.errors import print_error

        print_error(f"{bin_dir} does not exist.")
        raise typer.Exit(1)

    if _install_harness_link(bin_dir, "roid", force=force):
        console.print(f"[green]Installed[/green] {bin_dir / 'roid'} -> thegent-shims")
        return
    console.print(f"[yellow]Skipping {bin_dir / 'roid'} (already exists). Use --force to overwrite.[/yellow]")


if __name__ == "__main__":
    app()
