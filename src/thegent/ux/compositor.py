"""Minimal TUI compositor for terminal panes.

Implements the research "Path B" MVP by hosting pane state in a Rich layout
and linking to external tmux sessions.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from thegent.infra import yaml_load
from thegent.tools.terminal import capture_tmux_pane, is_claude_code_pane, list_tmux_panes


class TUICompositor:
    """Collect tmux panes and compose a simple two-pane terminal dashboard."""

    def __init__(
        self,
        include_non_claude: bool = False,
        config_path: Path | None = None,
    ) -> None:
        self.include_non_claude = include_non_claude
        self.config_path = config_path or Path(".factory") / "tui-config.yaml"
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        defaults: dict[str, Any] = {"layout": "balanced", "preview_lines": 30}
        if not self.config_path.exists():
            return defaults
        raw = yaml_load(self.config_path)
        if not isinstance(raw, dict):
            return defaults
        return {**defaults, **raw}

    def collect_panes(self) -> list[Any]:
        panes = list_tmux_panes()
        if self.include_non_claude:
            return panes
        return [pane for pane in panes if is_claude_code_pane(pane)]

    def _render_pane_table(self, panes: list[Any]) -> Table:
        table = Table(title="Compositor Panes", expand=True)
        table.add_column("Pane", style="cyan", width=8)
        table.add_column("Session", style="green", width=16)
        table.add_column("Path", style="yellow")
        table.add_column("Type", style="magenta", width=12)

        for pane in panes:
            pane_type = "Claude" if is_claude_code_pane(pane) else "Shell"
            table.add_row(pane.pane_id, pane.session_name, pane.path, pane_type)
        if not panes:
            table.add_row("-", "-", "No panes detected", "-")
        return table

    def _preview_panel(self, panes: list[Any]) -> Panel:
        if not panes:
            return Panel("No active panes available.", title="Preview", border_style="red")

        preview_lines = int(self.config.get("preview_lines", 30))
        preview_text = capture_tmux_pane(panes[0].pane_id, last_lines=preview_lines)
        title = f"Preview {panes[0].pane_id}"
        return Panel(preview_text.rstrip() or "(empty)", title=title, border_style="green")

    def render(self, layout_name: str = "balanced") -> Layout:
        panes = self.collect_panes()

        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3),
        )

        if layout_name == "stacked":
            layout["body"].split_column(Layout(name="left"), Layout(name="right"))
        else:
            layout["body"].split_row(Layout(name="left"), Layout(name="right"))

        layout["header"].update(Panel("[bold cyan]thegent TUI Compositor (MVP)[/bold cyan]", border_style="blue"))
        layout["left"].update(Panel(self._render_pane_table(panes), border_style="cyan"))
        layout["right"].update(self._preview_panel(panes))
        layout["footer"].update(
            Panel(
                "[dim]Ctrl+C to exit | link target: tmux panes | source: research-tui-compositor[/dim]",
                border_style="blue",
            )
        )
        return layout


def run_compositor_tui(
    layout_name: str = "balanced",
    include_non_claude: bool = False,
    once: bool = False,
    refresh_interval: float = 1.0,
) -> None:
    compositor = TUICompositor(include_non_claude=include_non_claude)
    console = Console()

    if once:
        console.print(compositor.render(layout_name=layout_name))
        return

    with Live(
        compositor.render(layout_name=layout_name), refresh_per_second=max(1.0, 1.0 / refresh_interval), screen=True
    ) as live:
        try:
            while True:
                live.update(compositor.render(layout_name=layout_name))
                time.sleep(refresh_interval)
        except KeyboardInterrupt:
            return
