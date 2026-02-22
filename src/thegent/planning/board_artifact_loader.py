"""Board artifact loader for CLIProxyAPI++ execution board integration into thegent workstream.

Loads board artifacts (markdown, CSV, JSON formats) and maps execution slices
into thegent unified workstream loop. Enables bidirectional sync between CLIProxyAPI++
board and thegent WORK_STREAM.md.
"""

import csv
import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)


@dataclass
class BoardItem:
    """Represents a single board item with CLIProxyAPI++ → thegent mapping."""

    board_id: str
    item_title: str
    status: str
    priority: str
    lead_agent: str
    mapped_wl: str  # thegent WL ID (e.g., "WL-158")
    slice_id: str
    effort_estimate: str
    completion_pct: int


@dataclass
class ExecutionSlice:
    """Represents an execution slice with thegent workstream mapping."""

    slice_id: str
    name: str
    item_count: int
    completion_pct: int
    lead_agent: str
    mapped_wl_range: str  # e.g., "WL-001..WL-015"


class BoardArtifactLoader:
    """Load and parse CLIProxyAPI++ board artifacts for workstream integration."""

    def __init__(self, board_dir: Path) -> None:
        self.board_dir = Path(board_dir)
        self.items: list[BoardItem] = []
        self.slices: list[ExecutionSlice] = []
        self.metadata: dict[str, Any] = {}

    def load_all(self) -> dict[str, Any]:
        """Load all available board artifacts (MD, CSV, JSON)."""
        result = {"success": True, "loaded": [], "errors": []}

        # Try JSON first (has both items and slices)
        json_file = self._find_file("*.json")
        if json_file:
            try:
                self._load_json(json_file)
                result["loaded"].append(str(json_file))
            except Exception as e:
                result["errors"].append(f"JSON load error: {e}")
                result["success"] = False

        # Load CSV (contains board items)
        csv_file = self._find_file("*BOARD*2026*.csv")
        if csv_file:
            try:
                self._load_csv(csv_file)
                result["loaded"].append(str(csv_file))
            except Exception as e:
                result["errors"].append(f"CSV load error: {e}")
                result["success"] = False

        # Load markdown for reference (metadata only, not parsed)
        md_file = self._find_file("*BOARD*2026*.md")
        if md_file:
            result["loaded"].append(str(md_file))

        return result

    def _find_file(self, pattern: str) -> Path | None:
        """Find first file matching pattern in board_dir."""
        matches = list(self.board_dir.glob(pattern))
        return matches[0] if matches else None

    def _load_json(self, json_file: Path) -> None:
        """Load JSON board artifact with metadata and execution slices."""
        with open(json_file) as f:
            data = json.load(f)

        self.metadata = data.get("board_metadata", {})

        # Parse slices from JSON
        for slice_data in data.get("execution_slices", []):
            self.slices.append(
                ExecutionSlice(
                    slice_id=slice_data["slice_id"],
                    name=slice_data["name"],
                    item_count=slice_data["item_count"],
                    completion_pct=slice_data["completion_pct"],
                    lead_agent=slice_data["lead_agent"],
                    mapped_wl_range=slice_data["mapped_wl_range"],
                )
            )

        _log.info(f"Loaded {len(self.slices)} execution slices from JSON")

    def _load_csv(self, csv_file: Path) -> None:
        """Load CSV board artifact containing board items."""
        with open(csv_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                item = BoardItem(
                    board_id=row["board_id"],
                    item_title=row["item_title"],
                    status=row["status"],
                    priority=row["priority"],
                    lead_agent=row["lead_agent"],
                    mapped_wl=row["mapped_wl"],
                    slice_id=row["slice"],
                    effort_estimate=row["effort_estimate"],
                    completion_pct=int(row["completion_pct"]),
                )
                self.items.append(item)

        _log.info(f"Loaded {len(self.items)} board items from CSV")

    def map_to_workstream(self) -> dict[str, Any]:
        """Map loaded board items to thegent WORK_STREAM.md reference entries.

        Returns:
            Dictionary mapping WL IDs to board items and metadata.
        """
        wl_map: dict[str, dict[str, Any]] = {}

        for item in self.items:
            wl_id = item.mapped_wl
            if wl_id not in wl_map:
                wl_map[wl_id] = {
                    "wl_id": wl_id,
                    "board_items": [],
                    "slice": None,
                    "lead_agent": item.lead_agent,
                    "completion_pct": 0,
                }

            wl_map[wl_id]["board_items"].append(
                {
                    "board_id": item.board_id,
                    "title": item.item_title,
                    "status": item.status,
                    "priority": item.priority,
                    "completion_pct": item.completion_pct,
                }
            )

            # Find and attach slice info
            for slice_obj in self.slices:
                if slice_obj.slice_id == item.slice_id:
                    wl_map[wl_id]["slice"] = {
                        "slice_id": slice_obj.slice_id,
                        "name": slice_obj.name,
                        "lead_agent": slice_obj.lead_agent,
                    }
                    break

            # Update completion percentage (take max from items)
            wl_map[wl_id]["completion_pct"] = max(
                wl_map[wl_id]["completion_pct"],
                item.completion_pct,
            )

        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "board_metadata": self.metadata,
            "wl_map": wl_map,
            "summary": {
                "total_items": len(self.items),
                "total_slices": len(self.slices),
                "wl_ids_covered": len(wl_map),
            },
        }

    def get_completion_status(self) -> dict[str, Any]:
        """Get aggregated completion status for all slices."""
        slice_status = {}

        for slice_obj in self.slices:
            slice_status[slice_obj.slice_id] = {
                "name": slice_obj.name,
                "completion_pct": slice_obj.completion_pct,
                "lead_agent": slice_obj.lead_agent,
                "item_count": slice_obj.item_count,
                "wl_range": slice_obj.mapped_wl_range,
            }

        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "slices": slice_status,
            "overall_completion_pct": (
                sum(s["completion_pct"] for s in slice_status.values()) // len(slice_status)
                if slice_status
                else 0
            ),
        }
