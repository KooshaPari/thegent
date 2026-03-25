"""Projects tab widget for thegent tray plugin."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from thegent_platform.tray.plugins.thegent.api_client import ThegentAPIClient

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget as QtQWidget

logger = logging.getLogger(__name__)


# Supported languages
LANGUAGES = [
    "Python",
    "JavaScript",
    "TypeScript",
    "Go",
    "Rust",
    "Java",
    "C#",
    "C++",
    "Ruby",
    "PHP",
    "Swift",
    "Kotlin",
]

# Supported test frameworks
TEST_FRAMEWORKS = [
    "pytest",
    "unittest",
    "jest",
    "mocha",
    "go test",
    "cargo test",
    "rspec",
    "phpunit",
    "junit",
    "xunit",
]


class ProjectEditDialog(QDialog):
    """Dialog for editing/creating a project."""

    def __init__(self, parent: QtQWidget | None = None, project_data: dict[str, Any] | None = None) -> None:
        """Initialize the project edit dialog.

        Args:
            parent: Parent widget.
            project_data: Existing project data for editing.
        """
        super().__init__(parent)
        self.setWindowTitle("Edit Project" if project_data else "New Project")
        self.setMinimumWidth(500)
        self._project_data = project_data or {}

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        layout = QVBoxLayout(self)

        # Form layout for project fields
        form_layout = QFormLayout()

        # Project fields
        self._name_input = QLineEdit(self._project_data.get("name", ""))
        self._name_input.setPlaceholderText("Project name")
        form_layout.addRow("Name:", self._name_input)

        self._path_input = QLineEdit(self._project_data.get("path", ""))
        self._path_input.setPlaceholderText("/path/to/project")
        form_layout.addRow("Path:", self._path_input)

        # Language combo
        self._language_combo = QComboBox()
        self._language_combo.addItems(LANGUAGES)
        if self._project_data.get("language"):
            index = self._language_combo.findText(self._project_data["language"])
            if index >= 0:
                self._language_combo.setCurrentIndex(index)
        form_layout.addRow("Language:", self._language_combo)

        # Framework
        self._framework_input = QLineEdit(self._project_data.get("framework", ""))
        self._framework_input.setPlaceholderText("e.g., Django, React, FastAPI")
        form_layout.addRow("Framework:", self._framework_input)

        # Test framework combo
        self._test_framework_combo = QComboBox()
        self._test_framework_combo.addItems(TEST_FRAMEWORKS)
        if self._project_data.get("test_framework"):
            index = self._test_framework_combo.findText(self._project_data["test_framework"])
            if index >= 0:
                self._test_framework_combo.setCurrentIndex(index)
        form_layout.addRow("Test Framework:", self._test_framework_combo)

        # Coverage target
        self._coverage_spin = QDoubleSpinBox()
        self._coverage_spin.setRange(0, 100)
        self._coverage_spin.setSuffix(" %")
        self._coverage_spin.setValue(self._project_data.get("coverage_target", 80.0))
        form_layout.addRow("Coverage Target:", self._coverage_spin)

        # Gardener settings group
        gardener_group = QWidget()
        gardener_layout = QVBoxLayout(gardener_group)
        gardener_title = QLabel("Gardener Settings")
        gardener_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        gardener_layout.addWidget(gardener_title)

        gardener_form = QFormLayout()

        # Auto-scan checkbox
        self._auto_scan_check = QPushButton("Auto-scan")
        self._auto_scan_check.setCheckable(True)
        self._auto_scan_check.setChecked(self._project_data.get("auto_scan", True))
        gardener_form.addRow("Auto-scan:", self._auto_scan_check)

        # Scan interval
        self._scan_interval_spin = QSpinBox()
        self._scan_interval_spin.setRange(5, 1440)
        self._scan_interval_spin.setSuffix(" min")
        self._scan_interval_spin.setValue(self._project_data.get("scan_interval", 30))
        gardener_form.addRow("Scan Interval:", self._scan_interval_spin)

        # Auto-fix lint
        self._auto_fix_lint_check = QPushButton("Auto-fix lint")
        self._auto_fix_lint_check.setCheckable(True)
        self._auto_fix_lint_check.setChecked(self._project_data.get("auto_fix_lint", False))
        gardener_form.addRow("Auto-fix Lint:", self._auto_fix_lint_check)

        # Auto-generate tests
        self._auto_generate_tests_check = QPushButton("Auto-generate tests")
        self._auto_generate_tests_check.setCheckable(True)
        self._auto_generate_tests_check.setChecked(self._project_data.get("auto_generate_tests", False))
        gardener_form.addRow("Auto-generate Tests:", self._auto_generate_tests_check)

        # Track cost
        self._track_cost_check = QPushButton("Track cost")
        self._track_cost_check.setCheckable(True)
        self._track_cost_check.setChecked(self._project_data.get("track_cost", True))
        gardener_form.addRow("Track Cost:", self._track_cost_check)

        # Daily budget
        self._daily_budget_spin = QDoubleSpinBox()
        self._daily_budget_spin.setRange(0, 10000)
        self._daily_budget_spin.setPrefix("$ ")
        self._daily_budget_spin.setValue(self._project_data.get("daily_budget", 10.0))
        gardener_form.addRow("Daily Budget:", self._daily_budget_spin)

        gardener_layout.addLayout(gardener_form)
        layout.addLayout(form_layout)
        layout.addWidget(gardener_group)

        # Dialog buttons
        self._buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Save)
        self._buttons.rejected.connect(self.reject)
        self._buttons.accepted.connect(self.accept)
        layout.addWidget(self._buttons)

    def get_data(self) -> dict[str, Any]:
        """Get the project data from the dialog.

        Returns:
            Dictionary containing project and gardener settings.
        """
        return {
            # Project fields
            "name": self._name_input.text(),
            "path": self._path_input.text(),
            "language": self._language_combo.currentText(),
            "framework": self._framework_input.text(),
            "test_framework": self._test_framework_combo.currentText(),
            "coverage_target": self._coverage_spin.value(),
            # Gardener settings
            "auto_scan": self._auto_scan_check.isChecked(),
            "scan_interval": self._scan_interval_spin.value(),
            "auto_fix_lint": self._auto_fix_lint_check.isChecked(),
            "auto_generate_tests": self._auto_generate_tests_check.isChecked(),
            "track_cost": self._track_cost_check.isChecked(),
            "daily_budget": self._daily_budget_spin.value(),
        }


class ProjectsTab(QWidget):
    """Projects tab widget displaying list of projects."""

    # Tab ID for the plugin system
    TAB_ID = "thegent-projects"

    def __init__(self, api_client: ThegentAPIClient) -> None:
        """Initialize the projects tab.

        Args:
            api_client: Thegent API client.
        """
        super().__init__()
        self._api_client = api_client
        self._projects: list[dict[str, Any]] = []

        self._setup_ui()
        self._load_projects()

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header with search and buttons
        header_layout = QHBoxLayout()

        # Search input
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search projects...")
        self._search_input.textChanged.connect(self._on_search_changed)
        header_layout.addWidget(self._search_input)

        # New project button
        self._new_button = QPushButton("+ New Project")
        self._new_button.clicked.connect(self._on_new_project)
        header_layout.addWidget(self._new_button)

        layout.addLayout(header_layout)

        # Projects table
        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["Name", "Language", "Coverage", "Last Run", "Actions"])
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self._table)

        # Auto-refresh timer (30 seconds)
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._load_projects)
        self._refresh_timer.start(30000)  # 30 seconds

    def _load_projects(self) -> None:
        """Load projects from the API."""
        try:
            self._projects = []
            # Get projects from API
            api_projects = self._api_client.get_projects()
            for proj in api_projects:
                self._projects.append(
                    {
                        "id": proj.id,
                        "name": proj.name,
                        "language": proj.language,
                        "coverage": proj.coverage,
                        "last_run": proj.last_run,
                    }
                )
            self._update_table()
        except Exception as e:
            # Handle error - could show a message or log
            logger.warning("Failed to load projects: %s", e)

    def _update_table(self) -> None:
        """Update the table with current projects."""
        search_text = self._search_input.text().lower()
        self._table.setRowCount(0)

        for project in self._projects:
            # Filter by search text
            if search_text and search_text not in project["name"].lower():
                continue

            row = self._table.rowCount()
            self._table.insertRow(row)

            # Name
            name_item = QTableWidgetItem(project["name"])
            name_item.setData(Qt.ItemDataRole.UserRole, project["id"])
            self._table.setItem(row, 0, name_item)

            # Language
            language_item = QTableWidgetItem(project.get("language", ""))
            self._table.setItem(row, 1, language_item)

            # Coverage
            coverage = project.get("coverage", 0.0)
            coverage_item = QTableWidgetItem(f"{coverage:.1f}%")
            self._table.setItem(row, 2, coverage_item)

            # Last Run
            last_run = project.get("last_run", "Never")
            last_run_item = QTableWidgetItem(last_run)
            self._table.setItem(row, 3, last_run_item)

            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)

            # View button
            view_btn = QPushButton("View")
            view_btn.setFixedSize(50, 24)
            view_btn.clicked.connect(lambda checked, p=project: self._on_view_project(p))
            actions_layout.addWidget(view_btn)

            # Edit button
            edit_btn = QPushButton("Edit")
            edit_btn.setFixedSize(50, 24)
            edit_btn.clicked.connect(lambda checked, p=project: self._on_edit_project(p))
            actions_layout.addWidget(edit_btn)

            # Delete button
            delete_btn = QPushButton("Delete")
            delete_btn.setFixedSize(60, 24)
            delete_btn.clicked.connect(lambda checked, p=project: self._on_delete_project(p))
            actions_layout.addWidget(delete_btn)

            self._table.setCellWidget(row, 4, actions_widget)

    def _on_search_changed(self, text: str) -> None:
        """Handle search text changed."""
        self._update_table()

    def _on_new_project(self) -> None:
        """Handle new project button clicked."""
        dialog = ProjectEditDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self._api_client.create_project(**data)
                self._load_projects()
            except Exception as e:
                logger.warning("Failed to create project: %s", e)

    def _on_view_project(self, project: dict[str, Any]) -> None:
        """Handle view project button clicked."""
        # For now, just show the project details
        # Could open a detail dialog in the future
        logger.debug("View project: %s", project["name"])

    def _on_edit_project(self, project: dict[str, Any]) -> None:
        """Handle edit project button clicked."""
        dialog = ProjectEditDialog(parent=self, project_data=project)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self._api_client.update_project(project["id"], **data)
                self._load_projects()
            except Exception as e:
                logger.warning("Failed to update project: %s", e)

    def _on_delete_project(self, project: dict[str, Any]) -> None:
        """Handle delete project button clicked."""
        # Could show a confirmation dialog in the future
        try:
            self._api_client.delete_project(project["id"])
            self._load_projects()
        except Exception as e:
            logger.warning("Failed to delete project: %s", e)


def get_tab(tab_id: str, api_client: ThegentAPIClient) -> QWidget | None:
    """Get the tab widget for the given tab_id.

    Args:
        tab_id: The tab ID to retrieve.
        api_client: Thegent API client.

    Returns:
        The widget for the tab, or None if not found.
    """
    if tab_id == "thegent-projects":
        return ProjectsTab(api_client=api_client)
    return None
