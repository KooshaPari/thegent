"""UI terminal pane compatibility module."""

from __future__ import annotations

import logging

from thegent.compositor.terminal_pane import TerminalPane as _CoreTerminalPane

logger = logging.getLogger(__name__)


class TerminalPane(_CoreTerminalPane):
    """Terminal pane with a UI mount hook."""

    def on_mount(self) -> None:
        try:
            self.spawn_shell()
            logger.info("Mounted terminal pane %s", self.pane_id)
        except OSError as exc:
            logger.error("Failed to spawn terminal pane %s: %s", self.pane_id, exc)


__all__ = ["TerminalPane", "logger"]
