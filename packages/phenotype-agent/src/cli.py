"""Agent roles CLI — render YAML specs to agents/ markdown."""

from __future__ import annotations

from pathlib import Path

import typer

app = typer.Typer(name="roles", help="Agent roles library commands.")

_LIBRARY_DIR = Path(__file__).parent / "library"
_DEFAULT_AGENTS_DIR = Path(__file__).parent.parent.parent / "agents"
_DEFAULT_HOOK_CONFIG = Path(__file__).parent.parent.parent / "hooks" / "hook-config.yaml"


def _all_yaml_files() -> list[Path]:
    """List all YAML role spec files in library directory.

    Returns:
        Sorted list of YAML file paths.
    """
    return sorted(_LIBRARY_DIR.rglob("*.yaml"))


@app.command("render-all")
def render_all(
    agents_dir: Path = typer.Option(
        _DEFAULT_AGENTS_DIR,
        help="Output agents/ directory",
    ),
    no_register: bool = typer.Option(
        False,
        "--no-register",
        help="Skip hook registration",
    ),
) -> None:
    """Render all role YAML specs to agents/ markdown files."""
    from agent_roles.hook_registrar import HookRegistrar
    from agent_roles.renderer import RoleRenderer
    from agent_roles.spec import AgentRoleSpec

    renderer = RoleRenderer(agents_dir=agents_dir)
    registrar = HookRegistrar(hook_config_path=_DEFAULT_HOOK_CONFIG) if not no_register else None
    count = 0
    for yaml_file in _all_yaml_files():
        spec = AgentRoleSpec.from_yaml(yaml_file)
        path = renderer.render(spec)
        if registrar:
            registrar.register(spec)
        typer.echo(f"  {spec.category}/{spec.name} → {path.name}")
        count += 1
    typer.echo(f"\nRendered {count} roles.")


@app.command("render")
def render_single(
    name: str = typer.Argument(
        ...,
        help="Role name (e.g. property_tester)",
    ),
    agents_dir: Path = typer.Option(
        _DEFAULT_AGENTS_DIR,
        help="Output agents/ directory",
    ),
    no_register: bool = typer.Option(
        False,
        "--no-register",
        help="Skip hook registration",
    ),
) -> None:
    """Render a single role by name.

    Args:
        name: Role name to render.
        agents_dir: Output directory for rendered markdown.
        no_register: If True, skip hook registration.

    Raises:
        typer.Exit: If role not found.
    """
    from agent_roles.hook_registrar import HookRegistrar
    from agent_roles.renderer import RoleRenderer
    from agent_roles.spec import AgentRoleSpec

    matches = [f for f in _all_yaml_files() if f.stem == name]
    if not matches:
        typer.echo(f"Role '{name}' not found.", err=True)
        raise typer.Exit(1)

    spec = AgentRoleSpec.from_yaml(matches[0])
    renderer = RoleRenderer(agents_dir=agents_dir)
    path = renderer.render(spec)
    if not no_register and _DEFAULT_HOOK_CONFIG.exists():
        HookRegistrar(hook_config_path=_DEFAULT_HOOK_CONFIG).register(spec)
    typer.echo(f"Rendered: {path}")


@app.command("list")
def list_roles() -> None:
    """List all available role specs."""
    for yaml_file in _all_yaml_files():
        typer.echo(f"  {yaml_file.parent.name}/{yaml_file.stem}")
