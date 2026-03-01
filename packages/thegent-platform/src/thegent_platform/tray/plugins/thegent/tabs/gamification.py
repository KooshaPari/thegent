"""Gamification tab widget for thegent tray plugin."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from thegent_platform.tray.plugins.thegent.api_client import ThegentAPIClient

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget as QtQWidget

logger = logging.getLogger(__name__)


class AchievementsDialog(QDialog):
    """Dialog for displaying all achievements with filtering."""

    def __init__(
        self, parent: QtQWidget | None = None, achievements: list[dict[str, Any]] | None = None
    ) -> None:
        """Initialize the achievements dialog.

        Args:
            parent: Parent widget.
            achievements: List of achievement data.
        """
        super().__init__(parent)
        self.setWindowTitle("Achievements")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self._achievements = achievements or []
        self._all_achievements = self._achievements.copy()

        self._setup_ui()
        self._populate_list()

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("All Achievements")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Filter combo
        self._filter_combo = QComboBox()
        self._filter_combo.addItems(["All", "Earned", "Locked"])
        self._filter_combo.currentTextChanged.connect(self._on_filter_changed)
        header_layout.addWidget(QLabel("Filter:"))
        header_layout.addWidget(self._filter_combo)

        layout.addLayout(header_layout)

        # Achievements list
        self._achievements_list = QListWidget()
        self._achievements_list.setFrameShape(QFrame.Shape.NoFrame)
        layout.addWidget(self._achievements_list)

        # Close button
        self._close_button = QPushButton("Close")
        self._close_button.clicked.connect(self.accept)
        layout.addWidget(self._close_button)

    def _populate_list(self, filter_type: str = "All") -> None:
        """Populate the achievements list.

        Args:
            filter_type: Filter type - "All", "Earned", or "Locked".
        """
        self._achievements_list.clear()

        for achievement in self._all_achievements:
            # Apply filter
            if filter_type == "Earned" and not achievement.get("earned", False):
                continue
            if filter_type == "Locked" and achievement.get("earned", False):
                continue

            # Create item widget
            item = QListWidgetItem()
            item_widget = self._create_achievement_item(achievement)
            item.setSizeHint(item_widget.sizeHint())
            self._achievements_list.addItem(item)
            self._achievements_list.setItemWidget(item, item_widget)

    def _create_achievement_item(self, achievement: dict[str, Any]) -> QWidget:
        """Create a widget for an achievement.

        Args:
            achievement: Achievement data.

        Returns:
            Widget for the achievement.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # Header row
        header_layout = QHBoxLayout()

        # Name
        name = achievement.get("name", "Unknown")
        name_label = QLabel(name)
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(name_label)

        header_layout.addStretch()

        # XP reward
        xp = achievement.get("xp_reward", 0)
        xp_label = QLabel(f"+{xp} XP")
        xp_label.setStyleSheet("color: gold; font-weight: bold;")
        header_layout.addWidget(xp_label)

        layout.addLayout(header_layout)

        # Description
        description = achievement.get("description", "")
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #888;")
        layout.addWidget(desc_label)

        # Status and date
        status_layout = QHBoxLayout()

        if achievement.get("earned", False):
            status_label = QLabel("EARNED")
            status_label.setStyleSheet("color: green; font-weight: bold;")
            status_layout.addWidget(status_label)

            earned_at = achievement.get("earned_at")
            if earned_at:
                # Format the date
                date_label = QLabel(f"Earned: {earned_at[:10]}")
                status_layout.addWidget(date_label)
        else:
            status_label = QLabel("LOCKED")
            status_label.setStyleSheet("color: #666;")
            status_layout.addWidget(status_label)

        status_layout.addStretch()
        layout.addLayout(status_layout)

        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #ddd;")
        layout.addWidget(separator)

        return widget

    def _on_filter_changed(self, filter_type: str) -> None:
        """Handle filter changed.

        Args:
            filter_type: The new filter type.
        """
        self._populate_list(filter_type)


class GamificationTab(QWidget):
    """Gamification tab widget displaying XP, levels, and achievements."""

    # Tab ID for the plugin system
    TAB_ID = "thegent-gamification"

    def __init__(self, api_client: ThegentAPIClient) -> None:
        """Initialize the gamification tab.

        Args:
            api_client: Thegent API client.
        """
        super().__init__()
        self._api_client = api_client
        self._stats: dict[str, Any] | None = None
        self._achievements: list[dict[str, Any]] = []

        self._setup_ui()
        self._load_data()

    def _setup_ui(self) -> None:
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Title
        title = QLabel("Gamification")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Level progress section
        level_section = self._create_level_section()
        layout.addWidget(level_section)

        # Stats cards row
        stats_row = self._create_stats_row()
        layout.addWidget(stats_row)

        # Recent achievements section
        recent_section = self._create_recent_section()
        layout.addWidget(recent_section)

        # Leaderboard section (optional, with mock data)
        leaderboard_section = self._create_leaderboard_section()
        layout.addWidget(leaderboard_section)

        layout.addStretch()

        # Auto-refresh timer (30 seconds)
        self._refresh_timer = QTimer(self)
        self._refresh_timer.timeout.connect(self._load_data)
        self._refresh_timer.start(30000)  # 30 seconds

    def _create_level_section(self) -> QWidget:
        """Create the level progress section.

        Returns:
            The level section widget.
        """
        section = QFrame()
        section.setFrameShape(QFrame.Shape.StyledPanel)
        section.setStyleSheet("background-color: #2a2a3e; border-radius: 8px; padding: 10px;")
        layout = QVBoxLayout(section)

        # Level header
        level_header = QHBoxLayout()

        self._level_label = QLabel("Level 1")
        self._level_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffd700;")
        level_header.addWidget(self._level_label)

        level_header.addStretch()

        # XP info
        self._xp_info_label = QLabel("0 / 1000 XP")
        self._xp_info_label.setStyleSheet("font-size: 14px; color: #aaa;")
        level_header.addWidget(self._xp_info_label)

        layout.addLayout(level_header)

        # Progress bar
        self._xp_progress = QProgressBar()
        self._xp_progress.setRange(0, 100)
        self._xp_progress.setValue(0)
        self._xp_progress.setTextVisible(True)
        self._xp_progress.setFormat("%p%")
        self._xp_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #444;
                border-radius: 4px;
                text-align: center;
                background-color: #1a1a2e;
                color: #fff;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ffd700, stop:1 #ff8c00);
                border-radius: 3px;
            }
        """)
        layout.addWidget(self._xp_progress)

        return section

    def _create_stats_row(self) -> QWidget:
        """Create the stats cards row.

        Returns:
            The stats row widget.
        """
        row = QHBoxLayout()
        row.setSpacing(15)

        # Total XP card
        self._total_xp_card = self._create_stat_card("Total XP", "0", "#4a90d9")
        row.addWidget(self._total_xp_card)

        # Runs Today card
        self._runs_today_card = self._create_stat_card("Runs Today", "0", "#5cb85c")
        row.addWidget(self._runs_today_card)

        # Achievements card
        self._achievements_card = self._create_stat_card("Achievements", "0", "#f0ad4e")
        row.addWidget(self._achievements_card)

        # Streak card
        self._streak_card = self._create_stat_card("Streak", "0 days", "#d9534f")
        row.addWidget(self._streak_card)

        widget = QWidget()
        widget.setLayout(row)
        return widget

    def _create_stat_card(self, title: str, value: str, color: str) -> QWidget:
        """Create a stat card widget.

        Args:
            title: Card title.
            value: Card value.
            color: Accent color.

        Returns:
            The stat card widget.
        """
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setStyleSheet(f"""
            background-color: #2a2a3e;
            border-radius: 8px;
            border-left: 3px solid {color};
            padding: 10px;
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(title_label)

        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
        layout.addWidget(value_label)

        # Store reference for updating
        if title == "Total XP":
            self._total_xp_label = value_label
        elif title == "Runs Today":
            self._runs_today_label = value_label
        elif title == "Achievements":
            self._achievements_count_label = value_label
        elif title == "Streak":
            self._streak_label = value_label

        return card

    def _create_recent_section(self) -> QWidget:
        """Create the recent achievements section.

        Returns:
            The recent achievements section widget.
        """
        section = QFrame()
        section.setFrameShape(QFrame.Shape.StyledPanel)
        section.setStyleSheet("background-color: #2a2a3e; border-radius: 8px; padding: 10px;")
        layout = QVBoxLayout(section)

        # Header
        header = QHBoxLayout()

        title = QLabel("Recent Achievements")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        header.addWidget(title)

        header.addStretch()

        # View All button
        self._view_all_button = QPushButton("+ View All")
        self._view_all_button.setStyleSheet("""
            QPushButton {
                background-color: #4a90d9;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a9fe9;
            }
        """)
        self._view_all_button.clicked.connect(self._on_view_all)
        header.addWidget(self._view_all_button)

        layout.addLayout(header)

        # Recent achievements list
        self._recent_achievements_list = QListWidget()
        self._recent_achievements_list.setFrameShape(QFrame.Shape.NoFrame)
        self._recent_achievements_list.setMaximumHeight(150)
        layout.addWidget(self._recent_achievements_list)

        return section

    def _create_leaderboard_section(self) -> QWidget:
        """Create the leaderboard section (with mock data).

        Returns:
            The leaderboard section widget.
        """
        section = QFrame()
        section.setFrameShape(QFrame.Shape.StyledPanel)
        section.setStyleSheet("background-color: #2a2a3e; border-radius: 8px; padding: 10px;")
        layout = QVBoxLayout(section)

        # Title
        title = QLabel("Leaderboard (Mock)")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # Note label
        note = QLabel("Leaderboard feature coming soon!")
        note.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(note)

        # Mock leaderboard entries
        leaderboard = QListWidget()
        leaderboard.setFrameShape(QFrame.Shape.NoFrame)

        mock_leaders = [
            ("You", "Level 5", "1500 XP"),
            ("DevBot", "Level 8", "3200 XP"),
            ("CodeMaster", "Level 7", "2800 XP"),
        ]

        for name, level, xp in mock_leaders:
            item = QListWidgetItem(f"{name} - {level} - {xp}")
            leaderboard.addItem(item)

        layout.addWidget(leaderboard)

        return section

    def _load_data(self) -> None:
        """Load gamification data from the API."""
        try:
            # Get stats
            stats = self._api_client.get_gamification_stats()
            self._stats = {
                "total_xp": stats.total_xp,
                "level": stats.level,
                "xp_to_next_level": stats.xp_to_next_level,
                "runs_today": stats.runs_today,
                "achievements_count": stats.achievements_count,
                "streak_days": stats.streak_days,
            }

            # Get achievements
            self._achievements = self._api_client.get_achievements()

            # Update UI
            self._update_ui()
        except Exception as e:
            logger.warning("Failed to load gamification data: %s", e)
            # Set default values on error
            self._stats = {
                "total_xp": 0,
                "level": 1,
                "xp_to_next_level": 1000,
                "runs_today": 0,
                "achievements_count": 0,
                "streak_days": 0,
            }
            self._achievements = []
            self._update_ui()

    def _update_ui(self) -> None:
        """Update the UI with current data."""
        if not self._stats:
            return

        # Update level
        level = self._stats.get("level", 1)
        self._level_label.setText(f"Level {level}")

        # Update XP progress
        total_xp = self._stats.get("total_xp", 0)
        xp_to_next = self._stats.get("xp_to_next_level", 1000)
        xp_for_current_level = total_xp - xp_to_next
        xp_needed = xp_to_next + xp_for_current_level

        if xp_needed > 0:
            progress = int((xp_for_current_level / xp_needed) * 100)
        else:
            progress = 0

        self._xp_progress.setValue(progress)
        self._xp_info_label.setText(f"{total_xp} / {xp_needed} XP")

        # Update stat cards
        self._total_xp_label.setText(str(total_xp))
        self._runs_today_label.setText(str(self._stats.get("runs_today", 0)))
        self._achievements_count_label.setText(str(self._stats.get("achievements_count", 0)))
        self._streak_label.setText(f"{self._stats.get('streak_days', 0)} days")

        # Update recent achievements
        self._update_recent_achievements()

    def _update_recent_achievements(self) -> None:
        """Update the recent achievements list."""
        self._recent_achievements_list.clear()

        # Sort achievements by earned date (most recent first)
        earned_achievements = [
            a for a in self._achievements if a.get("earned", False)
        ]
        earned_achievements.sort(
            key=lambda a: a.get("earned_at", ""),
            reverse=True
        )

        # Show up to 3 recent
        for achievement in earned_achievements[:3]:
            item = QListWidgetItem()
            item_widget = self._create_recent_achievement_item(achievement)
            item.setSizeHint(item_widget.sizeHint())
            self._recent_achievements_list.addItem(item)
            self._recent_achievements_list.setItemWidget(item, item_widget)

        if not earned_achievements:
            # Show placeholder
            placeholder = QLabel("No achievements yet. Start earning!")
            placeholder.setStyleSheet("color: #666; font-style: italic;")
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._recent_achievements_list.addItem(
                QListWidgetItem("No achievements yet. Start earning!")
            )

    def _create_recent_achievement_item(self, achievement: dict[str, Any]) -> QWidget:
        """Create a widget for a recent achievement.

        Args:
            achievement: Achievement data.

        Returns:
            The achievement item widget.
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # Achievement icon (checkmark)
        icon = QLabel("[check]")
        icon.setStyleSheet("color: #5cb85c; font-weight: bold;")
        layout.addWidget(icon)

        # Name
        name = achievement.get("name", "Unknown")
        name_label = QLabel(name)
        name_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(name_label)

        layout.addStretch()

        # XP
        xp = achievement.get("xp_reward", 0)
        xp_label = QLabel(f"+{xp} XP")
        xp_label.setStyleSheet("color: gold;")
        layout.addWidget(xp_label)

        return widget

    def _on_view_all(self) -> None:
        """Handle View All button clicked."""
        dialog = AchievementsDialog(parent=self, achievements=self._achievements)
        dialog.exec()


def get_tab(tab_id: str, api_client: ThegentAPIClient) -> QWidget | None:
    """Get the tab widget for the given tab_id.

    Args:
        tab_id: The tab ID to retrieve.
        api_client: Thegent API client.

    Returns:
        The widget for the tab, or None if not found.
    """
    if tab_id == "thegent-gamification":
        return GamificationTab(api_client=api_client)
    return None
