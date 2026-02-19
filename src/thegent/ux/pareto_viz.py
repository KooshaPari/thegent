"""WP-1009: Pareto frontier visualization for model selection."""

from typing import Any

from rich.console import Console
from rich.table import Table


class ParetoViz:
    """Visualizes the Pareto frontier of model/provider options."""

    def __init__(self) -> None:
        self.console = Console()

    def show_frontier(
        self, model_id: str, routes: list[Any], speed_map: dict[str, float], quality_map: dict[str, float]
    ) -> None:
        """Display a table of routes showing their Pareto status."""
        table = Table(title=f"Pareto Frontier for '{model_id}'", expand=True)
        table.add_column("Provider", style="cyan")
        table.add_column("Speed (0-1)", style="green")
        table.add_column("Quality (0-1)", style="magenta")
        table.add_column("Cost Weight", style="yellow")
        table.add_column("Pareto Efficient?", style="bold")

        # Mock Pareto logic for viz
        for r in routes:
            speed = speed_map.get(r.provider, r.accuracy_score)  # fallback
            quality = quality_map.get(r.provider, r.accuracy_score)

            # Simple check: is there any route that is better in ALL dimensions?
            is_pareto = True
            for other in routes:
                if other == r:
                    continue
                other_speed = speed_map.get(other.provider, other.accuracy_score)
                other_quality = quality_map.get(other.provider, other.accuracy_score)
                if other_speed >= speed and other_quality >= quality and other.cost_weight <= r.cost_weight:
                    if other_speed > speed or other_quality > quality or other.cost_weight < r.cost_weight:
                        is_pareto = False
                        break

            table.add_row(
                r.provider,
                f"{speed:.2f}",
                f"{quality:.2f}",
                f"{r.cost_weight:.2f}",
                "[green]YES[/green]" if is_pareto else "[red]NO[/red]",
            )

        self.console.print(table)
