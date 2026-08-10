"""TUI compositor public surface.

Provides :class:`TUICompositor` for rendering a tmux pane list into a
structured 4-region TUI frame (header / footer / left / right) with
ARIA annotations on every section.

The previous stub returned an empty string from ``compose()``; this
module keeps a thin compatibility alias (``compose`` returns the
joined frame) so any legacy caller that still uses it does not blow
up, while new callers should use :meth:`TUICompositor.render`.

**Traces to**: L16 Frontend (audit scorecard), FR-UX-001..003,
L17 I18n/A11y (ARIA trailers).
"""

from __future__ import annotations

from typing import Any

from thegent.ux.compositor.tui_compositor import PaneSnapshot, TUICompositor

__all__ = ["TUICompositor", "PaneSnapshot", "compositor_compose"]


def compositor_compose(components: list[Any]) -> str:
    """Compatibility shim: join ``components`` after light sanitization.

    Legacy callers used ``TUICompositor().compose(components)`` and
    expected a single string back. New callers should construct
    :class:`TUICompositor` directly and use :meth:`TUICompositor.render`.
    """
    return "\n".join(str(c) for c in components if c is not None)
