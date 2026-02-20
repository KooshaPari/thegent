"""Sub-stream: Model and Provider Management."""

import typer
from rich.console import Console

app = typer.Typer(help="Manage custom models and providers.")
console = Console()


@app.command("tui", help="Launch rich TUI for model management.")
def models_tui():
    """Launch rich TUI for adding and managing custom models/providers."""
    try:
        from thegent.ui.models_tui import models_tui_main

        models_tui_main()
    except Exception as e:
        console.print(f"[red]Error: Failed to launch Models TUI: {e}[/red]")


@app.command("list", help="List all models in the catalog.")
def models_list():
    """List all models in the catalog (static + custom)."""
    from rich.table import Table

    from thegent.models.catalog import ModelCatalog

    catalog = ModelCatalog.to_contract_view(use_scraped=False)
    routes = catalog.get("routes", {})

    table = Table(title="Model Catalog (Static + Custom)")
    table.add_column("Model ID", style="cyan")
    table.add_column("Provider", style="green")
    table.add_column("Alias", style="yellow")
    table.add_column("Type", style="magenta")
    table.add_column("Prio", justify="right")
    table.add_column("Cost", justify="right")

    for model_id, model_routes in sorted(routes.items()):
        for r in model_routes:
            table.add_row(
                model_id,
                str(r.get("provider")),
                str(r.get("model_alias")),
                str(r.get("backend_type")),
                str(r.get("priority")),
                f"{r.get('cost_weight'):.2f}",
            )

    console.print(table)
