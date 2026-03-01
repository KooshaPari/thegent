"""Shared UI components for tray application."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGridLayout, QGroupBox, QLabel

# CSS string for metric cards
CARD_STYLE = """
QGroupBox {
    border: 1px solid #3c3c3c;
    border-radius: 8px;
    margin-top: 8px;
    padding: 8px;
    background-color: #2d2d2d;
}
QGroupBox::title {
    color: #a0a0a0;
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 8px;
}
"""


def metric_card(title: str, value: str, unit: str) -> QGroupBox:
    """Create a metric card widget.

    Args:
        title: The label for the metric
        value: The numeric value to display
        unit: The unit of measurement

    Returns:
        A QGroupBox containing the metric display
    """
    group = QGroupBox(title)
    layout = QGridLayout()

    value_label = QLabel(value)
    value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")

    unit_label = QLabel(unit)
    unit_label.setStyleSheet("font-size: 14px; color: #a0a0a0;")

    layout.addWidget(value_label, 0, 0)
    layout.addWidget(unit_label, 0, 1)
    layout.setColumnStretch(0, 1)
    layout.setColumnStretch(1, 0)

    group.setLayout(layout)
    group.setStyleSheet(CARD_STYLE)

    return group


def create_status_badge(status: str) -> QLabel:
    """Create a status badge widget.

    Args:
        status: The status type - "success", "warning", "error", or other

    Returns:
        A QLabel with appropriate styling
    """
    badge = QLabel(status.capitalize())
    badge.setAlignment(Qt.AlignmentFlag.AlignCenter)  # type: ignore[reportAttributeAccessIssue]

    # Define colors for each status
    colors = {
        "success": QColor("#22c55e"),  # Green
        "warning": QColor("#eab308"),  # Yellow
        "error": QColor("#ef4444"),    # Red
    }

    bg_color = colors.get(status.lower(), QColor("#6b7280"))  # Gray for unknown

    style = f"""
        QLabel {{
            background-color: {bg_color.name()};
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }}
    """
    badge.setStyleSheet(style)

    return badge
