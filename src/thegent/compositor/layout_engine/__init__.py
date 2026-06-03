"""Composable layout primitives used by the compositor and tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Direction(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class SizeUnit(Enum):
    PERCENT = "%"
    FRACTION = "fr"
    CELLS = "cells"
    AUTO = "auto"


@dataclass
class Size:
    """A scalar size with a unit."""

    value: int
    unit: str | SizeUnit

    def __post_init__(self) -> None:
        if not isinstance(self.unit, SizeUnit):
            self.unit = SizeUnit(self.unit)

    def __str__(self) -> str:
        if self.unit is SizeUnit.AUTO:
            return "auto"
        if self.unit is SizeUnit.CELLS:
            return f"{self.value}cells"
        if self.unit is SizeUnit.FRACTION:
            return f"{self.value}fr"
        return f"{self.value}%"

    def to_textual_css(self) -> str:
        if self.unit is SizeUnit.CELLS:
            return f"{self.value}w"
        if self.unit is SizeUnit.AUTO:
            return "auto"
        return str(self)


@dataclass
class Padding:
    """Edge spacing for layout containers."""

    top: int = 0
    right: int = 0
    bottom: int = 0
    left: int = 0

    def to_textual_css(self) -> str:
        if self.top == self.right == self.bottom == self.left:
            return str(self.top)
        return f"{self.top} {self.right} {self.bottom} {self.left}"


@dataclass
class LayoutNode:
    """A node in a layout tree."""

    direction: Direction | None = None
    widget_id: str | None = None
    parent: "LayoutNode | None" = None
    constraints: Size | None = None
    children: list["LayoutNode"] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.direction is not None and self.direction not in (Direction.HORIZONTAL, Direction.VERTICAL):
            raise ValueError("direction must be Direction.HORIZONTAL or Direction.VERTICAL")
        if self.widget_id is None and self.direction is None:
            self.direction = Direction.VERTICAL

    def add_child(
        self,
        child: str | "LayoutNode",
        constraints: Size | None = None,
    ) -> "LayoutNode":
        """Add and return a child node."""
        if isinstance(child, str):
            child_node = LayoutNode(widget_id=child, constraints=constraints, parent=self, direction=None)
            self.children.append(child_node)
            return child_node
        child.parent = self
        child.constraints = constraints
        self.children.append(child)
        return child

    def get_css_for_child(self, index: int) -> str:
        """Return textual size hint for a child."""
        child = self.children[index]
        if child.constraints is None:
            return "1fr"
        return child.constraints.to_textual_css()

    def to_dict(self) -> dict[str, Any]:
        """Serialize this node to a plain dictionary."""
        if self.direction is None:
            return {"widget_id": self.widget_id}
        return {
            "direction": self.direction.value,
            "children": [child.to_dict() for child in self.children],
        }


class LayoutEngine:
    """Small helper for creating and walking layout trees."""

    def __init__(self) -> None:
        self.root: LayoutNode | None = None
        self._widget_registry: dict[str, Any] = {}

    def create_vertical_stack(self, widgets: list[str]) -> LayoutNode:
        """Create a vertical root node with all widgets as leaves."""
        root = LayoutNode(direction=Direction.VERTICAL)
        for widget_id in widgets:
            root.add_child(widget_id)
        self.root = root
        return root

    def create_horizontal_stack(self, widgets: list[str]) -> LayoutNode:
        """Create a horizontal root node with all widgets as leaves."""
        root = LayoutNode(direction=Direction.HORIZONTAL)
        for widget_id in widgets:
            root.add_child(widget_id)
        self.root = root
        return root

    def create_grid(self, rows: int, cols: int, widgets: list[str]) -> LayoutNode:
        """Create a row/column grid of widgets."""
        if rows <= 0 or cols <= 0:
            raise ValueError("rows and cols must be positive")
        root = LayoutNode(direction=Direction.VERTICAL)
        index = 0
        for _ in range(rows):
            row = LayoutNode(direction=Direction.HORIZONTAL, parent=root)
            for _ in range(cols):
                if index >= len(widgets):
                    break
                row.add_child(widgets[index])
                index += 1
            root.children.append(row)
        self.root = root
        return root

    def register_widget(self, widget_id: str, widget: Any) -> None:
        """Register a widget instance for a symbolic identifier."""
        self._widget_registry[widget_id] = widget

    def get_widget(self, widget_id: str) -> Any:
        """Lookup a widget by identifier."""
        return self._widget_registry.get(widget_id)

    def calculate_layout(self, width: int, height: int) -> dict[str, tuple[int, int, int, int]]:
        """Return a simple rectangle map keyed by widget id.

        The layout map uses `(x, y, w, h)` tuples.
        """

        if self.root is None:
            return {}

        layout: dict[str, tuple[int, int, int, int]] = {}

        def walk(node: LayoutNode, x: int, y: int, w: int, h: int) -> None:
            if not node.children:
                if node.widget_id is not None:
                    layout[node.widget_id] = (x, y, w, h)
                return
            if node.direction is Direction.VERTICAL:
                y_cursor = y
                each = max(1, h // len(node.children))
                for index, child in enumerate(node.children):
                    child_h = each
                    if index == len(node.children) - 1:
                        child_h = h - (each * (len(node.children) - 1))
                    walk(child, x, y_cursor, w, child_h)
                    y_cursor += child_h
            else:
                x_cursor = x
                each = max(1, w // len(node.children))
                for index, child in enumerate(node.children):
                    child_w = each
                    if index == len(node.children) - 1:
                        child_w = w - (each * (len(node.children) - 1))
                    walk(child, x_cursor, y, child_w, h)
                    x_cursor += child_w

        walk(self.root, 0, 0, width, height)
        return layout

    def generate_layout_css(self) -> str:
        """Generate a compact CSS snippet for the current root."""
        direction = self.root.direction.value if self.root and self.root.direction else "vertical"
        css_chunks: list[str] = [
            f"layout: {direction}",
            f"children: {len(self.root.children) if self.root else 0}",
        ]
        return "; ".join(css_chunks)


__all__ = [
    "Direction",
    "LayoutEngine",
    "LayoutNode",
    "Padding",
    "Size",
    "SizeUnit",
]
