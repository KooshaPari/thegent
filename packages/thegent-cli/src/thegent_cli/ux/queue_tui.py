"""WP-7002: Queue TUI for managing deferred prompts."""

from pathlib import Path

from rich.console import Console
from rich.live import Live
from rich.table import Table

from thegent.queue.storage import PromptQueue


class QueueTUI:
    """Rich-based TUI for the prompt queue."""

    def __init__(self, session_dir: Path) -> None:
        self.pq = PromptQueue(session_dir)
        self.console = Console()

    def render_table(self) -> Table:
        """Render the queue as a Rich Table."""
        items = self.pq.list_pending()
        table = Table(title="Deferred Prompt Queue ($defer)", expand=True)
        table.add_column("Index", style="dim", width=6)
        table.add_column("Timestamp", style="cyan", width=20)
        table.add_column("Agent", style="magenta", width=12)
        table.add_column("Project", style="green")
        table.add_column("Prompt", style="white", no_wrap=False)

        for i, item in enumerate(items):
            table.add_row(
                str(i),
                item.get("ts", "")[:19],
                item.get("agent") or "any",
                item.get("project", ""),
                item.get("prompt", "")[:100] + ("..." if len(item.get("prompt", "")) > 100 else ""),
            )
        return table

    def show(self) -> None:
        """Show the queue once."""
        self.console.print(self.render_table())

    def watch(self, interval: float = 2.0) -> None:
        """Watch the queue live."""
        with Live(self.render_table(), refresh_per_second=1 / interval) as live:
            try:
                while True:
                    live.update(self.render_table())
                    import time

                    time.sleep(interval)
            except KeyboardInterrupt:
                pass
