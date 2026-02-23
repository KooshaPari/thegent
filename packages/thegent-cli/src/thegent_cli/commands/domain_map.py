"""Domain map command implementation.

Advisor-mode guidance for Cloudflare Tunnel + DNS domain mapping.
Apply mode is intentionally not enabled — all mutations must be
performed manually by the operator after reviewing the advisor output.
"""

from __future__ import annotations

import json

import typer

_ADVISOR_STEPS = [
    "Log in to Cloudflare: cloudflared tunnel login",
    "Create tunnel: cloudflared tunnel create {tunnel_name}",
    "Add CNAME record: {domain} → {tunnel_name}.cfargotunnel.com",
    "Route DNS: cloudflared tunnel route dns {tunnel_name} {domain}",
    "Configure ingress in ~/.cloudflared/config.yml targeting {target}",
    "Start tunnel: cloudflared tunnel run {tunnel_name}",
    "Verify propagation: dig {domain} CNAME",
]


def domain_map_cmd(
    domain: str,
    target: str,
    mode: str,
    registrar: str,
    dns_provider: str,
    tunnel_name: str,
    format: str,
) -> None:
    """Emit domain mapping guidance or raise Exit(2) on invalid inputs."""
    if "." not in domain:
        typer.echo("Error: domain must include at least one dot")
        raise typer.Exit(2)

    if mode == "apply":
        typer.echo("Error: Apply mode is intentionally not enabled yet")
        raise typer.Exit(2)

    steps = [s.format(domain=domain, tunnel_name=tunnel_name, target=target) for s in _ADVISOR_STEPS]

    if format == "json":
        payload = {
            "mode": mode,
            "domain": domain,
            "target": target,
            "tunnel_name": tunnel_name,
            "steps": steps,
        }
        typer.echo(json.dumps(payload))
    elif format == "md":
        typer.echo(f"# Domain Mapping: {domain}\n")
        for i, step in enumerate(steps, 1):
            typer.echo(f"{i}. {step}")
    else:
        typer.echo(f"Domain Mapping Advisor: {domain}")
        typer.echo(f"Target : {target}")
        typer.echo(f"Mode   : {mode}")
        typer.echo(f"Tunnel : {tunnel_name}")
        typer.echo("\nSteps:")
        for step in steps:
            typer.echo(f"  • {step}")
