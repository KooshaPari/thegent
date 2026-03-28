"""Costs tab widget for thegent tray plugin."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget as QtQWidget

    from thegent_platform.tray.plugins.thegent.api_client import ThegentAPIClient

logger = logging.getLogger(__name__)


# Alert types
ALERT_TYPES = [
    "daily_threshold",
    "monthly_threshold",
    "spike",
    "project_specific",
]


class CostAlertDialog(QDialog):
    """Dialog for configuring cost alerts."""

    def __init__(self, parent: QtQWidget | None = None, alert_data: dict[str, Any] | None = None) -> None:
        """Initialize the cost alert dialog.

        Args:
            parent: Parent widget.
            alert_data: Existing alert data for editing.
        """
        super().__init__(parent)
        self.setWindowTitle("Configure Cost Alert")
        self.setMinimumWidth(450)
        self._alert_data = alert_data or {}

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        layout = QVBoxLayout(self)

        # Alert type section
        type_group = QWidget()
        type_layout = QVBoxLayout(type_group)

        type_title = QLabel("Alert Type")
        type_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        type_layout.addWidget(type_title)

        # Radio buttons for alert type
        self._alert_type_group = QButtonGroup(self)

        for alert_type in ALERT_TYPES:
            radio = QRadioButton(alert_type.replace("_", " ").title())
            radio.setObjectName(alert_type)
            self._alert_type_group.addButton(radio)
            type_layout.addWidget(radio)

        # Select default
        default_type = self._alert_data.get("alert_type", ALERT_TYPES[0])
        for button in self._alert_type_group.buttons():
            if button.objectName() == default_type:
                button.setChecked(True)
                break

        layout.addWidget(type_group)

        # Threshold section
        threshold_group = QWidget()
        threshold_layout = QFormLayout(threshold_group)

        threshold_title = QLabel("Threshold")
        threshold_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        threshold_layout.addRow("", threshold_title)

        # Threshold type (percentage or absolute)
        self._threshold_type_combo = QComboBox()
        self._threshold_type_combo.addItems(["Percentage", "Absolute Value"])
        threshold_layout.addRow("Type:", self._threshold_type_combo)

        # Threshold value
        self._threshold_spin = QDoubleSpinBox()
        self._threshold_spin.setRange(0, 10000)
        self._threshold_spin.setPrefix("$ ")
        self._threshold_spin.setDecimals(2)
        self._threshold_spin.setValue(self._alert_data.get("threshold_value", 80.0))
        threshold_layout.addRow("Value:", self._threshold_spin)

        # Percentage spin (alternative)
        self._percentage_spin = QDoubleSpinBox()
        self._percentage_spin.setRange(0, 200)
        self._percentage_spin.setSuffix(" %")
        self._percentage_spin.setValue(self._alert_data.get("threshold_percent", 80.0))
        threshold_layout.addRow("Percentage:", self._percentage_spin)

        layout.addWidget(threshold_group)

        # Notification section
        notification_group = QWidget()
        notification_layout = QVBoxLayout(notification_group)

        notification_title = QLabel("Notifications")
        notification_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        notification_layout.addWidget(notification_title)

        # Notification checkboxes
        self._system_notification_check = QCheckBox("System Notification")
        self._system_notification_check.setChecked(self._alert_data.get("notify_system", True))
        notification_layout.addWidget(self._system_notification_check)

        self._email_notification_check = QCheckBox("Email")
        self._email_notification_check.setChecked(self._alert_data.get("notify_email", False))
        notification_layout.addWidget(self._email_notification_check)

        self._auto_pause_check = QCheckBox("Auto-pause Agents")
        self._auto_pause_check.setChecked(self._alert_data.get("auto_pause", False))
        notification_layout.addWidget(self._auto_pause_check)

        layout.addWidget(notification_group)

        # Project selector (for project-specific alerts)
        project_group = QWidget()
        project_layout = QFormLayout(project_group)

        project_title = QLabel("Project")
        project_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        project_layout.addRow("", project_title)

        self._project_combo = QComboBox()
        self._project_combo.addItem("All Projects", "all")
        # Projects would be loaded from API in a real implementation
        project_layout.addRow("Project:", self._project_combo)

        layout.addWidget(project_group)

        # Dialog buttons
        self._buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Save)
        self._buttons.rejected.connect(self.reject)
        self._buttons.accepted.connect(self.accept)
        layout.addWidget(self._buttons)

    def get_data(self) -> dict[str, Any]:
        """Get the alert data from the dialog.

        Returns:
            Dictionary containing alert configuration.
        """
        # Get selected alert type
        selected_type = "daily_threshold"
        for button in self._alert_type_group.buttons():
            if button.isChecked():
                selected_type = button.objectName()
                break

        return {
            "alert_type": selected_type,
            "threshold_type": self._threshold_type_combo.currentText().lower().replace(" ", "_"),
            "threshold_value": self._threshold_spin.value(),
            "threshold_percent": self._percentage_spin.value(),
            "notify_system": self._system_notification_check.isChecked(),
            "notify_email": self._email_notification_check.isChecked(),
            "auto_pause": self._auto_pause_check.isChecked(),
            "project_id": self._project_combo.currentData(),
        }


class CostsTab(QWidget):
    """Costs tab widget displaying cost tracking and alerts."""

    # Tab ID for the plugin system
    TAB_ID = "thegent-costs"

    def __init__(self, api_client: ThegentAPIClient) -> None:
        """Initialize the costs tab.

        Args:
            api_client: Thegent API client.
        """
        super().__init__()
        self._api_client = api_client
        self._daily_cost: dict[str, Any] = {}
        self._monthly_cost: dict[str, Any] = {}
        self._alerts: list[dict[str, Any]] = []

        self._setup_ui()
        self._load_costs()

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Costs")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # Refresh button
        self._refresh_button = QPushButton("Refresh")
        self._refresh_button.clicked.connect(self._load_costs)
        header_layout.addWidget(self._refresh_button)

        scroll_layout.addLayout(header_layout)

        # Daily spend section
        daily_group = self._create_daily_spend_section()
        scroll_layout.addWidget(daily_group)

        # Monthly spend section
        monthly_group = self._create_monthly_spend_section()
        scroll_layout.addWidget(monthly_group)

        # Daily trend chart section
        trend_group = self._create_daily_trend_section()
        scroll_layout.addWidget(trend_group)

        # By-project breakdown section
        project_group = self._create_project_breakdown_section()
        scroll_layout.addWidget(project_group)

        # By-agent breakdown section
        agent_group = self._create_agent_breakdown_section()
        scroll_layout.addWidget(agent_group)

        # Alert configuration section
        alert_group = self._create_alert_section()
        scroll_layout.addWidget(alert_group)

        scroll_layout.addStretch()

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # Auto-refresh timer (30 seconds)
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._load_costs)
        self._refresh_timer.start(30000)  # 30 seconds

    def _create_daily_spend_section(self) -> QWidget:
        """Create the daily spend progress section.

        Returns:
            The daily spend widget.
        """
        group = QFrame()
        group.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(group)

        # Title
        title = QLabel("Daily Spend")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Progress bar and labels
        progress_layout = QHBoxLayout()

        self._daily_progress = QProgressBar()
        self._daily_progress.setRange(0, 100)
        self._daily_progress.setValue(0)
        progress_layout.addWidget(self._daily_progress)

        self._daily_label = QLabel("$0.00 / $0.00 (0%)")
        self._daily_label.setMinimumWidth(150)
        progress_layout.addWidget(self._daily_label)

        layout.addLayout(progress_layout)

        return group

    def _create_monthly_spend_section(self) -> QWidget:
        """Create the monthly spend progress section.

        Returns:
            The monthly spend widget.
        """
        group = QFrame()
        group.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(group)

        # Title
        title = QLabel("Monthly Spend")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Progress bar and labels
        progress_layout = QHBoxLayout()

        self._monthly_progress = QProgressBar()
        self._monthly_progress.setRange(0, 100)
        self._monthly_progress.setValue(0)
        progress_layout.addWidget(self._monthly_progress)

        self._monthly_label = QLabel("$0.00 / $0.00 (0%)")
        self._monthly_label.setMinimumWidth(150)
        progress_layout.addWidget(self._monthly_label)

        layout.addLayout(progress_layout)

        return group

    def _create_daily_trend_section(self) -> QWidget:
        """Create the daily trend bar chart section.

        Returns:
            The daily trend widget.
        """
        group = QFrame()
        group.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(group)

        # Title
        title = QLabel("Daily Trend (Last 7 Days)")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Bar chart using progress bars
        self._trend_layout = QHBoxLayout()
        self._trend_bars: list[QProgressBar] = []
        self._trend_labels: list[QLabel] = []

        for i in range(7):
            # Day label
            day_label = QLabel(f"Day {i + 1}")
            day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._trend_layout.addWidget(day_label)
            self._trend_labels.append(day_label)

        layout.addLayout(self._trend_layout)

        # Values layout
        values_layout = QHBoxLayout()
        self._trend_values: list[QLabel] = []

        for _i in range(7):
            value_label = QLabel("$0")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            values_layout.addWidget(value_label)
            self._trend_values.append(value_label)

        layout.addLayout(values_layout)

        return group

    def _create_project_breakdown_section(self) -> QWidget:
        """Create the by-project breakdown section.

        Returns:
            The project breakdown widget.
        """
        group = QFrame()
        group.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(group)

        # Title
        title = QLabel("By Project")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Table
        self._project_table = QTableWidget()
        self._project_table.setColumnCount(3)
        self._project_table.setHorizontalHeaderLabels(["Project", "Spend", "Budget"])
        self._project_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._project_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._project_table.horizontalHeader().setStretchLastSection(True)
        self._project_table.setMaximumHeight(150)

        layout.addWidget(self._project_table)

        return group

    def _create_agent_breakdown_section(self) -> QWidget:
        """Create the by-agent breakdown section.

        Returns:
            The agent breakdown widget.
        """
        group = QFrame()
        group.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(group)

        # Title
        title = QLabel("By Agent")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Table
        self._agent_table = QTableWidget()
        self._agent_table.setColumnCount(3)
        self._agent_table.setHorizontalHeaderLabels(["Agent", "Spend", "Budget"])
        self._agent_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._agent_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._agent_table.horizontalHeader().setStretchLastSection(True)
        self._agent_table.setMaximumHeight(150)

        layout.addWidget(self._agent_table)

        return group

    def _create_alert_section(self) -> QWidget:
        """Create the alert configuration section.

        Returns:
            The alert configuration widget.
        """
        group = QFrame()
        group.setFrameShape(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(group)

        # Title and add button
        header_layout = QHBoxLayout()
        title = QLabel("Alert Configuration")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        self._add_alert_button = QPushButton("+ Add Alert")
        self._add_alert_button.clicked.connect(self._on_add_alert)
        header_layout.addWidget(self._add_alert_button)

        layout.addLayout(header_layout)

        # Alerts table
        self._alerts_table = QTableWidget()
        self._alerts_table.setColumnCount(4)
        self._alerts_table.setHorizontalHeaderLabels(["Type", "Threshold", "Notifications", "Actions"])
        self._alerts_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._alerts_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._alerts_table.horizontalHeader().setStretchLastSection(True)
        self._alerts_table.setMaximumHeight(120)

        layout.addWidget(self._alerts_table)

        return group

    def _load_costs(self) -> None:
        """Load cost data from the API."""
        try:
            # Load daily costs
            daily = self._api_client.get_cost_daily()
            self._daily_cost = {
                "spend": daily.daily_spend,
                "budget": daily.daily_budget,
                "percent": daily.daily_percent,
                "by_project": daily.by_project,
                "by_agent": daily.by_agent,
            }

            # Load monthly costs
            monthly = self._api_client.get_cost_monthly()
            self._monthly_cost = {
                "spend": monthly.monthly_spend,
                "budget": monthly.monthly_budget,
                "percent": monthly.monthly_percent,  # type: ignore[reportAttributeAccessIssue]
            }

            # Load alerts
            self._alerts = self._api_client.get_cost_alerts()

            # Update UI
            self._update_daily_spend()
            self._update_monthly_spend()
            self._update_trend()
            self._update_project_breakdown()
            self._update_agent_breakdown()
            self._update_alerts()

        except Exception as e:
            logger.warning("Failed to load costs: %s", e)

    def _update_daily_spend(self) -> None:
        """Update the daily spend display."""
        spend = self._daily_cost.get("spend", 0)
        budget = self._daily_cost.get("budget", 0)
        percent = self._daily_cost.get("percent", 0)

        self._daily_progress.setValue(int(min(percent, 100)))
        self._daily_label.setText(f"${spend:.2f} / ${budget:.2f} ({percent:.1f}%)")

        # Color code based on percentage
        if percent >= 100:
            self._daily_progress.setStyleSheet("QProgressBar::chunk { background-color: red; }")
        elif percent >= 80:
            self._daily_progress.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
        else:
            self._daily_progress.setStyleSheet("QProgressBar::chunk { background-color: green; }")

    def _update_monthly_spend(self) -> None:
        """Update the monthly spend display."""
        spend = self._monthly_cost.get("spend", 0)
        budget = self._monthly_cost.get("budget", 0)
        percent = self._monthly_cost.get("percent", 0)

        self._monthly_progress.setValue(int(min(percent, 100)))
        self._monthly_label.setText(f"${spend:.2f} / ${budget:.2f} ({percent:.1f}%)")

        # Color code based on percentage
        if percent >= 100:
            self._monthly_progress.setStyleSheet("QProgressBar::chunk { background-color: red; }")
        elif percent >= 80:
            self._monthly_progress.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
        else:
            self._monthly_progress.setStyleSheet("QProgressBar::chunk { background-color: green; }")

    def _update_trend(self) -> None:
        """Update the daily trend chart."""
        # For now, display placeholder data
        # In a real implementation, this would fetch historical data
        for i in range(7):
            # Simulated daily values
            value = (i + 1) * 10.0
            self._trend_values[i].setText(f"${value:.2f}")

    def _update_project_breakdown(self) -> None:
        """Update the project breakdown table."""
        self._project_table.setRowCount(0)

        # Get project costs from the daily summary
        project_costs = self._daily_cost.get("by_project", {})
        budget_per_project = 10.0  # Default budget

        for project_name, spend in project_costs.items():
            row = self._project_table.rowCount()
            self._project_table.insertRow(row)

            # Project name
            self._project_table.setItem(row, 0, QTableWidgetItem(project_name))

            # Spend
            spend_item = QTableWidgetItem(f"${spend:.2f}")
            self._project_table.setItem(row, 1, spend_item)

            # Budget
            budget_item = QTableWidgetItem(f"${budget_per_project:.2f}")
            self._project_table.setItem(row, 2, budget_item)

    def _update_agent_breakdown(self) -> None:
        """Update the agent breakdown table."""
        self._agent_table.setRowCount(0)

        # Get agent costs from the daily summary
        agent_costs = self._daily_cost.get("by_agent", {})
        budget_per_agent = 5.0  # Default budget

        for agent_name, spend in agent_costs.items():
            row = self._agent_table.rowCount()
            self._agent_table.insertRow(row)

            # Agent name
            self._agent_table.setItem(row, 0, QTableWidgetItem(agent_name))

            # Spend
            spend_item = QTableWidgetItem(f"${spend:.2f}")
            self._agent_table.setItem(row, 1, spend_item)

            # Budget
            budget_item = QTableWidgetItem(f"${budget_per_agent:.2f}")
            self._agent_table.setItem(row, 2, budget_item)

    def _update_alerts(self) -> None:
        """Update the alerts table."""
        self._alerts_table.setRowCount(0)

        for alert in self._alerts:
            row = self._alerts_table.rowCount()
            self._alerts_table.insertRow(row)

            # Type
            alert_type = alert.get("alert_type", "unknown")
            self._alerts_table.setItem(row, 0, QTableWidgetItem(alert_type))

            # Threshold
            threshold = alert.get("threshold_value", 0)
            self._alerts_table.setItem(row, 1, QTableWidgetItem(f"${threshold}"))

            # Notifications
            notifications = []
            if alert.get("notify_system"):
                notifications.append("System")
            if alert.get("notify_email"):
                notifications.append("Email")
            if alert.get("auto_pause"):
                notifications.append("Auto-pause")
            self._alerts_table.setItem(row, 2, QTableWidgetItem(", ".join(notifications) if notifications else "None"))

            # Actions - Delete button
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)

            delete_btn = QPushButton("Delete")
            delete_btn.setFixedSize(60, 24)
            delete_btn.clicked.connect(lambda checked, a=alert: self._on_delete_alert(a))
            actions_layout.addWidget(delete_btn)

            self._alerts_table.setCellWidget(row, 3, actions_widget)

    def _on_add_alert(self) -> None:
        """Handle add alert button clicked."""
        dialog = CostAlertDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self._api_client.create_cost_alert(**data)
                self._load_costs()
            except Exception as e:
                logger.warning("Failed to create alert: %s", e)

    def _on_delete_alert(self, alert: dict[str, Any]) -> None:
        """Handle delete alert button clicked."""
        # In a real implementation, this would call the API to delete
        logger.debug("Delete alert: %s", alert.get("id"))
        self._load_costs()


def get_tab(tab_id: str, api_client: ThegentAPIClient) -> QWidget | None:
    """Get the tab widget for the given tab_id.

    Args:
        tab_id: The tab ID to retrieve.
        api_client: Thegent API client.

    Returns:
        The widget for the tab, or None if not found.
    """
    if tab_id == "thegent-costs":
        return CostsTab(api_client=api_client)
    return None
