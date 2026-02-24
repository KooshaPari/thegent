"""Form-based UI for provider management.

Extracted from provider_model_manager.py for maintainability.
"""

from __future__ import annotations

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

console = Console()


def run_provider_form() -> None:
    """Interactive form for provider management."""
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
        console.print("  0. Exit")

        choice = Prompt.ask("[bold]Choice[/bold]", default="0")

        if choice == "0":
            break
        if choice == "1":
            _form_list_providers()
        elif choice == "2":
            _form_add_provider()
        elif choice == "3":
            _form_update_provider()
        elif choice == "4":
            _form_delete_provider()
        elif choice == "5":
            _form_validate_provider()
        elif choice == "6":
            _form_list_credentials()
        elif choice == "7":
            _form_add_api_key()
        elif choice == "8":
            _form_remove_api_key()


def _form_list_providers() -> None:
    from thegent.provider_crud import list_providers
    providers = list_providers()
    if not providers:
        console.print("[yellow]No providers configured[/yellow]")
        return
    table = Table(title="Providers")
    table.add_column("Name", style="cyan")
    table.add_column("Base URL", style="dim")
    table.add_column("Model", style="green")
    for p in providers:
        table.add_row(p.get("name", ""), p.get("base_url", "")[:40], p.get("model", ""))
    console.print(table)


def _form_add_provider() -> None:
    from thegent.provider_crud import add_provider
    name = Prompt.ask("[bold]Provider name[/bold]")
    base_url = Prompt.ask("[bold]Base URL[/bold]")
    model = Prompt.ask("[bold]Default model[/bold]")
    api_key = Prompt.ask("[bold]API key[/bold] (optional)", default="", password=True)
    success, msg = add_provider(name=name, base_url=base_url, model=model, api_key=api_key or None)
    console.print(f"[green]{msg}[/green]" if success else f"[red]{msg}[/red]")


def _form_update_provider() -> None:
    from thegent.provider_crud import get_provider, update_provider
    name = Prompt.ask("[bold]Provider name to update[/bold]")
    existing = get_provider(name)
    if not existing:
        console.print(f"[red]Provider '{name}' not found[/red]")
        return
    base_url = Prompt.ask("[bold]New base URL[/bold] (empty to keep)", default="")
    model = Prompt.ask("[bold]New model[/bold] (empty to keep)", default="")
    success, msg = update_provider(name=name, base_url=base_url or None, model=model or None)
    console.print(f"[green]{msg}[/green]" if success else f"[red]{msg}[/red]")


def _form_delete_provider() -> None:
    from thegent.provider_crud import delete_provider
    name = Prompt.ask("[bold]Provider name to delete[/bold]")
    if Prompt.ask(f"Delete '{name}'?", choices=["y", "n"], default="n") == "y":
        success, msg = delete_provider(name)
        console.print(f"[green]{msg}[/green]" if success else f"[red]{msg}[/red]")


def _form_validate_provider() -> None:
    from thegent.provider_crud import validate_provider
    name = Prompt.ask("[bold]Provider to validate[/bold]")
    success, msg, details = validate_provider(name)
    console.print(f"[green]{msg}[/green]" if success else f"[red]{msg}[/red]")
    if details:
        console.print(f"Details: {details}")


def _form_list_credentials() -> None:
    from thegent.provider_crud import list_credentials
    credentials = list_credentials()
    if not credentials:
        console.print("[yellow]No credentials[/yellow]")
        return
    table = Table(title="Credentials")
    table.add_column("Provider", style="cyan")
    table.add_column("Has Key", style="green")
    for c in credentials:
        table.add_row(c.get("provider", ""), "Yes" if c.get("has_api_key") else "No")
    console.print(table)


def _form_add_api_key() -> None:
    from thegent.provider_crud import add_api_key
    provider = Prompt.ask("[bold]Provider[/bold]")
    api_key = Prompt.ask("[bold]API key[/bold]", password=True)
    success, msg = add_api_key(provider, api_key)
    console.print(f"[green]{msg}[/green]" if success else f"[red]{msg}[/red]")


def _form_remove_api_key() -> None:
    from thegent.provider_crud import remove_api_key
    provider = Prompt.ask("[bold]Provider[/bold]")
    success, msg = remove_api_key(provider)
    console.print(f"[green]{msg}[/green]" if success else f"[red]{msg}[/red]")


__all__ = ["run_provider_form"]
