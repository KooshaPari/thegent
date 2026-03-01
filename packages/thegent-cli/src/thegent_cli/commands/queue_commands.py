"""Queue command group extracted from cli.py (WL-124)."""

from __future__ import annotations


def queue_list_cmd(*, watch: bool = False) -> None:
    """WP-7002: List pending prompts in the queue."""
    from thegent_core.config import ThegentSettings
    from thegent_cli.ux.queue_tui import QueueTUI

    settings = ThegentSettings()
    tui = QueueTUI(settings.session_dir)
    if watch:
        tui.watch()
    else:
        tui.show()


__all__ = ["queue_list_cmd"]
