"""Rich TUI for adding models and providers with full harness configuration.

Covers:
- Provider-model mapping (provider_definitions, model aliases)
- Per-harness config (cliproxy openai-compatibility, ensure-config)
- API key injection, validation, credentials
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

console = Console()

# OAuth-only providers use login flow, not API key
_OAUTH_ONLY = frozenset({"claude", "codex"})


def _header() -> None:
    console.print()
    console.print(
        Panel(
            "[bold cyan]Models & Providers Setup[/bold cyan]\n"
            "[dim]Add providers, map models, configure harness (CLIProxyAPIPlus)[/dim]",
            border_style="cyan",
        )
    )


def _menu() -> str:
    console.print()
    console.print("[bold]Actions:[/bold]")
    console.print("  [cyan]1[/cyan]. Add provider (base URL, model, aliases, login)")
    console.print("  [cyan]2[/cyan]. Add model alias to provider")
    console.print("  [cyan]3[/cyan]. Add common model alias")
    console.print("  [cyan]4[/cyan]. Configure harness (ensure-config + API key)")
    console.print("  [cyan]5[/cyan]. List providers & models")
    console.print("  [cyan]6[/cyan]. Validate provider")
    console.print("  [cyan]0[/cyan]. Exit")
    return Prompt.ask("[bold]Choice[/bold]", default="0")


def _add_provider() -> None:
    from thegent_routing.provider_model_manager import add_provider

    console.print(Panel("[bold]Add New Provider[/bold]", border_style="green"))
    console.print("[dim]Provider = API source (e.g. openrouter, my-custom-api)[/dim]\n")

    name = Prompt.ask("[bold]Provider name[/bold] (e.g. openrouter, myapi)", default="")
    if not name.strip():
        console.print("[yellow]Cancelled.[/yellow]")
        return
    name = name.lower().strip()

    if name in _OAUTH_ONLY:
        console.print(f"[yellow]Provider '{name}' uses OAuth. Use: [bold]thegent cliproxy login {name}[/bold][/yellow]")
        return

    base_url = Prompt.ask(
        "[bold]Base URL[/bold] (e.g. https://api.example.com/v1)",
        default="",
    )
    if not base_url.strip():
        console.print("[red]Base URL is required.[/red]")
        return

    model = Prompt.ask(
        "[bold]Default model[/bold] (e.g. gpt-4, google/gemini-2.0-flash-001)",
        default="",
    )
    if not model.strip():
        console.print("[red]Default model is required.[/red]")
        return

    base_url_env = Prompt.ask(
        "[bold]Base URL env var[/bold] (optional, e.g. THGENT_MYAPI_BASE_URL)",
        default="",
    )
    base_url_env = base_url_env.strip() or None

    aliases_input = Prompt.ask(
        "[bold]Extra model aliases[/bold] (comma-separated, optional)",
        default="",
    )
    extra_aliases = [a.strip() for a in aliases_input.split(",") if a.strip()] or None

    add_login = Confirm.ask("[bold]Add login instructions?[/bold]", default=True)
    login_url = ""
    login_instructions: list[str] = []
    display_name = name.title()
    if add_login:
        login_url = Prompt.ask(
            "[bold]Login URL[/bold] (where users get API key)",
            default="",
        )
        display_name = Prompt.ask(
            "[bold]Display name[/bold] (e.g. OpenRouter)",
            default=name.title(),
        )
        console.print("[dim]Enter instructions (one per line, empty line to finish):[/dim]")
        while True:
            line = Prompt.ask("  Instruction", default="")
            if not line:
                break
            login_instructions.append(line)

    add_creds = Confirm.ask("[bold]Add API key now?[/bold]", default=False)
    api_key = ""
    if add_creds:
        api_key = Prompt.ask("[bold]API Key[/bold]", password=True) or ""

    success, msg = add_provider(
        name=name,
        base_url=base_url.strip(),
        model=model.strip(),
        login_url=login_url.strip() or None,
        login_instructions=login_instructions or None,
        display_name=display_name or None,
        extra_aliases=extra_aliases,
        api_key=api_key or None,
        base_url_env=base_url_env,
    )
    if success:
        console.print(f"[green]✓ {msg}[/green]")
        console.print("[dim]Run [bold]thegent cliproxy ensure-config[/bold] to refresh harness.[/dim]")
    else:
        console.print(f"[red]✗ {msg}[/red]")


def _add_model_alias() -> None:
    from thegent_routing.provider_model_manager import add_model_alias, list_providers

    providers = list_providers()
    if not providers:
        console.print("[yellow]No providers. Add one first.[/yellow]")
        return

    console.print(Panel("[bold]Add Model Alias to Provider[/bold]", border_style="green"))
    console.print("[dim]Alias = alternative name for the same model (e.g. glm-5 for z-ai/glm-5)[/dim]\n")

    for i, p in enumerate(providers):
        console.print(f"  [cyan]{i + 1}[/cyan]. {p.get('name')} (model: {p.get('model')})")
    idx = Prompt.ask("[bold]Provider number[/bold]", default="1")
    try:
        provider = providers[int(idx) - 1]
    except (ValueError, IndexError):
        console.print("[red]Invalid selection.[/red]")
        return

    alias = Prompt.ask("[bold]New alias[/bold] (e.g. glm-5)", default="")
    if not alias.strip():
        console.print("[yellow]Cancelled.[/yellow]")
        return

    success, msg = add_model_alias(provider["name"], provider.get("model", ""), alias.strip())
    if success:
        console.print(f"[green]✓ {msg}[/green]")
    else:
        console.print(f"[red]✗ {msg}[/red]")


def _add_common_alias() -> None:
    from thegent_routing.provider_model_manager import add_common_alias

    console.print(Panel("[bold]Add Common Model Alias[/bold]", border_style="green"))
    console.print("[dim]Common alias = works across providers (e.g. sonnet, opus)[/dim]\n")

    alias = Prompt.ask("[bold]Alias[/bold] (e.g. sonnet)", default="")
    if not alias.strip():
        console.print("[yellow]Cancelled.[/yellow]")
        return

    success, msg = add_common_alias(alias.strip())
    if success:
        console.print(f"[green]✓ {msg}[/green]")
    else:
        console.print(f"[red]✗ {msg}[/red]")


def _configure_harness() -> None:
    from thegent_agents.agents.cliproxy_manager import _ensure_config
    from thegent_core.config import ThegentSettings
    from thegent_routing.provider_model_manager import add_api_key, list_providers

    console.print(Panel("[bold]Configure Harness (CLIProxyAPIPlus)[/bold]", border_style="green"))
    console.print("[dim]Ensures cliproxy-config.yaml exists and is up to date.[/dim]\n")

    settings = ThegentSettings()
    config_path = _ensure_config(settings)
    console.print(f"[green]✓ Config: {config_path}[/green]")

    add_key = Confirm.ask("[bold]Add API key for a provider?[/bold]", default=False)
    if not add_key:
        console.print("[dim]Run [bold]thegent cliproxy ensure-config[/bold] to refresh.[/dim]")
        return

    providers = list_providers()
    api_key_providers = [p for p in providers if p.get("name") not in _OAUTH_ONLY]
    if not api_key_providers:
        console.print("[yellow]No API-key providers. Add one first.[/yellow]")
        return

    for i, p in enumerate(api_key_providers):
        console.print(f"  [cyan]{i + 1}[/cyan]. {p.get('name')}")
    idx = Prompt.ask("[bold]Provider number[/bold]", default="1")
    try:
        provider = api_key_providers[int(idx) - 1]
    except (ValueError, IndexError):
        console.print("[red]Invalid selection.[/red]")
        return

    api_key = Prompt.ask("[bold]API Key[/bold]", password=True)
    if not api_key:
        console.print("[yellow]No key entered.[/yellow]")
        return

    success, msg = add_api_key(provider["name"], api_key)
    if success:
        console.print(f"[green]✓ {msg}[/green]")
        console.print("[dim]Restart proxy: [bold]thegent cliproxy restart[/bold][/dim]")
    else:
        console.print(f"[red]✗ {msg}[/red]")


def _list_providers_models() -> None:
    from thegent_routing.provider_model_manager import list_models, list_providers

    providers = list_providers()
    if not providers:
        console.print("[yellow]No providers configured.[/yellow]")
        return

    table = Table(title="Providers", show_header=True, header_style="bold cyan")
    table.add_column("Name", style="cyan")
    table.add_column("Base URL", style="dim", max_width=40)
    table.add_column("Model", style="green")
    table.add_column("Aliases", style="magenta")
    table.add_column("Login", style="dim")

    for p in providers:
        aliases = ", ".join(p.get("extra_aliases", []))
        login = "Yes" if p.get("login") else "—"
        table.add_row(
            p.get("name", ""),
            (p.get("base_url", "") or "")[:40],
            p.get("model", ""),
            aliases[:30] if aliases else "—",
            login,
        )
    console.print(table)

    models = list_models()
    if models:
        console.print()
        mtable = Table(title="Models by Provider", show_header=True, header_style="bold cyan")
        mtable.add_column("Provider", style="cyan")
        mtable.add_column("Model", style="green")
        mtable.add_column("Aliases", style="magenta")
        for m in models[:20]:
            mtable.add_row(
                m.get("provider", ""),
                m.get("model", ""),
                ", ".join(m.get("aliases", []))[:40],
            )
        if len(models) > 20:
            mtable.add_row("…", f"{len(models) - 20} more", "")
        console.print(mtable)


def _validate_provider() -> None:
    from thegent_routing.provider_model_manager import list_providers, validate_provider

    providers = list_providers()
    if not providers:
        console.print("[yellow]No providers to validate.[/yellow]")
        return

    console.print(Panel("[bold]Validate Provider[/bold]", border_style="green"))
    for i, p in enumerate(providers):
        console.print(f"  [cyan]{i + 1}[/cyan]. {p.get('name')}")
    idx = Prompt.ask("[bold]Provider number[/bold]", default="1")
    try:
        provider = providers[int(idx) - 1]
    except (ValueError, IndexError):
        console.print("[red]Invalid selection.[/red]")
        return

    name = provider.get("name")
    if not name:
        console.print("[red]Invalid provider selection.[/red]")
        return
    console.print(f"\n[dim]Validating {name}...[/dim]")
    success, msg, details = validate_provider(name)
    if success:
        console.print(f"[green]✓ {msg}[/green]")
    else:
        console.print(f"[red]✗ {msg}[/red]")
        if details.get("has_credentials") is False:
            console.print("[dim]Add API key: option 4 in this menu, or thegent cliproxy login[/dim]")


def run_models_providers_tui() -> None:
    """Run the Rich TUI for models and providers setup."""
    _header()
    while True:
        choice = _menu()
        if choice == "0":
            console.print("\n[dim]Exit.[/dim]")
            break
        if choice == "1":
            _add_provider()
        elif choice == "2":
            _add_model_alias()
        elif choice == "3":
            _add_common_alias()
        elif choice == "4":
            _configure_harness()
        elif choice == "5":
            _list_providers_models()
        elif choice == "6":
            _validate_provider()
        else:
            console.print("[yellow]Unknown option.[/yellow]")
