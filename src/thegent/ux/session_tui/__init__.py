"""Stub module."""

from typing import TYPE_CHECKING, Any


class SessionTUI:
    """Session TUI stub."""

    def __init__(self) -> None:
        self.running = False

    def run(self) -> None:
        self.running = True

    def stop(self) -> None:
        self.running = False


__all__ = ["SessionTUI"]
