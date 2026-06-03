"""TUI composition helpers."""

from pathlib import Path
from typing import Any

from rich.panel import Panel
from yaml import safe_load

from thegent.tools.terminal import capture_tmux_pane, is_claude_code_pane, list_tmux_panes


class TUICompositor:
    """Collect tmux panes and render a simple dashboard layout."""

    def __init__(self, config_path: Path | None = None, include_non_claude: bool = False) -> None:
        self.include_non_claude = include_non_claude
        self.config: dict[str, Any] = {}
        if config_path is not None and config_path.exists():
            loaded = safe_load(config_path.read_text(encoding="utf-8"))
            self.config = loaded if isinstance(loaded, dict) else {}

    def collect_panes(self) -> list[Any]:
        panes = list_tmux_panes()
        if self.include_non_claude:
            return panes
        return [pane for pane in panes if is_claude_code_pane(pane)]

    def compose(self, components: list[Any]) -> str:
        """Compose TUI components."""
        return "\n".join(str(component) for component in components)

    def render(self, layout_name: str | None = None) -> dict[str, Panel]:
        panes = self.collect_panes()
        preview_lines = int(self.config.get("preview_lines", 30))
        previews = [
            f"{pane.pane_id} {getattr(pane, 'title', '')}\n{capture_tmux_pane(pane.pane_id, last_lines=preview_lines)}"
            for pane in panes
        ]
        body = "\n\n".join(previews) or "No panes"
        layout = layout_name or self.config.get("layout", "balanced")
        return {
            "header": Panel(f"TheGent TUI - {layout}"),
            "left": Panel(body),
            "right": Panel(f"{len(panes)} panes"),
            "footer": Panel("ready"),
        }


__all__ = ["TUICompositor"]
