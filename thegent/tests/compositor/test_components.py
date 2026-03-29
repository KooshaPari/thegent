"""Tests for the TUI components.

Tests OutputWidget, StatusWidget, SidebarWidget and other basic components.
"""

import pytest
from textual.app import App, ComposeResult

from thegent.compositor.components import (
    DiffViewerPanel,
    FooterStatusBar,
    HeaderWidget,
    MetricsPanel,
    OutputWidget,
    ProgressIndicator,
    SidebarWidget,
    StatusWidget,
)


class TestApp(App):
    """Test application for component testing."""

    def compose(self) -> ComposeResult:
        """Compose test app."""
        yield OutputWidget()
        yield StatusWidget()
        yield SidebarWidget()


class TestOutputWidget:
    """Tests for the OutputWidget."""

    def test_output_widget_creation(self):
        """Test creating an output widget."""
        widget = OutputWidget(title="Test Output")
        assert widget.title == "Test Output"
        assert widget.line_count == 0

    def test_write_to_output(self):
        """Test writing to output widget."""
        widget = OutputWidget()
        # Note: Writing requires the widget to be in a running app
        # This test just verifies the method exists and basic state
        assert hasattr(widget, "write")
        assert hasattr(widget, "clear")


class TestStatusWidget:
    """Tests for the StatusWidget."""

    def test_status_widget_creation(self):
        """Test creating a status widget."""
        widget = StatusWidget()
        assert widget.status == "idle"
        assert widget.model == "gpt-4"
        assert widget.tokens_used == 0

    def test_update_status(self):
        """Test updating status."""
        widget = StatusWidget()
        # Can't actually test reactive updates without running app
        # but we can verify the method exists
        assert hasattr(widget, "update_status")
        assert hasattr(widget, "start_timer")
        assert hasattr(widget, "stop_timer")


class TestSidebarWidget:
    """Tests for the SidebarWidget."""

    def test_sidebar_widget_creation(self):
        """Test creating a sidebar widget."""
        widget = SidebarWidget()
        assert len(widget.agents) == 0

    def test_add_agent(self):
        """Test adding an agent."""
        widget = SidebarWidget()
        widget.add_agent("agent-1", "Agent One", "running")
        assert "agent-1" in widget.agents
        assert widget.agents["agent-1"]["name"] == "Agent One"
        assert widget.agents["agent-1"]["status"] == "running"

    def test_update_agent_status(self):
        """Test updating agent status."""
        widget = SidebarWidget()
        widget.add_agent("agent-1", "Agent One", "idle")
        widget.update_agent_status("agent-1", "running")
        assert widget.agents["agent-1"]["status"] == "running"


class TestHeaderWidget:
    """Tests for the HeaderWidget."""

    def test_header_widget_creation(self):
        """Test creating a header widget."""
        widget = HeaderWidget(title="MyApp", version="1.0.0")
        assert widget.title == "MyApp"
        assert widget.version == "1.0.0"

    def test_header_render(self):
        """Test header rendering."""
        widget = HeaderWidget(title="Test", version="0.1.0")
        rendered = widget.render()
        assert "Test v0.1.0" in rendered


class TestFooterStatusBar:
    """Tests for the FooterStatusBar."""

    def test_footer_creation(self):
        """Test creating a footer status bar."""
        widget = FooterStatusBar()
        assert widget.pane_count == 1
        assert widget.focus_id == "root"

    def test_footer_update_pane_info(self):
        """Test updating pane info."""
        widget = FooterStatusBar()
        widget.update_pane_info(3, "pane-abc123")
        assert widget.pane_count == 3
        assert widget.focus_id == "pane-abc123"


class TestMetricsPanel:
    """Tests for the MetricsPanel."""

    def test_metrics_panel_creation(self):
        """Test creating metrics panel."""
        widget = MetricsPanel()
        assert len(widget.metrics) == 0

    def test_update_single_metric(self):
        """Test updating a single metric."""
        widget = MetricsPanel()
        widget.update_metric("cpu", "45%")
        assert widget.metrics["cpu"] == "45%"

    def test_update_multiple_metrics(self):
        """Test updating multiple metrics."""
        widget = MetricsPanel()
        metrics = {
            "cpu": "45%",
            "memory": "2.1GB",
            "requests": "1234",
        }
        widget.update_metrics(metrics)
        assert len(widget.metrics) == 3
        assert widget.metrics["cpu"] == "45%"


class TestProgressIndicator:
    """Tests for the ProgressIndicator."""

    def test_progress_creation(self):
        """Test creating progress indicator."""
        widget = ProgressIndicator()
        assert widget.progress == 0
        assert widget.total == 100

    def test_update_progress(self):
        """Test updating progress."""
        widget = ProgressIndicator()
        widget.update_progress(25, 100, "Loading...")
        assert widget.progress == 25
        assert widget.total == 100
        assert widget.message == "Loading..."

    def test_progress_render(self):
        """Test progress rendering."""
        widget = ProgressIndicator()
        widget.update_progress(50, 100, "Processing")
        rendered = widget.render()
        assert "50%" in rendered
        assert "Processing" in rendered


class TestDiffViewerPanel:
    """Tests for DiffViewerPanel line styling."""

    def test_style_diff_line_colors(self):
        """WL-100: additions/deletions/hunks are color-coded."""
        panel = DiffViewerPanel()
        add = panel._style_diff_line("+added")
        delete = panel._style_diff_line("-deleted")
        hunk = panel._style_diff_line("@@ -1 +1 @@")
        header = panel._style_diff_line("+++ b/file.py")
        context = panel._style_diff_line(" context")

        assert add.plain == "+added"
        assert delete.plain == "-deleted"
        assert hunk.plain == "@@ -1 +1 @@"
        assert header.plain == "+++ b/file.py"
        assert context.plain == " context"

        assert str(add.style) == "green"
        assert str(delete.style) == "red"
        assert str(hunk.style) == "yellow bold"
        assert str(header.style) == "dim cyan"
        assert str(context.style) == "white"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
