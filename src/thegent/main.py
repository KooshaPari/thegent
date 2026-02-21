"""Thegent CLI entry point redirect.
Migrated to the apps structure for 2026.
"""

from pathlib import Path

import typer

from thegent.cli.apps.main import app
from thegent.cli.apps.sync import app as sync_app
from thegent.clode_main import sitback_cmd

__all__ = ["app", "sync_app"]


# Expose sitback on the top-level app (`thegent sitback ...`) in addition to harness-local entry points.
app.command("sitback", help="Start Sitback harness (claude/codex/droid/antigma).")(sitback_cmd)


@app.command("roid", help="Factory Droid-backed interactive harness.")
def roid_cmd(
    prompt: str = typer.Argument("", help="Optional prompt to pass to the Factory Droid harness"),
) -> None:
    """Factory Droid-backed interactive harness."""
    typer.echo("Launching roid (Factory Droid harness)...")
    import subprocess
    import sys

    args = ["thegent", "run", "--harness", "droid"]
    if prompt:
        args.append(prompt)
    result = subprocess.run(args, check=False)
    raise typer.Exit(result.returncode)


_SHIM_SCRIPTS: dict[str, str] = {
    "codex": ('#!/usr/bin/env bash\n# thegent accelerator: routes to dex|clode harness\nexec thegent dex|clode "$@"\n'),
    "roid": ('#!/usr/bin/env bash\nexport THGENT_HARNESS="droid"\nexec thegent roid "$@"\n'),
    "dex": ('#!/usr/bin/env bash\nexport THGENT_HARNESS="codex"\nexec thegent dex "$@"\n'),
    "clode": ('#!/usr/bin/env bash\nexport THGENT_HARNESS="claude"\nexec thegent clode "$@"\n'),
}


def _install_agent_accelerators(bin_dir: Path, force: bool = False) -> None:
    """Write shell script shims for codex, roid, dex, and clode into bin_dir."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    for name, script in _SHIM_SCRIPTS.items():
        target = bin_dir / name
        if target.exists() and not force:
            continue
        target.write_text(script, encoding="utf-8")
        target.chmod(target.stat().st_mode | 0o111)  # noqa: S103 -- executable shim script


def main() -> None:  # @trace WL-040 WP-4001
    """CLI entry point with actionable error formatting."""
    import sys

    try:
        app()
    except Exception as exc:
        from thegent.infra.enhanced_errors import format_error

        import typer

        typer.echo(f"Error: {format_error(exc)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
