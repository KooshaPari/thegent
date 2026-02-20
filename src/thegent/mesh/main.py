"""heliosShield: High-performance CLI for agent mesh orchestration."""

from pathlib import Path
from typing import Optional

import typer

from thegent.mesh.mesh import heliosShieldMesh
from thegent.mesh.observability import mesh_status_cmd

app = typer.Typer(help="heliosShield: Agent Mesh Orchestration")

@app.command("status")
def status(mesh_root: Path = typer.Option(Path("/tmp/agent-mesh"), help="Path to mesh root")):
    """Show current mesh status."""
    mesh_status_cmd(mesh_root)

@app.command("init")
def init(mesh_root: Path = typer.Option(Path("/tmp/agent-mesh"), help="Path to mesh root")):
    """Initialize agent mesh."""
    mesh = heliosShieldMesh(mesh_root)

@app.command("discover")
def discover(
    patterns: str = typer.Option("claude,aider,cursor", help="Comma-separated agent process patterns"),
    mesh_root: Path = typer.Option(Path("/tmp/agent-mesh"), help="Path to mesh root")
):
    """Discover active agents and register them."""
    mesh = heliosShieldMesh(mesh_root)
    pattern_list = [p.strip() for p in patterns.split(",")]
    agents = mesh.discover_agents(pattern_list)
    for _a in agents:
        pass

if __name__ == "__main__":
    app()
