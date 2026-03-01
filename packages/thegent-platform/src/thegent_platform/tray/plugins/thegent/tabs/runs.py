"""Runs tab widget for thegent tray plugin."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from thegent_platform.tray.plugins.thegent.api_client import ThegentAPIClient

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget as QtQWidget

logger = logging.getLogger(__name__)


# Run status options
RUN_STATUSES = [
    "all",
    "pending",
    "running",
    "completed",
    "failed",
    "cancelled",
]


class RunDetailDialog(QDialog):
    """Dialog for displaying run details."""

    def __init__(
        self, parent: QtQWidget | None = None, run_data: dict[str, Any] | None = None
    ) -> None:
        """Initialize the run detail dialog.

        Args:
            parent: Parent widget.
            run_data: Existing run data for display.
        """
        super().__init__(parent)
        self.setWindowTitle(f"Run Details - {run_data.get('id', 'Unknown')}")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self._run_data = run_data or {}

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        layout = QVBoxLayout(self)

        # Run info section
        info_group = QWidget()
        info_layout = QFormLayout(info_group)

        # Project
        project = self._run_data.get("project", "Unknown")
        info_layout.addRow("Project:", QLabel(project))

        # Agent
        agent = self._run_data.get("agent", "Unknown")
        info_layout.addRow("Agent:", QLabel(agent))

        # Status
        status = self._run_data.get("status", "unknown")
        status_label = QLabel(status)
        # Color code the status
        if status == "completed":
            status_label.setStyleSheet("color: green; font-weight: bold;")
        elif status == "failed":
            status_label.setStyleSheet("color: red; font-weight: bold;")
        elif status == "running":
            status_label.setStyleSheet("color: blue; font-weight: bold;")
        info_layout.addRow("Status:", status_label)

        # Duration
        duration = self._run_data.get("duration", 0)
        duration_str = f"{duration:.2f}s" if duration else "N/A"
        info_layout.addRow("Duration:", QLabel(duration_str))

        # Cost
        cost = self._run_data.get("cost", 0)
        cost_str = f"${cost:.4f}" if cost else "$0.00"
        info_layout.addRow("Cost:", QLabel(cost_str))

        # XP
        xp = self._run_data.get("xp", 0)
        info_layout.addRow("XP:", QLabel(str(xp)))

        # Started at
        started_at = self._run_data.get("started_at", "N/A")
        info_layout.addRow("Started:", QLabel(started_at))

        # Ended at
        ended_at = self._run_data.get("ended_at", "N/A")
        info_layout.addRow("Ended:", QLabel(ended_at))

        layout.addWidget(info_group)

        # Changes section
        changes_group = QWidget()
        changes_layout = QFormLayout(changes_group)
        changes_title = QLabel("Changes")
        changes_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        changes_layout.addRow(changes_title)

        # Files changed
        files_changed = self._run_data.get("files_changed", 0)
        info_layout.addRow("Files Changed:", QLabel(str(files_changed)))

        # Tests added
        tests_added = self._run_data.get("tests_added", 0)
        info_layout.addRow("Tests Added:", QLabel(str(tests_added)))

        # Docs updated
        docs_updated = self._run_data.get("docs_updated", 0)
        info_layout.addRow("Docs Updated:", QLabel(str(docs_updated)))

        layout.addWidget(changes_group)

        # Output log section
        log_group = QWidget()
        log_layout = QVBoxLayout(log_group)

        log_title = QLabel("Output Log")
        log_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        log_layout.addWidget(log_title)

        self._log_output = QTextEdit()
        self._log_output.setReadOnly(True)
        self._log_output.setMaximumHeight(150)
        self._log_output.setText(self._run_data.get("output_log", "No output available"))
        log_layout.addWidget(self._log_output)

        # Expand/Collapse button for log
        self._expand_log_btn = QPushButton("Expand Log")
        self._expand_log_btn.setCheckable(True)
        self._expand_log_btn.clicked.connect(self._toggle_log_expansion)
        log_layout.addWidget(self._expand_log_btn)

        layout.addWidget(log_group)

        # Dialog buttons
        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close
        )
        self._buttons.rejected.connect(self.reject)

        # Add Re-run button
        self._rerun_button = QPushButton("Re-run")
        self._buttons.addButton(self._rerun_button, QDialogButtonBox.ButtonRole.ActionRole)
        self._rerun_button.clicked.connect(self._on_rerun)

        layout.addWidget(self._buttons)

    def _toggle_log_expansion(self, expanded: bool) -> None:
        """Toggle log expansion.

        Args:
            expanded: Whether to expand the log.
        """
        if expanded:
            self._log_output.setMaximumHeight(400)
            self._expand_log_btn.setText("Collapse Log")
        else:
            self._log_output.setMaximumHeight(150)
            self._expand_log_btn.setText("Expand Log")

    def _on_rerun(self) -> None:
        """Handle re-run button clicked."""
        # This would trigger a re-run of the agent
        logger.debug("Re-run requested for run: %s", self._run_data.get("id"))
        self.accept()

    def get_data(self) -> dict[str, Any]:
        """Get the run data from the dialog.

        Returns:
            Dictionary containing run data.
        """
        return self._run_data


class RunsTab(QWidget):
    """Runs tab widget displaying list of runs."""

    # Tab ID for the plugin system
    TAB_ID = "thegent-runs"

    def __init__(self, api_client: ThegentAPIClient) -> None:
        """Initialize the runs tab.

        Args:
            api_client: Thegent API client.
        """
        super().__init__()
        self._api_client = api_client
        self._runs: list[dict[str, Any]] = []
        self._projects: list[dict[str, Any]] = []
        self._selected_project: str = "all"
        self._selected_status: str = "all"

        self._setup_ui()
        self._load_projects()
        self._load_runs()

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header with filters
        header_layout = QHBoxLayout()

        # Title
        title_label = QLabel("Runs")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Project filter
        project_label = QLabel("Project:")
        header_layout.addWidget(project_label)

        self._project_filter = QComboBox()
        self._project_filter.addItem("All Projects", "all")
        self._project_filter.currentIndexChanged.connect(self._on_project_filter_changed)
        header_layout.addWidget(self._project_filter)

        # Status filter
        status_label = QLabel("Status:")
        header_layout.addWidget(status_label)

        self._status_filter = QComboBox()
        for status in RUN_STATUSES:
            self._status_filter.addItem(status.capitalize(), status)
        self._status_filter.currentIndexChanged.connect(self._on_status_filter_changed)
        header_layout.addWidget(self._status_filter)

        # Refresh button
        self._refresh_button = QPushButton("Refresh")
        self._refresh_button.clicked.connect(self._load_runs)
        header_layout.addWidget(self._refresh_button)

        layout.addLayout(header_layout)

        # Runs table
        self._table = QTableWidget()
        self._table.setColumnCount(8)
        self._table.setHorizontalHeaderLabels(
            ["ID", "Project", "Duration", "Cost", "Date", "Agent", "XP", "Actions"]
        )
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self._table)

        # Auto-refresh timer (30 seconds)
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._load_runs)
        self._refresh_timer.start(30000)  # 30 seconds

    def _load_projects(self) -> None:
        """Load projects for filter dropdown."""
        try:
            self._projects = []
            # Get projects from API
            api_projects = self._api_client.get_projects()
            for proj in api_projects:
                self._projects.append({
                    "id": proj.id,
                    "name": proj.name,
                })
            self._update_project_filter()
        except Exception as e:
            # Handle error - could show a message or log
            logger.warning("Failed to load projects: %s", e)

    def _update_project_filter(self) -> None:
        """Update the project filter dropdown."""
        self._project_filter.clear()
        self._project_filter.addItem("All Projects", "all")
        for project in self._projects:
            self._project_filter.addItem(project["name"], project["id"])

    def _load_runs(self) -> None:
        """Load runs from the API."""
        try:
            self._runs = []

            # Determine project_id filter
            project_id = None if self._selected_project == "all" else self._selected_project

            # Determine status filter
            status = None if self._selected_status == "all" else self._selected_status

            # Get runs from API
            if project_id:
                api_runs = self._api_client.get_runs(project_id, status)
                for run in api_runs:
                    # Look up project name
                    project_name = "Unknown"
                    for proj in self._projects:
                        if proj["id"] == run.project_id:
                            project_name = proj["name"]
                            break

                    # Look up agent name (would need get_agent API, using ID for now)
                    agent_name = run.agent_id

                    self._runs.append({
                        "id": run.id,
                        "project_id": run.project_id,
                        "project": project_name,
                        "agent_id": run.agent_id,
                        "agent": agent_name,
                        "status": run.status,
                        "duration": run.duration,
                        "cost": run.cost,
                        "xp": run.xp,
                        "started_at": run.started_at,
                        "ended_at": run.ended_at,
                        # Additional fields that might be available from extended API
                        "files_changed": 0,
                        "tests_added": 0,
                        "docs_updated": 0,
                        "output_log": "",
                    })
            else:
                # No project selected - get runs for all projects
                for proj in self._projects:
                    try:
                        api_runs = self._api_client.get_runs(proj["id"], status)
                        for run in api_runs:
                            self._runs.append({
                                "id": run.id,
                                "project_id": run.project_id,
                                "project": proj["name"],
                                "agent_id": run.agent_id,
                                "agent": run.agent_id,
                                "status": run.status,
                                "duration": run.duration,
                                "cost": run.cost,
                                "xp": run.xp,
                                "started_at": run.started_at,
                                "ended_at": run.ended_at,
                                "files_changed": 0,
                                "tests_added": 0,
                                "docs_updated": 0,
                                "output_log": "",
                            })
                    except Exception:
                        pass  # Skip projects that fail

            self._update_table()
        except Exception as e:
            # Handle error - could show a message or log
            logger.warning("Failed to load runs: %s", e)

    def _update_table(self) -> None:
        """Update the table with current runs."""
        self._table.setRowCount(0)

        for run in self._runs:
            row = self._table.rowCount()
            self._table.insertRow(row)

            # ID
            id_item = QTableWidgetItem(run["id"][:8] if len(run["id"]) > 8 else run["id"])
            id_item.setData(Qt.ItemDataRole.UserRole, run["id"])
            self._table.setItem(row, 0, id_item)

            # Project
            project_item = QTableWidgetItem(run.get("project", ""))
            self._table.setItem(row, 1, project_item)

            # Duration
            duration = run.get("duration", 0)
            duration_item = QTableWidgetItem(f"{duration:.1f}s" if duration else "N/A")
            self._table.setItem(row, 2, duration_item)

            # Cost
            cost = run.get("cost", 0)
            cost_item = QTableWidgetItem(f"${cost:.2f}" if cost else "$0.00")
            self._table.setItem(row, 3, cost_item)

            # Date
            started_at = run.get("started_at", "N/A")
            # Truncate to just the date/time portion
            if started_at and started_at != "N/A":
                date_item = QTableWidgetItem(started_at[:19].replace("T", " "))
            else:
                date_item = QTableWidgetItem("N/A")
            self._table.setItem(row, 4, date_item)

            # Agent
            agent_item = QTableWidgetItem(run.get("agent", ""))
            self._table.setItem(row, 5, agent_item)

            # XP
            xp_item = QTableWidgetItem(str(run.get("xp", 0)))
            self._table.setItem(row, 6, xp_item)

            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)

            # View Log button
            view_btn = QPushButton("View Log")
            view_btn.setFixedSize(70, 24)
            view_btn.clicked.connect(lambda checked, r=run: self._on_view_log(r))
            actions_layout.addWidget(view_btn)

            self._table.setCellWidget(row, 7, actions_widget)

    def _on_project_filter_changed(self, index: int) -> None:
        """Handle project filter changed."""
        self._selected_project = self._project_filter.currentData()
        self._load_runs()

    def _on_status_filter_changed(self, index: int) -> None:
        """Handle status filter changed."""
        self._selected_status = self._status_filter.currentData()
        self._load_runs()

    def _on_view_log(self, run: dict[str, Any]) -> None:
        """Handle view log button clicked."""
        dialog = RunDetailDialog(parent=self, run_data=run)
        dialog.exec()


def get_tab(tab_id: str, api_client: ThegentAPIClient) -> QWidget | None:
    """Get the tab widget for the given tab_id.

    Args:
        tab_id: The tab ID to retrieve.
        api_client: Thegent API client.

    Returns:
        The widget for the tab, or None if not found.
    """
    if tab_id == "thegent-runs":
        return RunsTab(api_client=api_client)
    return None
