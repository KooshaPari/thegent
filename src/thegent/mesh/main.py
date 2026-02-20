"""heliosShield: High-performance CLI for agent mesh orchestration."""

from pathlib import Path
from typing import Optional

import typer

from thegent.mesh.mesh import MeshManager
from thegent.mesh.observability import mesh_status_cmd

app = typer.Typer(help="Mesh: Local agent mesh coordination (init, status, discover).")


@app.command("status")
def status(mesh_root: Path | None = typer.Option(None, "--mesh-root", help="Path to mesh root")):
    """Show current mesh status."""
    from thegent.config import ThegentSettings

    root = mesh_root or Path(ThegentSettings().harness_root)
    mesh_status_cmd(root)


@app.command("init")
def init(mesh_root: Path | None = typer.Option(None, "--mesh-root", help="Path to mesh root")):
    """Initialize agent mesh."""
    from thegent.config import ThegentSettings

    root = mesh_root or Path(ThegentSettings().harness_root)
    MeshManager(root)
    print(f"Mesh initialized at {root}")


@app.command("discover")
def discover(
    patterns: str = typer.Option("claude,aider,cursor", help="Comma-separated agent process patterns"),
    mesh_root: Path | None = typer.Option(None, "--mesh-root", help="Path to mesh root"),
):
    """Discover active agents and register them."""
    from thegent.config import ThegentSettings

    root = mesh_root or Path(ThegentSettings().harness_root)
    mesh = MeshManager(root)
    pattern_list = [p.strip() for p in patterns.split(",")]
    agents = mesh.discover_agents(pattern_list)
    print(f"Discovered {len(agents)} agents.")
    for a in agents:
        print(f"  - {a['name']} (PID: {a['pid']})")


if __name__ == "__main__":
    app()
