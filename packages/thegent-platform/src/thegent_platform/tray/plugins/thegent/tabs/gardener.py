"""Gardener tab widget for thegent tray plugin."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget as QtQWidget

    from thegent_platform.tray.plugins.thegent.api_client import ThegentAPIClient

logger = logging.getLogger(__name__)


class GardenerConfigDialog(QDialog):
    """Dialog for configuring gardener settings."""

    def __init__(
        self,
        parent: QtQWidget | None = None,
        config_data: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the gardener config dialog.

        Args:
            parent: Parent widget.
            config_data: Existing config data for editing.
        """
        super().__init__(parent)
        self.setWindowTitle("Gardener Configuration")
        self.setMinimumWidth(500)
        self._config_data = config_data or self._default_config()

        self._setup_ui()

    def _default_config(self) -> dict[str, Any]:
        """Return default configuration."""
        return {
            # General
            "enabled": True,
            "start_on_launch": False,
            "scan_interval": 300,
            # Thresholds
            "coverage_warn": 70.0,
            "coverage_critical": 50.0,
            "complexity_warn": 15,
            "complexity_critical": 25,
            "lint_errors_warn": 5,
            "lint_errors_critical": 20,
            # Auto-fix
            "auto_fix_lint": True,
            "auto_fix_tests": True,
            "auto_fix_docs": False,
            "auto_fix_complexity": True,
            # Resources
            "max_concurrent_agents": 5,
            "max_runtime_per_task": 600,
            "stop_at_budget_percent": 90,
            # Notifications
            "notify_on_scan": True,
            "notify_on_fix": True,
            "notify_on_error": True,
            "notify_on_budget": True,
        }

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        layout = QVBoxLayout(self)

        # General settings group
        general_group = QGroupBox("General")
        general_layout = QFormLayout()

        self._enabled_check = QCheckBox()
        self._enabled_check.setChecked(self._config_data.get("enabled", True))
        general_layout.addRow("Enable Gardener:", self._enabled_check)

        self._start_on_launch_check = QCheckBox()
        self._start_on_launch_check.setChecked(self._config_data.get("start_on_launch", False))
        general_layout.addRow("Start on Launch:", self._start_on_launch_check)

        self._scan_interval_spin = QSpinBox()
        self._scan_interval_spin.setRange(60, 3600)
        self._scan_interval_spin.setSuffix(" seconds")
        self._scan_interval_spin.setValue(self._config_data.get("scan_interval", 300))
        general_layout.addRow("Scan Interval:", self._scan_interval_spin)

        general_group.setLayout(general_layout)
        layout.addWidget(general_group)

        # Thresholds group
        thresholds_group = QGroupBox("Thresholds")
        thresholds_layout = QFormLayout()

        # Coverage thresholds
        self._coverage_warn_spin = QSpinBox()
        self._coverage_warn_spin.setRange(0, 100)
        self._coverage_warn_spin.setSuffix(" %")
        self._coverage_warn_spin.setValue(int(self._config_data.get("coverage_warn", 70.0)))
        thresholds_layout.addRow("Coverage Warn:", self._coverage_warn_spin)

        self._coverage_critical_spin = QSpinBox()
        self._coverage_critical_spin.setRange(0, 100)
        self._coverage_critical_spin.setSuffix(" %")
        self._coverage_critical_spin.setValue(int(self._config_data.get("coverage_critical", 50.0)))
        thresholds_layout.addRow("Coverage Critical:", self._coverage_critical_spin)

        # Complexity thresholds
        self._complexity_warn_spin = QSpinBox()
        self._complexity_warn_spin.setRange(1, 100)
        self._complexity_warn_spin.setValue(self._config_data.get("complexity_warn", 15))
        thresholds_layout.addRow("Complexity Warn:", self._complexity_warn_spin)

        self._complexity_critical_spin = QSpinBox()
        self._complexity_critical_spin.setRange(1, 100)
        self._complexity_critical_spin.setValue(self._config_data.get("complexity_critical", 25))
        thresholds_layout.addRow("Complexity Critical:", self._complexity_critical_spin)

        # Lint error thresholds
        self._lint_warn_spin = QSpinBox()
        self._lint_warn_spin.setRange(0, 1000)
        self._lint_warn_spin.setValue(self._config_data.get("lint_errors_warn", 5))
        thresholds_layout.addRow("Lint Errors Warn:", self._lint_warn_spin)

        self._lint_critical_spin = QSpinBox()
        self._lint_critical_spin.setRange(0, 1000)
        self._lint_critical_spin.setValue(self._config_data.get("lint_errors_critical", 20))
        thresholds_layout.addRow("Lint Errors Critical:", self._lint_critical_spin)

        thresholds_group.setLayout(thresholds_layout)
        layout.addWidget(thresholds_group)

        # Auto-fix group
        autofix_group = QGroupBox("Auto-fix Settings")
        autofix_layout = QHBoxLayout()

        self._auto_fix_lint_check = QCheckBox("Lint")
        self._auto_fix_lint_check.setChecked(self._config_data.get("auto_fix_lint", True))
        autofix_layout.addWidget(self._auto_fix_lint_check)

        self._auto_fix_tests_check = QCheckBox("Tests")
        self._auto_fix_tests_check.setChecked(self._config_data.get("auto_fix_tests", True))
        autofix_layout.addWidget(self._auto_fix_tests_check)

        self._auto_fix_docs_check = QCheckBox("Docs")
        self._auto_fix_docs_check.setChecked(self._config_data.get("auto_fix_docs", False))
        autofix_layout.addWidget(self._auto_fix_docs_check)

        self._auto_fix_complexity_check = QCheckBox("Complexity")
        self._auto_fix_complexity_check.setChecked(self._config_data.get("auto_fix_complexity", True))
        autofix_layout.addWidget(self._auto_fix_complexity_check)

        autofix_group.setLayout(autofix_layout)
        layout.addWidget(autofix_group)

        # Resources group
        resources_group = QGroupBox("Resources")
        resources_layout = QFormLayout()

        self._max_concurrent_spin = QSpinBox()
        self._max_concurrent_spin.setRange(1, 50)
        self._max_concurrent_spin.setValue(self._config_data.get("max_concurrent_agents", 5))
        resources_layout.addRow("Max Concurrent Agents:", self._max_concurrent_spin)

        self._max_runtime_spin = QSpinBox()
        self._max_runtime_spin.setRange(60, 3600)
        self._max_runtime_spin.setSuffix(" seconds")
        self._max_runtime_spin.setValue(self._config_data.get("max_runtime_per_task", 600))
        resources_layout.addRow("Max Runtime per Task:", self._max_runtime_spin)

        self._budget_stop_spin = QSpinBox()
        self._budget_stop_spin.setRange(50, 100)
        self._budget_stop_spin.setSuffix(" %")
        self._budget_stop_spin.setValue(self._config_data.get("stop_at_budget_percent", 90))
        resources_layout.addRow("Stop at Budget:", self._budget_stop_spin)

        resources_group.setLayout(resources_layout)
        layout.addWidget(resources_group)

        # Notifications group
        notifications_group = QGroupBox("Notifications")
        notifications_layout = QHBoxLayout()

        self._notify_scan_check = QCheckBox("On Scan")
        self._notify_scan_check.setChecked(self._config_data.get("notify_on_scan", True))
        notifications_layout.addWidget(self._notify_scan_check)

        self._notify_fix_check = QCheckBox("On Fix")
        self._notify_fix_check.setChecked(self._config_data.get("notify_on_fix", True))
        notifications_layout.addWidget(self._notify_fix_check)

        self._notify_error_check = QCheckBox("On Error")
        self._notify_error_check.setChecked(self._config_data.get("notify_on_error", True))
        notifications_layout.addWidget(self._notify_error_check)

        self._notify_budget_check = QCheckBox("On Budget")
        self._notify_budget_check.setChecked(self._config_data.get("notify_on_budget", True))
        notifications_layout.addWidget(self._notify_budget_check)

        notifications_group.setLayout(notifications_layout)
        layout.addWidget(notifications_group)

        # Dialog buttons
        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Save
        )
        self._buttons.rejected.connect(self.reject)
        self._buttons.accepted.connect(self.accept)
        layout.addWidget(self._buttons)

    def get_data(self) -> dict[str, Any]:
        """Get the config data from the dialog.

        Returns:
            Dictionary containing gardener settings.
        """
        return {
            # General
            "enabled": self._enabled_check.isChecked(),
            "start_on_launch": self._start_on_launch_check.isChecked(),
            "scan_interval": self._scan_interval_spin.value(),
            # Thresholds
            "coverage_warn": float(self._coverage_warn_spin.value()),
            "coverage_critical": float(self._coverage_critical_spin.value()),
            "complexity_warn": self._complexity_warn_spin.value(),
            "complexity_critical": self._complexity_critical_spin.value(),
            "lint_errors_warn": self._lint_warn_spin.value(),
            "lint_errors_critical": self._lint_critical_spin.value(),
            # Auto-fix
            "auto_fix_lint": self._auto_fix_lint_check.isChecked(),
            "auto_fix_tests": self._auto_fix_tests_check.isChecked(),
            "auto_fix_docs": self._auto_fix_docs_check.isChecked(),
            "auto_fix_complexity": self._auto_fix_complexity_check.isChecked(),
            # Resources
            "max_concurrent_agents": self._max_concurrent_spin.value(),
            "max_runtime_per_task": self._max_runtime_spin.value(),
            "stop_at_budget_percent": self._budget_stop_spin.value(),
            # Notifications
            "notify_on_scan": self._notify_scan_check.isChecked(),
            "notify_on_fix": self._notify_fix_check.isChecked(),
            "notify_on_error": self._notify_error_check.isChecked(),
            "notify_on_budget": self._notify_budget_check.isChecked(),
        }


class GardenerTab(QWidget):
    """Gardener tab widget displaying gardener status and controls."""

    # Tab ID for the plugin system
    TAB_ID = "thegent-gardener"

    def __init__(self, api_client: ThegentAPIClient) -> None:
        """Initialize the gardener tab.

        Args:
            api_client: Thegent API client.
        """
        super().__init__()
        self._api_client = api_client
        self._status: dict[str, Any] = {}
        self._hunger_states: list[dict[str, Any]] = []
        self._recent_activity: list[dict[str, Any]] = []

        self._setup_ui()
        self._load_status()

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header with title and buttons
        header_layout = QHBoxLayout()

        # Title
        title_label = QLabel("Gardener")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Settings button
        self._settings_button = QPushButton("Settings")
        self._settings_button.clicked.connect(self._on_settings)
        header_layout.addWidget(self._settings_button)

        layout.addLayout(header_layout)

        # Status section
        status_group = QGroupBox("Status")
        status_layout = QHBoxLayout()

        # Status indicator
        self._status_indicator = QLabel("Stopped")
        self._status_indicator.setStyleSheet(
            "padding: 5px 10px; border-radius: 4px; background-color: #ff6b6b; color: white; font-weight: bold;"
        )
        status_layout.addWidget(self._status_indicator)

        # Start button
        self._start_button = QPushButton("Start")
        self._start_button.clicked.connect(self._on_start)
        status_layout.addWidget(self._start_button)

        # Stop button
        self._stop_button = QPushButton("Stop")
        self._stop_button.setEnabled(False)
        self._stop_button.clicked.connect(self._on_stop)
        status_layout.addWidget(self._stop_button)

        # Scan Now button
        self._scan_button = QPushButton("Scan Now")
        self._scan_button.clicked.connect(self._on_scan)
        status_layout.addWidget(self._scan_button)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Main content area - split into two columns
        main_layout = QHBoxLayout()

        # Left column: Garden State and Recent Activity
        left_column = QVBoxLayout()

        # Garden State section
        garden_state_group = QGroupBox("Garden State")
        garden_state_layout = QFormLayout()

        self._total_xp_label = QLabel("0")
        garden_state_layout.addRow("Total XP:", self._total_xp_label)

        self._level_label = QLabel("1")
        garden_state_layout.addRow("Level:", self._level_label)

        self._active_agents_label = QLabel("0")
        garden_state_layout.addRow("Active Agents:", self._active_agents_label)

        self._last_scan_label = QLabel("Never")
        garden_state_layout.addRow("Last Scan:", self._last_scan_label)

        self._uptime_label = QLabel("0:00:00")
        garden_state_layout.addRow("Uptime:", self._uptime_label)

        self._runs_today_label = QLabel("0")
        garden_state_layout.addRow("Runs Today:", self._runs_today_label)

        garden_state_group.setLayout(garden_state_layout)
        left_column.addWidget(garden_state_group)

        # Recent Activity section
        activity_group = QGroupBox("Recent Activity")
        activity_layout = QVBoxLayout()

        self._activity_list = QListWidget()
        self._activity_list.setMaximumHeight(150)
        self._activity_list.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        activity_layout.addWidget(self._activity_list)

        activity_group.setLayout(activity_layout)
        left_column.addWidget(activity_group)

        main_layout.addLayout(left_column)

        # Right column: Hunger States
        right_column = QVBoxLayout()

        hunger_group = QGroupBox("Hunger States")
        hunger_layout = QVBoxLayout()

        self._hunger_list = QListWidget()
        self._hunger_list.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        hunger_layout.addWidget(self._hunger_list)

        # Action buttons for hunger states
        hunger_actions_layout = QHBoxLayout()

        self._auto_fix_button = QPushButton("Auto-fix")
        self._auto_fix_button.clicked.connect(self._on_auto_fix)
        hunger_actions_layout.addWidget(self._auto_fix_button)

        self._ignore_button = QPushButton("Ignore")
        self._ignore_button.clicked.connect(self._on_ignore)
        hunger_actions_layout.addWidget(self._ignore_button)

        self._snooze_button = QPushButton("Snooze")
        self._snooze_button.clicked.connect(self._on_snooze)
        hunger_actions_layout.addWidget(self._snooze_button)

        hunger_actions_layout.addStretch()

        hunger_layout.addLayout(hunger_actions_layout)

        hunger_group.setLayout(hunger_layout)
        right_column.addWidget(hunger_group)

        main_layout.addLayout(right_column)

        layout.addLayout(main_layout)

        # Auto-refresh timer (10 seconds)
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._load_status)
        self._refresh_timer.start(10000)  # 10 seconds

    def _load_status(self) -> None:
        """Load gardener status from the API."""
        try:
            status = self._api_client.get_gardener_status()
            self._status = {
                "running": status.running,
                "active_agents": status.active_agents,
                "max_agents": status.max_agents,
                "uptime_seconds": status.uptime_seconds,
                "runs_today": status.runs_today,
                "total_xp": status.total_xp,
                "level": status.level,
                "hunger_states": status.hunger_states,
            }
            self._update_ui()
        except Exception as e:
            logger.warning("Failed to load gardener status: %s", e)

    def _update_ui(self) -> None:
        """Update the UI with current status."""
        # Update status indicator
        if self._status.get("running", False):
            self._status_indicator.setText("Running")
            self._status_indicator.setStyleSheet(
                "padding: 5px 10px; border-radius: 4px; background-color: #51cf66; color: white; font-weight: bold;"
            )
            self._start_button.setEnabled(False)
            self._stop_button.setEnabled(True)
        else:
            self._status_indicator.setText("Stopped")
            self._status_indicator.setStyleSheet(
                "padding: 5px 10px; border-radius: 4px; background-color: #ff6b6b; color: white; font-weight: bold;"
            )
            self._start_button.setEnabled(True)
            self._stop_button.setEnabled(False)

        # Update garden state
        self._total_xp_label.setText(f"{self._status.get('total_xp', 0):,}")
        self._level_label.setText(str(self._status.get("level", 1)))
        self._active_agents_label.setText(
            f"{self._status.get('active_agents', 0)}/{self._status.get('max_agents', 0)}"
        )

        # Format uptime
        uptime_seconds = self._status.get("uptime_seconds", 0)
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        self._uptime_label.setText(f"{hours}:{minutes:02d}:{seconds:02d}")

        self._runs_today_label.setText(str(self._status.get("runs_today", 0)))
        self._last_scan_label.setText("Recently")

        # Update hunger states
        self._hunger_states = []
        hunger_data = self._status.get("hunger_states", {})
        self._hunger_list.clear()

        for issue_type, value in hunger_data.items():
            severity = "info"
            if isinstance(value, dict):
                severity = value.get("severity", "info")
                display_value = value.get("value", value.get("count", 0))
            else:
                display_value = value

            self._hunger_states.append({
                "type": issue_type,
                "value": display_value,
                "severity": severity,
            })

            # Create list item
            item = QListWidgetItem(f"{issue_type}: {display_value}")
            # Set color based on severity
            if severity == "critical":
                item.setForeground(Qt.GlobalColor.red)
            elif severity == "warning":
                item.setForeground(Qt.GlobalColor.darkYellow)
            else:
                item.setForeground(Qt.GlobalColor.blue)
            self._hunger_list.addItem(item)

    def _on_start(self) -> None:
        """Handle start button clicked."""
        try:
            self._api_client.start_gardener()
            self._load_status()
        except Exception as e:
            logger.warning("Failed to start gardener: %s", e)

    def _on_stop(self) -> None:
        """Handle stop button clicked."""
        try:
            self._api_client.stop_gardener()
            self._load_status()
        except Exception as e:
            logger.warning("Failed to stop gardener: %s", e)

    def _on_scan(self) -> None:
        """Handle scan button clicked."""
        try:
            self._api_client.trigger_scan()
            self._add_activity("Scan triggered")
            self._load_status()
        except Exception as e:
            logger.warning("Failed to trigger scan: %s", e)

    def _on_settings(self) -> None:
        """Handle settings button clicked."""
        try:
            config = self._api_client.get_gardener_config()
            dialog = GardenerConfigDialog(parent=self, config_data=config)
            if dialog.exec():
                data = dialog.get_data()
                self._api_client.update_gardener_config(**data)
        except Exception as e:
            logger.warning("Failed to update gardener config: %s", e)

    def _on_auto_fix(self) -> None:
        """Handle auto-fix button clicked for selected hunger state."""
        current_item = self._hunger_list.currentItem()
        if current_item:
            index = self._hunger_list.row(current_item)
            if index < len(self._hunger_states):
                issue = self._hunger_states[index]
                self._add_activity(f"Auto-fix applied to: {issue['type']}")
                logger.debug("Auto-fix requested for: %s", issue["type"])

    def _on_ignore(self) -> None:
        """Handle ignore button clicked for selected hunger state."""
        current_item = self._hunger_list.currentItem()
        if current_item:
            index = self._hunger_list.row(current_item)
            if index < len(self._hunger_states):
                issue = self._hunger_states[index]
                self._add_activity(f"Ignored: {issue['type']}")
                logger.debug("Ignore requested for: %s", issue["type"])
                # Remove from list
                self._hunger_list.takeItem(index)
                self._hunger_states.pop(index)

    def _on_snooze(self) -> None:
        """Handle snooze button clicked for selected hunger state."""
        current_item = self._hunger_list.currentItem()
        if current_item:
            index = self._hunger_list.row(current_item)
            if index < len(self._hunger_states):
                issue = self._hunger_states[index]
                self._add_activity(f"Snoozed: {issue['type']}")
                logger.debug("Snooze requested for: %s", issue["type"])

    def _add_activity(self, message: str) -> None:
        """Add an activity log entry.

        Args:
            message: Activity message to add.
        """
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        self._activity_list.insertItem(0, f"[{timestamp}] {message}")

        # Keep only last 50 items
        while self._activity_list.count() > 50:
            self._activity_list.takeItem(self._activity_list.count() - 1)

        self._recent_activity.append({"timestamp": timestamp, "message": message})


def get_tab(tab_id: str, api_client: ThegentAPIClient) -> QWidget | None:
    """Get the tab widget for the given tab_id.

    Args:
        tab_id: The tab ID to retrieve.
        api_client: Thegent API client.

    Returns:
        The widget for the tab, or None if not found.
    """
    if tab_id == "thegent-gardener":
        return GardenerTab(api_client=api_client)
    return None
