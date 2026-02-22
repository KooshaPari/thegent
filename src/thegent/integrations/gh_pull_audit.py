"""GitHub Pull Reflection Audit Trail for workstream sync cycles.

# @trace WL-163
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class PullReflectionAuditEntry:
    """Single audit entry for a GitHub pull reflection event."""

    wl_id: str
    cycle_id: str
    connector: str
    before_status: str
    after_status: str
    timestamp: str
    sync_note: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return asdict(self)

    def to_json_line(self) -> str:
        """Convert to JSONL format (single line)."""
        return json.dumps(self.to_dict())


class PullReflectionAuditLog:
    """Audit log for GitHub pull reflection events across sync cycles."""

    def __init__(self, log_path: Path | str | None = None) -> None:
        """Initialize the audit log.

        Args:
            log_path: Path to JSONL log file. If None, uses docs/reference/gh_pull_audit.jsonl.
        """
        if log_path is None:
            # Default to docs/reference/gh_pull_audit.jsonl relative to project root
            log_path = Path("docs/reference/gh_pull_audit.jsonl")
        self.log_path = Path(log_path)

    def append(self, entry: PullReflectionAuditEntry) -> None:
        """Append an audit entry to the log.

        Args:
            entry: The PullReflectionAuditEntry to append.
        """
        # Ensure parent directory exists
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        # Append as JSONL (single line per entry)
        with self.log_path.open("a") as f:
            f.write(entry.to_json_line() + "\n")

    def read_all(self) -> list[PullReflectionAuditEntry]:
        """Read all audit entries from the log.

        Returns:
            List of all PullReflectionAuditEntry objects in the log.
        """
        if not self.log_path.exists():
            return []

        entries: list[PullReflectionAuditEntry] = []
        with self.log_path.open("r") as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    entries.append(PullReflectionAuditEntry(**data))
        return entries

    def read_by_cycle(self, cycle_id: str) -> list[PullReflectionAuditEntry]:
        """Read all audit entries for a specific sync cycle.

        Args:
            cycle_id: The cycle ID to filter by.

        Returns:
            List of PullReflectionAuditEntry objects for the given cycle.
        """
        all_entries = self.read_all()
        return [e for e in all_entries if e.cycle_id == cycle_id]

    def clear(self) -> None:
        """Clear the entire audit log."""
        if self.log_path.exists():
            self.log_path.unlink()
