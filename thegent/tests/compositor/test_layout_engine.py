"""Tests for the layout engine.

Tests basic layout operations: vertical stacking, horizontal arrangement,
and layout calculations.
"""

import pytest

from thegent.compositor.layout_engine import (
    Direction,
    LayoutEngine,
    LayoutNode,
    Padding,
    Size,
    SizeUnit,
)


class TestSize:
    """Tests for the Size class."""

    def test_size_percent(self):
        """Test percentage size."""
        size = Size(70, "%")
        assert size.value == 70
        assert size.unit == SizeUnit.PERCENT
        assert str(size) == "70%"
        assert size.to_textual_css() == "70%"

    def test_size_fraction(self):
        """Test fraction size."""
        size = Size(1, "fr")
        assert size.value == 1
        assert size.unit == SizeUnit.FRACTION
        assert str(size) == "1fr"
        assert size.to_textual_css() == "1fr"

    def test_size_cells(self):
        """Test cell size."""
        size = Size(30, "cells")
        assert size.value == 30
        assert size.unit == SizeUnit.CELLS
        assert str(size) == "30cells"
        assert size.to_textual_css() == "30w"

    def test_size_auto(self):
        """Test auto size."""
        size = Size(1, "auto")
        assert size.value == 1
        assert size.unit == SizeUnit.AUTO
        assert str(size) == "auto"
        assert size.to_textual_css() == "auto"


class TestLayoutNode:
    """Tests for the LayoutNode class."""

    def test_create_vertical_node(self):
        """Test creating a vertical layout node."""
        node = LayoutNode(direction=Direction.VERTICAL)
        assert node.direction == Direction.VERTICAL
        assert len(node.children) == 0

    def test_create_horizontal_node(self):
        """Test creating a horizontal layout node."""
        node = LayoutNode(direction=Direction.HORIZONTAL)
        assert node.direction == Direction.HORIZONTAL
        assert len(node.children) == 0

    def test_add_child_with_id(self):
        """Test adding a child by widget ID."""
        parent = LayoutNode()
        child = parent.add_child("widget-1")
        assert child.widget_id == "widget-1"
        assert child.parent == parent
        assert len(parent.children) == 1

    def test_add_child_node(self):
        """Test adding a child node."""
        parent = LayoutNode()
        child_node = LayoutNode()
        returned = parent.add_child(child_node)
        assert returned == child_node
        assert child_node.parent == parent
        assert len(parent.children) == 1

    def test_get_css_for_child(self):
        """Test getting CSS for children."""
        parent = LayoutNode(direction=Direction.VERTICAL)
        parent.add_child("widget-1", constraints=None)
        parent.add_child("widget-2", constraints=None)

        css1 = parent.get_css_for_child(0)
        css2 = parent.get_css_for_child(1)
        assert css1 == "1fr"
        assert css2 == "1fr"

    def test_to_dict_serialization(self):
        """Test layout serialization to dictionary."""
        node = LayoutNode(direction=Direction.VERTICAL)
        node.add_child("widget-1")
        node.add_child("widget-2")

        result = node.to_dict()
        assert result["direction"] == "vertical"
        assert len(result["children"]) == 2
        assert result["children"][0]["widget_id"] == "widget-1"


class TestLayoutEngine:
    """Tests for the LayoutEngine class."""

    def test_create_vertical_stack(self):
        """Test creating a vertical stack."""
        engine = LayoutEngine()
        stack = engine.create_vertical_stack(["widget-1", "widget-2", "widget-3"])

        assert stack.direction == Direction.VERTICAL
        assert len(stack.children) == 3
        assert stack.children[0].widget_id == "widget-1"
        assert stack.children[1].widget_id == "widget-2"
        assert stack.children[2].widget_id == "widget-3"

    def test_create_horizontal_stack(self):
        """Test creating a horizontal stack."""
        engine = LayoutEngine()
        stack = engine.create_horizontal_stack(["widget-1", "widget-2"])

        assert stack.direction == Direction.HORIZONTAL
        assert len(stack.children) == 2
        assert stack.children[0].widget_id == "widget-1"

    def test_create_grid(self):
        """Test creating a grid layout."""
        engine = LayoutEngine()
        widgets = ["w1", "w2", "w3", "w4"]
        grid = engine.create_grid(2, 2, widgets)

        assert grid.direction == Direction.VERTICAL
        assert len(grid.children) == 2
        # First row
        assert grid.children[0].direction == Direction.HORIZONTAL
        assert len(grid.children[0].children) == 2

    def test_register_and_get_widget(self):
        """Test registering and retrieving widgets."""
        engine = LayoutEngine()

        class FakeWidget:
            pass

        widget = FakeWidget()
        engine.register_widget("my-widget", widget)

        retrieved = engine.get_widget("my-widget")
        assert retrieved == widget

    def test_calculate_layout_vertical(self):
        """Test layout calculation for vertical stacking."""
        engine = LayoutEngine()
        stack = engine.create_vertical_stack(["top", "bottom"])
        engine.root = stack

        layout = engine.calculate_layout(100, 50)

        assert "top" in layout
        assert "bottom" in layout
        # Both should span full width
        assert layout["top"][2] == 100
        assert layout["bottom"][2] == 100

    def test_generate_layout_css(self):
        """Test CSS generation."""
        engine = LayoutEngine()
        css = engine.generate_layout_css()

        assert "layout: vertical" in css


class TestPadding:
    """Tests for the Padding class."""

    def test_padding_uniform(self):
        """Test uniform padding."""
        padding = Padding(top=1, right=1, bottom=1, left=1)
        assert padding.to_textual_css() == "1"

    def test_padding_non_uniform(self):
        """Test non-uniform padding."""
        padding = Padding(top=1, right=2, bottom=3, left=4)
        assert padding.to_textual_css() == "1 2 3 4"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
