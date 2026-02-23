"""Work stream commands: parse, claim, complete items.

Provides a pydantic-modeled interface to the canonical WORK_STREAM.md file.

# @trace FR-DX-004
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from pathlib import Path


class WorkItem(BaseModel):
    """A single item from the WORK_STREAM.md backlog table."""

    id: str = Field(description="Work item identifier")
    title: str = Field(description="Human-readable title")
    source: str = Field(default="", description="Origin document or plan")
    priority: str = Field(default="P2", description="Priority level")
    depends: str = Field(default="-", description="Dependencies (comma-separated IDs or '-')")
    status: str = Field(default="BACKLOG", description="Current status")


_TABLE_ROW_RE = re.compile(r"^\|(.+)\|$")
_WL_HEADER_RE = re.compile(r"^###\s+\[(WL-(\d+))\]\s+(.+?)$", re.MULTILINE)


def _parse_table_row(line: str) -> list[str]:
    """Extract cell values from a markdown table row."""
    m = _TABLE_ROW_RE.match(line.strip())
    if not m:
        return []
    return [cell.strip() for cell in m.group(1).split("|")]


def normalize_owner_identifier(owner: str) -> str:
    """Normalize owner identifiers across local and remote systems."""
    normalized = owner.strip()
    if not normalized:
        raise ValueError("owner must not be empty")
    return normalized


def parse_workstream(path: Path) -> list[WorkItem]:
    """Parse WORK_STREAM.md and return all backlog items.

    Args:
        path: Path to the WORK_STREAM.md file.

    Returns:
        List of WorkItem models from the BACKLOG section.

    Raises:
        FileNotFoundError: If path does not exist.
    """
    text = path.read_text()
    lines = text.splitlines()

    in_backlog = False
    header_seen = False
    items: list[WorkItem] = []

    for line in lines:
        if "## BACKLOG" in line:
            in_backlog = True
            continue
        if in_backlog and line.startswith("## "):
            break
        if not in_backlog:
            continue
        if "|----" in line:
            header_seen = True
            continue
        if "| ID |" in line:
            continue
        if not header_seen:
            continue

        cells = _parse_table_row(line)
        if len(cells) < 5:
            continue

        item_id = cells[0].strip("~").strip()
        if not item_id or item_id.startswith("*"):
            continue

        items.append(
            WorkItem(
                id=item_id,
                title=cells[1].strip("~").strip(),
                source=cells[2] if len(cells) > 2 else "",
                priority=cells[3] if len(cells) > 3 else "P2",
                depends=cells[4] if len(cells) > 4 else "-",
            )
        )

    return items


def claim_item(path: Path, item_id: str, owner: str) -> None:
    """Claim a work item by appending to the CLAIMED section.

    Args:
        path: Path to WORK_STREAM.md.
        item_id: ID of the item to claim.
        owner: Agent or user identifier.

    Raises:
        FileNotFoundError: If path does not exist.
        ValueError: If CLAIMED section not found.
    """
    from datetime import UTC, datetime

    text = path.read_text()
    lines = text.splitlines()

    claimed_idx = None
    for i, line in enumerate(lines):
        if "## CLAIMED" in line:
            claimed_idx = i
            break

    if claimed_idx is None:
        raise ValueError("CLAIMED section not found in work stream file")

    insert_at = claimed_idx + 1
    for i in range(claimed_idx + 1, len(lines)):
        if lines[i].startswith("## "):
            insert_at = i
            break
        if lines[i].startswith("|") and "| ID |" not in lines[i] and "|----" not in lines[i]:
            insert_at = i + 1

    timestamp = datetime.now(UTC).isoformat()
    claim_line = f"| {item_id} | {normalize_owner_identifier(owner)} | {timestamp} |"
    lines.insert(insert_at, claim_line)
    path.write_text("\n".join(lines) + "\n")


def mark_completed(path: Path, item_id: str) -> None:
    """Mark a work item as completed by striking through in BACKLOG.

    Args:
        path: Path to WORK_STREAM.md.
        item_id: ID of the item to mark completed.

    Raises:
        FileNotFoundError: If path does not exist.
    """
    text = path.read_text()
    # Strike through the item ID in the backlog
    updated = text.replace(f"| {item_id} |", f"| ~~{item_id}~~ |")
    path.write_text(updated)


def lint_workstream_schema(path: Path) -> list[str]:
    """Validate canonical WORK_STREAM structural requirements."""
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    for section in ("## BACKLOG", "## CLAIMED", "## COMPLETED"):
        if section not in text:
            errors.append(f"missing required section: {section}")

    required_header = "| ID | Title | Source | Priority | Depends |"
    if required_header not in text:
        errors.append("missing required BACKLOG table header")

    if not _WL_HEADER_RE.search(text):
        errors.append("missing WL section headers (### [WL-<id>] Title)")

    return errors


def normalize_workstream_sections(path: Path) -> str:
    """Sort WL sections by numeric ID and normalize status line formatting."""
    text = path.read_text(encoding="utf-8")
    matches = list(_WL_HEADER_RE.finditer(text))
    if not matches:
        return text

    sections: list[tuple[int, str]] = []
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        raw = text[start:end].rstrip() + "\n"
        normalized = re.sub(
            r"^\*\*Status:\*\*\s+(.+)$",
            lambda m: f"**Status:** {m.group(1).strip().upper()}",
            raw,
            flags=re.MULTILINE,
        )
        sections.append((int(match.group(2)), normalized))

    ordered = "".join(section for _, section in sorted(sections, key=lambda item: item[0]))
    prefix = text[: matches[0].start()]
    normalized_text = f"{prefix}{ordered}"
    path.write_text(normalized_text, encoding="utf-8")
    return normalized_text
