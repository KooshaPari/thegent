"""Agents tab widget for thegent tray plugin."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
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

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget as QtQWidget

    from thegent_platform.tray.plugins.thegent.api_client import ThegentAPIClient

logger = logging.getLogger(__name__)


# Supported models
MODELS = [
    "claude-opus-4-6",
    "claude-opus-4-5",
    "claude-opus-4-4",
    "claude-opus-4-3",
    "claude-opus-4-2",
    "claude-opus-4-1",
    "claude-opus-4-0",
    "claude-sonnet-4-6",
    "claude-sonnet-4-5",
    "claude-sonnet-4-4",
    "claude-sonnet-4-3",
    "claude-sonnet-4-2",
    "claude-sonnet-4-1",
    "claude-sonnet-4-0",
    "claude-haiku-3-5",
    "claude-haiku-3-0",
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo",
]

# Bounded context options
BOUNDED_CONTEXTS = [
    "code",
    "qa",
    "docs",
    "research",
    "planning",
    "governance",
    "infrastructure",
    "safety",
]


class AgentEditDialog(QDialog):
    """Dialog for editing/creating an agent."""

    def __init__(
        self, parent: QtQWidget | None = None, agent_data: dict[str, Any] | None = None
    ) -> None:
        """Initialize the agent edit dialog.

        Args:
            parent: Parent widget.
            agent_data: Existing agent data for editing.
        """
        super().__init__(parent)
        self.setWindowTitle("Edit Agent" if agent_data else "New Agent")
        self.setMinimumWidth(500)
        self._agent_data = agent_data or {}

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        layout = QVBoxLayout(self)

        # Form layout for agent fields
        form_layout = QFormLayout()

        # Agent name
        self._name_input = QLineEdit(self._agent_data.get("name", ""))
        self._name_input.setPlaceholderText("Agent name")
        form_layout.addRow("Name:", self._name_input)

        # Model combo
        self._model_combo = QComboBox()
        self._model_combo.addItems(MODELS)
        if self._agent_data.get("model"):
            index = self._model_combo.findText(self._agent_data["model"])
            if index >= 0:
                self._model_combo.setCurrentIndex(index)
        form_layout.addRow("Model:", self._model_combo)

        # Context limit spinbox
        self._context_spin = QSpinBox()
        self._context_spin.setRange(1000, 1000000)
        self._context_spin.setSuffix(" tokens")
        self._context_spin.setValue(self._agent_data.get("context_limit", 200000))
        form_layout.addRow("Context Limit:", self._context_spin)

        # Input rate spinbox
        self._input_rate_spin = QSpinBox()
        self._input_rate_spin.setRange(0, 10000)
        self._input_rate_spin.setPrefix("$ ")
        self._input_rate_spin.setSuffix(" /M tokens")
        self._input_rate_spin.setValue(int(self._agent_data.get("rate_input", 15.0)))
        form_layout.addRow("Input Rate:", self._input_rate_spin)

        # Output rate spinbox
        self._output_rate_spin = QSpinBox()
        self._output_rate_spin.setRange(0, 10000)
        self._output_rate_spin.setPrefix("$ ")
        self._output_rate_spin.setSuffix(" /M tokens")
        self._output_rate_spin.setValue(int(self._agent_data.get("rate_output", 75.0)))
        form_layout.addRow("Output Rate:", self._output_rate_spin)

        layout.addLayout(form_layout)

        # Bounded contexts group
        contexts_group = QGroupBox("Bounded Contexts")
        contexts_layout = QHBoxLayout()

        self._context_checkboxes: dict[str, QCheckBox] = {}
        selected_contexts = self._agent_data.get("bounded_contexts", [])

        for context in BOUNDED_CONTEXTS:
            checkbox = QCheckBox(context.capitalize())
            checkbox.setChecked(context in selected_contexts)
            self._context_checkboxes[context] = checkbox
            contexts_layout.addWidget(checkbox)

        contexts_group.setLayout(contexts_layout)
        layout.addWidget(contexts_group)

        # Auto-spawn settings group
        spawn_group = QGroupBox("Auto-Spawn Settings")
        spawn_layout = QFormLayout()

        # Auto-spawn checkbox
        self._auto_spawn_check = QCheckBox("Enable auto-spawn")
        self._auto_spawn_check.setChecked(self._agent_data.get("auto_spawn", False))
        spawn_layout.addRow("Auto-Spawn:", self._auto_spawn_check)

        # Max concurrent spinbox
        self._max_concurrent_spin = QSpinBox()
        self._max_concurrent_spin.setRange(1, 100)
        self._max_concurrent_spin.setValue(self._agent_data.get("max_concurrent", 5))
        spawn_layout.addRow("Max Concurrent:", self._max_concurrent_spin)

        spawn_group.setLayout(spawn_layout)
        layout.addWidget(spawn_group)

        # Dialog buttons
        self._buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Save
        )
        self._buttons.rejected.connect(self.reject)
        self._buttons.accepted.connect(self.accept)
        layout.addWidget(self._buttons)

    def get_data(self) -> dict[str, Any]:
        """Get the agent data from the dialog.

        Returns:
            Dictionary containing agent settings.
        """
        # Collect selected bounded contexts
        selected_contexts = [
            context
            for context, checkbox in self._context_checkboxes.items()
            if checkbox.isChecked()
        ]

        return {
            # Agent fields
            "name": self._name_input.text(),
            "model": self._model_combo.currentText(),
            "context_limit": self._context_spin.value(),
            "rate_input": self._input_rate_spin.value(),
            "rate_output": self._output_rate_spin.value(),
            "bounded_contexts": selected_contexts,
            # Auto-spawn settings
            "auto_spawn": self._auto_spawn_check.isChecked(),
            "max_concurrent": self._max_concurrent_spin.value(),
        }


class AgentsTab(QWidget):
    """Agents tab widget displaying list of agents."""

    # Tab ID for the plugin system
    TAB_ID = "thegent-agents"

    def __init__(self, api_client: ThegentAPIClient) -> None:
        """Initialize the agents tab.

        Args:
            api_client: Thegent API client.
        """
        super().__init__()
        self._api_client = api_client
        self._agents: list[dict[str, Any]] = []

        self._setup_ui()
        self._load_agents()

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header with buttons
        header_layout = QHBoxLayout()

        # Title
        title_label = QLabel("Agents")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # New agent button
        self._new_button = QPushButton("+ New Agent")
        self._new_button.clicked.connect(self._on_new_agent)
        header_layout.addWidget(self._new_button)

        layout.addLayout(header_layout)

        # Agents table
        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["Name", "Model", "Context", "Status", "Actions"])
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self._table)

        # Auto-refresh timer (30 seconds)
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._load_agents)
        self._refresh_timer.start(30000)  # 30 seconds

    def _load_agents(self) -> None:
        """Load agents from the API."""
        try:
            self._agents = []
            # Get agents from API
            api_agents = self._api_client.get_agents()
            for agent in api_agents:
                self._agents.append({
                    "id": agent.id,
                    "name": agent.name,
                    "model": agent.model,
                    "context_limit": agent.context_limit,
                    "rate_input": agent.rate_input,
                    "rate_output": agent.rate_output,
                    "status": agent.status,
                    "bounded_contexts": agent.bounded_contexts,
                })
            self._update_table()
        except Exception as e:
            # Handle error - could show a message or log
            logger.warning("Failed to load agents: %s", e)

    def _update_table(self) -> None:
        """Update the table with current agents."""
        self._table.setRowCount(0)

        for agent in self._agents:
            row = self._table.rowCount()
            self._table.insertRow(row)

            # Name
            name_item = QTableWidgetItem(agent["name"])
            name_item.setData(Qt.ItemDataRole.UserRole, agent["id"])
            self._table.setItem(row, 0, name_item)

            # Model
            model_item = QTableWidgetItem(agent.get("model", ""))
            self._table.setItem(row, 1, model_item)

            # Context
            context_limit = agent.get("context_limit", 0)
            context_item = QTableWidgetItem(f"{context_limit:,}")
            self._table.setItem(row, 2, context_item)

            # Status
            status = agent.get("status", "unknown")
            status_item = QTableWidgetItem(status)
            self._table.setItem(row, 3, status_item)

            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)

            # Edit button
            edit_btn = QPushButton("Edit")
            edit_btn.setFixedSize(50, 24)
            edit_btn.clicked.connect(lambda checked, a=agent: self._on_edit_agent(a))
            actions_layout.addWidget(edit_btn)

            # Enable/Disable toggle button
            status = agent.get("status", "unknown")
            if status == "enabled":
                toggle_btn = QPushButton("Disable")
                toggle_btn.setFixedSize(60, 24)
            else:
                toggle_btn = QPushButton("Enable")
                toggle_btn.setFixedSize(60, 24)
            toggle_btn.clicked.connect(lambda checked, a=agent: self._on_toggle_agent(a))
            actions_layout.addWidget(toggle_btn)

            self._table.setCellWidget(row, 4, actions_widget)

    def _on_new_agent(self) -> None:
        """Handle new agent button clicked."""
        dialog = AgentEditDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                # Note: Would call api_client.create_agent(**data) when available
                logger.debug("Creating agent: %s", data)
                self._load_agents()
            except Exception as e:
                logger.warning("Failed to create agent: %s", e)

    def _on_edit_agent(self, agent: dict[str, Any]) -> None:
        """Handle edit agent button clicked."""
        dialog = AgentEditDialog(parent=self, agent_data=agent)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self._api_client.update_agent(agent["id"], **data)
                self._load_agents()
            except Exception as e:
                logger.warning("Failed to update agent: %s", e)

    def _on_toggle_agent(self, agent: dict[str, Any]) -> None:
        """Handle enable/disable agent button clicked."""
        current_status = agent.get("status", "unknown")
        new_status = "disabled" if current_status == "enabled" else "enabled"
        try:
            self._api_client.update_agent(agent["id"], status=new_status)
            self._load_agents()
        except Exception as e:
            logger.warning("Failed to toggle agent: %s", e)


def get_tab(tab_id: str, api_client: ThegentAPIClient) -> QWidget | None:
    """Get the tab widget for the given tab_id.

    Args:
        tab_id: The tab ID to retrieve.
        api_client: Thegent API client.

    Returns:
        The widget for the tab, or None if not found.
    """
    if tab_id == "thegent-agents":
        return AgentsTab(api_client=api_client)
    return None
