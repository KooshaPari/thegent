"""CLI entry point for thegent-mcp server."""

from __future__ import annotations

import typer

from thegent_mcp.server import mcp

app = typer.Typer()


@app.command()
def main(
    host: str = typer.Option("127.0.0.1", "--host", help="Bind host"),
    port: int = typer.Option(3848, "--port", help="Bind port"),
) -> None:
    """Start thegent-mcp server."""
    mcp.run(transport="sse")


if __name__ == "__main__":
    app()
