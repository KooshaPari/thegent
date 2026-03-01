"""CompositorManager: manage multiple Compositor instances with layout.

Provides:
- Layout: Enum of supported multi-compositor layouts (SINGLE, SPLIT_H,
  SPLIT_V, GRID_2X2).
- CompositorSlot: Dataclass binding a Compositor to a named slot with a
  relative size weight.
- CompositorManager: Manages a collection of CompositorSlots, computes per-
  slot column widths from weights and layout, renders each compositor into a
  box-drawn frame, and combines the frames into a single terminal string.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from thegent_cli.ui.compositor.compositor import Compositor

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Box-drawing constants (single-line)
# ---------------------------------------------------------------------------
_H = "\u2500"  # ─
_V = "\u2502"  # │
_TL = "\u250c"  # ┌
_TR = "\u2510"  # ┐
_BL = "\u2514"  # └
_BR = "\u2518"  # ┘


# ---------------------------------------------------------------------------
# Layout enum
# ---------------------------------------------------------------------------


class Layout(Enum):
    """Supported multi-compositor screen layouts.

    Attributes:
        SINGLE: One compositor fills the entire terminal width.
        SPLIT_H: Horizontal split — compositors are placed side-by-side
            (left | right).  Widths are proportional to slot weights.
        SPLIT_V: Vertical split — compositors are stacked top-to-bottom.
            Each compositor receives the full width; heights are equal.
        GRID_2X2: 2x2 grid — first four slots are arranged in two rows of
            two columns each.  Additional slots are appended below in a
            single-column fallback.
    """

    SINGLE = "single"
    SPLIT_H = "split_h"
    SPLIT_V = "split_v"
    GRID_2X2 = "grid_2x2"


# ---------------------------------------------------------------------------
# CompositorSlot
# ---------------------------------------------------------------------------


@dataclass
class CompositorSlot:
    """A named slot that holds one Compositor with a relative size weight.

    Attributes:
        id: Unique identifier for the slot within a CompositorManager.
        compositor: The Compositor instance managed by this slot.
        weight: Relative size weight (> 0).  Larger weights produce wider /
            taller sections in the final render.  Weights do not need to sum
            to 1; the manager normalises them.
    """

    id: str
    compositor: Compositor
    weight: float = field(default=1.0)

    def __post_init__(self) -> None:
        if self.weight <= 0:
            msg = f"CompositorSlot weight must be > 0, got {self.weight!r}"
            raise ValueError(msg)


# ---------------------------------------------------------------------------
# CompositorManager
# ---------------------------------------------------------------------------


class CompositorManager:
    """Manage multiple Compositor instances and provide layout management.

    The manager stores slots in insertion order.  A *focused* slot is brought
    visually to the foreground by rendering its border with a ``[*]`` marker.

    Args:
        layout: Initial layout.  Defaults to :attr:`Layout.SINGLE`.
    """

    def __init__(self, layout: Layout = Layout.SINGLE) -> None:
        """Initialise an empty manager with the given layout."""
        self._slots: dict[str, CompositorSlot] = {}
        self._layout: Layout = layout
        self._focused_id: str | None = None
        logger.debug("CompositorManager initialised with layout=%s", layout)

    # ------------------------------------------------------------------
    # Slot management
    # ------------------------------------------------------------------

    def add_compositor(
        self,
        compositor: Compositor,
        slot_id: str,
        weight: float = 1.0,
    ) -> None:
        """Add a compositor to the manager under *slot_id*.

        If a slot with the same ID already exists it is replaced.

        Args:
            compositor: The :class:`Compositor` to manage.
            slot_id: Unique identifier for the slot.
            weight: Relative size weight (must be > 0).
        """
        slot = CompositorSlot(id=slot_id, compositor=compositor, weight=weight)
        if slot_id in self._slots:
            logger.debug("Replacing existing slot '%s'", slot_id)
        self._slots[slot_id] = slot
        logger.debug("CompositorSlot '%s' added (weight=%s)", slot_id, weight)

        # If this is the first slot, focus it automatically.
        if self._focused_id is None:
            self._focused_id = slot_id

    def remove_compositor(self, slot_id: str) -> bool:
        """Remove a slot by ID.

        Args:
            slot_id: The slot to remove.

        Returns:
            ``True`` if the slot existed and was removed, ``False`` otherwise.
        """
        if slot_id not in self._slots:
            logger.warning("remove_compositor: no slot '%s'", slot_id)
            return False
        del self._slots[slot_id]
        logger.debug("CompositorSlot '%s' removed", slot_id)

        # Update focus if the removed slot was focused.
        if self._focused_id == slot_id:
            self._focused_id = next(iter(self._slots), None)
        return True

    def get_compositor(self, slot_id: str) -> Compositor | None:
        """Return the Compositor for *slot_id*, or None if not found.

        Args:
            slot_id: Slot identifier.

        Returns:
            The :class:`Compositor`, or *None*.
        """
        slot = self._slots.get(slot_id)
        return slot.compositor if slot is not None else None

    # ------------------------------------------------------------------
    # Focus management
    # ------------------------------------------------------------------

    def focus(self, slot_id: str) -> None:
        """Bring the compositor at *slot_id* to the foreground.

        Raises:
            KeyError: If no slot with the given ID exists.

        Args:
            slot_id: The slot to focus.
        """
        if slot_id not in self._slots:
            msg = f"No slot '{slot_id}' in CompositorManager"
            raise KeyError(msg)
        self._focused_id = slot_id
        logger.debug("Focus moved to slot '%s'", slot_id)

    def get_focused(self) -> CompositorSlot | None:
        """Return the currently focused :class:`CompositorSlot`, or None.

        Returns:
            The focused slot, or *None* if no slots are registered.
        """
        if self._focused_id is None:
            return None
        return self._slots.get(self._focused_id)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def switch_layout(self, layout: Layout) -> None:
        """Change the current layout.

        Args:
            layout: New :class:`Layout` value.
        """
        self._layout = layout
        logger.debug("Layout switched to %s", layout)

    @property
    def layout(self) -> Layout:
        """The current layout."""
        return self._layout

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render_all(self, width: int = 80) -> str:
        """Render all compositors and combine them with ANSI box drawing.

        Each compositor's panels are rendered and wrapped in a single-line box
        border.  The focused slot's border title shows a ``[*]`` indicator.

        Layout rules:
        - ``SINGLE``: The first slot fills the entire *width*.
        - ``SPLIT_H``: Slots are side-by-side; column widths are proportional
          to slot weights.
        - ``SPLIT_V``: Slots are stacked; each gets the full *width*.
        - ``GRID_2X2``: First four slots form a 2x2 grid; any extra slots
          fall through as a vertical stack below the grid.

        Args:
            width: Total terminal character width (default 80).

        Returns:
            A multi-line string suitable for writing to a terminal.
        """
        if not self._slots:
            return ""

        slots = list(self._slots.values())

        if self._layout == Layout.SINGLE:
            return self._render_single(slots, width)
        if self._layout == Layout.SPLIT_H:
            return self._render_split_h(slots, width)
        if self._layout == Layout.SPLIT_V:
            return self._render_split_v(slots, width)
        # GRID_2X2
        return self._render_grid_2x2(slots, width)

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------

    def _render_single(self, slots: list[CompositorSlot], width: int) -> str:
        """Render only the first slot at full width."""
        slot = slots[0]
        content = self._get_slot_content(slot)
        return self._box(slot, content, width)

    def _render_split_h(self, slots: list[CompositorSlot], width: int) -> str:
        """Render slots side-by-side, widths proportional to weights."""
        total_weight = sum(s.weight for s in slots)
        available = max(width, len(slots))
        col_widths = self._distribute_widths(slots, total_weight, available)

        boxed_columns = []
        for slot, col_w in zip(slots, col_widths, strict=False):
            content = self._get_slot_content(slot)
            boxed_columns.append(self._box_lines(slot, content, col_w))

        return self._merge_columns(boxed_columns)

    def _render_split_v(self, slots: list[CompositorSlot], width: int) -> str:
        """Render slots stacked vertically, each at full width."""
        parts = []
        for slot in slots:
            content = self._get_slot_content(slot)
            parts.append(self._box(slot, content, width))
        return "\n".join(parts)

    def _render_grid_2x2(self, slots: list[CompositorSlot], width: int) -> str:
        """Render up to four slots in a 2x2 grid; overflow appended below."""
        grid_slots = slots[:4]
        overflow = slots[4:]

        parts = []
        for row_start in range(0, len(grid_slots), 2):
            pair = grid_slots[row_start : row_start + 2]
            if len(pair) == 2:
                total_w = pair[0].weight + pair[1].weight
                available = max(width, 2)
                w0 = max(1, round(pair[0].weight / total_w * available))
                w1 = max(1, available - w0)
                left_lines = self._box_lines(pair[0], self._get_slot_content(pair[0]), w0)
                right_lines = self._box_lines(pair[1], self._get_slot_content(pair[1]), w1)
                parts.append(self._merge_columns([left_lines, right_lines]))
            else:
                slot = pair[0]
                parts.append(self._box(slot, self._get_slot_content(slot), width))

        for slot in overflow:
            parts.append(self._box(slot, self._get_slot_content(slot), width))

        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Box drawing helpers
    # ------------------------------------------------------------------

    def _box(self, slot: CompositorSlot, content: str, width: int) -> str:
        """Build a full box string for *slot* at *width* characters wide."""
        return "\n".join(self._box_lines(slot, content, width))

    def _box_lines(self, slot: CompositorSlot, content: str, width: int) -> list[str]:
        """Return a list of strings forming the box for *slot*.

        The box uses single-line box-drawing characters.  The top border
        contains the slot's ID as a title; if this slot is focused, ``[*]``
        is prepended to the title.

        Args:
            slot: The slot being rendered.
            content: The pre-rendered content string (may be multi-line).
            width: Total column width including the border characters.

        Returns:
            List of strings, one per line.
        """
        inner_w = max(width - 2, 0)

        focused = slot.id == self._focused_id
        raw_title = f"[*] {slot.id}" if focused else slot.id
        title = raw_title[:inner_w]
        top_fill = inner_w - len(title)
        top_border = f"{_TL}{title}{_H * top_fill}{_TR}"
        bot_border = f"{_BL}{_H * inner_w}{_BR}"

        lines: list[str] = [top_border]

        if inner_w == 0:
            lines.append(bot_border)
            return lines

        content_lines = content.splitlines() if content else [""]
        if not content_lines:
            content_lines = [""]
        for cl in content_lines:
            padded = cl[:inner_w].ljust(inner_w)
            lines.append(f"{_V}{padded}{_V}")

        lines.append(bot_border)
        return lines

    # ------------------------------------------------------------------
    # Column merging
    # ------------------------------------------------------------------

    @staticmethod
    def _merge_columns(columns: list[list[str]]) -> str:
        """Merge parallel column line-lists into a single string.

        All columns are padded to the same height by repeating their last
        line.  Adjacent columns are concatenated without extra separators
        (box borders of adjacent columns act as the visual separator).

        Args:
            columns: Each element is a list of strings (lines) for one column.

        Returns:
            Merged multi-line string.
        """
        if not columns:
            return ""

        max_height = max(len(c) for c in columns)
        padded: list[list[str]] = []
        for col in columns:
            extra_rows = max_height - len(col)
            if extra_rows > 0:
                last = col[-1] if col else ""
                col = col + [last] * extra_rows
            padded.append(col)

        row_strings = []
        for row_idx in range(max_height):
            row_strings.append("".join(col[row_idx] for col in padded))
        return "\n".join(row_strings)

    # ------------------------------------------------------------------
    # Width distribution
    # ------------------------------------------------------------------

    @staticmethod
    def _distribute_widths(
        slots: list[CompositorSlot],
        total_weight: float,
        available: int,
    ) -> list[int]:
        """Distribute *available* chars across slots by weight.

        Uses proportional rounding; any rounding remainder is assigned to the
        last slot so the total always equals *available*.

        Args:
            slots: Ordered slots whose weights determine allocation.
            total_weight: Sum of all slot weights.
            available: Total character width to distribute.

        Returns:
            List of integer widths, one per slot, summing to *available*.
        """
        if not slots:
            return []
        widths: list[int] = []
        allocated = 0
        for i, slot in enumerate(slots):
            if i == len(slots) - 1:
                widths.append(max(1, available - allocated))
            else:
                w = max(1, round(slot.weight / total_weight * available))
                widths.append(w)
                allocated += w
        return widths

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_slot_content(self, slot: CompositorSlot) -> str:
        """Render all panels from *slot.compositor* into a single string.

        Args:
            slot: The slot whose compositor is rendered.

        Returns:
            A newline-joined string of all panel outputs.
        """
        try:
            panel_outputs = slot.compositor.render()
            return "\n".join(panel_outputs)
        except Exception:
            logger.exception("CompositorManager: error rendering slot '%s'", slot.id)
            return f"[render error: {slot.id}]"

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Return the number of registered slots."""
        return len(self._slots)

    def __contains__(self, slot_id: object) -> bool:
        """Return True if *slot_id* is registered."""
        return slot_id in self._slots

    @property
    def slot_ids(self) -> list[str]:
        """Ordered list of registered slot IDs."""
        return list(self._slots)
