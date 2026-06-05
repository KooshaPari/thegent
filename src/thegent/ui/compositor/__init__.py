"""UI compositor facade used by tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

from thegent.compositor.session_state import SessionState as _CoreSessionState

from .compositor import CacheStats, Compositor, CompositorProfiler, Panel, RenderProfile
from .pane_manager import Pane, PaneManager, PaneNode
from .terminal_pane import TerminalPane


def _default_terminal_workdir() -> str:
    return str(Path.cwd())


class SessionState(_CoreSessionState):
    def __init__(self, session_id: str = "test-session", session_dir: Path | None = None) -> None:
        super().__init__(session_id)
        self.session_id = session_id
        if session_dir is not None:
            self.session_dir = Path(session_dir)
            self.session_dir.mkdir(parents=True, exist_ok=True)
            self.session_file = self.session_dir / f"{session_id}.yaml"

    def save(self, state: dict[str, Any]) -> bool:
        return self.save_session({"session_id": self.session_id, **state})

    def load(self) -> dict[str, Any] | None:
        return self.load_session()

    def save_session(self, layout: dict[str, Any]) -> bool:
        return super().save_session(layout)

    def load_session(self) -> dict[str, Any] | None:
        return super().load_session()

    def list_sessions(self) -> list[str]:
        return super().list_sessions()


class CompositApp:
    TITLE = "Thegent Compositor"
    CSS = "Screen { } #main-pane-container { } Header { }"
    BINDINGS: ClassVar[list[tuple[str, str]]] = [
        ("ctrl+n", "new_pane"),
        ("ctrl+v", "split_vertical"),
        ("ctrl+h", "split_horizontal"),
        ("ctrl+x", "close_pane"),
        ("ctrl+l", "focus_next"),
        ("ctrl+r", "retry_pane"),
        ("ctrl+q", "quit"),
    ]

    def __init__(self, session_state: SessionState | None = None) -> None:
        self.session_state = session_state
        self.pane_manager = PaneManager()
        self._mounted = False
        self._pane_count = 0
        self._error_panes: set[str] = set()
        self._pane_widgets: dict[str, TerminalPane] = {}
        self.title = ""
        self.sub_title = ""

    def on_mount(self) -> None:
        try:
            self.title = self.TITLE
            self.sub_title = "Terminal UI for Agent Orchestration"
            root = self.pane_manager.create_root_pane("pane-0")
            self._pane_widgets[root.pane_id] = TerminalPane(root.pane_id, _default_terminal_workdir())
            self._pane_count = 1
            self._mounted = True
        except Exception:
            self._mounted = False

    def on_unmount(self) -> None:
        for pane in list(self._pane_widgets.values()):
            try:
                pane.close()
            except Exception:
                pass
        if self.session_state is not None:
            self.session_state.save({"layout": self.pane_manager.save_layout(), "pane_count": self._pane_count})
        self._pane_widgets.clear()

    def _update_statusbar(self) -> None:
        self.sub_title = f"{self._pane_count} panes"

    def action_new_pane(self) -> None:
        self.action_split_vertical()

    def action_split_vertical(self) -> None:
        self._split("V")

    def action_split_horizontal(self) -> None:
        self._split("H")

    def _split(self, direction: str) -> None:
        try:
            node = self.pane_manager.split_pane(direction)
            self._pane_widgets[node.pane.pane_id if node.pane else node.pane_id] = TerminalPane(
                node.pane.pane_id if node.pane else node.pane_id,
                _default_terminal_workdir(),
            )
            self._pane_count = self.pane_manager.get_pane_count()
        except Exception:
            self._error_panes.add(self.pane_manager.current_pane_id)

    def action_close_pane(self) -> None:
        pane_id = self.pane_manager.current_pane_id
        pane = self._pane_widgets.get(pane_id)
        if pane is not None:
            try:
                pane.close()
            except Exception:
                pass
        try:
            if self.pane_manager.close_pane(pane_id):
                self._pane_widgets.pop(pane_id, None)
                self._pane_count = self.pane_manager.get_pane_count()
        except Exception:
            self._error_panes.add(pane_id)

    def action_focus_next(self) -> None:
        self.pane_manager.focus_next()

    def action_retry_pane(self) -> None:
        self._error_panes.discard(self.pane_manager.current_pane_id)

    def action_quit(self) -> None:
        return None


__all__ = [
    "CacheStats",
    "CompositApp",
    "Compositor",
    "CompositorProfiler",
    "Pane",
    "PaneManager",
    "PaneNode",
    "Panel",
    "RenderProfile",
    "SessionState",
    "TerminalPane",
]
