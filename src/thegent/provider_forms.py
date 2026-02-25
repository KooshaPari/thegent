"""Interactive forms for provider management using Rich.

This module provides interactive CLI forms for managing providers.
It uses lazy imports to avoid circular dependencies with provider_model_manager.
"""

from typing import Any

from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

console = Console()


def _get_manager_functions():
    """Lazy import to avoid circular dependency."""
    from thegent.provider_model_manager import (
        add_api_key,
        add_provider,
        delete_provider,
        discover_models,
        list_credentials,
        list_providers,
        remove_api_key,
        update_provider,
        validate_provider,
    )
    return {
        "add_api_key": add_api_key,
        "add_provider": add_provider,
        "delete_provider": delete_provider,
        "discover_models": discover_models,
        "list_credentials": list_credentials,
        "list_providers": list_providers,
        "remove_api_key": remove_api_key,
        "update_provider": update_provider,
        "validate_provider": validate_provider,
    }


def run_provider_form() -> None:
    """Interactive form for provider management."""
    fns = _get_manager_functions()
    
    console.print("\n[bold cyan]Provider Management[/bold cyan]\n")

    while True:
        console.print("\n[bold]Choose an action:[/bold]")
        console.print("  1. List providers")
        console.print("  2. Add provider")
        console.print("  3. Update provider")
        console.print("  4. Delete provider")
        console.print("  5. Validate provider")
        console.print("  6. List credentials")
        console.print("  7. Add API key")
        console.print("  8. Remove API key")
        console.print("  9. Discover models")
        console.print("  0. Exit")

        choice = Prompt.ask("[bold]Choice[/bold]", default="0")

        if choice == "0":
            break
        if choice == "1":
            _form_list_providers(fns)
        elif choice == "2":
            _form_add_provider(fns)
        elif choice == "3":
            _form_update_provider(fns)
        elif choice == "4":
            _form_delete_provider(fns)
        elif choice == "5":
            _form_validate_provider(fns)
        elif choice == "6":
            _form_list_credentials(fns)
        elif choice == "7":
            _form_add_api_key(fns)
        elif choice == "8":
            _form_remove_api_key(fns)
        elif choice == "9":
            _form_discover_models(fns)


def _form_list_providers(fns: dict) -> None:
    providers = fns["list_providers"]()
    if not providers:
        console.print("[yellow]No providers configured[/yellow]")
        return

    table = Table(title="Providers")
    table.add_column("Name", style="cyan")
    table.add_column("Base URL", style="dim")
    table.add_column("Model", style="green")
    table.add_column("Aliases", style="magenta")

    for p in providers:
        aliases = ", ".join(p.get("extra_aliases", []))
        table.add_row(
            p.get("name", ""),
            p.get("base_url", "")[:40],
            p.get("model", ""),
            aliases[:30],
        )

    console.print(table)


def _form_add_provider(fns: dict) -> None:
    console.print("\n[bold]Add New Provider[/bold]\n")

    name = Prompt.ask("[bold]Provider name[/bold] (e.g., myprovider)")
    base_url = Prompt.ask("[bold]Base URL[/bold] (e.g., https://api.example.com/v1)")
    model = Prompt.ask("[bold]Default model[/bold] (e.g., gpt-4)")

    add_extra = Confirm.ask("[bold]Add extra aliases?[/bold]", default=False)
    extra_aliases = []
    if add_extra:
        aliases_input = Prompt.ask("[bold]Aliases[/bold] (comma-separated)", default="")
        extra_aliases = [a.strip() for a in aliases_input.split(",") if a.strip()]

    add_login = Confirm.ask("[bold]Add login instructions?[/bold]", default=False)
    login_url = ""
    login_instructions: list[str] = []
    if add_login:
        login_url = Prompt.ask("[bold]Login URL[/bold]")
        instr_input = Prompt.ask("[bold]Instructions[/bold] (one per line, empty to finish)")
        while instr_input:
            login_instructions.append(instr_input)
            instr_input = Prompt.ask("[bold]Next instruction[/bold] (empty to finish)", default="")

    add_creds = Confirm.ask("[bold]Add API key now?[/bold]", default=False)
    api_key = ""
    if add_creds:
        api_key = Prompt.ask("[bold]API Key[/bold]", password=True)

    success, msg = fns["add_provider"](
        name=name,
        base_url=base_url,
        model=model,
        login_url=login_url or None,
        login_instructions=login_instructions or None,
        extra_aliases=extra_aliases or None,
        api_key=api_key or None,
    )

    if success:
        console.print(f"[green]{msg}[/green]")
    else:
        console.print(f"[red]{msg}[/red]")


def _prompt_for_provider_selection(
    providers: list[dict[str, Any]],
    prompt_title: str,
    empty_message: str,
) -> dict[str, Any] | None:
    """Prompt user to select a provider from a numbered list."""
    if not providers:
        console.print(f"[yellow]{empty_message}[/yellow]")
        return None

    console.print(f"\n[bold]{prompt_title}[/bold]")
    for i, provider in enumerate(providers):
        console.print(f"  {i + 1}. {provider.get('name')}")

    idx = Prompt.ask("[bold]Provider number[/bold]", default="1")
    try:
        return providers[int(idx) - 1]
    except (ValueError, IndexError):
        console.print("[red]Invalid selection[/red]")
        return None


def _form_update_provider(fns: dict) -> None:
    providers = fns["list_providers"]()
    provider = _prompt_for_provider_selection(
        providers,
        prompt_title="Select Provider to Update",
        empty_message="No providers to update",
    )
    if not provider:
        return

    name = provider.get("name")
    console.print(f"\n[bold]Updating: {name}[/bold]\n")

    base_url = Prompt.ask(
        "[bold]New base URL[/bold] (leave empty to keep current)", default=provider.get("base_url", "")
    )
    model = Prompt.ask("[bold]New model[/bold] (leave empty to keep current)", default=provider.get("model", ""))

    success, msg = fns["update_provider"](
        name=str(name),
        base_url=base_url or None,
        model=model or None,
    )

    if success:
        console.print(f"[green]{msg}[/green]")
    else:
        console.print(f"[red]{msg}[/red]")


def _form_delete_provider(fns: dict) -> None:
    providers = fns["list_providers"]()
    provider = _prompt_for_provider_selection(
        providers,
        prompt_title="Select Provider to Delete",
        empty_message="No providers to delete",
    )
    if not provider:
        return

    if Confirm.ask(f"[bold]Delete provider '{provider.get('name')}'?[/bold]", default=False):
        success, msg = fns["delete_provider"](str(provider.get("name")))
        if success:
            console.print(f"[green]{msg}[/green]")
        else:
            console.print(f"[red]{msg}[/red]")


def _form_validate_provider(fns: dict) -> None:
    providers = fns["list_providers"]()
    provider = _prompt_for_provider_selection(
        providers,
        prompt_title="Select Provider to Validate",
        empty_message="No providers to validate",
    )
    if not provider:
        return

    console.print(f"\n[dim]Validating {provider.get('name')}...[/dim]")
    success, msg, _details = fns["validate_provider"](str(provider.get("name")))

    if success:
        console.print(f"[green]✓ {msg}[/green]")
    else:
        console.print(f"[red]✗ {msg}[/red]")


def _form_list_credentials(fns: dict) -> None:
    creds = fns["list_credentials"]()
    if not creds:
        console.print("[yellow]No credentials configured[/yellow]")
        return

    table = Table(title="Credentials")
    table.add_column("Type", style="cyan")
    table.add_column("Provider", style="green")
    table.add_column("Details", style="dim")

    for c in creds:
        details = c.get("file") or c.get("base_url", "")[:30]
        table.add_row(c.get("type", ""), c.get("provider", ""), details)

    console.print(table)


def _form_add_api_key(fns: dict) -> None:
    providers = fns["list_providers"]()
    provider = _prompt_for_provider_selection(
        providers,
        prompt_title="Select Provider for API Key",
        empty_message="No providers available",
    )
    if not provider:
        return

    api_key = Prompt.ask(f"[bold]API Key for {provider.get('name')}[/bold]", password=True)

    success, msg = fns["add_api_key"](str(provider.get("name")), api_key)
    if success:
        console.print(f"[green]{msg}[/green]")
    else:
        console.print(f"[red]{msg}[/red]")


def _form_remove_api_key(fns: dict) -> None:
    providers = fns["list_providers"]()
    provider = _prompt_for_provider_selection(
        providers,
        prompt_title="Select Provider to Remove API Key",
        empty_message="No providers available",
    )
    if not provider:
        return

    if Confirm.ask(f"[bold]Remove API key for '{provider.get('name')}'?[/bold]", default=False):
        success, msg = fns["remove_api_key"](str(provider.get("name")))
        if success:
            console.print(f"[green]{msg}[/green]")
        else:
            console.print(f"[red]{msg}[/red]")


def _form_discover_models(fns: dict) -> None:
    console.print("\n[dim]Discovering models from CLIProxy...[/dim]")
    discovery = fns["discover_models"](include_status=True)
    models: list[dict[str, Any]] = discovery.get("models", [])
    status: dict[str, Any] = discovery.get("discovery", {})

    if not models:
        if status.get("status") != "ok":
            console.print(
                f"[yellow]Discovery degraded:[/yellow] {status.get('failure_type', 'unknown')} - {status.get('error_message', '')}"
            )
        console.print("[yellow]No models discovered (is CLIProxy running?)[/yellow]")
        return

    table = Table(title="Discovered Models")
    table.add_column("Model ID", style="cyan")
    table.add_column("Provider", style="green")
    table.add_column("Created", style="dim")

    for m in models[:50]:  # Limit to 50
        created = str(m.get("created", ""))[:8]
        table.add_row(m.get("id", "")[:40], m.get("provider", ""), created)

    console.print(table)
    console.print(f"\n[dim]Showing {min(50, len(models))} of {len(models)} models[/dim]")


__all__ = [
    "run_provider_form",
    "_form_list_providers",
    "_form_add_provider",
    "_form_update_provider",
    "_form_delete_provider",
    "_form_validate_provider",
    "_form_list_credentials",
    "_form_add_api_key",
    "_form_remove_api_key",
    "_form_discover_models",
    "_prompt_for_provider_selection",
]
