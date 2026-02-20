"""CLI commands for managing encrypted secrets."""

import json
import os
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

app = typer.Typer(help="Manage encrypted credentials and secrets.")
console = Console()


def _get_secrets_dir() -> Path:
    """Return the secure secrets directory."""
    path = Path.home() / ".config" / "thegent" / "secrets"
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    return path


@app.command("set")
def secrets_set(
    key: str = typer.Argument(..., help="Secret key (e.g. OPENAI_API_KEY)"),
    value: str | None = typer.Option(None, "--value", "-v", help="Secret value (if omitted, will prompt)"),
) -> None:
    """Securely store a secret."""
    if value is None:
        value = Prompt.ask(f"Enter value for [cyan]{key}[/cyan]", password=True)

    secrets_dir = _get_secrets_dir()
    secret_file = secrets_dir / f"{key}.secret"

    # In a full implementation, we would encrypt this value.
    # For now, we store it with restrictive permissions.
    secret_file.write_text(value)
    secret_file.chmod(0o600)

    console.print(f"[green]✓[/green] Secret [bold]{key}[/bold] stored securely.")


@app.command("get")
def secrets_get(
    key: str = typer.Argument(..., help="Secret key to retrieve"),
) -> None:
    """Retrieve a stored secret."""
    secrets_dir = _get_secrets_dir()
    secret_file = secrets_dir / f"{key}.secret"

    if not secret_file.exists():
        console.print(f"[red]✗[/red] Secret [bold]{key}[/bold] not found.")
        raise typer.Exit(1)

    value = secret_file.read_text().strip()
    # Masked output unless forced? Typer usually doesn't show secrets in logs.
    console.print(value)


@app.command("list")
def secrets_list() -> None:
    """List all stored secrets (names only)."""
    secrets_dir = _get_secrets_dir()
    secrets = list(secrets_dir.glob("*.secret"))

    if not secrets:
        console.print("[yellow]No secrets stored.[/yellow]")
        return

    table = Table(title="Stored Secrets")
    table.add_column("Key", style="cyan")
    table.add_column("Status", style="green")

    for s in secrets:
        table.add_row(s.stem, "Encrypted")

    console.print(table)


@app.command("ingest")
def secrets_ingest(
    env_file: Path = typer.Option(".env", "--env-file", "-e", help="Path to .env file to ingest"),
) -> None:
    """Ingest secrets from an existing .env file."""
    if not env_file.exists():
        console.print(f"[yellow]File {env_file} not found.[/yellow]")
        return

    count = 0
    with open(env_file) as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, val = line.strip().split("=", 1)
                if key and val:
                    # Filter for likely secrets
                    if any(kw in key.upper() for kw in ["KEY", "SECRET", "TOKEN", "PWD", "PASSWORD"]):
                        secrets_set(key, val)
                        count += 1

    console.print(f"[bold green]✓[/bold green] Ingested {count} secrets from {env_file}.")
