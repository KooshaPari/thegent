"""Domain mapping stream: registrar + DNS + tunnel workflows."""

from __future__ import annotations

import typer

app = typer.Typer(help="Domain mapping and exposure workflows.")


@app.command("map", help="Guide domain mapping setup (advisor mode) for Cloudflare Tunnel + DNS.")
def domain_map(
    domain: str = typer.Argument(..., help="Domain or subdomain to expose (example.com or app.example.com)"),
    target: str = typer.Option(
        "http://localhost:3847",
        "--target",
        "-t",
        help="Local service URL that Cloudflare Tunnel should route to.",
    ),
    mode: str = typer.Option("advisor", "--mode", help="Execution mode: advisor|apply"),
    registrar: str = typer.Option("porkbun", "--registrar", help="Domain registrar."),
    dns_provider: str = typer.Option("cloudflare", "--dns-provider", help="Authoritative DNS provider."),
    tunnel_name: str = typer.Option("thegent", "--tunnel-name", help="Cloudflare tunnel name."),
    format: str = typer.Option("rich", "--format", "-F", help="Output format: rich|json|md"),
) -> None:
    from thegent.cli.commands.domain_map import domain_map_cmd

    domain_map_cmd(
        domain=domain,
        target=target,
        mode=mode,
        registrar=registrar,
        dns_provider=dns_provider,
        tunnel_name=tunnel_name,
        format=format,
    )
