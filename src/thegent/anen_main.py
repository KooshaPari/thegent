"""Backward-compatible anen entrypoint layered on canonical ``fanta_main``."""

from __future__ import annotations

import subprocess

import typer
from thegent.fanta_main import app as app

from thegent import fanta_main as _fanta_main

console = _fanta_main.console
GEMINI_FLASH_MODEL = _fanta_main.GEMINI_FLASH_MODEL
_MODEL_ALIAS = _fanta_main._MODEL_ALIAS
_is_thegent_wrapper = _fanta_main._is_thegent_wrapper
_install_harness_link = _fanta_main._install_harness_link
anen_doctor = _fanta_main.anen_doctor
anen_config = _fanta_main.anen_config
fanta_doctor = _fanta_main.fanta_doctor
fanta_config = _fanta_main.fanta_config


def _resolve_anen_cmd() -> str:  # pyright: ignore[reportUnusedFunction] -- re-exported compatibility shim
    return _fanta_main._resolve_anen_cmd()


def _run_anen_with_alias(alias: str, passthrough_args: list[str]) -> None:  # pyright: ignore[reportUnusedFunction] -- re-exported compatibility shim
    model = _MODEL_ALIAS.get(alias.lower(), alias)
    anen_cmd = _resolve_anen_cmd()

    if passthrough_args and passthrough_args[0] == "exec":
        cmd = [anen_cmd, "exec", "-m", model, *passthrough_args[1:]]
    else:
        cmd = [anen_cmd, "--model", model, *passthrough_args]
    try:
        proc = subprocess.run(cmd, check=False)
    except FileNotFoundError:
        console.print("[red]Resolved anen binary is not executable.[/red]")
        raise typer.Exit(1) from None

    if proc.returncode != 0:
        raise typer.Exit(proc.returncode)


def default_anen(ctx: typer.Context) -> None:
    """Legacy callback that preserves monkeypatch points for anen tests."""
    if ctx.invoked_subcommand is None:
        _run_anen_with_alias("flash", list(ctx.args))


# Rebind runner path so anen module monkeypatches affect CLI behavior.
_fanta_main._run_anen_with_alias = _run_anen_with_alias

default_fanta = default_anen  # pyright: ignore[reportUnusedVariable] -- re-exported compatibility shim
_resolve_fanta_cmd = _resolve_anen_cmd  # pyright: ignore[reportUnusedVariable] -- re-exported compatibility shim
_run_fanta_with_alias = _run_anen_with_alias  # pyright: ignore[reportUnusedVariable] -- re-exported compatibility shim

if __name__ == "__main__":
    app()
