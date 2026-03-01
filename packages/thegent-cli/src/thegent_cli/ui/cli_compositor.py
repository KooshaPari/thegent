"""CLI Compositor: composites progress bars, status panels, and output.

Integrates with the Compositor panel system (thegent.ui.compositor.compositor)
to provide rich.progress-backed progress bars and dynamic status lines for
long-running CLI commands.

Main exports:
- ProgressPanel: A compositor panel backed by a rich Progress task.
- StatusPanel: A compositor panel backed by a dynamic callable.
- CliCompositor: Manages multiple progress bars and info panels in CLI output.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from rich.console import Console
from rich.live import Live
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.table import Table

from thegent_cli.ui.compositor.compositor import Compositor, Panel

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)

_DEFAULT_COLUMNS = (
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    TimeRemainingColumn(),
)


@dataclass
class ProgressPanel:
    """A compositor panel backed by a rich Progress bar task.

    Attributes:
        name: Unique identifier for the panel.
        task_id: The rich Progress task ID associated with this panel.
        progress: The rich Progress instance that owns the task.
    """

    name: str
    task_id: TaskID
    progress: Progress

    def advance(self, amount: int = 1, description: str | None = None) -> None:
        """Advance the underlying progress task.

        Args:
            amount: Number of steps to advance.
            description: Optional new description to display.
        """
        kwargs: dict[str, Any] = {"advance": amount}
        if description is not None:
            kwargs["description"] = description
        self.progress.update(self.task_id, **kwargs)

    def complete(self) -> None:
        """Mark the progress task as fully completed."""
        task = self.progress.tasks[self.task_id]
        remaining = task.total - task.completed if task.total is not None else 0
        if remaining > 0:
            self.progress.update(self.task_id, advance=remaining)
        self.progress.stop_task(self.task_id)

    def render(self) -> str:
        """Return a text representation of current progress state."""
        task = self.progress.tasks[self.task_id]
        total = task.total if task.total is not None else "?"
        return f"[{self.name}] {task.description}: {task.completed}/{total} ({task.percentage:.0f}%)"


@dataclass
class StatusPanel:
    """A compositor panel backed by a dynamic callable that returns a status string.

    Attributes:
        name: Unique identifier for the panel.
        content_fn: Callable invoked each render to produce the current status string.
    """

    name: str
    content_fn: Callable[[], str]

    def render(self) -> str:
        """Render the current status string from content_fn."""
        try:
            return self.content_fn()
        except Exception as exc:
            # Intentional error boundary: a broken status_fn must not crash the compositor
            logger.error(
                "StatusPanel %r content_fn raised %s: %s",
                self.name,
                type(exc).__name__,
                exc,
            )
            return f"[Status error: {self.name} — {type(exc).__name__}]"


class CliCompositor:
    """Manages multiple progress bars and info panels in CLI output.

    Uses rich.progress.Progress for progress tracking and rich.live.Live for
    live rendering of the combined panel output. Integrates with the
    Compositor panel system for lifecycle management.

    All progress panels share a single Progress instance so that they render
    in a unified live display. Status panels render beneath progress bars in
    a rich Table layout.

    Usage::

        with CliCompositor() as comp:
            panel = comp.add_progress("download", total=100, description="Downloading…")
            comp.add_status_line("status", lambda: "Running…")
            for i in range(100):
                comp.update_progress("download", advance=1)
            comp.complete_progress("download")

    Attributes:
        _progress_panels: Ordered mapping of name to ProgressPanel.
        _status_panels: Ordered mapping of name to StatusPanel.
        _compositor: Underlying Compositor for lifecycle management.
        _console: Rich Console used for live display.
        _progress: Shared rich Progress instance.
        _live: Rich Live context (active while compositor is used as context manager).
        _lock: Thread lock protecting shared state.
    """

    def __init__(
        self,
        console: Console | None = None,
        *,
        refresh_per_second: float = 4.0,
        transient: bool = False,
    ) -> None:
        """Initialise a CliCompositor.

        Args:
            console: Rich Console to use for output. Creates a new one if None.
            refresh_per_second: How many times per second to refresh the live display.
            transient: If True, the live display disappears on exit (useful for
                non-interactive pipelines).
        """
        self._console: Console = console or Console()
        self._refresh_per_second = refresh_per_second
        self._transient = transient
        self._progress_panels: dict[str, ProgressPanel] = {}
        self._status_panels: dict[str, StatusPanel] = {}
        self._compositor: Compositor = Compositor()
        self._progress: Progress = Progress(
            *_DEFAULT_COLUMNS,
            console=self._console,
            transient=transient,
        )
        self._live: Live | None = None
        self._lock: threading.Lock = threading.Lock()
        logger.debug("CliCompositor initialised (refresh=%.1f/s)", refresh_per_second)

    # ------------------------------------------------------------------
    # Progress panel API
    # ------------------------------------------------------------------

    def add_progress(
        self,
        name: str,
        total: int,
        description: str = "",
    ) -> ProgressPanel:
        """Add a named progress bar panel.

        If a panel with the same name already exists it is replaced.

        Args:
            name: Unique name for this progress panel.
            total: Total number of steps for the progress bar.
            description: Initial description shown beside the bar.

        Returns:
            The created ProgressPanel.
        """
        with self._lock:
            if name in self._progress_panels:
                logger.debug("CliCompositor: replacing existing progress panel '%s'", name)
                old = self._progress_panels[name]
                self._progress.stop_task(old.task_id)
                self._compositor.remove_panel(name)

            task_id = self._progress.add_task(description, total=total)
            pp = ProgressPanel(name=name, task_id=task_id, progress=self._progress)
            self._progress_panels[name] = pp

            # Wire into compositor for lifecycle management
            composite_panel = Panel(
                name=name,
                content_fn=pp.render,
                on_mount=lambda p: logger.debug("Progress panel '%s' mounted", p.name),
                on_unmount=lambda p: logger.debug("Progress panel '%s' unmounted", p.name),
            )
            self._compositor.add_panel(composite_panel)
            self._refresh_live()
            logger.debug("CliCompositor: added progress panel '%s' (total=%d)", name, total)
            return pp

    def update_progress(
        self,
        name: str,
        advance: int = 1,
        description: str | None = None,
    ) -> None:
        """Update a named progress panel.

        Args:
            name: The progress panel name.
            advance: Number of steps to advance.
            description: Optional new description.

        Raises:
            KeyError: If no progress panel with ``name`` exists.
        """
        with self._lock:
            pp = self._progress_panels.get(name)
            if pp is None:
                raise KeyError(f"No progress panel named {name!r}")
            pp.advance(advance, description)
            self._refresh_live()

    def complete_progress(self, name: str) -> None:
        """Mark a named progress panel as fully completed.

        Args:
            name: The progress panel name.

        Raises:
            KeyError: If no progress panel with ``name`` exists.
        """
        with self._lock:
            pp = self._progress_panels.get(name)
            if pp is None:
                raise KeyError(f"No progress panel named {name!r}")
            pp.complete()
            self._refresh_live()
            logger.debug("CliCompositor: completed progress panel '%s'", name)

    def remove_progress(self, name: str) -> bool:
        """Remove a named progress panel entirely.

        Args:
            name: The progress panel name.

        Returns:
            True if found and removed, False if not found.
        """
        with self._lock:
            pp = self._progress_panels.pop(name, None)
            if pp is None:
                return False
            self._progress.stop_task(pp.task_id)
            self._compositor.remove_panel(name)
            self._refresh_live()
            return True

    # ------------------------------------------------------------------
    # Status line API
    # ------------------------------------------------------------------

    def add_status_line(self, name: str, content_fn: Callable[[], str]) -> None:
        """Add a named dynamic status line.

        Status lines are rendered beneath all progress bars. If a status
        panel with the same name already exists it is replaced.

        Args:
            name: Unique name for this status panel.
            content_fn: Callable returning the status string. Called each render.
        """
        with self._lock:
            sp = StatusPanel(name=name, content_fn=content_fn)
            self._status_panels[name] = sp

            composite_panel = Panel(
                name=f"__status__{name}",
                content_fn=sp.render,
                on_mount=lambda p: logger.debug("Status panel '%s' mounted", p.name),
                on_unmount=lambda p: logger.debug("Status panel '%s' unmounted", p.name),
            )
            # add_panel handles replacement if name already exists
            self._compositor.add_panel(composite_panel)
            self._refresh_live()
            logger.debug("CliCompositor: added status panel '%s'", name)

    def remove_status_line(self, name: str) -> bool:
        """Remove a named status panel.

        Args:
            name: The status panel name.

        Returns:
            True if found and removed, False if not found.
        """
        with self._lock:
            sp = self._status_panels.pop(name, None)
            if sp is None:
                return False
            self._compositor.remove_panel(f"__status__{name}")
            self._refresh_live()
            return True

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self) -> Table:
        """Build and return a rich Table containing all panels.

        Progress bars are rendered first via the Progress instance, then
        status panels appear as rows in the table.

        Returns:
            A rich Table renderable containing the combined display.
        """
        table = Table.grid(expand=True)
        table.add_column()

        # Progress bars row
        table.add_row(self._progress)

        # Status panel rows
        with self._lock:
            for sp in self._status_panels.values():
                table.add_row(sp.render())

        return table

    def _refresh_live(self) -> None:
        """Trigger a live display refresh if active."""
        if self._live is not None:
            try:
                self._live.update(self.render())
            except Exception as exc:
                # Best-effort refresh; do not propagate live display errors
                logger.debug("CliCompositor live refresh error: %s", exc)

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> CliCompositor:
        """Start the compositor's live display.

        Returns:
            self (the CliCompositor instance).
        """
        self._progress.start()
        self._live = Live(
            self.render(),
            console=self._console,
            refresh_per_second=self._refresh_per_second,
            transient=self._transient,
        )
        self._live.start()
        logger.debug("CliCompositor entered (live display active)")
        return self

    def __exit__(self, *args: object) -> None:
        """Stop the live display and clean up all panels."""
        if self._live is not None:
            try:
                self._live.update(self.render())
                self._live.stop()
            except Exception as exc:
                # Best-effort cleanup; log and continue
                logger.debug("CliCompositor live stop error: %s", exc)
            finally:
                self._live = None

        try:
            self._progress.stop()
        except Exception as exc:
            # Best-effort cleanup; log and continue
            logger.debug("CliCompositor progress stop error: %s", exc)

        logger.debug("CliCompositor exited")

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    @property
    def progress_panel_names(self) -> list[str]:
        """Return ordered list of current progress panel names."""
        return list(self._progress_panels)

    @property
    def status_panel_names(self) -> list[str]:
        """Return ordered list of current status panel names."""
        return list(self._status_panels)

    def __len__(self) -> int:
        """Return total number of managed panels (progress + status)."""
        return len(self._progress_panels) + len(self._status_panels)

    def __contains__(self, name: object) -> bool:
        """Return True if a panel (progress or status) with ``name`` is registered."""
        return name in self._progress_panels or name in self._status_panels


def make_cli_compositor(
    *,
    console: Console | None = None,
    refresh_per_second: float = 4.0,
    transient: bool = True,
) -> CliCompositor:
    """Factory helper to build a CliCompositor with common defaults.

    Args:
        console: Optional Rich Console; creates a fresh one if None.
        refresh_per_second: Live refresh rate.
        transient: Whether the display disappears on exit (default: True for CI).

    Returns:
        A configured CliCompositor (not yet entered as context manager).
    """
    return CliCompositor(
        console=console,
        refresh_per_second=refresh_per_second,
        transient=transient,
    )
