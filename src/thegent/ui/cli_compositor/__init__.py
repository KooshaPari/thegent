"""CLI compositor widgets built on Rich."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from rich.console import Console
from rich.live import Live
from rich.progress import Progress, TaskID
from rich.table import Table

from thegent.ui.compositor.compositor import Compositor, Panel


@dataclass
class ProgressPanel:
    name: str
    task_id: TaskID
    progress: Progress

    def advance(self, amount: float, description: str | None = None) -> None:
        kwargs = {"advance": amount}
        if description is not None:
            kwargs["description"] = description
        self.progress.update(self.task_id, **kwargs)

    def complete(self) -> None:
        task = self.progress.tasks[self.task_id]
        total = task.total or task.completed
        self.progress.update(self.task_id, completed=total)
        self.progress.stop_task(self.task_id)

    def render(self) -> str:
        task = self.progress.tasks[self.task_id]
        return f"{self.name}: {task.description} {task.completed}/{task.total}"


@dataclass
class StatusPanel:
    name: str
    content_fn: Callable[[], str]

    def render(self) -> str:
        try:
            return self.content_fn()
        except Exception as exc:  # noqa: BLE001
            return f"[StatusPanel error: {self.name} {type(exc).__name__}]"


class CliCompositor:
    """Manage progress and status panels for CLI rendering."""

    def __init__(
        self,
        console: Console | None = None,
        refresh_per_second: float = 4.0,
        transient: bool = False,
    ) -> None:
        self.console = console or Console()
        self._refresh_per_second = refresh_per_second
        self._transient = transient
        self._progress = Progress(console=self.console)
        self._progress_panels: dict[str, ProgressPanel] = {}
        self._status_panels: dict[str, StatusPanel] = {}
        self._compositor = Compositor()
        self._live: Live | None = None

    def __enter__(self) -> "CliCompositor":
        self._progress.start()
        self._live = Live(
            self.render(), console=self.console, refresh_per_second=self._refresh_per_second, transient=self._transient
        )
        self._live.start()
        return self

    def __exit__(self, *_exc: object) -> None:
        if self._live is not None:
            self._live.stop()
            self._live = None
        self._progress.stop()

    def __contains__(self, name: str) -> bool:
        return name in self._progress_panels or name in self._status_panels

    def __len__(self) -> int:
        return len(self._progress_panels) + len(self._status_panels)

    @property
    def progress_panel_names(self) -> list[str]:
        return list(self._progress_panels)

    @property
    def status_panel_names(self) -> list[str]:
        return list(self._status_panels)

    def add_progress(self, name: str, total: float, description: str | None = None) -> ProgressPanel:
        task_id = self._progress.add_task(description or name, total=total)
        panel = ProgressPanel(name, task_id, self._progress)
        self._progress_panels[name] = panel
        self._compositor.add_panel(Panel(name=name, content_fn=panel.render))
        return panel

    def update_progress(self, name: str, advance: float = 1.0, description: str | None = None) -> None:
        if name not in self._progress_panels:
            raise KeyError(name)
        self._progress_panels[name].advance(advance, description)

    def complete_progress(self, name: str) -> None:
        if name not in self._progress_panels:
            raise KeyError(name)
        self._progress_panels[name].complete()

    def remove_progress(self, name: str) -> bool:
        if name not in self._progress_panels:
            return False
        del self._progress_panels[name]
        self._compositor.remove_panel(name)
        return True

    def add_status_line(self, name: str, content_fn: Callable[[], str]) -> StatusPanel:
        panel = StatusPanel(name, content_fn)
        self._status_panels[name] = panel
        self._compositor.add_panel(Panel(name=name, content_fn=panel.render))
        return panel

    def remove_status_line(self, name: str) -> bool:
        if name not in self._status_panels:
            return False
        del self._status_panels[name]
        self._compositor.remove_panel(name)
        return True

    def render(self) -> Table:
        table = Table("Name", "Value")
        for name, panel in self._progress_panels.items():
            table.add_row(name, panel.render())
        for name, panel in self._status_panels.items():
            table.add_row(name, panel.render())
        return table


def make_cli_compositor(refresh_per_second: float = 4.0, transient: bool = False) -> CliCompositor:
    return CliCompositor(refresh_per_second=refresh_per_second, transient=transient)


__all__ = ["CliCompositor", "ProgressPanel", "StatusPanel", "make_cli_compositor"]
