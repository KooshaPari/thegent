"""Core layout engine for TUI Compositor.

Provides layout primitives for organizing widgets: vertical stacking, horizontal arrangement,
nested containers, and responsive sizing.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, StrEnum


class Direction(StrEnum):
    """Layout direction."""

    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"


class SizeUnit(StrEnum):
    """Size specification unit."""

    PERCENT = "%"
    FRACTION = "fr"
    CELLS = "cells"
    AUTO = "auto"


@dataclass
class Size:
    """Represents a dimension (width or height)."""

    value: float
    unit: SizeUnit

    def __init__(self, value: float, unit: SizeUnit | str = SizeUnit.FRACTION) -> None:
        """Initialize a size.

        Args:
            value: Numeric value
            unit: Unit type (%, fr, cells, auto)

        Examples:
            Size(70, "%")          # 70 percent of parent
            Size(1, "fr")          # 1 fraction (1fr)
            Size(30, "cells")      # 30 cells
            Size(1, "auto")        # Automatic sizing
        """
        if isinstance(unit, str):
            try:
                unit = SizeUnit(unit)
            except ValueError:
                unit = SizeUnit(unit.strip(" "))
        self.value = value
        self.unit = unit

    def __str__(self) -> str:
        """String representation."""
        if self.unit == SizeUnit.AUTO:
            return "auto"
        return f"{self.value}{self.unit.value}"

    def to_textual_css(self) -> str:
        """Convert to Textual CSS size specification.

        Returns:
            CSS size string (e.g., "1fr", "70%", "30w")
        """
        if self.unit == SizeUnit.PERCENT:
            return f"{self.value}%"
        if self.unit == SizeUnit.FRACTION:
            return f"{self.value}fr"
        if self.unit == SizeUnit.CELLS:
            return f"{int(self.value)}w"
        return "auto"


@dataclass
class Padding:
    """Padding specification."""

    top: int = 0
    right: int = 0
    bottom: int = 0
    left: int = 0

    def to_textual_css(self) -> str:
        """Convert to Textual CSS padding."""
        if self.top == self.right == self.bottom == self.left:
            return f"{self.top}"
        if self.top == self.bottom and self.right == self.left:
            return f"{self.top} {self.right}"
        return f"{self.top} {self.right} {self.bottom} {self.left}"


@dataclass
class Margin:
    """Margin specification."""

    top: int = 0
    right: int = 0
    bottom: int = 0
    left: int = 0

    def to_textual_css(self) -> str:
        """Convert to Textual CSS margin."""
        if self.top == self.right == self.bottom == self.left:
            return f"{self.top}"
        if self.top == self.bottom and self.right == self.left:
            return f"{self.top} {self.right}"
        return f"{self.top} {self.right} {self.bottom} {self.left}"


@dataclass
class LayoutConstraints:
    """Layout constraints for a widget or container."""

    min_width: int | None = None
    max_width: int | None = None
    min_height: int | None = None
    max_height: int | None = None
    width: Size | None = None
    height: Size | None = None
    padding: Padding = None
    margin: Margin = None
    flex_grow: float = 1.0

    def __post_init__(self) -> None:
        """Initialize default padding and margin."""
        if self.padding is None:
            self.padding = Padding()
        if self.margin is None:
            self.margin = Margin()


class LayoutNode:
    """Represents a layout node in the layout tree."""

    def __init__(
        self,
        direction: Direction = Direction.VERTICAL,
        constraints: LayoutConstraints | None = None,
    ) -> None:
        """Initialize a layout node.

        Args:
            direction: Layout direction (vertical or horizontal)
            constraints: Layout constraints
        """
        self.direction = direction
        self.constraints = constraints or LayoutConstraints()
        self.children: list[LayoutNode] = []
        self.widget_id: str | None = None
        self.parent: LayoutNode | None = None

    def add_child(self, child: LayoutNode | str, constraints: LayoutConstraints | None = None) -> LayoutNode:
        """Add a child to this node.

        Args:
            child: Child node or widget ID
            constraints: Optional layout constraints

        Returns:
            The child node
        """
        if isinstance(child, str):
            child_node = LayoutNode(constraints=constraints)
            child_node.widget_id = child
        else:
            child_node = child
            if constraints:
                child_node.constraints = constraints

        child_node.parent = self
        self.children.append(child_node)
        return child_node

    def get_css_for_child(self, index: int) -> str:
        """Get CSS for a child at the given index.

        Args:
            index: Child index

        Returns:
            CSS size specification
        """
        if not self.children or index >= len(self.children):
            return "1fr"

        child = self.children[index]
        if child.constraints.width and self.direction == Direction.HORIZONTAL:
            return child.constraints.width.to_textual_css()
        if child.constraints.height and self.direction == Direction.VERTICAL:
            return child.constraints.height.to_textual_css()

        return f"{child.constraints.flex_grow}fr"

    def generate_css(self, indent: int = 0) -> str:
        """Generate CSS for this layout node.

        Args:
            indent: CSS indentation level

        Returns:
            CSS rules
        """
        css_lines = []
        ind = "    " * indent

        if self.widget_id:
            css_lines.append(f"{ind}#{self.widget_id} {{")
            if self.constraints.width:
                css_lines.append(f"{ind}    width: {self.constraints.width.to_textual_css()};")
            if self.constraints.height:
                css_lines.append(f"{ind}    height: {self.constraints.height.to_textual_css()};")
            css_lines.append(f"{ind}}}")
        else:
            # Container CSS
            dir_css = "vertical" if self.direction == Direction.VERTICAL else "horizontal"
            css_lines.append(f"{ind}.layout-{id(self)} {{")
            css_lines.append(f"{ind}    layout: {dir_css};")
            if self.constraints.width:
                css_lines.append(f"{ind}    width: {self.constraints.width.to_textual_css()};")
            if self.constraints.height:
                css_lines.append(f"{ind}    height: {self.constraints.height.to_textual_css()};")
            css_lines.append(f"{ind}}}")

            # Child CSS
            for i, _child in enumerate(self.children):
                child_size = self.get_css_for_child(i)
                if self.direction == Direction.VERTICAL:
                    css_lines.append(f"{ind}.layout-child-{i} {{ height: {child_size}; }}")
                else:
                    css_lines.append(f"{ind}.layout-child-{i} {{ width: {child_size}; }}")

        return "\n".join(css_lines)

    def to_dict(self) -> dict:
        """Serialize layout to dictionary.

        Returns:
            Dictionary representation of layout tree
        """
        return {
            "direction": self.direction.value,
            "widget_id": self.widget_id,
            "children": [child.to_dict() for child in self.children],
            "constraints": {
                "min_width": self.constraints.min_width,
                "max_width": self.constraints.max_width,
                "min_height": self.constraints.min_height,
                "max_height": self.constraints.max_height,
                "width": str(self.constraints.width) if self.constraints.width else None,
                "height": str(self.constraints.height) if self.constraints.height else None,
            },
        }


class LayoutEngine:
    """Core layout engine for compositing multiple widgets."""

    def __init__(self) -> None:
        """Initialize the layout engine."""
        self.root = LayoutNode(direction=Direction.VERTICAL)
        self.widgets: dict[str, object] = {}

    def create_vertical_stack(
        self, widget_ids: list[str], constraints: list[LayoutConstraints] | None = None
    ) -> LayoutNode:
        """Create a vertical stack of widgets.

        Args:
            widget_ids: List of widget IDs
            constraints: Optional list of constraints per widget

        Returns:
            Root node of the stack
        """
        stack = LayoutNode(direction=Direction.VERTICAL)
        for i, widget_id in enumerate(widget_ids):
            constraint = constraints[i] if constraints and i < len(constraints) else None
            stack.add_child(widget_id, constraint)
        return stack

    def create_horizontal_stack(
        self, widget_ids: list[str], constraints: list[LayoutConstraints] | None = None
    ) -> LayoutNode:
        """Create a horizontal stack of widgets.

        Args:
            widget_ids: List of widget IDs
            constraints: Optional list of constraints per widget

        Returns:
            Root node of the stack
        """
        stack = LayoutNode(direction=Direction.HORIZONTAL)
        for i, widget_id in enumerate(widget_ids):
            constraint = constraints[i] if constraints and i < len(constraints) else None
            stack.add_child(widget_id, constraint)
        return stack

    def create_grid(self, rows: int, cols: int, widget_ids: list[str]) -> LayoutNode:
        """Create a grid layout.

        Args:
            rows: Number of rows
            cols: Number of columns
            widget_ids: List of widget IDs in row-major order

        Returns:
            Root node of the grid
        """
        grid = LayoutNode(direction=Direction.VERTICAL)
        for r in range(rows):
            row = LayoutNode(direction=Direction.HORIZONTAL)
            for c in range(cols):
                idx = r * cols + c
                if idx < len(widget_ids):
                    row.add_child(widget_ids[idx])
            grid.add_child(row)
        return grid

    def register_widget(self, widget_id: str, widget: object) -> None:
        """Register a widget instance.

        Args:
            widget_id: Unique widget ID
            widget: Widget instance
        """
        self.widgets[widget_id] = widget

    def get_widget(self, widget_id: str) -> object | None:
        """Get a registered widget.

        Args:
            widget_id: Widget ID

        Returns:
            Widget instance or None
        """
        return self.widgets.get(widget_id)

    def generate_layout_css(self) -> str:
        """Generate CSS for the current layout.

        Returns:
            Complete CSS rules
        """
        return self.root.generate_css()

    def calculate_layout(self, width: int, height: int) -> dict:
        """Calculate final layout dimensions.

        Args:
            width: Container width in cells
            height: Container height in cells

        Returns:
            Dictionary mapping widget IDs to (x, y, w, h) tuples
        """
        layout_map: dict[str, tuple] = {}
        self._calculate_recursive(self.root, 0, 0, width, height, layout_map)
        return layout_map

    def _calculate_recursive(
        self,
        node: LayoutNode,
        x: int,
        y: int,
        width: int,
        height: int,
        layout_map: dict[str, tuple],
    ) -> None:
        """Recursively calculate layout positions.

        Args:
            node: Current layout node
            x: X coordinate
            y: Y coordinate
            width: Available width
            height: Available height
            layout_map: Output map of positions
        """
        if node.widget_id:
            layout_map[node.widget_id] = (x, y, width, height)
            return

        # Calculate space for children
        if node.direction == Direction.VERTICAL:
            current_y = y
            for child in node.children:
                child_height = self._get_child_height(child, height)
                self._calculate_recursive(child, x, current_y, width, child_height, layout_map)
                current_y += child_height
        else:
            current_x = x
            for child in node.children:
                child_width = self._get_child_width(child, width)
                self._calculate_recursive(child, current_x, y, child_width, height, layout_map)
                current_x += child_width

    def _get_child_height(self, node: LayoutNode, available_height: int) -> int:
        """Calculate height for a child node."""
        if node.constraints.height:
            if node.constraints.height.unit == SizeUnit.PERCENT:
                return int(available_height * node.constraints.height.value / 100)
            if node.constraints.height.unit == SizeUnit.CELLS:
                return int(node.constraints.height.value)
        return available_height

    def _get_child_width(self, node: LayoutNode, available_width: int) -> int:
        """Calculate width for a child node."""
        if node.constraints.width:
            if node.constraints.width.unit == SizeUnit.PERCENT:
                return int(available_width * node.constraints.width.value / 100)
            if node.constraints.width.unit == SizeUnit.CELLS:
                return int(node.constraints.width.value)
        return available_width
