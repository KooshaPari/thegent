"""Layout manager for TUI compositor.

Provides multi-pane layout management with save/restore functionality.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PaneConfig:
    """Configuration for a single pane."""

    pane_id: str
    pane_type: str  # "output", "terminal", "status", "custom"
    weight: int = 1
    custom_config: dict[str, Any] | None = None


@dataclass
class SplitConfig:
    """Configuration for a split pane."""

    orientation: str  # "horizontal", "vertical"
    panes: list[PaneConfig | SplitConfig]
    weights: list[int] | None = None


@dataclass
class LayoutState:
    """Complete layout state."""

    name: str
    root: SplitConfig | PaneConfig
    sidebar_visible: bool = True
    sidebar_width: int = 30
    output_maximized: bool = False
    created_at: str = ""
    updated_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class LayoutManager:
    """Manages layout persistence and switching."""

    def __init__(self, storage_dir: Path | None = None) -> None:
        self._layouts: dict[str, LayoutState] = {}
        self._current: str | None = None
        self._storage_dir = storage_dir or Path.home() / ".config" / "thegent" / "layouts"
        self._load_all()

    def _load_all(self) -> None:
        """Load all saved layouts from disk."""
        if not self._storage_dir.exists():
            return

        for layout_file in self._storage_dir.glob("*.json"):
            try:
                data = json.loads(layout_file.read_text())
                state = LayoutState(
                    name=data.get("name", layout_file.stem),
                    root=data.get("root", {"pane_type": "output"}),
                    sidebar_visible=data.get("sidebar_visible", True),
                    sidebar_width=data.get("sidebar_width", 30),
                    output_maximized=data.get("output_maximized", False),
                    created_at=data.get("created_at", ""),
                    updated_at=data.get("updated_at", ""),
                    metadata=data.get("metadata", {}),
                )
                self._layouts[state.name] = state
            except Exception:  # noqa: PERF203 - intentional per-item error handling
                pass

    def _save(self, state: LayoutState) -> None:
        """Save a layout to disk."""
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "name": state.name,
            "root": self._serialize_config(state.root),
            "sidebar_visible": state.sidebar_visible,
            "sidebar_width": state.sidebar_width,
            "output_maximized": state.output_maximized,
            "created_at": state.created_at,
            "updated_at": state.updated_at,
            "metadata": state.metadata,
        }
        (self._storage_dir / f"{state.name}.json").write_text(json.dumps(data, indent=2))

    def _serialize_config(self, config: SplitConfig | PaneConfig) -> dict:
        """Serialize a config to dict."""
        if isinstance(config, PaneConfig):
            result = {
                "pane_id": config.pane_id,
                "pane_type": config.pane_type,
                "weight": config.weight,
            }
            if config.custom_config:
                result["custom_config"] = config.custom_config
            return result
        return {
            "orientation": config.orientation,
            "panes": [self._serialize_config(p) for p in config.panes],
            "weights": config.weights,
        }

    def create_layout(
        self,
        name: str,
        root: SplitConfig | PaneConfig,
        *,
        sidebar_visible: bool = True,
        sidebar_width: int = 30,
        output_maximized: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> LayoutState:
        """Create a new layout."""
        from datetime import datetime

        now = datetime.now().isoformat()
        state = LayoutState(
            name=name,
            root=root,
            sidebar_visible=sidebar_visible,
            sidebar_width=sidebar_width,
            output_maximized=output_maximized,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
        )
        self._layouts[name] = state
        self._save(state)
        return state

    def get_layout(self, name: str) -> LayoutState | None:
        """Get a layout by name."""
        return self._layouts.get(name)

    def delete_layout(self, name: str) -> bool:
        """Delete a layout."""
        if name in self._layouts:
            del self._layouts[name]
            layout_file = self._storage_dir / f"{name}.json"
            if layout_file.exists():
                layout_file.unlink()
            return True
        return False

    def rename_layout(self, old_name: str, new_name: str) -> bool:
        """Rename a layout."""
        if old_name in self._layouts:
            state = self._layouts.pop(old_name)
            state.name = new_name
            self._layouts[new_name] = state

            # Rename file
            old_file = self._storage_dir / f"{old_name}.json"
            new_file = self._storage_dir / f"{new_name}.json"
            if old_file.exists():
                old_file.rename(new_file)
            return True
        return False

    def list_layouts(self) -> list[str]:
        """List all saved layouts."""
        return list(self._layouts.keys())

    def switch_layout(self, name: str) -> LayoutState | None:
        """Switch to a layout (returns the state for application)."""
        if name in self._layouts:
            self._current = name
            return self._layouts[name]
        return None

    def get_current(self) -> LayoutState | None:
        """Get the current active layout."""
        if self._current:
            return self._layouts.get(self._current)
        return None

    def duplicate_layout(self, source_name: str, new_name: str) -> LayoutState | None:
        """Duplicate an existing layout."""
        source = self._layouts.get(source_name)
        if source:
            return self.create_layout(
                new_name,
                source.root,
                sidebar_visible=source.sidebar_visible,
                sidebar_width=source.sidebar_width,
                output_maximized=source.output_maximized,
                metadata={"duplicated_from": source_name},
            )
        return None


# Factory functions for common layouts
def create_horizontal_split(
    left_pane: PaneConfig,
    right_pane: PaneConfig,
    left_weight: int = 1,
    right_weight: int = 1,
) -> SplitConfig:
    """Create a horizontal split layout."""
    return SplitConfig(
        orientation="horizontal",
        panes=[left_pane, right_pane],
        weights=[left_weight, right_weight],
    )


def create_vertical_split(
    top_pane: PaneConfig,
    bottom_pane: PaneConfig,
    top_weight: int = 1,
    bottom_weight: int = 1,
) -> SplitConfig:
    """Create a vertical split layout."""
    return SplitConfig(
        orientation="vertical",
        panes=[top_pane, bottom_pane],
        weights=[top_weight, bottom_weight],
    )


def create_three_column(
    left: PaneConfig,
    center: PaneConfig,
    right: PaneConfig,
    weights: list[int] | None = None,
) -> SplitConfig:
    """Create a three-column layout."""
    return SplitConfig(
        orientation="horizontal",
        panes=[left, center, right],
        weights=weights or [1, 2, 1],
    )


def create_main_sidebar(
    main_pane: PaneConfig,
    sidebar_pane: PaneConfig,
    sidebar_width: int = 30,
) -> SplitConfig:
    """Create a main content + sidebar layout."""
    return SplitConfig(
        orientation="horizontal",
        panes=[main_pane, sidebar_pane],
        weights=[100 - sidebar_width, sidebar_width],
    )


# Predefined layouts
def create_default_layout() -> LayoutState:
    """Create the default layout."""
    main_pane = PaneConfig(pane_id="output", pane_type="output", weight=70)
    sidebar_pane = PaneConfig(pane_id="sidebar", pane_type="status", weight=30)
    root = create_main_sidebar(main_pane, sidebar_pane, sidebar_width=30)

    manager = LayoutManager()
    return manager.create_layout(
        name="default",
        root=root,
        sidebar_visible=True,
        sidebar_width=30,
        output_maximized=False,
        metadata={"description": "Default two-pane layout"},
    )


def create_full_output_layout() -> LayoutState:
    """Create a full-screen output layout."""
    main_pane = PaneConfig(pane_id="output", pane_type="output", weight=100)

    manager = LayoutManager()
    return manager.create_layout(
        name="full-output",
        root=main_pane,
        sidebar_visible=False,
        sidebar_width=0,
        output_maximized=True,
        metadata={"description": "Full-screen output"},
    )


def create_terminal_layout() -> LayoutState:
    """Create a layout optimized for terminal use."""
    terminal_pane = PaneConfig(pane_id="terminal", pane_type="terminal", weight=70)
    output_pane = PaneConfig(pane_id="output", pane_type="output", weight=30)
    root = create_horizontal_split(terminal_pane, output_pane, 70, 30)

    manager = LayoutManager()
    return manager.create_layout(
        name="terminal",
        root=root,
        sidebar_visible=False,
        sidebar_width=0,
        output_maximized=False,
        metadata={"description": "Terminal-focused layout"},
    )
