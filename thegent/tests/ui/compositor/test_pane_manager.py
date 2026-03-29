"""Tests for the PaneManager."""

from thegent.compositor.pane_manager import PaneManager


class TestPaneManager:
    """Tests for PaneManager functionality."""

    def test_pane_manager_initialization(self) -> None:
        """Test that PaneManager initializes correctly."""
        pm = PaneManager()
        assert pm.root is not None
        assert pm.root.pane is not None
        assert pm.focus_pane_id == "root"
        assert pm.get_pane_count() == 1

    def test_get_focused_pane(self) -> None:
        """Test getting the focused pane."""
        pm = PaneManager()
        focused = pm.get_focused_pane()
        assert focused is not None
        assert focused.pane is not None

    def test_split_pane_horizontal(self) -> None:
        """Test horizontal split operation."""
        pm = PaneManager()
        new_pane = pm.split_pane("H")
        assert new_pane is not None
        assert pm.get_pane_count() == 2
        assert pm.focus_pane_id == new_pane.pane.pane_id

    def test_split_pane_vertical(self) -> None:
        """Test vertical split operation."""
        pm = PaneManager()
        new_pane = pm.split_pane("V")
        assert new_pane is not None
        assert pm.get_pane_count() == 2

    def test_close_pane_single(self) -> None:
        """Test that closing the only pane fails."""
        pm = PaneManager()
        result = pm.close_pane()
        assert result is False
        assert pm.get_pane_count() == 1

    def test_close_pane_after_split(self) -> None:
        """Test closing a pane after split."""
        pm = PaneManager()
        new_pane = pm.split_pane("H")
        new_pane_id = new_pane.pane.pane_id if new_pane and new_pane.pane else None

        result = pm.close_pane(new_pane_id)
        assert result is True
        assert pm.get_pane_count() == 1

    def test_focus_next_single_pane(self) -> None:
        """Test focus_next with single pane."""
        pm = PaneManager()
        initial_focus = pm.focus_pane_id
        pm.focus_next()
        assert pm.focus_pane_id == initial_focus

    def test_focus_next_multiple_panes(self) -> None:
        """Test focus_next with multiple panes."""
        pm = PaneManager()
        pane1_id = pm.focus_pane_id
        pm.split_pane("H")
        pane2_id = pm.focus_pane_id

        pm.focus_next()
        assert pm.focus_pane_id == pane1_id

        pm.focus_next()
        assert pm.focus_pane_id == pane2_id

    def test_get_all_panes(self) -> None:
        """Test getting all panes."""
        pm = PaneManager()
        assert len(pm.get_all_panes()) == 1

        pm.split_pane("H")
        assert len(pm.get_all_panes()) == 2

        pm.split_pane("V")
        assert len(pm.get_all_panes()) == 3

    def test_save_layout(self) -> None:
        """Test saving layout."""
        pm = PaneManager()
        pm.split_pane("H")
        layout = pm.save_layout()

        assert layout is not None
        assert layout.get("type") == "branch"
        assert layout.get("direction") == "H"
        assert len(layout.get("children", [])) == 2

    def test_restore_layout(self) -> None:
        """Test restoring layout."""
        pm = PaneManager()
        pm.split_pane("H")
        pm.split_pane("V")
        layout = pm.save_layout()

        # Create new manager and restore
        pm2 = PaneManager()
        result = pm2.restore_layout(layout)

        assert result is True
        assert pm2.get_pane_count() == 3

    def test_restore_layout_invalid(self) -> None:
        """Test restoring invalid layout."""
        pm = PaneManager()
        result = pm.restore_layout({"invalid": "data"})
        assert result is False

    def test_get_pane_by_id(self) -> None:
        """Test getting pane by ID."""
        pm = PaneManager()
        pane_node = pm.get_pane_by_id("root")
        assert pane_node is not None
        assert pane_node.pane is not None

        pane_node = pm.get_pane_by_id("nonexistent")
        assert pane_node is None
