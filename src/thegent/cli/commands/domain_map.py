"""Domain map command implementation.

Advisor-mode guidance for Cloudflare Tunnel + DNS domain mapping.
Apply mode is intentionally disabled until idempotent API execution is implemented.
"""

from __future__ import annotations

from urllib.parse import urlparse


def parse_domain_mapping(domain_input: str) -> dict:
    """Parse a domain mapping input into structured data."""
    parsed = urlparse(domain_input) if "://" in domain_input else urlparse(f"https://{domain_input}")
    return {
        "domain": parsed.netloc or parsed.path,
        "scheme": parsed.scheme or "https",
        "path": parsed.path,
    }


def validate_domain_mapping(mapping: dict) -> list[str]:
    """Validate a domain mapping and return any errors."""
    errors = []
    if not mapping.get("domain"):
        errors.append("Domain is required")
    return errors


def domain_map_cmd(
    domain: str,
    target: str = "http://localhost:3847",
    mode: str = "advisor",
    registrar: str = "porkbun",
    dns_provider: str = "cloudflare",
    tunnel_name: str = "thegent",
    format: str = "rich",
) -> None:
    """Guide domain mapping setup (advisor mode) for Cloudflare Tunnel + DNS."""
    from rich.console import Console
    import typer
    
    console = Console()
    
    # Parse and validate domain
    mapping = parse_domain_mapping(domain)
    errors = validate_domain_mapping(mapping)
    
    if errors:
        for error in errors:
            console.print(f"[red]Error: {error}[/red]")
        raise typer.Exit(1)
    
    if format == "json":
        import json
        output = {
            "domain": mapping["domain"],
            "target": target,
            "dns_provider": dns_provider,
            "tunnel_name": tunnel_name,
            "mode": mode,
        }
        console.print(json.dumps(output))
        return
        
    if mode == "advisor":
        console.print("[bold cyan]Domain Mapping Advisor[/bold cyan]")
        console.print(f"Domain: [green]{mapping['domain']}[/green]")
        console.print(f"Target: [green]{target}[/green]")
        console.print(f"DNS Provider: [green]{dns_provider}[/green]")
        console.print(f"Tunnel Name: [green]{tunnel_name}[/green]")
        console.print("[bold]Steps to configure:[/bold]")
        console.print(f"1. Install Cloudflare tunnel: cloudflared tunnel create {tunnel_name}")
        console.print("2. Configure DNS: Add CNAME record pointing to tunnel")
        console.print(f"3. Update tunnel config to route {domain} -> {target}")
        console.print(f"4. Start tunnel: cloudflared tunnel run {tunnel_name}")
        
    elif mode == "apply":
        console.print("[yellow]Apply mode not yet implemented.[/yellow]")
        console.print("Run in advisor mode for setup instructions.")
        raise typer.Exit(1)
