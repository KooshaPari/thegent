"""Roid CLI: Factory Droid-backed interactive harness with dex/clode-style aliases."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import typer
from rich.console import Console

if TYPE_CHECKING:
    from collections.abc import Iterator

console = Console()
GEMINI_FLASH_MODEL = "gemini-3-flash"

app = typer.Typer(
    help="Factory Droid-backed interactive harness (roid).",
    invoke_without_command=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)

_MODEL_ALIAS: dict[str, str] = {
    "composer": "composer-1.5",
    "max": "minimax-m2.5",
    "glm": "glm-5",
    "haiku": "claude-haiku-4.5",
    "opus": "claude-opus-4.6",
    "sonnet": "claude-sonnet-4.5",
    "step": "step-3.5-flash",
    "step3.5": "step-3.5-flash",
    "ultra": "nvidia/llama-3.1-nemotron-ultra-253b-v1",
    "flash": GEMINI_FLASH_MODEL,
    "mini": "gpt-5-mini",
    "free": "gpt-5-mini",
}


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
    cmd = [_resolve_droid_cmd(), "--model", model, *passthrough_args]
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
def default_roid(ctx: typer.Context) -> None:
    """Default roid behavior: flash model (gemini-3-flash)."""
    if ctx.invoked_subcommand is None:
        _run_droid_with_alias("flash", list(ctx.args))


@app.command("composer")
def roid_composer(ctx: typer.Context) -> None:
    _run_droid_with_alias("composer", list(ctx.args))


@app.command("max")
def roid_max(ctx: typer.Context) -> None:
    _run_droid_with_alias("max", list(ctx.args))


@app.command("glm")
def roid_glm(ctx: typer.Context) -> None:
    _run_droid_with_alias("glm", list(ctx.args))


@app.command("haiku")
def roid_haiku(ctx: typer.Context) -> None:
    _run_droid_with_alias("haiku", list(ctx.args))


@app.command("opus")
def roid_opus(ctx: typer.Context) -> None:
    _run_droid_with_alias("opus", list(ctx.args))


@app.command("sonnet")
def roid_sonnet(ctx: typer.Context) -> None:
    _run_droid_with_alias("sonnet", list(ctx.args))


@app.command("step")
def roid_step(ctx: typer.Context) -> None:
    _run_droid_with_alias("step", list(ctx.args))


@app.command("ultra")
def roid_ultra(ctx: typer.Context) -> None:
    _run_droid_with_alias("ultra", list(ctx.args))


@app.command("flash")
def roid_flash(ctx: typer.Context) -> None:
    _run_droid_with_alias("flash", list(ctx.args))


@app.command("mini")
def roid_mini(ctx: typer.Context) -> None:
    _run_droid_with_alias("mini", list(ctx.args))


@app.command("free")
def roid_free(ctx: typer.Context) -> None:
    _run_droid_with_alias("free", list(ctx.args))


def _iter_install_targets() -> Iterator[tuple[str, str, str]]:
    yield ("roid", "thegent roid", "roid")
    yield ("roidcomposer", "thegent roid composer", "roidcomposer")
    yield ("roidmax", "thegent roid max", "roidmax")
    yield ("roidglm", "thegent roid glm", "roidglm")
    yield ("roidhaiku", "thegent roid haiku", "roidhaiku")
    yield ("roidopus", "thegent roid opus", "roidopus")
    yield ("roidsonnet", "thegent roid sonnet", "roidsonnet")
    yield ("roidstep", "thegent roid step", "roidstep")
    yield ("roidultra", "thegent roid ultra", "roidultra")
    yield ("roidflash", "thegent roid flash", "roidflash")
    yield ("roidmini", "thegent roid mini", "roidmini")
    yield ("roidfree", "thegent roid free", "roidfree")


def _write_wrapper(path: Path, command: str, force: bool = False) -> bool:
    if path.exists() and not force:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'#!/usr/bin/env sh\nset -e\nexport THGENT_HARNESS="droid"\nexec {command} "$@"\n')
    path.chmod(0o755)
    return True


@app.command("doctor")
def roid_doctor(
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
    """Install roid shims under ~/.local/bin."""
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
