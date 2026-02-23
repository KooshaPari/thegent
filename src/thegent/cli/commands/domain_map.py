"""Domain map command implementation.

Advisor-mode guidance for Cloudflare Tunnel + DNS domain mapping.
Apply mode is intentionally disabled until idempotent API execution is implemented.
"""

from __future__ import annotations

import json
import re
from urllib.parse import urlparse

import typer

_DOMAIN_RE = re.compile(r"^(?=.{1,253}$)(?!-)(?:[a-z0-9-]{1,63}\.)+[a-z]{2,63}$", re.IGNORECASE)

_ADVISOR_STEPS = [
    "Delegate nameservers at {registrar} to Cloudflare for the apex zone",
    "Authenticate cloudflared: cloudflared tunnel login",
    "Create tunnel: cloudflared tunnel create {tunnel_name}",
    "Route DNS: cloudflared tunnel route dns {tunnel_name} {domain}",
    "Create or verify CNAME in Cloudflare DNS: {domain} -> {tunnel_name}.cfargotunnel.com",
    "Write ingress in ~/.cloudflared/config.yml mapping hostname {domain} to service {target}",
    "Start tunnel: cloudflared tunnel run {tunnel_name}",
    "Verify DNS: dig +short {domain} CNAME",
    "Verify endpoint: curl -I https://{domain}",
]


def _validate_domain(value: str) -> str:
    domain = value.strip().rstrip(".").lower()
    if not _DOMAIN_RE.match(domain):
        typer.echo("Error: domain must be a valid FQDN (example.com or app.example.com)")
        raise typer.Exit(2)
    return domain


def _validate_target(value: str) -> str:
    target = value.strip()
    parsed = urlparse(target)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        typer.echo("Error: target must be an absolute URL (http://localhost:3847)")
        raise typer.Exit(2)
    return target


def _validate_mode(value: str) -> str:
    mode = value.strip().lower()
    if mode not in {"advisor", "apply"}:
        typer.echo("Error: mode must be advisor or apply")
        raise typer.Exit(2)
    return mode


def _build_steps(domain: str, target: str, registrar: str, tunnel_name: str) -> list[str]:
    return [s.format(domain=domain, target=target, registrar=registrar, tunnel_name=tunnel_name) for s in _ADVISOR_STEPS]


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
    domain = _validate_domain(domain)
    target = _validate_target(target)
    mode = _validate_mode(mode)

    if mode == "apply":
        typer.echo("Error: Apply mode is intentionally not enabled yet")
        raise typer.Exit(2)

    steps = _build_steps(domain=domain, target=target, registrar=registrar, tunnel_name=tunnel_name)
    output_format = format.strip().lower()

    if output_format == "json":
        payload = {
            "mode": mode,
            "domain": domain,
            "target": target,
            "registrar": registrar,
            "dns_provider": dns_provider,
            "tunnel_name": tunnel_name,
            "steps": steps,
            "assumptions": [
                "Cloudflare account and cloudflared are available on the operator machine",
                "DNS authority is delegated to Cloudflare",
                "Target endpoint is reachable from the host running cloudflared",
            ],
        }
        typer.echo(json.dumps(payload, indent=2))
        return

    if output_format == "md":
        typer.echo(f"# Domain Mapping Advisor: {domain}\n")
        typer.echo(f"- Mode: `{mode}`")
        typer.echo(f"- Registrar: `{registrar}`")
        typer.echo(f"- DNS Provider: `{dns_provider}`")
        typer.echo(f"- Tunnel Name: `{tunnel_name}`")
        typer.echo(f"- Target: `{target}`\n")
        typer.echo("## Checklist\n")
        for i, step in enumerate(steps, 1):
            typer.echo(f"{i}. {step}")
        return

    if output_format != "rich":
        typer.echo("Error: format must be rich, json, or md")
        raise typer.Exit(2)

    typer.echo(f"Domain Mapping Advisor: {domain}")
    typer.echo(f"Target    : {target}")
    typer.echo(f"Mode      : {mode}")
    typer.echo(f"Registrar : {registrar}")
    typer.echo(f"DNS       : {dns_provider}")
    typer.echo(f"Tunnel    : {tunnel_name}")
    typer.echo("\nSteps:")
    for step in steps:
        typer.echo(f"  - {step}")
