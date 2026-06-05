"""Composable terminal widgets used by the compositor UI tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque
from time import perf_counter
from typing import Callable, Any
from textual.text import Text


class DiffViewerPanel:
    """Tiny utility for rendering diff snippets with style."""

    def _style_diff_line(self, line: str) -> Text:
        if line.startswith("+"):
            return Text(line, style="green")
        if line.startswith("-"):
            return Text(line, style="red")
        if line.startswith("@@"):
            return Text(line, style="yellow bold")
        if line.startswith("+++ ") or line.startswith("--- "):
            return Text(line, style="dim cyan")
        return Text(line, style="white")


@dataclass
class FooterStatusBar:
    """Status bar at the bottom of the TUI."""

    pane_count: int = 1
    focus_id: str = "root"

    def update_pane_info(self, pane_count: int, focus_id: str) -> None:
        self.pane_count = pane_count
        self.focus_id = focus_id


@dataclass
class HeaderWidget:
    """Simple textual header."""

    title: str = ""
    version: str = ""

    def render(self) -> str:
        return f"{self.title} v{self.version}"


@dataclass
class MetricsPanel:
    """Container for arbitrary metrics."""

    metrics: dict[str, Any] = field(default_factory=dict)

    def update_metric(self, key: str, value: Any) -> None:
        self.metrics[key] = value

    def update_metrics(self, values: dict[str, Any]) -> None:
        self.metrics.update(values)


@dataclass
class OutputWidget:
    """Terminal output buffer."""

    title: str = ""
    line_count: int = 0
    _lines: deque[str] = field(default_factory=deque)

    def write(self, text: str) -> None:
        self._lines.append(text)
        while self.line_count > 0 and len(self._lines) > self.line_count:
            self._lines.popleft()

    def clear(self) -> None:
        self._lines.clear()


@dataclass
class ProgressIndicator:
    """Progress value render helper."""

    progress: int = 0
    total: int = 100
    message: str = ""

    def update_progress(self, progress: int, total: int, message: str) -> None:
        self.progress = progress
        self.total = max(1, total)
        self.message = message

    def render(self) -> str:
        pct = 0.0 if self.total == 0 else (self.progress / self.total) * 100
        return f"{self.progress}/{self.total} ({pct:.0f}%) {self.message}".strip()


@dataclass
class SidebarWidget:
    """Agent sidebar panel."""

    agents: dict[str, dict[str, str]] = field(default_factory=dict)

    def add_agent(self, agent_id: str, name: str, status: str) -> None:
        self.agents[agent_id] = {"name": name, "status": status}

    def update_agent_status(self, agent_id: str, status: str) -> None:
        if agent_id in self.agents:
            self.agents[agent_id]["status"] = status


@dataclass
class StatusWidget:
    """Status badge with model / token metadata."""

    status: str = "idle"
    model: str = "gpt-4"
    tokens_used: int = 0
    start_time: float | None = None

    def update_status(self, status: str) -> None:
        self.status = status

    def start_timer(self) -> None:
        self.start_time = perf_counter()

    def stop_timer(self) -> None:
        if self.start_time is None:
            return
        self.start_time = None

    def start(self) -> None:
        self.start_timer()

    def stop(self) -> None:
        self.stop_timer()


__all__ = [
    "DiffViewerPanel",
    "FooterStatusBar",
    "HeaderWidget",
    "MetricsPanel",
    "OutputWidget",
    "ProgressIndicator",
    "SidebarWidget",
    "StatusWidget",
]
