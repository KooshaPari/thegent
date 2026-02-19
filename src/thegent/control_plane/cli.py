"""CLI commands for thegent Control Plane."""

import typer
from rich.console import Console

app = typer.Typer(help="Control plane: multi-tenant config service")
console = Console()


@app.command("status")
def control_plane_status() -> None:
    """Check the health and status of the control plane."""
    import os
    cp_url = os.environ.get("THGENT_CONTROL_PLANE_URL")
    if not cp_url:
        console.print("[yellow]THGENT_CONTROL_PLANE_URL not set.[/yellow] System is running in [bold]embedded mode[/bold].")
        return

    import httpx
    try:
        with httpx.Client(timeout=2.0) as client:
            response = client.get(f"{cp_url.rstrip('/')}/health")
            if response.status_code == 200:
                data = response.json()
                console.print(f"[green]Control Plane is UP[/green] (version {data.get('version', 'unknown')})")
                console.print(f"URL: {cp_url}")
            else:
                console.print(f"[red]Control Plane returned error {response.status_code}[/red]")
    except Exception as e:
        console.print(f"[red]Control Plane is DOWN or unreachable[/red]: {e}")


@app.command("serve")
def control_plane_serve(
    host: str = typer.Option("127.0.0.1", "--host", help="Bind address"),
    port: int = typer.Option(3848, "--port", help="Bind port"),
    reload: bool = typer.Option(False, "--reload", help="Enable hot reload"),
) -> None:
    """Start the Control Plane configuration service (Phase 2)."""
    console.print(f"[bold cyan]thegent control-plane serve[/bold cyan] on http://{host}:{port}")
    
    # Check if granian/uvicorn is available
    import uvicorn
    from thegent.control_plane.server import app as fastapi_app
    
    uvicorn.run(fastapi_app, host=host, port=port, reload=reload)
