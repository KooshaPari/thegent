"""Fanta CLI: Antigma-backed interactive harness with dex/clode/roid-style aliases."""

from __future__ import annotations

import os
import shutil
from thegent.infra.shim_subprocess import run as shim_run
import sys
from pathlib import Path

import typer
from rich.console import Console

console = Console()
GEMINI_FLASH_MODEL = "gemini-3-flash"

app = typer.Typer(
    help="Antigma-backed interactive harness (fanta).",
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
    "flash": GEMINI_FLASH_MODEL,
    "high": "gpt-5.3-codex-high",
    "xhigh": "gpt-5.3-codex-xhigh",
    "mini": "gpt-5-mini",
    "free": "gpt-5-mini",
}


def _resolve_anen_cmd() -> str:
    override = os.environ.get("THGENT_NATIVE_ANTE_BIN") or os.environ.get("THGENT_NATIVE_ANEN_BIN")
    candidates: list[str] = []
    if override:
        candidates.append(override)
    candidates.extend(
        [
            str(Path.home() / ".ante" / "bin" / "ante"),
            str(Path.home() / ".antigma" / "bin" / "anen"),
            str(Path("/opt/homebrew/bin/ante")),
            str(Path("/usr/local/bin/ante")),
            str(Path("/opt/homebrew/bin/anen")),
            str(Path("/usr/local/bin/anen")),
        ]
    )
    for binary in ("ante", "anen"):
        resolved = shutil.which(binary)
        if resolved:
            candidates.append(resolved)

    for candidate in candidates:
        path = Path(candidate).expanduser()
        if not (path.is_file() and os.access(path, os.X_OK)):
            continue
        if _is_thegent_wrapper(path):
            continue
        return str(path)

    console.print(
        "[red]Native ante CLI not found (or only thegent wrapper was found).[/red]\n"
        "[dim]Install ante and ensure ~/.ante/bin is on PATH.[/dim]\n"
        "[dim]Set THGENT_NATIVE_ANTE_BIN=/absolute/path/to/ante to force a specific binary.[/dim]"
    )
    raise typer.Exit(1)


def _is_thegent_wrapper(path: Path) -> bool:
    if "thegent-shims" in path.name:
        return True

    try:
        resolved = path.resolve()
    except OSError:
        return False

    current = Path(sys.argv[0]).expanduser()
    try:
        if current.exists() and resolved == current.resolve():
            return True
    except OSError:
        pass

    try:
        if path.is_symlink() and "thegent-shims" in str(path.readlink()):
            return True
    except OSError:
        pass

    # Detect shell wrapper scripts that invoke `thegent anen` or module entrypoint.
    try:
        if path.suffix == "" and path.stat().st_size < 8192:
            contents = path.read_text(encoding="utf-8", errors="ignore")
            if (
                "thegent anen" in contents
                or "thegent fanta" in contents
                or "python -m thegent.anen_main" in contents
                or "from thegent.anen_main import app" in contents
            ):
                return True
    except OSError:
        pass
    return False


def _run_anen_with_alias(alias: str, passthrough_args: list[str]) -> None:
    model = _MODEL_ALIAS.get(alias.lower(), alias)
    anen_cmd = _resolve_anen_cmd()

    # Headless path: anen exec expects model on exec subcommand (-m/--model).
    if passthrough_args and passthrough_args[0] == "exec":
        cmd = [anen_cmd, "exec", "-m", model, *passthrough_args[1:]]
    else:
        cmd = [anen_cmd, "--model", model, *passthrough_args]
    try:
        proc = shim_run(cmd, check=False)
    except FileNotFoundError:
        console.print("[red]Resolved anen binary is not executable.[/red]")
        raise typer.Exit(1) from None

    if proc.returncode != 0:
        raise typer.Exit(proc.returncode)


@app.callback(invoke_without_command=True)
def default_anen(ctx: typer.Context) -> None:
    """Default fanta behavior: flash model (gemini-3-flash)."""
    if ctx.invoked_subcommand is None:
        _run_anen_with_alias("flash", list(ctx.args))


@app.command("composer", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def anen_composer(ctx: typer.Context) -> None:
    _run_anen_with_alias("composer", list(ctx.args))


@app.command("max", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def anen_max(ctx: typer.Context) -> None:
    _run_anen_with_alias("max", list(ctx.args))


@app.command("glm", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def anen_glm(ctx: typer.Context) -> None:
    _run_anen_with_alias("glm", list(ctx.args))


@app.command("haiku", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def anen_haiku(ctx: typer.Context) -> None:
    _run_anen_with_alias("haiku", list(ctx.args))


@app.command("opus", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def anen_opus(ctx: typer.Context) -> None:
    _run_anen_with_alias("opus", list(ctx.args))


@app.command("sonnet", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def anen_sonnet(ctx: typer.Context) -> None:
    _run_anen_with_alias("sonnet", list(ctx.args))


@app.command("step", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def anen_step(ctx: typer.Context) -> None:
    _run_anen_with_alias("step", list(ctx.args))


@app.command("ultra", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def anen_ultra(ctx: typer.Context) -> None:
    _run_anen_with_alias("ultra", list(ctx.args))


@app.command("flash", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def anen_flash(ctx: typer.Context) -> None:
    _run_anen_with_alias("flash", list(ctx.args))


@app.command("high", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def anen_high(ctx: typer.Context) -> None:
    _run_anen_with_alias("high", list(ctx.args))


@app.command("xhigh", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def anen_xhigh(ctx: typer.Context) -> None:
    _run_anen_with_alias("xhigh", list(ctx.args))


@app.command("mini", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def anen_mini(ctx: typer.Context) -> None:
    _run_anen_with_alias("mini", list(ctx.args))


@app.command("free", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def anen_free(ctx: typer.Context) -> None:
    _run_anen_with_alias("free", list(ctx.args))


@app.command("exec", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def anen_exec(
    ctx: typer.Context,
    model: str = typer.Option("flash", "-m", "--model", help="Model alias (dex, high, xhigh, max, glm, flash, etc.)"),
    prompt: str = typer.Argument(..., help="Prompt to run headlessly"),
) -> None:
    """Run Antigma headlessly with model alias mapping."""
    _run_anen_with_alias(model, ["exec", prompt, *list(ctx.args)])


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


@app.command("doctor")
def anen_doctor(
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
def anen_config(
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
        help="Directory to install harness shim symlinks",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
) -> None:
    """Install/update fanta/antigma -> thegent-shims under ~/.local/bin."""
    if not bin_dir.exists():
        from thegent.errors import print_error

        print_error(f"{bin_dir} does not exist.")
        raise typer.Exit(1)

    installed = 0
    for harness in ("fanta", "antigma"):
        target = bin_dir / harness
        if _install_harness_link(bin_dir, harness, force=force):
            installed += 1
            console.print(f"[green]Installed[/green] {target} -> thegent-shims")
        else:
            console.print(f"[yellow]Skipping {target} (already exists). Use --force to overwrite.[/yellow]")

    if installed:
        console.print("[bold]Harness links installed successfully.[/bold]")
    elif not force:
        console.print("[yellow]No links updated.[/yellow]")


if __name__ == "__main__":
    app()

# Canonical fanta names (anen compatibility remains available).
default_fanta = default_anen
_resolve_fanta_cmd = _resolve_anen_cmd
_run_fanta_with_alias = _run_anen_with_alias
fanta_doctor = anen_doctor
fanta_config = anen_config
