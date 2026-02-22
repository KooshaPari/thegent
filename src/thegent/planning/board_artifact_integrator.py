"""Board artifact integration for unified workstream.

Ingests CLIProxyAPI++ board artifacts (CSV, JSON, MD) and maps them
into thegent workstream items.

WL-158: Unified Workstream Integration for CLIProxyAPI++ Board Artifacts
"""

import csv
import json
import logging
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)


class BoardArtifactParser:
    """Parse board artifacts in multiple formats (CSV, JSON, Markdown)."""

    @staticmethod
    def parse_csv(file_path: Path) -> list[dict[str, Any]]:
        """Parse CSV board artifact.

        Expected columns: id, title, status, priority, source, effort, depends_on, evidence
        """
        items = []
        try:
            with open(file_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row:
                        items.append({
                            "id": row.get("id", "").strip(),
                            "title": row.get("title", "").strip(),
                            "status": row.get("status", "BACKLOG").upper(),
                            "priority": row.get("priority", "P2").upper(),
                            "source": row.get("source", "BOARD").upper(),
                            "effort": row.get("effort", "M").upper(),
                            "depends_on": row.get("depends_on", "").strip() or None,
                            "evidence": row.get("evidence", "").strip() or None,
                        })
        except Exception as e:
            _log.error(f"Failed to parse CSV {file_path}: {e}")
        return items

    @staticmethod
    def parse_json(file_path: Path) -> list[dict[str, Any]]:
        """Parse JSON board artifact.

        Expected structure: list of items or root with 'items' key.
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            # Handle both list and dict with items key
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict) and "items" in data:
                items = data["items"]
            else:
                _log.warning(f"Unexpected JSON structure in {file_path}")
                return []

            # Normalize items
            normalized = []
            for item in items:
                if isinstance(item, dict):
                    normalized.append({
                        "id": item.get("id", "").strip(),
                        "title": item.get("title", "").strip(),
                        "status": item.get("status", "BACKLOG").upper(),
                        "priority": item.get("priority", "P2").upper(),
                        "source": item.get("source", "BOARD").upper(),
                        "effort": item.get("effort", "M").upper(),
                        "depends_on": item.get("depends_on") or item.get("dependsOn") or None,
                        "evidence": item.get("evidence") or None,
                    })
            return normalized
        except Exception as e:
            _log.error(f"Failed to parse JSON {file_path}: {e}")
            return []

    @staticmethod
    def parse_markdown(file_path: Path) -> list[dict[str, Any]]:
        """Parse Markdown board artifact.

        Expects table format:
        | ID | Title | Status | Priority | Source | Effort | Depends | Evidence |
        """
        items = []
        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            in_table = False
            for line in lines:
                if "|" not in line:
                    continue

                # Skip header separator
                if all(c in "|-: " for c in line):
                    in_table = True
                    continue

                if not in_table or not line.strip().startswith("|"):
                    continue

                # Parse table row
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) < 3:
                    continue

                # Extract row with proper column handling
                item_id = parts[0].strip("~").strip() if parts else ""
                if not item_id or item_id.startswith("ID"):
                    continue

                items.append({
                    "id": item_id,
                    "title": parts[1] if len(parts) > 1 else "",
                    "status": (parts[2] if len(parts) > 2 else "BACKLOG").upper(),
                    "priority": (parts[3] if len(parts) > 3 else "P2").upper(),
                    "source": (parts[4] if len(parts) > 4 else "BOARD").upper(),
                    "effort": (parts[5] if len(parts) > 5 else "M").upper(),
                    "depends_on": parts[6] if len(parts) > 6 else None,
                    "evidence": parts[7] if len(parts) > 7 else None,
                })
        except Exception as e:
            _log.error(f"Failed to parse Markdown {file_path}: {e}")
        return items


class BoardArtifactIntegrator:
    """Integrate board artifacts into unified workstream."""

    def __init__(self, board_artifacts_dir: Path | None = None) -> None:
        """Initialize integrator.

        Args:
            board_artifacts_dir: Directory containing board artifacts.
                                Defaults to cliproxyapi-plusplus/docs/planning/
        """
        if board_artifacts_dir is None:
            # Try common locations
            cwd = Path.cwd()
            possible_dirs = [
                cwd / "cliproxyapi-plusplus" / "docs" / "planning",
                cwd / "docs" / "planning" / "board-artifacts",
            ]
            for d in possible_dirs:
                if d.exists():
                    board_artifacts_dir = d
                    break

        self.board_artifacts_dir = board_artifacts_dir or Path()
        self.parser = BoardArtifactParser()

    def find_board_artifacts(self) -> dict[str, Path]:
        """Find all board artifact files in the artifacts directory.

        Returns:
            Dict mapping artifact type to file path
        """
        artifacts = {}
        if not self.board_artifacts_dir.exists():
            return artifacts

        # Look for standard board artifact patterns
        patterns = {
            "execution_board_md": "*_EXECUTION_BOARD_*.md",
            "execution_board_csv": "*_EXECUTION_BOARD_*.csv",
            "execution_board_json": "*_EXECUTION_BOARD_*.json",
            "github_import_csv": "*_IMPORT_*.csv",
        }

        for artifact_type, pattern in patterns.items():
            matching = list(self.board_artifacts_dir.glob(pattern))
            if matching:
                artifacts[artifact_type] = matching[0]

        return artifacts

    def ingest_artifacts(self) -> list[dict[str, Any]]:
        """Ingest all available board artifacts.

        Returns:
            List of normalized workstream items from board artifacts
        """
        artifacts = self.find_board_artifacts()
        if not artifacts:
            _log.debug(f"No board artifacts found in {self.board_artifacts_dir}")
            return []

        items = []

        # Ingest execution board (prefer JSON, fallback to CSV or MD)
        for key in ["execution_board_json", "execution_board_csv", "execution_board_md"]:
            if key in artifacts:
                path = artifacts[key]
                _log.info(f"Ingesting board artifact: {path}")

                if key.endswith("_json"):
                    items = self.parser.parse_json(path)
                elif key.endswith("_csv"):
                    items = self.parser.parse_csv(path)
                else:
                    items = self.parser.parse_markdown(path)

                if items:
                    break

        return items

    def to_workstream_format(self, items: list[dict[str, Any]]) -> str:
        """Convert board items to workstream markdown table format.

        Returns:
            Markdown table representation of items
        """
        if not items:
            return ""

        lines = [
            "| ID | Title | Source | Priority | Effort | Status | Depends |",
            "|----|----|--------|----------|--------|--------|---------|",
        ]

        for item in items:
            item_id = item.get("id", "")
            title = item.get("title", "")[:60]
            source = item.get("source", "BOARD")
            priority = item.get("priority", "P2")
            effort = item.get("effort", "M")
            status = item.get("status", "BACKLOG")
            depends = item.get("depends_on") or "-"

            # Mark completed items with strikethrough
            if status == "COMPLETED":
                item_id = f"~~{item_id}~~"

            line = f"| {item_id} | {title} | {source} | {priority} | {effort} | {status} | {depends} |"
            lines.append(line)

        return "\n".join(lines)


def create_board_artifact_integrator(
    board_artifacts_dir: Path | None = None,
) -> BoardArtifactIntegrator:
    """Factory function to create integrator instance."""
    return BoardArtifactIntegrator(board_artifacts_dir=board_artifacts_dir)
