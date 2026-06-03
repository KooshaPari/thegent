"""Manage multiple compositor instances."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from thegent.ui.compositor.compositor import Compositor


class Layout(Enum):
    SINGLE = "single"
    SPLIT_H = "split_h"
    SPLIT_V = "split_v"
    GRID_2X2 = "grid_2x2"


@dataclass
class CompositorSlot:
    id: str
    compositor: Compositor
    weight: float = 1.0

    def __post_init__(self) -> None:
        if self.weight <= 0:
            raise ValueError("weight must be > 0")


class CompositorManager:
    """Store compositors and render simple text layouts."""

    def __init__(self, layout: Layout = Layout.SINGLE) -> None:
        self.layout = layout
        self._slots: dict[str, CompositorSlot] = {}
        self._focused_id: str | None = None

    def __len__(self) -> int:
        return len(self._slots)

    def __contains__(self, slot_id: str) -> bool:
        return slot_id in self._slots

    @property
    def slot_ids(self) -> list[str]:
        return list(self._slots)

    def add_compositor(self, compositor: Compositor, slot_id: str, weight: float = 1.0) -> None:
        self._slots[slot_id] = CompositorSlot(slot_id, compositor, weight)
        if self._focused_id is None:
            self._focused_id = slot_id

    def remove_compositor(self, slot_id: str) -> bool:
        if slot_id not in self._slots:
            return False
        del self._slots[slot_id]
        if self._focused_id == slot_id:
            self._focused_id = next(iter(self._slots), None)
        return True

    def get_compositor(self, slot_id: str) -> Compositor | None:
        slot = self._slots.get(slot_id)
        return slot.compositor if slot else None

    def focus(self, slot_id: str) -> None:
        if slot_id not in self._slots:
            raise KeyError(slot_id)
        self._focused_id = slot_id

    def get_focused(self) -> CompositorSlot | None:
        return self._slots.get(self._focused_id or "")

    def switch_layout(self, layout: Layout) -> None:
        self.layout = layout

    def render_all(self, width: int = 80) -> str:
        slots = list(self._slots.values())
        if not slots:
            return ""
        if self.layout == Layout.SINGLE:
            return self._box(slots[0], width)
        if self.layout == Layout.SPLIT_H:
            widths = self._distribute_widths(slots, sum(slot.weight for slot in slots), width)
            return self._join_horizontal(
                [self._box(slot, slot_width) for slot, slot_width in zip(slots, widths, strict=False)]
            )
        if self.layout == Layout.GRID_2X2:
            rows = [slots[index : index + 2] for index in range(0, len(slots), 2)]
            return "\n".join(
                self._join_horizontal([self._box(slot, width // max(len(row), 1)) for slot in row]) for row in rows
            )
        return "\n".join(self._box(slot, width) for slot in slots)

    @staticmethod
    def _distribute_widths(slots: list[CompositorSlot], total_weight: float, width: int) -> list[int]:
        if not slots:
            return []
        widths = [int(width * (slot.weight / total_weight)) for slot in slots]
        widths[-1] += width - sum(widths)
        return widths

    def _box(self, slot: CompositorSlot, width: int) -> str:
        width = max(width, 10)
        title = f"{slot.id}{' [*]' if slot.id == self._focused_id else ''}"
        content = "\n".join(slot.compositor.render())
        top = "┌" + title[: width - 2].ljust(width - 2, "─") + "┐"
        body = [f"│{line[: width - 2].ljust(width - 2)}│" for line in (content.splitlines() or [""])]
        bottom = "└" + "─" * (width - 2) + "┘"
        return "\n".join([top, *body, bottom])

    def _join_horizontal(self, boxes: list[str]) -> str:
        split = [box.splitlines() for box in boxes]
        max_lines = max(len(lines) for lines in split)
        return "\n".join(
            " ".join(lines[index] if index < len(lines) else " " * len(lines[0]) for lines in split)
            for index in range(max_lines)
        )


__all__ = ["CompositorManager", "CompositorSlot", "Layout"]
