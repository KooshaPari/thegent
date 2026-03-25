"""Basic component library for the TUI Compositor.

Phase 1 components: OutputWidget, StatusWidget, SidebarWidget, Header.
Provides reusable Textual widgets for displaying agent output, status, and navigation.
"""

from datetime import datetime

from rich.text import Text
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widgets import Button, Label, RichLog, Static


class OutputWidget(ScrollableContainer):
    """Display agent output with auto-scrolling and syntax highlighting.

    Features:
    - Rich text rendering with syntax highlighting
    - Auto-scroll on new messages
    - Search and filter capabilities (Phase 2+)
    - Timestamp display
    """

    DEFAULT_CSS = """
    OutputWidget {
        width: 70%;
        border: solid $primary;
        background: $panel;
        layout: vertical;
    }
    """

    def __init__(self, title: str = "Output", **kwargs) -> None:
        """Initialize the output widget.

        Args:
            title: Widget title
        """
        super().__init__(**kwargs)
        self.title = title
        self.line_count = 0

    def compose(self):
        """Compose the output widget."""
        yield Static(f"📋 {self.title}", id="output-header", classes="widget-header")
        yield RichLog(id="output-log", wrap=True, highlight=True)

    def write(self, text: str, style: str = "white", timestamp: bool = True) -> None:
        """Write text to the output widget.

        Args:
            text: Text to display
            style: Rich style to apply
            timestamp: Whether to prepend timestamp
        """
        log_widget = self.query_one("#output-log", RichLog)
        if timestamp:
            ts = datetime.now().strftime("%H:%M:%S")
            text = f"[dim]{ts}[/dim] {text}"
        log_widget.write(Text(text, style=style))
        self.line_count += 1

    def clear(self) -> None:
        """Clear all output."""
        log_widget = self.query_one("#output-log", RichLog)
        log_widget.clear()
        self.line_count = 0

    def get_line_count(self) -> int:
        """Get the number of lines displayed."""
        return self.line_count


class StatusWidget(Container):
    """Display agent status, model info, and metrics.

    Features:
    - Real-time status updates
    - Model information display
    - Token counter
    - Cost tracking (Phase 2+)
    """

    DEFAULT_CSS = """
    StatusWidget {
        width: 30%;
        height: 1fr;
        border: solid $primary;
        background: $panel;
        layout: vertical;
    }

    .status-row {
        height: 1;
        width: 1fr;
    }

    .status-label {
        width: 40%;
        text-align: left;
        color: $text-muted;
    }

    .status-value {
        width: 60%;
        text-align: left;
        color: $text;
    }
    """

    status = reactive("idle", recompose=True)
    model = reactive("gpt-4", recompose=True)
    tokens_used = reactive(0, recompose=True)
    elapsed_time = reactive(0.0, recompose=True)

    def __init__(self, **kwargs) -> None:
        """Initialize the status widget."""
        super().__init__(**kwargs)
        self.start_time: datetime | None = None

    def compose(self):
        """Compose the status widget."""
        yield Static("🔷 Status", id="status-header", classes="widget-header")

        with Vertical(id="status-info"):
            yield Label("", id="status-line")
            yield Label("", id="model-line")
            yield Label("", id="tokens-line")
            yield Label("", id="time-line")

    def watch_status(self, status: str) -> None:
        """Update status display."""
        label = self._get_status_label("#status-line")
        if label is None:
            return
        color = "green" if status == "running" else "yellow" if status == "idle" else "red"
        label.update(f"Status: [{color}]{status}[/{color}]")

    def watch_model(self, model: str) -> None:
        """Update model display."""
        label = self._get_status_label("#model-line")
        if label is None:
            return
        label.update(f"Model: {model}")

    def watch_tokens_used(self, tokens: int) -> None:
        """Update token count display."""
        label = self._get_status_label("#tokens-line")
        if label is None:
            return
        label.update(f"Tokens: {tokens:,}")

    def watch_elapsed_time(self, elapsed: float) -> None:
        """Update elapsed time display."""
        label = self._get_status_label("#time-line")
        if label is None:
            return
        minutes, seconds = divmod(int(elapsed), 60)
        label.update(f"Time: {minutes:02d}:{seconds:02d}")

    def _get_status_label(self, selector: str) -> Label | None:
        """Return a status label when composed, otherwise skip pre-mount updates."""
        try:
            return self.query_one(selector, Label)
        except NoMatches:
            return None

    def update_status(self, status: str, model: str | None = None, tokens: int | None = None) -> None:
        """Update all status fields.

        Args:
            status: New status (idle, running, error, done)
            model: Optional model name
            tokens: Optional token count
        """
        self.status = status
        if model:
            self.model = model
        if tokens is not None:
            self.tokens_used = tokens

    def start_timer(self) -> None:
        """Start the elapsed time timer."""
        self.start_time = datetime.now()

    def stop_timer(self) -> None:
        """Stop the elapsed time timer."""
        self.start_time = None


class SidebarWidget(ScrollableContainer):
    """Display agent list, session info, and quick actions.

    Features:
    - Agent list with status indicators
    - Session information
    - Quick action buttons
    - Navigation (Phase 2+)
    """

    DEFAULT_CSS = """
    SidebarWidget {
        width: 30%;
        height: 1fr;
        border: solid $primary;
        background: $panel;
        layout: vertical;
    }

    .sidebar-section {
        height: auto;
        width: 1fr;
        border-bottom: solid $primary;
        padding: 1 0;
    }

    .sidebar-title {
        width: 1fr;
        height: 1;
        color: $accent;
        text-style: bold;
        text-align: left;
    }

    .agent-item {
        width: 1fr;
        height: 1;
        padding: 0 1;
    }
    """

    def __init__(self, **kwargs) -> None:
        """Initialize the sidebar widget."""
        super().__init__(**kwargs)
        self.agents: dict[str, dict] = {}

    def compose(self):
        """Compose the sidebar widget."""
        yield Static("🔷 Sidebar", id="sidebar-header", classes="widget-header")

        with Vertical(id="sidebar-content"):
            # Agents section
            yield Static("Agents", classes="sidebar-title")
            yield Static("", id="agents-list")

            # Session info section
            yield Static("Session", classes="sidebar-title")
            yield Static("", id="session-info")

            # Actions section
            yield Static("Actions", classes="sidebar-title")
            with Horizontal(id="action-buttons"):
                yield Button("⏸ Pause", id="btn-pause", variant="warning")
                yield Button("▶ Resume", id="btn-resume", variant="success")
                yield Button("⏹ Stop", id="btn-stop", variant="error")

    def add_agent(self, agent_id: str, name: str, status: str = "idle") -> None:
        """Add an agent to the sidebar.

        Args:
            agent_id: Unique agent ID
            name: Display name
            status: Current status
        """
        self.agents[agent_id] = {"name": name, "status": status, "id": agent_id}
        self._update_agents_list()

    def update_agent_status(self, agent_id: str, status: str) -> None:
        """Update an agent's status.

        Args:
            agent_id: Agent ID
            status: New status
        """
        if agent_id in self.agents:
            self.agents[agent_id]["status"] = status
            self._update_agents_list()

    def _update_agents_list(self) -> None:
        """Update the displayed agents list."""
        agents_label = self._get_sidebar_static("#agents-list")
        if agents_label is None:
            return

        lines = []
        for info in self.agents.values():
            status = info["status"]
            icon = "🟢" if status == "running" else "🟡" if status == "idle" else "🔴"
            lines.append(f"{icon} {info['name']}")

        content = "\n".join(lines) if lines else "(no agents)"
        agents_label.update(content)

    def update_session_info(self, session_id: str, start_time: str, uptime: str) -> None:
        """Update session information.

        Args:
            session_id: Session ID
            start_time: Start time string
            uptime: Uptime string
        """
        session_label = self._get_sidebar_static("#session-info")
        if session_label is None:
            return
        info = f"ID: {session_id[:8]}...\nStart: {start_time}\nUptime: {uptime}"
        session_label.update(info)

    def _get_sidebar_static(self, selector: str) -> Static | None:
        """Return a sidebar node when composed, otherwise skip pre-mount updates."""
        try:
            return self.query_one(selector, Static)
        except NoMatches:
            return None


class HeaderWidget(Static):
    """Main header with title and version.

    Features:
    - Application title
    - Version display
    - Status indicator
    """

    DEFAULT_CSS = """
    HeaderWidget {
        dock: top;
        height: 3;
        background: $accent;
        color: $text;
        border-bottom: solid $primary;
        content-align: center middle;
        text-style: bold;
    }
    """

    def __init__(self, title: str = "Thegent", version: str = "0.1.0", **kwargs) -> None:
        """Initialize the header widget.

        Args:
            title: Application title
            version: Version string
        """
        super().__init__(**kwargs)
        self.title = title
        self.version = version

    def render(self) -> str:
        """Render the header."""
        return f"{self.title} v{self.version}\nMulti-pane Terminal Interface"


class FooterStatusBar(Static):
    """Footer status bar with quick info and bindings.

    Features:
    - Current focus info
    - Keyboard shortcuts
    - Connection status
    """

    DEFAULT_CSS = """
    FooterStatusBar {
        dock: bottom;
        height: 1;
        background: $boost;
        color: $text;
        border-top: solid $primary;
        text-style: dim;
    }
    """

    pane_count = reactive(1, recompose=True)
    focus_id = reactive("root", recompose=True)

    def render(self) -> str:
        """Render the footer."""
        return f"Panes: {self.pane_count} | Focus: {self.focus_id[:8]} | Ctrl+H: Split H | Ctrl+V: Split V | Ctrl+X: Close | Ctrl+Q: Quit"

    def update_pane_info(self, count: int, focus_id: str) -> None:
        """Update pane information.

        Args:
            count: Number of panes
            focus_id: Focused pane ID
        """
        self.pane_count = count
        self.focus_id = focus_id


class MetricsPanel(Container):
    """Display performance metrics and statistics.

    Features:
    - CPU/Memory usage (Phase 2+)
    - Request/response times
    - Success/error rates
    - Cost tracking
    """

    DEFAULT_CSS = """
    MetricsPanel {
        width: 1fr;
        height: auto;
        border: solid $primary;
        background: $panel;
        padding: 1;
    }

    .metric-row {
        width: 1fr;
        height: 1;
    }
    """

    def __init__(self, **kwargs) -> None:
        """Initialize the metrics panel."""
        super().__init__(**kwargs)
        self.metrics: dict[str, str] = {}

    def compose(self):
        """Compose the metrics panel."""
        yield Static("📊 Metrics", classes="widget-header")
        yield Static("", id="metrics-content")

    def update_metric(self, key: str, value: str) -> None:
        """Update a metric value.

        Args:
            key: Metric key
            value: Metric value
        """
        self.metrics[key] = value
        self._render_metrics()

    def update_metrics(self, metrics: dict[str, str]) -> None:
        """Update multiple metrics.

        Args:
            metrics: Dictionary of metric key-value pairs
        """
        self.metrics.update(metrics)
        self._render_metrics()

    def _render_metrics(self) -> None:
        """Render the metrics display."""
        metrics_widget = self._get_metrics_widget()
        if metrics_widget is None:
            return
        lines = [f"{k}: {v}" for k, v in self.metrics.items()]
        content = "\n".join(lines) if lines else "(no metrics)"
        metrics_widget.update(content)

    def _get_metrics_widget(self) -> Static | None:
        """Return the metrics body when composed, otherwise skip pre-mount updates."""
        try:
            return self.query_one("#metrics-content", Static)
        except NoMatches:
            return None


class ProgressIndicator(Static):
    """Display progress and status indicator.

    Features:
    - Progress bar
    - Percentage display
    - ETA
    - Status message
    """

    DEFAULT_CSS = """
    ProgressIndicator {
        width: 1fr;
        height: 3;
        border: solid $primary;
        background: $panel;
        padding: 1;
    }
    """

    progress = reactive(0, recompose=True)
    total = reactive(100, recompose=True)
    message = reactive("Processing...", recompose=True)

    def render(self) -> str:
        """Render the progress indicator."""
        percentage = (self.progress / self.total * 100) if self.total > 0 else 0
        bar_length = 30
        filled = int(bar_length * self.progress / self.total) if self.total > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)
        return f"{self.message}\n[{bar}] {percentage:.0f}% ({self.progress}/{self.total})"

    def update_progress(self, current: int, total: int, message: str | None = None) -> None:
        """Update progress.

        Args:
            current: Current progress
            total: Total items
            message: Optional status message
        """
        self.progress = current
        self.total = total
        if message:
            self.message = message


class DiffViewerPanel(ScrollableContainer):
    """Display unified diff with ANSI color highlighting.

    Features:
    - Renders unified diff with color coding (green for additions, red for deletions)
    - Line number display
    - Scrollable view for large diffs
    - Syntax highlighting for diff meta (headers, hunks)
    """

    DEFAULT_CSS = """
    DiffViewerPanel {
        width: 1fr;
        height: 1fr;
        border: solid $primary;
        background: $panel;
        layout: vertical;
    }

    .diff-header {
        width: 1fr;
        height: auto;
        color: $accent;
        text-style: bold;
    }

    .diff-hunk {
        width: 1fr;
        height: auto;
        color: $text-muted;
    }

    .diff-add {
        width: 1fr;
        height: auto;
        color: $success;
    }

    .diff-del {
        width: 1fr;
        height: auto;
        color: $error;
    }

    .diff-context {
        width: 1fr;
        height: auto;
        color: $text;
    }

    .diff-meta {
        width: 1fr;
        height: auto;
        color: $text-muted;
        text-style: dim;
    }
    """

    def __init__(self, title: str = "Diff Viewer", **kwargs) -> None:
        """Initialize the diff viewer panel.

        Args:
            title: Panel title
        """
        super().__init__(**kwargs)
        self.title = title

    def compose(self):
        """Compose the diff viewer panel."""
        yield Static(f"📄 {self.title}", id="diff-header", classes="widget-header")
        yield RichLog(id="diff-content", wrap=False, highlight=False)

    def set_diff(self, unified_diff: str) -> None:
        """Set and render a unified diff string.

        Args:
            unified_diff: Unified diff string to display
        """
        log_widget = self.query_one("#diff-content", RichLog)
        log_widget.clear()

        for line in unified_diff.splitlines():
            styled_line = self._style_diff_line(line)
            log_widget.write(styled_line)

    def _style_diff_line(self, line: str) -> Text:
        """Style a single diff line with appropriate colors.

        Args:
            line: A single line from the diff

        Returns:
            Rich Text with styling applied
        """
        if line.startswith("---") or line.startswith("+++"):
            # File header lines
            return Text(line, style="dim cyan")
        if line.startswith("@@"):
            # Hunk headers
            return Text(line, style="yellow bold")
        if line.startswith("+"):
            # Additions - green
            return Text(line, style="green")
        if line.startswith("-"):
            # Deletions - red
            return Text(line, style="red")
        if line.startswith("\\"):
            # No newline at end warning
            return Text(line, style="dim italic")
        # Context lines
        return Text(line, style="white")

    def clear(self) -> None:
        """Clear the diff viewer."""
        log_widget = self.query_one("#diff-content", RichLog)
        log_widget.clear()
