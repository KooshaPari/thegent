"""Terminal management utilities for thegent."""

from __future__ import annotations

from typing import NamedTuple


class TmuxPane(NamedTuple):
    """Represents a tmux pane."""

    pane_id: str
    session_name: str
    window_index: str
    pane_index: str
    pane_current_path: str
    command: str
    pane_title: str
